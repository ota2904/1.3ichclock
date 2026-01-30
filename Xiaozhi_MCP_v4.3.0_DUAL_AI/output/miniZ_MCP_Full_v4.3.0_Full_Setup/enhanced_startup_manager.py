#!/usr/bin/env python3
"""
Enhanced Startup Manager
Tự động cấu hình khởi động cùng Windows
"""

import os
import sys
import winreg
from pathlib import Path

class StartupManager:
    """Quản lý khởi động cùng Windows"""
    
    APP_NAME = "miniZ_MCP_Full"
    
    @staticmethod
    def enable(exe_path: str = None, hidden: bool = True):
        """Bật khởi động cùng Windows"""
        try:
            if exe_path is None:
                exe_path = sys.executable
            
            # Mở registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set value với --hidden flag
            value = f'"{exe_path}"'
            if hidden:
                value += " --hidden"
            
            winreg.SetValueEx(
                key,
                StartupManager.APP_NAME,
                0,
                winreg.REG_SZ,
                value
            )
            
            winreg.CloseKey(key)
            print(f"✅ Đã bật khởi động cùng Windows")
            print(f"   Path: {value}")
            return True
        except Exception as e:
            print(f"❌ Error enabling startup: {e}")
            return False
    
    @staticmethod
    def disable():
        """Tắt khởi động cùng Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.DeleteValue(key, StartupManager.APP_NAME)
            winreg.CloseKey(key)
            print(f"✅ Đã tắt khởi động cùng Windows")
            return True
        except FileNotFoundError:
            print("ℹ️ Startup đã được tắt sẵn")
            return True
        except Exception as e:
            print(f"❌ Error disabling startup: {e}")
            return False
    
    @staticmethod
    def is_enabled() -> bool:
        """Kiểm tra xem startup có được bật không"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            value, _ = winreg.QueryValueEx(key, StartupManager.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def toggle() -> bool:
        """Toggle startup on/off"""
        if StartupManager.is_enabled():
            return StartupManager.disable()
        else:
            return StartupManager.enable()
