"""
Test các tình huống phát nhạc khác nhau
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from xiaozhi_final import play_music, list_music

async def test_all_scenarios():
    print("\n" + "="*60)
    print("🎵 TEST CÁC TÌNH HUỐNG PHÁT NHẠC")
    print("="*60)
    
    # 1. List nhạc để lấy tên file thực
    print("\n1️⃣ Lấy danh sách nhạc...")
    result = await list_music()
    if not result.get("success"):
        print(f"❌ Không thể list nhạc: {result.get('error')}")
        return
    
    music_files = result.get("files", [])
    if not music_files:
        print("⚠️ Không có nhạc nào để test")
        return
    
    first_file = music_files[0]
    filename = first_file["filename"]
    filepath = first_file["path"]
    
    print(f"   📀 File test: {filename}")
    print(f"   📂 Path: {filepath}")
    
    # 2. Test với tên file chính xác
    print(f"\n2️⃣ Test với tên file chính xác: '{filename}'")
    result = await play_music(filename)
    print(f"   Result: {result}")
    if result.get("success"):
        print("   ✅ PASS")
        await asyncio.sleep(1)
    else:
        print(f"   ❌ FAIL: {result.get('error')}")
    
    # 3. Test với path đầy đủ
    print(f"\n3️⃣ Test với path đầy đủ: '{filepath}'")
    result = await play_music(filepath)
    print(f"   Result: {result}")
    if result.get("success"):
        print("   ✅ PASS")
        await asyncio.sleep(1)
    else:
        print(f"   ❌ FAIL: {result.get('error')}")
    
    # 4. Test với lowercase
    print(f"\n4️⃣ Test với lowercase: '{filename.lower()}'")
    result = await play_music(filename.lower())
    print(f"   Result: {result}")
    if result.get("success"):
        print("   ✅ PASS")
        await asyncio.sleep(1)
    else:
        print(f"   ❌ FAIL: {result.get('error')}")
    
    # 5. Test với partial name
    partial = filename[:10] if len(filename) > 10 else filename[:5]
    print(f"\n5️⃣ Test với partial name: '{partial}'")
    result = await play_music(partial)
    print(f"   Result: {result}")
    if result.get("success"):
        print("   ✅ PASS")
        await asyncio.sleep(1)
    else:
        print(f"   ❌ FAIL: {result.get('error')}")
    
    # 6. Test với file không tồn tại
    print(f"\n6️⃣ Test với file không tồn tại: 'notexist.mp3'")
    result = await play_music("notexist.mp3")
    print(f"   Result: {result}")
    if not result.get("success"):
        print("   ✅ PASS (đúng là phải fail)")
        if "available_files" in result:
            print(f"   📋 Gợi ý files: {result['available_files']}")
    else:
        print(f"   ❌ FAIL: Phải báo lỗi chứ không phải success")
    
    print("\n" + "="*60)
    print("✅ TEST HOÀN TẤT")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(test_all_scenarios())
    except KeyboardInterrupt:
        print("\n⚠️ Đã hủy test")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
