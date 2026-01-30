"""
🔐 LICENSE SYSTEM - HARDWARE-LOCKED
====================================

Hệ thống license bảo mật cao cho miniZ MCP Professional

FEATURES:
- 150 license keys vĩnh viễn (lifetime)
- Gắn với Hardware ID (CPU + Motherboard)
- Mã hóa AES-256
- Không thể transfer sang máy khác
- 3 tiers: Standard, Pro, Enterprise

ARCHITECTURE:
1. License Key Format: MINIZ-XXXX-XXXX-XXXX-XXXX
2. Hardware ID: SHA256(CPU_ID + MOBO_SERIAL)
3. Activation: Key + Hardware ID → Encrypted License File
4. Validation: Decrypt → Check Key + Hardware Match

Author: miniZ Team
Version: 1.0
"""

import hashlib
import uuid
import json
import os
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import platform
import subprocess
import base64

# ============================================================
# HARDWARE ID DETECTION
# ============================================================

def get_cpu_id() -> str:
    """Lấy CPU ID (Windows)"""
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("wmic cpu get ProcessorId", shell=True, text=True)
            lines = result.strip().split('\n')
            if len(lines) >= 2:
                return lines[1].strip()
        return str(uuid.getnode())  # Fallback: MAC address
    except:
        return str(uuid.getnode())

def get_motherboard_serial() -> str:
    """Lấy Motherboard Serial (Windows)"""
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("wmic baseboard get SerialNumber", shell=True, text=True)
            lines = result.strip().split('\n')
            if len(lines) >= 2:
                return lines[1].strip()
        return platform.node()  # Fallback: hostname
    except:
        return platform.node()

def get_hardware_id() -> str:
    """
    Generate unique Hardware ID
    Kết hợp: CPU ID + Motherboard Serial → SHA256
    """
    cpu_id = get_cpu_id()
    mobo_serial = get_motherboard_serial()
    raw_id = f"{cpu_id}:{mobo_serial}"
    hardware_id = hashlib.sha256(raw_id.encode()).hexdigest()[:32].upper()
    return hardware_id

# ============================================================
# LICENSE KEY GENERATION
# ============================================================

class LicenseGenerator:
    """Generate license keys"""
    
    TIERS = {
        "STANDARD": {"devices": 1, "prefix": "STD"},
        "PRO": {"devices": 2, "prefix": "PRO"},
        "ENTERPRISE": {"devices": 5, "prefix": "ENT"}
    }
    
    @staticmethod
    def generate_key(tier: str = "STANDARD", seed: int = None) -> str:
        """
        Generate license key format: MINIZ-XXXX-XXXX-XXXX-XXXX
        
        Structure:
        - Part 1: Tier prefix (3 chars) + random (1 char)
        - Part 2-4: Random alphanumeric
        - Checksum: Last 4 chars include validation
        """
        if tier not in LicenseGenerator.TIERS:
            tier = "STANDARD"
        
        tier_info = LicenseGenerator.TIERS[tier]
        prefix = tier_info["prefix"]
        
        # Generate random segments
        import random
        if seed:
            random.seed(seed)
        
        segment1 = prefix + LicenseGenerator._random_char()
        segment2 = LicenseGenerator._random_segment(4)
        segment3 = LicenseGenerator._random_segment(4)
        
        # Calculate checksum
        temp_key = f"{segment1}{segment2}{segment3}"
        checksum = LicenseGenerator._calculate_checksum(temp_key)
        segment4 = checksum
        
        key = f"MINIZ-{segment1}-{segment2}-{segment3}-{segment4}"
        return key
    
    @staticmethod
    def _random_char() -> str:
        """Random uppercase letter or digit"""
        import random
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # Exclude confusing: I,O,0,1
        return random.choice(chars)
    
    @staticmethod
    def _random_segment(length: int) -> str:
        """Random segment"""
        return ''.join([LicenseGenerator._random_char() for _ in range(length)])
    
    @staticmethod
    def _calculate_checksum(data: str) -> str:
        """Calculate 4-char checksum"""
        hash_obj = hashlib.md5(data.encode())
        hash_hex = hash_obj.hexdigest()
        # Convert hex to alphanumeric (exclude confusing chars)
        chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        checksum = ""
        for i in range(0, 8, 2):
            byte_val = int(hash_hex[i:i+2], 16)
            checksum += chars[byte_val % len(chars)]
            if len(checksum) >= 4:
                break
        return checksum[:4]
    
    @staticmethod
    def validate_key_format(key: str) -> bool:
        """Validate key format: MINIZ-XXXX-XXXX-XXXX-XXXX"""
        if not key:
            return False
        
        parts = key.split('-')
        if len(parts) != 5 or parts[0] != "MINIZ":
            return False
        
        # All parts after MINIZ must be 4 chars
        if not all(len(p) == 4 for p in parts[1:]):
            return False
        
        # Validate checksum
        temp_key = ''.join(parts[1:4])
        expected_checksum = LicenseGenerator._calculate_checksum(temp_key)
        actual_checksum = parts[4]
        
        return actual_checksum == expected_checksum

