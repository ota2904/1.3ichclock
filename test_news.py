#!/usr/bin/env python3
"""
Test script for VnExpress news scraping tools
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import get_vnexpress_news, get_news_summary, search_news

async def test_get_news():
    """Test getting news from VnExpress"""
    print("=" * 60)
    print("TEST 1: Lấy tin tức mới nhất (home)")
    print("=" * 60)
    result = await get_vnexpress_news(category="home", max_articles=3)
    
    if result.get("success"):
        print(f"✅ {result['message']}")
        for i, article in enumerate(result["articles"], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Link: {article['link']}")
            print(f"   Mô tả: {article['description'][:100]}...")
    else:
        print(f"❌ Error: {result.get('error')}")

async def test_news_categories():
    """Test different news categories"""
    print("\n" + "=" * 60)
    print("TEST 2: Lấy tin từ các chủ đề khác nhau")
    print("=" * 60)
    
    categories = ["the-thao", "kinh-doanh", "giai-tri"]
    
    for cat in categories:
        print(f"\n📰 Category: {cat.upper()}")
        print("-" * 40)
        result = await get_vnexpress_news(category=cat, max_articles=2)
        
        if result.get("success"):
            for i, article in enumerate(result["articles"], 1):
                print(f"{i}. {article['title'][:60]}...")
        else:
            print(f"❌ Error: {result.get('error')}")

async def test_news_summary():
    """Test news summary"""
    print("\n" + "=" * 60)
    print("TEST 3: Tóm tắt tin tức")
    print("=" * 60)
    
    result = await get_news_summary(category="home")
    
    if result.get("success"):
        print(result["summary"])
    else:
        print(f"❌ Error: {result.get('error')}")

async def test_search_news():
    """Test news search"""
    print("\n" + "=" * 60)
    print("TEST 4: Tìm kiếm tin tức")
    print("=" * 60)
    
    keywords = ["bóng đá", "kinh tế", "công nghệ"]
    
    for keyword in keywords:
        print(f"\n🔍 Tìm kiếm: '{keyword}'")
        print("-" * 40)
        result = await search_news(keyword=keyword, max_results=3)
        
        if result.get("success"):
            print(f"✅ {result['message']}")
            for i, article in enumerate(result["articles"], 1):
                print(f"{i}. {article['title'][:60]}...")
        else:
            print(f"❌ Error: {result.get('error')}")

async def main():
    """Run all tests"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "VNEXPRESS NEWS TOOLS TEST" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    await test_get_news()
    await test_news_categories()
    await test_news_summary()
    await test_search_news()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
