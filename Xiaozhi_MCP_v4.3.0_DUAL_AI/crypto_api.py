"""
Crypto Price API Module
Real-time cryptocurrency prices from trusted sources
"""
import aiohttp
import asyncio
from typing import Dict, Optional


async def get_crypto_price(symbol: str = "bitcoin") -> Optional[Dict]:
    """
    Get real-time crypto price from CoinGecko API (free, no API key)
    
    Args:
        symbol: Crypto symbol (bitcoin, ethereum, etc.)
        
    Returns:
        {
            "symbol": "bitcoin",
            "price_usd": 86695.32,
            "price_change_24h": -2.5,
            "market_cap": 1730720000000,
            "volume_24h": 38490000000,
            "ath": 108353.47,
            "ath_date": "2024-12-17",
            "source": "CoinGecko",
            "timestamp": "2025-12-17T22:15:00"
        }
    """
    try:
        async with aiohttp.ClientSession() as session:
            # CoinGecko API (no key needed)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": symbol,
                "order": "market_cap_desc",
                "per_page": 1,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h"
            }
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                if not data:
                    return None
                
                coin = data[0]
                
                return {
                    "symbol": coin["id"],
                    "name": coin["name"],
                    "price_usd": coin["current_price"],
                    "price_change_24h": coin.get("price_change_percentage_24h", 0),
                    "market_cap": coin["market_cap"],
                    "volume_24h": coin["total_volume"],
                    "ath": coin["ath"],
                    "ath_date": coin["ath_date"][:10],
                    "source": "CoinGecko API",
                    "timestamp": coin["last_updated"]
                }
    except Exception as e:
        print(f"⚠️ [CryptoAPI] Error: {e}")
        return None


async def get_crypto_price_binance(symbol: str = "BTCUSDT") -> Optional[Dict]:
    """
    Fallback: Get price from Binance API
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT, etc.)
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Binance API
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                return {
                    "symbol": symbol,
                    "price_usd": float(data["lastPrice"]),
                    "price_change_24h": float(data["priceChangePercent"]),
                    "volume_24h": float(data["volume"]),
                    "source": "Binance API",
                    "timestamp": data["closeTime"]
                }
    except Exception as e:
        print(f"⚠️ [BinanceAPI] Error: {e}")
        return None


async def detect_crypto_query(query: str) -> Optional[str]:
    """
    Detect if query is about cryptocurrency price
    
    Returns:
        Crypto symbol if detected, None otherwise
    """
    query_lower = query.lower()
    
    crypto_map = {
        "bitcoin": "bitcoin",
        "btc": "bitcoin",
        "ethereum": "ethereum",
        "eth": "ethereum",
        "ripple": "ripple",
        "xrp": "ripple",
        "cardano": "cardano",
        "ada": "cardano",
        "dogecoin": "dogecoin",
        "doge": "dogecoin",
        "solana": "solana",
        "sol": "solana",
        "polkadot": "polkadot",
        "dot": "polkadot",
    }
    
    # Check if asking about price
    if any(word in query_lower for word in ["giá", "price", "cost", "bao nhiêu"]):
        # Find crypto symbol
        for keyword, symbol in crypto_map.items():
            if keyword in query_lower:
                return symbol
    
    return None


# Test
if __name__ == "__main__":
    async def test():
        print("🔍 Testing Crypto API...")
        
        # Test CoinGecko
        btc = await get_crypto_price("bitcoin")
        if btc:
            print(f"\n✅ CoinGecko:")
            print(f"   {btc['name']}: ${btc['price_usd']:,.2f}")
            print(f"   24h change: {btc['price_change_24h']:.2f}%")
            print(f"   ATH: ${btc['ath']:,.2f} on {btc['ath_date']}")
        
        # Test Binance
        btc_binance = await get_crypto_price_binance("BTCUSDT")
        if btc_binance:
            print(f"\n✅ Binance:")
            print(f"   Price: ${btc_binance['price_usd']:,.2f}")
            print(f"   24h change: {btc_binance['price_change_24h']:.2f}%")
        
        # Test detection
        queries = [
            "giá Bitcoin hiện nay",
            "Bitcoin price today",
            "tin tức công nghệ"
        ]
        print(f"\n🔍 Query Detection:")
        for q in queries:
            symbol = await detect_crypto_query(q)
            print(f"   '{q}' → {symbol}")
    
    asyncio.run(test())
