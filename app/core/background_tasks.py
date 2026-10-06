"""
Background tasks for real-time price updates
Smart on-demand fetching with intelligent caching
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
import threading

logger = logging.getLogger(__name__)

# In-memory price cache with timestamps
_price_cache: Dict[str, dict] = {}
_cache_timestamps: Dict[str, datetime] = {}
_cache_lock = threading.Lock()
_cache_ttl = 300  # Cache for 5 minutes (reduced API calls)

# Fetching state to prevent duplicate requests
_fetching: Dict[str, asyncio.Task] = {}
_fetch_lock = threading.Lock()


def get_cached_price(symbol: str) -> Optional[dict]:
    """Get price from cache if available and not expired"""
    with _cache_lock:
        symbol = symbol.upper()
        if symbol in _price_cache:
            timestamp = _cache_timestamps.get(symbol)
            if timestamp and (datetime.now(timezone.utc) - timestamp).total_seconds() < _cache_ttl:
                return _price_cache[symbol]
    return None


def update_price_cache(quotes: Dict[str, dict]):
    """Update price cache with new quotes"""
    with _cache_lock:
        now = datetime.now(timezone.utc)
        for symbol, quote in quotes.items():
            if quote:
                _price_cache[symbol.upper()] = quote
                _cache_timestamps[symbol.upper()] = now


def get_all_cached_prices() -> Dict[str, dict]:
    """Get all cached prices"""
    with _cache_lock:
        # Return only non-expired prices
        now = datetime.now(timezone.utc)
        return {
            k: v for k, v in _price_cache.items()
            if (now - _cache_timestamps.get(k, now)).total_seconds() < _cache_ttl
        }


async def fetch_price(symbol: str) -> Optional[dict]:
    """
    Fetch price for a single symbol with intelligent caching
    Returns cached data if available and fresh, otherwise fetches fresh data
    """
    symbol = symbol.upper()
    
    # Check cache first
    cached = get_cached_price(symbol)
    if cached:
        return cached
    
    # Check if already fetching this symbol
    with _fetch_lock:
        if symbol in _fetching:
            # Wait for existing fetch to complete
            try:
                return await _fetching[symbol]
            except:
                del _fetching[symbol]
    
    # Start new fetch
    from app.core import data
    
    async def _fetch():
        try:
            quote = data.get_live_quote(symbol)
            if quote:
                update_price_cache({symbol: quote})
            return quote
        except Exception as e:
            logger.warning(f"Error fetching price for {symbol}: {e}")
            return None
        finally:
            with _fetch_lock:
                if symbol in _fetching:
                    del _fetching[symbol]
    
    task = asyncio.create_task(_fetch())
    with _fetch_lock:
        _fetching[symbol] = task
    
    return await task


async def fetch_prices_batch(symbols: List[str], batch_size: int = 20) -> Dict[str, dict]:
    """
    Fetch prices for multiple symbols in batches to respect rate limits
    Returns cached data where available, fetches fresh data for others
    """
    results = {}

    # First, get all cached prices
    for symbol in symbols:
        cached = get_cached_price(symbol)
        if cached:
            results[symbol.upper()] = cached

    # Determine which symbols need fresh data
    symbols_to_fetch = [s for s in symbols if s.upper() not in results]

    if not symbols_to_fetch:
        return results

    # Fetch in batches with minimal delays
    from app.core import data

    for i in range(0, len(symbols_to_fetch), batch_size):
        batch = symbols_to_fetch[i:i + batch_size]

        # Fetch batch in parallel
        tasks = [fetch_price(symbol) for symbol in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, result in zip(batch, batch_results):
            if isinstance(result, Exception):
                logger.warning(f"Error fetching {symbol}: {result}")
            elif result:
                results[symbol.upper()] = result

        # Minimal delay between batches
        if i + batch_size < len(symbols_to_fetch):
            await asyncio.sleep(0.2)  # Reduced to 0.2 seconds

    return results


async def background_price_update_task():
    """
    Lightweight background task that pre-fetches popular assets
    All other assets are fetched on-demand when requested
    """
    from app.core import config

    # Popular assets to pre-fetch (top 10 from each category)
    POPULAR_ASSETS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BTC-USD", "ETH-USD"
    ]

    logger.info("Starting lightweight background price update task...")

    while True:
        try:
            # Pre-fetch popular assets in small batches
            logger.info("Pre-fetching popular assets...")
            results = await fetch_prices_batch(POPULAR_ASSETS, batch_size=10)
            logger.info(f"Pre-fetched {len(results)} popular assets")

            # Sleep for 30 seconds (faster updates)
            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Background task error: {e}")
            await asyncio.sleep(10)


def get_cache_status() -> dict:
    """Get cache statistics"""
    with _cache_lock:
        now = datetime.now(timezone.utc)
        return {
            "total_cached": len(_price_cache),
            "fresh_count": len([
                k for k, v in _cache_timestamps.items()
                if (now - v).total_seconds() < _cache_ttl
            ]),
            "crypto_count": len([s for s in _price_cache if s.endswith("-USD")]),
            "stock_count": len([s for s in _price_cache if not s.endswith("-USD") and not s.endswith("=X")]),
            "forex_count": len([s for s in _price_cache if s.endswith("=X")])
        }
