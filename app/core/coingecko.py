"""CoinGecko API integration for cryptocurrency data."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional, Dict, List

import requests

# Import extended crypto database
try:
    from ..providers.crypto_extended_300 import get_coingecko_id_map
    COINGECKO_ID_MAP = get_coingecko_id_map()
except ImportError:
    COINGECKO_ID_MAP = {}


class CoinGeckoError(Exception):
    """Custom exception for CoinGecko API errors."""
    pass


class CoinGeckoClient:
    """CoinGecko API client for fetching cryptocurrency data."""

    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize CoinGecko client.
        
        Args:
            api_key: Optional API key for higher rate limits (CoinGecko Pro)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Market-Predictor/1.0",
            "Accept": "application/json"
        })
        if api_key:
            self.session.headers.update({"x-cg-pro-api-key": api_key})
        
        # Cache for API responses
        self._cache: Dict[str, tuple[float, dict]] = {}
        self._cache_ttl = 300  # 5 minutes cache to reduce rate limits
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum 1 second between requests
    
    def _get(self, endpoint: str, params: Optional[dict] = None, use_cache: bool = True) -> dict:
        """Make a GET request to CoinGecko API with caching and rate limiting.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            use_cache: Whether to use cached response if available
            
        Returns:
            JSON response as dictionary
            
        Raises:
            CoinGeckoError: If API request fails
        """
        cache_key = f"{endpoint}|{str(params)}"
        
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached and time.time() - cached[0] < self._cache_ttl:
                return cached[1]
        
        # Rate limiting: wait between requests
        time_since_last = time.time() - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self._last_request_time = time.time()
            
            if response.status_code == 429:
                # Rate limited - wait and retry once
                time.sleep(2)
                response = self.session.get(url, params=params, timeout=10)
                self._last_request_time = time.time()
            
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._cache[cache_key] = (time.time(), data)
            
            return data
        except requests.exceptions.RequestException as e:
            raise CoinGeckoError(f"CoinGecko API request failed: {e}")
        except ValueError as e:
            raise CoinGeckoError(f"Failed to parse CoinGecko response: {e}")
    
    def get_top_coins(self, vs_currency: str = "usd", order: str = "market_cap_desc", 
                      per_page: int = 250, page: int = 1, 
                      sparkline: bool = False, price_change_percentage: Optional[str] = None) -> List[dict]:
        """Get top cryptocurrencies by market cap.
        
        Args:
            vs_currency: Target currency (default: usd)
            order: Sort order (market_cap_desc, market_cap_asc, etc.)
            per_page: Number of results per page (max 250)
            page: Page number
            sparkline: Include sparkline data
            price_change_percentage: Price change percentage (e.g., "1h,24h,7d")
            
        Returns:
            List of coin data dictionaries
        """
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": sparkline
        }
        if price_change_percentage:
            params["price_change_percentage"] = price_change_percentage
        
        return self._get("/coins/markets", params=params)
    
    def get_coin_list(self) -> List[dict]:
        """Get list of all supported coins with their ids and symbols.
        
        Returns:
            List of coin dictionaries with id, symbol, and name
        """
        return self._get("/coins/list")
    
    def get_coin_price(self, coin_id: str, vs_currencies: str = "usd", 
                       include_market_cap: bool = True, 
                       include_24hr_vol: bool = True, 
                       include_24hr_change: bool = True, 
                       include_last_updated: bool = True) -> dict:
        """Get current price for a specific coin.
        
        Args:
            coin_id: Coin identifier (e.g., "bitcoin")
            vs_currencies: Target currencies (comma-separated, e.g., "usd,eur")
            include_market_cap: Include market cap
            include_24hr_vol: Include 24h volume
            include_24hr_change: Include 24h change
            include_last_updated: Include last updated timestamp
            
        Returns:
            Dictionary with price data
        """
        params = {
            "vs_currencies": vs_currencies,
            "include_market_cap": str(include_market_cap).lower(),
            "include_24hr_vol": str(include_24hr_vol).lower(),
            "include_24hr_change": str(include_24hr_change).lower(),
            "include_last_updated": str(include_last_updated).lower()
        }
        return self._get(f"/simple/price", params=params)
    
    def get_coin_market_data(self, coin_id: str, vs_currency: str = "usd", days: int = 365) -> dict:
        """Get historical market data for a coin.
        
        Args:
            coin_id: Coin identifier
            vs_currency: Target currency
            days: Number of days of history
            
        Returns:
            Dictionary with historical data
        """
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        return self._get(f"/coins/{coin_id}/market_chart", params=params)
    
    def search_coins(self, query: str) -> dict:
        """Search for coins by name or symbol.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        params = {"query": query}
        return self._get("/search", params=params)
    
    def get_all_coins_data(self, limit: int = 300) -> List[dict]:
        """Get top N coins by fetching multiple pages.
        
        Args:
            limit: Total number of coins to fetch
            
        Returns:
            List of coin data dictionaries
        """
        all_coins = []
        per_page = 250
        pages = (limit + per_page - 1) // per_page
        
        for page in range(1, pages + 1):
            coins = self.get_top_coins(per_page=per_page, page=page)
            all_coins.extend(coins)
            if len(all_coins) >= limit:
                break
        
        return all_coins[:limit]
    
    def coin_to_yahoo_symbol(self, coin_id: str, symbol: str) -> str:
        """Convert CoinGecko coin to Yahoo Finance symbol format.
        
        Args:
            coin_id: CoinGecko coin id
            symbol: Coin symbol
            
        Returns:
            Yahoo Finance symbol (e.g., "BTC-USD")
        """
        return f"{symbol.upper()}-USD"


