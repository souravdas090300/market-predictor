"""
Redis Caching Layer — Replaces slow SQLite queries with sub-100ms responses
Handles: prices, assets, indicators, charts
TTL: 5-60 seconds depending on data type
"""

import redis
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from functools import wraps
import asyncio
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None, raise_on_error: bool = False):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_keepalive=True,
            socket_keepalive_options={
                1: 1,  # TCP_KEEPIDLE
                2: 1,  # TCP_KEEPINTVL
                3: 3,  # TCP_KEEPCNT
            }
        )

        # Test connection
        try:
            self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            if raise_on_error:
                raise
            # If not raising, set redis_client to None to indicate no connection
            self.redis_client = None

    def _is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None

    def set_prices(self, prices: List[Dict], ttl: int = 300):
        """Cache all live prices (5 min TTL)"""
        if not self.redis_client:
            return
        try:
            key = "cache:prices:all"
            value = json.dumps([{
                "symbol": p["symbol"],
                "name": p["name"],
                "category": p["category"],
                "current_price": p["current_price"],
                "change_24h": p["change_24h"],
                "change_percent_24h": p["change_percent_24h"],
                "updated_at": p["updated_at"].isoformat() if hasattr(p["updated_at"], 'isoformat') else p["updated_at"]
            } for p in prices], default=str)

            self.redis_client.setex(key, ttl, value)
            logger.debug(f"Cached {len(prices)} prices")
        except Exception as e:
            logger.error(f"Error caching prices: {e}")

    def get_prices(self) -> Optional[List[Dict]]:
        """Get cached prices (instant <1ms)"""
        if not self._is_available():
            return None
        try:
            key = "cache:prices:all"
            cached = self.redis_client.get(key)
            if cached:
                logger.debug("Price cache hit")
                return json.loads(cached)
            logger.debug("Price cache miss - query DB")
            return None
        except Exception as e:
            logger.error(f"Error getting prices from cache: {e}")
            return None

    def set_prices_by_category(self, category: str, prices: List[Dict], ttl: int = 300):
        """Cache prices by category (crypto, stocks, forex, etc)"""
        try:
            key = f"cache:prices:{category}"
            value = json.dumps([p for p in prices if p.get("category") == category], default=str)
            self.redis_client.setex(key, ttl, value)
            logger.debug(f"Cached {len(prices)} {category} prices")
        except Exception as e:
            logger.error(f"Error caching {category} prices: {e}")

    def get_prices_by_category(self, category: str) -> Optional[List[Dict]]:
        """Get cached prices by category"""
        try:
            key = f"cache:prices:{category}"
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"✅ {category} price cache hit")
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting {category} prices: {e}")
            return None

    def set_ohlcv(self, symbol: str, timeframe: str, ohlcv_data: List[Dict], ttl: int = 3600):
        """Cache OHLCV candlestick data (1 hour TTL for 1d, 5 min for 1m)"""
        try:
            key = f"cache:ohlcv:{symbol}:{timeframe}"
            value = json.dumps(ohlcv_data, default=str)
            self.redis_client.setex(key, ttl, value)
            logger.debug(f"Cached OHLCV for {symbol} {timeframe}")
        except Exception as e:
            logger.error(f"Error caching OHLCV: {e}")

    def get_ohlcv(self, symbol: str, timeframe: str) -> Optional[List[Dict]]:
        """Get cached OHLCV candlestick (instant <10ms)"""
        try:
            key = f"cache:ohlcv:{symbol}:{timeframe}"
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"✅ OHLCV cache hit for {symbol} {timeframe}")
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting OHLCV: {e}")
            return None

    def set_asset_detail(self, symbol: str, asset_data: Dict, ttl: int = 300):
        """Cache individual asset detail"""
        try:
            key = f"cache:asset:{symbol}"
            value = json.dumps(asset_data, default=str)
            self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Error caching asset detail: {e}")

    def get_asset_detail(self, symbol: str) -> Optional[Dict]:
        """Get cached asset detail"""
        try:
            key = f"cache:asset:{symbol}"
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting asset detail: {e}")
            return None

    def set_search_results(self, query: str, results: List[Dict], ttl: int = 3600):
        """Cache search results (1 hour)"""
        try:
            key = f"cache:search:{query.lower()}"
            value = json.dumps(results, default=str)
            self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Error caching search: {e}")

    def get_search_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        try:
            key = f"cache:search:{query.lower()}"
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting search cache: {e}")
            return None

    def set_indicators(self, symbol: str, indicator_type: str, data: Dict, ttl: int = 300):
        """Cache technical indicators (SMA, EMA, RSI, MACD, etc)"""
        try:
            key = f"cache:indicator:{symbol}:{indicator_type}"
            value = json.dumps(data, default=str)
            self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Error caching indicator: {e}")

    def get_indicators(self, symbol: str, indicator_type: str) -> Optional[Dict]:
        """Get cached indicators"""
        try:
            key = f"cache:indicator:{symbol}:{indicator_type}"
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting indicator cache: {e}")
            return None

    def invalidate_prices(self):
        """Clear all price caches"""
        try:
            keys = self.redis_client.keys("cache:prices:*")
            if keys:
                self.redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} price caches")
        except Exception as e:
            logger.error(f"Error invalidating price cache: {e}")

    def invalidate_ohlcv(self, symbol: Optional[str] = None):
        """Clear OHLCV cache (specific symbol or all)"""
        try:
            pattern = f"cache:ohlcv:{symbol}:*" if symbol else "cache:ohlcv:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} OHLCV caches")
        except Exception as e:
            logger.error(f"Error invalidating OHLCV cache: {e}")

    def get_stats(self) -> Dict:
        """Get Redis stats"""
        try:
            info = self.redis_client.info()
            return {
                "memory_usage_mb": info.get("used_memory", 0) / 1024 / 1024,
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / (info.get("keyspace_hits", 1) + info.get("keyspace_misses", 1)),
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {}

    def close(self):
        """Close Redis connection"""
        try:
            self.redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")


# Initialize globally
redis_cache: Optional[RedisCache] = None

def init_redis(host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None, raise_on_error: bool = False) -> RedisCache:
    """Initialize Redis cache"""
    global redis_cache
    redis_cache = RedisCache(host=host, port=port, db=db, password=password, raise_on_error=raise_on_error)
    return redis_cache

def get_redis() -> RedisCache:
    """Get Redis instance"""
    if redis_cache is None:
        raise RuntimeError("Redis not initialized. Call init_redis() in app startup.")
    return redis_cache


# Decorator for automatic caching
def cache_response(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator to automatically cache function responses

    Usage:
    @cache_response(ttl=300, key_prefix="assets")
    async def get_assets():
        return expensive_query()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            try:
                cached = redis_cache.redis_client.get(cache_key)
                if cached:
                    logger.debug(f"✅ Cache hit: {cache_key}")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache lookup failed: {e}")

            # Cache miss - call function
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                redis_cache.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
            except Exception as e:
                logger.warning(f"Cache store failed: {e}")

            return result

        return wrapper
    return decorator
