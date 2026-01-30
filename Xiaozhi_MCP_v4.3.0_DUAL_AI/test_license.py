"""
TEST LICENSE SYSTEM - Demo và kiểm tra
"""

from license_generator import LicenseKeyGenerator

def test_license_system():
    """Test toàn bộ hệ thống license"""
    
    print("=" * 70)
    print(" 🧪 TEST LICENSE SYSTEM - miniZ MCP v4.3.0")
    print("=" * 70)
    
    generator = LicenseKeyGenerator()
    
    # Test 1: Tạo license mới
    print("\n✅ TEST 1: Tạo license key mới")
    print("-" * 70)
    
    license_data = generator.create_license(
        customer_name="Nguyen Van Test",
        license_type="standard",
        duration_days=365,
        max_devices=1,
        notes="License test"
    )
    
    test_key = license_data['license_key']
    print(f"License Key: {test_key}")
    print(f"Customer: {license_data['customer_name']}")
    print(f"Type: {license_data['license_type']}")
    print(f"Expires: {license_data['expires_at']}")
    
    # Test 2: Verify license lần đầu (kích hoạt máy 1)
    print("\n✅ TEST 2: Kích hoạt lần đầu (Hardware ID 1)")
    print("-" * 70)
    
    hw_id_1 = "TEST-HARDWARE-ID-001"
    result = generator.verify_license(test_key, hw_id_1)
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 3: Verify lại trên cùng máy (OK)
    print("\n✅ TEST 3: Kích hoạt lại trên cùng máy (Hardware ID 1)")
    print("-" * 70)
    
    result = generator.verify_license(test_key, hw_id_1)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 4: Thử kích hoạt máy thứ 2 (Fail - vượt giới hạn)
    print("\n❌ TEST 4: Kích hoạt máy thứ 2 (Hardware ID 2) - PHẢI FAIL")
    print("-" * 70)
    
    hw_id_2 = "TEST-HARDWARE-ID-002"
    result = generator.verify_license(test_key, hw_id_2)
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Expected: success=False (đã đạt giới hạn 1 máy)")
    
    # Test 5: Deactivate máy 1
    print("\n🔓 TEST 5: Deactivate Hardware ID 1")
    print("-" * 70)
    
    success = generator.deactivate_device(test_key, hw_id_1)
    print(f"Deactivate Success: {success}")
    
    # Test 6: Kích hoạt máy 2 sau khi deactivate máy 1 (OK)
    print("\n✅ TEST 6: Kích hoạt máy 2 sau khi deactivate máy 1")
    print("-" * 70)
    
    result = generator.verify_license(test_key, hw_id_2)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 7: Revoke license
    print("\n⛔ TEST 7: Revoke (vô hiệu hóa) license")
    print("-" * 70)
    
    success = generator.revoke_license(test_key, "Test revoke")
    print(f"Revoke Success: {success}")
    
    # Test 8: Thử verify license đã revoke (Fail)
    print("\n❌ TEST 8: Verify license đã revoke - PHẢI FAIL")
    print("-" * 70)
    
    result = generator.verify_license(test_key, hw_id_2)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 9: Tạo Enterprise license (nhiều máy)
    print("\n✅ TEST 9: Tạo Enterprise license (5 máy)")
    print("-" * 70)
    
    ent_license = generator.create_license(
        customer_name="Company ABC",
        license_type="enterprise",
        duration_days=365,
        max_devices=5,
        notes="Enterprise package"
    )
    
    ent_key = ent_license['license_key']
    print(f"Enterprise Key: {ent_key}")
    print(f"Max Devices: {ent_license['max_devices']}")
    
    # Test 10: Kích hoạt 5 máy enterprise
    print("\n✅ TEST 10: Kích hoạt 5 máy enterprise")
    print("-" * 70)
    
    for i in range(1, 6):
        hw_id = f"ENTERPRISE-HW-ID-{i:03d}"
        result = generator.verify_license(ent_key, hw_id)
        print(f"Máy {i}: {result['success']} - {result['message']}")
    
    # Test 11: Thử máy thứ 6 (Fail)
    print("\n❌ TEST 11: Kích hoạt máy thứ 6 - PHẢI FAIL")
    print("-" * 70)
    
    result = generator.verify_license(ent_key, "ENTERPRISE-HW-ID-006")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Summary
    print("\n" + "=" * 70)
    print(" 📊 SUMMARY")
    print("=" * 70)
    
    all_licenses = generator.list_licenses()
    print(f"Tổng số license đã tạo: {len(all_licenses)}")
    
    for lic in all_licenses:
        devices_count = len(lic.get('activated_devices', []))
        print(f"\n📋 {lic['license_key']}")
        print(f"   Customer: {lic['customer_name']}")
        print(f"   Type: {lic['license_type']}")
        print(f"   Status: {lic['status']}")
        print(f"   Devices: {devices_count}/{lic['max_devices']}")
    
    print("\n" + "=" * 70)
    print(" ✅ TEST HOÀN TẤT!")
    print("=" * 70)
    print("\n💡 Lưu ý:")
    print("   - File license_database.json đã được tạo")
    print("   - Chạy 'python license_generator.py' để quản lý license")
    print("   - Xem LICENSE_SYSTEM_README.md để biết thêm chi tiết")
    print()


if __name__ == "__main__":
    test_license_system()
