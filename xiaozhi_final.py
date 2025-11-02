#!/usr/bin/env python3
"""
Xiaozhi Final - Giao diện Sidebar matching Official Design
Web UI + WebSocket MCP + 20 Tools - Single File!
"""

import asyncio
import json
import subprocess
import psutil
from datetime import datetime
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import websockets

# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_ENDPOINT = {
    "name": "Thiết bị 1",
    "token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ1MzYxMSwiYWdlbnRJZCI6OTQ0MjE4LCJlbmRwb2ludElkIjoiYWdlbnRfOTQ0MjE4IiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc2MjA4NTI1OSwiZXhwIjoxNzkzNjQyODU5fQ.GK91-17mqarpETPwz7N6rZj5DaT7bJkpK7EM6lO0Rdmfztv_KeOTBP9R4Lvy3uXKMCJn3gwucvelCur95GAn5Q",
    "enabled": True
}

endpoints_config = [
    DEFAULT_ENDPOINT,
    {"name": "Thiết bị 2", "token": "", "enabled": False},
    {"name": "Thiết bị 3", "token": "", "enabled": False}
]

active_endpoint_index = 0
xiaozhi_connected = False
active_connections = []
xiaozhi_ws = None

print("🚀 Xiaozhi Final - Sidebar UI")
print(f"🌐 Web: http://localhost:8000")
print(f"📡 MCP: Multi-device ready")

# ============================================================
# TOOL IMPLEMENTATIONS (20 TOOLS)
# ============================================================

