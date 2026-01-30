"""
miniZ MCP Startup Manager
Quản lý khởi động cùng Windows
"""

import os
import sys
import ctypes
from pathlib import Path

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

APP_NAME = "miniZ_MCP"

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_startup_registry_key():
    """Get Windows startup registry key"""
    if not WINREG_AVAILABLE:
        return None
    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_ALL_ACCESS
    )

def enable_startup(exe_path: str = None, run_hidden: bool = True):
    """Enable startup with Windows"""
    if not WINREG_AVAILABLE:
        print("❌ winreg not available on this platform")
        return False
    
    try:
        key = get_startup_registry_key()
        if key is None:
            return False
        
        # Use current executable if not specified
        if exe_path is None:
            exe_path = sys.executable
        
        # Add --hidden flag for background mode
        value = f'"{exe_path}"'
        if run_hidden:
            value += " --hidden"
        
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        print(f"✅ Đã bật khởi động cùng Windows")
        print(f"   Path: {value}")
        return True
    except Exception as e:
        print(f"❌ Error enabling startup: {e}")
        return False

def disable_startup():
    """Disable startup with Windows"""
    if not WINREG_AVAILABLE:
        return False
    
    try:
        key = get_startup_registry_key()
        if key is None:
            return False
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"✅ Đã tắt khởi động cùng Windows")
        return True
    except FileNotFoundError:
        print("ℹ️ Startup đã được tắt sẵn")
        return True  # Already disabled
    except Exception as e:
        print(f"❌ Error disabling startup: {e}")
        return False

def is_startup_enabled():
    """Check if startup is enabled"""
    if not WINREG_AVAILABLE:
        return False
    
    try:
        key = get_startup_registry_key()
        if key is None:
            return False
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def toggle_startup(exe_path: str = None):
    """Toggle startup on/off"""
    if is_startup_enabled():
        return disable_startup()
    else:
        return enable_startup(exe_path)

def get_startup_info():
    """Get startup configuration info"""
    if not WINREG_AVAILABLE:
        return {"enabled": False, "path": None, "platform_supported": False}
    
    try:
        key = get_startup_registry_key()
        if key is None:
            return {"enabled": False, "path": None, "platform_supported": True}
        
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return {"enabled": True, "path": value, "platform_supported": True}
    except FileNotFoundError:
        return {"enabled": False, "path": None, "platform_supported": True}
    except Exception as e:
        return {"enabled": False, "path": None, "error": str(e), "platform_supported": True}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="miniZ MCP Startup Manager")
    parser.add_argument("--enable", action="store_true", help="Enable startup with Windows")
    parser.add_argument("--disable", action="store_true", help="Disable startup with Windows")
    parser.add_argument("--toggle", action="store_true", help="Toggle startup on/off")
    parser.add_argument("--status", action="store_true", help="Check startup status")
    parser.add_argument("--hidden", action="store_true", help="Run hidden (with tray)")
    
    args = parser.parse_args()
    
    if args.enable:
        enable_startup(run_hidden=args.hidden)
    elif args.disable:
        disable_startup()
    elif args.toggle:
        toggle_startup()
    else:
        # Default: show status
        info = get_startup_info()
        print(f"\n{'='*50}")
        print(f"  miniZ MCP Startup Manager")
        print(f"{'='*50}")
        print(f"  Status: {'✅ Enabled' if info['enabled'] else '❌ Disabled'}")
        if info.get('path'):
            print(f"  Path: {info['path']}")
        if not info.get('platform_supported'):
            print(f"  ⚠️ Windows registry not available on this platform")
        print(f"{'='*50}")
        print(f"\nUsage:")
        print(f"  python startup_manager.py --enable   Enable startup")
        print(f"  python startup_manager.py --disable  Disable startup")
        print(f"  python startup_manager.py --toggle   Toggle on/off")
