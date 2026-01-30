import json
from pathlib import Path

# Check AppData knowledge index
appdata_path = Path(r"C:\Users\congh\AppData\Local\miniZ_MCP\knowledge\knowledge_index.json")

if appdata_path.exists():
    with open(appdata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    docs = data['documents']
    print(f"📚 AppData knowledge index: {len(docs)} documents\n")
    
    for i, doc in enumerate(docs, 1):
        fname = doc.get('file_name', 'unknown')
        content = doc.get('content', '')
        print(f"{i}. {fname[:50]}")
        print(f"   Content: {len(content)} chars")
        if len(content) < 100:
            print(f"   ⚠️ TOO SHORT")
        print()
else:
    print("❌ AppData knowledge index not found!")
