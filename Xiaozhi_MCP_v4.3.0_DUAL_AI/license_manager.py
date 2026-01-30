"""
miniZ MCP v4.3.0 - Professional License Management System
Copyright © 2025 miniZ Team
"""

import hashlib
import json
import os
import platform
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import requests

class LicenseManager:
    """Professional license management with hardware binding"""
    
    # Save license file to user's AppData directory (writable location)
    LICENSE_FILE = Path(os.path.expanduser("~")) / "AppData" / "Local" / "miniZ_MCP" / "miniz_license.json"
    LICENSE_SERVER = "https://api.miniz-mcp.com/license/verify"  # Your license server
    
    def __init__(self):
        # Ensure license directory exists
        self.LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.hardware_id = self._generate_hardware_id()
        self.license_data = self._load_license()
    
    def _generate_hardware_id(self) -> str:
        """Generate unique hardware ID from system info"""
        try:
            # Get CPU ID
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'ProcessorId'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                cpu_id = result.stdout.strip().split('\n')[-1].strip()
            else:
                cpu_id = str(uuid.getnode())
            
            # Get motherboard serial
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'SerialNumber'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                mb_serial = result.stdout.strip().split('\n')[-1].strip()
            else:
                mb_serial = platform.node()
            
            # Combine and hash
            combined = f"{cpu_id}-{mb_serial}-{platform.machine()}"
            hardware_hash = hashlib.sha256(combined.encode()).hexdigest()[:32]
            
            return hardware_hash.upper()
        except Exception as e:
            print(f"⚠️ Warning: Could not generate hardware ID: {e}")
            # Fallback to MAC address
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:32].upper()
    
    def _load_license(self) -> Optional[Dict[str, Any]]:
        """Load license from file"""
        if self.LICENSE_FILE.exists():
            try:
                with open(self.LICENSE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading license: {e}")
                return None
        return None
    
    def _save_license(self, license_data: Dict[str, Any]) -> bool:
        """Save license to file"""
        try:
            with open(self.LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving license: {e}")
            return False
    
    def verify_license_format(self, license_key: str) -> bool:
        """Verify license key format (XXXX-XXXX-XXXX-XXXX)"""
        parts = license_key.strip().upper().split('-')
        if len(parts) != 4:
            return False
        for part in parts:
            if len(part) != 4 or not part.isalnum():
                return False
        return True
    
    def activate_license(self, license_key: str, offline_mode: bool = False) -> Dict[str, Any]:
        """
        Activate license key and bind to hardware
        
        Args:
            license_key: License key in format XXXX-XXXX-XXXX-XXXX
            offline_mode: Skip online verification (for airgapped systems)
        
        Returns:
            Dict with success status and message
        """
        license_key = license_key.strip().upper()
        
        # Validate format
        if not self.verify_license_format(license_key):
            return {
                "success": False,
                "message": "❌ License key format không hợp lệ. Định dạng: XXXX-XXXX-XXXX-XXXX"
            }
        
        # Check if already activated on different machine
        if self.license_data:
            existing_hw_id = self.license_data.get('hardware_id')
            # Only check if hardware_id is set and different
            # Allow if no hardware_id (installer-created license) or same machine
            if existing_hw_id and existing_hw_id != self.hardware_id:
                return {
                    "success": False,
                    "message": f"❌ License key đã được kích hoạt trên máy khác!\n"
                              f"Hardware ID hiện tại: {self.hardware_id}\n"
                              f"Hardware ID đã đăng ký: {existing_hw_id}"
                }
        
        if not offline_mode:
            # Online verification with license server
            try:
                response = requests.post(
                    self.LICENSE_SERVER,
                    json={
                        'license_key': license_key,
                        'hardware_id': self.hardware_id,
                        'product': 'miniZ_MCP_v4.3.0',
                        'action': 'activate'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        license_data = {
                            'license_key': license_key,
                            'hardware_id': self.hardware_id,
                            'activated_at': datetime.now().isoformat(),
                            'expires_at': result.get('expires_at'),
                            'license_type': result.get('license_type', 'standard'),
                            'customer_name': result.get('customer_name', 'Unknown'),
                            'max_devices': result.get('max_devices', 1),
                            'verified_online': True
                        }
                        
                        if self._save_license(license_data):
                            self.license_data = license_data
                            return {
                                "success": True,
                                "message": f"✅ Kích hoạt thành công!\n"
                                          f"Loại license: {license_data['license_type']}\n"
                                          f"Khách hàng: {license_data['customer_name']}\n"
                                          f"Hạn sử dụng: {license_data['expires_at']}"
                            }
                        else:
                            return {
                                "success": False,
                                "message": "❌ Không thể lưu license file!"
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"❌ {result.get('message', 'License key không hợp lệ')}"
                        }
                else:
                    return {
                        "success": False,
                        "message": f"❌ Server trả về lỗi: {response.status_code}"
                    }
                    
            except requests.exceptions.Timeout:
                return {
                    "success": False,
                    "message": "⏱️ Timeout kết nối server. Vui lòng thử lại hoặc dùng chế độ offline."
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"❌ Lỗi kết nối server: {str(e)}\nVui lòng kiểm tra internet hoặc dùng chế độ offline."
                }
        else:
            # Offline activation (for demonstration or airgapped systems)
            # In production, this should require offline activation code from vendor
            license_data = {
                'license_key': license_key,
                'hardware_id': self.hardware_id,
                'activated_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),
                'license_type': 'offline',
                'customer_name': 'Offline User',
                'max_devices': 1,
                'verified_online': False
            }
            
            if self._save_license(license_data):
                self.license_data = license_data
                return {
                    "success": True,
                    "message": f"✅ Kích hoạt offline thành công!\n"
                              f"⚠️ Lưu ý: Chế độ offline không có hỗ trợ tự động\n"
                              f"Hardware ID: {self.hardware_id}"
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Không thể lưu license file!"
                }
    
    def check_license(self) -> Dict[str, Any]:
        """Check if license is valid and active"""
        if not self.license_data:
            return {
                "valid": False,
                "message": "Chưa kích hoạt license",
                "show_activation": True
            }
        
        # Verify hardware ID
        if self.license_data.get('hardware_id') != self.hardware_id:
            return {
                "valid": False,
                "message": f"License key đã được kích hoạt trên máy khác!\n"
                          f"Hardware ID không khớp: {self.hardware_id}",
                "show_activation": True
            }
        
        # Check expiration
        expires_at = self.license_data.get('expires_at')
        if expires_at:
            try:
                expire_date = datetime.fromisoformat(expires_at)
                if datetime.now() > expire_date:
                    return {
                        "valid": False,
                        "message": f"License đã hết hạn vào {expire_date.strftime('%Y-%m-%d')}",
                        "show_activation": True
                    }
                
                # Warning if expiring soon
                days_left = (expire_date - datetime.now()).days
                if days_left <= 30:
                    warning = f"⚠️ License sắp hết hạn trong {days_left} ngày!"
                else:
                    warning = None
                    
            except Exception as e:
                print(f"Warning: Could not parse expiration date: {e}")
                warning = None
        else:
            warning = None
        
        return {
            "valid": True,
            "message": "License hợp lệ",
            "license_data": self.license_data,
            "warning": warning,
            "show_activation": False
        }
    
    def get_hardware_id(self) -> str:
        """Get current machine's hardware ID"""
        return self.hardware_id
    
    def deactivate_license(self) -> bool:
        """Deactivate current license (for moving to another machine)"""
        if self.LICENSE_FILE.exists():
            try:
                # Notify server about deactivation
                if self.license_data and self.license_data.get('verified_online'):
                    try:
                        requests.post(
                            self.LICENSE_SERVER,
                            json={
                                'license_key': self.license_data.get('license_key'),
                                'hardware_id': self.hardware_id,
                                'action': 'deactivate'
                            },
                            timeout=5
                        )
                    except:
                        pass  # Ignore network errors during deactivation
                
                self.LICENSE_FILE.unlink()
                self.license_data = None
                return True
            except Exception as e:
                print(f"❌ Error deactivating license: {e}")
                return False
        return True


# Singleton instance
_license_manager = None

def get_license_manager() -> LicenseManager:
    """Get or create license manager instance"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager
