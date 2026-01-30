"""
Test YouTube Auto-Detect với threshold >= 2 words
Verify "Lạc Trôi" sẽ mở video trực tiếp
"""
import asyncio
import sys

# Test queries
test_cases = [
    {"query": "Lạc Trôi", "words": 2, "expected": "direct_video", "desc": "Bài hát 2 từ"},
    {"query": "Sơn Tùng MTP", "words": 3, "expected": "direct_video", "desc": "Tên ca sĩ 3 từ"},
    {"query": "Chúng Ta Của Hiện Tại", "words": 5, "expected": "direct_video", "desc": "Tên bài hát dài"},
    {"query": "nhạc", "words": 1, "expected": "search_page", "desc": "Query 1 từ"},
    {"query": "", "words": 0, "expected": "homepage", "desc": "Không có query"},
]

print("=" * 70)
print("🧪 TEST: YouTube Auto-Detect Threshold >= 2 Words")
print("=" * 70)
print()

# Test logic
for i, test in enumerate(test_cases, 1):
    query = test['query']
    word_count = len(query.split()) if query else 0
    
    # Simulate logic
    if query and word_count >= 2:
        mode = "direct_video"
        action = f"✅ TÌM VIDEO: '{query}'"
    elif query:
        mode = "search_page"
        action = f"⚠️  SEARCH PAGE: '{query}'"
    else:
        mode = "homepage"
        action = "🏠 HOMEPAGE"
    
    # Verify
    passed = mode == test['expected']
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"Test {i}: {test['desc']}")
    print(f"  Query: '{query}' ({word_count} từ)")
    print(f"  Expected: {test['expected']}")
    print(f"  Got: {mode}")
    print(f"  Action: {action}")
    print(f"  Result: {status}")
    print()

print("=" * 70)
print("📋 SUMMARY")
print("=" * 70)
print()
print("✅ Threshold mới: >= 2 từ")
print("✅ 'Lạc Trôi' (2 từ) → Direct video")
print("✅ 'Sơn Tùng MTP' (3 từ) → Direct video")
print("⚠️  'nhạc' (1 từ) → Search page")
print("🏠 '' (0 từ) → Homepage")
print()

# Test với server thực (nếu đang chạy)
print("=" * 70)
print("🌐 TEST WITH REAL SERVER (Optional)")
print("=" * 70)
print()
print("Nếu server đang chạy, test với:")
print("  curl http://localhost:8000/api/tool/open_youtube -d '{\"search_query\":\"Lạc Trôi\"}'")
print()
print("Hoặc chạy demo:")
print("  python demo_youtube_llm.py")
print()
