"""
Polygon.io API integration for real-time market data.
Supports stocks, crypto, forex, and options with WebSocket streaming.
"""
from __future__ import annotations

import time
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List

import requests


class PolygonError(Exception):
    """Custom exception for Polygon API errors."""
    pass


class PolygonClient:
    """Polygon.io API client for fetching real-time market data."""

    BASE_URL = "https://api.polygon.io"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Polygon client.
        
        Args:
            api_key: Polygon.io API key (get from https://polygon.io/)
        """
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY environment variable or api_key parameter is required")
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Market-Predictor/1.0",
            "Accept": "application/json"
        })
        
        # Cache for API responses
        self._cache: Dict[str, tuple[float, dict]] = {}
        self._cache_ttl = 5  # 5 seconds default cache for real-time data
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # Polygon allows 5 requests/minute on free tier
    
    def _get(self, endpoint: str, params: Optional[dict] = None, use_cache: bool = True) -> dict:
        """Make a GET request to Polygon API with caching and rate limiting.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            use_cache: Whether to use cached response if available
            
        Returns:
            JSON response as dictionary
            
        Raises:
            PolygonError: If API request fails
        """
        cache_key = f"{endpoint}|{str(params)}"
        
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached and time.time() - cached[0] < self._cache_ttl:
                return cached[1]
        
        # Rate limiting
        time_since_last = time.time() - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
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
            raise PolygonError(f"Polygon API request failed: {e}")
        except ValueError as e:
            raise PolygonError(f"Failed to parse Polygon response: {e}")
    
    def get_ticker_snapshot(self, ticker: str) -> dict:
        """Get current ticker data for a stock.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            
        Returns:
            Dictionary with ticker data
        """
        try:
            data = self._get(f"/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}")
            results = data.get("results", [])
            if results:
                return results[0]
            return {}
        except Exception as e:
            raise PolygonError(f"Failed to get ticker snapshot for {ticker}: {e}")
    
    def get_crypto_snapshot(self, ticker: str) -> dict:
        """Get current crypto data.
        
        Args:
            ticker: Crypto ticker (e.g., "X:BTCUSD")
            
        Returns:
            Dictionary with crypto data
        """
        try:
            data = self._get(f"/v2/snapshot/locale/us/markets/crypto/tickers/{ticker}")
            results = data.get("results", [])
            if results:
                return results[0]
            return {}
        except Exception as e:
            raise PolygonError(f"Failed to get crypto snapshot for {ticker}: {e}")
    
    def get_forex_snapshot(self, from_currency: str, to_currency: str) -> dict:
        """Get current forex rate.
        
        Args:
            from_currency: Base currency (e.g., "USD")
            to_currency: Quote currency (e.g., "EUR")
            
        Returns:
            Dictionary with forex data
        """
        try:
            ticker = f"C:{from_currency}{to_currency}"
            data = self._get(f"/v2/snapshot/locale/us/markets/forex/tickers/{ticker}")
            results = data.get("results", [])
            if results:
                return results[0]
            return {}
        except Exception as e:
            raise PolygonError(f"Failed to get forex snapshot for {from_currency}/{to_currency}: {e}")
    
    def get_previous_close(self, ticker: str) -> Optional[float]:
        """Get previous close price for a ticker.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Previous close price or None
        """
        try:
            data = self._get(f"/v2/aggs/ticker/{ticker}/prev")
            close = data.get("c")
            return float(close) if close else None
        except Exception:
            return None
    
    def get_grouped_daily_bars(self, ticker: str, adjusted: bool = True) -> dict:
        """Get daily OHLCV bars.
        
        Args:
            ticker: Ticker symbol
            adjusted: Whether to return adjusted prices
            
        Returns:
            Dictionary with OHLCV data
        """
        try:
            params = {
                "adjusted": "true" if adjusted else "false"
            }
            data = self._get(f"/v2/aggs/ticker/{ticker}/range/1/day", params=params)
            return data
        except Exception as e:
            raise PolygonError(f"Failed to get daily bars for {ticker}: {e}")


# Global client instance
_client: Optional[PolygonClient] = None


def get_polygon_client() -> PolygonClient:
    """Get or create the global Polygon client instance."""
    global _client
    if _client is None:
        _client = PolygonClient()
    return _client


def get_polygon_quote(symbol: str, asset_class: str = "stock") -> Optional[dict]:
    """Get live quote from Polygon.io.
    
    Args:
        symbol: Asset symbol
        asset_class: Asset class (stock, crypto, forex)
        
    Returns:
        Quote dictionary or None if failed
    """
    try:
        client = get_polygon_client()
        
        if asset_class == "crypto":
            # Convert symbol to Polygon format (BTC-USD -> X:BTCUSD)
            if symbol.endswith("-USD"):
                ticker = f"X:{symbol.replace('-', '')}"
            else:
                ticker = symbol
            data = client.get_crypto_snapshot(ticker)
            
            if data:
                last = data.get("lastTrade", {}).get("p")
                prev_close = data.get("prevClose")
                if last:
                    prev = prev_close if prev_close else last
                    return {
                        "symbol": symbol,
                        "price": float(last),
                        "previous_close": float(prev) if prev else float(last),
                        "change": float(last) - float(prev) if prev else 0.0,
                        "change_pct": ((float(last) - float(prev)) / float(prev) * 100) if prev else 0.0,
                        "volume": data.get("day", {}).get("v"),
                        "market_cap": data.get("marketCap"),
                        "day_high": data.get("day", {}).get("h"),
                        "day_low": data.get("day", {}).get("l"),
                        "open": data.get("day", {}).get("o"),
                        "as_of": datetime.now(timezone.utc).isoformat(),
                        "source": "polygon"
                    }
        
        elif asset_class == "forex":
            # Convert symbol to Polygon format (EURUSD=X -> C:EURUSD)
            if symbol.endswith("=X"):
                pair = symbol.replace("=X", "")
                if len(pair) == 6:
                    from_curr, to_curr = pair[:3], pair[3:]
                    data = client.get_forex_snapshot(from_curr, to_curr)
                    
                    if data:
                        last = data.get("lastTrade", {}).get("p")
                        prev_close = data.get("prevClose")
                        if last:
                            prev = prev_close if prev_close else last
                            return {
                                "symbol": symbol,
                                "price": float(last),
                                "previous_close": float(prev) if prev else float(last),
                                "change": float(last) - float(prev) if prev else 0.0,
                                "change_pct": ((float(last) - float(prev)) / float(prev) * 100) if prev else 0.0,
                                "volume": data.get("day", {}).get("v"),
                                "market_cap": None,
                                "day_high": data.get("day", {}).get("h"),
                                "day_low": data.get("day", {}).get("l"),
                                "open": data.get("day", {}).get("o"),
                                "as_of": datetime.now(timezone.utc).isoformat(),
                                "source": "polygon"
                            }
        
        else:  # stock
            data = client.get_ticker_snapshot(symbol)
            
            if data:
                last = data.get("lastTrade", {}).get("p")
                prev_close = data.get("prevClose")
                if last:
                    prev = prev_close if prev_close else last
                    return {
                        "symbol": symbol,
                        "price": float(last),
                        "previous_close": float(prev) if prev else float(last),
                        "change": float(last) - float(prev) if prev else 0.0,
                        "change_pct": ((float(last) - float(prev)) / float(prev) * 100) if prev else 0.0,
                        "volume": data.get("day", {}).get("v"),
                        "market_cap": data.get("marketCap"),
                        "day_high": data.get("day", {}).get("h"),
                        "day_low": data.get("day", {}).get("l"),
                        "open": data.get("day", {}).get("o"),
                        "as_of": datetime.now(timezone.utc).isoformat(),
                        "source": "polygon"
                    }
    except PolygonError:
        return None
    except Exception as e:
        print(f"Polygon error for {symbol}: {e}")
        return None
    
    return None
