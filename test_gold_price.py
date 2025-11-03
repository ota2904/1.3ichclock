#!/usr/bin/env python3
"""
Test script for gold price tool
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import get_gold_price

async def test_gold_price():
    """Test getting gold prices from BNews"""
    print("=" * 60)
    print("TEST: Lấy giá vàng từ BNews RSS")
    print("=" * 60)
    
    result = await get_gold_price()
    
    if result.get("success"):
        print(f"\n✅ {result['message']}")
        print(f"📊 Nguồn: {result['source']}")
        print(f"📈 Tổng số loại vàng: {result['total']}")
        
        print("\n" + result["summary"])
        
        print("\n📋 Chi tiết từng loại:")
        print("-" * 60)
        for i, item in enumerate(result["gold_prices"], 1):
            gold_type = item.get('type', item.get('title', 'N/A'))
            buy = item.get('buy', item.get('buy_price', 'N/A'))
            sell = item.get('sell', item.get('sell_price', 'N/A'))
            
            print(f"\n{i}. {gold_type}")
            print(f"   Mua vào: {buy}")
            print(f"   Bán ra: {sell}")
    else:
        print(f"❌ Error: {result.get('error')}")

async def main():
    """Run test"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "GOLD PRICE TEST" + " " * 25 + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    await test_gold_price()
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
