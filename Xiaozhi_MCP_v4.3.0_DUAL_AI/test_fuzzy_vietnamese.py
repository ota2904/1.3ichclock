"""
Test fuzzy matching với tiếng Việt có dấu
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from xiaozhi_final import VLCMusicPlayer

async def test_vietnamese_fuzzy():
    print("=" * 70)
    print("🧪 TEST FUZZY MATCHING WITH VIETNAMESE DIACRITICS")
    print("=" * 70)
    
    # Initialize player
    player = VLCMusicPlayer()
    
    # Refresh song cache from music_library
    music_folder = Path(__file__).parent / "music_library"
    
    if not music_folder.exists():
        print(f"❌ Music folder not found: {music_folder}")
        return
    
    print(f"\n📂 Scanning music folder: {music_folder}")
    player.refresh_song_cache(music_folder)
    
    print(f"✅ Song cache loaded: {len(player._song_cache)} songs\n")
    
    # List all songs in cache
    print("📋 Songs in cache:")
    for i, (song_name, song_path) in enumerate(player._song_cache.items(), 1):
        print(f"   {i}. '{song_name}' -> {Path(song_path).name}")
    
    print("\n" + "=" * 70)
    print("🔍 TEST 1: Query 'Đa Nghi' -> Should find 'ĐA NGHI.mp3'")
    print("=" * 70)
    
    query1 = "Đa Nghi"
    best_match1, score1 = player.fuzzy_match_song(query1, threshold=0.3)
    
    if best_match1:
        print(f"\n✅ TEST 1 PASSED")
        print(f"   Query: '{query1}'")
        print(f"   Match: {Path(best_match1).name}")
        print(f"   Score: {score1:.2f}")
    else:
        print(f"\n❌ TEST 1 FAILED")
        print(f"   Query: '{query1}'")
        print(f"   Result: No match found")
    
    print("\n" + "=" * 70)
    print("🔍 TEST 2: Query 'da nghi' (no diacritics) -> Should still find 'ĐA NGHI.mp3'")
    print("=" * 70)
    
    query2 = "da nghi"
    best_match2, score2 = player.fuzzy_match_song(query2, threshold=0.3)
    
    if best_match2:
        print(f"\n✅ TEST 2 PASSED")
        print(f"   Query: '{query2}'")
        print(f"   Match: {Path(best_match2).name}")
        print(f"   Score: {score2:.2f}")
    else:
        print(f"\n❌ TEST 2 FAILED")
        print(f"   Query: '{query2}'")
        print(f"   Result: No match found")
    
    print("\n" + "=" * 70)
    print("🔍 TEST 3: Query 'phát bài Em' -> Should find 'Em.mp3'")
    print("=" * 70)
    
    query3 = "phát bài Em"
    best_match3, score3 = player.fuzzy_match_song(query3, threshold=0.3)
    
    if best_match3:
        print(f"\n✅ TEST 3 PASSED")
        print(f"   Query: '{query3}'")
        print(f"   Match: {Path(best_match3).name}")
        print(f"   Score: {score3:.2f}")
    else:
        print(f"\n❌ TEST 3 FAILED")
        print(f"   Query: '{query3}'")
        print(f"   Result: No match found")
    
    print("\n" + "=" * 70)
    print("🔍 TEST 4: Query 'chang phai tinh dau' (no diacritics) -> Should find 'chẳng phải tình đầu...'")
    print("=" * 70)
    
    query4 = "chang phai tinh dau"
    best_match4, score4 = player.fuzzy_match_song(query4, threshold=0.3)
    
    if best_match4:
        print(f"\n✅ TEST 4 PASSED")
        print(f"   Query: '{query4}'")
        print(f"   Match: {Path(best_match4).name}")
        print(f"   Score: {score4:.2f}")
    else:
        print(f"\n❌ TEST 4 FAILED")
        print(f"   Query: '{query4}'")
        print(f"   Result: No match found")
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    tests = [
        (best_match1, "Đa Nghi", query1),
        (best_match2, "da nghi", query2),
        (best_match3, "Em", query3),
        (best_match4, "chẳng phải tình đầu", query4)
    ]
    
    passed = sum(1 for match, _, _ in tests if match is not None)
    total = len(tests)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Vietnamese fuzzy matching is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Review the implementation.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_vietnamese_fuzzy())
