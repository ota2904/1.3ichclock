#!/usr/bin/env python3
"""
Test script for YouTube tools - Manual Testing Guide
Mở YouTube trong browser và test các controls
"""
import asyncio
import sys
import os
import webbrowser

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import open_youtube, control_youtube

async def test_youtube_workflow():
    """Test full YouTube workflow: open + control"""
    print("🎥 Testing YouTube Tools - Complete Workflow")
    print("=" * 60)
    
    # Test 1: Mở YouTube
    print("\n📋 TEST 1: Mở YouTube")
    print("-" * 60)
    result = await open_youtube(search_query="")
    print(f"✅ Open YouTube: {result}")
    
    # Wait for user to click on a video
    print("\n⏸️  MANUAL STEP: Hãy click vào một video trên YouTube...")
    print("   Nhấn Enter sau khi video bắt đầu phát...")
    input()
    
    # Test 2: Play/Pause
    print("\n📋 TEST 2: Play/Pause Video")
    print("-" * 60)
    result = await control_youtube("play_pause")
    print(f"✅ Result: {result}")
    await asyncio.sleep(2)
    
    # Test 3: Volume Up
    print("\n📋 TEST 3: Tăng âm lượng")
    print("-" * 60)
    for i in range(3):
        result = await control_youtube("volume_up")
        print(f"✅ Volume Up #{i+1}: {result.get('message', result)}")
        await asyncio.sleep(0.5)
    
    # Test 4: Volume Down
    print("\n📋 TEST 4: Giảm âm lượng")
    print("-" * 60)
    for i in range(3):
        result = await control_youtube("volume_down")
        print(f"✅ Volume Down #{i+1}: {result.get('message', result)}")
        await asyncio.sleep(0.5)
    
    # Test 5: Rewind
    print("\n📋 TEST 5: Lùi video 10 giây")
    print("-" * 60)
    result = await control_youtube("rewind_10")
    print(f"✅ Result: {result}")
    await asyncio.sleep(1)
    
    # Test 6: Forward
    print("\n📋 TEST 6: Tua video 10 giây")
    print("-" * 60)
    result = await control_youtube("forward_10")
    print(f"✅ Result: {result}")
    await asyncio.sleep(1)
    
    # Test 7: Mute Toggle
    print("\n📋 TEST 7: Bật/Tắt tiếng")
    print("-" * 60)
    result = await control_youtube("mute_toggle")
    print(f"✅ Mute: {result}")
    await asyncio.sleep(2)
    result = await control_youtube("mute_toggle")
    print(f"✅ Unmute: {result}")
    
    # Test 8: Rewind 5 seconds
    print("\n📋 TEST 8: Lùi video 5 giây")
    print("-" * 60)
    result = await control_youtube("rewind_5")
    print(f"✅ Result: {result}")
    await asyncio.sleep(1)
    
    # Test 9: Forward 5 seconds
    print("\n📋 TEST 9: Tua video 5 giây")
    print("-" * 60)
    result = await control_youtube("forward_5")
    print(f"✅ Result: {result}")
    await asyncio.sleep(1)
    
    # Test 10: Go to beginning
    print("\n📋 TEST 10: Quay về đầu video")
    print("-" * 60)
    result = await control_youtube("beginning")
    print(f"✅ Result: {result}")
    
    print("\n" + "=" * 60)
    print("🎉 Test workflow hoàn tất!")
    print("=" * 60)

async def test_youtube_search():
    """Test YouTube search"""
    print("\n🔍 Testing YouTube Search")
    print("=" * 60)
    
    search_queries = [
        "nhạc trẻ hay nhất",
        "lofi chill beats",
        "vietnamese music"
    ]
    
    for query in search_queries:
        print(f"\n🔎 Searching: '{query}'")
        result = await open_youtube(search_query=query)
        print(f"✅ Result: {result}")
        await asyncio.sleep(2)

async def main():
    """Main test function"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "YOUTUBE TOOLS TEST SUITE" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    
    print("\n📝 Chọn test mode:")
    print("1. Full Workflow Test (mở YouTube + controls)")
    print("2. Search Test (test tìm kiếm YouTube)")
    print("3. Quick Controls Test (test nhanh các phím)")
    
    choice = input("\nNhập lựa chọn (1/2/3): ").strip()
    
    if choice == "1":
        await test_youtube_workflow()
    elif choice == "2":
        await test_youtube_search()
    elif choice == "3":
        await quick_controls_test()
    else:
        print("❌ Lựa chọn không hợp lệ!")

async def quick_controls_test():
    """Quick test for controls only"""
    print("\n⚡ Quick Controls Test")
    print("=" * 60)
    print("⚠️  Đảm bảo YouTube đang mở và video đang phát!")
    print("   Nhấn Enter để bắt đầu test...")
    input()
    
    controls = [
        ("play_pause", "Play/Pause"),
        ("volume_up", "Tăng âm lượng"),
        ("volume_down", "Giảm âm lượng"),
        ("rewind_10", "Lùi 10s"),
        ("forward_10", "Tua 10s"),
        ("mute_toggle", "Bật/Tắt tiếng")
    ]
    
    for action, description in controls:
        print(f"\n🎬 {description}")
        result = await control_youtube(action)
        status = "✅" if result.get('success') else "❌"
        print(f"{status} {result.get('message', result)}")
        await asyncio.sleep(1.5)
    
    print("\n🎉 Quick test hoàn tất!")

if __name__ == "__main__":
    asyncio.run(main())
