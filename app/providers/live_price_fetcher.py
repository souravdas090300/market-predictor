"""
Working Live Price Fetcher
Actually calls APIs and stores real prices in database
Fixes the $0.0000 issue
"""

import httpx
import asyncio
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CRYPTO PRICES (CoinGecko) - ACTUAL WORKING IMPLEMENTATION
# ============================================================================

class CoinGeckoLivePriceFetcher:
    """Fetch real crypto prices from CoinGecko"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Map symbols to CoinGecko IDs
    CRYPTO_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "SOL": "solana",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "ARB": "arbitrum",
        "OP": "optimism",
        "LDO": "lido-dao",
        "UNI": "uniswap",
        "AAVE": "aave",
        "CURVE": "curve-dao-token",
        "MKR": "maker",
        "COMP": "compound-coin",
        "SNX": "synthetix-network-token",
        # Add more as needed
    }
    
    @staticmethod
    async def fetch_price(symbol: str) -> Optional[Dict]:
        """
        Fetch single crypto price
        Returns: {price, change_24h, high_24h, low_24h, volume_24h, market_cap, ...}
        """
        crypto_id = CoinGeckoLivePriceFetcher.CRYPTO_ID_MAP.get(symbol.upper())
        if not crypto_id:
            logger.warning(f"Unknown crypto symbol: {symbol}")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CoinGeckoLivePriceFetcher.BASE_URL}/simple/price",
                    params={
                        "ids": crypto_id,
                        "vs_currencies": "usd",
                        "include_market_cap": "true",
                        "include_24hr_vol": "true",
                        "include_24hr_change": "true",
                        "include_high_low_24h": "true"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                if crypto_id not in data:
                    logger.error(f"No data returned for {symbol}")
                    return None
                
                price_data = data[crypto_id]
                
                return {
                    "symbol": symbol.upper(),
                    "current_price": float(price_data.get("usd", 0)),
                    "change_24h": float(price_data.get("usd_24h_change", 0)),
                    "high_24h": float(price_data.get("usd_24h_high", 0)),
                    "low_24h": float(price_data.get("usd_24h_low", 0)),
                    "volume_24h": float(price_data.get("usd_24h_vol", 0)),
                    "market_cap": float(price_data.get("usd_market_cap", 0)),
                    "source": "coingecko",
                    "timestamp": datetime.utcnow()
                }
        
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {e}")
            return None
    
    @staticmethod
    async def fetch_multiple(symbols: List[str]) -> Dict[str, Dict]:
        """Fetch multiple crypto prices at once"""
        tasks = [CoinGeckoLivePriceFetcher.fetch_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            result["symbol"]: result 
            for result in results 
            if result is not None
        }


# ============================================================================
# STOCK PRICES (Yahoo Finance) - ACTUAL WORKING IMPLEMENTATION
# ============================================================================

class YahooFinanceLivePriceFetcher:
    """Fetch real stock prices from Yahoo Finance (yfinance)"""
    
    @staticmethod
    def fetch_price(symbol: str) -> Optional[Dict]:
        """
        Fetch single stock price
        Returns: {price, change_24h, high_24h, low_24h, volume_24h, market_cap, ...}
        """
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            if not info or "currentPrice" not in info:
                logger.warning(f"No data found for stock: {symbol}")
                return None
            
            current_price = float(info.get("currentPrice", 0))
            previous_close = float(info.get("previousClose", current_price))
            change_24h = current_price - previous_close
            change_percent = (change_24h / previous_close * 100) if previous_close != 0 else 0
            
            return {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "change_24h": change_24h,
                "change_percent_24h": change_percent,
                "high_24h": float(info.get("dayHigh", 0)),
                "low_24h": float(info.get("dayLow", 0)),
                "volume_24h": float(info.get("volume", 0)),
                "market_cap": float(info.get("marketCap", 0)),
                "bid": float(info.get("bid", 0)),
                "ask": float(info.get("ask", 0)),
                "source": "yfinance",
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None
    
    @staticmethod
    def fetch_multiple(symbols: List[str]) -> Dict[str, Dict]:
        """Fetch multiple stock prices"""
        results = {}
        for symbol in symbols:
            result = YahooFinanceLivePriceFetcher.fetch_price(symbol)
            if result:
                results[result["symbol"]] = result
        return results


# ============================================================================
# FOREX PRICES (Twelve Data) - ACTUAL WORKING IMPLEMENTATION
# ============================================================================

class TwelveDataLivePriceFetcher:
    """Fetch real forex prices from Twelve Data API"""
    
    BASE_URL = "https://api.twelvedata.com/price"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def fetch_price(self, symbol: str) -> Optional[Dict]:
        """
        Fetch single forex price
        Symbol format: EURUSD, GBPUSD, etc.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "symbol": symbol.upper(),
                        "apikey": self.api_key
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                if "price" not in data:
                    logger.error(f"No price data for {symbol}: {data}")
                    return None
                
                return {
                    "symbol": symbol.upper(),
                    "current_price": float(data["price"]),
                    "bid": float(data.get("bid", data["price"])),
                    "ask": float(data.get("ask", data["price"])),
                    "change_24h": float(data.get("change", 0)),
                    "change_percent_24h": float(data.get("percent_change", 0)),
                    "high_24h": float(data.get("high", data["price"])),
                    "low_24h": float(data.get("low", data["price"])),
                    "volume_24h": float(data.get("volume", 0)),
                    "source": "twelvedata",
                    "timestamp": datetime.utcnow()
                }
        
        except Exception as e:
            logger.error(f"Error fetching forex price for {symbol}: {e}")
            return None
    
    async def fetch_multiple(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch multiple forex prices"""
        tasks = [self.fetch_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            result["symbol"]: result 
            for result in results 
            if result is not None
        }


# ============================================================================
# DATABASE UPDATE FUNCTION
# ============================================================================

async def update_live_prices_in_db(db_session, prices_dict: Dict):
    """
    Store fetched prices in LivePrice table
    This FIXES the $0.0000 issue
    """
    from app.database_models import LivePrice
    
    for symbol, price_data in prices_dict.items():
        try:
            # Find or create LivePrice entry
            live_price = db_session.query(LivePrice).filter_by(symbol=symbol).first()
            
            if not live_price:
                live_price = LivePrice(symbol=symbol)
                db_session.add(live_price)
            
            # Update all fields
            live_price.current_price = price_data.get("current_price", 0)
            live_price.change_24h = price_data.get("change_24h", 0)
            live_price.change_percent_24h = price_data.get("change_percent_24h", 
                                                           price_data.get("change_24h", 0))
            live_price.high_24h = price_data.get("high_24h", 0)
            live_price.low_24h = price_data.get("low_24h", 0)
            live_price.volume_24h = price_data.get("volume_24h", 0)
            live_price.market_cap = price_data.get("market_cap", 0)
            live_price.bid = price_data.get("bid")
            live_price.ask = price_data.get("ask")
            live_price.source = price_data.get("source", "unknown")
            live_price.updated_at = datetime.utcnow()
            
            logger.info(f"Updated {symbol}: ${live_price.current_price}")
        
        except Exception as e:
            logger.error(f"Error updating {symbol} in DB: {e}")
    
    try:
        db_session.commit()
        logger.info(f"✅ Committed {len(prices_dict)} price updates to database")
    except Exception as e:
        logger.error(f"Error committing to database: {e}")
        db_session.rollback()


# ============================================================================
# BACKGROUND TASK - RUNS ON STARTUP
# ============================================================================

async def background_price_update_task(db_session, twelve_data_key: str = None):
    """
    Continuously update live prices in database
    Call this from main.py startup event
    """
    
    # Top assets to update
    CRYPTO_SYMBOLS = [
        "BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "AVAX", 
        "LINK", "DOT", "MATIC", "ARB", "OP", "LDO", "UNI"
    ]
    
    STOCK_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B",
        "JNJ", "V", "WMT", "PG", "XOM", "KO", "JPM"
    ]
    
    FOREX_SYMBOLS = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"
    ]
    
    logger.info("🚀 Starting background price update task...")
    
    update_interval = 5  # Update every 5 seconds
    
    while True:
        try:
            all_prices = {}
            
            # Fetch crypto prices
            logger.info("📊 Fetching crypto prices from CoinGecko...")
            crypto_prices = await CoinGeckoLivePriceFetcher.fetch_multiple(CRYPTO_SYMBOLS)
            all_prices.update(crypto_prices)
            logger.info(f"✅ Got {len(crypto_prices)} crypto prices")
            
            # Fetch stock prices
            logger.info("📊 Fetching stock prices from Yahoo Finance...")
            stock_prices = YahooFinanceLivePriceFetcher.fetch_multiple(STOCK_SYMBOLS)
            all_prices.update(stock_prices)
            logger.info(f"✅ Got {len(stock_prices)} stock prices")
            
            # Fetch forex prices (if API key available)
            if twelve_data_key:
                logger.info("📊 Fetching forex prices from Twelve Data...")
                forex_fetcher = TwelveDataLivePriceFetcher(twelve_data_key)
                try:
                    forex_prices = await forex_fetcher.fetch_multiple(FOREX_SYMBOLS)
                    all_prices.update(forex_prices)
                    logger.info(f"✅ Got {len(forex_prices)} forex prices")
                except Exception as e:
                    logger.warning(f"⚠️ Forex update failed: {e}")
            
            # Update database
            if all_prices:
                await update_live_prices_in_db(db_session, all_prices)
                logger.info(f"💾 Updated {len(all_prices)} prices in database")
            
            # Wait before next update
            await asyncio.sleep(update_interval)
        
        except Exception as e:
            logger.error(f"❌ Error in background task: {e}")
            await asyncio.sleep(update_interval)


# ============================================================================
# TEST FUNCTION
# ============================================================================

async def test_price_fetchers():
    """Test all price fetchers"""
    
    print("\n" + "="*60)
    print("Testing Price Fetchers")
    print("="*60)
    
    # Test crypto
    print("\n📊 Testing CoinGecko (Crypto)...")
    btc = await CoinGeckoLivePriceFetcher.fetch_price("BTC")
    if btc:
        print(f"✅ BTC: ${btc['current_price']:.2f} ({btc['change_percent_24h']:+.2f}%)")
    else:
        print("❌ Failed to fetch BTC")
    
    eth = await CoinGeckoLivePriceFetcher.fetch_price("ETH")
    if eth:
        print(f"✅ ETH: ${eth['current_price']:.2f} ({eth['change_percent_24h']:+.2f}%)")
    else:
        print("❌ Failed to fetch ETH")
    
    # Test stocks
    print("\n📊 Testing Yahoo Finance (Stocks)...")
    aapl = YahooFinanceLivePriceFetcher.fetch_price("AAPL")
    if aapl:
        print(f"✅ AAPL: ${aapl['current_price']:.2f} ({aapl['change_percent_24h']:+.2f}%)")
    else:
        print("❌ Failed to fetch AAPL")
    
    msft = YahooFinanceLivePriceFetcher.fetch_price("MSFT")
    if msft:
        print(f"✅ MSFT: ${msft['current_price']:.2f} ({msft['change_percent_24h']:+.2f}%)")
    else:
        print("❌ Failed to fetch MSFT")
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test the fetchers
    asyncio.run(test_price_fetchers())
