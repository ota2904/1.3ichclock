"""
miniZ MCP v4.3.0 - License Key Generator (Admin Tool)
Tạo license key và quản lý database
"""

import hashlib
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class LicenseKeyGenerator:
    """Generate and manage license keys"""
    
    LICENSE_DB = Path("license_database.json")
    
    def __init__(self):
        self.db = self._load_database()
    
    def _load_database(self) -> dict:
        """Load license database"""
        if self.LICENSE_DB.exists():
            with open(self.LICENSE_DB, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "licenses": {},
            "created_at": datetime.now().isoformat(),
            "version": "4.3.0"
        }
    
    def _save_database(self):
        """Save license database"""
        with open(self.LICENSE_DB, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    def generate_license_key(self) -> str:
        """Generate a random license key in format XXXX-XXXX-XXXX-XXXX"""
        parts = []
        for _ in range(4):
            # Generate 4 random alphanumeric characters
            part = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(4))
            parts.append(part)
        return '-'.join(parts)
    
    def create_license(
        self,
        customer_name: str,
        license_type: str = "standard",
        duration_days: int = 365,
        max_devices: int = 1,
        notes: str = ""
    ) -> dict:
        """
        Create a new license
        
        Args:
            customer_name: Tên khách hàng
            license_type: Loại license (trial, standard, professional, enterprise)
            duration_days: Số ngày sử dụng (365 = 1 năm)
            max_devices: Số máy tối đa (mặc định 1)
            notes: Ghi chú thêm
        
        Returns:
            Dict chứa thông tin license
        """
        license_key = self.generate_license_key()
        
        # Ensure unique key
        while license_key in self.db['licenses']:
            license_key = self.generate_license_key()
        
        expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        license_data = {
            "license_key": license_key,
            "customer_name": customer_name,
            "license_type": license_type,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "duration_days": duration_days,
            "max_devices": max_devices,
            "activated_devices": [],  # List of hardware IDs
            "status": "active",
            "notes": notes
        }
        
        self.db['licenses'][license_key] = license_data
        self._save_database()
        
        return license_data
    
    def verify_license(self, license_key: str, hardware_id: str) -> dict:
        """
        Verify and activate license
        
        Returns:
            Dict with success status and message
        """
        if license_key not in self.db['licenses']:
            return {
                "success": False,
                "message": "License key không tồn tại"
            }
        
        license_data = self.db['licenses'][license_key]
        
        # Check status
        if license_data['status'] != 'active':
            return {
                "success": False,
                "message": f"License đã bị vô hiệu hóa: {license_data['status']}"
            }
        
        # Check expiration
        expires_at = datetime.fromisoformat(license_data['expires_at'])
        if datetime.now() > expires_at:
            return {
                "success": False,
                "message": f"License đã hết hạn vào {expires_at.strftime('%Y-%m-%d')}"
            }
        
        # Check hardware ID
        activated_devices = license_data.get('activated_devices', [])
        
        if hardware_id in activated_devices:
            # Already activated on this device - OK
            return {
                "success": True,
                "message": "License hợp lệ (đã kích hoạt trên máy này)",
                "license_type": license_data['license_type'],
                "customer_name": license_data['customer_name'],
                "expires_at": license_data['expires_at']
            }
        
        # Check max devices
        if len(activated_devices) >= license_data['max_devices']:
            return {
                "success": False,
                "message": f"License đã đạt giới hạn {license_data['max_devices']} thiết bị.\n"
                          f"Thiết bị đã kích hoạt: {', '.join(activated_devices[:3])}"
            }
        
        # Activate on new device
        activated_devices.append(hardware_id)
        license_data['activated_devices'] = activated_devices
        license_data['last_activated'] = datetime.now().isoformat()
        self._save_database()
        
        return {
            "success": True,
            "message": f"Kích hoạt thành công! ({len(activated_devices)}/{license_data['max_devices']} thiết bị)",
            "license_type": license_data['license_type'],
            "customer_name": license_data['customer_name'],
            "expires_at": license_data['expires_at']
        }
    
    def deactivate_device(self, license_key: str, hardware_id: str) -> bool:
        """Remove hardware ID from license (để chuyển sang máy khác)"""
        if license_key not in self.db['licenses']:
            return False
        
        license_data = self.db['licenses'][license_key]
        activated_devices = license_data.get('activated_devices', [])
        
        if hardware_id in activated_devices:
            activated_devices.remove(hardware_id)
            license_data['activated_devices'] = activated_devices
            self._save_database()
            return True
        
        return False
    
    def revoke_license(self, license_key: str, reason: str = "") -> bool:
        """Vô hiệu hóa license"""
        if license_key not in self.db['licenses']:
            return False
        
        self.db['licenses'][license_key]['status'] = 'revoked'
        self.db['licenses'][license_key]['revoked_at'] = datetime.now().isoformat()
        self.db['licenses'][license_key]['revoke_reason'] = reason
        self._save_database()
        return True
    
    def list_licenses(self, filter_type: Optional[str] = None) -> list:
        """List all licenses, optionally filtered by type"""
        licenses = []
        for key, data in self.db['licenses'].items():
            if filter_type and data['license_type'] != filter_type:
                continue
            licenses.append(data)
        return licenses
    
    def get_license_info(self, license_key: str) -> Optional[dict]:
        """Get detailed info about a license"""
        return self.db['licenses'].get(license_key)


