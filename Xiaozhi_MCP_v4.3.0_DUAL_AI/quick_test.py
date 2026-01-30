import requests

r = requests.get('http://localhost:8000/api/conversation/history')
d = r.json()
print(f'✅ Keys: {list(d.keys())}')
print(f'✅ Total messages: {d.get("total_messages")}')
print(f'✅ Messages count: {len(d.get("messages", []))}')
print('\n🎉 API FIXED!' if d.get('total_messages') is not None else '❌ STILL BROKEN')
