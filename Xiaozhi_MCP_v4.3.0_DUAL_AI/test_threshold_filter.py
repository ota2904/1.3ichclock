"""
Test cải tiến: Threshold filtering cho Knowledge Base
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import get_knowledge_context

async def test_threshold_filtering():
    """Test với query có từ phổ biến để thấy threshold filtering hoạt động"""
    
    print("\n" + "="*70)
    print("🧪 TEST THRESHOLD FILTERING")
    print("="*70)
    
    # Test case: Query có từ phổ biến như "nhân", "sinh"
    # Sẽ match nhiều documents nhưng chỉ 1 document có điểm CAO
    result = await get_knowledge_context(
        query="Muôn Kiếp Nhân Sinh",
        max_chars=10000,
        use_gemini_summary=True
    )
    
    print("\n📊 RESULT:")
    print(f"   Success: {result.get('success')}")
    print(f"   Total documents: {result.get('total_documents')}")
    print(f"   Documents included: {result.get('documents_included')}")
    print(f"   Context length: {result.get('context_length'):,} chars")
    print(f"   Keywords: {result.get('keywords_used')}")
    
    context = result.get('context', '')
    
    # Đếm số lần xuất hiện file names trong context
    files_in_context = []
    if '_muon-kiep-nhan-sinh-tap-1.pdf' in context:
        files_in_context.append('_muon-kiep-nhan-sinh-tap-1.pdf')
    if 'kiến thức b.rtf' in context:
        files_in_context.append('kiến thức b.rtf')
    if 'kiến thức c.docx' in context:
        files_in_context.append('kiến thức c.docx')
    if 'testLLM.docx' in context:
        files_in_context.append('testLLM.docx')
    
    print(f"\n📄 Files in context: {len(files_in_context)}")
    for f in files_in_context:
        print(f"   - {f}")
    
    # Validation
    print("\n✅ VALIDATION:")
    if len(files_in_context) == 1 and files_in_context[0] == '_muon-kiep-nhan-sinh-tap-1.pdf':
        print("   ✅ PERFECT! Chỉ có file 'Muôn Kiếp Nhân Sinh', không có noise")
    elif len(files_in_context) > 1:
        print(f"   ⚠️ WARNING: Có {len(files_in_context)} files, bao gồm cả files KHÔNG LIÊN QUAN!")
        print("   ❌ Threshold filtering KHÔNG hoạt động hoặc chưa được áp dụng")
    else:
        print("   ❌ ERROR: Không tìm thấy file nào")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_threshold_filtering())