def main():
    """Main menu for license management"""
    generator = LicenseKeyGenerator()
    
    while True:
        print("\n" + "=" * 60)
        print("🔑 miniZ MCP v4.3.0 - License Key Generator")
        print("=" * 60)
        print("1. Tạo license mới")
        print("2. Xem danh sách license")
        print("3. Kiểm tra license cụ thể")
        print("4. Vô hiệu hóa license")
        print("5. Gỡ kích hoạt thiết bị")
        print("0. Thoát")
        print("=" * 60)
        
        choice = input("\nChọn chức năng (0-5): ").strip()
        
        if choice == "1":
            print("\n📝 TẠO LICENSE MỚI")
            print("-" * 60)
            customer_name = input("Tên khách hàng: ").strip()
            
            print("\nLoại license:")
            print("  1. Trial (30 ngày)")
            print("  2. Standard (1 năm)")
            print("  3. Professional (1 năm)")
            print("  4. Enterprise (1 năm, nhiều thiết bị)")
            license_type_choice = input("Chọn loại (1-4): ").strip()
            
            license_type_map = {
                "1": ("trial", 30, 1),
                "2": ("standard", 365, 1),
                "3": ("professional", 365, 1),
                "4": ("enterprise", 365, 5)
            }
            
            license_type, duration, max_devices = license_type_map.get(
                license_type_choice,
                ("standard", 365, 1)
            )
            
            custom_duration = input(f"Số ngày (Enter = {duration}): ").strip()
            if custom_duration:
                duration = int(custom_duration)
            
            if license_type == "enterprise":
                custom_devices = input(f"Số thiết bị (Enter = {max_devices}): ").strip()
                if custom_devices:
                    max_devices = int(custom_devices)
            
            notes = input("Ghi chú (tùy chọn): ").strip()
            
            license_data = generator.create_license(
                customer_name=customer_name,
                license_type=license_type,
                duration_days=duration,
                max_devices=max_devices,
                notes=notes
            )
            
            print("\n✅ TẠO LICENSE THÀNH CÔNG!")
            print("=" * 60)
            print(f"LICENSE KEY: {license_data['license_key']}")
            print(f"Khách hàng: {license_data['customer_name']}")
            print(f"Loại: {license_data['license_type']}")
            print(f"Hạn sử dụng: {license_data['expires_at']}")
            print(f"Số thiết bị: {license_data['max_devices']}")
            print("=" * 60)
            
        elif choice == "2":
            print("\n📋 DANH SÁCH LICENSE")
            print("-" * 60)
            licenses = generator.list_licenses()
            
            if not licenses:
                print("Chưa có license nào.")
            else:
                for i, lic in enumerate(licenses, 1):
                    status_emoji = "✅" if lic['status'] == 'active' else "❌"
                    print(f"{i}. {status_emoji} {lic['license_key']}")
                    print(f"   Khách hàng: {lic['customer_name']}")
                    print(f"   Loại: {lic['license_type']} | Thiết bị: {len(lic.get('activated_devices', []))}/{lic['max_devices']}")
                    print(f"   Hết hạn: {lic['expires_at']}")
                    print()
        
        elif choice == "3":
            print("\n🔍 KIỂM TRA LICENSE")
            print("-" * 60)
            license_key = input("Nhập license key: ").strip().upper()
            
            info = generator.get_license_info(license_key)
            if info:
                print(f"\n✅ Tìm thấy license:")
                print(f"Khách hàng: {info['customer_name']}")
                print(f"Loại: {info['license_type']}")
                print(f"Trạng thái: {info['status']}")
                print(f"Tạo lúc: {info['created_at']}")
                print(f"Hết hạn: {info['expires_at']}")
                print(f"Thiết bị kích hoạt: {len(info.get('activated_devices', []))}/{info['max_devices']}")
                if info.get('activated_devices'):
                    print("Hardware IDs:")
                    for hw_id in info['activated_devices']:
                        print(f"  - {hw_id}")
                if info.get('notes'):
                    print(f"Ghi chú: {info['notes']}")
            else:
                print("❌ License key không tồn tại!")
        
        elif choice == "4":
            print("\n⛔ VÔ HIỆU HÓA LICENSE")
            print("-" * 60)
            license_key = input("Nhập license key: ").strip().upper()
            reason = input("Lý do (tùy chọn): ").strip()
            
            if generator.revoke_license(license_key, reason):
                print("✅ Đã vô hiệu hóa license!")
            else:
                print("❌ License key không tồn tại!")
        
        elif choice == "5":
            print("\n🔓 GỠ KÍCH HOẠT THIẾT BỊ")
            print("-" * 60)
            license_key = input("Nhập license key: ").strip().upper()
            hardware_id = input("Nhập Hardware ID: ").strip().upper()
            
            if generator.deactivate_device(license_key, hardware_id):
                print("✅ Đã gỡ kích hoạt thiết bị!")
            else:
                print("❌ Không tìm thấy thiết bị trong license này!")
        
        elif choice == "0":
            print("\n👋 Tạm biệt!")
            break
        
        else:
            print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
