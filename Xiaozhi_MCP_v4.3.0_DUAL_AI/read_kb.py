import json
import os

kbPath = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'miniZ_MCP', 'knowledge', 'knowledge_index.json')
print(f'Path: {kbPath}')

with open(kbPath, 'r', encoding='utf-8') as f:
    data = json.load(f)

for doc in data.get('documents', []):
    file_name = doc.get('file_name', 'unknown')
    content = doc.get('content', '')
    print(f'\n📄 File: {file_name}')
    print(f'Length: {len(content):,} chars')
    print('Preview (500 chars):')
    print(content[:500])
    print('---')