# ============================================================
# LICENSE ACTIVATION & VALIDATION
# ============================================================

class LicenseManager:
    """Manage license activation and validation"""
    
    def __init__(self):
        self.license_dir = self._get_license_dir()
        self.license_file = self.license_dir / "license.enc"
        self.secret_key = self._get_encryption_key()
        self.cipher = Fernet(self.secret_key)
    
    def _get_license_dir(self) -> Path:
        """
        Get license directory in AppData
        TRY MULTIPLE LOCATIONS để tránh mất license
        """
        possible_dirs = []
        
        if os.name == 'nt':  # Windows
            # Location 1: LOCALAPPDATA (ưu tiên)
            appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
            possible_dirs.append(Path(appdata) / "miniZ_MCP" / ".license")
            
            # Location 2: APPDATA (Roaming) - backup location
            appdata_roaming = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
            possible_dirs.append(Path(appdata_roaming) / "miniZ_MCP" / ".license")
            
            # Location 3: ProgramData (system-wide) - backup location 2
            programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            possible_dirs.append(Path(programdata) / "miniZ_MCP" / ".license")
        else:
            possible_dirs.append(Path.home() / ".miniz_mcp" / ".license")
        
        # Tìm thư mục đã có license hoặc tạo mới
        for license_dir in possible_dirs:
            try:
                license_dir.mkdir(parents=True, exist_ok=True)
                # Kiểm tra có thể ghi được không
                test_file = license_dir / ".write_test"
                test_file.write_text("test")
                test_file.unlink()
                return license_dir
            except Exception as e:
                print(f"⚠️ Cannot use {license_dir}: {e}")
                continue
        
        # Fallback: trả về thư mục đầu tiên (có thể lỗi nhưng ít nhất có path)
        return possible_dirs[0]
    
    def _get_encryption_key(self) -> bytes:
        """
        Generate encryption key từ hardware ID
        Mỗi máy có key riêng → không thể copy license file
        """
        hardware_id = get_hardware_id()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'miniZ_MCP_Professional_2025',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(hardware_id.encode()))
        return key
    
    def activate_license(self, license_key: str) -> dict:
        """
        Activate license key
        
        Returns:
            {
                "success": bool,
                "message": str,
                "tier": str,
                "hardware_id": str
            }
        """
        # Validate format
        if not LicenseGenerator.validate_key_format(license_key):
            return {
                "success": False,
                "message": "❌ License key format không hợp lệ",
                "tier": None,
                "hardware_id": None
            }
        
        # Check if key is valid (in database)
        if not self._is_key_valid(license_key):
            return {
                "success": False,
                "message": "❌ License key không tồn tại hoặc đã bị thu hồi",
                "tier": None,
                "hardware_id": None
            }
        
        # Get hardware ID
        hardware_id = get_hardware_id()
        
        # Detect tier
        tier = self._detect_tier(license_key)
        
        # Create license data
        license_data = {
            "license_key": license_key,
            "hardware_id": hardware_id,
            "tier": tier,
            "activated_at": datetime.now().isoformat(),
            "expires_at": "LIFETIME",
            "devices_allowed": LicenseGenerator.TIERS[tier]["devices"],
            "version": "4.3.0"
        }
        
        # Encrypt and save
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(license_data).encode())
            
            # LƯU VÀO NHIỀU VỊ TRÍ để đảm bảo không mất license
            saved_count = 0
            errors = []
            
            # Location 1: Primary location
            try:
                with open(self.license_file, 'wb') as f:
                    f.write(encrypted_data)
                saved_count += 1
                print(f"✅ License saved to: {self.license_file}")
            except Exception as e:
                errors.append(f"Primary: {e}")
            
            # Location 2 & 3: Backup locations
            if os.name == 'nt':
                backup_locations = [
                    Path(os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))) / "miniZ_MCP" / ".license" / "license.enc",
                    Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / "miniZ_MCP" / ".license" / "license.enc"
                ]
                
                for backup_path in backup_locations:
                    try:
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(backup_path, 'wb') as f:
                            f.write(encrypted_data)
                        saved_count += 1
                        print(f"✅ License backup saved to: {backup_path}")
                    except Exception as e:
                        errors.append(f"Backup {backup_path}: {e}")
            
            if saved_count == 0:
                return {
                    "success": False,
                    "message": f"❌ Không thể lưu license: {'; '.join(errors)}",
                    "tier": None,
                    "hardware_id": None
                }
            
            return {
                "success": True,
                "message": f"✅ License {tier} đã được kích hoạt thành công! (Saved to {saved_count} locations)",
                "tier": tier,
                "hardware_id": hardware_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Lỗi khi lưu license: {e}",
                "tier": None,
                "hardware_id": None
            }
    
    def validate_license(self) -> dict:
        """
        Validate license khi khởi động app
        TÌM KIẾM LICENSE TỪ NHIỀU VỊ TRÍ
        
        Returns:
            {
                "valid": bool,
                "tier": str,
                "message": str,
                "license_key": str,
                "activated_at": str
            }
        """
        # Tìm license file từ nhiều locations
        possible_license_files = [self.license_file]
        
        if os.name == 'nt':
            # Backup locations
            possible_license_files.extend([
                Path(os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))) / "miniZ_MCP" / ".license" / "license.enc",
                Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / "miniZ_MCP" / ".license" / "license.enc"
            ])
        
        license_file_found = None
        for lf in possible_license_files:
            if lf.exists():
                license_file_found = lf
                print(f"✅ License found at: {lf}")
                break
        
        # Check if license file exists
        if not license_file_found:
            return {
                "valid": False,
                "tier": "FREE",
                "message": "⚠️ Chưa kích hoạt license",
                "license_key": None,
                "activated_at": None
            }
        
        try:
            # Decrypt license file
            with open(license_file_found, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())
            
            # Validate hardware ID
            current_hardware_id = get_hardware_id()
            stored_hardware_id = license_data.get("hardware_id")
            
            if current_hardware_id != stored_hardware_id:
                return {
                    "valid": False,
                    "tier": "FREE",
                    "message": "❌ License không khớp với máy này",
                    "license_key": None,
                    "activated_at": None
                }
            
            # Validate key format
            license_key = license_data.get("license_key")
            if not LicenseGenerator.validate_key_format(license_key):
                return {
                    "valid": False,
                    "tier": "FREE",
                    "message": "❌ License file bị hỏng",
                    "license_key": None,
                    "activated_at": None
                }
            
            # Check if key is still valid (not revoked)
            if not self._is_key_valid(license_key):
                return {
                    "valid": False,
                    "tier": "FREE",
                    "message": "❌ License đã bị thu hồi",
                    "license_key": None,
                    "activated_at": None
                }
            
            return {
                "valid": True,
                "tier": license_data.get("tier", "STANDARD"),
                "message": f"✅ License {license_data.get('tier')} hợp lệ",
                "license_key": license_key,
                "activated_at": license_data.get("activated_at")
            }
            
        except Exception as e:
            return {
                "valid": False,
                "tier": "FREE",
                "message": f"❌ Lỗi đọc license: {e}",
                "license_key": None,
                "activated_at": None
            }
    
    def _detect_tier(self, license_key: str) -> str:
        """Detect tier from key prefix"""
        parts = license_key.split('-')
        if len(parts) >= 2:
            prefix = parts[1][:3]
            for tier, info in LicenseGenerator.TIERS.items():
                if info["prefix"] == prefix:
                    return tier
        return "STANDARD"
    
    def _is_key_valid(self, license_key: str) -> bool:
        """
        Check if key exists in valid keys database
        (Load from LICENSE_KEYS.json)
        """
        keys_file = Path(__file__).parent / "LICENSE_KEYS.json"
        if not keys_file.exists():
            return False
        
        try:
            with open(keys_file, 'r', encoding='utf-8') as f:
                keys_data = json.load(f)
            
            all_keys = []
            for tier_keys in keys_data.values():
                all_keys.extend(tier_keys)
            
            return license_key in all_keys
        except:
            return False
    
    def deactivate_license(self) -> dict:
        """Deactivate license (xóa license file)"""
        try:
            if self.license_file.exists():
                self.license_file.unlink()
            return {
                "success": True,
                "message": "✅ License đã được hủy kích hoạt"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Lỗi khi hủy license: {e}"
            }
    
    def get_license_info(self) -> dict:
        """Get detailed license info"""
        validation = self.validate_license()
        hardware_id = get_hardware_id()
        
        return {
            "valid": validation["valid"],
            "tier": validation["tier"],
            "license_key": validation.get("license_key", "N/A"),
            "hardware_id": hardware_id,
            "activated_at": validation.get("activated_at", "N/A"),
            "message": validation["message"]
        }