async def set_volume(level: int) -> dict:
    try:
        if not 0 <= level <= 100:
            return {"success": False, "error": "Level 0-100"}
        ps_cmd = f"$obj = New-Object -ComObject WScript.Shell; for($i=0; $i -lt 50; $i++) {{ $obj.SendKeys([char]174) }}; for($i=0; $i -lt {level}; $i+=2) {{ $obj.SendKeys([char]175) }}"
        proc = await asyncio.create_subprocess_exec("powershell", "-Command", ps_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(proc.wait(), timeout=5)
        return {"success": True, "level": level, "message": f"Âm lượng: {level}%"}
    except Exception as e:
        return {"success": False, "error": str(e)}

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

async def get_system_resources() -> dict:
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {"success": True, "data": {"cpu_percent": cpu, "memory_percent": mem.percent, "memory_used_gb": round(mem.used / (1024**3), 2), "memory_total_gb": round(mem.total / (1024**3), 2), "disk_percent": disk.percent, "disk_used_gb": round(disk.used / (1024**3), 2), "disk_total_gb": round(disk.total / (1024**3), 2)}}
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
            except:
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
                if identifier.lower() in p.info['name'].lower():
                    p.terminate()
                    killed.append(f"{p.info['name']} (PID: {p.info['pid']})")
        if killed:
            return {"success": True, "message": f"Đã tắt: {', '.join(killed)}"}
        return {"success": False, "error": f"Không tìm thấy '{identifier}'"}
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
        return {"success": True, "content": stdout.decode('utf-8', errors='ignore').strip()}
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
            except:
                pass
        return {"success": True, "disks": disks, "count": len(disks)}
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
    """Đổi theme Windows sáng/tối"""
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        value = 0 if dark_mode else 1
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
        
        mode = "tối" if dark_mode else "sáng"
        return {"success": True, "message": f"Đã chuyển sang theme {mode}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def change_wallpaper(keyword: str = "") -> dict:
    """Đổi hình nền desktop (từ API)"""
    try:
        import ctypes
        import requests
        import tempfile
        
        api_url = "https://wp.upx8.com/api.php"
        params = {"content": keyword} if keyword else {}
        
        resp = requests.get(api_url, params=params, timeout=15, allow_redirects=False)
        image_url = resp.headers.get("Location") or resp.headers.get("location")
        
        if not image_url:
            return {"success": False, "error": "Không lấy được hình nền"}
        
        img_resp = requests.get(image_url, timeout=15, stream=True)
        img_resp.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        for chunk in img_resp.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, temp_file.name, 0x01 | 0x02)
        
        theme = keyword if keyword else "ngẫu nhiên"
        return {"success": True, "message": f"Đã đổi hình nền: {theme}"}
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

async def paste_content(content: str) -> dict:
    """Dán nội dung vào vị trí con trỏ"""
    try:
        import pyperclip
        import pyautogui
        import time
        
        pyperclip.copy(content)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        
        return {"success": True, "message": f"Đã dán: {content[:50]}..."}
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
    "set_volume": {"handler": set_volume, "description": "Điều chỉnh âm lượng (0-100)", "parameters": {"level": {"type": "integer", "description": "Mức âm lượng", "required": True}}},
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
    
    # NEW TOOLS FROM REFERENCE
    "lock_computer": {"handler": lock_computer, "description": "Khóa máy tính", "parameters": {}},
    "shutdown_schedule": {"handler": shutdown_schedule, "description": "Lên lịch tắt máy", "parameters": {"action": {"type": "string", "description": "shutdown/restart/cancel", "required": True}, "delay": {"type": "integer", "description": "Trì hoãn (giây)", "required": False}}},
    "show_desktop": {"handler": show_desktop, "description": "Hiển thị desktop (Win+D)", "parameters": {}},
    "undo_operation": {"handler": undo_operation, "description": "Hoàn tác (Ctrl+Z)", "parameters": {}},
    "set_theme": {"handler": set_theme, "description": "Đổi theme Windows", "parameters": {"dark_mode": {"type": "boolean", "description": "True=tối, False=sáng", "required": False}}},
    "change_wallpaper": {"handler": change_wallpaper, "description": "Đổi hình nền", "parameters": {"keyword": {"type": "string", "description": "Từ khóa (phong cảnh, anime...)", "required": False}}},
    "get_desktop_path": {"handler": get_desktop_path, "description": "Lấy đường dẫn Desktop", "parameters": {}},
    "paste_content": {"handler": paste_content, "description": "Dán nội dung (Ctrl+V)", "parameters": {"content": {"type": "string", "description": "Nội dung cần dán", "required": True}}},
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
        if tool_name not in TOOLS:
            return {"content": [{"type": "text", "text": f"Error: Tool '{tool_name}' not found"}], "isError": True}
        try:
            result = await TOOLS[tool_name]["handler"](**args)
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
    return {"error": f"Unknown method: {method}"}

async def xiaozhi_websocket_client():
    global xiaozhi_connected, xiaozhi_ws
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
                print(f"✅ [Xiaozhi] Connected! ({ep['name']})")
                
                for conn in active_connections:
                    try:
                        await conn.send_json({"type": "endpoint_connected", "endpoint": ep['name'], "index": active_endpoint_index})
                    except:
                        pass
                
                init_msg = {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "xiaozhi-final", "version": "4.0.0"}}, "id": 1}
                await ws.send(json.dumps(init_msg))
                
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                        method = data.get("method", "unknown")
                        if method != "ping":
                            print(f"📨 [{method}]")
                        response = await handle_xiaozhi_message(data)
                        await ws.send(json.dumps({"jsonrpc": "2.0", "id": data.get("id"), "result": response}))
                        
                        for conn in active_connections:
                            try:
                                await conn.send_json({"type": "xiaozhi_activity", "method": method, "timestamp": datetime.now().isoformat()})
                            except:
                                pass
                    except:
                        pass
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
    </style>
