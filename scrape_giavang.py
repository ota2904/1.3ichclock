import requests
from bs4 import BeautifulSoup
import re

# Test scraping gold prices from giavang.org
try:
    print("🔍 Scraping gold prices from giavang.org...")
    response = requests.get('https://giavang.org/', timeout=15, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for gold price tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")

        gold_data = []

        for i, table in enumerate(tables):
            print(f"\n--- Table {i+1} ---")
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    # Get text from columns
                    col_texts = [col.get_text(strip=True) for col in cols]
                    print(f"Row: {col_texts}")

                    # Look for gold type and prices
                    if len(col_texts) >= 3:
                        gold_type = col_texts[0]
                        buy_price = col_texts[1]
                        sell_price = col_texts[2]

                        # Check if this looks like gold data
                        if ('vàng' in gold_type.lower() or 'sjc' in gold_type.lower() or 'nhẫn' in gold_type.lower()) and buy_price and sell_price:
                            # Clean prices
                            buy_clean = re.sub(r'[^\d]', '', buy_price)
                            sell_clean = re.sub(r'[^\d]', '', sell_price)

                            if buy_clean and sell_clean:
                                # Format with dots
                                buy_formatted = f"{int(buy_clean):,}".replace(',', '.')
                                sell_formatted = f"{int(sell_clean):,}".replace(',', '.')

                                gold_data.append({
                                    "type": gold_type,
                                    "buy": buy_formatted,
                                    "sell": sell_formatted
                                })
                                print(f"✅ Found: {gold_type} - Buy: {buy_formatted}, Sell: {sell_formatted}")

        print(f"\n📊 Total gold types found: {len(gold_data)}")

        if gold_data:
            print("\n💰 GOLD PRICES:")
            for item in gold_data:
                print(f"📊 {item['type']}")
                print(f"   Mua: {item['buy']} VNĐ | Bán: {item['sell']} VNĐ")
                print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()