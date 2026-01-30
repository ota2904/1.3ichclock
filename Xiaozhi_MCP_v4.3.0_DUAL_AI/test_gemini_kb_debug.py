"""
Test Advanced: Debug Gemini KB Context Error
Tìm và fix lỗi khi Gemini tóm tắt không đúng hoặc không trả về kết quả
"""

import asyncio
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from xiaozhi_final import (
        get_knowledge_context, 
        KNOWLEDGE_INDEX_FILE,
        GEMINI_API_KEY,
        GEMINI_AVAILABLE
    )
    print("✅ Import thành công")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_gemini_summarization_direct():
    """Test Gemini summarization trực tiếp"""
    
    print("\n" + "="*70)
    print("🧪 TEST GEMINI SUMMARIZATION TRỰC TIẾP")
    print("="*70)
    
    if not GEMINI_AVAILABLE:
        print("❌ Gemini không khả dụng!")
        print(f"   GEMINI_API_KEY exists: {bool(GEMINI_API_KEY)}")
        return
    
    print(f"✅ Gemini khả dụng")
    print(f"   API Key: ...{GEMINI_API_KEY[-10:]}")
    
    # Test content dài cần tóm tắt
    test_content = """
Lê Trung Khoa là người bị Bộ Công an ra quyết định truy nã ngày 5/12/2024 
về tội "Lừa đảo chiếm đoạt tài sản" theo Điều 174 Bộ luật Hình sự. 
Ông ta sinh năm 1985, quê quán tại Hà Nội. 
Các thông tin chi tiết:
- Họ và tên: Lê Trung Khoa
- Năm sinh: 1985
- Quê quán: Hà Nội
- Tội danh: Lừa đảo chiếm đoạt tài sản
- Ngày ra quyết định truy nã: 5/12/2024
- Điều luật: Điều 174 Bộ luật Hình sự
""" * 10  # Nhân 10 để có nội dung dài
    
    test_cases = [
        {
            "name": "Test với query cụ thể",
            "content": test_content,
            "query": "Lê Trung Khoa",
            "max_tokens": 500
        },
        {
            "name": "Test không có query (tóm tắt chung)",
            "content": test_content,
            "query": "",
            "max_tokens": 500
        },
        {
            "name": "Test với content ngắn (không cần tóm tắt)",
            "content": "Nguyễn Công Huy sinh ngày 29/04/1993",
            "query": "",
            "max_tokens": 500
        }
    ]
    
    for test in test_cases:
        print("\n" + "-"*70)
        print(f"🔬 {test['name']}")
        print(f"   Content length: {len(test['content'])} chars")
        print(f"   Query: '{test['query']}'")
        print("-"*70)
        
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Tạo prompt
            if test['query']:
                summary_prompt = f"""Tóm tắt nội dung sau đây NGẮN GỌN (tối đa 300 từ), tập trung vào thông tin liên quan đến câu hỏi: "{test['query']}"

Nội dung:
{test['content'][:3000]}

Yêu cầu:
- Chỉ trích xuất thông tin TRỰC TIẾP liên quan đến câu hỏi
- Bỏ qua phần không liên quan
- Ngắn gọn, súc tích
- Giữ nguyên các con số, tên riêng quan trọng

Tóm tắt:"""
            else:
                summary_prompt = f"""Tóm tắt NỘI DUNG CHÍNH của tài liệu sau (tối đa 400 từ):

Nội dung:
{test['content'][:4000]}

Yêu cầu:
- Tóm tắt các thông tin QUAN TRỌNG NHẤT
- Giữ nguyên cấu trúc chính
- Giữ các con số, tên riêng, thuật ngữ kỹ thuật
- Ngắn gọn nhưng đầy đủ ý chính

Tóm tắt:"""
            
            print("📤 Gửi request đến Gemini...")
            
            # Gọi Gemini
            response = model.generate_content(
                summary_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=test['max_tokens']
                )
            )
            
            if response and response.text:
                print("✅ Gemini trả về kết quả:")
                print(f"   Response length: {len(response.text)} chars")
                print(f"   Response preview:")
                print("-" * 60)
                print(response.text[:500])
                print("-" * 60)
            else:
                print("❌ Gemini không trả về text!")
                print(f"   Response object: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"   Prompt feedback: {response.prompt_feedback}")
                if hasattr(response, 'candidates'):
                    print(f"   Candidates: {response.candidates}")
                    
        except Exception as e:
            print(f"❌ LỖI: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)


async def test_edge_cases():
    """Test các trường hợp đặc biệt"""
    
    print("\n" + "="*70)
    print("🧪 TEST CÁC TRƯỜNG HỢP ĐẶC BIỆT")
    print("="*70)
    
    test_cases = [
        {
            "name": "Query với ký tự đặc biệt",
            "query": "Lê Trung Khoa @#$%",
            "max_chars": 10000,
            "use_gemini_summary": True
        },
        {
            "name": "Query rất dài",
            "query": "Lê Trung Khoa " * 100,
            "max_chars": 10000,
            "use_gemini_summary": True
        },
        {
            "name": "Max chars rất nhỏ",
            "query": "",
            "max_chars": 100,
            "use_gemini_summary": True
        },
        {
            "name": "Max chars rất lớn",
            "query": "",
            "max_chars": 1000000,
            "use_gemini_summary": True
        }
    ]
    
    for test in test_cases:
        print("\n" + "-"*70)
        print(f"🔬 {test['name']}")
        print("-"*70)
        
        try:
            result = await get_knowledge_context(
                query=test['query'],
                max_chars=test['max_chars'],
                use_gemini_summary=test['use_gemini_summary']
            )
            
            if result.get("success"):
                print("✅ SUCCESS")
                print(f"   Documents: {result.get('documents_included', 0)}")
                print(f"   Context length: {result.get('context_length', 0):,} chars")
            else:
                print("❌ FAILED")
                print(f"   Error: {result.get('error', '')}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)


async def main():
    """Chạy tất cả tests"""
    
    print("\n" + "="*80)
    print(" "*20 + "DEBUG GEMINI KB CONTEXT")
    print("="*80)
    
    # Test 1: Gemini summarization trực tiếp
    await test_gemini_summarization_direct()
    
    # Test 2: Edge cases
    await test_edge_cases()
    
    print("\n" + "="*80)
    print(" "*25 + "HOÀN THÀNH TẤT CẢ TESTS")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
