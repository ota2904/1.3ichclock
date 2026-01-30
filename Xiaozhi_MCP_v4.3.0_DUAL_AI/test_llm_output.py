"""Test output của get_knowledge_context để xem LLM nhận được gì"""
import asyncio
import sys
sys.path.insert(0, '.')
from xiaozhi_final import get_knowledge_context

async def test():
    # Test case 1: Hỏi về Lê Trung Khoa
    print("="*80)
    print("TEST 1: Lê Trung Khoa là ai")
    print("="*80)
    query = "Lê Trung Khoa là ai"
    result = await get_knowledge_context(query=query, max_chars=5000)
    print(f"✅ Success: {result.get('success')}")
    print(f"📄 Included docs: {result.get('documents_included')}")
    print(f"📏 Context length: {result.get('context_length')}")
    print(f"Context preview: {result.get('context', '')[:300]}...")
    
    # Test case 2: Hỏi về Nguyễn Công Huy
    print("\n" + "="*80)
    print("TEST 2: Nguyễn Công Huy là ai")
    print("="*80)
    query = "Nguyễn Công Huy"
    result = await get_knowledge_context(query=query, max_chars=5000)
    print(f"✅ Success: {result.get('success')}")
    print(f"📄 Included docs: {result.get('documents_included')}")
    print(f"📏 Context length: {result.get('context_length')}")
    print(f"Context preview: {result.get('context', '')[:300]}...")
    
    # Test case 3: Query chung (JLPT)
    print("\n" + "="*80)
    print("TEST 3: JLPT N3")
    print("="*80)
    query = "JLPT N3"
    result = await get_knowledge_context(query=query, max_chars=5000)
    print(f"✅ Success: {result.get('success')}")
    print(f"📄 Included docs: {result.get('documents_included')}")
    print(f"📏 Context length: {result.get('context_length')}")
    print(f"Context preview: {result.get('context', '')[:200]}...")

if __name__ == "__main__":
    asyncio.run(test())
