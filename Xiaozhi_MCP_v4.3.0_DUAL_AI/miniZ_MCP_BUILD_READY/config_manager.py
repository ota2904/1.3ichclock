#!/usr/bin/env python3
"""
Config Manager với Auto-Save và Encryption
Tự động lưu API keys và cấu hình khi thay đổi
"""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib

class ConfigManager:
    """
    Quản lý cấu hình với auto-save và mã hóa
    """
    
    def __init__(self, config_file="xiaozhi_endpoints.json"):
        self.config_file = Path(config_file)
        self.config = {}
        self.cipher = None
        self._init_encryption()
        self.load()
    
    def _init_encryption(self):
        """Khởi tạo encryption key từ machine ID"""
        try:
            # Tạo key từ machine-specific data
            import platform
            import uuid
            
            machine_id = f"{platform.node()}-{uuid.getnode()}"
            key_material = hashlib.sha256(machine_id.encode()).digest()
            key = base64.urlsafe_b64encode(key_material)
            self.cipher = Fernet(key)
        except Exception as e:
            print(f"⚠️ Encryption init failed: {e}")
            self.cipher = None
    
    def _encrypt(self, data: str) -> str:
        """Mã hóa dữ liệu"""
        if not self.cipher:
            return data
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except:
            return data
    
    def _decrypt(self, data: str) -> str:
        """Giải mã dữ liệu"""
        if not self.cipher:
            return data
        try:
            return self.cipher.decrypt(data.encode()).decode()
        except:
            return data
    
    def load(self) -> dict:
        """Load config từ file"""
        if not self.config_file.exists():
            self.config = self._create_default()
            self.save()
            return self.config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Giải mã API keys nếu được mã hóa
            if data.get('encrypted', False):
                for key in ['gemini_api_key', 'openai_api_key', 'serper_api_key']:
                    if key in data and data[key]:
                        data[key] = self._decrypt(data[key])
            
            self.config = data
            return self.config
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
            self.config = self._create_default()
            return self.config
    
    def save(self):
        """Auto-save config với mã hóa"""
        try:
            # Mã hóa API keys trước khi lưu
            save_data = self.config.copy()
            save_data['encrypted'] = True
            
            for key in ['gemini_api_key', 'openai_api_key', 'serper_api_key']:
                if key in save_data and save_data[key]:
                    save_data[key] = self._encrypt(save_data[key])
            
            save_data['last_saved'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"⚠️ Config save error: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set config value và auto-save"""
        self.config[key] = value
        self.save()
    
    def update(self, **kwargs):
        """Update nhiều values và auto-save"""
        self.config.update(kwargs)
        self.save()
    
    def _create_default(self) -> dict:
        """Create default config"""
        return {
            "endpoints": [
                {"name": "Thiết bị 1", "token": "", "enabled": False},
                {"name": "Thiết bị 2", "token": "", "enabled": False},
                {"name": "Thiết bị 3", "token": "", "enabled": False}
            ],
            "active_index": 0,
            "gemini_api_key": "",
            "openai_api_key": "",
            "serper_api_key": "",
            "auto_start": True,  # Mặc định bật auto-start
            "start_minimized": True,  # Khởi động ẩn vào tray
            "encrypted": False,
            "last_saved": None
        }

# Global config manager instance
_config_manager = None

def get_config_manager():
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