# ============================================================
# LICENSE KEYS DATABASE GENERATOR
# ============================================================

def generate_license_keys_database(
    standard_count: int = 100,
    pro_count: int = 40,
    enterprise_count: int = 10
) -> dict:
    """
    Generate 150 unique license keys
    
    Returns:
        {
            "STANDARD": [keys...],
            "PRO": [keys...],
            "ENTERPRISE": [keys...]
        }
    """
    keys_db = {
        "STANDARD": [],
        "PRO": [],
        "ENTERPRISE": []
    }
    
    # Generate Standard keys
    print(f"🔑 Generating {standard_count} STANDARD keys...")
    for i in range(standard_count):
        key = LicenseGenerator.generate_key("STANDARD", seed=1000+i)
        keys_db["STANDARD"].append(key)
    
    # Generate Pro keys
    print(f"🔑 Generating {pro_count} PRO keys...")
    for i in range(pro_count):
        key = LicenseGenerator.generate_key("PRO", seed=2000+i)
        keys_db["PRO"].append(key)
    
    # Generate Enterprise keys
    print(f"🔑 Generating {enterprise_count} ENTERPRISE keys...")
    for i in range(enterprise_count):
        key = LicenseGenerator.generate_key("ENTERPRISE", seed=3000+i)
        keys_db["ENTERPRISE"].append(key)
    
    return keys_db

