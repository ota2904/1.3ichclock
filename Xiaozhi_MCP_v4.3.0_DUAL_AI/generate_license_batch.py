"""
Generate 150 Pre-made License Keys for miniZ MCP v4.3.0
Tạo 150 license keys sẵn để phân phối cho khách hàng
"""

import hashlib
import json
import secrets
import string
from datetime import datetime, timedelta

def generate_universal_license_key(index, license_type="standard", days=365):
    """
    Tạo universal license key không gắn với hardware ID cụ thể
    Key này sẽ work với bất kỳ máy nào (dùng cho pre-made keys)
    """
    # Create unique seed for each key
    seed = f"minizMCP_v4.3.0_{index}_{license_type}_{datetime.now().timestamp()}"
    seed_hash = hashlib.sha256(seed.encode()).hexdigest()
    
    # Generate random characters for key
    chars = string.ascii_uppercase + string.digits
    key_parts = []
    
    for i in range(5):
        part = ''.join(secrets.choice(chars) for _ in range(4))
        key_parts.append(part)
    
    license_key = "-".join(key_parts)
    
    # Create metadata
    expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    metadata = {
        "key_id": index,
        "license_key": license_key,
        "type": license_type,
        "status": "available",
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expiry_date": expiry_date,
        "days_valid": days,
        "version": "4.3.0"
    }
    
    return license_key, metadata

def generate_batch_licenses():
    """Tạo 150 license keys với phân loại"""
    licenses = {
        "standard": [],
        "pro": [],
        "enterprise": []
    }
    
    all_keys = []
    
    print("\n" + "="*70)
    print("    Generating 150 Pre-made License Keys for miniZ MCP v4.3.0")
    print("="*70 + "\n")
    
    key_id = 1
    
    # Generate 100 Standard licenses (365 days)
    print("Generating 100 Standard licenses...")
    for i in range(100):
        key, metadata = generate_universal_license_key(key_id, "standard", 365)
        metadata["customer_limit"] = "Individual Use Only"
        licenses["standard"].append(metadata)
        all_keys.append(metadata)
        key_id += 1
        if (i + 1) % 20 == 0:
            print(f"  ✓ {i + 1}/100 Standard keys generated")
    
    # Generate 40 Pro licenses (730 days = 2 years)
    print("\nGenerating 40 Pro licenses...")
    for i in range(40):
        key, metadata = generate_universal_license_key(key_id, "pro", 730)
        metadata["customer_limit"] = "Professional Use"
        licenses["pro"].append(metadata)
        all_keys.append(metadata)
        key_id += 1
        if (i + 1) % 10 == 0:
            print(f"  ✓ {i + 1}/40 Pro keys generated")
    
    # Generate 10 Enterprise licenses (1825 days = 5 years)
    print("\nGenerating 10 Enterprise licenses...")
    for i in range(10):
        key, metadata = generate_universal_license_key(key_id, "enterprise", 1825)
        metadata["customer_limit"] = "Enterprise - Unlimited Machines"
        licenses["enterprise"].append(metadata)
        all_keys.append(metadata)
        key_id += 1
    
    print(f"  ✓ 10/10 Enterprise keys generated")
    
    # Save to files
    print("\n" + "="*70)
    print("Saving license keys to files...")
    print("="*70 + "\n")
    
    # Save by type
    for license_type, keys in licenses.items():
        filename = f"licenses_{license_type}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(keys, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(keys)} {license_type.upper()} keys to: {filename}")
    
    # Save all keys
    with open("licenses_all.json", 'w', encoding='utf-8') as f:
        json.dump(all_keys, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved all 150 keys to: licenses_all.json")
    
    # Create human-readable text file
    with open("LICENSE_KEYS.txt", 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("    miniZ MCP v4.3.0 - PRE-MADE LICENSE KEYS (150 Keys)\n")
        f.write("    Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("="*70 + "\n\n")
        
        for license_type in ["standard", "pro", "enterprise"]:
            f.write("\n" + "="*70 + "\n")
            f.write(f"    {license_type.upper()} LICENSE KEYS\n")
            f.write("="*70 + "\n\n")
            
            for idx, key_data in enumerate(licenses[license_type], 1):
                f.write(f"Key #{key_data['key_id']:03d} | {key_data['license_key']}\n")
                f.write(f"  Type: {license_type.upper()}\n")
                f.write(f"  Valid: {key_data['days_valid']} days (until {key_data['expiry_date']})\n")
                f.write(f"  Status: {key_data['status']}\n")
                if idx < len(licenses[license_type]):
                    f.write("\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("USAGE INSTRUCTIONS:\n")
        f.write("="*70 + "\n")
        f.write("1. Give one key to each customer\n")
        f.write("2. Customer enters key during installation\n")
        f.write("3. Mark key as 'used' in the JSON file\n")
        f.write("4. Keep track of which customer has which key\n")
        f.write("\n© 2024-2025 miniZ MCP. All rights reserved.\n")
    
    print(f"✓ Saved human-readable list to: LICENSE_KEYS.txt")
    
    # Create key distribution tracking
    tracking = {
        "total_keys": 150,
        "available": 150,
        "used": 0,
        "by_type": {
            "standard": {"total": 100, "available": 100, "used": 0},
            "pro": {"total": 40, "available": 40, "used": 0},
            "enterprise": {"total": 10, "available": 10, "used": 0}
        },
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("license_tracking.json", 'w', encoding='utf-8') as f:
        json.dump(tracking, f, indent=2)
    print(f"✓ Created tracking file: license_tracking.json")
    
    # Print summary
    print("\n" + "="*70)
    print("    ✅ GENERATION COMPLETE")
    print("="*70)
    print(f"\nTotal Keys Generated: 150")
    print(f"  • Standard (365 days):   100 keys")
    print(f"  • Pro (730 days):        40 keys")
    print(f"  • Enterprise (1825 days): 10 keys")
    print(f"\nFiles Created:")
    print(f"  📄 LICENSE_KEYS.txt         - Human-readable list")
    print(f"  📄 licenses_all.json        - All keys (JSON)")
    print(f"  📄 licenses_standard.json   - Standard keys only")
    print(f"  📄 licenses_pro.json        - Pro keys only")
    print(f"  📄 licenses_enterprise.json - Enterprise keys only")
    print(f"  📄 license_tracking.json    - Usage tracking")
    print("\n" + "="*70 + "\n")
    
    # Show sample keys
    print("Sample Keys:")
    print(f"  Standard:   {licenses['standard'][0]['license_key']}")
    print(f"  Pro:        {licenses['pro'][0]['license_key']}")
    print(f"  Enterprise: {licenses['enterprise'][0]['license_key']}")
    print()

if __name__ == "__main__":
    generate_batch_licenses()
