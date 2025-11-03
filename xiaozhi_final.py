#!/usr/bin/env python3
"""
Xiaozhi Final - Giao diện Sidebar matching Official Design
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

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG_FILE = Path(__file__).parent / "xiaozhi_endpoints.json"

DEFAULT_ENDPOINT = {
    "name": "Thiết bị 1",
    "token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ1MzYxMSwiYWdlbnRJZCI6OTQ0MjE4LCJlbmRwb2ludElkIjoiYWdlbnRfOTQ0MjE4IiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc2MjA4NTI1OSwiZXhwIjoxNzkzNjQyODU5fQ.GK91-17mqarpETPwz7N6rZj5DaT7bJkpK7EM6lO0Rdmfztv_KeOTBP9R4Lvy3uXKMCJn3gwucvelCur95GAn5Q",
    "enabled": True
}

def load_endpoints_from_file():
    """Đọc cấu hình endpoints từ file JSON"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ [Config] Loaded {len(data.get('endpoints', []))} endpoints from {CONFIG_FILE.name}")
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
    try:
        # Kiểm tra nếu data không thay đổi thì không cần lưu
        new_data = {
            'endpoints': endpoints,
            'active_index': active_index,
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

print("🚀 Xiaozhi Final - Sidebar UI")
print(f"🌐 Web: http://localhost:8000")
print(f"📡 MCP: Multi-device ready")

# ============================================================
# TOOL IMPLEMENTATIONS (20 TOOLS)
# ============================================================

async def set_volume(level: int) -> dict:
    """Điều chỉnh âm lượng hệ thống - Cải tiến cho MCP"""
    try:
        if not 0 <= level <= 100:
            return {"success": False, "error": "Level phải từ 0-100"}
        
        # Sử dụng pycaw để điều chỉnh âm lượng chính xác và nhanh
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            # Lấy âm lượng hiện tại trước khi thay đổi
            current_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
            
            # Set âm lượng mới (0.0 - 1.0)
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            
            return {
                "success": True, 
                "level": level, 
                "previous_level": current_volume,
                "message": f"✅ Âm lượng: {current_volume}% → {level}%"
            }
        except ImportError:
            # Fallback về PowerShell nếu không có pycaw (nhưng cải thiện logic)
            # Sử dụng WMI để set âm lượng chính xác hơn
            ps_cmd = f"""
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {{
    int NotImpl1(); int NotImpl2();
    int GetMasterVolumeLevelScalar(out float level);
    int SetMasterVolumeLevelScalar(float level, System.Guid eventContext);
}}
[Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject {{ }}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {{
    int NotImpl1();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice device);
}}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {{
    int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
}}
'@
$enumerator = [System.Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]'BCDE0395-E52F-467C-8E3D-C4579291692E'))
$device = $null
$enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device)
$aev = $null
$device.Activate([Guid]'5CDF2C82-841E-4546-9722-0CF74078229A', 0, 0, [ref]$aev)
$current = 0.0
$aev.GetMasterVolumeLevelScalar([ref]$current)
$aev.SetMasterVolumeLevelScalar({level / 100.0}, [Guid]::Empty)
Write-Output "Volume changed from $([int]($current * 100))% to {level}%"
"""
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-NoProfile", "-Command", ps_cmd,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=3)
            
            if proc.returncode == 0:
                output = stdout.decode('utf-8', errors='ignore').strip()
                return {
                    "success": True, 
                    "level": level, 
                    "message": f"✅ {output if output else f'Âm lượng: {level}%'}"
                }
            else:
                error_msg = stderr.decode('utf-8', errors='ignore').strip()
                return {"success": False, "error": f"PowerShell error: {error_msg}"}
                
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout khi điều chỉnh âm lượng"}
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

async def take_screenshot() -> dict:
    try:
        subprocess.Popen(["snippingtool"])
        return {"success": True, "message": "Đã mở công cụ chụp màn hình"}
    except Exception as e:
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

async def open_application(app_name: str) -> dict:
    try:
        apps = {"notepad": "notepad.exe", "calc": "calc.exe", "paint": "mspaint.exe", "cmd": "cmd.exe", "explorer": "explorer.exe"}
        app = apps.get(app_name.lower())
        if not app:
            return {"success": False, "error": f"App '{app_name}' không hỗ trợ"}
        subprocess.Popen([app])
        return {"success": True, "message": f"Đã mở {app_name}"}
    except Exception as e:
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
            return {"success": False, "error": "Không có pin"}
        return {"success": True, "percent": bat.percent, "charging": bat.power_plugged, "time_left": f"{bat.secsleft // 3600}h {(bat.secsleft % 3600) // 60}m" if bat.secsleft != psutil.POWER_TIME_UNLIMITED else "Unknown"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_network_info() -> dict:
    try:
        import socket
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        net_info = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    net_info.append({"interface": iface, "ip": addr.address, "netmask": addr.netmask})
        return {"success": True, "hostname": hostname, "primary_ip": ip, "interfaces": net_info}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_web(query: str) -> dict:
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {"success": True, "query": query, "message": f"Đã mở: {query}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_brightness(level: int) -> dict:
    try:
        if not 0 <= level <= 100:
            return {"success": False, "error": "Level 0-100"}
        ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        proc = await asyncio.create_subprocess_exec("powershell", "-Command", ps_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(proc.wait(), timeout=5)
        return {"success": True, "level": level, "message": f"Độ sáng: {level}%"}
    except Exception as e:
        return {"success": False, "error": "Không hỗ trợ"}

async def get_clipboard() -> dict:
    try:
        proc = await asyncio.create_subprocess_exec("powershell", "-Command", "Get-Clipboard", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        content = stdout.decode('utf-8', errors='ignore').strip()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_clipboard(text: str) -> dict:
    try:
        proc = await asyncio.create_subprocess_exec("powershell", "-Command", f"Set-Clipboard -Value '{text}'", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(proc.wait(), timeout=5)
        return {"success": True, "message": "Đã copy", "text": text}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_sound(frequency: int = 1000, duration: int = 500) -> dict:
    try:
        import winsound
        if not 200 <= frequency <= 2000: frequency = 1000
        if not 100 <= duration <= 3000: duration = 500
        winsound.Beep(frequency, duration)
        return {"success": True, "frequency": frequency, "duration": duration}
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
# MUSIC LIBRARY TOOLS
# ============================================================

MUSIC_LIBRARY = Path(__file__).parent / "music_library"
MUSIC_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac'}

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

async def play_music(filename: str) -> dict:
    """
    Phát nhạc từ music_library bằng Windows Media Player.
    
    IMPORTANT: Always use 'list_music' first to get exact filename!
    
    Args:
        filename: Exact filename from list_music (e.g., 'song.mp3' or 'Pop/song.mp3')
        
    Returns:
        dict with 'success', 'filename', 'path', 'size_mb', 'message'
        
    Examples:
        play_music("my_song.mp3") -> Plays the file
        play_music("Pop/my_song.mp3") -> Plays file from Pop folder
        
    Note: Search is case-insensitive and supports partial matching
    """
    try:
        if not MUSIC_LIBRARY.exists():
            return {"success": False, "error": "Thư mục music_library không tồn tại"}
        
        print(f"🎵 [Play Music] Tìm file: '{filename}'")
        
        # Tìm file trong thư mục và các subfolder (hỗ trợ tìm theo tên hoặc path)
        music_path = None
        filename_lower = filename.lower()
        
        # Thử tìm exact match trước
        for file_path in MUSIC_LIBRARY.rglob("*"):
            if file_path.is_file():
                if file_path.name == filename:
                    music_path = file_path
                    break
        
        # Nếu không tìm thấy, thử case-insensitive
        if not music_path:
            for file_path in MUSIC_LIBRARY.rglob("*"):
                if file_path.is_file():
                    if file_path.name.lower() == filename_lower:
                        music_path = file_path
                        break
        
        # Nếu vẫn không tìm thấy, thử tìm theo relative path
        if not music_path:
            for file_path in MUSIC_LIBRARY.rglob("*"):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(MUSIC_LIBRARY))
                    if rel_path == filename or rel_path.lower() == filename_lower:
                        music_path = file_path
                        break
        
        # Nếu vẫn không tìm thấy, thử partial match
        if not music_path:
            for file_path in MUSIC_LIBRARY.rglob("*"):
                if file_path.is_file() and filename_lower in file_path.name.lower():
                    music_path = file_path
                    break
        
        if not music_path or not music_path.exists():
            # List available files for debugging
            available = [f.name for f in MUSIC_LIBRARY.rglob("*") if f.is_file() and f.suffix.lower() in MUSIC_EXTENSIONS]
            return {
                "success": False, 
                "error": f"Không tìm thấy file '{filename}'",
                "available_files": available[:5]  # Show first 5 files
            }
        
        if music_path.suffix.lower() not in MUSIC_EXTENSIONS:
            return {"success": False, "error": f"Định dạng file không được hỗ trợ: {music_path.suffix}"}
        
        print(f"🎵 [Play Music] Đã tìm thấy: {music_path}")
        
        # Mở file nhạc với Windows Media Player (chạy async)
        import os
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, os.startfile, str(music_path))
        
        return {
            "success": True,
            "filename": music_path.name,
            "path": str(music_path.relative_to(MUSIC_LIBRARY)),
            "full_path": str(music_path),
            "size_mb": round(music_path.stat().st_size / (1024**2), 2),
            "message": f"✅ Đang phát: {music_path.name}"
        }
    except Exception as e:
        print(f"❌ [Play Music] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def stop_music() -> dict:
    """Dừng nhạc đang phát (đóng Windows Media Player)"""
    try:
        # Đóng tất cả các process Windows Media Player
        ps_cmd = "Stop-Process -Name 'wmplayer' -Force -ErrorAction SilentlyContinue"
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.wait(), timeout=3)
        
        return {
            "success": True,
            "message": "✅ Đã dừng phát nhạc"
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
# TOOLS REGISTRY
# ============================================================

TOOLS = {
    "set_volume": {"handler": set_volume, "description": "Điều chỉnh âm lượng hệ thống (0-100) - Nhanh và chính xác", "parameters": {"level": {"type": "integer", "description": "Mức âm lượng từ 0-100", "required": True}}},
    "get_volume": {"handler": get_volume, "description": "Lấy mức âm lượng hiện tại của hệ thống", "parameters": {}},
    "take_screenshot": {"handler": take_screenshot, "description": "Chụp màn hình", "parameters": {}},
    "show_notification": {"handler": show_notification, "description": "Hiển thị thông báo", "parameters": {"title": {"type": "string", "description": "Tiêu đề", "required": True}, "message": {"type": "string", "description": "Nội dung", "required": True}}},
    "get_system_resources": {"handler": get_system_resources, "description": "Tài nguyên hệ thống", "parameters": {}},
    "get_current_time": {"handler": get_current_time, "description": "Thời gian hiện tại", "parameters": {}},
    "calculator": {"handler": calculator, "description": "Tính toán", "parameters": {"expression": {"type": "string", "description": "Biểu thức", "required": True}}},
    "open_application": {"handler": open_application, "description": "Mở ứng dụng", "parameters": {"app_name": {"type": "string", "description": "Tên app", "required": True}}},
    "list_running_processes": {"handler": list_running_processes, "description": "Liệt kê tiến trình", "parameters": {"limit": {"type": "integer", "description": "Số lượng", "required": False}}},
    "kill_process": {"handler": kill_process, "description": "Tắt tiến trình", "parameters": {"identifier": {"type": "string", "description": "PID hoặc tên", "required": True}}},
    "create_file": {"handler": create_file, "description": "Tạo file", "parameters": {"path": {"type": "string", "description": "Đường dẫn", "required": True}, "content": {"type": "string", "description": "Nội dung", "required": True}}},
    "read_file": {"handler": read_file, "description": "Đọc file", "parameters": {"path": {"type": "string", "description": "Đường dẫn", "required": True}}},
    "list_files": {"handler": list_files, "description": "Liệt kê files", "parameters": {"directory": {"type": "string", "description": "Thư mục", "required": True}}},
    "get_battery_status": {"handler": get_battery_status, "description": "Thông tin pin", "parameters": {}},
    "get_network_info": {"handler": get_network_info, "description": "Thông tin mạng", "parameters": {}},
    "search_web": {"handler": search_web, "description": "Tìm kiếm Google", "parameters": {"query": {"type": "string", "description": "Từ khóa", "required": True}}},
    "set_brightness": {"handler": set_brightness, "description": "Độ sáng màn hình", "parameters": {"level": {"type": "integer", "description": "Độ sáng 0-100", "required": True}}},
    "get_clipboard": {"handler": get_clipboard, "description": "Lấy clipboard", "parameters": {}},
    "set_clipboard": {"handler": set_clipboard, "description": "Đặt clipboard", "parameters": {"text": {"type": "string", "description": "Nội dung", "required": True}}},
    "play_sound": {"handler": play_sound, "description": "Phát âm thanh", "parameters": {"frequency": {"type": "integer", "description": "Tần số Hz", "required": False}, "duration": {"type": "integer", "description": "Thời gian ms", "required": False}}},
    "get_disk_usage": {"handler": get_disk_usage, "description": "Thông tin đĩa", "parameters": {}},
    
    # MUSIC LIBRARY TOOLS
    "list_music": {
        "handler": list_music, 
        "description": "List and AUTO-PLAY music from music_library. By default, automatically plays the first song found (like xinnan-tech reference). Returns list of all songs + auto-play result. Set auto_play=False to only list without playing.", 
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
        "description": "Play a specific music file by EXACT filename. Use this when you know the exact filename (e.g., from list_music or search_music results). Supports flexible matching: exact name, case-insensitive, path, or partial match. Example: play_music(filename='In Love.mp3') or play_music(filename='Pop/song.mp3')", 
        "parameters": {
            "filename": {
                "type": "string", 
                "description": "Music filename or path. Can be: 1) Exact filename: 'song.mp3', 2) Path: 'Pop/song.mp3', 3) Case-insensitive: 'SONG.MP3', 4) Partial: 'love' matches 'In Love.mp3'", 
                "required": True
            }
        }
    },
    "stop_music": {
        "handler": stop_music, 
        "description": "Stop currently playing music by closing Windows Media Player. Use when user wants to stop/pause music.", 
        "parameters": {}
    },
    "search_music": {
        "handler": search_music, 
        "description": "Search for songs by keyword and AUTO-PLAY first match (default). Perfect for: 'play songs with love', 'play rock music', 'find and play remix'. Returns matching files + auto-plays first result. Set auto_play=False to only search without playing.", 
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
    "find_in_document": {"handler": find_in_document, "description": "Tìm trong tài liệu (Ctrl+F)", "parameters": {"search_text": {"type": "string", "description": "Nội dung tìm kiếm", "required": True}}}
}

# ============================================================
# XIAOZHI MCP CLIENT
# ============================================================

async def handle_xiaozhi_message(message: dict) -> dict:
    method = message.get("method")
    params = message.get("params", {})
    
    if method == "initialize":
        return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "xiaozhi-final", "version": "4.0.0"}}
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
        if tool_name not in TOOLS:
            error_msg = f"Error: Tool '{tool_name}' not found"
            print(f"❌ {error_msg}")
            return {"content": [{"type": "text", "text": error_msg}], "isError": True}
        try:
            result = await TOOLS[tool_name]["handler"](**args)
            print(f"✅ [Tool Result] {tool_name}: {result}")
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
        except Exception as e:
            error_msg = f"Error calling {tool_name}: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
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
                
                init_msg = {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "xiaozhi-final", "version": "4.0.0"}}, "id": 1}
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

app = FastAPI(title="Xiaozhi Final", version="4.0.0")

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
    <title>🚀 Xiaozhi MCP - Điều Khiển Máy Tính</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; }
        
        /* SIDEBAR */
        .sidebar { width: 280px; background: #1a1a2e; color: white; padding: 30px 20px; display: flex; flex-direction: column; box-shadow: 2px 0 20px rgba(0,0,0,0.3); }
        .logo { font-size: 1.5em; font-weight: bold; margin-bottom: 40px; text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; }
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
        .log-panel { background: #1a1a2e; color: white; border-radius: 15px; padding: 25px; max-height: 400px; overflow-y: auto; font-family: 'Courier New', monospace; }
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
    </style>
</head>
<body>
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="logo">🚀 Xiaozhi MCP<br><small style="font-size:0.6em;opacity:0.8;">Điều Khiển Máy Tính</small></div>
        <div class="menu-item active" onclick="showSection('dashboard')">📊 Dashboard</div>
        <div class="menu-item" onclick="showSection('tools')">🛠️ Công Cụ</div>
        <div class="menu-item" onclick="showSection('log')">📋 Log</div>
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
            <h2 style="color:#667eea;margin-bottom:20px;">🚀 Tất cả công cụ (20 Tools)</h2>
            <div class="quick-actions">
                <!-- HỆ THỐNG (5) -->
                <div class="action-card blue" onclick="setVolumeQuick(50)"><div class="icon">🔊</div><div class="title">Điều Chỉnh Âm Lượng</div></div>
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
        
        <!-- LOG SECTION -->
        <div id="log-section" style="display:none;">
            <div class="log-panel" id="log"></div>
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
            document.getElementById('log-section').style.display = name === 'log' ? 'block' : 'none';
        }
        
        // Tab switching
        function switchTab(index) {
            document.querySelectorAll('.tab-btn').forEach((btn, i) => btn.classList.toggle('active', i === index));
            document.querySelectorAll('.tab-content').forEach((content, i) => content.classList.toggle('active', i === index));
        }
        
        // Quick actions - 20 tools
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
        
        connectWS();
        // Giảm polling từ 5s xuống 10s để giảm tải
        setInterval(getResources, 10000);
        getResources();
    </script>
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


# ===== 23 API ENDPOINTS MỚI (Tool 8-30) =====

@app.post("/api/tool/open_application")
async def api_open_app(data: dict):
    result = await open_application(data.get("app_name", ""))
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

@app.post("/api/tool/set_brightness")
async def api_brightness(data: dict):
    result = await set_brightness(data.get("level", 50))
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


@app.get("/api/endpoints")
async def get_endpoints():
    return {"endpoints": endpoints_config}

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
        
        return {"success": True, "message": f"Đã lưu {len(devices)} thiết bị vào file" + (" và đang kết nối lại..." if should_reconnect else "")}
    except Exception as e:
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
    asyncio.create_task(xiaozhi_websocket_client())

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
    print(" XIAOZHI FINAL - SIDEBAR UI")
    print("=" * 60)
    print(" Web Dashboard: http://localhost:8000")
    print(" WebSocket MCP: Multi-device support")
    print("  Tools: 30 available (20 original + 10 new from reference)")
    print(" Browser se tu dong mo sau 2 giay...")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)

