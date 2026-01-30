"""
Test để debug scoring cho query cụ thể (KHÔNG import xiaozhi_final.py)
"""
import json
import os

# Load knowledge base
kb_path = r"C:\Users\congh\AppData\Local\miniZ_MCP\knowledge\knowledge_index.json"
if not os.path.exists(kb_path):
    print(f"❌ KB file not found: {kb_path}")
    exit(1)

with open(kb_path, 'r', encoding='utf-8') as f:
    kb = json.load(f)

query = "ngày 24 tháng 11 năm 2025 nhóm nghiên cứu thu thập mẫu thực"
print(f"🔍 Query: {query}\n")

# Stopwords
stop_words = {'là', 'của', 'và', 'có', 'các', 'được', 'trong', 'để', 'này', 'đó', 'cho', 'với', 'từ', 'về', 'như', 'theo', 'không', 'khi', 'đã', 'sẽ', 
             'ngày', 'tháng', 'năm', 'số', 'loại', 'nhóm', 'việc', 'cũng', 'hay', 'nên', 'thể', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười',
             'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'day', 'month', 'year', 'number', 'type', 'group'}

keywords = [w.lower() for w in query.split() if w.lower() not in stop_words and len(w) > 2]
print(f"📝 Keywords after stopwords: {keywords}\n")

# Check testLLM.docx
for doc in kb["documents"]:
    if "testLLM" in doc["file_name"]:
        print(f"📄 File: {doc['file_name']}")
        print(f"📏 Content length: {len(doc['content'])} chars")
        content_lower = doc['content'].lower()
        
        # Show first 2000 chars
        print(f"\n📖 First 2000 chars:")
        print(doc['content'][:2000])
        print("\n" + "="*60 + "\n")
        
        # Check each keyword
        for kw in keywords:
            count = content_lower.count(kw)
            if count > 0:
                # Find positions
                positions = []
                idx = 0
                while len(positions) < 3:  # Show first 3 occurrences
                    idx = content_lower.find(kw, idx)
                    if idx == -1:
                        break
                    # Get context
                    start = max(0, idx - 30)
                    end = min(len(doc['content']), idx + len(kw) + 30)
                    context = doc['content'][start:end].replace('\n', ' ')
                    positions.append(f"  pos {idx}: ...{context}...")
                    idx += 1
                
                print(f"✅ '{kw}': {count} times")
                for p in positions:
                    print(p)
            else:
                print(f"❌ '{kw}': NOT FOUND")
        
        print("\n" + "="*60 + "\n")
        
        # Check if exact phrase exists
        if query.lower() in content_lower:
            print(f"🎯 EXACT PHRASE FOUND: '{query}'")
        else:
            print(f"❌ Exact phrase NOT found")
            
        # Check variations
        variations = [
            "24 tháng 11 năm 2025",
            "24/11/2025",
            "thu thập mẫu thực",
            "thu thập 3 loại mẫu",
            "nhóm nghiên cứu thu thập"
        ]
        print(f"\n🔍 Checking variations:")
        for var in variations:
            if var in content_lower:
                print(f"  ✅ '{var}' FOUND")
            else:
                print(f"  ❌ '{var}' NOT found")
        
        break

print("\n" + "="*60)
print("🧪 Test completed!")