</head>
<body>
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="logo">🚀 Xiaozhi MCP<br><small style="font-size:0.6em;opacity:0.8;">Điều Khiển Máy Tính</small></div>
        <div class="menu-item active" onclick="showSection('dashboard')">📊 Dashboard</div>
        <div class="menu-item" onclick="showSection('tools')">🛠️ Công Cụ</div>
        <div class="menu-item" onclick="showSection('config')">⚙️ Cấu hình</div>
        <div class="menu-item" onclick="showSection('log')">📋 Log</div>
    </div>
    
    <!-- MAIN CONTENT -->
    <div class="main-content">
        <!-- HEADER -->
        <div class="header">
            <h1>Dashboard</h1>
            <div class="status">
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
                        <button onclick="callAPI('/api/volume', {level: parseInt(document.getElementById('volume').value)})">Đặt âm lượng</button>
                    </div>
                    <div class="tool-card">
                        <h3>📸 Chụp màn hình</h3>
                        <button onclick="callAPI('/api/screenshot', {})">Chụp màn hình ngay</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔔 Thông báo</h3>
                        <input type="text" id="notif-title" placeholder="Tiêu đề">
                        <input type="text" id="notif-message" placeholder="Nội dung">
                        <button onclick="callAPI('/api/notification', {title: document.getElementById('notif-title').value, message: document.getElementById('notif-message').value})">Hiển thị</button>
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
                        <button onclick="callTool('set_brightness', {level: parseInt(document.getElementById('brightness').value)})">Đặt độ sáng</button>
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
        
        <!-- CONFIG SECTION -->
        <div id="config-section" style="display:none;">
            <div class="config-section">
                <h2 style="color:#667eea;margin-bottom:20px;">⚙️ Quản lý Thiết bị (3 Devices)</h2>
                <div class="device-grid" id="device-grid"></div>
                <div style="margin-top:20px;display:flex;gap:10px;justify-content:center;">
                    <button style="background:#10b981;padding:12px 24px;border:none;border-radius:8px;color:white;cursor:pointer;font-weight:bold;" onclick="loadDevices()">🔄 Tải lại</button>
                    <button style="background:#3b82f6;padding:12px 24px;border:none;border-radius:8px;color:white;cursor:pointer;font-weight:bold;" onclick="saveDevices()">💾 Lưu cấu hình</button>
                </div>
            </div>
        </div>
        
        <!-- LOG SECTION -->
        <div id="log-section" style="display:none;">
            <div class="log-panel" id="log"></div>
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
            document.getElementById('config-section').style.display = name === 'config' ? 'block' : 'none';
            document.getElementById('log-section').style.display = name === 'log' ? 'block' : 'none';
            
            if (name === 'config') loadDevices();
        }
        
        // Tab switching
        function switchTab(index) {
            document.querySelectorAll('.tab-btn').forEach((btn, i) => btn.classList.toggle('active', i === index));
            document.querySelectorAll('.tab-content').forEach((content, i) => content.classList.toggle('active', i === index));
        }
        
        // Quick actions - 20 tools
        function setVolumeQuick(level) { callAPI('/api/volume', {level}); }
        function screenshot() { callAPI('/api/screenshot', {}); }
        function notification() { callAPI('/api/notification', {title: 'Xiaozhi', message: 'Test notification'}); }
        function setBrightness() { 
            const level = prompt('Nhập độ sáng (0-100):', '50');
            if (level) callTool('set_brightness', {level: parseInt(level)});
        }
        function openApp() {
            const app = prompt('Nhập tên app (notepad/calc/paint/cmd/explorer):', 'notepad');
            if (app) callTool('open_application', {app_name: app});
        }
        function listProcesses() { callTool('list_running_processes', {limit: 10}); }
        function killProcess() {
            const id = prompt('Nhập PID hoặc tên tiến trình:', 'chrome');
            if (id) callTool('kill_process', {identifier: id});
        }
        function createFile() {
            const path = prompt('Đường dẫn file:', 'C:/test.txt');
            const content = prompt('Nội dung:', 'Hello World');
            if (path && content) callTool('create_file', {path, content});
        }
        function readFile() {
            const path = prompt('Đường dẫn file:', 'C:/test.txt');
            if (path) callTool('read_file', {path});
        }
        function listFiles() {
            const dir = prompt('Thư mục:', 'C:/Users');
            if (dir) callTool('list_files', {directory: dir});
        }
        function diskUsage() { callTool('get_disk_usage', {}); }
        function networkInfo() { callTool('get_network_info', {}); }
        function batteryStatus() { callTool('get_battery_status', {}); }
        function searchWeb() {
            const query = prompt('Từ khóa tìm kiếm:', '');
            if (query) callTool('search_web', {query});
        }
        function calculator() {
            const expr = prompt('Biểu thức toán học:', '2+2*3');
            if (expr) callAPI('/api/calculator', {expression: expr});
        }
        function getClipboard() { callTool('get_clipboard', {}); }
        function setClipboard() {
            const text = prompt('Nội dung cần copy:', '');
            if (text) callTool('set_clipboard', {text});
        }
        function playSound() {
            const freq = prompt('Tần số Hz (200-2000):', '1000');
            const dur = prompt('Thời gian ms (100-3000):', '500');
            if (freq && dur) callTool('play_sound', {frequency: parseInt(freq), duration: parseInt(dur)});
        }
        
        // NEW TOOL FUNCTIONS
        function lockComputer() {
            if (confirm('Bạn có chắc muốn khóa máy tính?')) {
                callTool('lock_computer', {});
            }
        }
        function shutdownSchedule() {
            const action = prompt('Hành động (shutdown/restart/cancel):', 'shutdown');
            const delay = prompt('Trì hoãn (giây):', '60');
            if (action) callTool('shutdown_schedule', {action: action, delay: parseInt(delay) || 0});
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
            const keyword = prompt('Từ khóa hình nền (phong cảnh, anime, v.v... hoặc để trống):', '');
            callTool('change_wallpaper', {keyword: keyword || ''});
        }
        function getDesktopPath() {
            callTool('get_desktop_path', {});
        }
        function pasteContent() {
            const content = prompt('Nhập nội dung cần dán:', '');
            if (content) callTool('paste_content', {content: content});
        }
        function pressEnter() {
            callTool('press_enter', {});
        }
        function findInDocument() {
            const searchText = prompt('Nhập nội dung tìm kiếm:', '');
            if (searchText) callTool('find_in_document', {search_text: searchText});
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
            } catch (error) {
                addLog(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        function callTool(name, params) {
            addLog(`🛠️ Tool: ${name}`, 'info');
        }
        
        async function getResources() {
            try {
                const response = await fetch('/api/resources');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('cpu').textContent = data.data.cpu_percent + '%';
                    document.getElementById('ram').textContent = data.data.memory_percent + '%';
                    document.getElementById('disk').textContent = data.data.disk_percent + '%';
                }
            } catch (error) {
                addLog(`❌ ${error.message}`, 'error');
            }
        }
        
        async function calculate() {
            const expr = document.getElementById('calc-expr').value;
            const response = await fetch('/api/calculator', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({expression: expr})
            });
            const data = await response.json();
            document.getElementById('calc-result').textContent = data.success ? data.result : data.error;
        }
        
        async function getCurrentTime() {
            const response = await fetch('/api/time');
            const data = await response.json();
            document.getElementById('time-result').textContent = data.data.datetime;
        }
        
        async function loadDevices() {
            const response = await fetch('/api/endpoints');
            const data = await response.json();
            const grid = document.getElementById('device-grid');
            grid.innerHTML = '';
            data.endpoints.forEach((ep, i) => {
                const card = document.createElement('div');
                card.className = 'device-card' + (ep.enabled ? ' active' : '');
                card.innerHTML = `
                    <h4>📱 ${ep.name}</h4>
                    <input type="text" placeholder="JWT Token" value="${ep.token}" id="token-${i}">
                    <button onclick="switchDevice(${i})">🔄 Chuyển sang thiết bị này</button>
                `;
                grid.appendChild(card);
            });
        }
        
        async function switchDevice(index) {
            const response = await fetch(`/api/endpoints/switch/${index}`, {method: 'POST'});
            const data = await response.json();
            addLog(`✅ ${data.message}`, 'success');
            loadDevices();
        }
        
        function saveDevices() {
            addLog('💾 Saving devices...', 'info');
        }
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            const time = new Date().toLocaleTimeString();
            entry.innerHTML = `<span class="log-time">${time}</span> ${message}`;
            log.insertBefore(entry, log.firstChild);
            if (log.children.length > 100) log.removeChild(log.lastChild);
        }
        
        // WebSocket
        function connectWS() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onopen = () => addLog('✅ WebSocket connected', 'success');
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
                setTimeout(connectWS, 3000);
            };
        }
        
        connectWS();
        setInterval(getResources, 5000);
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

@app.get("/api/endpoints")
async def get_endpoints():
    return {"endpoints": endpoints_config}

@app.post("/api/endpoints/switch/{index}")
async def switch_endpoint(index: int):
    global active_endpoint_index
    if 0 <= index < len(endpoints_config):
        if endpoints_config[index]["token"]:
            active_endpoint_index = index
            return {"success": True, "message": f"Đã chuyển sang {endpoints_config[index]['name']}"}
        raise HTTPException(400, "Token is empty")
    raise HTTPException(404, "Invalid device index")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({"type": "xiaozhi_status", "connected": xiaozhi_connected})
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except:
        pass
    finally:
        active_connections.remove(websocket)

@app.on_event("startup")
async def startup():
    asyncio.create_task(xiaozhi_websocket_client())

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 XIAOZHI FINAL - SIDEBAR UI")
    print("=" * 60)
    print("📊 Web Dashboard: http://localhost:8000")
    print("🔌 WebSocket MCP: Multi-device support")
    print("🛠️  Tools: 30 available (20 original + 10 new from reference)")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
