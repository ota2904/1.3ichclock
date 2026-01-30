"""
🧪 TEST GEMINI + SERPER API (GOOGLE SEARCH DIRECT)
Test integration của ask_gemini() với Serper API
"""

import asyncio
import sys
from pathlib import Path

# Import từ xiaozhi_final.py
sys.path.insert(0, str(Path(__file__).parent))
from xiaozhi_final import ask_gemini, GEMINI_API_KEY, SERPER_API_KEY

print("="*60)
print("🧪 TESTING GEMINI + SERPER API INTEGRATION")
print("="*60)
print()

# Check API keys
if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 10:
    print("❌ Gemini API Key not configured")
    sys.exit(1)

if not SERPER_API_KEY or len(SERPER_API_KEY) < 10:
    print("⚠️ Serper API Key not configured - will use RAG fallback")
else:
    print(f"✅ Serper API Key: ...{SERPER_API_KEY[-8:]}")

print(f"✅ Gemini API Key: ...{GEMINI_API_KEY[-8:]}\n")

async def test_ask_gemini():
    """Test ask_gemini() với các query khác nhau"""
    
    test_cases = [
        {
            "query": "Giá vàng SJC hôm nay bao nhiêu?",
            "should_trigger_search": True,
            "description": "Realtime: Giá cả"
        },
        {
            "query": "Thời tiết Hà Nội hôm nay thế nào?",
            "should_trigger_search": True,
            "description": "Realtime: Thời tiết"
        },
        {
            "query": "Tổng thống Mỹ hiện tại 2025 là ai?",
            "should_trigger_search": True,
            "description": "Realtime: Chính trị"
        },
        {
            "query": "iPhone 16 đã ra mắt chưa?",
            "should_trigger_search": True,
            "description": "Realtime: Sản phẩm"
        },
        {
            "query": "2 + 2 bằng mấy?",
            "should_trigger_search": False,
            "description": "General: Toán học"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📝 TEST {i}/{len(test_cases)}: {test['description']}")
        print(f"{'='*60}")
        print(f"Query: {test['query']}")
        print(f"Should trigger search: {test['should_trigger_search']}")
        print()
        
        try:
            result = await ask_gemini(test['query'])
            
            if result.get('success'):
                response_text = result.get('response_text', '')
                print(f"✅ SUCCESS")
                print(f"Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                
                # Check if used grounding
                if '[Gemini+Serper]' in str(result) or '[Gemini+RAG]' in str(result):
                    print(f"🔍 Google Search: ✅ USED")
                else:
                    print(f"🔍 Google Search: ❌ NOT USED")
            else:
                print(f"❌ FAILED: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        
        print()
    
    print("="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_ask_gemini())
