"""
miniZ MCP v4.3.0 - Generate New License Keys (Key cũ đã bị lộ)
Generated: November 28, 2025
Thay thế toàn bộ key cũ
"""

import json
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path

def generate_secure_license_key():
    """Generate a cryptographically secure license key in format XXXX-XXXX-XXXX-XXXX"""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Loại bỏ I, O, 1, 0 để tránh nhầm lẫn
    parts = []
    for _ in range(4):
        part = ''.join(secrets.choice(chars) for _ in range(4))
        parts.append(part)
    return '-'.join(parts)

def create_new_keys(count=100):
    """Create new pre-generated license keys"""
    licenses = {}
    
    for i in range(1, count + 1):
        key = generate_secure_license_key()
        
        # Ensure unique key
        while key in licenses:
            key = generate_secure_license_key()
        
        # Create license entry with unlimited duration (100 years)
        licenses[key] = {
            "license_key": key,
            "customer_name": f"miniZ License #{i}",
            "license_type": "professional",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=36500)).isoformat(),  # 100 years
            "max_devices": 1,
            "activated_devices": [],
            "status": "active",
            "notes": f"New key batch - {datetime.now().strftime('%Y%m%d')}"
        }
    
    return licenses

def main():
    print("\n" + "=" * 70)
    print("🔑 miniZ MCP v4.3.0 - TẠO 100 LICENSE KEY MỚI")
    print("=" * 70)
    print(f"📅 Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("⚠️  Keys cũ đã bị lộ - Tạo batch mới hoàn toàn")
    print("=" * 70)
    
    # Generate 100 new keys
    licenses = create_new_keys(100)
    
    # Create new database file
    db_output = {
        "licenses": licenses,
        "created_at": datetime.now().isoformat(),
        "version": "4.3.0",
        "batch_id": f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_keys": len(licenses),
        "notes": "New key batch - Previous keys compromised"
    }
    
    # Save new license database
    with open('license_database_NEW.json', 'w', encoding='utf-8') as f:
        json.dump(db_output, f, indent=2, ensure_ascii=False)
    
    # Save plain text list for admin
    with open('NEW_LICENSE_KEYS.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("🔐 miniZ MCP v4.3.0 PROFESSIONAL - DANH SÁCH LICENSE KEY MỚI\n")
        f.write("=" * 80 + "\n\n")
        f.write("⚠️  CẢNH BÁO BẢO MẬT:\n")
        f.write("-" * 80 + "\n")
        f.write("• File này chứa thông tin nhạy cảm\n")
        f.write("• KHÔNG chia sẻ file này với bất kỳ ai\n")
        f.write("• Keys cũ đã bị vô hiệu hóa\n")
        f.write("• Chỉ sử dụng keys trong file này\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("📋 THÔNG TIN BATCH:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Batch ID:         {db_output['batch_id']}\n")
        f.write(f"Tổng số keys:     100\n")
        f.write(f"Loại license:     Professional (Vô thời hạn)\n")
        f.write(f"Thiết bị/key:     1 máy\n")
        f.write(f"Ngày tạo:         {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Hết hạn:          Không giới hạn (100 năm)\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("DANH SÁCH 100 LICENSE KEYS MỚI\n")
        f.write("=" * 80 + "\n\n")
        
        keys_list = list(licenses.keys())
        for idx, key in enumerate(keys_list, 1):
            f.write(f"[{idx:03d}] {key}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("💡 HƯỚNG DẪN SỬ DỤNG:\n")
        f.write("-" * 80 + "\n")
        f.write("1. Mỗi key chỉ có thể kích hoạt trên 1 máy tính duy nhất\n")
        f.write("2. Sau khi kích hoạt, key sẽ được bind với Hardware ID của máy\n")
        f.write("3. Key có thời hạn vô tận (100 năm)\n")
        f.write("4. Kích hoạt bằng chế độ Offline\n")
        f.write("\n")
        f.write("⚠️ LƯU Ý QUAN TRỌNG:\n")
        f.write("-" * 80 + "\n")
        f.write("• KEYS CŨ ĐÃ BỊ VÔ HIỆU HÓA - KHÔNG SỬ DỤNG ĐƯỢC NỮA\n")
        f.write("• Mỗi key chỉ dùng được 1 lần (1 máy)\n")
        f.write("• Không chia sẻ key đã kích hoạt\n")
        f.write("• Key đã kích hoạt không thể chuyển sang máy khác\n")
        f.write("• GIỮ FILE NÀY BẢO MẬT TUYỆT ĐỐI!\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("miniZ Software © 2025 - All Rights Reserved\n")
        f.write("=" * 80 + "\n")
    
    # Print keys to console
    print("\n📋 DANH SÁCH 100 LICENSE KEYS MỚI:")
    print("-" * 70)
    
    keys_list = list(licenses.keys())
    for idx, key in enumerate(keys_list, 1):
        print(f"[{idx:03d}] {key}")
    
    print("\n" + "=" * 70)
    print("✅ ĐÃ TẠO THÀNH CÔNG 100 LICENSE KEY MỚI!")
    print("=" * 70)
    print(f"📁 File Database: license_database_NEW.json")
    print(f"📁 File Text:     NEW_LICENSE_KEYS.txt")
    print("\n⚠️  HÀNH ĐỘNG TIẾP THEO:")
    print("-" * 70)
    print("1. Xóa file license_database.json cũ (nếu có)")
    print("2. Đổi tên license_database_NEW.json -> license_database.json")
    print("3. Xóa file PRE_GENERATED_KEYS.txt cũ")
    print("4. Giữ bảo mật file NEW_LICENSE_KEYS.txt")
    print("=" * 70)
    
    return keys_list

if __name__ == "__main__":
    main()
