#!/usr/bin/env python3
"""
🧠 SMART CONVERSATION ANALYZER - TEST SUITE
Test tất cả các chức năng của Smart Analyzer
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

# Test cases
TEST_CASES = [
    # === MUSIC CONTROLS ===
    {"query": "bài tiếp theo đi", "expected_tool": "music_next", "category": "Music"},
    {"query": "quay lại bài trước", "expected_tool": "music_previous", "category": "Music"},
    {"query": "tạm dừng nhạc", "expected_tool": "pause_music", "category": "Music"},
    {"query": "tiếp tục phát nhạc", "expected_tool": "resume_music", "category": "Music"},
    {"query": "tắt nhạc đi", "expected_tool": "stop_music", "category": "Music"},
    {"query": "phát bài đa nghi", "expected_tool": "play_music", "category": "Music"},
    {"query": "mở nhạc lên", "expected_tool": "play_music", "category": "Music"},
    
    # === VOLUME CONTROLS ===
    {"query": "tăng âm lượng lên", "expected_tool": "volume_up", "category": "Volume"},
    {"query": "giảm âm lượng xuống", "expected_tool": "volume_down", "category": "Volume"},
    {"query": "tắt tiếng đi", "expected_tool": "mute_volume", "category": "Volume"},
    {"query": "chỉnh âm lượng 50", "expected_tool": "set_volume", "category": "Volume"},
    
    # === APPLICATIONS ===
    {"query": "mở chrome lên", "expected_tool": "open_application", "category": "Apps"},
    {"query": "khởi động notepad", "expected_tool": "open_application", "category": "Apps"},
    {"query": "tắt chrome đi", "expected_tool": "kill_process", "category": "Apps"},
    
    # === SYSTEM ===
    {"query": "chụp màn hình cho tôi", "expected_tool": "take_screenshot", "category": "System"},
    {"query": "bây giờ là mấy giờ", "expected_tool": "get_current_time", "category": "System"},
    {"query": "xem tài nguyên hệ thống", "expected_tool": "get_system_resources", "category": "System"},
    
    # === FILES ===
    {"query": "tạo file test.txt", "expected_tool": "create_file", "category": "Files"},
    {"query": "đọc file readme.md", "expected_tool": "read_file", "category": "Files"},
    {"query": "liệt kê files trong thư mục", "expected_tool": "list_files", "category": "Files"},
    
    # === CALCULATOR ===
    {"query": "tính 5 + 3", "expected_tool": "calculator", "category": "Calc"},
    {"query": "5 nhân 10 bằng bao nhiêu", "expected_tool": "calculator", "category": "Calc"},
    
    # === EDGE CASES ===
    {"query": "hôm nay thời tiết thế nào", "expected_tool": None, "category": "No Tool"},
    {"query": "bạn tên gì", "expected_tool": None, "category": "No Tool"},
]


async def test_smart_analyze(session, test_case, use_ai=False):
    """Test một case với Smart Analyzer"""
    try:
        async with session.post(
            f"{BASE_URL}/api/smart_analyze",
            json={
                "user_query": test_case["query"],
                "auto_execute": False,  # Không thực thi thật
                "use_ai": use_ai
            }
        ) as response:
            result = await response.json()
            
            if not result.get("success"):
                return {
                    "query": test_case["query"],
                    "expected": test_case["expected_tool"],
                    "actual": None,
                    "passed": False,
                    "error": result.get("error")
                }
            
            analysis = result.get("analysis", {})
            actual_tool = analysis.get("tool_name")
            confidence = analysis.get("confidence", 0)
            
            passed = actual_tool == test_case["expected_tool"]
            
            return {
                "query": test_case["query"],
                "expected": test_case["expected_tool"],
                "actual": actual_tool,
                "confidence": confidence,
                "passed": passed,
                "reasoning": analysis.get("reasoning", "")
            }
            
    except Exception as e:
        return {
            "query": test_case["query"],
            "expected": test_case["expected_tool"],
            "actual": None,
            "passed": False,
            "error": str(e)
        }


async def run_all_tests():
    """Chạy tất cả test cases"""
    print("\n" + "="*70)
    print("🧠 SMART CONVERSATION ANALYZER - TEST SUITE")
    print("="*70 + "\n")
    
    async with aiohttp.ClientSession() as session:
        # Test với rule-based
        print("📋 Testing with RULE-BASED analysis...\n")
        
        results = []
        categories = {}
        
        for test in TEST_CASES:
            result = await test_smart_analyze(session, test, use_ai=False)
            results.append(result)
            
            # Group by category
            cat = test["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0}
            
            if result["passed"]:
                categories[cat]["passed"] += 1
                status = "✅"
            else:
                categories[cat]["failed"] += 1
                status = "❌"
            
            print(f"  {status} [{cat}] '{result['query']}'")
            print(f"      Expected: {result['expected']} | Got: {result['actual']} (conf: {result.get('confidence', 0):.2f})")
        
        # Summary
        print("\n" + "-"*70)
        print("📊 SUMMARY BY CATEGORY:")
        print("-"*70)
        
        total_passed = 0
        total_failed = 0
        
        for cat, stats in categories.items():
            passed = stats["passed"]
            failed = stats["failed"]
            total = passed + failed
            total_passed += passed
            total_failed += failed
            
            pct = (passed / total * 100) if total > 0 else 0
            print(f"  {cat}: {passed}/{total} ({pct:.0f}%)")
        
        print("-"*70)
        overall_pct = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"  OVERALL: {total_passed}/{total_passed + total_failed} ({overall_pct:.1f}%)")
        print("="*70 + "\n")
        
        return results


async def test_conversation_flow():
    """Test conversation history flow"""
    print("\n" + "="*70)
    print("📜 TESTING CONVERSATION FLOW")
    print("="*70 + "\n")
    
    async with aiohttp.ClientSession() as session:
        # 1. Clear history
        async with session.post(f"{BASE_URL}/api/conversation/clear") as resp:
            result = await resp.json()
            print(f"1. Clear history: {'✅' if result.get('success') else '❌'}")
        
        # 2. Add messages
        messages = [
            {"role": "user", "content": "phát nhạc đi"},
            {"role": "assistant", "content": "Đang phát nhạc...", "tool_called": "play_music"},
            {"role": "user", "content": "bài tiếp theo"},
        ]
        
        for msg in messages:
            async with session.post(f"{BASE_URL}/api/conversation/add", json=msg) as resp:
                result = await resp.json()
                print(f"2. Add '{msg['content'][:20]}...': {'✅' if result.get('success') else '❌'}")
        
        # 3. Get history
        async with session.get(f"{BASE_URL}/api/conversation/history") as resp:
            result = await resp.json()
            history = result.get("history", [])
            print(f"3. Get history: {len(history)} messages")
            for h in history:
                print(f"   - {h['role']}: {h['content'][:30]}...")
        
        # 4. Analyze with history
        async with session.post(f"{BASE_URL}/api/smart_analyze", json={
            "user_query": "bài trước",
            "auto_execute": False
        }) as resp:
            result = await resp.json()
            analysis = result.get("analysis", {})
            print(f"4. Analyze 'bài trước': {analysis.get('tool_name')} (conf: {analysis.get('confidence', 0):.2f})")
        
        print("\n" + "="*70 + "\n")


async def main():
    """Main test function"""
    try:
        # Check server
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/endpoints") as resp:
                if resp.status != 200:
                    print("❌ Server không hoạt động! Hãy chạy: python xiaozhi_final.py")
                    return
        
        # Run tests
        await run_all_tests()
        await test_conversation_flow()
        
        print("✅ All tests completed!")
        
    except aiohttp.ClientConnectorError:
        print("❌ Không thể kết nối server!")
        print("   Hãy chạy: python xiaozhi_final.py")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
