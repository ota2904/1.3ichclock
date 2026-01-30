"""
Test YouTube với server thực - Threshold >= 2 words
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 TEST: YouTube Auto-Detect với Server Thực")
print("=" * 70)
print()

# Wait for server
print("⏳ Checking server status...")
for i in range(5):
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print("✅ Server is ready!")
        break
    except:
        if i < 4:
            print(f"   Waiting... ({i+1}/5)")
            time.sleep(2)
        else:
            print("❌ Server not responding. Please start: python xiaozhi_final.py")
            exit(1)

print()
print("=" * 70)
print("🎬 TEST CASES")
print("=" * 70)
print()

test_cases = [
    {
        "query": "Lạc Trôi",
        "words": 2,
        "expected_mode": "direct_video",
        "desc": "Bài hát Sơn Tùng MTP (2 từ)"
    },
    {
        "query": "Sơn Tùng MTP",
        "words": 3,
        "expected_mode": "direct_video",
        "desc": "Tên ca sĩ (3 từ)"
    },
    {
        "query": "nhạc",
        "words": 1,
        "expected_mode": "search_page",
        "desc": "Query chung (1 từ)"
    }
]

results = []

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}/{len(test_cases)}: {test['desc']}")
    print(f"{'='*70}")
    print(f"💬 Query: \"{test['query']}\" ({test['words']} từ)")
    print(f"🎯 Expected: {test['expected_mode']}")
    print()
    
    try:
        # Call API
        response = requests.post(
            f"{BASE_URL}/api/tool/open_youtube",
            json={"search_query": test['query']},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            mode = result.get('mode', 'unknown')
            success = result.get('success', False)
            url = result.get('url', '')
            
            print(f"📡 Response:")
            print(f"   Success: {success}")
            print(f"   Mode: {mode}")
            print(f"   URL: {url[:60]}..." if len(url) > 60 else f"   URL: {url}")
            
            if mode == "direct_video":
                print(f"   Title: {result.get('title', 'N/A')[:50]}...")
                print(f"   Channel: {result.get('channel', 'N/A')[:40]}...")
            
            # Verify
            passed = mode == test['expected_mode']
            if passed:
                print(f"\n✅ PASS: Mode đúng ({mode})")
                results.append({"test": i, "status": "PASS"})
            else:
                print(f"\n❌ FAIL: Expected {test['expected_mode']}, got {mode}")
                results.append({"test": i, "status": "FAIL"})
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            results.append({"test": i, "status": "ERROR"})
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        results.append({"test": i, "status": "ERROR"})

# Summary
print()
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print()

pass_count = sum(1 for r in results if r['status'] == 'PASS')
fail_count = sum(1 for r in results if r['status'] == 'FAIL')
error_count = sum(1 for r in results if r['status'] == 'ERROR')

print(f"Total: {len(results)} tests")
print(f"✅ Pass: {pass_count}")
print(f"❌ Fail: {fail_count}")
print(f"⚠️  Error: {error_count}")
print()

if pass_count == len(results):
    print("🎉 ALL TESTS PASSED!")
    print()
    print("✅ Threshold >= 2 words hoạt động đúng:")
    print("   - 'Lạc Trôi' (2 từ) → Video trực tiếp")
    print("   - 'Sơn Tùng MTP' (3 từ) → Video trực tiếp")
    print("   - 'nhạc' (1 từ) → Search page")
else:
    print("⚠️  Some tests failed. Please check logs above.")

print()
