"""
Background tasks for real-time price updates
Pre-fetches data every 5 seconds to avoid slow API calls on page load
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict
import threading

logger = logging.getLogger(__name__)

# In-memory price cache (global for fast access)
_price_cache: Dict[str, dict] = {}
_cache_lock = threading.Lock()
_last_update = None

# Top assets to update (limited for performance and rate limits)
TOP_CRYPTO = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD", 
    "ADA-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "LINK-USD"
]

TOP_STOCKS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
    "JPM", "V", "JNJ", "WMT", "PG", "XOM"
]

TOP_FOREX = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"
]


def get_cached_price(symbol: str) -> dict | None:
    """Get price from in-memory cache"""
    with _cache_lock:
        return _price_cache.get(symbol.upper())


def get_all_cached_prices() -> Dict[str, dict]:
    """Get all cached prices"""
    with _cache_lock:
        return _price_cache.copy()


def update_price_cache(quotes: Dict[str, dict]):
    """Update price cache with new quotes"""
    with _cache_lock:
        for symbol, quote in quotes.items():
            if quote:
                _price_cache[symbol.upper()] = quote
        global _last_update
        _last_update = datetime.now(timezone.utc)


async def background_price_update_task():
    """
    Background task to update prices every 5 seconds
    Pre-fetches data to avoid slow API calls on page load
    PARALLELIZED - Updates crypto, stocks, and forex simultaneously
    
    Usage in main.py:
        @app.on_event("startup")
        async def startup():
            asyncio.create_task(background_price_update_task())
    """
    from app.core import data
    
    logger.info("Starting background price update task...")
    
    async def update_crypto():
        """Update crypto prices in parallel using thread pool"""
        logger.info("Updating crypto prices...")
        crypto_quotes = {}
        tasks = []
        
        for symbol in TOP_CRYPTO:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_crypto_quote(sym) if data.get_crypto_quote(sym) else None)
            )
            tasks.append(task)
        
        # Run all crypto fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    crypto_quotes[sym] = quote
        
        update_price_cache(crypto_quotes)
        logger.info(f"Updated {len(crypto_quotes)} crypto prices")
        return crypto_quotes
    
    async def update_stocks():
        """Update stock prices in parallel using thread pool"""
        logger.info("Updating stock prices...")
        stock_quotes = {}
        tasks = []
        
        for symbol in TOP_STOCKS:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_live_quote(sym) if data.get_live_quote(sym) else None)
            )
            tasks.append(task)
        
        # Run all stock fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    stock_quotes[sym] = quote
        
        update_price_cache(stock_quotes)
        logger.info(f"Updated {len(stock_quotes)} stock prices")
        return stock_quotes
    
    async def update_forex():
        """Update forex prices in parallel using thread pool"""
        logger.info("Updating forex prices...")
        forex_quotes = {}
        tasks = []
        
        for symbol in TOP_FOREX:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_live_quote(sym) if data.get_live_quote(sym) else None)
            )
            tasks.append(task)
        
        # Run all forex fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    forex_quotes[sym] = quote
        
        update_price_cache(forex_quotes)
        logger.info(f"Updated {len(forex_quotes)} forex prices")
        return forex_quotes
    
    while True:
        try:
            # PARALLELIZE ALL UPDATES - Run crypto, stocks, and forex simultaneously
            await asyncio.gather(
                update_crypto(),
                update_stocks(),
                update_forex()
            )
            
            logger.info(f"Total cached prices: {len(_price_cache)}")
            
            await asyncio.sleep(5)  # Update every 5 seconds
        
        except Exception as e:
            logger.error(f"Background task error: {e}")
            await asyncio.sleep(5)


def get_cache_status() -> dict:
    """Get cache statistics"""
    with _cache_lock:
        return {
            "total_cached": len(_price_cache),
            "last_update": _last_update.isoformat() if _last_update else None,
            "crypto_count": len([s for s in _price_cache if s.endswith("-USD")]),
            "stock_count": len([s for s in _price_cache if not s.endswith("-USD") and not s.endswith("=X")]),
            "forex_count": len([s for s in _price_cache if s.endswith("=X")])
        }
