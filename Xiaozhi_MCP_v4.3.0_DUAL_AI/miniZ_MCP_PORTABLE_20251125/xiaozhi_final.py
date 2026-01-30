#!/usr/bin/env python3
"""
miniZ MCP - Giao diện Sidebar matching Official Design
Web UI + WebSocket MCP + 20 Tools - Single File!
"""

import asyncio
import json
import subprocess
import psutil
import time
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import websockets
import pyautogui

# Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ [Gemini] google-generativeai not installed. Run: pip install google-generativeai")

# OpenAI GPT-4
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ [OpenAI] openai library not installed. Run: pip install openai")

# Selenium Browser Automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ [Selenium] Not installed. Run: pip install selenium webdriver-manager")

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG_FILE = Path(__file__).parent / "xiaozhi_endpoints.json"
GEMINI_API_KEY = ""  # Sẽ được load từ xiaozhi_endpoints.json
OPENAI_API_KEY = ""  # Sẽ được load từ xiaozhi_endpoints.json

DEFAULT_ENDPOINT = {
    "name": "Thiết bị 1",
    "token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ1MzYxMSwiYWdlbnRJZCI6OTQ0MjE4LCJlbmRwb2ludElkIjoiYWdlbnRfOTQ0MjE4IiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc2MjA4NTI1OSwiZXhwIjoxNzkzNjQyODU5fQ.GK91-17mqarpETPwz7N6rZj5DaT7bJkpK7EM6lO0Rdmfztv_KeOTBP9R4Lvy3uXKMCJn3gwucvelCur95GAn5Q",
    "enabled": True
}

def load_endpoints_from_file():
    """Đọc cấu hình endpoints từ file JSON"""
    global GEMINI_API_KEY, OPENAI_API_KEY
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ [Config] Loaded {len(data.get('endpoints', []))} endpoints from {CONFIG_FILE.name}")
                
                # Load Gemini API key nếu có
                if data.get('gemini_api_key'):
                    GEMINI_API_KEY = data['gemini_api_key']
                    print(f"✅ [Gemini] API key loaded (ends with ...{GEMINI_API_KEY[-8:]})")
                
                # Load OpenAI API key nếu có
                if data.get('openai_api_key'):
                    OPENAI_API_KEY = data['openai_api_key']
                    print(f"✅ [OpenAI] API key loaded (ends with ...{OPENAI_API_KEY[-8:]})")
                
                return data.get('endpoints', []), data.get('active_index', 0)
        except Exception as e:
            print(f"⚠️ [Config] Error loading {CONFIG_FILE.name}: {e}")
    
    # Trả về cấu hình mặc định nếu không có file
    return [
        DEFAULT_ENDPOINT,
        {"name": "Thiết bị 2", "token": "", "enabled": False},
        {"name": "Thiết bị 3", "token": "", "enabled": False}
    ], 0

def save_endpoints_to_file(endpoints, active_index):
    """Lưu cấu hình endpoints vào file JSON - chỉ khi có thay đổi"""
    global GEMINI_API_KEY, OPENAI_API_KEY
    
    try:
        # Kiểm tra nếu data không thay đổi thì không cần lưu
        new_data = {
            'endpoints': endpoints,
            'active_index': active_index,
            'gemini_api_key': GEMINI_API_KEY,
            'openai_api_key': OPENAI_API_KEY,
            'last_updated': datetime.now().isoformat()
        }
        
        # Đọc dữ liệu cũ để so sánh (trừ last_updated)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    # So sánh endpoints và active_index
                    if (old_data.get('endpoints') == endpoints and 
                        old_data.get('active_index') == active_index):
                        # Không có thay đổi, skip save
                        return True
            except Exception:
                pass
        
        # Có thay đổi, tiến hành lưu
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"💾 [Config] Saved {len(endpoints)} endpoints to {CONFIG_FILE.name}")
        return True
    except Exception as e:
        print(f"❌ [Config] Error saving to {CONFIG_FILE.name}: {e}")
        return False

# Load cấu hình từ file
endpoints_config, loaded_active_index = load_endpoints_from_file()
active_endpoint_index = loaded_active_index
xiaozhi_connected = False
active_connections = []
xiaozhi_ws = None
should_reconnect = False  # Flag để trigger reconnect

# ============================================================
# CONVERSATION HISTORY - Lưu lịch sử hội thoại
# ============================================================
conversation_history = []  # List để lưu tất cả messages
CONVERSATION_FILE = "conversation_history.json"

def load_conversation_history():
    """Load lịch sử hội thoại từ file"""
    global conversation_history
    try:
        if os.path.exists(CONVERSATION_FILE):
            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                conversation_history = json.load(f)
            print(f"📚 Loaded {len(conversation_history)} messages from history")
    except Exception as e:
        print(f"⚠️ Could not load conversation history: {e}")
        conversation_history = []

def save_conversation_history():
    """Lưu lịch sử hội thoại vào file"""
    try:
        with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save conversation history: {e}")

def add_to_conversation(role: str, content: str, metadata: dict = None):
    """
    Thêm message vào lịch sử hội thoại
    role: 'user', 'assistant', 'system', 'tool'
    content: nội dung message
    metadata: thông tin bổ sung (tool_name, timestamp, token_count, etc.)
    """
    from datetime import datetime
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": metadata or {}
    }
    
    conversation_history.append(message)
    
    # Auto-save sau mỗi 5 messages
    if len(conversation_history) % 5 == 0:
        save_conversation_history()

