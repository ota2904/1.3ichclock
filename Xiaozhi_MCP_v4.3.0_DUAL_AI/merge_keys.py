import json
import os

# Load pre-generated keys
with open('pre_generated_licenses.json', encoding='utf-8') as f:
    pre_gen = json.load(f)

# Load existing database or create new
if os.path.exists('license_database.json'):
    with open('license_database.json', encoding='utf-8') as f:
        db = json.load(f)
else:
    db = {'licenses': {}}

# Merge
db['licenses'].update(pre_gen['licenses'])

# Save
with open('license_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"✅ Đã merge {len(pre_gen['licenses'])} keys vào license_database.json")
print(f"📊 Tổng số keys hiện có: {len(db['licenses'])}")
print("\n🔑 Sample keys:")
for i, key in enumerate(list(db['licenses'].keys())[:5], 1):
    print(f"  {i}. {key}")
