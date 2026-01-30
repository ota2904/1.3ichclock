"""
Test Auto Document Processing với Gemini 2.5 Flash
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 TEST AUTO DOCUMENT PROCESSING WITH GEMINI 2.5 FLASH")
print("=" * 70)
print()

# Test queries
test_queries = [
    "Cho tôi biết thông tin trong cơ sở dữ liệu",
    "Tìm trong tài liệu xem có thông tin gì về khách hàng",
    "Đọc file config.json và cho tôi biết các settings",
    "Trong database có bao nhiêu records?",
    "Tóm tắt nội dung các files PDF",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}/{len(test_queries)}")
    print(f"{'='*70}")
    print(f"📝 Query: {query}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/smart_chat",
            json={
                "query": query,
                "model": "models/gemini-2.5-flash"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("auto_document_processing"):
                print("✅ Auto Document Processing ACTIVATED!")
                print(f"📚 Documents found: {len(result.get('documents_found', []))}")
                print(f"🤖 Model used: {result.get('model')}")
                print(f"💬 Response: {result.get('response', 'N/A')[:200]}...")
            else:
                print("⚠️  Auto Document Processing NOT activated")
                print(f"Intent: {result.get('intent', 'N/A')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Is the server running?")
        print("   Run: python xiaozhi_final.py")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("=" * 70)
print("✨ TEST COMPLETE")
print("=" * 70)
print()
print("💡 TIP: Make sure to index documents first:")
print("   POST /api/knowledge/index_directory")
print("   {\"directory\": \"path/to/your/documents\"}")