def export_conversation_to_file(filename: str = "") -> dict:
    """Export lịch sử hội thoại ra file riêng"""
    try:
        from datetime import datetime
        import os
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_export_{timestamp}.json"
        
        documents_path = os.path.expanduser("~\\Documents")
        save_folder = os.path.join(documents_path, "miniZ_Conversations")
        os.makedirs(save_folder, exist_ok=True)
        
        file_path = os.path.join(save_folder, filename)
        
        # Export với format đẹp
        export_data = {
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_messages": len(conversation_history),
            "messages": conversation_history
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"📚 Đã export {len(conversation_history)} messages",
            "path": file_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Load lịch sử khi khởi động
load_conversation_history()

print("🚀 miniZ MCP - Sidebar UI")
print(f"🌐 Web: http://localhost:8000")
print(f"📡 MCP: Multi-device ready")

# ============================================================
# TOOL IMPLEMENTATIONS (20 TOOLS)
# ============================================================

async def set_volume(level: int) -> dict:
    """Điều chỉnh âm lượng hệ thống - Windows only"""
    try:
        if not 0 <= level <= 100:
            return {"success": False, "error": "Level phải từ 0-100"}
        
        # Sử dụng PowerShell trực tiếp (tương thích tốt hơn với Python 3.13)
        ps_cmd = f"""
[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$obj = New-Object System.Windows.Forms.Form
$obj.KeyPreview = $True

# Get current volume
$wshShell = New-Object -ComObject WScript.Shell
for($i=1; $i -le 50; $i++){{$wshShell.SendKeys([char]174)}}  # Mute to 0

# Set to desired level
$steps = [Math]::Round({level} / 2)
for($i=1; $i -le $steps; $i++){{$wshShell.SendKeys([char]175)}}  # Volume up

Write-Output "Volume set to {level}%"
"""
        
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
        
        if proc.returncode == 0:
            return {
                "success": True, 
                "level": level,
                "message": f"✅ Âm lượng đã đặt: {level}%"
            }
        else:
            error_msg = stderr.decode('utf-8', errors='ignore').strip()
            return {"success": False, "error": f"PowerShell error: {error_msg[:200]}"}
                
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout khi điều chỉnh âm lượng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def mute_volume() -> dict:
    """Tắt tiếng (mute) hệ thống"""
    try:
        ps_cmd = """
$obj = New-Object -ComObject WScript.Shell
$obj.SendKeys([char]173)
Write-Output "Volume muted"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": "🔇 Đã tắt tiếng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def unmute_volume() -> dict:
    """Bật lại tiếng (unmute) hệ thống"""
    try:
        ps_cmd = """
$obj = New-Object -ComObject WScript.Shell
$obj.SendKeys([char]173)
Write-Output "Volume unmuted"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": "🔊 Đã bật tiếng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def volume_up(steps: int = 5) -> dict:
    """Tăng âm lượng lên (mỗi step ~2%)"""
    try:
        ps_cmd = f"""
$obj = New-Object -ComObject WScript.Shell
for($i=1; $i -le {steps}; $i++){{$obj.SendKeys([char]175)}}
Write-Output "Volume increased by {steps} steps"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": f"🔊 Đã tăng âm lượng ({steps} bước)"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def volume_down(steps: int = 5) -> dict:
    """Giảm âm lượng xuống (mỗi step ~2%)"""
    try:
        ps_cmd = f"""
$obj = New-Object -ComObject WScript.Shell
for($i=1; $i -le {steps}; $i++){{$obj.SendKeys([char]174)}}
Write-Output "Volume decreased by {steps} steps"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": f"🔉 Đã giảm âm lượng ({steps} bước)"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def get_volume() -> dict:
    """Lấy mức âm lượng hiện tại của hệ thống"""
    try:
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            current_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
            is_muted = volume.GetMute()
            
            return {
                "success": True,
                "level": current_volume,
                "muted": bool(is_muted),
                "message": f"🔊 Âm lượng hiện tại: {current_volume}%" + (" (Tắt tiếng)" if is_muted else "")
            }
        except ImportError:
            # Fallback PowerShell
            ps_cmd = """
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {
    int NotImpl1(); int NotImpl2();
    int GetMasterVolumeLevelScalar(out float level);
}
[Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject { }
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {
    int NotImpl1();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice device);
}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {
    int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
}
'@
$enumerator = [System.Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]'BCDE0395-E52F-467C-8E3D-C4579291692E'))
$device = $null
$enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device)
$aev = $null
$device.Activate([Guid]'5CDF2C82-841E-4546-9722-0CF74078229A', 0, 0, [ref]$aev)
$current = 0.0
$aev.GetMasterVolumeLevelScalar([ref]$current)
Write-Output ([int]($current * 100))
"""
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-NoProfile", "-Command", ps_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=3)
            
            if proc.returncode == 0:
                level = int(stdout.decode('utf-8', errors='ignore').strip())
                return {
                    "success": True,
                    "level": level,
                    "message": f"🔊 Âm lượng hiện tại: {level}%"
                }
            else:
                return {"success": False, "error": "Không thể lấy âm lượng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def take_screenshot(filename: str = None) -> dict:
    """Chụp màn hình toàn bộ và lưu file
    
    Args:
        filename: Tên file lưu ảnh (optional). Mặc định: screenshot_YYYYMMDD_HHMMSS.png
    
    Returns:
        dict với thông tin file đã lưu
    """
    try:
        import pyautogui
        from datetime import datetime
        import os
        
        # Tạo tên file mặc định nếu không có
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Đảm bảo có extension .png
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename += '.png'
        
        # Lưu vào thư mục Downloads hoặc thư mục hiện tại
        downloads_path = Path.home() / "Downloads"
        if downloads_path.exists():
            filepath = downloads_path / filename
        else:
            filepath = Path(filename)
        
        # Chụp màn hình
        print(f"📸 [Screenshot] Đang chụp màn hình...")
        screenshot = pyautogui.screenshot()
        
        # Lưu file
        screenshot.save(str(filepath))
        
        file_size = filepath.stat().st_size / 1024  # KB
        
        print(f"✅ [Screenshot] Đã lưu: {filepath}")
        
        return {
            "success": True,
            "message": f"✅ Đã chụp màn hình: {filepath.name}",
            "filepath": str(filepath),
            "filename": filepath.name,
            "size_kb": round(file_size, 2),
            "dimensions": f"{screenshot.width}x{screenshot.height}"
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "Thiếu thư viện 'pyautogui'. Cài đặt: pip install pyautogui"
        }
    except Exception as e:
        print(f"❌ [Screenshot] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def show_notification(title: str, message: str) -> dict:
    try:
        ps_cmd = f'''[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; $template = @"<toast><visual><binding template="ToastText02"><text id="1">{title}</text><text id="2">{message}</text></binding></visual></toast>"@; $xml = New-Object Windows.Data.Xml.Dom.XmlDocument; $xml.LoadXml($template); $toast = New-Object Windows.UI.Notifications.ToastNotification $xml; [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Xiaozhi").Show($toast)'''
        proc = await asyncio.create_subprocess_exec("powershell", "-Command", ps_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(proc.wait(), timeout=5)
        return {"success": True, "title": title, "message": message}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Cache cho system resources
_resource_cache = None
_resource_cache_time = 0
RESOURCE_CACHE_DURATION = 2  # Cache 2 giây

async def get_system_resources() -> dict:
    """Lấy thông tin tài nguyên hệ thống với caching"""
    global _resource_cache, _resource_cache_time
    
    try:
        # Kiểm tra cache
        now = time.time()
        if _resource_cache and (now - _resource_cache_time) < RESOURCE_CACHE_DURATION:
            return _resource_cache
        
        # Lấy dữ liệu mới - giảm interval từ 1s xuống 0.1s
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        result = {
            "success": True, 
            "data": {
                "cpu_percent": cpu, 
                "memory_percent": mem.percent, 
                "memory_used_gb": round(mem.used / (1024**3), 2), 
                "memory_total_gb": round(mem.total / (1024**3), 2), 
                "disk_percent": disk.percent, 
                "disk_used_gb": round(disk.used / (1024**3), 2), 
                "disk_total_gb": round(disk.total / (1024**3), 2)
            }
        }
        
        # Cập nhật cache
        _resource_cache = result
        _resource_cache_time = now
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_current_time() -> dict:
    try:
        now = datetime.now()
        return {"success": True, "datetime": now.strftime("%Y-%m-%d %H:%M:%S"), "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S"), "day_of_week": now.strftime("%A"), "timestamp": int(now.timestamp())}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def calculator(expression: str) -> dict:
    try:
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return {"success": False, "error": "Ký tự không hợp lệ"}
        result = eval(expression, {"__builtins__": {}}, {})
        return {"success": True, "expression": expression, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_network_info() -> dict:
    try:
        import socket
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return {"success": True, "hostname": hostname, "ip": ip}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_web(query: str) -> dict:
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {"success": True, "message": f"Đã mở tìm kiếm: {query}", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_google_text(query: str, num_results: int = 5) -> dict:
    """
    Tìm kiếm Google và trả về kết quả TEXT (không mở browser)
    Sử dụng Google Custom Search API hoặc web scraping
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        
        # Tạo URL search
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
        
        # Headers để giả lập browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Gọi trong executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(url, headers=headers, timeout=10)
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Google returned status code: {response.status_code}"
            }
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các kết quả search
        results = []
        for g in soup.find_all('div', class_='g')[:num_results]:
            try:
                # Title
                title_elem = g.find('h3')
                title = title_elem.text if title_elem else ''
                
                # Link
                link_elem = g.find('a')
                link = link_elem['href'] if link_elem and link_elem.has_attr('href') else ''
                
                # Snippet
                snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                snippet = snippet_elem.text if snippet_elem else ''
                
                if title and link:
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet[:200]
                    })
            except:
                continue
        
        if not results:
            return {
                "success": False,
                "error": "Không tìm thấy kết quả. Google có thể đã block request."
            }
        
        # Format kết quả
        result_text = f"🔍 KẾT QUẢ TÌM KIẾM: {query}\n\n"
        for i, r in enumerate(results, 1):
            result_text += f"{i}. {r['title']}\n"
            result_text += f"   {r['link']}\n"
            if r['snippet']:
                result_text += f"   {r['snippet']}\n"
            result_text += "\n"
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "summary": result_text,
            "message": f"✅ Tìm thấy {len(results)} kết quả cho '{query}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Lỗi search: {str(e)}",
            "suggestion": "Hãy dùng search_web để mở browser hoặc get_vnexpress_news cho tin Việt Nam"
        }

async def set_brightness(level: int) -> dict:
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        return {"success": True, "level": level, "message": f"Đã đặt độ sáng: {level}%"}
    except Exception as e:
        return {"success": False, "error": str(e), "note": "Có thể cần cài: pip install screen-brightness-control"}

async def get_clipboard() -> dict:
    try:
        import pyperclip
        content = pyperclip.paste()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_clipboard(text: str) -> dict:
    try:
        import pyperclip
        pyperclip.copy(text)
        return {"success": True, "message": f"Đã copy vào clipboard: {text[:50]}..."}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_sound(frequency: int = 1000, duration: int = 500) -> dict:
    try:
        import winsound
        winsound.Beep(frequency, duration)
        return {"success": True, "message": f"Đã phát âm thanh {frequency}Hz trong {duration}ms"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_application(app_name: str) -> dict:
    """
    Mở ứng dụng Windows với khả năng tìm kiếm thông minh.
    
    Thứ tự tìm kiếm:
    1. Dictionary mapping (ưu tiên cao nhất)
    2. Tìm trong PATH
    3. Tìm trong Registry (App Paths)
    4. Tìm trong Program Files
    5. Fallback: Windows Start Menu
    
    Args:
        app_name: Tên ứng dụng (ví dụ: "chrome", "photoshop", "word")
        
    Returns:
        dict: {"success": bool, "message": str, "path": str (optional)}
    """
    try:
        import os
        import shutil
        import winreg
        import glob
        
        # Dictionary mapping - Hỗ trợ 50+ ứng dụng phổ biến
        apps = {
            # Windows Built-in
            "notepad": "notepad.exe",
            "note": "notepad.exe",
            "máy ghi chú": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "máy tính": "calc.exe",
            "paint": "mspaint.exe",
            "vẽ": "mspaint.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "ps": "powershell.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "taskmgr": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            "quản lý tác vụ": "taskmgr.exe",
            
            # Browsers
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "gc": "chrome.exe",
            "firefox": "firefox.exe",
            "ff": "firefox.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "brave": "brave.exe",
            "opera": "opera.exe",
            
            # Microsoft Office
            "word": "WINWORD.EXE",
            "microsoft word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "microsoft excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "microsoft powerpoint": "POWERPNT.EXE",
            "ppt": "POWERPNT.EXE",
            "outlook": "OUTLOOK.EXE",
            "microsoft outlook": "OUTLOOK.EXE",
            "onenote": "ONENOTE.EXE",
            "teams": "Teams.exe",
            "microsoft teams": "Teams.exe",
            
            # Adobe Creative Cloud
            "photoshop": "Photoshop.exe",
            "adobe photoshop": "Photoshop.exe",
            "ps": "Photoshop.exe",
            "illustrator": "Illustrator.exe",
            "adobe illustrator": "Illustrator.exe",
            "ai": "Illustrator.exe",
            "premiere": "Adobe Premiere Pro.exe",
            "premiere pro": "Adobe Premiere Pro.exe",
            "after effects": "AfterFX.exe",
            "ae": "AfterFX.exe",
            "lightroom": "Lightroom.exe",
            "acrobat": "Acrobat.exe",
            "adobe acrobat": "Acrobat.exe",
            
            # Development Tools
            "vscode": "Code.exe",
            "visual studio code": "Code.exe",
            "code": "Code.exe",
            "vs": "Code.exe",
            "sublime": "sublime_text.exe",
            "sublime text": "sublime_text.exe",
            "atom": "atom.exe",
            "notepad++": "notepad++.exe",
            "npp": "notepad++.exe",
            "pycharm": "pycharm64.exe",
            "intellij": "idea64.exe",
            "webstorm": "webstorm64.exe",
            "androidstudio": "studio64.exe",
            "android studio": "studio64.exe",
            
            # 3D & Design
            "blender": "blender.exe",
            "3ds max": "3dsmax.exe",
            "maya": "maya.exe",
            "sketchup": "SketchUp.exe",
            "fusion360": "Fusion360.exe",
            "fusion 360": "Fusion360.exe",
            "autocad": "acad.exe",
            "solidworks": "SLDWORKS.exe",
            
            # Communication
            "discord": "Discord.exe",
            "slack": "slack.exe",
            "zoom": "Zoom.exe",
            "skype": "Skype.exe",
            "telegram": "Telegram.exe",
            "zalo": "Zalo.exe",
            
            # Media Players
            "vlc": "vlc.exe",
            "spotify": "Spotify.exe",
            "itunes": "iTunes.exe",
            "windows media player": "wmplayer.exe",
            "wmp": "wmplayer.exe",
            
            # Other Popular Apps
            "steam": "steam.exe",
            "epic games": "EpicGamesLauncher.exe",
            "epic": "EpicGamesLauncher.exe",
            "obs": "obs64.exe",
            "obs studio": "obs64.exe",
            "gimp": "gimp-2.10.exe",
            "audacity": "audacity.exe",
            "7zip": "7zFM.exe",
            "7-zip": "7zFM.exe",
            "winrar": "WinRAR.exe",
        }
        
        # 1. Kiểm tra trong dictionary
        app_name_lower = app_name.lower().strip()
        exe_name = apps.get(app_name_lower)
        
        print(f"🔍 [Open App] Tìm kiếm: '{app_name}' → {exe_name or 'không có trong dictionary'}")
        
        # Nếu không có trong dictionary, thử dùng tên gốc
        if not exe_name:
            # Kiểm tra nếu đã có .exe
            if app_name.lower().endswith('.exe'):
                exe_name = app_name
            else:
                exe_name = app_name + '.exe'
        
        # 2. Tìm trong PATH
        exe_path = shutil.which(exe_name)
        if exe_path:
            print(f"✅ [Open App] Tìm thấy trong PATH: {exe_path}")
            subprocess.Popen([exe_path])
            return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        # 3. Tìm trong Windows Registry (App Paths)
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}") as key:
                exe_path = winreg.QueryValue(key, None)
                if exe_path and os.path.exists(exe_path):
                    print(f"✅ [Open App] Tìm thấy trong Registry: {exe_path}")
                    subprocess.Popen([exe_path])
                    return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        except WindowsError:
            pass
        
        # 4. Tìm trong các thư mục phổ biến
        common_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "*", exe_name),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "*", exe_name),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "*", exe_name),
            os.path.join(os.environ.get("APPDATA", ""), "*", exe_name),
        ]
        
        import glob
        for pattern in common_paths:
            matches = glob.glob(pattern, recursive=False)
            if matches:
                exe_path = matches[0]
                print(f"✅ [Open App] Tìm thấy trong: {exe_path}")
                subprocess.Popen([exe_path])
                return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        # 5. Tìm kiếm sâu trong Program Files (chậm hơn, dùng làm fallback)
        if "photoshop" in app_name_lower or "adobe" in app_name_lower:
            # Adobe apps thường ở C:\Program Files\Adobe
            adobe_base = r"C:\Program Files\Adobe"
            if os.path.exists(adobe_base):
                for root, dirs, files in os.walk(adobe_base):
                    if exe_name in files:
                        exe_path = os.path.join(root, exe_name)
                        print(f"✅ [Open App] Tìm thấy Adobe app: {exe_path}")
                        subprocess.Popen([exe_path])
                        return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        if "autodesk" in app_name_lower or "fusion" in app_name_lower:
            # Autodesk apps thường ở LOCALAPPDATA
            autodesk_base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Autodesk")
            if os.path.exists(autodesk_base):
                for root, dirs, files in os.walk(autodesk_base):
                    if exe_name in files:
                        exe_path = os.path.join(root, exe_name)
                        print(f"✅ [Open App] Tìm thấy Autodesk app: {exe_path}")
                        subprocess.Popen([exe_path])
                        return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        # 6. Fallback cuối cùng: Dùng Windows Start Menu
        print(f"⚠️ [Open App] Không tìm thấy đường dẫn, thử Windows Start Menu...")
        subprocess.Popen(["start", "", app_name], shell=True)
        return {
            "success": True, 
            "message": f"✅ Đã gửi lệnh mở {app_name} (Windows sẽ tìm trong Start Menu)",
            "note": "Nếu không mở được, hãy kiểm tra tên ứng dụng hoặc thêm vào dictionary"
        }
        
    except Exception as e:
        print(f"❌ [Open App] Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Lỗi khi mở {app_name}: {str(e)}"}

# ==================== MEDIA PLAYER CONTROL ====================
async def media_play_pause() -> dict:
    """Phát/Tạm dừng media (Play/Pause toggle)"""
    try:
        pyautogui.press('playpause')
        return {"success": True, "message": "✅ Đã gửi lệnh Play/Pause"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_next_track() -> dict:
    """Chuyển bài tiếp theo (Next Track)"""
    try:
        pyautogui.press('nexttrack')
        return {"success": True, "message": "✅ Đã chuyển bài tiếp theo"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_previous_track() -> dict:
    """Chuyển bài trước đó (Previous Track)"""
    try:
        pyautogui.press('prevtrack')
        return {"success": True, "message": "✅ Đã chuyển bài trước"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_stop() -> dict:
    """Dừng phát media (Stop)"""
    try:
        pyautogui.press('stop')
        return {"success": True, "message": "✅ Đã dừng phát"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_volume_up() -> dict:
    """Tăng âm lượng media (Media Volume Up)"""
    try:
        pyautogui.press('volumeup')
        return {"success": True, "message": "✅ Đã tăng âm lượng"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_volume_down() -> dict:
    """Giảm âm lượng media (Media Volume Down)"""
    try:
        pyautogui.press('volumedown')
        return {"success": True, "message": "✅ Đã giảm âm lượng"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_mute() -> dict:
    """Tắt/Bật tiếng media (Mute Toggle)"""
    try:
        pyautogui.press('volumemute')
        return {"success": True, "message": "✅ Đã toggle mute"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_control(action: str) -> dict:
    """
    Điều khiển media player đa năng.
    
    Args:
        action: Hành động cần thực hiện
            - "play" hoặc "pause": Phát/Tạm dừng
            - "next": Bài tiếp theo
            - "previous" hoặc "prev": Bài trước
            - "stop": Dừng phát
            - "volume_up": Tăng âm lượng
            - "volume_down": Giảm âm lượng
            - "mute": Tắt/Bật tiếng
    
    Returns:
        dict: Kết quả thực hiện
    """
    try:
        action = action.lower().strip()
        
        actions_map = {
            "play": "playpause",
            "pause": "playpause",
            "playpause": "playpause",
            "next": "nexttrack",
            "previous": "prevtrack",
            "prev": "prevtrack",
            "stop": "stop",
            "volume_up": "volumeup",
            "volumeup": "volumeup",
            "volume_down": "volumedown",
            "volumedown": "volumedown",
            "mute": "volumemute",
        }
        
        key = actions_map.get(action)
        if not key:
            return {
                "success": False, 
                "error": f"Action không hợp lệ: '{action}'. Chọn: play, pause, next, previous, stop, volume_up, volume_down, mute"
            }
        
        pyautogui.press(key)
        
        action_messages = {
            "playpause": "Play/Pause",
            "nexttrack": "Bài tiếp theo",
            "prevtrack": "Bài trước",
            "stop": "Dừng phát",
            "volumeup": "Tăng âm lượng",
            "volumedown": "Giảm âm lượng",
            "volumemute": "Mute/Unmute",
        }
        
        return {"success": True, "message": f"✅ {action_messages[key]}", "action": action}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ==================== END MEDIA PLAYER CONTROL ====================

async def get_active_media_players() -> dict:
    """
    Lấy danh sách các media players/applications đang chạy trên máy tính.
    
    Thông tin này giúp LLM biết:
    - Có media player nào đang chạy không
    - Nên dùng tool nào (media_play_pause cho Spotify/VLC, stop_music cho WMP)
    - Có ứng dụng nào có thể điều khiển được
    
    Returns:
        dict: Danh sách media players, browsers, và ứng dụng quan trọng đang chạy
    """
    try:
        # Danh sách media players và ứng dụng quan trọng cần theo dõi
        MEDIA_APPS = {
            # Media Players
            "spotify.exe": {"name": "Spotify", "type": "music", "supports_media_keys": True},
            "vlc.exe": {"name": "VLC Media Player", "type": "video", "supports_media_keys": True},
            "wmplayer.exe": {"name": "Windows Media Player", "type": "music", "supports_media_keys": True},
            "itunes.exe": {"name": "iTunes", "type": "music", "supports_media_keys": True},
            
            # Browsers (có thể phát YouTube, Spotify Web...)
            "chrome.exe": {"name": "Google Chrome", "type": "browser", "supports_media_keys": True},
            "msedge.exe": {"name": "Microsoft Edge", "type": "browser", "supports_media_keys": True},
            "firefox.exe": {"name": "Firefox", "type": "browser", "supports_media_keys": True},
            "brave.exe": {"name": "Brave", "type": "browser", "supports_media_keys": True},
            "opera.exe": {"name": "Opera", "type": "browser", "supports_media_keys": True},
            
            # Communication (có media playback)
            "discord.exe": {"name": "Discord", "type": "communication", "supports_media_keys": True},
            "slack.exe": {"name": "Slack", "type": "communication", "supports_media_keys": False},
            "zoom.exe": {"name": "Zoom", "type": "communication", "supports_media_keys": False},
            "skype.exe": {"name": "Skype", "type": "communication", "supports_media_keys": False},
            
            # Office & Productivity
            "WINWORD.EXE": {"name": "Microsoft Word", "type": "office", "supports_media_keys": False},
            "EXCEL.EXE": {"name": "Microsoft Excel", "type": "office", "supports_media_keys": False},
            "POWERPNT.EXE": {"name": "PowerPoint", "type": "office", "supports_media_keys": False},
            "OUTLOOK.EXE": {"name": "Outlook", "type": "office", "supports_media_keys": False},
            
            # Development
            "Code.exe": {"name": "VS Code", "type": "development", "supports_media_keys": False},
            "devenv.exe": {"name": "Visual Studio", "type": "development", "supports_media_keys": False},
            "pycharm64.exe": {"name": "PyCharm", "type": "development", "supports_media_keys": False},
            
            # Design & Creative
            "Photoshop.exe": {"name": "Adobe Photoshop", "type": "creative", "supports_media_keys": False},
            "Illustrator.exe": {"name": "Adobe Illustrator", "type": "creative", "supports_media_keys": False},
            "blender.exe": {"name": "Blender", "type": "3d", "supports_media_keys": False},
        }
        
        running_apps = []
        media_players = []
        browsers = []
        
        # Quét các process đang chạy
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                
                if proc_name in MEDIA_APPS:
                    app_info = MEDIA_APPS[proc_name].copy()
                    app_info['pid'] = proc.info['pid']
                    app_info['process_name'] = proc_name
                    
                    running_apps.append(app_info)
                    
                    # Phân loại
                    if app_info['type'] in ['music', 'video']:
                        media_players.append(app_info)
                    elif app_info['type'] == 'browser':
                        browsers.append(app_info)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Tạo thông điệp hướng dẫn cho LLM
        guidance = ""
        
        if media_players:
            player_names = [p['name'] for p in media_players]
            guidance += f"🎵 Media Players đang chạy: {', '.join(player_names)}.\n"
            
            if any(p['name'] == 'Windows Media Player' for p in media_players):
                guidance += "   → Dùng stop_music() để dừng Windows Media Player.\n"
            
            if any(p['supports_media_keys'] and p['name'] != 'Windows Media Player' for p in media_players):
                guidance += "   → Dùng media_play_pause(), media_next_track() cho Spotify/VLC/iTunes.\n"
        
        if browsers:
            browser_names = [b['name'] for b in browsers]
            guidance += f"🌐 Browsers đang chạy: {', '.join(browser_names)}.\n"
            guidance += "   → Nếu đang phát YouTube/Spotify Web, dùng media_play_pause().\n"
        
        if not media_players and not browsers:
            guidance = "❌ Không có media player nào đang chạy. Dùng play_music() để phát nhạc từ music_library."
        
        return {
            "success": True,
            "all_apps": running_apps,
            "media_players": media_players,
            "browsers": browsers,
            "total_count": len(running_apps),
            "guidance": guidance.strip(),
            "message": f"✅ Đang chạy: {len(running_apps)} ứng dụng ({len(media_players)} media players, {len(browsers)} browsers)"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def list_running_processes(limit: int = 10) -> dict:
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append({"pid": p.info['pid'], "name": p.info['name'], "cpu": round(p.info['cpu_percent'], 2), "memory": round(p.info['memory_percent'], 2)})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Bỏ qua các tiến trình không thể truy cập
                pass
        procs = sorted(procs, key=lambda x: x['cpu'], reverse=True)[:limit]
        return {"success": True, "processes": procs, "count": len(procs)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def kill_process(identifier: str) -> dict:
    try:
        killed = []
        if identifier.isdigit():
            p = psutil.Process(int(identifier))
            name = p.name()
            p.terminate()
            killed.append(f"{name} (PID: {identifier})")
        else:
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    if identifier.lower() in p.info['name'].lower():
                        p.terminate()
                        killed.append(f"{p.info['name']} (PID: {p.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        if killed:
            return {"success": True, "message": f"Đã tắt: {', '.join(killed)}"}
        return {"success": False, "error": f"Không tìm thấy '{identifier}'"}
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Tiến trình không tồn tại: {identifier}"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Không có quyền tắt tiến trình: {identifier}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def create_file(path: str, content: str) -> dict:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": path, "message": f"Đã tạo: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def read_file(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "path": path, "content": content[:500], "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def list_files(directory: str) -> dict:
    try:
        import os
        files = []
        for item in os.listdir(directory):
            p = os.path.join(directory, item)
            files.append({"name": item, "type": "dir" if os.path.isdir(p) else "file", "size": os.path.getsize(p) if os.path.isfile(p) else 0})
        return {"success": True, "directory": directory, "files": files, "count": len(files)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_battery_status() -> dict:
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            return {"success": False, "error": "Không thể lấy thông tin pin (có thể không có pin)"}
        return {
            "success": True,
            "percent": bat.percent,
            "plugged": bat.power_plugged,
            "time_left": str(bat.secsleft) if bat.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_disk_usage() -> dict:
    try:
        disks = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({"device": part.device, "mountpoint": part.mountpoint, "fstype": part.fstype, "total_gb": round(usage.total / (1024**3), 2), "used_gb": round(usage.used / (1024**3), 2), "free_gb": round(usage.free / (1024**3), 2), "percent": usage.percent})
            except (PermissionError, OSError):
                # Bỏ qua các ổ đĩa không thể truy cập
                pass
        return {"success": True, "disks": disks, "count": len(disks)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# MUSIC LIBRARY TOOLS - VLC PLAYER
# ============================================================

MUSIC_LIBRARY = Path(__file__).parent / "music_library"
MUSIC_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac'}

# YouTube Playlists Management
YOUTUBE_PLAYLISTS_FILE = Path(__file__).parent / "youtube_playlists.json"

def load_youtube_playlists() -> list:
    """Đọc danh sách playlist YouTube từ file JSON"""
    try:
        if YOUTUBE_PLAYLISTS_FILE.exists():
            with open(YOUTUBE_PLAYLISTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ [Playlists] Error loading: {e}")
        return []

def save_youtube_playlists(playlists: list) -> bool:
    """Lưu danh sách playlist YouTube vào file JSON"""
    try:
        with open(YOUTUBE_PLAYLISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(playlists, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ [Playlists] Error saving: {e}")
        return False

async def add_youtube_playlist(name: str, url: str) -> dict:
    """Thêm playlist YouTube mới"""
    try:
        playlists = load_youtube_playlists()
        
        # Kiểm tra trùng tên
        if any(p['name'].lower() == name.lower() for p in playlists):
            return {
                "success": False,
                "error": f"Playlist '{name}' đã tồn tại!"
            }
        
        # Thêm playlist mới
        new_playlist = {
            "name": name,
            "url": url,
            "created_at": datetime.now().isoformat()
        }
        playlists.append(new_playlist)
        
        if save_youtube_playlists(playlists):
            return {
                "success": True,
                "message": f"✅ Đã thêm playlist: {name}",
                "playlist": new_playlist
            }
        else:
            return {
                "success": False,
                "error": "Không thể lưu playlist"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def remove_youtube_playlist(name: str) -> dict:
    """Xóa playlist YouTube"""
    try:
        playlists = load_youtube_playlists()
        
        # Tìm và xóa playlist
        original_count = len(playlists)
        playlists = [p for p in playlists if p['name'].lower() != name.lower()]
        
        if len(playlists) == original_count:
            return {
                "success": False,
                "error": f"Không tìm thấy playlist: {name}"
            }
        
        if save_youtube_playlists(playlists):
            return {
                "success": True,
                "message": f"✅ Đã xóa playlist: {name}"
            }
        else:
            return {
                "success": False,
                "error": "Không thể lưu thay đổi"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_youtube_playlists() -> dict:
    """Lấy danh sách tất cả playlist YouTube"""
    try:
        playlists = load_youtube_playlists()
        return {
            "success": True,
            "playlists": playlists,
            "count": len(playlists)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_youtube_playlist(playlist_name: str) -> dict:
    """Mở playlist YouTube đã lưu trong browser
    
    Args:
        playlist_name: Tên playlist đã đăng ký (có thể là tên đầy đủ hoặc từ khóa)
    
    Returns:
        dict với thông tin playlist đã mở
    """
    try:
        import webbrowser
        
        playlists = load_youtube_playlists()
        
        if not playlists:
            return {
                "success": False,
                "error": "Chưa có playlist nào. Hãy thêm playlist trên Web UI!"
            }
        
        # Tìm playlist (exact match hoặc partial match)
        playlist_name_lower = playlist_name.lower()
        matched_playlist = None
        
        # Tìm exact match trước
        for p in playlists:
            if p['name'].lower() == playlist_name_lower:
                matched_playlist = p
                break
        
        # Nếu không có exact match, tìm partial match
        if not matched_playlist:
            for p in playlists:
                if playlist_name_lower in p['name'].lower():
                    matched_playlist = p
                    break
        
        if not matched_playlist:
            # Hiển thị danh sách playlist có sẵn
            available = [p['name'] for p in playlists]
            return {
                "success": False,
                "error": f"Không tìm thấy playlist: '{playlist_name}'",
                "available_playlists": available,
                "hint": f"Có {len(available)} playlist: {', '.join(available)}"
            }
        
        # Mở playlist trong browser
        webbrowser.open(matched_playlist['url'])
        
        print(f"🎵 [YouTube Playlist] Đã mở: {matched_playlist['name']}")
        
        return {
            "success": True,
            "message": f"✅ Đã mở playlist: {matched_playlist['name']}",
            "playlist": matched_playlist,
            "url": matched_playlist['url']
        }
        
    except Exception as e:
        print(f"❌ [YouTube Playlist] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# VLC Player Manager (Singleton)
class VLCMusicPlayer:
    """
    VLC Music Player với hỗ trợ đầy đủ:
    - Play/Pause/Stop
    - Next/Previous track
    - Playlist management
    - Media keys support (VLC tự động hỗ trợ)
    """
    _instance = None
    _player = None
    _media_list = None
    _list_player = None
    _current_playlist = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._player is None:
            try:
                import vlc
                self._vlc = vlc
                # Tạo VLC instance với options tốt nhất
                self._instance_vlc = vlc.Instance('--no-xlib --quiet')
                self._player = self._instance_vlc.media_player_new()
                self._media_list = self._instance_vlc.media_list_new()
                self._list_player = self._instance_vlc.media_list_player_new()
                self._list_player.set_media_player(self._player)
                print("✅ [VLC] VLC Music Player initialized")
            except Exception as e:
                print(f"❌ [VLC] Failed to initialize: {e}")
                self._player = None
    
    def play_file(self, file_path: str):
        """Phát 1 file nhạc"""
        if not self._player:
            return False
        try:
            media = self._instance_vlc.media_new(file_path)
            self._player.set_media(media)
            self._player.play()
            return True
        except Exception as e:
            print(f"❌ [VLC] Play error: {e}")
            return False
    
    def play_playlist(self, file_paths: list):
        """Phát playlist với nhiều bài"""
        if not self._list_player:
            return False
        try:
            # Clear playlist cũ
            self._media_list = self._instance_vlc.media_list_new()
            self._current_playlist = file_paths
            
            # Thêm tất cả bài vào playlist
            for path in file_paths:
                media = self._instance_vlc.media_new(path)
                self._media_list.add_media(media)
            
            # Set playlist và phát
            self._list_player.set_media_list(self._media_list)
            self._list_player.play()
            return True
        except Exception as e:
            print(f"❌ [VLC] Playlist error: {e}")
            return False
    
    def pause(self):
        """Tạm dừng"""
        if self._player:
            self._player.pause()
            return True
        return False
    
    def stop(self):
        """Dừng phát"""
        if self._list_player:
            self._list_player.stop()
        if self._player:
            self._player.stop()
        return True
    
    def next_track(self):
        """Bài tiếp theo"""
        if self._list_player:
            self._list_player.next()
            return True
        return False
    
    def previous_track(self):
        """Bài trước"""
        if self._list_player:
            self._list_player.previous()
            return True
        return False
    
    def is_playing(self):
        """Kiểm tra đang phát không"""
        if self._player:
            return self._player.is_playing()
        return False
    
    def get_state(self):
        """Lấy trạng thái player"""
        if not self._player:
            return "not_initialized"
        
        state = self._player.get_state()
        state_map = {
            0: "idle",
            1: "opening",
            2: "buffering", 
            3: "playing",
            4: "paused",
            5: "stopped",
            6: "ended",
            7: "error"
        }
        return state_map.get(state, "unknown")

# Global VLC player instance
vlc_player = VLCMusicPlayer()

# ============================================================
# BROWSER CONTROLLER - Selenium Automation
# ============================================================

class BrowserController:
    """Singleton class để điều khiển trình duyệt Chrome bằng Selenium"""
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _ensure_driver(self):
        """Khởi tạo Chrome driver nếu chưa có"""
        if self._driver is None:
            if not SELENIUM_AVAILABLE:
                raise Exception("Selenium chưa được cài đặt. Chạy: pip install selenium webdriver-manager")
            
            try:
                chrome_options = Options()
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--start-maximized')
                
                service = Service(ChromeDriverManager().install())
                self._driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ [Browser] Chrome driver initialized")
            except Exception as e:
                print(f"❌ [Browser] Failed to initialize: {e}")
                raise
        return self._driver
    
    def open_url(self, url: str) -> dict:
        """Mở URL trong browser"""
        try:
            driver = self._ensure_driver()
            driver.get(url)
            return {
                "success": True,
                "url": driver.current_url,
                "title": driver.title,
                "message": f"Đã mở: {driver.title}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_current_info(self) -> dict:
        """Lấy thông tin trang hiện tại"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            
            return {
                "success": True,
                "url": self._driver.current_url,
                "title": self._driver.title,
                "window_handles": len(self._driver.window_handles)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click_element(self, selector: str, by: str = "css") -> dict:
        """Click vào element"""
        try:
            driver = self._ensure_driver()
            
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            element.click()
            
            return {
                "success": True,
                "message": f"Đã click vào element: {selector}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fill_input(self, selector: str, text: str, by: str = "css") -> dict:
        """Điền text vào input field"""
        try:
            driver = self._ensure_driver()
            
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by_type, selector))
            )
            element.clear()
            element.send_keys(text)
            
            return {
                "success": True,
                "message": f"Đã điền text vào: {selector}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scroll(self, direction: str = "down", amount: int = 500) -> dict:
        """Cuộn trang"""
        try:
            driver = self._ensure_driver()
            
            if direction == "top":
                driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction == "down":
                driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                driver.execute_script(f"window.scrollBy(0, -{amount});")
            else:
                return {"success": False, "error": f"Invalid direction: {direction}"}
            
            return {
                "success": True,
                "message": f"Đã cuộn {direction}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def go_back(self) -> dict:
        """Quay lại trang trước"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            self._driver.back()
            return {"success": True, "message": "Đã quay lại trang trước"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def go_forward(self) -> dict:
        """Tiến tới trang sau"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            self._driver.forward()
            return {"success": True, "message": "Đã tiến tới trang sau"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refresh(self) -> dict:
        """Làm mới trang"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            self._driver.refresh()
            return {"success": True, "message": "Đã làm mới trang"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def screenshot(self, filepath: str = None) -> dict:
        """Chụp screenshot trang hiện tại"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"screenshot_{timestamp}.png"
            
            self._driver.save_screenshot(filepath)
            return {
                "success": True,
                "filepath": filepath,
                "message": f"Đã lưu screenshot: {filepath}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def new_tab(self, url: str = None) -> dict:
        """Mở tab mới"""
        try:
            driver = self._ensure_driver()
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            if url:
                driver.get(url)
            
            return {
                "success": True,
                "message": f"Đã mở tab mới{' và truy cập ' + url if url else ''}",
                "total_tabs": len(driver.window_handles)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_tab(self) -> dict:
        """Đóng tab hiện tại"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            
            self._driver.close()
            if len(self._driver.window_handles) > 0:
                self._driver.switch_to.window(self._driver.window_handles[-1])
            
            return {
                "success": True,
                "message": "Đã đóng tab",
                "remaining_tabs": len(self._driver.window_handles)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_script(self, script: str) -> dict:
        """Thực thi JavaScript code"""
        try:
            driver = self._ensure_driver()
            result = driver.execute_script(script)
            return {
                "success": True,
                "result": result,
                "message": "Đã thực thi JavaScript"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_browser(self) -> dict:
        """Đóng browser hoàn toàn"""
        try:
            if self._driver:
                self._driver.quit()
                self._driver = None
                return {"success": True, "message": "Đã đóng browser"}
            return {"success": False, "error": "Browser chưa được khởi động"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global browser controller instance
browser_controller = BrowserController()

async def list_music(subfolder: str = "", auto_play: bool = True) -> dict:
    """
    Liệt kê file nhạc trong music_library.
    Theo mặc định TỰ ĐỘNG PHÁT bài đầu tiên (giống xinnan-tech/xiaozhi-esp32-server).
    Set auto_play=False để chỉ liệt kê không phát.
    """
    try:
        if not MUSIC_LIBRARY.exists():
            MUSIC_LIBRARY.mkdir(exist_ok=True)
            return {"success": True, "files": [], "count": 0, "message": "Thư mục music_library đã được tạo. Hãy thêm nhạc vào!"}
        
        search_path = MUSIC_LIBRARY / subfolder if subfolder else MUSIC_LIBRARY
        
        if not search_path.exists():
            return {"success": False, "error": f"Thư mục '{subfolder}' không tồn tại"}
        
        music_files = []
        for file_path in search_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in MUSIC_EXTENSIONS:
                relative_path = file_path.relative_to(MUSIC_LIBRARY)
                music_files.append({
                    "filename": file_path.name,
                    "path": str(relative_path).replace('\\', '/'),
                    "size_mb": round(file_path.stat().st_size / (1024**2), 2),
                    "extension": file_path.suffix.lower()
                })
        
        music_files.sort(key=lambda x: x['filename'])
        
        if len(music_files) == 0:
            return {
                "success": True, 
                "files": [], 
                "count": 0,
                "message": "No music files found. Please add music files to music_library folder."
            }
        
        # 🎵 AUTO-PLAY: Tự động phát bài đầu tiên (như code reference)
        first_file = music_files[0]['filename']
        play_result = None
        
        if auto_play:
            print(f"🎵 [Auto-Play] list_music tự động phát: {first_file}")
            play_result = await play_music(first_file)
            
            if play_result.get("success"):
                message = f"✅ Auto-played: {first_file}\nTotal {len(music_files)} song(s) in library"
            else:
                message = f"❌ Found {len(music_files)} songs but failed to play: {play_result.get('error', 'Unknown error')}"
        else:
            filenames_list = [f['filename'] for f in music_files]
            message = f"Found {len(music_files)} song(s):\n" + "\n".join([f"  - {fname}" for fname in filenames_list[:10]])
            if len(music_files) > 10:
                message += f"\n  ... and {len(music_files) - 10} more"
        
        return {
            "success": True,
            "files": music_files,
            "count": len(music_files),
            "library_path": str(MUSIC_LIBRARY),
            "message": message,
            "auto_played": auto_play,
            "play_result": play_result if auto_play else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_music(filename: str, create_playlist: bool = True) -> dict:
    """
    Phát nhạc từ music_library bằng VLC player.
    
    Args:
        filename: Tên file (e.g., 'song.mp3' or 'Pop/song.mp3')
        create_playlist: Tạo playlist với tất cả bài (default True) để hỗ trợ Next/Previous
        
    Returns:
        dict with 'success', 'filename', 'path', 'message'
    """
    try:
        if not MUSIC_LIBRARY.exists():
            return {"success": False, "error": "Thư mục music_library không tồn tại"}
        
        print(f"🎵 [VLC Play] Tìm file: '{filename}'")
        
        # Tìm file
        music_path = None
        filename_lower = filename.lower()
        
        for file_path in MUSIC_LIBRARY.rglob("*"):
            if file_path.is_file():
                if (file_path.name == filename or 
                    file_path.name.lower() == filename_lower or
                    str(file_path.relative_to(MUSIC_LIBRARY)).replace('\\', '/') == filename or
                    filename_lower in file_path.name.lower()):
                    if file_path.suffix.lower() in MUSIC_EXTENSIONS:
                        music_path = file_path
                        break
        
        if not music_path:
            available = [f.name for f in MUSIC_LIBRARY.rglob("*") if f.is_file() and f.suffix.lower() in MUSIC_EXTENSIONS]
            return {
                "success": False, 
                "error": f"Không tìm thấy '{filename}'",
                "available_files": available[:5]
            }
        
        print(f"🎵 [VLC Play] Đã tìm thấy: {music_path}")
        
        if create_playlist:
            # Tạo playlist với tất cả bài trong thư mục
            all_songs = sorted([
                str(f) for f in MUSIC_LIBRARY.rglob("*") 
                if f.is_file() and f.suffix.lower() in MUSIC_EXTENSIONS
            ])
            
            # Đảm bảo bài hiện tại ở đầu playlist
            if str(music_path) in all_songs:
                all_songs.remove(str(music_path))
            all_songs.insert(0, str(music_path))
            
            success = vlc_player.play_playlist(all_songs)
            print(f"🎵 [VLC] Created playlist with {len(all_songs)} songs")
        else:
            success = vlc_player.play_file(str(music_path))
        
        if success:
            return {
                "success": True,
                "filename": music_path.name,
                "path": str(music_path.relative_to(MUSIC_LIBRARY)),
                "full_path": str(music_path),
                "size_mb": round(music_path.stat().st_size / (1024**2), 2),
                "message": f"✅ Đang phát: {music_path.name} (VLC Player)",
                "playlist_mode": create_playlist,
                "note": "Dùng media_play_pause(), media_next_track(), media_previous_track() để điều khiển!"
            }
        else:
            return {"success": False, "error": "VLC player failed to play"}
    except Exception as e:
        print(f"❌ [VLC Play] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def pause_music() -> dict:
    """Tạm dừng nhạc (VLC Player)"""
    try:
        vlc_player.pause()
        return {"success": True, "message": "⏸️ Đã tạm dừng nhạc (VLC)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def resume_music() -> dict:
    """Tiếp tục phát nhạc (VLC Player)"""
    try:
        vlc_player.pause()  # VLC pause() toggles play/pause
        return {"success": True, "message": "▶️ Đã tiếp tục phát nhạc (VLC)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def stop_music() -> dict:
    """Dừng nhạc đang phát (VLC Player)"""
    try:
        vlc_player.stop()
        return {"success": True, "message": "⏹️ Đã dừng phát nhạc (VLC)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def music_next() -> dict:
    """Chuyển bài tiếp theo trong playlist (VLC Player)"""
    try:
        success = vlc_player.next_track()
        if success:
            return {"success": True, "message": "⏭️ Đã chuyển bài tiếp theo (VLC)"}
        return {"success": False, "error": "Không có bài tiếp theo hoặc không có playlist"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def music_previous() -> dict:
    """Quay lại bài trước trong playlist (VLC Player)"""
    try:
        success = vlc_player.previous_track()
        if success:
            return {"success": True, "message": "⏮️ Đã quay lại bài trước (VLC)"}
        return {"success": False, "error": "Không có bài trước hoặc không có playlist"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_music_status() -> dict:
    """Lấy trạng thái music player (VLC)"""
    try:
        state = vlc_player.get_state()
        is_playing = vlc_player.is_playing()
        
        return {
            "success": True,
            "state": state,
            "is_playing": is_playing,
            "playlist_count": len(vlc_player._current_playlist) if vlc_player._current_playlist else 0,
            "message": f"VLC Player: {state}" + (" (Playing)" if is_playing else "")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_music(keyword: str, auto_play: bool = True) -> dict:
    """
    Tìm kiếm nhạc theo từ khóa và TỰ ĐỘNG PHÁT bài đầu tiên.
    Set auto_play=False để chỉ tìm kiếm không phát.
    """
    try:
        if not MUSIC_LIBRARY.exists():
            return {"success": False, "error": "Thư mục music_library không tồn tại"}
        
        keyword_lower = keyword.lower()
        music_files = []
        
        for file_path in MUSIC_LIBRARY.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in MUSIC_EXTENSIONS:
                if keyword_lower in file_path.name.lower():
                    relative_path = file_path.relative_to(MUSIC_LIBRARY)
                    music_files.append({
                        "filename": file_path.name,
                        "path": str(relative_path).replace('\\', '/'),
                        "size_mb": round(file_path.stat().st_size / (1024**2), 2),
                        "extension": file_path.suffix.lower()
                    })
        
        music_files.sort(key=lambda x: x['filename'])
        
        if len(music_files) == 0:
            return {
                "success": False,
                "error": f"Không tìm thấy bài hát nào với từ khóa '{keyword}'"
            }
        
        # 🎵 AUTO-PLAY: Tự động phát bài đầu tiên
        first_file = music_files[0]['filename']
        play_result = None
        
        if auto_play:
            print(f"🔍 [Search Music] Tìm thấy '{keyword}', tự động phát: {first_file}")
            play_result = await play_music(first_file)
            
            if play_result.get("success"):
                message = f"✅ Found & playing: {first_file}\nTotal {len(music_files)} match(es) for '{keyword}'"
            else:
                message = f"❌ Found {len(music_files)} songs but failed to play: {play_result.get('error', 'Unknown error')}"
        else:
            message = f"Tìm thấy {len(music_files)} kết quả cho '{keyword}'"
        
        return {
            "success": True,
            "files": music_files,
            "count": len(music_files),
            "keyword": keyword,
            "message": message,
            "auto_played": auto_play,
            "play_result": play_result if auto_play else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# QUICK WEBSITE ACCESS TOOLS
# ============================================================

async def open_youtube(search_query: str = "") -> dict:
    """Mở YouTube với từ khóa tìm kiếm (nếu có)"""
    try:
        import webbrowser
        if search_query:
            url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            message = f"Đã mở YouTube với tìm kiếm: '{search_query}'"
        else:
            url = "https://www.youtube.com"
            message = "Đã mở YouTube"
        webbrowser.open(url)
        return {"success": True, "message": message, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_youtube_video(video_title: str, auto_open: bool = True) -> dict:
    """Tìm kiếm video YouTube chính xác theo tên và mở video đó
    
    Args:
        video_title: Tên video cần tìm (có thể là tên chính xác hoặc từ khóa)
        auto_open: Tự động mở video trong browser (default: True)
    
    Returns:
        dict với thông tin video: title, link, channel, views, duration
    """
    try:
        from youtubesearchpython import VideosSearch
        import webbrowser
        
        print(f"🔍 [YouTube Search] Đang tìm kiếm: '{video_title}'")
        
        # Tìm kiếm video
        search = VideosSearch(video_title, limit=5)
        results = search.result()
        
        if not results or not results.get('result'):
            return {
                "success": False,
                "error": f"Không tìm thấy video nào với tên: '{video_title}'"
            }
        
        # Lấy video đầu tiên (khớp nhất)
        top_video = results['result'][0]
        video_id = top_video['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        result = {
            "success": True,
            "title": top_video['title'],
            "url": video_url,
            "channel": top_video['channel']['name'],
            "duration": top_video['duration'],
            "views": top_video.get('viewCount', {}).get('text', 'N/A'),
            "thumbnail": top_video['thumbnails'][0]['url'] if top_video.get('thumbnails') else None,
            "published_time": top_video.get('publishedTime', 'N/A')
        }
        
        # Thêm top 5 kết quả để user có thể chọn
        result['top_5_results'] = [
            {
                "title": vid['title'],
                "url": f"https://www.youtube.com/watch?v={vid['id']}",
                "channel": vid['channel']['name'],
                "duration": vid['duration']
            }
            for vid in results['result'][:5]
        ]
        
        if auto_open:
            webbrowser.open(video_url)
            result['message'] = f"✅ Đã mở video: {top_video['title']}"
            print(f"✅ [YouTube] Đã mở: {top_video['title']}")
        else:
            result['message'] = f"✅ Đã tìm thấy video: {top_video['title']}"
            print(f"✅ [YouTube] Tìm thấy: {top_video['title']}")
        
        return result
        
    except ImportError:
        return {
            "success": False,
            "error": "Thiếu thư viện 'youtube-search-python'. Cài đặt: pip install youtube-search-python"
        }
    except Exception as e:
        print(f"❌ [YouTube Search] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ============================================================
# BROWSER AUTOMATION TOOLS
# ============================================================

async def browser_open_url(url: str) -> dict:
    """Mở URL trong browser được điều khiển (Selenium)"""
    return browser_controller.open_url(url)

async def browser_get_info() -> dict:
    """Lấy thông tin trang hiện tại"""
    return browser_controller.get_current_info()

async def browser_click(selector: str, by: str = "css") -> dict:
    """Click vào element trên trang web
    
    Args:
        selector: CSS selector, XPath, ID, etc.
        by: Loại selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
    """
    return browser_controller.click_element(selector, by)

async def browser_fill_input(selector: str, text: str, by: str = "css") -> dict:
    """Điền text vào input field
    
    Args:
        selector: CSS selector, XPath, ID, etc.
        text: Text cần điền
        by: Loại selector ('css', 'xpath', 'id', 'name', 'class')
    """
    return browser_controller.fill_input(selector, text, by)

async def browser_scroll(direction: str = "down", amount: int = 500) -> dict:
    """Cuộn trang
    
    Args:
        direction: 'down', 'up', 'top', 'bottom'
        amount: Số pixel cuộn (nếu direction là down/up)
    """
    return browser_controller.scroll(direction, amount)

async def browser_back() -> dict:
    """Quay lại trang trước"""
    return browser_controller.go_back()

async def browser_forward() -> dict:
    """Tiến tới trang sau"""
    return browser_controller.go_forward()

async def browser_refresh() -> dict:
    """Làm mới trang"""
    return browser_controller.refresh()

async def browser_screenshot(filepath: str = None) -> dict:
    """Chụp screenshot trang hiện tại
    
    Args:
        filepath: Đường dẫn lưu file (tùy chọn, mặc định: screenshot_YYYYMMDD_HHMMSS.png)
    """
    return browser_controller.screenshot(filepath)

async def browser_new_tab(url: str = None) -> dict:
    """Mở tab mới
    
    Args:
        url: URL cần mở trong tab mới (tùy chọn)
    """
    return browser_controller.new_tab(url)

async def browser_close_tab() -> dict:
    """Đóng tab hiện tại"""
    return browser_controller.close_tab()

async def browser_execute_js(script: str) -> dict:
    """Thực thi JavaScript code trên trang
    
    Args:
        script: JavaScript code cần chạy
    """
    return browser_controller.execute_script(script)

async def browser_close() -> dict:
    """Đóng browser hoàn toàn"""
    return browser_controller.close_browser()

async def open_facebook() -> dict:
    """Mở Facebook"""
    try:
        import webbrowser
        url = "https://www.facebook.com"
        webbrowser.open(url)
        return {"success": True, "message": "Đã mở Facebook", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_google(search_query: str = "") -> dict:
    """Mở Google với từ khóa tìm kiếm (nếu có)"""
    try:
        import webbrowser
        if search_query:
            url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            message = f"Đã mở Google với tìm kiếm: '{search_query}'"
        else:
            url = "https://www.google.com"
            message = "Đã mở Google"
        webbrowser.open(url)
        return {"success": True, "message": message, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_tiktok() -> dict:
    """Mở TikTok"""
    try:
        import webbrowser
        url = "https://www.tiktok.com"
        webbrowser.open(url)
        return {"success": True, "message": "Đã mở TikTok", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_website(url: str) -> dict:
    """Mở trang web tùy chỉnh"""
    try:
        import webbrowser
        # Thêm https:// nếu chưa có
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        webbrowser.open(url)
        return {"success": True, "message": f"Đã mở trang web: {url}", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# YOUTUBE PLAYER CONTROL TOOLS
# ============================================================

async def control_youtube(action: str) -> dict:
    """
    Điều khiển YouTube player bằng keyboard shortcuts.
    Phải có cửa sổ YouTube đang active/focused.
    """
    try:
        import pyautogui
        import time

        # Định nghĩa các actions và keyboard shortcuts tương ứng
        shortcuts = {
            # Video control
            "play_pause": "k",  # K hoặc Space - Tạm dừng / Tiếp tục
            "rewind_10": "j",   # J - Lùi lại 10 giây
            "forward_10": "l",  # L - Tiến tới 10 giây
            "rewind_5": "left", # ← - Lùi lại 5 giây
            "forward_5": "right", # → - Tiến tới 5 giây
            "beginning": "home", # 0 hoặc Home - Quay về đầu video
            "end": "end",       # End - Tua đến cuối video
            "frame_back": ",",  # , - Lùi lại 1 khung hình
            "frame_forward": ".", # . - Tiến tới 1 khung hình

            # Volume control
            "volume_up": "up",    # ↑ - Tăng âm lượng 5%
            "volume_down": "down", # ↓ - Giảm âm lượng 5%
            "mute_toggle": "m",   # M - Bật / Tắt tiếng
        }

        if action not in shortcuts:
            available_actions = ", ".join(shortcuts.keys())
            return {
                "success": False,
                "error": f"Action không hợp lệ: {action}. Các actions có sẵn: {available_actions}"
            }

        key = shortcuts[action]

        # Đợi một chút để đảm bảo YouTube player đang active
        time.sleep(0.5)

        # Gửi keyboard shortcut
        if key in ["left", "right", "up", "down", "home", "end"]:
            pyautogui.press(key)
        else:
            pyautogui.press(key)

        # Mô tả action cho user
        action_descriptions = {
            "play_pause": "Tạm dừng / Tiếp tục video",
            "rewind_10": "Lùi lại 10 giây",
            "forward_10": "Tiến tới 10 giây",
            "rewind_5": "Lùi lại 5 giây",
            "forward_5": "Tiến tới 5 giây",
            "beginning": "Quay về đầu video",
            "end": "Tua đến cuối video",
            "frame_back": "Lùi lại 1 khung hình",
            "frame_forward": "Tiến tới 1 khung hình",
            "volume_up": "Tăng âm lượng 5%",
            "volume_down": "Giảm âm lượng 5%",
            "mute_toggle": "Bật / Tắt tiếng",
        }

        description = action_descriptions.get(action, action)

        return {
            "success": True,
            "message": f"✅ Đã thực hiện: {description}",
            "action": action,
            "key_pressed": key,
            "note": "Đảm bảo cửa sổ YouTube đang active/focused để lệnh có hiệu lực"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "note": "Có thể cần cài đặt pyautogui hoặc cửa sổ YouTube chưa active"
        }

# ============================================================
# NEW TOOLS FROM XIAOZHI-MCPTOOLS REFERENCE
# ============================================================

async def lock_computer() -> dict:
    """Khóa máy tính ngay lập tức"""
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True, check=True)
        return {"success": True, "message": "Máy tính đã được khóa"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def shutdown_schedule(action: str, delay: int = 0) -> dict:
    """
    Lên lịch tắt máy/khởi động lại
    action: 'shutdown', 'restart', 'cancel'
    delay: thời gian trì hoãn (giây)
    """
    try:
        action_map = {"shutdown": "/s", "restart": "/r", "cancel": "/a"}
        if action not in action_map:
            return {"success": False, "error": f"Action không hợp lệ: {action}"}
        
        if action == "cancel":
            subprocess.run("shutdown /a", shell=True, check=True)
            return {"success": True, "message": "Đã hủy lịch tắt máy"}
        else:
            subprocess.run(f"shutdown {action_map[action]} /t {delay}", shell=True, check=True)
            return {"success": True, "message": f"Đã lên lịch {action} sau {delay} giây"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def show_desktop() -> dict:
    """Hiển thị desktop (Win+D)"""
    try:
        import pyautogui
        pyautogui.hotkey('win', 'd')
        return {"success": True, "message": "Đã hiển thị desktop"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def undo_operation() -> dict:
    """Hoàn tác thao tác cuối (Ctrl+Z)"""
    try:
        import pyautogui
        pyautogui.hotkey('ctrl', 'z')
        return {"success": True, "message": "Đã thực hiện hoàn tác"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_theme(dark_mode: bool = True) -> dict:
    """Đổi theme Windows sáng/tối. Nếu dark_mode=None thì toggle"""
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        
        # Nếu dark_mode là None, toggle mode hiện tại
        if dark_mode is None:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                current_value = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
                dark_mode = (current_value == 1)  # Nếu đang sáng (1) thì chuyển sang tối (True)
        
        value = 0 if dark_mode else 1
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
        
        mode = "tối" if dark_mode else "sáng"
        return {"success": True, "message": f"Đã chuyển sang theme {mode}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def change_wallpaper(keyword: str = "", custom_path: str = "") -> dict:
    """
    Đổi hình nền desktop
    - Nếu có custom_path: dùng file được chỉ định
    - Nếu không: chọn ngẫu nhiên từ hình Windows có sẵn
    """
    try:
        import ctypes, os, random
        
        # Nếu có đường dẫn custom
        if custom_path:
            if not os.path.exists(custom_path):
                return {"success": False, "error": f"File không tồn tại: {custom_path}"}
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, custom_path, 0x01 | 0x02)
            return {"success": True, "message": f"Đã đặt hình nền: {custom_path}"}
        
        # Chọn ngẫu nhiên từ Windows wallpapers
        wallpaper_paths = [
            r"C:\Windows\Web\Wallpaper\Windows\img0.jpg",
            r"C:\Windows\Web\Wallpaper\Windows\img19.jpg",
            r"C:\Windows\Web\Wallpaper\Spotlight\img14.jpg",
            r"C:\Windows\Web\Wallpaper\Spotlight\img50.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeA\img20.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeA\img21.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeB\img24.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeB\img25.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeC\img28.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeC\img29.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeD\img32.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeD\img33.jpg",
        ]
        available = [p for p in wallpaper_paths if os.path.exists(p)]
        if not available:
            return {"success": False, "error": "Không tìm thấy hình nền Windows"}
        selected = random.choice(available)
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, selected, 0x01 | 0x02)
        return {"success": True, "message": f"Đã đổi hình nền: {os.path.basename(selected)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_desktop_path() -> dict:
    """Lấy đường dẫn thư mục Desktop"""
    try:
        user_profile = subprocess.check_output("echo %USERPROFILE%", shell=True, text=True).strip()
        desktop_path = f"{user_profile}\\Desktop"
        return {"success": True, "desktop_path": desktop_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def paste_content(content: str = "") -> dict:
    """
    Dán nội dung vào vị trí con trỏ
    Nếu content rỗng, chỉ thực hiện Ctrl+V với clipboard hiện tại
    """
    try:
        import pyperclip
        import pyautogui
        import time
        
        if content:
            # Nếu có content, copy vào clipboard trước
            pyperclip.copy(content)
            time.sleep(0.3)
        
        # Thực hiện paste
        pyautogui.hotkey('ctrl', 'v')
        
        msg = f"Đã dán: {content[:50]}..." if content else "Đã thực hiện paste"
        return {"success": True, "message": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def press_enter() -> dict:
    """Nhấn phím Enter"""
    try:
        import pyautogui
        pyautogui.press('enter')
        return {"success": True, "message": "Đã nhấn Enter"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def save_text_to_file(content: str, filename: str = "") -> dict:
    """
    Lưu văn bản do LLM soạn thành file text
    LLM có thể soạn bài viết, báo cáo, code, v.v. và lưu trực tiếp vào file
    """
    try:
        import os
        from datetime import datetime
        
        # Nếu không có filename, tự động tạo tên với timestamp
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_document_{timestamp}.txt"
        
        # Thêm .txt nếu chưa có extension
        if not filename.endswith(('.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css')):
            filename += '.txt'
        
        # Lưu vào thư mục Documents của user
        documents_path = os.path.expanduser("~\\Documents")
        save_folder = os.path.join(documents_path, "miniZ_LLM_Documents")
        
        # Tạo thư mục nếu chưa có
        os.makedirs(save_folder, exist_ok=True)
        
        # Đường dẫn file đầy đủ
        file_path = os.path.join(save_folder, filename)
        
        # Lưu nội dung
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True, 
            "message": f"📄 Đã lưu file: {filename}",
            "path": file_path,
            "size_bytes": file_size,
            "location": save_folder
        }
        
    except Exception as e:
        return {"success": False, "error": f"Không thể lưu file: {str(e)}"}


async def text_to_speech(text: str, save_audio: bool = False, filename: str = "") -> dict:
    """
    Text-to-Speech (TTS): Đọc văn bản thành giọng nói
    Sử dụng Windows SAPI (Microsoft Speech API) - có sẵn trong Windows
    """
    try:
        import win32com.client
        import os
        from datetime import datetime
        
        # Khởi tạo SAPI voice
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Lấy danh sách voices (tiếng Anh, tiếng Việt nếu có cài)
        voices = speaker.GetVoices()
        
        # Nếu muốn lưu thành file audio
        if save_audio:
            from comtypes.client import CreateObject
            from comtypes.gen import SpeechLib
            
            engine = CreateObject("SAPI.SpVoice")
            stream = CreateObject("SAPI.SpFileStream")
            
            # Tạo tên file nếu không có
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tts_audio_{timestamp}.wav"
            
            if not filename.endswith('.wav'):
                filename += '.wav'
            
            # Lưu vào Documents
            documents_path = os.path.expanduser("~\\Documents")
            save_folder = os.path.join(documents_path, "miniZ_TTS_Audio")
            os.makedirs(save_folder, exist_ok=True)
            
            file_path = os.path.join(save_folder, filename)
            
            # Mở stream và ghi audio
            stream.Open(file_path, SpeechLib.SSFMCreateForWrite)
            engine.AudioOutputStream = stream
            engine.Speak(text)
            stream.Close()
            
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "message": f"🔊 Đã đọc văn bản và lưu audio: {filename}",
                "path": file_path,
                "size_bytes": file_size,
                "text_length": len(text)
            }
        else:
            # Chỉ đọc không lưu
            speaker.Speak(text)
            
            return {
                "success": True,
                "message": f"🔊 Đã đọc văn bản ({len(text)} ký tự)",
                "text_length": len(text)
            }
        
    except ImportError:
        return {
            "success": False, 
            "error": "Thiếu module pywin32. Cài: pip install pywin32"
        }
    except Exception as e:
        return {"success": False, "error": f"TTS lỗi: {str(e)}"}


async def speech_to_text(duration: int = 5, save_transcript: bool = True, filename: str = "") -> dict:
    """
    Speech-to-Text (STT): Chuyển giọng nói thành văn bản
    Sử dụng Google Speech Recognition (cần Internet)
    """
    try:
        import speech_recognition as sr
        import os
        from datetime import datetime
        
        # Khởi tạo recognizer
        recognizer = sr.Recognizer()
        
        # Sử dụng microphone
        with sr.Microphone() as source:
            print(f"🎤 Đang lắng nghe ({duration} giây)...")
            
            # Điều chỉnh nhiễu môi trường
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Ghi âm
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            print("⏳ Đang nhận dạng giọng nói...")
            
            # Nhận dạng (Google Speech Recognition - miễn phí)
            try:
                # Thử tiếng Việt trước
                text_vi = recognizer.recognize_google(audio, language='vi-VN')
                text = text_vi
                language = "Tiếng Việt"
            except:
                try:
                    # Fallback sang tiếng Anh
                    text_en = recognizer.recognize_google(audio, language='en-US')
                    text = text_en
                    language = "English"
                except:
                    return {
                        "success": False,
                        "error": "Không nhận dạng được giọng nói. Hãy nói rõ hơn hoặc kiểm tra microphone."
                    }
        
        # Lưu transcript nếu cần
        if save_transcript and text:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stt_transcript_{timestamp}.txt"
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            documents_path = os.path.expanduser("~\\Documents")
            save_folder = os.path.join(documents_path, "miniZ_STT_Transcripts")
            os.makedirs(save_folder, exist_ok=True)
            
            file_path = os.path.join(save_folder, filename)
            
            # Lưu kèm metadata
            content = f"=== Speech-to-Text Transcript ===\n"
            content += f"Ngày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"Ngôn ngữ: {language}\n"
            content += f"Độ dài: {duration} giây\n"
            content += f"===================================\n\n"
            content += text
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"🎤 Đã nhận dạng và lưu: {filename}",
                "text": text,
                "language": language,
                "path": file_path,
                "duration": duration
            }
        else:
            return {
                "success": True,
                "message": f"🎤 Đã nhận dạng giọng nói ({language})",
                "text": text,
                "language": language,
                "duration": duration
            }
        
    except ImportError:
        return {
            "success": False,
            "error": "Thiếu module SpeechRecognition. Cài: pip install SpeechRecognition pyaudio"
        }
    except Exception as e:
        return {"success": False, "error": f"STT lỗi: {str(e)}"}


# CÁC HÀM TRÙNG LẶP ĐÃ ĐƯỢC XÓA - SỬ DỤNG PHIÊN BẢN GỐC Ở TRÊN
# minimize_all_windows -> sử dụng show_desktop
# undo_action -> sử dụng undo_operation  
# toggle_dark_mode -> sử dụng set_theme
# set_wallpaper -> đã tích hợp vào change_wallpaper
# paste_text -> sử dụng paste_content
# find_on_screen -> sử dụng find_in_document
# shutdown_computer -> sử dụng shutdown_schedule


async def find_in_document(search_text: str) -> dict:
    """Tìm kiếm trong tài liệu (Ctrl+F)"""
    try:
        import pyperclip
        import pyautogui
        import time
        
        pyautogui.press('esc')
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.1)
        
        pyperclip.copy(search_text)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        pyautogui.press('enter')
        
        return {"success": True, "message": f"Đã tìm kiếm: {search_text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# NEWS SCRAPING TOOLS
# ============================================================

async def get_vnexpress_news(category: str = "home", max_articles: int = 5) -> dict:
    """
    Lấy tin tức từ VnExpress RSS feeds
    category: home, thoi-su, goc-nhin, the-gioi, kinh-doanh, giai-tri, the-thao, phap-luat, giao-duc, suc-khoe, gia-dinh, du-lich, khoa-hoc, so-hoa, xe, cong-dong, tam-su, cuoi
    """
    try:
        import feedparser
        from bs4 import BeautifulSoup
        import requests
        
        # RSS URL mapping
        rss_urls = {
            "home": "https://vnexpress.net/rss/tin-moi-nhat.rss",
            "thoi-su": "https://vnexpress.net/rss/thoi-su.rss",
            "the-gioi": "https://vnexpress.net/rss/the-gioi.rss",
            "kinh-doanh": "https://vnexpress.net/rss/kinh-doanh.rss",
            "giai-tri": "https://vnexpress.net/rss/giai-tri.rss",
            "the-thao": "https://vnexpress.net/rss/the-thao.rss",
            "phap-luat": "https://vnexpress.net/rss/phap-luat.rss",
            "giao-duc": "https://vnexpress.net/rss/giao-duc.rss",
            "suc-khoe": "https://vnexpress.net/rss/suc-khoe.rss",
            "du-lich": "https://vnexpress.net/rss/du-lich.rss",
            "khoa-hoc": "https://vnexpress.net/rss/khoa-hoc.rss",
            "so-hoa": "https://vnexpress.net/rss/so-hoa.rss",
            "xe": "https://vnexpress.net/rss/oto-xe-may.rss",
        }
        
        rss_url = rss_urls.get(category, rss_urls["home"])
        
        print(f"📰 [News] Fetching news from: {rss_url}")
        
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            return {"success": False, "error": "Không thể lấy tin tức"}
        
        articles = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        for i, entry in enumerate(feed.entries[:max_articles]):
            try:
                article = {
                    "title": entry.get('title', 'No title'),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "description": ""
                }
                
                # Try to get description from RSS
                if 'description' in entry:
                    soup = BeautifulSoup(entry.description, 'html.parser')
                    article["description"] = soup.get_text().strip()[:200] + "..."
                
                articles.append(article)
                print(f"✅ [News] Article {i+1}: {article['title'][:50]}...")
                
            except Exception as e:
                print(f"⚠️ [News] Error parsing article {i+1}: {e}")
                continue
        
        result = {
            "success": True,
            "category": category,
            "total": len(articles),
            "articles": articles,
            "message": f"Đã lấy {len(articles)} tin tức từ VnExpress ({category})"
        }
        
        return result
        
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}


async def get_news_summary(category: str = "home") -> dict:
    """
    Lấy tóm tắt tin tức nhanh (chỉ tiêu đề)
    """
    try:
        result = await get_vnexpress_news(category=category, max_articles=10)
        
        if not result.get("success"):
            return result
        
        # Tạo summary text
        summary_lines = [f"📰 TIN TỨC {category.upper()} - VnExpress"]
        summary_lines.append("=" * 50)
        
        for i, article in enumerate(result["articles"], 1):
            summary_lines.append(f"{i}. {article['title']}")
        
        summary_text = "\n".join(summary_lines)
        
        return {
            "success": True,
            "category": category,
            "total": len(result["articles"]),
            "summary": summary_text,
            "articles": result["articles"],
            "message": f"Tóm tắt {len(result['articles'])} tin tức"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def search_news(keyword: str, max_results: int = 5) -> dict:
    """
    Tìm kiếm tin tức theo từ khóa trong các bài viết gần đây
    """
    try:
        # Get recent news from multiple categories
        categories = ["home", "thoi-su", "the-gioi", "kinh-doanh", "the-thao"]
        all_articles = []
        
        for cat in categories:
            result = await get_vnexpress_news(category=cat, max_articles=5)
            if result.get("success"):
                all_articles.extend(result["articles"])
        
        # Filter by keyword
        keyword_lower = keyword.lower()
        matched = []
        
        for article in all_articles:
            title_lower = article["title"].lower()
            desc_lower = article.get("description", "").lower()
            
            if keyword_lower in title_lower or keyword_lower in desc_lower:
                matched.append(article)
        
        matched = matched[:max_results]
        
        if not matched:
            return {
                "success": True,
                "keyword": keyword,
                "total": 0,
                "articles": [],
                "message": f"Không tìm thấy tin tức về '{keyword}'"
            }
        
        return {
            "success": True,
            "keyword": keyword,
            "total": len(matched),
            "articles": matched,
            "message": f"Tìm thấy {len(matched)} tin tức về '{keyword}'"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_gold_price() -> dict:
    """
    Lấy giá vàng từ các nguồn uy tín
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import re

        # Try multiple sources
        sources = [
            {
                "name": "Sjc.com.vn",
                "url": "https://sjc.com.vn/xml/tygiavang.xml",
                "type": "xml"
            },
            {
                "name": "BNews.vn",
                "url": "https://bnews.vn/gia-vang/t32.html",
                "type": "html"
            }
        ]

        print(f"💰 [Gold] Fetching gold prices...")

        # Try SJC XML first
        try:
            response = requests.get(sources[0]["url"], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.encoding = 'utf-8'

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                if items:
                    gold_data = []

                    for item in items[:10]:
                        try:
                            gold_item = {
                                "type": item.get('@type', 'N/A'),
                                "buy": item.get('@buy', 'N/A'),
                                "sell": item.get('@sell', 'N/A')
                            }

                            # Fallback to text content if attributes not found
                            if gold_item["type"] == 'N/A':
                                type_tag = item.find('type')
                                buy_tag = item.find('buy')
                                sell_tag = item.find('sell')

                                if type_tag:
                                    gold_item["type"] = type_tag.get_text(strip=True)
                                if buy_tag:
                                    gold_item["buy"] = buy_tag.get_text(strip=True)
                                if sell_tag:
                                    gold_item["sell"] = sell_tag.get_text(strip=True)

                            gold_data.append(gold_item)
                            print(f"✅ [Gold] {gold_item['type']}: Mua {gold_item['buy']} | Bán {gold_item['sell']}")

                        except Exception as e:
                            print(f"⚠️ [Gold] Error parsing item: {e}")
                            continue

                    if gold_data:
                        # Tạo summary
                        summary_lines = ["💰 GIÁ VÀNG HÔM NAY - SJC", "=" * 60]

                        for item in gold_data:
                            summary_lines.append(f"📊 {item['type']}")
                            summary_lines.append(f"   Mua vào: {item['buy']} VNĐ | Bán ra: {item['sell']} VNĐ")
                            summary_lines.append("")

                        summary_text = "\n".join(summary_lines)

                        return {
                            "success": True,
                            "total": len(gold_data),
                            "gold_prices": gold_data,
                            "summary": summary_text,
                            "message": f"Đã lấy giá {len(gold_data)} loại vàng",
                            "source": "SJC.com.vn"
                        }

        except Exception as e:
            print(f"⚠️ [Gold] Error with SJC source: {e}")

        # Fallback: Try giavang.org scraping
        try:
            print(f"💰 [Gold] Trying giavang.org...")
            response = requests.get('https://giavang.org/', timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for gold price tables
                tables = soup.find_all('table')
                gold_data = []

                for table in tables:
                    rows = table.find_all('tr')

                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 3:
                            # Get text from columns
                            col_texts = [col.get_text(strip=True) for col in cols]

                            # Look for gold type and prices
                            if len(col_texts) >= 3:
                                gold_type = col_texts[0]
                                buy_price = col_texts[1]
                                sell_price = col_texts[2]

                                # Check if this looks like gold data
                                if ('vàng' in gold_type.lower() or 'sjc' in gold_type.lower() or 'nhẫn' in gold_type.lower() or 'pnj' in gold_type.lower() or 'doji' in gold_type.lower()) and buy_price and sell_price:
                                    # Clean prices
                                    buy_clean = re.sub(r'[^\d]', '', buy_price)
                                    sell_clean = re.sub(r'[^\d]', '', sell_price)

                                    if buy_clean and sell_clean:
                                        # Format with dots
                                        buy_formatted = f"{int(buy_clean):,}".replace(',', '.')
                                        sell_formatted = f"{int(sell_clean):,}".replace(',', '.')

                                        gold_data.append({
                                            "type": gold_type,
                                            "buy": buy_formatted,
                                            "sell": sell_formatted
                                        })
                                        print(f"✅ [Gold] {gold_type}: Mua {buy_formatted} | Bán {sell_formatted}")

                if gold_data:
                    # Tạo summary
                    summary_lines = ["💰 GIÁ VÀNG HÔM NAY - GIAVANG.ORG", "=" * 60]

                    for item in gold_data[:15]:  # Limit to 15 items
                        summary_lines.append(f"📊 {item['type']}")
                        summary_lines.append(f"   Mua vào: {item['buy']} VNĐ | Bán ra: {item['sell']} VNĐ")
                        summary_lines.append("")

                    summary_text = "\n".join(summary_lines)

                    return {
                        "success": True,
                        "total": len(gold_data),
                        "gold_prices": gold_data,
                        "summary": summary_text,
                        "message": f"Đã lấy giá {len(gold_data)} loại vàng từ giavang.org",
                        "source": "giavang.org"
                    }

        except Exception as e:
            print(f"⚠️ [Gold] Error with giavang.org: {e}")

        # Final fallback: Return sample data
        sample_data = [
            {"type": "Vàng SJC 1L, 10L", "buy": "88.500.000", "sell": "90.000.000"},
            {"type": "Vàng SJC 5c", "buy": "88.500.000", "sell": "90.200.000"},
            {"type": "Vàng nhẫn SJC 99.99 1c, 5c", "buy": "87.800.000", "sell": "89.300.000"},
            {"type": "Vàng nhẫn SJC 99.99 0.5c", "buy": "87.800.000", "sell": "89.400.000"},
        ]

        summary_lines = ["💰 GIÁ VÀNG THAM KHẢO", "=" * 60]
        for item in sample_data:
            summary_lines.append(f"📊 {item['type']}")
            summary_lines.append(f"   Mua vào: {item['buy']} VNĐ | Bán ra: {item['sell']} VNĐ")
            summary_lines.append("")

        return {
            "success": True,
            "total": len(sample_data),
            "gold_prices": sample_data,
            "summary": "\n".join(summary_lines),
            "message": f"Giá vàng tham khảo ({len(sample_data)} loại)",
            "source": "Sample Data",
            "note": "Giá tham khảo, không thể kết nối nguồn chính thống"
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}


async def ask_gemini(prompt: str, model: str = "models/gemini-2.5-pro") -> dict:
    """
    Hỏi đáp với Google Gemini AI
    
    Args:
        prompt: Câu hỏi hoặc nội dung muốn gửi cho Gemini
        model: Tên model Gemini (mặc định: models/gemini-2.5-flash)
        
    Returns:
        dict với success, response_text, và message
    """
    try:
        # Kiểm tra Gemini có khả dụng không
        if not GEMINI_AVAILABLE:
            return {
                "success": False,
                "error": "Gemini library chưa cài đặt. Chạy: pip install google-generativeai"
            }
        
        # Kiểm tra API key
        if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
            return {
                "success": False,
                "error": "Gemini API key chưa được cấu hình. Vui lòng thêm 'gemini_api_key' vào xiaozhi_endpoints.json",
                "help": "Lấy API key tại: https://aistudio.google.com/apikey"
            }
        
        # Cấu hình Gemini với API key
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"[Gemini] Configured with API key: ...{GEMINI_API_KEY[-8:]}")
        
        # Khởi tạo model
        print(f"[Gemini] Creating model: {model}")
        gemini_model = genai.GenerativeModel(model)
        print(f"[Gemini] Model created successfully")
        
        # Gọi API trong executor để không block event loop
        print(f"[Gemini] Sending prompt: {prompt[:50]}...")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: gemini_model.generate_content(prompt)
        )
        print(f"[Gemini] Response received")
        
        # Lấy text từ response
        response_text = response.text if hasattr(response, 'text') else str(response)
        print(f"[Gemini] Response text: {response_text[:100]}...")
        
        return {
            "success": True,
            "prompt": prompt,
            "response_text": response_text,
            "model": model,
            "message": f"✅ Gemini đã trả lời (model: {model})"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Gemini] Exception caught: {type(e).__name__}")
        print(f"❌ [Gemini] Error message: {error_msg}")
        
        # Import traceback để debug
        import traceback
        traceback.print_exc()
        
        # Xử lý các lỗi phổ biến
        if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
            return {
                "success": False,
                "error": "API key không hợp lệ. Vui lòng kiểm tra lại gemini_api_key trong xiaozhi_endpoints.json",
                "help": "Lấy API key mới tại: https://aistudio.google.com/apikey"
            }
        elif "quota" in error_msg.lower():
            return {
                "success": False,
                "error": "Đã vượt quá quota API. Vui lòng chờ hoặc nâng cấp plan.",
                "details": error_msg
            }
        elif "rate limit" in error_msg.lower():
            return {
                "success": False,
                "error": "Rate limit exceeded. Vui lòng thử lại sau ít phút.",
                "details": error_msg
            }
        else:
            return {
                "success": False,
                "error": f"Lỗi khi gọi Gemini API: {error_msg}"
            }


async def ask_gpt4(prompt: str, model: str = "gpt-4o") -> dict:
    """
    Hỏi đáp với OpenAI GPT-4
    
    Args:
        prompt: Câu hỏi hoặc nội dung muốn gửi cho GPT-4
        model: Tên model OpenAI (mặc định: gpt-4o - GPT-4 Omni, nhanh và rẻ)
        
    Returns:
        dict với success, response_text, và message
    """
    try:
        # Kiểm tra OpenAI có khả dụng không
        if not OPENAI_AVAILABLE:
            return {
                "success": False,
                "error": "OpenAI library chưa cài đặt. Chạy: pip install openai"
            }
        
        # Kiểm tra API key
        if not OPENAI_API_KEY or OPENAI_API_KEY.strip() == "":
            return {
                "success": False,
                "error": "OpenAI API key chưa được cấu hình. Vui lòng thêm 'openai_api_key' vào xiaozhi_endpoints.json",
                "help": "Lấy API key tại: https://platform.openai.com/api-keys"
            }
        
        # Khởi tạo OpenAI client
        print(f"[GPT-4] Configured with API key: ...{OPENAI_API_KEY[-8:]}")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        print(f"[GPT-4] Sending prompt with model: {model}")
        
        # Gọi API trong executor để không block event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
        )
        
        print(f"[GPT-4] Response received")
        
        # Lấy text từ response
        response_text = response.choices[0].message.content
        print(f"[GPT-4] Response text: {response_text[:100]}...")
        
        return {
            "success": True,
            "prompt": prompt,
            "response_text": response_text,
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "message": f"✅ GPT-4 đã trả lời (model: {model})"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [GPT-4] Exception caught: {type(e).__name__}")
        print(f"❌ [GPT-4] Error message: {error_msg}")
        
        import traceback
        traceback.print_exc()
        
        # Xử lý các lỗi phổ biến
        if "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
            return {
                "success": False,
                "error": "OpenAI API key không hợp lệ. Vui lòng kiểm tra lại openai_api_key trong xiaozhi_endpoints.json",
                "help": "Lấy API key mới tại: https://platform.openai.com/api-keys"
            }
        elif "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            return {
                "success": False,
                "error": "Đã hết quota OpenAI. Vui lòng nạp tiền hoặc chờ quota reset.",
                "details": error_msg
            }
        elif "rate_limit" in error_msg.lower():
            return {
                "success": False,
                "error": "Rate limit exceeded. Vui lòng thử lại sau ít phút.",
                "details": error_msg
            }
        elif "model_not_found" in error_msg.lower():
            return {
                "success": False,
                "error": f"Model '{model}' không tồn tại. Thử: gpt-4o, gpt-4-turbo, gpt-3.5-turbo",
                "details": error_msg
            }
        else:
            return {
                "success": False,
                "error": f"Lỗi khi gọi OpenAI API: {error_msg}"
            }


# ============================================================
# TOOLS REGISTRY
# ============================================================

TOOLS = {
    "set_volume": {
        "handler": set_volume, 
        "description": "ĐIỀU CHỈNH âm lượng máy tính đến mức CỤ THỂ (0-100%). Use when user says: 'chỉnh âm lượng 50', 'đặt âm lượng 80', 'volume 30', 'set volume to 60', 'để âm lượng ở mức 40'. Examples: level=50 (âm lượng vừa), level=80 (to), level=20 (nhỏ), level=0 (tắt hẳn).", 
        "parameters": {"level": {"type": "integer", "description": "Mức âm lượng từ 0-100 (0=tắt hẳn, 50=vừa phải, 100=tối đa)", "required": True}}
    },
    "get_volume": {"handler": get_volume, "description": "Kiểm tra mức âm lượng hiện tại của máy tính. Use when: 'âm lượng bao nhiêu', 'check volume', 'xem âm lượng'", "parameters": {}},
    "mute_volume": {"handler": mute_volume, "description": "TẮT TIẾNG máy tính (mute) hoàn toàn. Use when: 'tắt tiếng', 'mute', 'câm', 'im lặng'", "parameters": {}},
    "unmute_volume": {"handler": unmute_volume, "description": "BẬT LẠI TIẾNG máy tính (unmute). Use when: 'bật tiếng', 'unmute', 'mở tiếng lại'", "parameters": {}},
    "volume_up": {"handler": volume_up, "description": "TĂNG âm lượng lên một chút (mỗi bước ~2%). Use when: 'tăng âm lượng', 'to hơn', 'volume up', 'lớn hơn'", "parameters": {"steps": {"type": "integer", "description": "Số bước tăng (mặc định 5 = tăng ~10%)", "required": False}}},
    "volume_down": {"handler": volume_down, "description": "GIẢM âm lượng xuống một chút (mỗi bước ~2%). Use when: 'giảm âm lượng', 'nhỏ hơn', 'volume down', 'bớt to'", "parameters": {"steps": {"type": "integer", "description": "Số bước giảm (mặc định 5 = giảm ~10%)", "required": False}}},
    "take_screenshot": {
        "handler": take_screenshot, 
        "description": "Chụp màn hình toàn bộ và LƯU FILE ẢNH. Tự động lưu vào thư mục Downloads với tên file có timestamp. Use when user asks: 'chụp màn hình', 'screenshot', 'capture screen'.", 
        "parameters": {
            "filename": {
                "type": "string",
                "description": "Tên file lưu ảnh (optional). Mặc định: screenshot_YYYYMMDD_HHMMSS.png. Ví dụ: 'my_screen.png'",
                "required": False
            }
        }
    },
    "show_notification": {"handler": show_notification, "description": "Hiển thị thông báo", "parameters": {"title": {"type": "string", "description": "Tiêu đề", "required": True}, "message": {"type": "string", "description": "Nội dung", "required": True}}},
    "get_system_resources": {"handler": get_system_resources, "description": "Tài nguyên hệ thống", "parameters": {}},
    "get_current_time": {"handler": get_current_time, "description": "Thời gian hiện tại", "parameters": {}},
    "calculator": {"handler": calculator, "description": "Tính toán", "parameters": {"expression": {"type": "string", "description": "Biểu thức", "required": True}}},
    "open_application": {
        "handler": open_application, 
        "description": "Mở ứng dụng Windows với tìm kiếm thông minh. HỖ TRỢ 50+ ỨNG DỤNG: Windows (notepad, calc, paint, cmd, taskmgr), Browsers (chrome, firefox, edge, brave), Microsoft Office (word, excel, powerpoint, outlook, teams), Adobe Creative (photoshop, illustrator, premiere, after effects, lightroom), Development (vscode, pycharm, sublime, notepad++), 3D/Design (blender, maya, autocad, solidworks, fusion360), Communication (discord, slack, zoom, telegram, zalo), Media (vlc, spotify, itunes). Hỗ trợ tên TIẾNG VIỆT ('máy tính'→Calculator, 'máy ghi chú'→Notepad). Tự động tìm trong PATH, Registry, Program Files. Ví dụ: 'photoshop', 'excel', 'chrome', 'blender'.", 
        "parameters": {
            "app_name": {
                "type": "string", 
                "description": "Tên ứng dụng (ví dụ: 'excel', 'photoshop', 'chrome', 'vscode', 'blender', 'word'). Có thể dùng tên đầy đủ ('microsoft excel') hoặc viết tắt ('ps'→Photoshop). Hỗ trợ tiếng Việt.", 
                "required": True
            }
        }
    },
    "list_running_processes": {"handler": list_running_processes, "description": "Liệt kê tiến trình", "parameters": {"limit": {"type": "integer", "description": "Số lượng", "required": False}}},
    "kill_process": {"handler": kill_process, "description": "Tắt tiến trình", "parameters": {"identifier": {"type": "string", "description": "PID hoặc tên", "required": True}}},
    "create_file": {"handler": create_file, "description": "Tạo file", "parameters": {"path": {"type": "string", "description": "Đường dẫn", "required": True}, "content": {"type": "string", "description": "Nội dung", "required": True}}},
    "read_file": {"handler": read_file, "description": "Đọc file", "parameters": {"path": {"type": "string", "description": "Đường dẫn", "required": True}}},
    "list_files": {"handler": list_files, "description": "Liệt kê files", "parameters": {"directory": {"type": "string", "description": "Thư mục", "required": True}}},
    "get_battery_status": {"handler": get_battery_status, "description": "Thông tin pin", "parameters": {}},
    "get_network_info": {"handler": get_network_info, "description": "Thông tin mạng", "parameters": {}},
    "search_web": {"handler": search_web, "description": "MỞ TRÌNH DUYỆT để tìm kiếm trên Google. CHỈ dùng khi user YÊU CẦU MỞ BROWSER để search (ví dụ: 'mở google tìm kiếm...', 'search google về...'). KHÔNG dùng để trả lời câu hỏi - hãy dùng ask_gemini thay vì search_web cho câu hỏi thông thường", "parameters": {"query": {"type": "string", "description": "Từ khóa", "required": True}}},
    
    "search_google_text": {
        "handler": search_google_text,
        "description": "TÌM KIẾM GOOGLE và trả về KẾT QUẢ DẠNG TEXT (KHÔNG mở browser). Dùng cho thông tin REAL-TIME, tin tức MỚI NHẤT, sự kiện hiện tại. Gemini chỉ biết đến 10/2024, nên dùng tool này cho thông tin sau đó (ví dụ: 'olympia 2025', 'world cup 2025', 'tin tức hôm nay'). Trả về title, link, snippet của 5 kết quả đầu.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Từ khóa tìm kiếm (ví dụ: 'olympia 2025 winner', 'latest news AI')",
                "required": True
            },
            "num_results": {
                "type": "integer",
                "description": "Số lượng kết quả (1-10, mặc định 5)",
                "required": False
            }
        }
    },
    
    # MEDIA PLAYER CONTROLS (Chủ yếu cho Spotify, YouTube, VLC - WMP có giới hạn)
    "media_play_pause": {
        "handler": media_play_pause, 
        "description": "⏯️ Phát/Tạm dừng external media players (Spotify, YouTube, VLC, iTunes, Discord, Chrome video...). Dùng Windows media keys. ⚠️ LƯU Ý: KHÔNG hoạt động tốt với music_library (Windows Media Player tự đóng sau khi phát). Dùng stop_music() để dừng music_library. Ví dụ: 'tạm dừng spotify', 'pause youtube'.", 
        "parameters": {}
    },
    "media_next_track": {
        "handler": media_next_track, 
        "description": "⏭️ Chuyển bài tiếp theo trên playlist. Hoạt động với: Spotify, YouTube playlist, VLC, iTunes. ⚠️ KHÔNG dùng cho music_library (WMP tự đóng). Ví dụ: 'bài tiếp spotify', 'next youtube'.", 
        "parameters": {}
    },
    "media_previous_track": {
        "handler": media_previous_track, 
        "description": "⏮️ Quay lại bài trước. Hoạt động với: Spotify, YouTube, VLC, iTunes. ⚠️ KHÔNG dùng cho music_library. Ví dụ: 'bài trước spotify', 'previous vlc'.", 
        "parameters": {}
    },
    "media_stop": {
        "handler": media_stop, 
        "description": "⏹️ Dừng phát external media players. Hoạt động với Spotify, VLC, YouTube. Với music_library, dùng stop_music() thay thế (đóng Windows Media Player). Ví dụ: 'stop spotify', 'dừng vlc'.", 
        "parameters": {}
    },
    "media_control": {
        "handler": media_control, 
        "description": "🎛️ Tool TỔNG HỢP điều khiển EXTERNAL media players (Spotify, YouTube, VLC, iTunes...). Hỗ trợ: play, pause, next, previous, stop, volume_up, volume_down, mute. ⚠️ KHÔNG dùng cho music_library (dùng stop_music). Best for: Spotify, YouTube, VLC. Ví dụ: media_control('next') cho Spotify, media_control('pause') cho YouTube.", 
        "parameters": {
            "action": {
                "type": "string", 
                "description": "Hành động: 'play', 'pause', 'next', 'previous', 'stop', 'volume_up', 'volume_down', 'mute'. Ví dụ: 'next', 'pause', 'mute'.", 
                "required": True
            }
        }
    },
    
    "get_active_media_players": {
        "handler": get_active_media_players,
        "description": "🔍 LẤY DANH SÁCH các media players và ứng dụng đang chạy trên máy tính. ⭐ GỌI TOOL NÀY TRƯỚC KHI ĐIỀU KHIỂN MEDIA! Tool này giúp LLM biết: (1) Có media player nào đang chạy không (Spotify, VLC, WMP...), (2) Có browser nào đang chạy (có thể đang phát YouTube), (3) Nên dùng tool nào (media_play_pause cho Spotify/VLC, stop_music cho WMP). Ví dụ: User nói 'dừng nhạc' → Gọi get_active_media_players() → Biết Spotify đang chạy → Dùng media_play_pause(). LUÔN GỌI TOOL NÀY trước khi thực hiện media control commands!",
        "parameters": {}
    },
    
    "set_brightness": {"handler": set_brightness, "description": "Độ sáng màn hình", "parameters": {"level": {"type": "integer", "description": "Độ sáng 0-100", "required": True}}},
    "get_clipboard": {"handler": get_clipboard, "description": "Lấy clipboard", "parameters": {}},
    "set_clipboard": {"handler": set_clipboard, "description": "Đặt clipboard", "parameters": {"text": {"type": "string", "description": "Nội dung", "required": True}}},
    "play_sound": {"handler": play_sound, "description": "Phát âm thanh", "parameters": {"frequency": {"type": "integer", "description": "Tần số Hz", "required": False}, "duration": {"type": "integer", "description": "Thời gian ms", "required": False}}},
    "get_disk_usage": {"handler": get_disk_usage, "description": "Thông tin đĩa", "parameters": {}},
    
    # MUSIC LIBRARY TOOLS
    "list_music": {
        "handler": list_music, 
        "description": "Liệt kê FILE NHẠC LOCAL trên máy tính (thư mục music_library - file .mp3, .wav, .flac). Dùng khi user muốn: 'xem nhạc trong máy', 'liệt kê file nhạc', 'nhạc đã tải', 'xem thư mục Pop/Rock'. KHÔNG DÙNG nếu user nói 'playlist', 'youtube', 'danh sách nhạc'. By default auto-plays first song.", 
        "parameters": {
            "subfolder": {
                "type": "string", 
                "description": "Optional subfolder name (e.g., 'Pop', 'Rock'). Leave empty to list all.", 
                "required": False
            },
            "auto_play": {
                "type": "boolean",
                "description": "Auto-play first song? Default is True (recommended). Set False to only list.",
                "required": False
            }
        }
    },
    "play_music": {
        "handler": play_music, 
        "description": "Phát nhạc LOCAL trên máy tính (từ thư mục music_library) bằng VLC Player. Dùng khi user muốn phát file nhạc ĐÃ TẢI về máy. KHÔNG dùng cho YouTube. Automatically creates playlist with all songs for next/previous track support. Example: play_music(filename='In Love.mp3', create_playlist=True)", 
        "parameters": {
            "filename": {
                "type": "string", 
                "description": "Music filename or path. Can be: 1) Exact filename: 'song.mp3', 2) Path: 'Pop/song.mp3', 3) Case-insensitive: 'SONG.MP3', 4) Partial: 'love' matches 'In Love.mp3'", 
                "required": True
            },
            "create_playlist": {
                "type": "boolean",
                "description": "Create VLC playlist with all songs (default True). Enables next/previous track navigation.",
                "required": False
            }
        }
    },
    "pause_music": {
        "handler": pause_music,
        "description": "Pause currently playing music in VLC Player. Use when user wants to pause/stop temporarily.",
        "parameters": {}
    },
    "resume_music": {
        "handler": resume_music,
        "description": "Resume playing music in VLC Player. Use when user wants to continue after pausing.",
        "parameters": {}
    },
    "stop_music": {
        "handler": stop_music, 
        "description": "Stop music playback and close VLC Player. Use when user wants to completely stop music.", 
        "parameters": {}
    },
    "music_next": {
        "handler": music_next,
        "description": "Play next track in VLC playlist. Only works when playlist was created (play_music with create_playlist=True).",
        "parameters": {}
    },
    "music_previous": {
        "handler": music_previous,
        "description": "Play previous track in VLC playlist. Only works when playlist was created (play_music with create_playlist=True).",
        "parameters": {}
    },
    "get_music_status": {
        "handler": get_music_status,
        "description": "Get current status of VLC Player: state (playing/paused/stopped), playlist count, playback info.",
        "parameters": {}
    },
    "search_music": {
        "handler": search_music, 
        "description": "Tìm kiếm nhạc LOCAL trên máy tính (từ thư mục music_library) theo từ khóa và AUTO-PLAY. Dùng khi user muốn tìm/phát file nhạc ĐÃ TẢI về máy. KHÔNG dùng cho YouTube. Perfect for: 'play songs with love', 'play rock music', 'find and play remix'. Set auto_play=False to only search without playing.", 
        "parameters": {
            "keyword": {
                "type": "string", 
                "description": "Keyword to search in filenames (e.g., 'love', 'rock', 'đa nghi'). Case-insensitive. Searches in all song names.", 
                "required": True
            },
            "auto_play": {
                "type": "boolean",
                "description": "Auto-play first found song? Default True. Set False to only search.",
                "required": False
            }
        }
    },
    
    # QUICK WEBSITE ACCESS TOOLS
    "open_youtube": {
        "handler": open_youtube, 
        "description": "Mở YouTube trong browser. Có thể tìm kiếm video ngay bằng cách thêm từ khóa. Ví dụ: 'mở youtube' hoặc 'mở youtube tìm kiếm nhạc'", 
        "parameters": {
            "search_query": {
                "type": "string", 
                "description": "Từ khóa tìm kiếm trên YouTube (tùy chọn). Để trống để mở trang chủ YouTube.", 
                "required": False
            }
        }
    },
    "search_youtube_video": {
        "handler": search_youtube_video,
        "description": "Tìm kiếm video YouTube CHÍNH XÁC theo tên và tự động mở video. Dùng khi user nói tên cụ thể của video (vd: 'mở clip Sơn Tùng MTP', 'phát video Hãy Trao Cho Anh', 'xem clip Rap Việt'). Trả về top 5 kết quả để user chọn nếu cần.",
        "parameters": {
            "video_title": {
                "type": "string",
                "description": "Tên video cần tìm (có thể là tên chính xác hoặc từ khóa chính). VD: 'Hãy Trao Cho Anh', 'Rap Việt tập 1', 'tutorial Python'",
                "required": True
            },
            "auto_open": {
                "type": "boolean",
                "description": "Tự động mở video trong browser (default: True). Set False để chỉ tìm kiếm không mở.",
                "required": False
            }
        }
    },
    "open_youtube_playlist": {
        "handler": open_youtube_playlist,
        "description": "Mở PLAYLIST YOUTUBE ONLINE (browser) - đã lưu sẵn trên Web UI. Dùng khi user nói: 'mở playlist [tên]', 'mở danh sách [tên]', 'phát playlist youtube [tên]', 'mở nhạc việt 1', 'mở nhạc hoa'. KHÔNG dùng cho file nhạc local .mp3. Chỉ dùng cho playlist YouTube đã đăng ký.",
        "parameters": {
            "playlist_name": {
                "type": "string",
                "description": "Tên playlist đã đăng ký trên Web UI. VD: 'nhạc việt 1', 'nhạc chill', 'EDM'",
                "required": True
            }
        }
    },
    
    # BROWSER AUTOMATION TOOLS
    "browser_open_url": {
        "handler": browser_open_url,
        "description": "Mở URL trong browser được điều khiển bởi Selenium (có thể tương tác với element). Khác với open_youtube/open_google là mở browser thông thường.",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL cần mở (VD: https://google.com, https://facebook.com)",
                "required": True
            }
        }
    },
    "browser_get_info": {
        "handler": browser_get_info,
        "description": "Lấy thông tin trang hiện tại (URL, title, số tab)",
        "parameters": {}
    },
    "browser_click": {
        "handler": browser_click,
        "description": "Click vào element trên trang web. Dùng để click button, link, etc.",
        "parameters": {
            "selector": {
                "type": "string",
                "description": "Selector để tìm element. VD: '#submit-btn', '.login-button', '//button[@id=\"login\"]'",
                "required": True
            },
            "by": {
                "type": "string",
                "description": "Loại selector: 'css' (default), 'xpath', 'id', 'name', 'class', 'tag'",
                "required": False
            }
        }
    },
    "browser_fill_input": {
        "handler": browser_fill_input,
        "description": "Điền text vào input field (form, search box, etc.)",
        "parameters": {
            "selector": {
                "type": "string",
                "description": "Selector của input field. VD: '#username', 'input[name=\"email\"]'",
                "required": True
            },
            "text": {
                "type": "string",
                "description": "Text cần điền vào input",
                "required": True
            },
            "by": {
                "type": "string",
                "description": "Loại selector: 'css' (default), 'xpath', 'id', 'name'",
                "required": False
            }
        }
    },
    "browser_scroll": {
        "handler": browser_scroll,
        "description": "Cuộn trang web lên/xuống",
        "parameters": {
            "direction": {
                "type": "string",
                "description": "Hướng cuộn: 'down' (default), 'up', 'top', 'bottom'",
                "required": False
            },
            "amount": {
                "type": "integer",
                "description": "Số pixel cuộn (nếu direction là down/up). Default: 500",
                "required": False
            }
        }
    },
    "browser_back": {
        "handler": browser_back,
        "description": "Quay lại trang trước trong browser",
        "parameters": {}
    },
    "browser_forward": {
        "handler": browser_forward,
        "description": "Tiến tới trang sau trong browser",
        "parameters": {}
    },
    "browser_refresh": {
        "handler": browser_refresh,
        "description": "Làm mới/reload trang hiện tại",
        "parameters": {}
    },
    "browser_screenshot": {
        "handler": browser_screenshot,
        "description": "Chụp screenshot trang web hiện tại",
        "parameters": {
            "filepath": {
                "type": "string",
                "description": "Đường dẫn lưu file (tùy chọn). VD: 'screenshot.png'. Mặc định: screenshot_YYYYMMDD_HHMMSS.png",
                "required": False
            }
        }
    },
    "browser_new_tab": {
        "handler": browser_new_tab,
        "description": "Mở tab mới trong browser",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL cần mở trong tab mới (tùy chọn)",
                "required": False
            }
        }
    },
    "browser_close_tab": {
        "handler": browser_close_tab,
        "description": "Đóng tab hiện tại",
        "parameters": {}
    },
    "browser_execute_js": {
        "handler": browser_execute_js,
        "description": "Thực thi JavaScript code trên trang web. Dùng cho các thao tác phức tạp.",
        "parameters": {
            "script": {
                "type": "string",
                "description": "JavaScript code cần chạy. VD: 'return document.title;', 'alert(\"Hello\");'",
                "required": True
            }
        }
    },
    "browser_close": {
        "handler": browser_close,
        "description": "Đóng browser hoàn toàn (đóng tất cả tab)",
        "parameters": {}
    },
    
    "open_facebook": {
        "handler": open_facebook, 
        "description": "Mở Facebook trong browser. Truy cập nhanh vào mạng xã hội phổ biến nhất.", 
        "parameters": {}
    },
    "open_google": {
        "handler": open_google, 
        "description": "MỞ TRÌNH DUYỆT Google. CHỈ dùng khi user YÊU CẦU MỞ TRANG WEB Google (ví dụ: 'mở google', 'mở trang google'). Nếu user chỉ HỎI CÂU HỎI thông thường, hãy dùng ask_gemini để TRẢ LỜI TRỰC TIẾP thay vì mở browser", 
        "parameters": {
            "search_query": {
                "type": "string", 
                "description": "Từ khóa tìm kiếm trên Google (tùy chọn). Để trống để mở trang chủ Google.", 
                "required": False
            }
        }
    },
    "open_tiktok": {
        "handler": open_tiktok, 
        "description": "Mở TikTok trong browser. Xem video ngắn trending và giải trí.", 
        "parameters": {}
    },
    "open_website": {
        "handler": open_website, 
        "description": "Mở trang web tùy chỉnh trong browser. Nhập URL đầy đủ hoặc tên miền.", 
        "parameters": {
            "url": {
                "type": "string", 
                "description": "URL của trang web (ví dụ: 'github.com' hoặc 'https://github.com/user/repo')", 
                "required": True
            }
        }
    },
    
    # YOUTUBE CONTROL TOOLS
    "control_youtube": {
        "handler": control_youtube, 
        "description": "Điều khiển YouTube player bằng keyboard shortcuts. Phải có cửa sổ YouTube đang active/focused. Hỗ trợ play/pause, tua video, điều chỉnh âm lượng, v.v.", 
        "parameters": {
            "action": {
                "type": "string", 
                "description": "Hành động điều khiển: play_pause, rewind_10, forward_10, rewind_5, forward_5, beginning, end, frame_back, frame_forward, volume_up, volume_down, mute_toggle", 
                "required": True
            }
        }
    },
    
    # NEWS TOOLS
    "get_vnexpress_news": {
        "handler": get_vnexpress_news,
        "description": "Lấy tin tức mới nhất từ VnExpress theo chủ đề. Trả về danh sách bài viết với tiêu đề, link, mô tả. Categories: home (mới nhất), thoi-su, the-gioi, kinh-doanh, giai-tri, the-thao, phap-luat, giao-duc, suc-khoe, du-lich, khoa-hoc, so-hoa, xe",
        "parameters": {
            "category": {
                "type": "string",
                "description": "Chủ đề tin tức: home, thoi-su, the-gioi, kinh-doanh, giai-tri, the-thao, phap-luat, giao-duc, suc-khoe, du-lich, khoa-hoc, so-hoa, xe. Mặc định: home",
                "required": False
            },
            "max_articles": {
                "type": "integer",
                "description": "Số lượng bài viết tối đa (1-20). Mặc định: 5",
                "required": False
            }
        }
    },
    "get_news_summary": {
        "handler": get_news_summary,
        "description": "Lấy tóm tắt nhanh tin tức (chỉ tiêu đề) từ VnExpress. Tự động lấy 10 tin mới nhất và hiển thị dạng danh sách ngắn gọn.",
        "parameters": {
            "category": {
                "type": "string",
                "description": "Chủ đề: home, thoi-su, the-gioi, kinh-doanh, giai-tri, the-thao, etc. Mặc định: home",
                "required": False
            }
        }
    },
    "search_news": {
        "handler": search_news,
        "description": "Tìm kiếm tin tức theo từ khóa trong các bài viết gần đây từ VnExpress. Tự động tìm trong nhiều chủ đề và trả về kết quả phù hợp nhất.",
        "parameters": {
            "keyword": {
                "type": "string",
                "description": "Từ khóa tìm kiếm (ví dụ: 'bóng đá', 'kinh tế', 'Covid', 'chính trị')",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Số kết quả tối đa (1-10). Mặc định: 5",
                "required": False
            }
        }
    },
    "get_gold_price": {
        "handler": get_gold_price,
        "description": "Lấy giá vàng hôm nay từ BNews RSS feed. Hiển thị giá mua vào và bán ra của các loại vàng phổ biến (SJC, 9999, nhẫn tròn, v.v.). Tự động cập nhật giá mới nhất.",
        "parameters": {}
    },
    
    # AI ASSISTANT TOOLS
    "ask_gemini": {
        "handler": ask_gemini,
        "description": "TRẢ LỜI CÂU HỎI bằng Google Gemini AI (MIỄN PHÍ 1500 requests/day). DÙNG TOOL NÀY khi user HỎI CÂU HỎI CHUNG (ví dụ: 'what is...', 'giải thích...', 'how to...', etc). Gemini sẽ TRẢ LỜI TRỰC TIẾP bằng text. Hữu ích cho: câu hỏi thông thường, phân tích, viết nội dung, dịch thuật, tính toán. Knowledge cutoff: ~10/2024.",
        "parameters": {
            "prompt": {
                "type": "string",
                "description": "Câu hỏi hoặc nội dung muốn gửi cho Gemini AI",
                "required": True
            },
            "model": {
                "type": "string",
                "description": "Tên model Gemini (mặc định: models/gemini-2.5-pro). Options: models/gemini-2.5-pro (chất lượng cao), models/gemini-2.5-flash (nhanh hơn)",
                "required": False
            }
        }
    },
    
    "ask_gpt4": {
        "handler": ask_gpt4,
        "description": "TRẢ LỜI CÂU HỎI bằng OpenAI GPT-4 (TRẢ PHÍ, cần API key). DÙNG KHI CẦN: 1) Thông tin MỚI HƠN (knowledge đến 04/2024), 2) Phân tích PHỨC TẠP, 3) Reasoning SÂU, 4) Code generation chuyên nghiệp. GPT-4 MẠN HƠN Gemini cho code và phân tích, nhưng TRẢ PHÍ (~$0.01-0.03/1K tokens). Chọn GPT-4 khi cần chất lượng tối đa.",
        "parameters": {
            "prompt": {
                "type": "string",
                "description": "Câu hỏi hoặc nội dung muốn gửi cho GPT-4",
                "required": True
            },
            "model": {
                "type": "string",
                "description": "Tên model OpenAI (mặc định: gpt-4o). Options: gpt-4o (GPT-4 Omni, nhanh & rẻ nhất), gpt-4-turbo (mạnh nhất), gpt-3.5-turbo (rẻ & nhanh)",
                "required": False
            }
        }
    },
    
    # NEW TOOLS FROM REFERENCE
    "lock_computer": {"handler": lock_computer, "description": "Khóa máy tính", "parameters": {}},
    "shutdown_schedule": {"handler": shutdown_schedule, "description": "Lên lịch tắt máy", "parameters": {"action": {"type": "string", "description": "shutdown/restart/cancel", "required": True}, "delay": {"type": "integer", "description": "Trì hoãn (giây)", "required": False}}},
    "show_desktop": {"handler": show_desktop, "description": "Hiển thị desktop (Win+D)", "parameters": {}},
    "undo_operation": {"handler": undo_operation, "description": "Hoàn tác (Ctrl+Z)", "parameters": {}},
    "set_theme": {"handler": set_theme, "description": "Đổi theme Windows", "parameters": {"dark_mode": {"type": "boolean", "description": "True=tối, False=sáng", "required": False}}},
    "change_wallpaper": {"handler": change_wallpaper, "description": "Đổi hình nền", "parameters": {"keyword": {"type": "string", "description": "Từ khóa (phong cảnh, anime...)", "required": False}}},
    "get_desktop_path": {"handler": get_desktop_path, "description": "Lấy đường dẫn Desktop", "parameters": {}},
    "paste_content": {"handler": paste_content, "description": "Dán nội dung (Ctrl+V)", "parameters": {"content": {"type": "string", "description": "Nội dung cần dán (tùy chọn)", "required": False}}},
    "press_enter": {"handler": press_enter, "description": "Nhấn Enter", "parameters": {}},
    "save_text_to_file": {
        "handler": save_text_to_file,
        "description": "LƯU VĂN BẢN do LLM soạn thành FILE. Use when: 'lưu văn bản', 'save document', 'ghi vào file', 'lưu bài viết', 'save code', 'export text'. LLM có thể soạn bài viết/báo cáo/code dài và lưu trực tiếp. File tự động lưu vào Documents\\miniZ_LLM_Documents\\ với tên có timestamp. Examples: Soạn CV→lưu file, viết báo cáo→lưu file, tạo code→lưu file.",
        "parameters": {
            "content": {
                "type": "string",
                "description": "Nội dung văn bản cần lưu (có thể rất dài). Hỗ trợ Unicode tiếng Việt, code, markdown, v.v.",
                "required": True
            },
            "filename": {
                "type": "string",
                "description": "Tên file (optional). Ví dụ: 'bao_cao.txt', 'code.py', 'cv.md'. Nếu không có, tự động tạo tên với timestamp.",
                "required": False
            }
        }
    },
    "text_to_speech": {
        "handler": text_to_speech,
        "description": "TEXT-TO-SPEECH (TTS): Đọc văn bản thành GIỌNG NÓI. Use when: 'đọc văn bản', 'text to speech', 'đọc cho tôi nghe', 'phát âm', 'nói ra'. Dùng Windows SAPI voice (có sẵn). Có thể lưu thành file WAV. Examples: 'đọc bài viết này', 'đọc và lưu audio', 'text to speech tiếng Việt'.",
        "parameters": {
            "text": {
                "type": "string",
                "description": "Văn bản cần đọc. Hỗ trợ tiếng Việt và tiếng Anh.",
                "required": True
            },
            "save_audio": {
                "type": "boolean",
                "description": "Có lưu thành file audio WAV không? (True/False). Mặc định False (chỉ đọc không lưu).",
                "required": False
            },
            "filename": {
                "type": "string",
                "description": "Tên file audio (optional). VD: 'doc_van_ban.wav'. Nếu không có, tự động tạo tên.",
                "required": False
            }
        }
    },
    "speech_to_text": {
        "handler": speech_to_text,
        "description": "SPEECH-TO-TEXT (STT): Chuyển GIỌNG NÓI thành VĂN BẢN. Use when: 'ghi âm giọng nói', 'speech to text', 'nhận dạng giọng nói', 'nghe và ghi lại', 'transcribe audio'. Dùng Google Speech Recognition (cần Internet). Hỗ trợ tiếng Việt + English. Examples: 'ghi âm 10 giây', 'nhận dạng giọng nói của tôi', 'speech to text'.",
        "parameters": {
            "duration": {
                "type": "integer",
                "description": "Thời gian ghi âm (giây). Mặc định 5 giây. VD: 10 để ghi âm 10 giây.",
                "required": False
            },
            "save_transcript": {
                "type": "boolean",
                "description": "Có lưu văn bản đã nhận dạng thành file không? (True/False). Mặc định True.",
                "required": False
            },
            "filename": {
                "type": "string",
                "description": "Tên file transcript (optional). VD: 'ghi_chu.txt'. Tự động tạo nếu không có.",
                "required": False
            }
        }
    },
    "export_conversation": {
        "handler": export_conversation_to_file,
        "description": "EXPORT LỊCH SỬ HỘI THOẠI ra file JSON. Lưu toàn bộ cuộc trò chuyện (user messages, AI responses, tool calls) với timestamp đầy đủ. Use when: 'xuất lịch sử chat', 'export conversation', 'lưu cuộc trò chuyện', 'backup chat history'. File lưu vào Documents\\miniZ_Conversations\\",
        "parameters": {
            "filename": {
                "type": "string",
                "description": "Tên file export (optional). VD: 'chat_history.json'. Tự động tạo tên với timestamp nếu không có.",
                "required": False
            }
        }
    },
    "find_in_document": {"handler": find_in_document, "description": "Tìm trong tài liệu (Ctrl+F)", "parameters": {"search_text": {"type": "string", "description": "Nội dung tìm kiếm", "required": True}}}
}

# ============================================================
# MINIZ MCP CLIENT
# ============================================================

async def handle_xiaozhi_message(message: dict) -> dict:
    method = message.get("method")
    params = message.get("params", {})
    
    if method == "initialize":
        return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "xiaozhi-final", "version": "4.3.0"}}
    elif method == "tools/list":
        tools = []
        for name, info in TOOLS.items():
            tool = {"name": name, "description": info["description"], "inputSchema": {"type": "object", "properties": {}, "required": []}}
            for pname, pinfo in info["parameters"].items():
                tool["inputSchema"]["properties"][pname] = {"type": pinfo["type"], "description": pinfo["description"]}
                if pinfo.get("required"):
                    tool["inputSchema"]["required"].append(pname)
            tools.append(tool)
        return {"tools": tools}
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        print(f"🔧 [Tool Call] {tool_name} with args: {args}")
        
        # Lưu tool call vào history
        add_to_conversation(
            role="tool",
            content=f"Tool: {tool_name}",
            metadata={
                "tool_name": tool_name,
                "arguments": args,
                "event_type": "tool_call"
            }
        )
        
        if tool_name not in TOOLS:
            error_msg = f"Error: Tool '{tool_name}' not found"
            print(f"❌ {error_msg}")
            add_to_conversation(role="tool", content=error_msg, metadata={"error": True})
            return {"content": [{"type": "text", "text": error_msg}], "isError": True}
        try:
            result = await TOOLS[tool_name]["handler"](**args)
            print(f"✅ [Tool Result] {tool_name}: {result}")
            
            # Lưu tool result vào history
            add_to_conversation(
                role="tool",
                content=json.dumps(result, ensure_ascii=False),
                metadata={
                    "tool_name": tool_name,
                    "success": result.get("success", True),
                    "event_type": "tool_result"
                }
            )
            
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
        except Exception as e:
            error_msg = f"Error calling {tool_name}: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            add_to_conversation(role="tool", content=error_msg, metadata={"error": True})
            return {"content": [{"type": "text", "text": error_msg}], "isError": True}
    return {"error": f"Unknown method: {method}"}

async def xiaozhi_websocket_client():
    global xiaozhi_connected, xiaozhi_ws, should_reconnect
    retry = 0
    while True:
        try:
            ep = endpoints_config[active_endpoint_index]
            if not ep.get("enabled") or not ep.get("token"):
                await asyncio.sleep(10)
                continue
            
            ws_url = f"wss://api.xiaozhi.me/mcp/?token={ep['token']}"
            retry += 1
            print(f"📡 [Xiaozhi] Connecting {ep['name']}... ({retry})")
            
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as ws:
                xiaozhi_ws = ws
                xiaozhi_connected = True
                should_reconnect = False  # Reset flag khi kết nối thành công
                print(f"✅ [Xiaozhi] Connected! ({ep['name']})")
                
                # Batch broadcast kết nối - tạo tasks và chạy parallel
                broadcast_msg = {"type": "endpoint_connected", "endpoint": ep['name'], "index": active_endpoint_index}
                tasks = []
                for conn in active_connections:
                    tasks.append(asyncio.create_task(conn.send_json(broadcast_msg)))
                # Chạy tất cả broadcasts cùng lúc
                await asyncio.gather(*tasks, return_exceptions=True)
                
                init_msg = {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "xiaozhi-final", "version": "4.3.0"}}, "id": 1}
                await ws.send(json.dumps(init_msg))
                
                async for msg in ws:
                    # Kiểm tra nếu cần reconnect (user đã chuyển thiết bị)
                    if should_reconnect:
                        print(f"🔄 [Xiaozhi] Reconnecting to new endpoint...")
                        await ws.close()
                        break
                    
                    try:
                        data = json.loads(msg)
                        method = data.get("method", "unknown")
                        if method != "ping":
                            print(f"📨 [{method}]")
                        response = await handle_xiaozhi_message(data)
                        await ws.send(json.dumps({"jsonrpc": "2.0", "id": data.get("id"), "result": response}))

                        # If the tool response suggests a next_action (for example list_music
                        # returning {'next_action': {'tool': 'play_music', 'parameters': {...}}}),
                        # execute it locally on the server as a fallback so music actually plays
                        # even if the remote AI/client doesn't invoke the follow-up.
                        try:
                            if isinstance(response, dict) and response.get("next_action"):
                                na = response.get("next_action")
                                next_tool = na.get("tool")
                                next_params = na.get("parameters", {}) or {}
                                # Only execute if the tool exists locally
                                if next_tool and next_tool in TOOLS:
                                    print(f"⏯️ [Auto Action] Executing suggested next_action {next_tool} with params: {next_params}")
                                    try:
                                        # call the handler (handlers may be async)
                                        handler = TOOLS[next_tool]["handler"]
                                        if asyncio.iscoroutinefunction(handler):
                                            res2 = await handler(**next_params)
                                        else:
                                            # run sync handlers in executor
                                            loop = asyncio.get_event_loop()
                                            res2 = await loop.run_in_executor(None, lambda: handler(**next_params))
                                        print(f"⏯️ [Auto Action Result] {next_tool}: {res2}")
                                    except Exception as e:
                                        print(f"❌ [Auto Action] Error executing {next_tool}: {e}")
                                        import traceback
                                        traceback.print_exc()
                        except Exception:
                            # defensive: do not let auto-action failures disrupt websocket loop
                            import traceback
                            traceback.print_exc()
                        
                        # Batch broadcast - chỉ broadcast cho methods quan trọng
                        if method in ["tools/call", "initialize"]:
                            broadcast_msg = {"type": "xiaozhi_activity", "method": method, "timestamp": datetime.now().isoformat()}
                            # Cleanup dead connections trước khi broadcast
                            dead_connections = []
                            for conn in active_connections:
                                try:
                                    await conn.send_json(broadcast_msg)
                                except Exception:
                                    dead_connections.append(conn)
                            # Remove dead connections
                            for conn in dead_connections:
                                active_connections.remove(conn)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ [Xiaozhi] JSON decode error: {e}")
                    except Exception as e:
                        print(f"⚠️ [Xiaozhi] Message handling error: {e}")
        except websockets.exceptions.WebSocketException as e:
            xiaozhi_connected = False
            wait = min(2 ** min(retry, 5), 60)
            print(f"❌ [Xiaozhi] WebSocket error: {e}")
            await asyncio.sleep(wait)
        except Exception as e:
            xiaozhi_connected = False
            wait = min(2 ** min(retry, 5), 60)
            print(f"❌ [Xiaozhi] Error: {e}")
            await asyncio.sleep(wait)

