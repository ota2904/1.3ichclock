#!/usr/bin/env python3
"""
Test Script - Music Library
Kiểm tra tính năng quản lý nhạc
"""

import asyncio
import sys
sys.path.insert(0, '.')

async def test_music_library():
    """Test music library features"""
    print("=" * 60)
    print("🎵 TEST MUSIC LIBRARY - MCP Music Player")
    print("=" * 60)
    
    try:
        from xiaozhi_final import list_music, play_music, stop_music, search_music
        
        # Test 1: Liệt kê tất cả nhạc
        print("\n1️⃣ Liệt kê tất cả nhạc trong music_library...")
        result = await list_music()
        if result['success']:
            print(f"   ✅ {result['message']}")
            print(f"   📂 Thư mục: {result['library_path']}")
            if result['files']:
                print(f"   🎵 Danh sách nhạc:")
                for idx, file in enumerate(result['files'][:5], 1):
                    print(f"      {idx}. {file['filename']} ({file['size_mb']} MB)")
                if result['count'] > 5:
                    print(f"      ... và {result['count'] - 5} bài khác")
            else:
                print(f"   ℹ️  Chưa có nhạc. Hãy thêm file vào thư mục music_library!")
        else:
            print(f"   ❌ Lỗi: {result['error']}")
        
        # Test 2: Tìm kiếm nhạc
        print("\n2️⃣ Tìm kiếm nhạc (keyword: 'song')...")
        result = await search_music("song")
        if result['success']:
            print(f"   ✅ {result['message']}")
            if result['files']:
                for file in result['files'][:3]:
                    print(f"      🎵 {file['filename']}")
        else:
            print(f"   ❌ Lỗi: {result['error']}")
        
        # Test 3: Liệt kê nhạc trong subfolder
        print("\n3️⃣ Liệt kê nhạc trong subfolder 'Pop'...")
        result = await list_music("Pop")
        if result['success']:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ Lỗi: {result['error']}")
        
        print("\n" + "=" * 60)
        print("✅ TEST HOÀN THÀNH!")
        print("=" * 60)
        
        print("\n📊 TÍNH NĂNG:")
        print("   • list_music(): Liệt kê tất cả nhạc")
        print("   • play_music(filename): Phát nhạc")
        print("   • stop_music(): Dừng phát nhạc")
        print("   • search_music(keyword): Tìm kiếm nhạc")
        
        print("\n📝 HƯỚNG DẪN:")
        print("   1. Thêm file nhạc vào thư mục music_library/")
        print("   2. Từ MCP gọi list_music() để xem danh sách")
        print("   3. Gọi play_music('tên_file.mp3') để phát")
        print("   4. Gọi stop_music() để dừng")
        
        print("\n🎯 READY FOR MCP/XIAOZHI!")
        
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 Starting Music Library Tests...\n")
    asyncio.run(test_music_library())
