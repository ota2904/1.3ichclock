"""
Test search_music function với auto-play
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from xiaozhi_final import search_music, play_music, list_music

async def main():
    print("=" * 60)
    print("TEST 1: Search 'love' và auto-play")
    print("=" * 60)
    result = await search_music(keyword="love", auto_play=True)
    print(f"✅ Result: {result['message']}")
    print(f"   Files found: {result['count']}")
    print(f"   Auto-played: {result.get('auto_played')}")
    if result.get('play_result'):
        print(f"   Play result: {result['play_result'].get('message')}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Search 'đa nghi' và auto-play")
    print("=" * 60)
    result = await search_music(keyword="đa nghi", auto_play=True)
    print(f"✅ Result: {result['message']}")
    print(f"   Files found: {result['count']}")
    
    print("\n" + "=" * 60)
    print("TEST 3: Search 'tình' không auto-play")
    print("=" * 60)
    result = await search_music(keyword="tình", auto_play=False)
    print(f"✅ Result: {result['message']}")
    print(f"   Files found: {result['count']}")
    print(f"   Auto-played: {result.get('auto_played')}")
    
    print("\n" + "=" * 60)
    print("TEST 4: Play bài cụ thể 'đa nghi' (partial match)")
    print("=" * 60)
    result = await play_music(filename="đa nghi")
    print(f"✅ Result: {result.get('message')}")
    
    print("\n" + "=" * 60)
    print("TEST 5: Play bài cụ thể 'in love' (case-insensitive)")
    print("=" * 60)
    result = await play_music(filename="in love")
    print(f"✅ Result: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(main())
