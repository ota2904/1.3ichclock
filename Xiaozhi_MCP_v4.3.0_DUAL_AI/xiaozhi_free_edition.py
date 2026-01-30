#!/usr/bin/env python3
"""
miniZ MCP v4.3.0 - FREE EDITION
=================================
- Không cần License Key
- Khởi động cùng Windows
- Đầy đủ tính năng
- Dễ dàng sử dụng

Copyright © 2025-2026 miniZ Team
"""

import os
import sys
import winreg
import ctypes

# ============================================================
# AUTO-STARTUP MANAGER
# ============================================================
class AutoStartupManager:
    """Quản lý khởi động cùng Windows"""
    
    APP_NAME = "miniZ_MCP_Professional"
    
    @staticmethod
    def get_exe_path():
        """Lấy đường dẫn EXE"""
        if getattr(sys, 'frozen', False):
            return sys.executable
        return os.path.abspath(__file__)
    
    @classmethod
    def enable_autostart(cls):
        """Thêm vào Startup của Windows"""
        try:
            exe_path = cls.get_exe_path()
            
            # Mở registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            # Thêm entry
            winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
            
            print(f"✅ [Startup] Đã thêm vào Windows Startup")
            return True
        except Exception as e:
            print(f"⚠️ [Startup] Không thể thêm auto-start: {e}")
            return False
    
    @classmethod
    def disable_autostart(cls):
        """Xóa khỏi Startup của Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, cls.APP_NAME)
                print(f"✅ [Startup] Đã xóa khỏi Windows Startup")
            except FileNotFoundError:
                pass  # Entry không tồn tại
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"⚠️ [Startup] Không thể xóa auto-start: {e}")
            return False
    
    @classmethod
    def is_autostart_enabled(cls):
        """Kiểm tra auto-start đã bật chưa"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            
            try:
                winreg.QueryValueEx(key, cls.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False


# ============================================================
# BYPASS LICENSE SYSTEM - FREE EDITION
# ============================================================
# Ghi đè biến LICENSE để luôn pass
LICENSE_SYSTEM_AVAILABLE = False  # Tắt hoàn toàn hệ thống license

# Fake license manager cho compatibility
class FakeLicenseManager:
    """Fake license manager - luôn trả về valid"""
    
    def check_license(self):
        return {
            'valid': True,
            'message': 'FREE EDITION - No license required',
            'license_data': {
                'license_type': 'FREE',
                'customer_name': 'Community User',
                'expiry': 'Lifetime'
            }
        }
    
    def get_hardware_id(self):
        return "FREE-EDITION"
    
    def activate_license(self, key, offline=True):
        return {'success': True, 'message': 'FREE EDITION'}

def get_license_manager():
    return FakeLicenseManager()

def show_activation_window():
    return True  # Luôn trả về activated


# ============================================================
# FIRST RUN SETUP
# ============================================================
def first_run_setup():
    """Cài đặt lần chạy đầu tiên"""
    
    # Kiểm tra nếu là lần đầu chạy
    marker_file = os.path.join(os.path.expanduser("~"), ".miniz_mcp_installed")
    
    if not os.path.exists(marker_file):
        print("🎉 Chào mừng đến với miniZ MCP FREE Edition!")
        print()
        
        # Tự động enable auto-start
        print("⚙️ Cài đặt khởi động cùng Windows...")
        AutoStartupManager.enable_autostart()
        
        # Tạo marker file
        try:
            with open(marker_file, 'w') as f:
                f.write(f"installed=true\nversion=4.3.0\n")
        except:
            pass
        
        print()
        print("✅ Cài đặt hoàn tất!")
        print("   - Ứng dụng sẽ tự động khởi động cùng Windows")
        print("   - Để tắt, vào Settings > Startup")
        print()


# ============================================================
# PATCH ORIGINAL CODE
# ============================================================
# Import và patch xiaozhi_final

def patch_and_run():
    """Patch và chạy ứng dụng chính"""
    
    # First run setup
    first_run_setup()
    
    # Patch các biến global trong xiaozhi_final
    import xiaozhi_final
    
    # Override license system
    xiaozhi_final.LICENSE_SYSTEM_AVAILABLE = False
    xiaozhi_final.get_license_manager = get_license_manager
    xiaozhi_final.show_activation_window = show_activation_window
    
    print("=" * 60)
    print("   miniZ MCP v4.3.0 - FREE EDITION")
    print("   Không cần License • Đầy đủ tính năng • Miễn phí")
    print("=" * 60)
    print()
    
    # Chạy main
    if hasattr(xiaozhi_final, 'main'):
        xiaozhi_final.main()


if __name__ == "__main__":
    patch_and_run()
