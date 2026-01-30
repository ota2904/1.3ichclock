import json

with open('knowledge_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

docs = data['documents']
print(f"📚 Total documents: {len(docs)}\n")

for i, doc in enumerate(docs, 1):
    content = doc.get('content', '')
    fname = doc.get('file_name', 'unknown')
    print(f"{i}. {fname}")
    print(f"   Content: {len(content)} chars")
    
    # Check if content is valid
    if len(content) < 50:
        print(f"   ⚠️ TOO SHORT - will be skipped in vector index")
    elif content.strip().startswith("%PDF-"):
        print(f"   ⚠️ PDF STRUCTURE - not properly extracted")
    else:
        print(f"   ✅ Valid for indexing")
    print()
