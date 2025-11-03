#!/usr/bin/env python3
"""
Test script for YouTube control tools
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import control_youtube

async def test_youtube_controls():
    """Test YouTube control functions"""
    print("🎥 Testing YouTube Control Tools")
    print("=" * 50)

    # Test actions
    test_actions = [
        "play_pause",
        "rewind_10",
        "forward_10",
        "volume_up",
        "volume_down",
        "mute_toggle"
    ]

    for action in test_actions:
        print(f"\n🧪 Testing action: {action}")
        try:
            result = await control_youtube(action)
            print(f"✅ Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Wait a bit between tests
        await asyncio.sleep(1)

    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_youtube_controls())