# Global client instance
_client: Optional[CoinGeckoClient] = None


def get_coingecko_client() -> CoinGeckoClient:
    """Get or create the global CoinGecko client instance."""
    global _client
    if _client is None:
        import os
        api_key = os.getenv("COINGECKO_API_KEY")
        _client = CoinGeckoClient(api_key=api_key)
    return _client


def get_top_cryptos(limit: int = 300) -> List[dict]:
    """Get top cryptocurrencies by market cap.
    
    Args:
        limit: Number of coins to fetch
        
    Returns:
        List of coin data dictionaries
    """
    client = get_coingecko_client()
    return client.get_all_coins_data(limit=limit)


def get_crypto_price(coin_id: str, symbol: str) -> Optional[dict]:
    """Get current price for a cryptocurrency.
    
    Args:
        coin_id: CoinGecko coin id
        symbol: Coin symbol
        
    Returns:
        Dictionary with price data or None if failed
    """
    try:
        client = get_coingecko_client()
        
        # First, try to find the correct coin ID if the provided one doesn't work
        try:
            coin_list = client.get_coin_list()
            matched_id = None
            for coin in coin_list:
                if coin['symbol'].lower() == coin_id.lower():
                    matched_id = coin['id']
                    break
            
            if matched_id:
                coin_id = matched_id
        except Exception:
            pass  # Use the provided coin_id as fallback
        
        data = client.get_coin_price(coin_id, vs_currencies="usd", 
                                     include_market_cap=True, 
                                     include_24hr_vol=True, 
                                     include_24hr_change=True,
                                     include_last_updated=True)
        
        if coin_id in data:
            coin_data = data[coin_id]
            return {
                "symbol": f"{symbol.upper()}-USD",
                "name": coin_id,
                "price": coin_data.get("usd"),
                "change_pct": coin_data.get("usd_24h_change"),
                "market_cap": coin_data.get("usd_market_cap"),
                "volume_24h": coin_data.get("usd_24h_vol"),
                "last_updated": coin_data.get("last_updated_at"),
                "source": "coingecko"
            }
    except CoinGeckoError:
        return None
    
    return None
