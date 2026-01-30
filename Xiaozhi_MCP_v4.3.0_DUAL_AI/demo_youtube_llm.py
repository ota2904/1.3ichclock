"""
DEMO: YouTube Direct Video cho LLM
Test xem LLM có gọi đúng tool và video có được phát trực tiếp không
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🎬 DEMO: YOUTUBE DIRECT VIDEO - LLM INTEGRATION TEST")
print("=" * 70)
print()
print("Test cases mô phỏng user queries thật:")
print()

test_queries = [
    {
        "user_input": "mở youtube Sơn Tùng Chúng Ta Của Hiện Tại",
        "expected_tool": "open_youtube",
        "expected_mode": "direct_video",
        "description": "User muốn xem video cụ thể (6 từ)"
    },
    {
        "user_input": "mở youtube Taylor Swift Shake It Off",
        "expected_tool": "open_youtube",
        "expected_mode": "direct_video",
        "description": "User muốn xem video cụ thể (5 từ)"
    },
    {
        "user_input": "mở youtube nhạc buồn",
        "expected_tool": "open_youtube",
        "expected_mode": "search_page",
        "description": "User tìm kiếm chung (2 từ)"
    },
    {
        "user_input": "vào youtube",
        "expected_tool": "open_youtube",
        "expected_mode": "homepage",
        "description": "User chỉ muốn vào YouTube"
    }
]

print("📋 Danh sách test:")
for i, tc in enumerate(test_queries, 1):
    print(f"   {i}. '{tc['user_input']}' → {tc['expected_mode']}")
print()
print("=" * 70)
print()

# Test qua /api/smart_chat để test toàn bộ LLM flow
for i, test in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}/{len(test_queries)}: {test['description']}")
    print(f"{'='*70}")
    print(f"💬 User: \"{test['user_input']}\"")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/smart_chat",
            json={
                "query": test['user_input'],
                "model": "models/gemini-2.5-flash"  # LLM sẽ decide tool
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"🤖 LLM Response:")
            print(f"   Intent: {result.get('intent', 'N/A')}")
            print(f"   Tool used: {result.get('tool_called', 'N/A')}")
            
            # Check tool result nếu có
            if result.get('tool_result'):
                tool_res = result['tool_result']
                mode = tool_res.get('mode', 'unknown')
                url = tool_res.get('url', '')
                
                print(f"   Mode: {mode}")
                print(f"   URL: {url[:60]}...")
                
                if mode == "direct_video":
                    print(f"   Video: {tool_res.get('title', 'N/A')[:50]}...")
                    print(f"   ✅ PHÁT VIDEO TRỰC TIẾP!")
                elif mode == "search_page":
                    print(f"   ⚠️  Search page (đúng vì query ngắn)")
                elif mode == "homepage":
                    print(f"   ✅ Homepage (đúng)")
                
                # Verify expectations
                if mode == test['expected_mode']:
                    print(f"\n✅ PASS: Mode đúng như mong đợi ({mode})")
                else:
                    print(f"\n❌ FAIL: Expected {test['expected_mode']}, got {mode}")
            
            # Check response text
            response_text = result.get('response', '')
            print(f"\n💬 Bot reply: {response_text[:100]}...")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server không chạy - Cần: python xiaozhi_final.py")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print()
print("✅ open_youtube() giờ TỰ ĐỘNG phát video trực tiếp khi:")
print("   - Query cụ thể (>= 3 từ)")
print("   - Ví dụ: 'Sơn Tùng Chúng Ta Của Hiện Tại'")
print()
print("⚠️  Vẫn mở search page khi:")
print("   - Query ngắn (< 3 từ)")
print("   - Ví dụ: 'nhạc buồn'")
print()
print("💡 LLM description đã được update:")
print("   - open_youtube: Có note về auto-detect direct video")
print("   - search_youtube_video: Clarify khi nào dùng")
print()
print("🔧 Nếu vẫn không hoạt động:")
print("   1. Restart server: python xiaozhi_final.py")
print("   2. Xóa cache LLM conversation history")
print("   3. Test lại với query mới")
