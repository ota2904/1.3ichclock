import json

with open('knowledge_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

docs = data['documents']
print(f"Total documents: {len(docs)}\n")

for i, doc in enumerate(docs, 1):
    content = doc.get('content', '')
    print(f"{i}. {doc['file_name']}: {len(content)} chars")