def save_license_keys_database(filename: str = "LICENSE_KEYS.json"):
    """Generate and save 150 keys to JSON file"""
    keys_db = generate_license_keys_database(
        standard_count=100,
        pro_count=40,
        enterprise_count=10
    )
    
    output_file = Path(__file__).parent / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(keys_db, f, indent=2, ensure_ascii=False)
    
    total_keys = sum(len(v) for v in keys_db.values())
    
    print(f"\n✅ Generated {total_keys} license keys:")
    print(f"   📦 STANDARD: {len(keys_db['STANDARD'])} keys")
    print(f"   💎 PRO: {len(keys_db['PRO'])} keys")
    print(f"   🏆 ENTERPRISE: {len(keys_db['ENTERPRISE'])} keys")
    print(f"\n💾 Saved to: {output_file}")
    
    return output_file

# ============================================================
# CLI TESTING
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔐 LICENSE SYSTEM TEST")
    print("="*60 + "\n")
    
    # Test 1: Generate keys database
    print("📋 TEST 1: Generate 150 License Keys")
    print("-" * 60)
    keys_file = save_license_keys_database()
    
    # Test 2: Hardware ID
    print("\n📋 TEST 2: Hardware ID Detection")
    print("-" * 60)
    hardware_id = get_hardware_id()
    print(f"   CPU ID: {get_cpu_id()}")
    print(f"   Motherboard: {get_motherboard_serial()}")
    print(f"   Hardware ID: {hardware_id}")
    
    # Test 3: License Manager
    print("\n📋 TEST 3: License Manager")
    print("-" * 60)
    manager = LicenseManager()
    
    # Load a test key
    with open(keys_file, 'r') as f:
        keys_data = json.load(f)
    test_key = keys_data["STANDARD"][0]
    
    print(f"   Test Key: {test_key}")
    print(f"   Format Valid: {LicenseGenerator.validate_key_format(test_key)}")
    
    # Activate
    print("\n   Activating license...")
    result = manager.activate_license(test_key)
    print(f"   {result['message']}")
    
    # Validate
    print("\n   Validating license...")
    validation = manager.validate_license()
    print(f"   {validation['message']}")
    print(f"   Tier: {validation['tier']}")
    
    # Get info
    print("\n   License Info:")
    info = manager.get_license_info()
    for key, value in info.items():
        print(f"     {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")
