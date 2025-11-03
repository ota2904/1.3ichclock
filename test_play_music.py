"""
Test phát nhạc qua MCP
"""
import asyncio
import sys
from pathlib import Path

# Import từ xiaozhi_final.py
sys.path.insert(0, str(Path(__file__).parent))
from xiaozhi_final import play_music, list_music, stop_music

async def test_play():
    print("\n" + "="*60)
    print("🎵 TEST PHÁT NHẠC QUA MCP")
    print("="*60)
    
    # 1. Liệt kê nhạc có sẵn
    print("\n1️⃣ Kiểm tra danh sách nhạc...")
    result = await list_music()
    if result.get("success"):
        music_list = result.get("music_files", [])
        print(f"   ✅ Có {len(music_list)} bài hát")
        if music_list:
            first_song = music_list[0]["filename"]
            print(f"   📀 Bài đầu tiên: {first_song}")
            
            # 2. Test phát nhạc
            print(f"\n2️⃣ Test phát nhạc: {first_song}")
            play_result = await play_music(first_song)
            
            if play_result.get("success"):
                print(f"   ✅ {play_result.get('message')}")
                print(f"   📂 Path: {play_result.get('path')}")
                print(f"   💾 Size: {play_result.get('size_mb')} MB")
                
                # Đợi 3 giây rồi dừng
                print("\n   ⏳ Đợi 3 giây...")
                await asyncio.sleep(3)
                
                # 3. Test dừng nhạc
                print("\n3️⃣ Test dừng nhạc...")
                stop_result = await stop_music()
                if stop_result.get("success"):
                    print(f"   ✅ {stop_result.get('message')}")
                else:
                    print(f"   ❌ Lỗi: {stop_result.get('error')}")
            else:
                print(f"   ❌ Lỗi phát nhạc: {play_result.get('error')}")
        else:
            print("   ⚠️ Không có nhạc nào trong thư viện")
            print("   💡 Hãy thêm file .mp3/.wav vào music_library/")
    else:
        print(f"   ❌ Lỗi: {result.get('error')}")
    
    print("\n" + "="*60)
    print("✅ TEST HOÀN TẤT!")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(test_play())
    except KeyboardInterrupt:
        print("\n⚠️ Đã hủy test")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
