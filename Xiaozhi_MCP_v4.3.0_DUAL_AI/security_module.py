"""
🔐 miniZ MCP Security Module
Bảo mật API keys và thông tin nhạy cảm

Features:
- Mã hóa API keys dựa trên Hardware ID
- Không lưu plaintext keys trong file
- Tự động decrypt khi chạy
"""

import os
import sys
import json
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# ============================================================
# HARDWARE ID GENERATION
# ============================================================

def get_hardware_id() -> str:
    """Get unique hardware ID for this machine"""
    try:
        import uuid
        import platform
        
        # Combine multiple hardware identifiers
        components = []
        
        # MAC address
        mac = uuid.getnode()
        components.append(str(mac))
        
        # Platform info
        components.append(platform.node())
        components.append(platform.machine())
        
        # Combine and hash
        combined = "-".join(components)
        hw_id = hashlib.sha256(combined.encode()).hexdigest()[:32].upper()
        
        return hw_id
    except Exception:
        # Fallback to random ID (stored in file)
        return _get_fallback_id()

def _get_fallback_id() -> str:
    """Get or create fallback ID"""
    id_file = Path.home() / ".miniz_mcp" / ".device_id"
    id_file.parent.mkdir(parents=True, exist_ok=True)
    
    if id_file.exists():
        return id_file.read_text().strip()
    else:
        new_id = secrets.token_hex(16).upper()
        id_file.write_text(new_id)
        return new_id

# ============================================================
# ENCRYPTION/DECRYPTION
# ============================================================

def _derive_key(hardware_id: str, salt: str = "miniZ_MCP_v4.3.0") -> bytes:
    """Derive encryption key from hardware ID"""
    combined = f"{hardware_id}:{salt}"
    return hashlib.sha256(combined.encode()).digest()

def encrypt_value(value: str, hardware_id: str = None) -> str:
    """Encrypt a value using XOR with derived key"""
    if not value:
        return ""
    
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    key = _derive_key(hardware_id)
    
    # XOR encryption
    encrypted_bytes = bytearray()
    for i, char in enumerate(value.encode('utf-8')):
        encrypted_bytes.append(char ^ key[i % len(key)])
    
    # Base64 encode for safe storage
    return base64.b64encode(encrypted_bytes).decode('ascii')

def decrypt_value(encrypted: str, hardware_id: str = None) -> str:
    """Decrypt a value"""
    if not encrypted:
        return ""
    
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    try:
        key = _derive_key(hardware_id)
        
        # Base64 decode
        encrypted_bytes = base64.b64decode(encrypted.encode('ascii'))
        
        # XOR decryption
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted_bytes.append(byte ^ key[i % len(key)])
        
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return ""

# ============================================================
# SECURE CONFIG STORAGE
# ============================================================

class SecureConfig:
    """Secure configuration storage with encryption"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path.home() / ".miniz_mcp" / "secure_config.enc"
        
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.hardware_id = get_hardware_id()
        self._cache: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """Load encrypted config"""
        if self.config_path.exists():
            try:
                encrypted_data = self.config_path.read_text()
                decrypted = decrypt_value(encrypted_data, self.hardware_id)
                if decrypted:
                    self._cache = json.loads(decrypted)
            except Exception:
                self._cache = {}
        else:
            self._cache = {}
    
    def _save(self):
        """Save encrypted config"""
        try:
            json_data = json.dumps(self._cache, indent=2)
            encrypted = encrypt_value(json_data, self.hardware_id)
            self.config_path.write_text(encrypted)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value"""
        return self._cache.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a config value"""
        self._cache[key] = value
        self._save()
    
    def delete(self, key: str):
        """Delete a config value"""
        if key in self._cache:
            del self._cache[key]
            self._save()
    
    def get_api_key(self, key_name: str) -> str:
        """Get an API key (auto-decrypted)"""
        return self.get(f"api_key_{key_name}", "")
    
    def set_api_key(self, key_name: str, api_key: str):
        """Set an API key (auto-encrypted)"""
        self.set(f"api_key_{key_name}", api_key)
    
    def has_api_key(self, key_name: str) -> bool:
        """Check if API key exists"""
        key = self.get_api_key(key_name)
        return bool(key and len(key) > 10)

# ============================================================
# LICENSE VALIDATION
# ============================================================

class LicenseManager:
    """Manage software license"""
    
    def __init__(self):
        self.hardware_id = get_hardware_id()
        self.license_path = Path.home() / ".miniz_mcp" / "license.key"
        self.license_path.parent.mkdir(parents=True, exist_ok=True)
    
    def generate_license_key(self, customer_name: str, expiry_days: int = 365) -> str:
        """Generate a license key for this hardware"""
        from datetime import datetime, timedelta
        
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
        
        # Create license data
        license_data = {
            "hardware_id": self.hardware_id,
            "customer": customer_name,
            "expiry": expiry_date,
            "created": datetime.now().isoformat(),
            "features": ["all"]
        }
        
        # Sign the license
        json_data = json.dumps(license_data, sort_keys=True)
        signature = hashlib.sha256(f"{json_data}:miniZ_SECRET".encode()).hexdigest()[:16]
        license_data["signature"] = signature
        
        # Encode
        license_json = json.dumps(license_data)
        license_key = base64.b64encode(license_json.encode()).decode()
        
        return license_key
    
    def validate_license(self, license_key: str = None) -> Dict[str, Any]:
        """Validate a license key"""
        try:
            if license_key is None:
                if self.license_path.exists():
                    license_key = self.license_path.read_text().strip()
                else:
                    return {"valid": False, "error": "No license found"}
            
            # Decode
            license_json = base64.b64decode(license_key.encode()).decode()
            license_data = json.loads(license_json)
            
            # Verify hardware ID
            if license_data.get("hardware_id") != self.hardware_id:
                return {"valid": False, "error": "License not valid for this device"}
            
            # Verify signature
            signature = license_data.pop("signature", None)
            json_data = json.dumps(license_data, sort_keys=True)
            expected_sig = hashlib.sha256(f"{json_data}:miniZ_SECRET".encode()).hexdigest()[:16]
            
            if signature != expected_sig:
                return {"valid": False, "error": "Invalid license signature"}
            
            # Check expiry
            expiry = datetime.strptime(license_data["expiry"], "%Y-%m-%d")
            if datetime.now() > expiry:
                return {"valid": False, "error": "License expired", "expiry": license_data["expiry"]}
            
            return {
                "valid": True,
                "customer": license_data.get("customer", "Unknown"),
                "expiry": license_data["expiry"],
                "features": license_data.get("features", [])
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def save_license(self, license_key: str):
        """Save license key to file"""
        self.license_path.write_text(license_key)
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get current license info"""
        return self.validate_license()

