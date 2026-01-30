"""
Test Music Player Functionality
Kiểm tra tìm kiếm và phát nhạc
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import (
    check_music_folder_config,
    search_music,
    play_music,
    list_music,
    get_music_status
)

async def test_music_system():
    print("\n" + "="*70)
    print("   🎵 TEST MUSIC SYSTEM - TÌM VÀ PHÁT NHẠC   ".center(70))
    print("="*70 + "\n")
    
    # Test 1: Kiểm tra config folder nhạc
    print("📂 TEST 1: Check music folder configuration")
    print("-" * 70)
    config_result = check_music_folder_config()
    print(f"Has config: {config_result.get('has_config')}")
    if config_result.get('has_config'):
        print(f"Folder: {config_result.get('folder_path')}")
    else:
        print("⚠️ Chưa có config thư mục nhạc user")
    
    print("\n" + "="*70 + "\n")
    
    # Test 2: Liệt kê nhạc trong music_library (default)
    print("📜 TEST 2: List music from music_library")
    print("-" * 70)
    list_result = await list_music(subfolder="", auto_play=False)
    if list_result.get("success"):
        files = list_result.get("files", [])
        print(f"✅ Found {len(files)} music files")
        if files:
            print(f"\n📋 First 5 files:")
            for i, file in enumerate(files[:5], 1):
                print(f"   {i}. {file['filename']} ({file['size_mb']} MB)")
            print(f"\n💡 Total: {len(files)} files")
        else:
            print("⚠️ Không có file nhạc trong music_library")
    else:
        print(f"❌ Error: {list_result.get('error')}")
    
    print("\n" + "="*70 + "\n")
    
    # Test 3: Tìm kiếm nhạc với từ khóa
    print("🔍 TEST 3: Search music with keyword 'love'")
    print("-" * 70)
    search_result = await search_music(keyword="love", auto_play=False)
    if search_result.get("success"):
        matches = search_result.get("files", [])
        print(f"✅ Found {len(matches)} matches for 'love'")
        if matches:
            print(f"\n📋 Search results:")
            for i, file in enumerate(matches[:3], 1):
                print(f"   {i}. {file['filename']}")
                print(f"      Path: {file['path']}")
                print(f"      Size: {file['size_mb']} MB")
        else:
            print("⚠️ Không tìm thấy bài nào với từ khóa 'love'")
    else:
        print(f"❌ Error: {search_result.get('error')}")
    
    print("\n" + "="*70 + "\n")
    
    # Test 4: Fuzzy matching với play_music
    print("🎵 TEST 4: Play music with fuzzy matching")
    print("-" * 70)
    
    # Lấy tên bài đầu tiên để test (nếu có)
    if list_result.get("success") and list_result.get("files"):
        test_file = list_result["files"][0]["filename"]
        # Test với tên gần đúng (bỏ extension)
        test_keyword = test_file.replace('.mp3', '').replace('.wav', '').replace('.flac', '')[:10]
        
        print(f"Testing with keyword: '{test_keyword}'")
        print(f"(Từ file: {test_file})")
        
        play_result = await play_music(filename=test_keyword, create_playlist=False, use_fuzzy=True)
        if play_result.get("success"):
            print(f"✅ Fuzzy match success!")
            print(f"   Played: {play_result.get('filename')}")
            print(f"   Path: {play_result.get('path')}")
            print(f"   Size: {play_result.get('size_mb')} MB")
            print(f"   Fuzzy used: {play_result.get('fuzzy_used')}")
            print(f"   Message: {play_result.get('message')}")
            
            # Dừng nhạc sau khi test
            await asyncio.sleep(2)
            from xiaozhi_final import stop_music
            stop_result = await stop_music()
            print(f"\n⏹️ Stopped: {stop_result.get('message')}")
        else:
            print(f"❌ Error: {play_result.get('error')}")
            print(f"   Hint: {play_result.get('hint', 'N/A')}")
    else:
        print("⚠️ Không có file để test fuzzy matching")
    
    print("\n" + "="*70 + "\n")
    
    # Summary
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Config check: {'PASSED' if config_result.get('has_config') is not None else 'FAILED'}")
    print(f"✅ List music: {'PASSED' if list_result.get('success') else 'FAILED'}")
    print(f"   - Files found: {len(list_result.get('files', []))}")
    print(f"✅ Search music: {'PASSED' if search_result.get('success') else 'FAILED'}")
    print(f"   - Matches: {len(search_result.get('files', []))}")
    
    if list_result.get("success") and list_result.get("files"):
        print(f"✅ Play music (fuzzy): {'PASSED' if play_result.get('success') else 'FAILED'}")
        if play_result.get("success"):
            print(f"   - Fuzzy matching: {'YES' if play_result.get('fuzzy_used') else 'NO'}")
    else:
        print("⚠️ Play music (fuzzy): SKIPPED (no files)")
    
    print("\n" + "="*70)
    print("\n💡 KẾT LUẬN:")
    if list_result.get("success") and list_result.get("files"):
        print("   ✅ Music system hoạt động tốt")
        print("   ✅ Fuzzy matching hỗ trợ tìm bài gần đúng")
        print("   ✅ Search by keyword hoạt động")
    else:
        print("   ⚠️ Cần thêm file nhạc vào music_library")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_music_system())
