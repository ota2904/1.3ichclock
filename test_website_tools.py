"""
Test Quick Website Access Tools
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from xiaozhi_final import open_youtube, open_facebook, open_google, open_tiktok, open_website

async def main():
    print("=" * 60)
    print("TEST 1: Open YouTube (homepage)")
    print("=" * 60)
    result = await open_youtube()
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 2: Open YouTube with search")
    print("=" * 60)
    result = await open_youtube("nhạc Việt Nam")
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 3: Open Facebook")
    print("=" * 60)
    result = await open_facebook()
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 4: Open Google (homepage)")
    print("=" * 60)
    result = await open_google()
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 5: Open Google with search")
    print("=" * 60)
    result = await open_google("AI programming")
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 6: Open TikTok")
    print("=" * 60)
    result = await open_tiktok()
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 7: Open custom website")
    print("=" * 60)
    result = await open_website("github.com")
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

    print("\n" + "=" * 60)
    print("TEST 8: Open custom website with https")
    print("=" * 60)
    result = await open_website("https://stackoverflow.com")
    print(f"✅ Result: {result['message']}")
    print(f"   URL: {result['url']}")

if __name__ == "__main__":
    asyncio.run(main())