# ============================================================
# FASTAPI WEB SERVER
# ============================================================

app = FastAPI(title="miniZ MCP", version="4.3.0")

class VolumeRequest(BaseModel):
    level: int

class NotificationRequest(BaseModel):
    title: str
    message: str

class CalculatorRequest(BaseModel):
    expression: str

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 miniZ MCP - Điều Khiển Máy Tính</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; }
        
        /* SIDEBAR */
        .sidebar { width: 280px; background: #1a1a2e; color: white; padding: 30px 20px; display: flex; flex-direction: column; box-shadow: 2px 0 20px rgba(0,0,0,0.3); }
        .logo { 
            font-size: 1.5em; 
            font-weight: bold; 
            margin-bottom: 40px; 
            text-align: center; 
            padding: 20px 15px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        .logo-icon {
            width: 120px;
            height: auto;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
            transition: transform 0.3s;
        }
        .logo-icon:hover {
            transform: scale(1.05);
        }
        .logo-text {
            font-size: 1.8em;
            font-weight: 900;
            letter-spacing: 2px;
            color: #ff9a8b;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .menu-item { padding: 15px 20px; margin: 8px 0; border-radius: 10px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 12px; font-size: 1.05em; }
        .menu-item:hover { background: rgba(102, 126, 234, 0.2); transform: translateX(5px); }
        .menu-item.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
        
        /* MAIN CONTENT */
        .main-content { flex: 1; padding: 30px; overflow-y: auto; }
        .header { background: white; border-radius: 15px; padding: 25px 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #667eea; font-size: 2em; }
        .status { display: flex; gap: 20px; }
        .status-badge { padding: 8px 20px; border-radius: 20px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .status-badge.online { background: #d4edda; color: #155724; }
        .status-badge.offline { background: #f8d7da; color: #721c24; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        /* QUICK ACTIONS */
        .quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .action-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); cursor: pointer; transition: all 0.3s; text-align: center; }
        .action-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }
        .action-card.blue { border-left: 5px solid #3b82f6; }
        .action-card.green { border-left: 5px solid #10b981; }
        .action-card.orange { border-left: 5px solid #f59e0b; }
        .action-card.red { border-left: 5px solid #ef4444; }
        .action-card.purple { border-left: 5px solid #8b5cf6; }
        .action-card.cyan { border-left: 5px solid #06b6d4; }
        .action-card.pink { border-left: 5px solid #ec4899; }
        .action-card.indigo { border-left: 5px solid #6366f1; }
        .action-card .icon { font-size: 2.5em; margin-bottom: 10px; }
        .action-card .title { font-weight: 600; color: #333; font-size: 1.1em; }
        
        /* TOOLS SECTION */
        .tools-section { background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .tools-tabs { display: flex; gap: 15px; margin-bottom: 25px; border-bottom: 2px solid #e5e7eb; padding-bottom: 15px; }
        .tab-btn { padding: 12px 30px; border: none; border-radius: 10px 10px 0 0; background: transparent; color: #666; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1em; }
        .tab-btn:hover { background: rgba(102, 126, 234, 0.1); color: #667eea; }
        .tab-btn.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; box-shadow: 0 -4px 15px rgba(102, 126, 234, 0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        
        /* TOOL CARDS */
        .tool-card { background: #f9fafb; padding: 25px; border-radius: 12px; border: 2px solid #e5e7eb; }
        .tool-card h3 { color: #667eea; margin-bottom: 15px; font-size: 1.2em; display: flex; align-items: center; gap: 10px; }
        .tool-card input, .tool-card select, .tool-card textarea { width: 100%; padding: 12px; margin-top: 10px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; }
        .tool-card button { width: 100%; padding: 14px; margin-top: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1em; }
        .tool-card button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }
        
        /* CONFIG SECTION */
        .config-section { background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .device-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .device-card { background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb; }
        .device-card.active { border-color: #10b981; background: #d4edda; }
        .device-card h4 { color: #667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .device-card input { width: 100%; padding: 10px; margin-top: 8px; border: 2px solid #e5e7eb; border-radius: 6px; }
        .device-card button { padding: 10px 20px; margin-top: 10px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; }
        
        /* LOG */
        .log-panel { background: #1a1a2e; color: white; border-radius: 15px; padding: 25px; max-height: 400px; overflow-y: auto; font-family: 'Courier New', monospace; box-shadow: 0 10px 30px rgba(0,0,0,0.12); }
        .log-entry { padding: 8px; margin: 5px 0; border-left: 3px solid #667eea; background: rgba(102, 126, 234, 0.1); border-radius: 4px; }
        .log-time { color: #9ca3af; margin-right: 10px; }
        .log-success { color: #10b981; border-left-color: #10b981; }
        .log-error { color: #ef4444; border-left-color: #ef4444; }
        .log-info { color: #3b82f6; border-left-color: #3b82f6; }
        
        /* SETTINGS ICON */
        .settings-icon { font-size: 1.8em; cursor: pointer; transition: all 0.3s; padding: 10px; border-radius: 50%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; width: 50px; height: 50px; }
        .settings-icon:hover { transform: rotate(90deg); background: #667eea; color: white; }
        
        /* MODAL POPUP */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); animation: fadeIn 0.3s; }
        .modal-content { background: white; margin: 5% auto; padding: 0; border-radius: 15px; width: 90%; max-width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); animation: slideDown 0.3s; }
        .modal-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 30px; border-radius: 15px 15px 0 0; display: flex; justify-content: space-between; align-items: center; }
        .modal-header h2 { margin: 0; font-size: 1.5em; }
        .close-btn { font-size: 2em; cursor: pointer; color: white; background: none; border: none; line-height: 1; transition: transform 0.2s; }
        .close-btn:hover { transform: scale(1.2); }
        .modal-body { padding: 30px; }
        .modal-body label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        .modal-body input { width: 100%; padding: 12px; margin-bottom: 20px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; transition: border-color 0.3s; }
        .modal-body input:focus { outline: none; border-color: #667eea; }
        .modal-footer { padding: 20px 30px; background: #f9fafb; border-radius: 0 0 15px 15px; display: flex; gap: 15px; justify-content: flex-end; }
        .modal-btn { padding: 12px 30px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1em; }
        .modal-btn.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .modal-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }
        .modal-btn.secondary { background: #e5e7eb; color: #666; }
        .modal-btn.secondary:hover { background: #d1d5db; }
        .modal-btn.info { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; }
        .modal-btn.info:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(23, 162, 184, 0.4); }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideDown { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        
        /* FOOTER MINIZ - Compact corner style */
        .footer-miniz { position: fixed; bottom: 20px; right: 20px; background: rgba(26, 26, 46, 0.95); color: white; padding: 12px 18px; border-radius: 50px; box-shadow: 0 5px 25px rgba(0,0,0,0.3); display: flex; align-items: center; gap: 12px; z-index: 1000; transition: all 0.3s; backdrop-filter: blur(10px); }
        .footer-miniz:hover { transform: translateY(-3px); box-shadow: 0 8px 35px rgba(102, 126, 234, 0.5); }
        .footer-logo-compact { display: flex; align-items: center; gap: 10px; }
        .footer-logo-compact img { width: 35px; height: 35px; border-radius: 50%; border: 2px solid #667eea; box-shadow: 0 0 10px rgba(102, 126, 234, 0.6); }
        .footer-brand-compact { font-size: 0.95em; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .footer-separator { width: 1px; height: 25px; background: rgba(255,255,255,0.3); }
        .footer-youtube-compact { display: flex; align-items: center; gap: 6px; padding: 8px 15px; background: #FF0000; color: white; border-radius: 25px; text-decoration: none; font-weight: 600; font-size: 0.85em; transition: all 0.3s; }
        .footer-youtube-compact:hover { background: #cc0000; transform: scale(1.05); }
        .footer-youtube-compact svg { width: 18px; height: 18px; fill: white; }
        
        @media (max-width: 768px) {
            .footer-miniz { bottom: 10px; right: 10px; padding: 10px 14px; }
            .footer-brand-compact { font-size: 0.85em; }
            .footer-youtube-compact { padding: 6px 12px; font-size: 0.8em; }
        }
    </style>
</head>
<body>
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="logo">
            <img src="/logo.png" alt="miniZ MCP Logo" class="logo-icon" />
            <div class="logo-text">miniZ MCP</div>
            <small style="font-size:0.55em;opacity:0.9;font-weight:600;letter-spacing:1px;">ĐIỀU KHIỂN MÁY TÍNH</small>
        </div>
        <div class="menu-item active" onclick="showSection('dashboard')">📊Sidebar</div>
        <div class="menu-item" onclick="showSection('tools')">🛠️ Công Cụ</div>
        <div class="menu-item" onclick="showSection('playlist')">🎵 Playlist YouTube</div>
    </div>
    
    <!-- MAIN CONTENT -->
    <div class="main-content">
        <!-- HEADER -->
        <div class="header">
            <h1>Dashboard</h1>
            <div class="status">
                <div class="settings-icon" onclick="openSettingsModal()" title="Cấu hình Endpoint">⚙️</div>
                <div class="status-badge" id="xiaozhi-status">
                    <span class="status-dot"></span>
                    <span id="xiaozhi-text">Connecting...</span>
                </div>
                <div class="status-badge online">
                    <span class="status-dot"></span>
                    Web Server
                </div>
            </div>
        </div>
        
        <!-- DASHBOARD SECTION -->
        <div id="dashboard-section">
            <h2 style="color:#667eea;margin-bottom:20px;">🚀 Tất cả công cụ (38 Tools)</h2>
            <div class="quick-actions">
                <!-- AI ASSISTANT (2) - NEW -->
                <div class="action-card purple" onclick="askGemini()"><div class="icon">🤖</div><div class="title">Hỏi Gemini AI</div></div>
                <div class="action-card indigo" onclick="askGPT4()"><div class="icon">🧠</div><div class="title">Hỏi GPT-4</div></div>
                
                <!-- HỆ THỐNG (5) -->
                <div class="action-card blue" onclick="setVolumePrompt()"><div class="icon">🔊</div><div class="title">Điều Chỉnh Âm Lượng</div></div>
                <div class="action-card cyan" onclick="screenshot()"><div class="icon">📸</div><div class="title">Chụp Màn Hình</div></div>
                <div class="action-card purple" onclick="notification()"><div class="icon">�</div><div class="title">Thông Báo</div></div>
                <div class="action-card green" onclick="getResources()"><div class="icon">💻</div><div class="title">Tài Nguyên Hệ Thống</div></div>
                <div class="action-card orange" onclick="setBrightness()"><div class="icon">🔆</div><div class="title">Độ Sáng Màn Hình</div></div>
                
                <!-- FILE & PROCESS (7) -->
                <div class="action-card indigo" onclick="openApp()"><div class="icon">🚀</div><div class="title">Mở Ứng Dụng</div></div>
                <div class="action-card blue" onclick="listProcesses()"><div class="icon">�</div><div class="title">Tiến Trình Đang Chạy</div></div>
                <div class="action-card red" onclick="killProcess()"><div class="icon">❌</div><div class="title">Tắt Tiến Trình</div></div>
                <div class="action-card green" onclick="createFile()"><div class="icon">�</div><div class="title">Tạo File Mới</div></div>
                <div class="action-card cyan" onclick="readFile()"><div class="icon">📖</div><div class="title">Đọc File</div></div>
                <div class="action-card purple" onclick="listFiles()"><div class="icon">📂</div><div class="title">Liệt Kê Files</div></div>
                <div class="action-card orange" onclick="diskUsage()"><div class="icon">�</div><div class="title">Thông Tin Đĩa</div></div>
                
                <!-- MẠNG & WEB (3) -->
                <div class="action-card blue" onclick="networkInfo()"><div class="icon">🌐</div><div class="title">Thông Tin Mạng</div></div>
                <div class="action-card green" onclick="batteryStatus()"><div class="icon">🔋</div><div class="title">Thông Tin Pin</div></div>
                <div class="action-card indigo" onclick="searchWeb()"><div class="icon">🔍</div><div class="title">Tìm Kiếm Google</div></div>
                
                <!-- TIỆN ÍCH (5) -->
                <div class="action-card pink" onclick="calculator()"><div class="icon">🧮</div><div class="title">Máy Tính</div></div>
                <div class="action-card cyan" onclick="getCurrentTime()"><div class="icon">�</div><div class="title">Thời Gian</div></div>
                <div class="action-card purple" onclick="getClipboard()"><div class="icon">📋</div><div class="title">Lấy Clipboard</div></div>
                <div class="action-card orange" onclick="setClipboard()"><div class="icon">📝</div><div class="title">Đặt Clipboard</div></div>
                <div class="action-card red" onclick="playSound()"><div class="icon">🔊</div><div class="title">Phát Âm Thanh</div></div>
                
                <!-- NEW TOOLS -->
                <div class="action-card blue" onclick="lockComputer()"><div class="icon">🔒</div><div class="title">Khóa Máy Tính</div></div>
                <div class="action-card red" onclick="shutdownSchedule()"><div class="icon">⏰</div><div class="title">Lên Lịch Tắt Máy</div></div>
                <div class="action-card green" onclick="showDesktop()"><div class="icon">🖥️</div><div class="title">Hiển Thị Desktop</div></div>
                <div class="action-card orange" onclick="undoOperation()"><div class="icon">↩️</div><div class="title">Hoàn Tác</div></div>
                <div class="action-card purple" onclick="setTheme()"><div class="icon">🎨</div><div class="title">Đổi Theme</div></div>
                <div class="action-card cyan" onclick="changeWallpaper()"><div class="icon">🖼️</div><div class="title">Đổi Hình Nền</div></div>
                <div class="action-card indigo" onclick="getDesktopPath()"><div class="icon">📁</div><div class="title">Đường Dẫn Desktop</div></div>
                <div class="action-card pink" onclick="pasteContent()"><div class="icon">📋</div><div class="title">Dán Nội Dung</div></div>
                <div class="action-card blue" onclick="pressEnter()"><div class="icon">⏎</div><div class="title">Nhấn Enter</div></div>
                <div class="action-card green" onclick="findInDocument()"><div class="icon">🔎</div><div class="title">Tìm Trong Tài Liệu</div></div>
            </div>
            
            <!-- LOG PANEL AT BOTTOM OF DASHBOARD -->
            <div style="margin-top: 30px;">
                <h2 style="color:#667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <span>📋 Log Hoạt Động</span>
                    <span style="font-size: 0.6em; color: #9ca3af; font-weight: 400;">(Thời gian thực)</span>
                </h2>
                <div class="log-panel" id="log"></div>
            </div>
        </div>

        <!-- TOOLS SECTION -->
        <div id="tools-section" style="display:none;">
            <div class="tools-section">
                <h2 style="color:#667eea;margin-bottom:20px;">🛠️ Công Cụ (20 Tools)</h2>
                
                <div class="tools-tabs">
                    <button class="tab-btn active" onclick="switchTab(0)">🎛️ Hệ thống</button>
                    <button class="tab-btn" onclick="switchTab(1)">📁 File & Process</button>
                    <button class="tab-btn" onclick="switchTab(2)">🌐 Mạng & Web</button>
                    <button class="tab-btn" onclick="switchTab(3)">🔧 Tiện ích</button>
                </div>
                
                <!-- TAB 1: HỆ THỐNG -->
                <div class="tab-content active" id="tab-0">
                    <div class="tool-card">
                        <h3>🔊 Điều chỉnh âm lượng</h3>
                        <input type="number" id="volume" min="0" max="100" value="50" placeholder="0-100">
                        <button onclick="
                            const level = parseInt(document.getElementById('volume').value);
                            if (isNaN(level) || level < 0 || level > 100) {
                                addLog('❌ Âm lượng phải từ 0-100', 'error');
                            } else {
                                callAPI('/api/volume', {level: level});
                            }
                        ">Đặt âm lượng</button>
                    </div>
                    <div class="tool-card">
                        <h3>📸 Chụp màn hình</h3>
                        <button onclick="callAPI('/api/screenshot', {})">Chụp màn hình ngay</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔔 Thông báo</h3>
                        <input type="text" id="notif-title" placeholder="Tiêu đề">
                        <input type="text" id="notif-message" placeholder="Nội dung">
                        <button onclick="
                            const title = document.getElementById('notif-title').value.trim();
                            const message = document.getElementById('notif-message').value.trim();
                            if (!title || !message) {
                                addLog('❌ Vui lòng nhập tiêu đề và nội dung', 'error');
                            } else {
                                callAPI('/api/notification', {title: title, message: message});
                            }
                        ">Hiển thị</button>
                    </div>
                    <div class="tool-card">
                        <h3>💻 Tài nguyên hệ thống</h3>
                        <button onclick="getResources()">Làm mới</button>
                        <div id="resources" style="margin-top:15px;">
                            <div>CPU: <span id="cpu">--%</span></div>
                            <div>RAM: <span id="ram">--%</span></div>
                            <div>Disk: <span id="disk">--%</span></div>
                        </div>
                    </div>
                    <div class="tool-card">
                        <h3>🔆 Độ sáng màn hình</h3>
                        <input type="number" id="brightness" min="0" max="100" value="50" placeholder="0-100">
                        <button onclick="
                            const level = parseInt(document.getElementById('brightness').value);
                            if (isNaN(level) || level < 0 || level > 100) {
                                addLog('❌ Độ sáng phải từ 0-100', 'error');
                            } else {
                                callTool('set_brightness', {level: level});
                            }
                        ">Đặt độ sáng</button>
                    </div>
                </div>
                
                <!-- TAB 2: FILE & PROCESS -->
                <div class="tab-content" id="tab-1">
                    <div class="tool-card">
                        <h3>🚀 Mở ứng dụng</h3>
                        <select id="app-name">
                            <option value="notepad">📝 Notepad</option>
                            <option value="calc">🧮 Calculator</option>
                            <option value="paint">🎨 Paint</option>
                            <option value="cmd">⌨️ CMD</option>
                            <option value="explorer">📂 Explorer</option>
                        </select>
                        <button onclick="callTool('open_application', {app_name: document.getElementById('app-name').value})">Mở</button>
                    </div>
                    <div class="tool-card">
                        <h3>📋 Tiến trình đang chạy</h3>
                        <input type="number" id="proc-limit" min="5" max="50" value="10" placeholder="Số lượng">
                        <button onclick="callTool('list_running_processes', {limit: parseInt(document.getElementById('proc-limit').value)})">Xem danh sách</button>
                    </div>
                    <div class="tool-card">
                        <h3>❌ Tắt tiến trình</h3>
                        <input type="text" id="kill-proc" placeholder="PID hoặc tên">
                        <button onclick="callTool('kill_process', {identifier: document.getElementById('kill-proc').value})">Tắt tiến trình</button>
                    </div>
                    <div class="tool-card">
                        <h3>📝 Tạo file mới</h3>
                        <input type="text" id="file-path" placeholder="C:/test.txt">
                        <textarea id="file-content" placeholder="Nội dung..." style="min-height:80px;"></textarea>
                        <button onclick="callTool('create_file', {path: document.getElementById('file-path').value, content: document.getElementById('file-content').value})">Tạo file</button>
                    </div>
                    <div class="tool-card">
                        <h3>📖 Đọc file</h3>
                        <input type="text" id="read-path" placeholder="C:/test.txt">
                        <button onclick="callTool('read_file', {path: document.getElementById('read-path').value})">Đọc file</button>
                    </div>
                    <div class="tool-card">
                        <h3>📂 Liệt kê files</h3>
                        <input type="text" id="list-dir" placeholder="C:/Users">
                        <button onclick="callTool('list_files', {directory: document.getElementById('list-dir').value})">Xem files</button>
                    </div>
                    <div class="tool-card">
                        <h3>💾 Thông tin đĩa</h3>
                        <button onclick="callTool('get_disk_usage', {})">Xem chi tiết</button>
                    </div>
                </div>
                
                <!-- TAB 3: MẠNG & WEB -->
                <div class="tab-content" id="tab-2">
                    <div class="tool-card">
                        <h3>🌐 Thông tin mạng</h3>
                        <button onclick="callTool('get_network_info', {})">Xem IP & hostname</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔋 Thông tin pin</h3>
                        <button onclick="callTool('get_battery_status', {})">Kiểm tra pin</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔍 Tìm kiếm Google</h3>
                        <input type="text" id="search-query" placeholder="Nhập từ khóa...">
                        <button onclick="callTool('search_web', {query: document.getElementById('search-query').value})">Tìm kiếm</button>
                    </div>
                </div>
                
                <!-- TAB 4: TIỆN ÍCH -->
                <div class="tab-content" id="tab-3">
                    <div class="tool-card">
                        <h3>🧮 Máy tính</h3>
                        <input type="text" id="calc-expr" placeholder="2+2*3">
                        <button onclick="calculate()">Tính toán</button>
                        <div id="calc-result" style="margin-top:10px;font-size:1.5em;font-weight:bold;color:#667eea;"></div>
                    </div>
                    <div class="tool-card">
                        <h3>🕐 Thời gian</h3>
                        <button onclick="getCurrentTime()">Lấy thời gian</button>
                        <div id="time-result" style="margin-top:10px;font-size:1.2em;color:#667eea;"></div>
                    </div>
                    <div class="tool-card">
                        <h3>📋 Lấy clipboard</h3>
                        <button onclick="callTool('get_clipboard', {})">Xem nội dung</button>
                    </div>
                    <div class="tool-card">
                        <h3>📝 Đặt clipboard</h3>
                        <input type="text" id="clip-text" placeholder="Nội dung cần copy">
                        <button onclick="callTool('set_clipboard', {text: document.getElementById('clip-text').value})">Copy vào clipboard</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔊 Phát âm thanh</h3>
                        <input type="number" id="sound-freq" min="200" max="2000" value="1000" placeholder="Tần số Hz">
                        <input type="number" id="sound-dur" min="100" max="3000" value="500" placeholder="Thời gian ms">
                        <button onclick="callTool('play_sound', {frequency: parseInt(document.getElementById('sound-freq').value), duration: parseInt(document.getElementById('sound-dur').value)})">Phát beep</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- CONFIG SECTION - HIDDEN (Replaced by Modal) -->
        <div id="config-section" style="display:none;">
            <div class="config-section">
                <h2 style="color:#667eea;margin-bottom:20px;">⚙️ Cấu hình hiện tại</h2>
                <p style="color:#666;margin-bottom:20px;">Sử dụng icon ⚙️ ở góc phải trên để thay đổi endpoint</p>
                <div id="current-endpoint-info" style="background:#f9fafb;padding:20px;border-radius:12px;border:2px solid #e5e7eb;">
                    <p><strong>Thiết bị đang hoạt động:</strong> <span id="current-device-name">-</span></p>
                    <p><strong>Token:</strong> <span id="current-device-token" style="font-family:monospace;font-size:0.9em;word-break:break-all;">-</span></p>
                </div>
            </div>
        </div>
        
        <!-- PLAYLIST SECTION -->
        <div id="playlist-section" style="display:none;">
            <div style="background: white; border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
                <h2 style="color:#667eea; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 15px;">
                    <span>🎵 Danh Sách Nhạc YouTube</span>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <input id="playlist-command" placeholder="Gõ từ khóa playlist (vd: nhạc, chill...)" style="padding:8px 12px; border-radius:8px; border:1px solid #e5e7eb; font-size:0.95em; width:280px;" 
                               onkeypress="if(event.key==='Enter') triggerPlayByName(this.value.trim())" />
                        <button onclick="triggerPlayByName(document.getElementById('playlist-command').value.trim())" style="padding:8px 12px; background:#667eea; color:white; border:none; border-radius:8px; cursor:pointer;">Mở</button>
                    </div>
                </h2>

                <div style="display:flex; gap:20px; align-items:flex-start;">
                    <div style="flex:1;">
                        <div id="playlist-list" style="background:#f9fafb; padding:12px; border-radius:8px; min-height:80px; border:1px solid #e5e7eb;">
                            <!-- playlists will be rendered here -->
                        </div>
                        <div style="margin-top:12px; display:flex; gap:10px;">
                            <button onclick="promptAddPlaylist()" style="padding:10px 14px; border-radius:8px; background:linear-gradient(135deg,#10b981,#059669); color:white; border:none; cursor:pointer; font-weight:600;">＋ Thêm Playlist</button>
                            <button onclick="renderPlaylists()" style="padding:10px 14px; border-radius:8px; background:#e5e7eb; border:none; cursor:pointer;">Làm mới</button>
                        </div>
                    </div>
                    <div style="width:320px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:14px; border-radius:12px;">
                            <div style="font-weight:700; margin-bottom:6px;">Hướng dẫn nhanh</div>
                            <div style="font-size:0.95em; opacity:0.95;">
                                • Nhấn <b>＋ Thêm Playlist</b> để thêm mới (tên + URL)<br>
                                • Gõ <b>từ khóa</b> (không cần chính xác) vào ô và nhấn <b>Mở</b><br>
                                • Ví dụ: gõ "nhạc" sẽ tìm "Nhạc chill", "Nhạc EDM"...<br>
                                • Voice: "mở danh sách [từ khóa]" hoặc "mở playlist [từ khóa]"
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- SETTINGS MODAL -->
        <div id="settingsModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>⚙️ Cấu hình Endpoint</h2>
                    <button class="close-btn" onclick="closeSettingsModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <label for="endpoint-url">Endpoint (JWT Token hoặc URL đầy đủ):</label>
                    <input type="text" id="endpoint-url" placeholder="Nhập JWT token hoặc URL đầy đủ wss://api.xiaozhi.me/mcp/?token=..." />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Lưu ý:</strong> Có thể nhập JWT token trực tiếp hoặc URL đầy đủ <code>wss://api.xiaozhi.me/mcp/?token=...</code> - hệ thống sẽ tự động xử lý
                    </p>
                    
                    <hr style="margin:25px 0;border:none;border-top:2px solid #e5e7eb;">
                    
                    <label for="gemini-api-key" style="display:flex;align-items:center;gap:10px;">
                        🤖 Gemini API Key 
                        <span style="color:#10b981;font-size:0.85em;font-weight:normal;">(Auto-save)</span>
                    </label>
                    <input 
                        type="text" 
                        id="gemini-api-key" 
                        placeholder="AIzaSyXXXXXXXXXXXXXXXXXX..."
                        oninput="autoSaveGeminiKey()"
                        style="font-family:monospace;font-size:0.9em;"
                    />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Miễn phí:</strong> Lấy API key tại 
                        <a href="https://aistudio.google.com/apikey" target="_blank" style="color:#667eea;">
                            aistudio.google.com/apikey
                        </a>
                        <br>
                        <span id="gemini-key-status" style="color:#10b981;font-weight:600;"></span>
                    </p>
                    
                    <hr style="margin:25px 0;border:none;border-top:2px solid #e5e7eb;">
                    
                    <label for="openai-api-key" style="display:flex;align-items:center;gap:10px;">
                        🧠 OpenAI API Key (GPT-4)
                        <span style="color:#10b981;font-size:0.85em;font-weight:normal;">(Auto-save)</span>
                        <span style="color:#ef4444;font-size:0.75em;font-weight:normal;">TRẢ PHÍ</span>
                    </label>
                    <input 
                        type="text" 
                        id="openai-api-key" 
                        placeholder="sk-proj-XXXXXXXXXXXXXXXXXX..."
                        oninput="autoSaveOpenAIKey()"
                        style="font-family:monospace;font-size:0.9em;"
                    />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Trả phí:</strong> Lấy API key tại 
                        <a href="https://platform.openai.com/api-keys" target="_blank" style="color:#667eea;">
                            platform.openai.com/api-keys
                        </a>
                        <br>
                        <span style="font-size:0.85em;">💰 Giá: $0.01-0.03/1K tokens | 🆓 Free trial: $5 credit</span>
                        <br>
                        <span id="openai-key-status" style="color:#10b981;font-weight:600;"></span>
                    </p>
                </div>
                <div class="modal-footer">
                    <button class="modal-btn secondary" onclick="closeSettingsModal()">Hủy</button>
                    <button class="modal-btn info" onclick="copyFullUrl()">📋 Copy URL đầy đủ</button>
                    <button class="modal-btn primary" onclick="saveEndpoint()">💾 Lưu</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws;
        
        // Section switching
        function showSection(name) {
            document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('dashboard-section').style.display = name === 'dashboard' ? 'block' : 'none';
            document.getElementById('tools-section').style.display = name === 'tools' ? 'block' : 'none';
            document.getElementById('playlist-section').style.display = name === 'playlist' ? 'block' : 'none';
            
            // Load playlist when opening playlist section
            if (name === 'playlist') {
                // use initPlaylists() (render existing playlists) - loadPlaylistSection was removed
                initPlaylists();
            }
        }
        
        // Tab switching
        function switchTab(index) {
            document.querySelectorAll('.tab-btn').forEach((btn, i) => btn.classList.toggle('active', i === index));
            document.querySelectorAll('.tab-content').forEach((content, i) => content.classList.toggle('active', i === index));
        }
        
        // Quick actions - 20 tools
        function setVolumePrompt() {
            const level = prompt('Nhập âm lượng (0-100):', '50');
            if (level === null) return;
            const levelNum = parseInt(level);
            if (isNaN(levelNum) || levelNum < 0 || levelNum > 100) {
                addLog('❌ Âm lượng phải từ 0-100', 'error');
                return;
            }
            setVolumeQuick(levelNum);
        }
        function setVolumeQuick(level) { 
            if (level >= 0 && level <= 100) {
                callTool('set_volume', {level});
            } else {
                addLog('❌ Âm lượng phải từ 0-100', 'error');
            }
        }
        function getVolumeInfo() {
            callTool('get_volume', {});
        }
        function screenshot() { callAPI('/api/screenshot', {}); }
        function notification() { callAPI('/api/notification', {title: 'Xiaozhi', message: 'Test notification'}); }
        function setBrightness() { 
            const level = prompt('Nhập độ sáng (0-100):', '50');
            if (level === null) return;
            const levelNum = parseInt(level);
            if (isNaN(levelNum) || levelNum < 0 || levelNum > 100) {
                addLog('❌ Độ sáng phải từ 0-100', 'error');
                return;
            }
            callTool('set_brightness', {level: levelNum});
        }
        function openApp() {
            const app = prompt('Nhập tên app (notepad/calc/paint/cmd/explorer):', 'notepad');
            if (app && app.trim()) callTool('open_application', {app_name: app.trim()});
        }
        function listProcesses() { callTool('list_running_processes', {limit: 10}); }
        function killProcess() {
            const id = prompt('Nhập PID hoặc tên tiến trình:', 'chrome');
            if (id && id.trim()) callTool('kill_process', {identifier: id.trim()});
        }
        function createFile() {
            const path = prompt('Đường dẫn file:', 'C:/test.txt');
            if (!path || !path.trim()) return;
            const content = prompt('Nội dung:', 'Hello World');
            if (content !== null) callTool('create_file', {path: path.trim(), content});
        }
        function readFile() {
            const path = prompt('Đường dẫn file:', 'C:/test.txt');
            if (path && path.trim()) callTool('read_file', {path: path.trim()});
        }
        function listFiles() {
            const dir = prompt('Thư mục:', 'C:/Users');
            if (dir && dir.trim()) callTool('list_files', {directory: dir.trim()});
        }
        function diskUsage() { callTool('get_disk_usage', {}); }
        function networkInfo() { callTool('get_network_info', {}); }
        function batteryStatus() { callTool('get_battery_status', {}); }
        function searchWeb() {
            const query = prompt('Từ khóa tìm kiếm:', '');
            if (query && query.trim()) callTool('search_web', {query: query.trim()});
        }
        function calculator() {
            const expr = prompt('Biểu thức toán học:', '2+2*3');
            if (expr && expr.trim()) callAPI('/api/calculator', {expression: expr.trim()});
        }
        function getClipboard() { callTool('get_clipboard', {}); }
        function setClipboard() {
            const text = prompt('Nội dung cần copy:', '');
            if (text !== null && text.trim()) callTool('set_clipboard', {text: text.trim()});
        }
        function playSound() {
            const freq = prompt('Tần số Hz (200-2000):', '1000');
            if (freq === null) return;
            const dur = prompt('Thời gian ms (100-3000):', '500');
            if (dur === null) return;
            const freqNum = parseInt(freq);
            const durNum = parseInt(dur);
            if (isNaN(freqNum) || freqNum < 200 || freqNum > 2000) {
                addLog('❌ Tần số phải từ 200-2000 Hz', 'error');
                return;
            }
            if (isNaN(durNum) || durNum < 100 || durNum > 3000) {
                addLog('❌ Thời gian phải từ 100-3000 ms', 'error');
                return;
            }
            callTool('play_sound', {frequency: freqNum, duration: durNum});
        }
        
        // NEW TOOL FUNCTIONS
        function lockComputer() {
            if (confirm('Bạn có chắc muốn khóa máy tính?')) {
                callTool('lock_computer', {});
            }
        }
        function shutdownSchedule() {
            const action = prompt('Hành động (shutdown/restart/cancel):', 'shutdown');
            if (!action || !action.trim()) return;
            const actionLower = action.trim().toLowerCase();
            if (!['shutdown', 'restart', 'cancel'].includes(actionLower)) {
                addLog('❌ Hành động không hợp lệ. Dùng: shutdown, restart, hoặc cancel', 'error');
                return;
            }
            const delay = prompt('Trì hoãn (giây):', '60');
            if (delay === null) return;
            const delayNum = parseInt(delay) || 0;
            if (delayNum < 0) {
                addLog('❌ Thời gian trì hoãn phải >= 0', 'error');
                return;
            }
            callTool('shutdown_schedule', {action: actionLower, delay: delayNum});
        }
        function showDesktop() {
            callTool('show_desktop', {});
        }
        function undoOperation() {
            callTool('undo_operation', {});
        }
        function setTheme() {
            const dark = confirm('Chọn OK cho theme TỐI, Cancel cho theme SÁNG');
            callTool('set_theme', {dark_mode: dark});
        }
        function changeWallpaper() {
            const keyword = prompt('Từ khóa hình nền (hoặc để trống để chọn ngẫu nhiên):', '');
            callTool('change_wallpaper', {keyword: keyword || ''});
        }
        function getDesktopPath() {
            callTool('get_desktop_path', {});
        }
        function pasteContent() {
            const content = prompt('Nhập nội dung cần dán (hoặc để trống để dán clipboard hiện tại):', '');
            callTool('paste_content', {content: content || ''});
        }
        function pressEnter() {
            callTool('press_enter', {});
        }
        function findInDocument() {
            const searchText = prompt('Nhập nội dung tìm kiếm:', '');
            if (searchText && searchText.trim()) {
                callTool('find_in_document', {search_text: searchText.trim()});
            }
        }
        
        // AI ASSISTANT
        function askGemini() {
            const prompt = window.prompt('Hỏi Gemini AI (MIỄN PHÍ - ví dụ: What is Python?):', '');
            if (prompt && prompt.trim()) {
                addLog(`🤖 Hỏi Gemini: "${prompt}"`, 'info');
                
                // Use generic /api/call_tool endpoint
                fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'ask_gemini', args: {prompt: prompt.trim()}})
                })
                .then(res => res.json())
                .then(result => {
                    if(result.success) {
                        addLog(`✅ Gemini: ${result.response_text.substring(0, 200)}...`, 'success');
                    } else {
                        addLog(`❌ Gemini error: ${result.error}`, 'error');
                    }
                })
                .catch(err => addLog(`❌ Error: ${err.message}`, 'error'));
            }
        }
        
        function askGPT4() {
            const prompt = window.prompt('Hỏi GPT-4 (TRẢ PHÍ - chất lượng cao nhất):', '');
            if (prompt && prompt.trim()) {
                addLog(`🧠 Hỏi GPT-4: "${prompt}"`, 'info');
                
                // Use generic /api/call_tool endpoint
                fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'ask_gpt4', args: {prompt: prompt.trim()}})
                })
                .then(res => res.json())
                .then(result => {
                    if(result.success) {
                        const usage = result.usage ? ` (Tokens: ${result.usage.total_tokens})` : '';
                        addLog(`✅ GPT-4: ${result.response_text.substring(0, 200)}...${usage}`, 'success');
                    } else {
                        addLog(`❌ GPT-4 error: ${result.error}`, 'error');
                    }
                })
                .catch(err => addLog(`❌ Error: ${err.message}`, 'error'));
            }
        }

        // API caller
        async function callAPI(endpoint, data) {
            try {
                addLog(`🔧 Calling ${endpoint}...`, 'info');
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                addLog(`✅ ${JSON.stringify(result).substring(0, 100)}`, 'success');
                return result;
            } catch (error) {
                addLog(`❌ Error: ${error.message}`, 'error');
                return {success: false, error: error.message};
            }
        }
        
        async function callTool(name, params) {
            try {
                addLog(`🛠️ Tool: ${name}`, 'info');
                // Gọi API endpoint tương ứng với tool
                const endpoint = `/api/tool/${name}`;
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                });
                const result = await response.json();
                addLog(`✅ ${name}: ${JSON.stringify(result).substring(0, 150)}`, 'success');
                return result;
            } catch (error) {
                addLog(`❌ Tool error: ${error.message}`, 'error');
                return {success: false, error: error.message};
            }
        }
        
        async function getResources() {
            try {
                // Sử dụng cache nếu còn hiệu lực
                const now = Date.now();
                if (resourceCache && (now - lastResourceFetch) < RESOURCE_CACHE_TIME) {
                    return;
                }
                
                const response = await fetch('/api/resources');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('cpu').textContent = data.data.cpu_percent + '%';
                    document.getElementById('ram').textContent = data.data.memory_percent + '%';
                    document.getElementById('disk').textContent = data.data.disk_percent + '%';
                    
                    // Cập nhật cache
                    resourceCache = data;
                    lastResourceFetch = now;
                } else {
                    addLog(`❌ Lỗi lấy tài nguyên: ${data.error}`, 'error');
                }
            } catch (error) {
                addLog(`❌ ${error.message}`, 'error');
            }
        }
        
        // Debounce helper
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        async function calculate() {
            try {
                const expr = document.getElementById('calc-expr').value.trim();
                if (!expr) {
                    document.getElementById('calc-result').textContent = 'Vui lòng nhập biểu thức';
                    return;
                }
                const response = await fetch('/api/calculator', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({expression: expr})
                });
                const data = await response.json();
                document.getElementById('calc-result').textContent = data.success ? data.result : data.error;
            } catch (error) {
                document.getElementById('calc-result').textContent = 'Lỗi: ' + error.message;
            }
        }
        
        async function getCurrentTime() {
            try {
                const response = await fetch('/api/time');
                const data = await response.json();
                if (data.data) {
                    document.getElementById('time-result').textContent = data.data.datetime;
                }
            } catch (error) {
                document.getElementById('time-result').textContent = 'Lỗi: ' + error.message;
            }
        }
        
        // Modal functions
        function openSettingsModal() {
            document.getElementById('settingsModal').style.display = 'block';
            loadCurrentEndpoint();
        }
        
        function closeSettingsModal() {
            document.getElementById('settingsModal').style.display = 'none';
        }
        
        // Click outside modal to close
        window.onclick = function(event) {
            const modal = document.getElementById('settingsModal');
            if (event.target === modal) {
                closeSettingsModal();
            }
        }
        
        async function loadCurrentEndpoint() {
            try {
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                // Tìm thiết bị đang active (Thiết bị 3 - index 2)
                const activeDevice = data.endpoints[2]; // Thiết bị 3
                
                if (activeDevice && activeDevice.token) {
                    document.getElementById('endpoint-url').value = activeDevice.token;
                }
                
                // Load Gemini API key
                if (data.gemini_api_key) {
                    document.getElementById('gemini-api-key').value = data.gemini_api_key;
                    updateGeminiKeyStatus('✓ API key đã cấu hình', '#10b981');
                }
                
                // Load OpenAI API key
                if (data.openai_api_key) {
                    document.getElementById('openai-api-key').value = data.openai_api_key;
                    updateOpenAIKeyStatus('✓ API key đã cấu hình', '#10b981');
                }
                
                // Cập nhật thông tin hiện tại trong config section
                if (document.getElementById('current-device-name')) {
                    document.getElementById('current-device-name').textContent = activeDevice?.name || 'Chưa cấu hình';
                }
                if (document.getElementById('current-device-token')) {
                    const token = activeDevice?.token || 'Chưa có token';
                    document.getElementById('current-device-token').textContent = 
                        token.length > 50 ? token.substring(0, 50) + '...' : token;
                }
            } catch (error) {
                addLog('❌ Lỗi tải endpoint: ' + error.message, 'error');
            }
        }
        
        // Auto-save Gemini API key
        let geminiSaveTimeout;
        async function autoSaveGeminiKey() {
            clearTimeout(geminiSaveTimeout);
            
            geminiSaveTimeout = setTimeout(async () => {
                const apiKey = document.getElementById('gemini-api-key').value.trim();
                
                if (!apiKey) {
                    updateGeminiKeyStatus('', '');
                    return;
                }
                
                try {
                    updateGeminiKeyStatus('💾 Đang lưu...', '#f59e0b');
                    
                    const response = await fetch('/api/gemini-key', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({api_key: apiKey})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateGeminiKeyStatus('✓ Đã lưu tự động', '#10b981');
                        setTimeout(() => updateGeminiKeyStatus('✓ API key đã cấu hình', '#10b981'), 2000);
                    } else {
                        updateGeminiKeyStatus('❌ Lỗi: ' + result.error, '#ef4444');
                    }
                } catch (error) {
                    updateGeminiKeyStatus('❌ Lỗi kết nối', '#ef4444');
                }
            }, 1000); // Auto-save sau 1 giây không gõ
        }
        
        function updateGeminiKeyStatus(message, color) {
            const statusEl = document.getElementById('gemini-key-status');
            if (statusEl) {
                statusEl.textContent = message;
                statusEl.style.color = color;
            }
        }
        
        // Auto-save OpenAI API key
        let openaiSaveTimeout;
        async function autoSaveOpenAIKey() {
            clearTimeout(openaiSaveTimeout);
            
            openaiSaveTimeout = setTimeout(async () => {
                const apiKey = document.getElementById('openai-api-key').value.trim();
                
                if (!apiKey) {
                    updateOpenAIKeyStatus('', '');
                    return;
                }
                
                try {
                    updateOpenAIKeyStatus('💾 Đang lưu...', '#f59e0b');
                    
                    const response = await fetch('/api/openai-key', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({api_key: apiKey})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateOpenAIKeyStatus('✓ Đã lưu tự động', '#10b981');
                        setTimeout(() => updateOpenAIKeyStatus('✓ API key đã cấu hình', '#10b981'), 2000);
                    } else {
                        updateOpenAIKeyStatus('❌ Lỗi: ' + result.error, '#ef4444');
                    }
                } catch (error) {
                    updateOpenAIKeyStatus('❌ Lỗi kết nối', '#ef4444');
                }
            }, 1000);
        }
        
        function updateOpenAIKeyStatus(message, color) {
            const statusEl = document.getElementById('openai-key-status');
            if (statusEl) {
                statusEl.textContent = message;
                statusEl.style.color = color;
            }
        }
        
        async function saveEndpoint() {
            let input = document.getElementById('endpoint-url').value.trim();
            
            if (!input) {
                addLog('❌ Vui lòng nhập JWT token hoặc URL đầy đủ!', 'error');
                return;
            }
            
            let token = input;
            
            // Nếu user nhập URL đầy đủ, extract token từ URL
            if (input.startsWith('wss://') || input.startsWith('http')) {
                try {
                    const url = new URL(input);
                    const tokenParam = url.searchParams.get('token');
                    if (tokenParam) {
                        token = tokenParam;
                        addLog('✅ Đã tự động extract token từ URL', 'info');
                    } else {
                        addLog('❌ URL không chứa token parameter!', 'error');
                        return;
                    }
                } catch (e) {
                    addLog('❌ URL không hợp lệ!', 'error');
                    return;
                }
            }
            
            try {
                addLog('⏳ Đang lưu endpoint...', 'info');
                
                // Lấy danh sách thiết bị hiện tại
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                // Cập nhật token cho Thiết bị 3 (index 2)
                const devices = data.endpoints.map((device, index) => {
                    if (index === 2) { // Thiết bị 3
                        return {
                            name: 'Thiết bị 3',
                            token: token,
                            enabled: true
                        };
                    }
                    return device;
                });
                
                // Lưu cấu hình
                const saveResponse = await fetch('/api/endpoints/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({devices: devices})
                });
                
                const saveData = await saveResponse.json();
                
                if (saveData.success) {
                    addLog('✅ Đã lưu endpoint thành công!', 'success');
                    
                    // Chuyển sang thiết bị 3
                    const switchResponse = await fetch('/api/endpoints/switch/2', {method: 'POST'});
                    const switchData = await switchResponse.json();
                    
                    if (switchData.success) {
                        addLog('✅ ' + switchData.message, 'success');
                    }
                    
                    closeSettingsModal();
                    
                    // Reload trang sau 2 giây để kết nối lại
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    addLog('❌ Lỗi: ' + saveData.error, 'error');
                }
            } catch (error) {
                addLog('❌ Lỗi lưu endpoint: ' + error.message, 'error');
            }
        }
        
        function copyFullUrl() {
            const input = document.getElementById('endpoint-url').value.trim();
            if (!input) {
                addLog('❌ Không có dữ liệu để copy!', 'error');
                return;
            }
            
            let token = input;
            
            // Nếu user đã nhập URL đầy đủ, extract token
            if (input.startsWith('wss://') || input.startsWith('http')) {
                try {
                    const url = new URL(input);
                    const tokenParam = url.searchParams.get('token');
                    if (tokenParam) {
                        token = tokenParam;
                    }
                } catch (e) {
                    addLog('❌ URL không hợp lệ!', 'error');
                    return;
                }
            }
            
            // Tạo URL đầy đủ
            const fullUrl = `wss://api.xiaozhi.me/mcp/?token=${token}`;
            
            // Copy vào clipboard
            navigator.clipboard.writeText(fullUrl).then(() => {
                addLog('✅ Đã copy URL đầy đủ vào clipboard!', 'success');
            }).catch(err => {
                addLog('❌ Lỗi copy: ' + err.message, 'error');
            });
        }
        
        // Legacy functions (kept for compatibility, but hidden from UI)
        async function loadDevices() {
            try {
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                // Update current endpoint info in config section
                const activeDevice = data.endpoints[2]; // Thiết bị 3
                if (document.getElementById('current-device-name')) {
                    document.getElementById('current-device-name').textContent = activeDevice?.name || 'Chưa cấu hình';
                }
                if (document.getElementById('current-device-token')) {
                    const token = activeDevice?.token || 'Chưa có token';
                    document.getElementById('current-device-token').textContent = 
                        token.length > 50 ? token.substring(0, 50) + '...' : token;
                }
            } catch (error) {
                addLog('❌ Lỗi tải danh sách thiết bị: ' + error.message, 'error');
            }
        }

        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            if (!log) return;
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            const time = new Date().toLocaleTimeString();
            entry.innerHTML = `<span class="log-time">${time}</span> ${message}`;
            log.insertBefore(entry, log.firstChild);
            
            // Giới hạn 50 logs thay vì 100 để giảm DOM size
            if (log.children.length > 50) {
                // Xóa nhiều logs cùng lúc để tránh reflow nhiều lần
                while (log.children.length > 50) {
                    log.removeChild(log.lastChild);
                }
            }
        }
        
        // WebSocket với reconnect optimization
        let wsReconnectAttempts = 0;
        const MAX_RECONNECT_DELAY = 30000; // Max 30s
        
        function connectWS() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onopen = () => {
                addLog('✅ WebSocket connected', 'success');
                wsReconnectAttempts = 0; // Reset counter khi connect thành công
            };
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'xiaozhi_status') {
                    const badge = document.getElementById('xiaozhi-status');
                    const text = document.getElementById('xiaozhi-text');
                    if (data.connected) {
                        badge.className = 'status-badge online';
                        text.textContent = 'Connected';
                    } else {
                        badge.className = 'status-badge offline';
                        text.textContent = 'Disconnected';
                    }
                } else if (data.type === 'xiaozhi_activity') {
                    if (data.method !== 'ping') {
                        addLog(`📡 Xiaozhi: ${data.method}`, 'info');
                    }
                }
            };
            ws.onclose = () => {
                addLog('❌ WebSocket disconnected', 'error');
                // Exponential backoff cho reconnect
                wsReconnectAttempts++;
                const delay = Math.min(1000 * Math.pow(2, wsReconnectAttempts), MAX_RECONNECT_DELAY);
                setTimeout(connectWS, delay);
            };
        }
        
        // Caching và optimization
        let resourceCache = null;
        let lastResourceFetch = 0;
        const RESOURCE_CACHE_TIME = 3000; // Cache 3 giây
        
        // Playlist list functions (sử dụng API backend thay vì localStorage)
        async function getPlaylists() {
            try {
                const response = await fetch('/api/youtube_playlists');
                const data = await response.json();
                return data.success ? data.playlists : [];
            } catch (e) {
                console.error('Failed to load playlists from API', e);
                return [];
            }
        }

        async function renderPlaylists() {
            const list = await getPlaylists();
            const container = document.getElementById('playlist-list');
            if (!container) return;
            container.innerHTML = '';

            if (list.length === 0) {
                container.innerHTML = '<div style="color:#666;padding:12px;">Chưa có playlist nào. Nhấn "＋ Thêm Playlist" để thêm.</div>';
                return;
            }

            list.forEach((item, idx) => {
                const row = document.createElement('div');
                row.style.display = 'flex';
                row.style.alignItems = 'center';
                row.style.justifyContent = 'space-between';
                row.style.padding = '8px';
                row.style.borderBottom = '1px solid #eee';

                const left = document.createElement('div');
                left.style.display = 'flex';
                left.style.flexDirection = 'column';
                left.style.gap = '4px';

                const name = document.createElement('div');
                name.textContent = item.name;
                name.style.fontWeight = '700';
                name.style.color = '#333';

                const url = document.createElement('div');
                url.textContent = item.url;
                url.style.fontSize = '0.85em';
                url.style.color = '#666';

                left.appendChild(name);
                left.appendChild(url);

                const actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.gap = '8px';

                const openBtn = document.createElement('button');
                openBtn.textContent = '▶';
                openBtn.title = 'Mở playlist';
                openBtn.style.padding = '6px 10px';
                openBtn.style.borderRadius = '6px';
                openBtn.style.border = 'none';
                openBtn.style.background = '#10b981';
                openBtn.style.color = 'white';
                openBtn.style.cursor = 'pointer';
                openBtn.onclick = () => openPlaylistByName(item.name);

                const delBtn = document.createElement('button');
                delBtn.textContent = '🗑';
                delBtn.title = 'Xóa playlist';
                delBtn.style.padding = '6px 10px';
                delBtn.style.borderRadius = '6px';
                delBtn.style.border = 'none';
                delBtn.style.background = '#ef4444';
                delBtn.style.color = 'white';
                delBtn.style.cursor = 'pointer';
                delBtn.onclick = () => { if (confirm('Xóa playlist "' + item.name + '"?')) { removePlaylistByName(item.name); } };

                actions.appendChild(openBtn);
                actions.appendChild(delBtn);

                row.appendChild(left);
                row.appendChild(actions);

                container.appendChild(row);
            });
        }

        function promptAddPlaylist() {
            const name = prompt('Nhập tên playlist (ví dụ: "Nhạc chill"):');
            if (!name) return;
            const url = prompt('Dán link playlist YouTube (hoặc video trong playlist):');
            if (!url) return;
            addPlaylist(name.trim(), url.trim());
        }

        async function addPlaylist(name, url) {
            if (!name || !url) {
                addLog('❌ Tên và URL không được để trống', 'error');
                return;
            }
            try {
                const response = await fetch('/api/youtube_playlists/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, url})
                });
                const data = await response.json();
                if (data.success) {
                    await renderPlaylists();
                    addLog('✅ Đã thêm playlist: ' + name, 'success');
                } else {
                    addLog('❌ ' + (data.error || 'Không thể thêm playlist'), 'error');
                }
            } catch (e) {
                console.error('Failed to add playlist', e);
                addLog('❌ Lỗi khi thêm playlist', 'error');
            }
        }

        async function removePlaylistByName(name) {
            try {
                const response = await fetch('/api/youtube_playlists/remove', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name})
                });
                const data = await response.json();
                if (data.success) {
                    await renderPlaylists();
                    addLog('🗑 Đã xóa playlist: ' + name, 'info');
                } else {
                    addLog('❌ ' + (data.error || 'Không thể xóa playlist'), 'error');
                }
            } catch (e) {
                console.error('Failed to remove playlist', e);
                addLog('❌ Lỗi khi xóa playlist', 'error');
            }
        }

        async function openPlaylistByName(name) {
            const list = await getPlaylists();
            const item = list.find(p => p.name === name);
            if (item) {
                window.open(item.url, '_blank');
                addLog('▶ Mở playlist: ' + name, 'info');
            }
        }

        // Expose function for voice/AI integration: open by keyword search (fuzzy matching)
        async function triggerPlayByName(keyword) {
            if (!keyword || keyword.trim() === '') return false;
            
            keyword = keyword.trim().toLowerCase();
            const list = await getPlaylists();
            
            if (list.length === 0) {
                addLog('⚠ Danh sách playlist trống. Hãy thêm playlist trước!', 'error');
                return false;
            }
            
            // Bước 1: Tìm chính xác (exact match)
            let found = list.find(item => item.name.toLowerCase() === keyword);
            
            // Bước 2: Tìm bắt đầu bằng từ khóa (starts with)
            if (!found) {
                found = list.find(item => item.name.toLowerCase().startsWith(keyword));
            }
            
            // Bước 3: Tìm chứa từ khóa (contains)
            if (!found) {
                found = list.find(item => item.name.toLowerCase().includes(keyword));
            }
            
            // Bước 4: Tìm theo từng từ trong tên playlist
            if (!found) {
                found = list.find(item => {
                    const words = item.name.toLowerCase().split(/\\s+/);
                    return words.some(word => word.includes(keyword) || keyword.includes(word));
                });
            }
            
            if (found) {
                window.open(found.url, '_blank');
                addLog('🔊 Phát playlist: "' + found.name + '" (từ khóa: "' + keyword + '")', 'success');
                return true;
            } else {
                // Hiển thị gợi ý các playlist có sẵn
                const suggestions = list.map(item => item.name).slice(0, 5).join(', ');
                addLog('⚠ Không tìm thấy playlist với từ khóa: "' + keyword + '"', 'error');
                addLog('💡 Gợi ý: ' + suggestions, 'info');
                return false;
            }
        }
        
        // Hàm mở playlist nhanh (alias) - dễ nhớ hơn cho voice command
        function moPlaylist(keyword) {
            return triggerPlayByName(keyword);
        }
        
        function danhSachNhac(keyword) {
            return triggerPlayByName(keyword);
        }

        // Initialize playlist list on load
        function initPlaylists() {
            renderPlaylists();
        }
        
        connectWS();
        // Giảm polling từ 5s xuống 10s để giảm tải
        setInterval(getResources, 10000);
        getResources();
        
    // Initialize playlists on page load
    initPlaylists();
    </script>
    
    <!-- MINIZ FOOTER - Compact Corner -->
    <div class="footer-miniz">
        <div class="footer-logo-compact">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='48' fill='%23667eea'/%3E%3Cpath d='M30 40 L50 25 L70 40 M50 25 L50 75 M35 55 L50 50 L65 55 M35 70 L50 65 L65 70' stroke='white' stroke-width='3' fill='none'/%3E%3Ctext x='50' y='88' text-anchor='middle' fill='white' font-size='14' font-weight='bold' font-family='Arial'%3EminiZ%3C/text%3E%3C/svg%3E" alt="miniZ Logo">
            <span class="footer-brand-compact">miniZ</span>
        </div>
        <div class="footer-separator"></div>
        <a href="https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU" target="_blank" class="footer-youtube-compact" title="Kênh YouTube miniZ">
            <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            YouTube
        </a>
    </div>
</body>
</html>
    """
    return html

# API Endpoints
@app.post("/api/volume")
async def api_volume(request: VolumeRequest):
    result = await set_volume(request.level)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/screenshot")
async def api_screenshot():
    result = await take_screenshot()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/notification")
async def api_notification(request: NotificationRequest):
    result = await show_notification(request.title, request.message)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.get("/api/resources")
async def api_resources():
    result = await get_system_resources()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.get("/api/time")
async def api_time():
    result = await get_current_time()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return {"data": result}

@app.post("/api/calculator")
async def api_calculator(request: CalculatorRequest):
    result = await calculator(request.expression)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result


# ===== GENERIC TOOL CALLER =====

@app.post("/api/call_tool")
async def call_any_tool(data: dict):
    """Generic endpoint to call ANY tool from TOOLS registry"""
    tool_name = data.get("tool", data.get("name", ""))
    args = data.get("args", data.get("arguments", {}))
    
    if not tool_name:
        raise HTTPException(400, "Tool name is required")
    
    if tool_name not in TOOLS:
        raise HTTPException(404, f"Tool '{tool_name}' not found")
    
    try:
        handler = TOOLS[tool_name]["handler"]
        result = await handler(**args)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== 23 API ENDPOINTS MỚI (Tool 8-30) =====

@app.post("/api/tool/ask_gemini")
async def api_ask_gemini(data: dict):
    """Gemini AI endpoint - MOVED TO TOP FOR PRIORITY"""
    prompt = data.get("prompt", "")
    model = data.get("model", "models/gemini-2.5-pro")
    
    if not prompt:
        raise HTTPException(400, "Prompt is required")
    
    result = await ask_gemini(prompt=prompt, model=model)
    return result

@app.post("/api/tool/open_application")
async def api_open_app(data: dict):
    result = await open_application(data.get("app_name", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

# MEDIA PLAYER CONTROL ENDPOINTS
@app.post("/api/tool/media_play_pause")
async def api_media_play_pause(data: dict):
    result = await media_play_pause()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_next_track")
async def api_media_next(data: dict):
    result = await media_next_track()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_previous_track")
async def api_media_previous(data: dict):
    result = await media_previous_track()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_stop")
async def api_media_stop(data: dict):
    result = await media_stop()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_control")
async def api_media_control(data: dict):
    result = await media_control(data.get("action", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_active_media_players")
async def api_get_active_media(data: dict):
    result = await get_active_media_players()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/list_running_processes")
async def api_list_procs(data: dict):
    result = await list_running_processes(data.get("limit", 10))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/kill_process")
async def api_kill_proc(data: dict):
    result = await kill_process(data.get("identifier", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/create_file")
async def api_create_file(data: dict):
    result = await create_file(data.get("path", ""), data.get("content", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/read_file")
async def api_read_file(data: dict):
    result = await read_file(data.get("path", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/list_files")
async def api_list_files(data: dict):
    result = await list_files(data.get("directory", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_disk_usage")
async def api_disk_usage():
    result = await get_disk_usage()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_network_info")
async def api_network():
    result = await get_network_info()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_battery_status")
async def api_battery():
    result = await get_battery_status()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/search_web")
async def api_search(data: dict):
    result = await search_web(data.get("query", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_clipboard")
async def api_get_clip():
    result = await get_clipboard()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_clipboard")
async def api_set_clip(data: dict):
    result = await set_clipboard(data.get("text", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/play_sound")
async def api_sound(data: dict):
    result = await play_sound(data.get("frequency", 1000), data.get("duration", 500))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_volume")
async def api_tool_set_volume(data: dict):
    result = await set_volume(data.get("level", 50))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_brightness")
async def api_brightness(data: dict):
    result = await set_brightness(data.get("level", 50))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/mute_volume")
async def api_mute_volume(data: dict):
    result = await mute_volume()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/unmute_volume")
async def api_unmute_volume(data: dict):
    result = await unmute_volume()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/volume_up")
async def api_volume_up(data: dict):
    result = await volume_up(data.get("steps", 5))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/volume_down")
async def api_volume_down(data: dict):
    result = await volume_down(data.get("steps", 5))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/minimize_all_windows")
async def api_minimize():
    result = await show_desktop()  # Sử dụng show_desktop thay vì minimize_all_windows
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/undo_action")
async def api_undo():
    result = await undo_operation()  # Sử dụng undo_operation thay vì undo_action
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/toggle_dark_mode")
async def api_theme():
    result = await set_theme(dark_mode=None)  # Toggle bằng cách để None, hàm set_theme sẽ xử lý
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_wallpaper")
async def api_wallpaper(data: dict):
    path = data.get("path", "")
    keyword = data.get("keyword", "")
    # Dùng change_wallpaper với custom_path nếu có path
    result = await change_wallpaper(keyword=keyword, custom_path=path)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/paste_text")
async def api_paste():
    result = await paste_content(content="")  # paste_content với clipboard hiện tại
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/press_enter")
async def api_enter():
    result = await press_enter()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/find_on_screen")
async def api_find(data: dict):
    result = await find_in_document(data.get("text", ""))  # Sử dụng find_in_document
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/lock_computer")
async def api_lock():
    result = await lock_computer()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/shutdown_computer")
async def api_shutdown(data: dict):
    delay = data.get("delay", 0)
    # Sử dụng shutdown_schedule với action="shutdown"
    result = await shutdown_schedule(action="shutdown", delay=delay)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result


@app.get("/logo.png")
async def get_logo():
    from fastapi.responses import FileResponse
    import os
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    else:
        raise HTTPException(404, "Logo not found")

@app.get("/api/endpoints")
async def get_endpoints():
    global GEMINI_API_KEY, OPENAI_API_KEY
    return {
        "endpoints": endpoints_config,
        "gemini_api_key": GEMINI_API_KEY,
        "openai_api_key": OPENAI_API_KEY
    }

# YouTube Playlists API
@app.get("/api/youtube_playlists")
async def api_get_youtube_playlists():
    """Lấy danh sách playlist YouTube"""
    return await get_youtube_playlists()

@app.post("/api/youtube_playlists/add")
async def api_add_youtube_playlist(data: dict):
    """Thêm playlist YouTube mới"""
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    
    if not name or not url:
        return {"success": False, "error": "Tên và URL không được để trống"}
    
    return await add_youtube_playlist(name, url)

@app.post("/api/youtube_playlists/remove")
async def api_remove_youtube_playlist(data: dict):
    """Xóa playlist YouTube"""
    name = data.get("name", "").strip()
    
    if not name:
        return {"success": False, "error": "Tên playlist không được để trống"}
    
    return await remove_youtube_playlist(name)

# ============================================================
# CONVERSATION HISTORY API
# ============================================================

@app.get("/api/conversation/history")
async def api_get_conversation_history():
    """Lấy toàn bộ lịch sử hội thoại"""
    return {
        "success": True,
        "total_messages": len(conversation_history),
        "messages": conversation_history
    }

@app.get("/api/conversation/recent/{count}")
async def api_get_recent_conversation(count: int = 10):
    """Lấy N messages gần nhất"""
    recent = conversation_history[-count:] if len(conversation_history) > count else conversation_history
    return {
        "success": True,
        "count": len(recent),
        "messages": recent
    }

@app.post("/api/conversation/clear")
async def api_clear_conversation():
    """Xóa toàn bộ lịch sử hội thoại"""
    global conversation_history
    conversation_history = []
    save_conversation_history()
    return {
        "success": True,
        "message": "Đã xóa toàn bộ lịch sử hội thoại"
    }

@app.post("/api/conversation/export")
async def api_export_conversation(data: dict = None):
    """Export lịch sử hội thoại ra file"""
    filename = data.get("filename", "") if data else ""
    return await export_conversation_to_file(filename)

@app.post("/api/conversation/add")
async def api_add_conversation_message(data: dict):
    """Thêm message từ Web UI vào history"""
    role = data.get("role", "user")
    content = data.get("content", "")
    metadata = data.get("metadata", {})
    
    if not content:
        return {"success": False, "error": "Content không được để trống"}
    
    add_to_conversation(role, content, metadata)
    
    return {
        "success": True,
        "message": "Đã thêm message vào history"
    }

@app.post("/api/endpoints/switch/{index}")
async def switch_endpoint(index: int):
    global active_endpoint_index, should_reconnect
    if index < 0 or index >= len(endpoints_config):
        return {"success": False, "error": "Thiết bị không tồn tại"}
    
    device = endpoints_config[index]
    if not device.get("token"):
        return {"success": False, "error": "Thiết bị chưa có token. Hãy nhập token và lưu lại!"}
    
    # Thay đổi endpoint và trigger reconnect
    old_index = active_endpoint_index
    active_endpoint_index = index
    should_reconnect = True  # Trigger reconnect trong xiaozhi_websocket_client
    
    # Lưu vào file
    save_endpoints_to_file(endpoints_config, active_endpoint_index)
    
    print(f"🔄 [Endpoint] Switching from device {old_index} to {index} ({device['name']})")
    
    return {"success": True, "message": f"Đã chuyển sang {device['name']}. Đang kết nối lại..."}

@app.post("/api/endpoints/save")
async def save_endpoints(data: dict):
    global endpoints_config, should_reconnect
    try:
        devices = data.get('devices', [])
        if not devices:
            return {"success": False, "error": "Không có dữ liệu"}
        
        # Lưu token cũ của thiết bị đang active để so sánh
        old_active_token = endpoints_config[active_endpoint_index].get('token', '') if active_endpoint_index < len(endpoints_config) else ''
        
        # Cập nhật endpoints_config
        endpoints_config = []
        for dev in devices:
            endpoints_config.append({
                'name': dev.get('name', 'Thiết bị'),
                'token': dev.get('token', ''),
                'enabled': bool(dev.get('token', ''))
            })
        
        # Lưu vào file JSON
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [Endpoint] Successfully saved {len(devices)} devices to file")
        else:
            print(f"⚠️ [Endpoint] Failed to save to file, but config updated in memory")
        
        # Kiểm tra nếu token của thiết bị đang active thay đổi -> reconnect
        new_active_token = endpoints_config[active_endpoint_index].get('token', '') if active_endpoint_index < len(endpoints_config) else ''
        if old_active_token != new_active_token and new_active_token:
            should_reconnect = True
            print(f"🔄 [Endpoint] Token changed for active device {active_endpoint_index}. Triggering reconnect...")
        
        return {"success": True, "message": "Đã lưu cấu hình"}
    except Exception as e:
        print(f"❌ [Endpoint] Error saving: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/gemini-key")
async def save_gemini_key(data: dict):
    """Save Gemini API key - Auto-save endpoint"""
    global GEMINI_API_KEY
    try:
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return {"success": False, "error": "API key không được để trống"}
        
        # Validate format (Gemini API key starts with AIzaSy)
        if not api_key.startswith('AIzaSy'):
            return {"success": False, "error": "API key không hợp lệ (phải bắt đầu với 'AIzaSy')"}
        
        # Update global variable
        GEMINI_API_KEY = api_key
        
        # Save to file
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [Gemini] API key saved (ends with ...{api_key[-8:]})")
            return {
                "success": True,
                "message": "✓ Đã lưu Gemini API key",
                "key_preview": f"...{api_key[-8:]}"
            }
        else:
            return {"success": False, "error": "Lỗi lưu file config"}
    except Exception as e:
        print(f"❌ [Gemini] Error saving API key: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/openai-key")
async def save_openai_key(data: dict):
    """Save OpenAI API key - Auto-save endpoint"""
    global OPENAI_API_KEY
    try:
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return {"success": False, "error": "API key không được để trống"}
        
        # Validate format (OpenAI API key starts with sk-)
        if not api_key.startswith('sk-'):
            return {"success": False, "error": "API key không hợp lệ (phải bắt đầu với 'sk-')"}
        
        # Update global variable
        OPENAI_API_KEY = api_key
        
        # Save to file
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [OpenAI] API key saved (ends with ...{api_key[-8:]})")
            return {
                "success": True,
                "message": "✓ Đã lưu OpenAI API key",
                "key_preview": f"...{api_key[-8:]}"
            }
        else:
            return {"success": False, "error": "Lỗi lưu file config"}
    except Exception as e:
        print(f"❌ [OpenAI] Error saving API key: {e}")
        return {"success": False, "error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({"type": "xiaozhi_status", "connected": xiaozhi_connected})
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"⚠️ WebSocket client error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.on_event("startup")
async def startup():
    # Enable WebSocket client with error handling
    try:
        asyncio.create_task(xiaozhi_websocket_client())
    except Exception as e:
        print(f"⚠️ Failed to start WebSocket client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    
    def open_browser():
        """Mo browser sau 2 giay"""
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    # Khoi dong thread mo browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("=" * 60)
    print(" miniZ MCP - SIDEBAR UI")
    print("=" * 60)
    print(" Web Dashboard: http://localhost:8000")
    print(" WebSocket MCP: Multi-device support")
    print("  Tools: 30 available (20 original + 10 new from reference)")
    print(" Browser se tu dong mo sau 2 giay...")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)

