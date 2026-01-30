"""
TEST SCRIPT: News Tools + Gemini Summarization
Tests 4 news tools with Gemini intelligent summarization
"""
import asyncio
import sys
from xiaozhi_final import (
    get_vnexpress_news, 
    get_news_summary,
    search_news,
    get_news_vietnam
)

async def test_news_tools():
    print("=" * 70)
    print("    NEWS TOOLS + GEMINI SUMMARIZATION TEST")
    print("=" * 70)
    
    # TEST 1: get_vnexpress_news (>3 articles → Gemini summary)
    print("\n📰 TEST 1: get_vnexpress_news (5 articles)")
    print("-" * 70)
    result1 = await get_vnexpress_news(category="home", max_articles=5)
    print(f"✅ Success: {result1['success']}")
    print(f"✅ Total: {result1['total']} articles")
    print(f"✅ Message: {result1['message']}")
    
    if 'gemini_summary' in result1:
        print("\n🌟 GEMINI SUMMARY:")
        print(result1['gemini_summary'])
    else:
        print("\n⚠️ No Gemini summary (expected if ≤3 articles)")
    
    print("\n📋 Raw Articles:")
    for i, article in enumerate(result1['articles'][:3], 1):
        print(f"{i}. {article['title'][:80]}...")
    
    # TEST 2: get_news_summary (≥5 → Gemini analysis)
    print("\n\n📊 TEST 2: get_news_summary (10 articles with analysis)")
    print("-" * 70)
    result2 = await get_news_summary(category="thoi-su")
    print(f"✅ Success: {result2['success']}")
    print(f"✅ Total: {result2['total']} articles")
    print(f"✅ Message: {result2['message']}")
    
    if 'gemini_analysis' in result2 and result2['gemini_analysis']:
        print("\n🌟 GEMINI ANALYSIS:")
        print(result2['gemini_analysis'])
    else:
        print("\n⚠️ No Gemini analysis (expected if <5 articles)")
    
    # TEST 3: search_news (>3 matches → Gemini summary)
    print("\n\n🔍 TEST 3: search_news (keyword='kinh tế')")
    print("-" * 70)
    result3 = await search_news(keyword="kinh tế", max_results=5)
    print(f"✅ Success: {result3['success']}")
    print(f"✅ Total: {result3['total']} matches")
    print(f"✅ Message: {result3['message']}")
    
    if 'gemini_summary' in result3:
        print("\n🌟 GEMINI SUMMARY:")
        print(result3['gemini_summary'])
    else:
        print("\n⚠️ No Gemini summary (expected if ≤3 matches)")
    
    # TEST 4: get_news_vietnam (5 news → Gemini summary)
    print("\n\n🇻🇳 TEST 4: get_news_vietnam (5 latest VN news)")
    print("-" * 70)
    result4 = await get_news_vietnam()
    print(f"✅ Success: {result4['success']}")
    
    if result4['success']:
        print(f"✅ Total: {len(result4.get('news', []))} news items")
        print(f"✅ Message preview: {result4['message'][:200]}...")
        
        if 'gemini_summary' in result4:
            print("\n🌟 GEMINI SUMMARY:")
            print(result4['gemini_summary'])
    
    # SUMMARY
    print("\n\n" + "=" * 70)
    print("    TEST COMPLETION SUMMARY")
    print("=" * 70)
    
    tests = [
        ("get_vnexpress_news", result1, 'gemini_summary'),
        ("get_news_summary", result2, 'gemini_analysis'),
        ("search_news", result3, 'gemini_summary'),
        ("get_news_vietnam", result4, 'gemini_summary')
    ]
    
    for tool_name, result, gemini_key in tests:
        has_gemini = gemini_key in result and result[gemini_key]
        status = "✅ PASSED" if result.get('success') else "❌ FAILED"
        gemini_status = "🌟 WITH GEMINI" if has_gemini else "📋 RAW ONLY"
        print(f"{status} {gemini_status:15} - {tool_name}")
    
    print("\n✅ ALL TESTS COMPLETED!")
    print("\n💡 KEY FEATURES:")
    print("   - Gemini summarizes when >3 articles")
    print("   - Intelligent analysis for news trends")
    print("   - Focused summaries for search results")
    print("   - Vietnamese language support")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_news_tools())
