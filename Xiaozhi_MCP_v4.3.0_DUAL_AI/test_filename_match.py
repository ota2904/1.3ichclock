"""Test filename match scoring"""
import asyncio
import sys
sys.path.insert(0, '.')
from xiaozhi_final import get_knowledge_context

async def test():
    # Test 1: Muôn Kiếp Nhân Sinh
    print('='*60)
    print('TEST: muon kiep nhan sinh')
    result = await get_knowledge_context('muôn kiếp nhân sinh', max_chars=3000)
    print(f"Success: {result.get('success')}")
    print(f"Docs: {result.get('documents_included')}")
    context = result.get('context', '')
    if 'muon-kiep' in context.lower() or 'kiếp' in context.lower():
        print('✅ OK: Found Muon Kiep')
    else:
        print('❌ WRONG: Did not find Muon Kiep')
        print(f"Context: {context[:300]}")
    
    # Test 2: Le Trung Khoa  
    print()
    print('='*60)
    print('TEST: Le Trung Khoa')
    result = await get_knowledge_context('Lê Trung Khoa', max_chars=3000)
    print(f"Success: {result.get('success')}")
    print(f"Docs: {result.get('documents_included')}")
    context = result.get('context', '')
    if 'lê trung khoa' in context.lower():
        print('✅ OK: Found Le Trung Khoa')
    else:
        print('❌ WRONG')

if __name__ == "__main__":
    asyncio.run(test())