# ============================================================
# OBFUSCATION HELPERS
# ============================================================

def obfuscate_key_display(api_key: str) -> str:
    """Show only last 8 characters of API key"""
    if not api_key or len(api_key) < 12:
        return "***"
    return f"...{api_key[-8:]}"

def is_key_valid_format(api_key: str, key_type: str) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    
    if key_type == "gemini":
        return len(api_key) >= 30 and api_key.startswith("AI")
    elif key_type == "openai":
        return api_key.startswith("sk-") and len(api_key) >= 40
    elif key_type == "serper":
        return len(api_key) >= 20
    else:
        return len(api_key) >= 10

# ============================================================
# EXPORT FUNCTIONS
# ============================================================

# Global instances
_secure_config: Optional[SecureConfig] = None
_license_manager: Optional[LicenseManager] = None

def get_secure_config() -> SecureConfig:
    """Get singleton SecureConfig instance"""
    global _secure_config
    if _secure_config is None:
        _secure_config = SecureConfig()
    return _secure_config

def get_license_manager() -> LicenseManager:
    """Get singleton LicenseManager instance"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager

# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="miniZ MCP Security Tools")
    subparsers = parser.add_subparsers(dest="command")
    
    # Hardware ID command
    hw_parser = subparsers.add_parser("hwid", help="Show hardware ID")
    
    # Encrypt command
    enc_parser = subparsers.add_parser("encrypt", help="Encrypt a value")
    enc_parser.add_argument("value", help="Value to encrypt")
    
    # Decrypt command
    dec_parser = subparsers.add_parser("decrypt", help="Decrypt a value")
    dec_parser.add_argument("value", help="Value to decrypt")
    
    # License command
    lic_parser = subparsers.add_parser("license", help="License management")
    lic_parser.add_argument("--generate", metavar="CUSTOMER", help="Generate license for customer")
    lic_parser.add_argument("--validate", metavar="KEY", help="Validate a license key")
    lic_parser.add_argument("--info", action="store_true", help="Show current license info")
    
    # API key command
    key_parser = subparsers.add_parser("apikey", help="API key management")
    key_parser.add_argument("--set", nargs=2, metavar=("NAME", "VALUE"), help="Set API key")
    key_parser.add_argument("--get", metavar="NAME", help="Get API key (masked)")
    key_parser.add_argument("--list", action="store_true", help="List all API keys")
    
    args = parser.parse_args()
    
    if args.command == "hwid":
        print(f"\n{'='*50}")
        print(f"  Hardware ID: {get_hardware_id()}")
        print(f"{'='*50}\n")
    
    elif args.command == "encrypt":
        encrypted = encrypt_value(args.value)
        print(f"Encrypted: {encrypted}")
    
    elif args.command == "decrypt":
        decrypted = decrypt_value(args.value)
        print(f"Decrypted: {decrypted}")
    
    elif args.command == "license":
        lm = get_license_manager()
        
        if args.generate:
            key = lm.generate_license_key(args.generate)
            print(f"\n{'='*50}")
            print(f"  Generated License for: {args.generate}")
            print(f"  Hardware ID: {lm.hardware_id}")
            print(f"{'='*50}")
            print(f"\nLicense Key:\n{key}\n")
        
        elif args.validate:
            result = lm.validate_license(args.validate)
            print(f"\nValidation Result: {result}\n")
        
        elif args.info:
            info = lm.get_license_info()
            print(f"\n{'='*50}")
            print(f"  License Status")
            print(f"{'='*50}")
            for k, v in info.items():
                print(f"  {k}: {v}")
            print(f"{'='*50}\n")
        
        else:
            print("Use --generate, --validate, or --info")
    
    elif args.command == "apikey":
        config = get_secure_config()
        
        if args.set:
            name, value = args.set
            config.set_api_key(name, value)
            print(f"✅ API key '{name}' saved (encrypted)")
        
        elif args.get:
            key = config.get_api_key(args.get)
            print(f"API key '{args.get}': {obfuscate_key_display(key)}")
        
        elif args.list:
            print("\nStored API Keys:")
            for k in config._cache.keys():
                if k.startswith("api_key_"):
                    name = k.replace("api_key_", "")
                    value = config.get(k)
                    print(f"  - {name}: {obfuscate_key_display(value)}")
        
        else:
            print("Use --set, --get, or --list")
    
    else:
        parser.print_help()
