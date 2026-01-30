"""Kiểm tra nội dung Knowledge Base"""
import json
import os

kb_path = r'C:\Users\congh\AppData\Local\miniZ_MCP\knowledge\knowledge_index.json'

if os.path.exists(kb_path):
    with open(kb_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    docs = data.get('documents', [])
    print(f"Tổng số documents: {len(docs)}\n")
    
    for i, doc in enumerate(docs):
        file_name = doc.get('file_name', 'N/A')
        content = doc.get('content', '')
        print(f"{i}: {file_name}")
        print(f"   Chars: {len(content)}")
        print(f"   Preview: {content[:200]}...")
        print()
else:
    print(f"Không tìm thấy: {kb_path}")
