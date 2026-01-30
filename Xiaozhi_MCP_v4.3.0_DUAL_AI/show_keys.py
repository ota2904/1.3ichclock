import json

with open('LICENSE_KEYS.json', 'r') as f:
    data = json.load(f)

print("📊 THỐNG KÊ 150 LICENSE KEYS VĨNH VIỄN")
print("="*60)
print(f"\n📦 STANDARD: {len(data['STANDARD'])} keys (1 thiết bị)")
print(f"💎 PRO: {len(data['PRO'])} keys (2 thiết bị)")
print(f"🏆 ENTERPRISE: {len(data['ENTERPRISE'])} keys (5 thiết bị)")
print(f"\n✅ TỔNG CỘNG: {sum(len(v) for v in data.values())} keys")

print("\n" + "="*60)
print("🔑 SAMPLE KEYS (để test):")
print("="*60)
print("\nSTANDARD (5 keys đầu):")
for i, key in enumerate(data['STANDARD'][:5], 1):
    print(f"  {i}. {key}")

print("\nPRO (5 keys đầu):")
for i, key in enumerate(data['PRO'][:5], 1):
    print(f"  {i}. {key}")

print("\nENTERPRISE (5 keys đầu):")
for i, key in enumerate(data['ENTERPRISE'][:5], 1):
    print(f"  {i}. {key}")

print("\n" + "="*60)
print("💾 File: LICENSE_KEYS.json")
print("📄 Guide: LICENSE_ACTIVATION_GUIDE.md")
print("="*60)
