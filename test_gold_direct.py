import asyncio
import sys
import os
sys.path.append('.')

from xiaozhi_final import get_gold_price

async def test_direct():
    print('🧪 Testing get_gold_price function directly...')
    result = await get_gold_price()

    if result['success']:
        print(f'✅ Success: {result["message"]}')
        print(f'📊 Source: {result["source"]}')
        print(f'📈 Total prices: {result["total"]}')

        print('\n💰 Current Gold Prices:')
        for i, price in enumerate(result['gold_prices'][:5]):
            print(f'{i+1}. {price["type"]}: Buy {price["buy"]} | Sell {price["sell"]}')

        if result['total'] > 5:
            print(f'... and {result["total"] - 5} more prices')
    else:
        print(f'❌ Error: {result.get("error", "Unknown error")}')

if __name__ == "__main__":
    asyncio.run(test_direct())