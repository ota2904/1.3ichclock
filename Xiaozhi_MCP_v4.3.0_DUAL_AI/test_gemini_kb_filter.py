"""
Test Gemini Smart Knowledge Base Filter
Kiểm tra khả năng lọc thông tin KB với Gemini Flash AI
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Knowledge base paths
APPDATA_KB = Path(os.environ.get("APPDATA", "")) / "miniZ_MCP" / "knowledge_base"
LOCAL_KB = Path(__file__).parent / "knowledge_base"
KNOWLEDGE_INDEX_FILE = APPDATA_KB / "kb_index.json"


async def test_gemini_smart_filter():
    """Test Gemini Smart KB Filter"""
    
    print("\n" + "="*70)
    print("🧪 TESTING GEMINI SMART KB FILTER")
    print("="*70)
    
    # Load API key
    config_file = Path(__file__).parent / "xiaozhi_config.json"
    api_key = None
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get("gemini_api_key", "")
            if api_key:
                print(f"✅ API key loaded (ends with ...{api_key[-7:]})")
    
    if not api_key:
        print("❌ No Gemini API key found")
        return
    
    # Configure Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        print("✅ Gemini configured")
    except Exception as e:
        print(f"❌ Failed to configure Gemini: {e}")
        return
    
    # Load documents from KB
    documents = []
    
    # Check KB index file
    if KNOWLEDGE_INDEX_FILE.exists():
        print(f"✅ KB index found: {KNOWLEDGE_INDEX_FILE}")
        with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
            documents = index_data.get("documents", [])
                    print(f"  {i}. {file_name} ({content_len:,} chars)")
    except Exception as e:
        print(f"❌ Error reading KB: {e}")
        return
    
    # Test scenarios
    test_cases = [
        {
            "name": "Test 1: Lấy TẤT CẢ documents (query rỗng)",
            "query": "",
            "max_chars": 50000,
            "use_gemini_summary": True
        },
        {
            "name": "Test 2: Tìm kiếm với từ khóa cụ thể",
            "query": "Lê Trung Khoa",
            "max_chars": 10000,
            "use_gemini_summary": True
        },
        {
            "name": "Test 3: Tìm kiếm với từ khóa phổ biến",
            "query": "thông tin",
            "max_chars": 10000,
            "use_gemini_summary": True
        },
        {
            "name": "Test 4: Không dùng Gemini summary",
            "query": "",
            "max_chars": 20000,
            "use_gemini_summary": False
        }
    ]
    
    for test in test_cases:
        print("\n" + "-"*70)
        print(f"🔬 {test['name']}")
        print(f"   Query: '{test['query']}'")
        print(f"   Max chars: {test['max_chars']}")
        print(f"   Gemini summary: {test['use_gemini_summary']}")
        print("-"*70)
        
        try:
            # Gọi hàm get_knowledge_context
            result = await get_knowledge_context(
                query=test['query'],
                max_chars=test['max_chars'],
                use_gemini_summary=test['use_gemini_summary']
            )
            
            # Kiểm tra kết quả
            if result.get("success"):
                print("✅ SUCCESS")
                print(f"   Total documents: {result.get('total_documents', 0)}")
                print(f"   Documents included: {result.get('documents_included', 0)}")
                print(f"   Context length: {result.get('context_length', 0):,} chars")
                print(f"   Keywords used: {result.get('keywords_used', [])}")
                print(f"   Gemini summarization: {result.get('gemini_summarization', False)}")
                print(f"   Message: {result.get('message', '')}")
                
                # Hiển thị một phần context
                context = result.get("context", "")
                if context:
                    print("\n📝 Context preview (first 500 chars):")
                    print("-" * 60)
                    print(context[:500])
                    print("-" * 60)
            else:
                print("❌ FAILED")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETED")
    print("="*70)


if __name__ == "__main__":
    # Chạy test
    asyncio.run(test_get_knowledge_context())
