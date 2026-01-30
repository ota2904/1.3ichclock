"""
Pre-generated License Keys for miniZ MCP v4.3.0 Professional
100 keys - Unlimited duration - 1 device each
Generated: November 27, 2025
"""

import json
import random
import string
from datetime import datetime, timedelta

def generate_license_key():
    """Generate a random license key in format XXXX-XXXX-XXXX-XXXX"""
    chars = string.ascii_uppercase + string.digits
    parts = []
    for _ in range(4):
        part = ''.join(random.choice(chars) for _ in range(4))
        parts.append(part)
    return '-'.join(parts)

def create_100_pregenerated_keys():
    """Create 100 pre-generated license keys with unlimited duration"""
    licenses = {}
    
    for i in range(1, 101):
        key = generate_license_key()
        
        # Ensure unique key
        while key in licenses:
            key = generate_license_key()
        
        # Create license entry with unlimited duration (100 years)
        licenses[key] = {
            "license_key": key,
            "customer_name": f"Pre-generated Key #{i}",
            "license_type": "unlimited",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=36500)).isoformat(),  # 100 years
            "max_devices": 1,
            "activated_devices": [],
            "status": "active",
            "notes": "Pre-generated unlimited license"
        }
    
    return licenses

# Generate 100 keys
print("🔑 Generating 100 pre-licensed keys...")
print("=" * 60)

licenses = create_100_pregenerated_keys()

# Save to pre_generated_licenses.json
output = {
    "licenses": licenses,
    "metadata": {
        "total_keys": 100,
        "generated_date": datetime.now().isoformat(),
        "license_type": "unlimited",
        "max_devices_per_key": 1,
        "duration": "Unlimited (100 years)"
    }
}

with open('pre_generated_licenses.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Save plain text list
with open('PRE_GENERATED_KEYS.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("miniZ MCP v4.3.0 PROFESSIONAL - PRE-GENERATED LICENSE KEYS\n")
    f.write("=" * 80 + "\n\n")
    f.write("📋 THÔNG TIN:\n")
    f.write("-" * 80 + "\n")
    f.write(f"Tổng số keys:     100\n")
    f.write(f"Loại license:     Unlimited (Vô thời hạn)\n")
    f.write(f"Thiết bị/key:     1 máy\n")
    f.write(f"Ngày tạo:         {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"Hết hạn:          Không giới hạn (100 năm)\n")
    f.write("\n")
    f.write("=" * 80 + "\n")
    f.write("DANH SÁCH 100 LICENSE KEYS\n")
    f.write("=" * 80 + "\n\n")
    
    for idx, (key, data) in enumerate(licenses.items(), 1):
        f.write(f"[{idx:03d}] {key}\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("💡 HƯỚNG DẪN SỬ DỤNG:\n")
    f.write("-" * 80 + "\n")
    f.write("1. Mỗi key chỉ có thể kích hoạt trên 1 máy tính duy nhất\n")
    f.write("2. Sau khi kích hoạt, key sẽ được bind với Hardware ID của máy\n")
    f.write("3. Key có thời hạn vô tận (100 năm)\n")
    f.write("4. Không cần xác nhận online - Kích hoạt offline tự động\n")
    f.write("\n")
    f.write("⚠️ LƯU Ý:\n")
    f.write("-" * 80 + "\n")
    f.write("• Mỗi key chỉ dùng được 1 lần (1 máy)\n")
    f.write("• Không chia sẻ key đã kích hoạt\n")
    f.write("• Key đã kích hoạt không thể chuyển sang máy khác\n")
    f.write("• Giữ danh sách này bảo mật\n")
    f.write("\n" + "=" * 80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write("miniZ Software © 2025\n")
    f.write("=" * 80 + "\n")

print("\n✅ Đã tạo thành công 100 license keys!")
print(f"📁 File 1: pre_generated_licenses.json (Database)")
print(f"📁 File 2: PRE_GENERATED_KEYS.txt (Danh sách đọc)")
print("\n📋 DANH SÁCH 100 KEYS:")
print("=" * 60)

for idx, key in enumerate(licenses.keys(), 1):
    print(f"[{idx:03d}] {key}")
    if idx % 20 == 0 and idx < 100:
        print()

print("\n" + "=" * 60)
print("✅ Hoàn tất! Merge file JSON vào license_database.json")
