"""
🧪 TEST GEMINI + GOOGLE SEARCH GROUNDING
Kiểm tra tính năng tự động tìm kiếm Google khi Gemini được hỏi về thông tin thời gian thực
"""

import asyncio
import sys
import json
from pathlib import Path

# Load config
config_file = Path("xiaozhi_endpoints.json")
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
        GEMINI_API_KEY = config.get('gemini_api_key', '')
        SERPER_API_KEY = config.get('serper_api_key', '')
else:
    print("❌ Config file not found")
    sys.exit(1)

# Check API keys
if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 10:
    print("❌ Gemini API Key not configured")
    sys.exit(1)

print(f"✅ Gemini API Key: ...{GEMINI_API_KEY[-8:]}")
print(f"✅ Serper API Key: ...{SERPER_API_KEY[-8:] if SERPER_API_KEY else 'NOT SET'}\n")

# Import necessary modules
try:
    import google.generativeai as genai
    print("✅ google.generativeai imported")
except ImportError:
    print("❌ google-generativeai not installed. Run: pip install google-generativeai")
    sys.exit(1)

# Check RAG system
try:
    import rag_system
    print("✅ rag_system.py available")
    RAG_AVAILABLE = True
except ImportError:
    print("⚠️ rag_system.py not found - Google Search grounding will NOT work")
    RAG_AVAILABLE = False

print("\n" + "="*60)
print("🧪 TESTING GEMINI + GOOGLE SEARCH GROUNDING")
print("="*60 + "\n")

async def test_gemini_grounding():
    """Test Gemini with Google Search grounding for realtime queries"""
    
    # Test cases: queries that should trigger Google Search
    test_cases = [
        {
            "query": "Giá vàng SJC hôm nay bao nhiêu?",
            "should_trigger": True,
            "keywords": ["giá vàng", "hôm nay"]
        },
        {
            "query": "Thời tiết Hà Nội hôm nay thế nào?",
            "should_trigger": True,
            "keywords": ["thời tiết", "hôm nay"]
        },
        {
            "query": "Tổng thống Mỹ hiện tại là ai?",
            "should_trigger": True,
            "keywords": ["tổng thống", "hiện tại"]
        },
        {
            "query": "iPhone 16 đã ra mắt chưa?",
            "should_trigger": True,
            "keywords": ["iphone", "ra mắt"]
        },
        {
            "query": "2 + 2 bằng mấy?",
            "should_trigger": False,
            "keywords": []
        }
    ]
    
    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"🤖 Gemini configured with API key\n")
    
    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        should_trigger = test["should_trigger"]
        
        print(f"\n{'='*60}")
        print(f"📝 TEST CASE {i}/{len(test_cases)}")
        print(f"{'='*60}")
        print(f"Query: {query}")
        print(f"Expected trigger: {'YES' if should_trigger else 'NO'} (Google Search)")
        print(f"Keywords: {test['keywords']}")
        print()
        
        # Detect if should trigger RAG
        prompt_lower = query.lower()
        realtime_keywords = [
            'giá vàng', 'giá usd', 'tỷ giá', 'giá bitcoin', 'crypto',
            'thời tiết', 'weather', 'nhiệt độ', 'temperature',
            'tin tức', 'news', 'mới nhất', 'latest',
            'hôm nay', 'bây giờ', 'hiện nay', 'hiện tại', 'today', 'now', 'current',
            'tổng thống', 'president', 'thủ tướng', 'prime minister',
            'iphone', 'samsung', 'tesla', 'apple', 'ra mắt', 'launch',
            'là ai', 'là gì', 'ở đâu', 'what is', 'where is'
        ]
        needs_realtime = any(kw in prompt_lower for kw in realtime_keywords)
        
        print(f"🔍 Auto-detection: {'TRIGGERED' if needs_realtime else 'NOT TRIGGERED'}")
        
        if needs_realtime != should_trigger:
            print(f"⚠️ WARNING: Detection mismatch! Expected {should_trigger}, got {needs_realtime}")
        
        # Simulate RAG search if needed
        rag_context = ""
        if needs_realtime and RAG_AVAILABLE:
            print(f"📊 Triggering Google Search via RAG system...")
            try:
                from datetime import datetime
                from rag_system import web_search
                
                current_date = datetime.now().strftime("%Y")
                enhanced_query = f"{query} {current_date}"
                
                print(f"   Enhanced query: {enhanced_query}")
                rag_result = await web_search(enhanced_query, max_results=5)
                
                if rag_result.get('success') and rag_result.get('results'):
                    results = rag_result['results']
                    print(f"   ✅ Found {len(results)} results from Google")
                    
                    rag_context = f"\n\n📊 THÔNG TIN TỪ INTERNET (tra cứu {datetime.now().strftime('%d/%m/%Y')}):\n"
                    for idx, r in enumerate(results, 1):
                        snippet = r['snippet'][:150]
                        rag_context += f"{idx}. **{r['title']}**\n   {snippet}...\n   🔗 {r.get('url', '')}\n\n"
                        print(f"   {idx}. {r['title'][:50]}...")
                else:
                    print(f"   ❌ No results from Google Search")
            except Exception as e:
                print(f"   ❌ RAG error: {e}")
        
        # Send to Gemini
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            if rag_context:
                enhanced_prompt = f"""CÂU HỎI: {query}

{rag_context}

⚠️ Hãy trả lời dựa trên thông tin trên một cách NGẮN GỌN (1-2 câu).
Nếu có nhiều nguồn, chọn thông tin chính xác nhất."""
                prompt_to_send = enhanced_prompt
                print(f"\n🤖 Sending to Gemini with RAG context ({len(rag_context)} chars)...")
            else:
                prompt_to_send = query
                print(f"\n🤖 Sending to Gemini without RAG context...")
            
            response = model.generate_content(
                prompt_to_send,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=300
                )
            )
            
            if response and response.text:
                print(f"\n✅ GEMINI RESPONSE:")
                print(f"   {response.text.strip()}")
            else:
                print(f"\n❌ No response from Gemini")
                
        except Exception as e:
            print(f"\n❌ Gemini API error: {e}")
        
        print()
    
    print("="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_gemini_grounding())
