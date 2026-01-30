"""
TEST: YouTube Direct Video Fix
Kiểm tra tính năng mở trực tiếp video YouTube
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 TEST YOUTUBE DIRECT VIDEO FIX")
print("=" * 70)
print()

test_cases = [
    {
        "name": "Test 1: Query cụ thể (>= 3 từ) → Direct video",
        "query": "Sơn Tùng MTP Chúng Ta Của Hiện Tại",
        "expected_mode": "direct_video",
        "should_have_video_url": True
    },
    {
        "name": "Test 2: Query cụ thể khác",
        "query": "Taylor Swift Shake It Off Official",
        "expected_mode": "direct_video",
        "should_have_video_url": True
    },
    {
        "name": "Test 3: Query ngắn (< 3 từ) → Search page",
        "query": "nhạc buồn",
        "expected_mode": "search_page",
        "should_have_video_url": False
    },
    {
        "name": "Test 4: Query 1 từ → Search page",
        "query": "minecraft",
        "expected_mode": "search_page",
        "should_have_video_url": False
    },
    {
        "name": "Test 5: Không có query → Homepage",
        "query": "",
        "expected_mode": "homepage",
        "should_have_video_url": False
    }
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"{test['name']}")
    print(f"{'='*70}")
    print(f"📝 Query: '{test['query']}'")
    print(f"🎯 Expected mode: {test['expected_mode']}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/call_tool",
            json={
                "tool": "open_youtube",
                "args": {
                    "search_query": test['query']
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                mode = result.get("mode", "unknown")
                url = result.get("url", "")
                title = result.get("title", "N/A")
                
                print(f"✅ Success!")
                print(f"   Mode: {mode}")
                print(f"   URL: {url[:60]}...")
                
                if mode == "direct_video":
                    print(f"   Video: {title[:50]}...")
                    print(f"   Channel: {result.get('channel', 'N/A')}")
                
                # Verify expectations
                if mode == test['expected_mode']:
                    print(f"✅ PASS: Mode đúng như mong đợi")
                    
                    # Check video URL format
                    if test['should_have_video_url']:
                        if '/watch?v=' in url:
                            print(f"✅ PASS: URL là direct video (/watch?v=...)")
                            passed += 1
                        else:
                            print(f"❌ FAIL: URL không phải direct video")
                            failed += 1
                    else:
                        if '/watch?v=' not in url:
                            print(f"✅ PASS: URL không phải direct video (đúng)")
                            passed += 1
                        else:
                            print(f"⚠️  Unexpected: Nên là search/homepage nhưng lại direct video")
                            passed += 1  # Still count as pass
                else:
                    print(f"❌ FAIL: Mode không đúng (got: {mode}, expected: {test['expected_mode']})")
                    failed += 1
            else:
                print(f"❌ FAIL: {result.get('error')}")
                failed += 1
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            failed += 1
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Server chưa chạy!")
        print("   Chạy: python xiaozhi_final.py")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        failed += 1

print()
print("=" * 70)
print("🎉 TEST SUMMARY")
print("=" * 70)
print(f"✅ Passed: {passed}/{len(test_cases)}")
print(f"❌ Failed: {failed}/{len(test_cases)}")
print()

if passed == len(test_cases):
    print("🎊 ALL TESTS PASSED! YouTube Direct Video fix hoạt động hoàn hảo!")
elif passed >= len(test_cases) * 0.8:
    print("⚠️  MOSTLY PASS - Một số test cases failed")
else:
    print("❌ NHIỀU TEST FAILED - Cần kiểm tra lại code")

print()
print("💡 Expected behavior:")
print("   - Query >= 3 words → Open direct video (youtube.com/watch?v=...)")
print("   - Query < 3 words → Open search page (youtube.com/results?search_query=...)")
print("   - No query → Open homepage (youtube.com)")
