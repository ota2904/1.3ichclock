"""
Test script cho KB Search với Gemini
Chạy: python test_kb_search.py
"""
import asyncio
import json
import os
import sys

# Add path
sys.path.insert(0, os.path.dirname(__file__))

# Import constants từ xiaozhi_final
KNOWLEDGE_INDEX_FILE = os.path.join(
    os.environ.get('LOCALAPPDATA', ''),
    'miniZ_MCP', 'knowledge', 'knowledge_index.json'
)

def test_basic_search():
    """Test basic search without Gemini"""
    print("=" * 60)
    print("🧪 TEST 1: Kiểm tra Knowledge Base Index")
    print("=" * 60)
    
    if not os.path.exists(KNOWLEDGE_INDEX_FILE):
        print(f"❌ Không tìm thấy index file: {KNOWLEDGE_INDEX_FILE}")
        print("💡 Vui lòng vào Web UI > Knowledge Base để index files trước")
        return False
    
    with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    documents = index_data.get("documents", [])
    print(f"✅ Loaded {len(documents)} documents from index")
    
    # Hiển thị danh sách files
    print("\n📄 Danh sách files trong KB:")
    for i, doc in enumerate(documents[:10], 1):
        file_name = doc.get("file_name", "unknown")
        content_len = len(doc.get("content", ""))
        print(f"   {i}. {file_name} ({content_len:,} chars)")
    
    if len(documents) > 10:
        print(f"   ... và {len(documents) - 10} files khác")
    
    return True

def test_keyword_search(query: str):
    """Test keyword search"""
    print("\n" + "=" * 60)
    print(f"🧪 TEST 2: Keyword Search")
    print(f"   Query: '{query}'")
    print("=" * 60)
    
    if not os.path.exists(KNOWLEDGE_INDEX_FILE):
        print("❌ KB index không tồn tại")
        return []
    
    with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    documents = index_data.get("documents", [])
    
    # Simple keyword matching
    stop_words = {'là', 'của', 'và', 'có', 'các', 'được', 'trong', 'để', 'này', 'đó', 
                 'cho', 'với', 'từ', 'về', 'như', 'theo', 'không', 'khi', 'đã', 'sẽ',
                 'ai', 'gì', 'nào', 'đâu', 'sao', 'thế'}
    
    keywords = [w.lower() for w in query.split() if w.lower() not in stop_words and len(w) > 1]
    print(f"🔑 Keywords: {keywords}")
    
    # Find matching docs
    results = []
    for doc in documents:
        content = doc.get("content", "").lower()
        file_name = doc.get("file_name", "")
        
        match_count = sum(1 for kw in keywords if kw in content)
        if match_count > 0:
            results.append({
                "file_name": file_name,
                "match_count": match_count,
                "preview": doc.get("content", "")[:200] + "..."
            })
    
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    print(f"\n📊 Tìm thấy {len(results)} documents có liên quan:")
    for i, r in enumerate(results[:5], 1):
        print(f"\n   {i}. {r['file_name']} (matched: {r['match_count']} keywords)")
        print(f"      Preview: {r['preview'][:100]}...")
    
    return results

async def test_gemini_answer(query: str):
    """Test Gemini answering"""
    print("\n" + "=" * 60)
    print(f"🧪 TEST 3: Gemini AI Answer")
    print(f"   Query: '{query}'")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        
        # Load API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Try loading from .env
            env_file = os.path.join(os.path.dirname(__file__), '.env')
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY='):
                            api_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
        
        if not api_key:
            print("❌ Không tìm thấy GEMINI_API_KEY")
            return None
        
        print(f"✅ Gemini API key loaded (ends with ...{api_key[-8:]})")
        
        # Get context from KB
        if not os.path.exists(KNOWLEDGE_INDEX_FILE):
            print("❌ KB index không tồn tại")
            return None
        
        with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        documents = index_data.get("documents", [])
        
        # Simple keyword matching để lấy context
        stop_words = {'là', 'của', 'và', 'có', 'các', 'được', 'trong', 'để'}
        keywords = [w.lower() for w in query.split() if w.lower() not in stop_words and len(w) > 1]
        
        # Find top 2 matching docs
        candidate_docs = []
        for doc in documents:
            content = doc.get("content", "").lower()
            match_count = sum(1 for kw in keywords if kw in content)
            if match_count > 0:
                candidate_docs.append({
                    "file_name": doc.get("file_name", ""),
                    "content": doc.get("content", ""),
                    "match_count": match_count
                })
        
        candidate_docs.sort(key=lambda x: x["match_count"], reverse=True)
        top_docs = candidate_docs[:2]
        
        if not top_docs:
            print("❌ Không tìm thấy documents liên quan")
            return None
        
        # Build context
        context = "\n\n---\n\n".join([
            f"📄 {d['file_name']}:\n{d['content'][:2000]}" 
            for d in top_docs
        ])
        
        print(f"📚 Context từ {len(top_docs)} documents ({len(context):,} chars)")
        
        # Call Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        prompt = f"""Bạn là trợ lý AI trả lời câu hỏi dựa trên tài liệu.

📋 TÀI LIỆU THAM KHẢO:
{context}

❓ CÂU HỎI:
{query}

📝 YÊU CẦU:
- TRẢ LỜI TRỰC TIẾP dựa trên tài liệu
- Ngắn gọn, súc tích
- Tiếng Việt

🎯 TRẢ LỜI:"""

        print("🤖 Đang gọi Gemini...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.3
            )
        )
        
        if response and response.text:
            answer = response.text.strip()
            print(f"\n✅ GEMINI ANSWER:")
            print("-" * 40)
            print(answer)
            print("-" * 40)
            print(f"\n📄 Sources: {[d['file_name'] for d in top_docs]}")
            return answer
        else:
            print("❌ Gemini không trả về response")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 miniZ MCP - Knowledge Base Search Test")
    print("=" * 60)
    
    # Test 1: Check index
    if not test_basic_search():
        return
    
    # Test 2: Keyword search
    query = "nhóm nghiên cứu"  # Change this to test different queries
    results = test_keyword_search(query)
    
    # Test 3: Gemini answer
    if results:
        asyncio.run(test_gemini_answer(query))
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
