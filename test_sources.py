import requests
from bs4 import BeautifulSoup
import re

# Test different gold price sources
sources = [
    {'name': 'giavang.org', 'url': 'https://giavang.org/'},
    {'name': 'pnj.com.vn', 'url': 'https://www.pnj.com.vn/blog/gia-vang/'},
    {'name': 'sjc.com.vn', 'url': 'https://sjc.com.vn/xml/tygiavang.xml'},
]

for source in sources:
    try:
        print(f'\n🔍 Testing {source["name"]}...')
        response = requests.get(source['url'], timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f'✅ Status: {response.status_code}')

        if source['name'] == 'sjc.com.vn':
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            print(f'📊 Found {len(items)} gold items')
            if items:
                for i, item in enumerate(items[:3]):
                    gold_type = item.get('@type', 'N/A')
                    buy = item.get('@buy', 'N/A')
                    sell = item.get('@sell', 'N/A')
                    print(f'  {i+1}. {gold_type}: Buy {buy}, Sell {sell}')
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Look for price patterns
            prices = re.findall(r'\d{1,3}(?:\.\d{3})*', response.text)
            print(f'📊 Found {len(prices)} price patterns')
            if prices:
                print(f'💰 Sample prices: {prices[:10]}')

    except Exception as e:
        print(f'❌ Error: {e}')