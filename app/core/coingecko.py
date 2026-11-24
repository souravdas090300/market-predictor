"""CoinGecko API integration for cryptocurrency data."""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

# Import extended crypto database
try:
    from ..providers.crypto_extended_300 import get_coingecko_id_map
    COINGECKO_ID_MAP = get_coingecko_id_map()
except ImportError:  # pragma: no cover - fallback when provider module is unavailable
    COINGECKO_ID_MAP = {}


class CoinGeckoError(Exception):
    """Custom exception for CoinGecko API errors."""


TIMEFRAME_DAYS = {
    "24H": 1,
    "1W": 7,
    "1M": 30,
    "6M": 180,
    "1Y": 365,
    "5Y": 365,
    "ALL": "max",
}

TIMEFRAME_BUCKET_SECONDS = {
    "24H": 300,
    "1W": 3600,
    "1M": 86400,
    "6M": 86400,
    "1Y": 86400,
    "5Y": 604800,
    "ALL": 2592000,
}

_COIN_LIST_TTL = 86400
_coin_list: List[dict] = []
_coin_list_updated: float = 0.0


class CoinGeckoClient:
    """CoinGecko API client with caching, rate limiting, and OHLC history."""

    PUBLIC_BASE_URL = "https://api.coingecko.com/api/v3"
    PRO_BASE_URL = "https://pro-api.coingecko.com/api/v3"

    def __init__(self, api_key: Optional[str] = None, api_type: Optional[str] = None):
        """Initialize CoinGecko client.

        Args:
            api_key: Optional demo or Pro API key.
            api_type: ``demo`` (public host) or ``pro`` (Pro host). Defaults to
                ``COINGECKO_API_TYPE`` or ``demo``.
        """
        self.api_key = api_key
        resolved_type = (api_type or os.getenv("COINGECKO_API_TYPE") or "demo").strip().lower()
        self.api_type = "pro" if resolved_type == "pro" else "demo"
        self.base_url = self.PRO_BASE_URL if self.api_type == "pro" else self.PUBLIC_BASE_URL

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Market-Predictor/1.0",
            "Accept": "application/json"
        })
        if api_key:
            header = "x-cg-pro-api-key" if self.api_type == "pro" else "x-cg-demo-api-key"
            self.session.headers.update({header: api_key})

        self._cache: Dict[str, tuple[float, Any]] = {}
        self._cache_ttl = 300
        self._last_request_time = 0.0
        self._min_request_interval = 1.0

    def _get(self, endpoint: str, params: Optional[dict] = None, use_cache: bool = True) -> Any:
        """Make a cached, rate-limited GET request to CoinGecko."""
        cache_key = f"{endpoint}|{sorted((params or {}).items())}"

        if use_cache:
            cached = self._cache.get(cache_key)
            if cached and time.time() - cached[0] < self._cache_ttl:
                return cached[1]

        time_since_last = time.time() - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)

        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            self._last_request_time = time.time()

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = min(float(retry_after), 5.0) if retry_after else 2.0
                except ValueError:
                    delay = 2.0
                time.sleep(delay)
                response = self.session.get(url, params=params, timeout=10)
                self._last_request_time = time.time()

            response.raise_for_status()
            data = response.json()
            if use_cache:
                self._cache[cache_key] = (time.time(), data)
            return data
        except requests.exceptions.RequestException as exc:
            raise CoinGeckoError(f"CoinGecko API request failed: {exc}") from exc
        except ValueError as exc:
            raise CoinGeckoError(f"Failed to parse CoinGecko response: {exc}") from exc

    def get_top_coins(
        self,
        vs_currency: str = "usd",
        order: str = "market_cap_desc",
        per_page: int = 250,
        page: int = 1,
        sparkline: bool = False,
        price_change_percentage: Optional[str] = None
    ) -> List[dict]:
        """Get top cryptocurrencies by market cap."""
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": max(1, min(per_page, 250)),
            "page": max(1, page),
            "sparkline": "true" if sparkline else "false"
        }
        if price_change_percentage:
            params["price_change_percentage"] = price_change_percentage
        return self._get("/coins/markets", params=params)

    def get_coin_list(self) -> List[dict]:
        """Get all supported coins with their ids and symbols."""
        return self._get("/coins/list")

    def get_coin_price(
        self,
        coin_id: str,
        vs_currencies: str = "usd",
        include_market_cap: bool = True,
        include_24hr_vol: bool = True,
        include_24hr_change: bool = True,
        include_last_updated: bool = True
    ) -> dict:
        """Get current price and 24h stats for a specific coin id."""
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currencies,
            "include_market_cap": str(include_market_cap).lower(),
            "include_24hr_vol": str(include_24hr_vol).lower(),
            "include_24hr_change": str(include_24hr_change).lower(),
            "include_last_updated": str(include_last_updated).lower()
        }
        return self._get("/simple/price", params=params)

    def get_coin_ohlc(self, coin_id: str, days: Any = 1) -> List[list]:
        """Get OHLC candles for a coin (up to 365 days on public plans)."""
        return self._get(
            f"/coins/{quote(str(coin_id), safe='')}/ohlc",
            params={"vs_currency": "usd", "days": days}
        )

    def get_coin_market_data(self, coin_id: str, vs_currency: str = "usd", days: Any = 365) -> dict:
        """Get historical market data for a coin."""
        return self._get(
            f"/coins/{quote(str(coin_id), safe='')}/market_chart",
            params={"vs_currency": vs_currency, "days": days}
        )

    def get_coin_history(self, coin_id: str, timeframe: str) -> List[Dict]:
        """Get normalized OHLCV candles for a coin and timeframe."""
        days = TIMEFRAME_DAYS.get(timeframe, 30)
        try:
            candles = normalize_ohlc(self.get_coin_ohlc(coin_id, days=days))
            if candles:
                return candles
        except CoinGeckoError:
            pass

        # Fallback for plans where the OHLC endpoint is unavailable.
        market_data = self.get_coin_market_data(coin_id, days=days)
        return market_chart_to_ohlc(market_data, timeframe)

    def search_coins(self, query: str) -> dict:
        """Search for coins by name or symbol."""
        return self._get("/search", params={"query": query})

    def get_all_coins_data(self, limit: int = 300) -> List[dict]:
        """Get top N coins by fetching multiple pages."""
        all_coins: List[dict] = []
        per_page = 250
        pages = (limit + per_page - 1) // per_page
        for page in range(1, pages + 1):
            coins = self.get_top_coins(per_page=per_page, page=page)
            all_coins.extend(coins)
            if len(all_coins) >= limit:
                break
        return all_coins[:limit]

    def coin_to_yahoo_symbol(self, coin_id: str, symbol: str) -> str:
        """Convert a CoinGecko coin to the Yahoo Finance symbol format."""
        return f"{symbol.upper()}-USD"


_client: Optional[CoinGeckoClient] = None


def get_coingecko_client() -> CoinGeckoClient:
    """Get or create the global CoinGecko client instance."""
    global _client
    if _client is None:
        _client = CoinGeckoClient(
            api_key=os.getenv("COINGECKO_API_KEY") or None,
            api_type=os.getenv("COINGECKO_API_TYPE") or None
        )
    return _client


def clear_client_cache() -> None:
    """Reset the shared client and caches (used by tests/cache endpoints)."""
    global _client, _coin_list, _coin_list_updated
    _client = None
    _coin_list = []
    _coin_list_updated = 0.0


def resolve_coin_id(symbol: str, client: Optional[CoinGeckoClient] = None) -> Optional[str]:
    """Resolve a Yahoo-style symbol (BTC-USD) to a CoinGecko id (bitcoin)."""
    normalized = (symbol or '').strip().upper().removesuffix('-USD')
    if not normalized:
        return None
    if normalized in COINGECKO_ID_MAP:
        return COINGECKO_ID_MAP[normalized]

    global _coin_list, _coin_list_updated
    if time.time() - _coin_list_updated >= _COIN_LIST_TTL:
        try:
            _coin_list = (client or get_coingecko_client()).get_coin_list() or []
            _coin_list_updated = time.time()
        except CoinGeckoError:
            return None

    for coin in _coin_list:
        if str(coin.get('symbol', '')).lower() == normalized.lower():
            return coin.get('id')
    return None


def get_coin_quote(symbol: str, coin_id: Optional[str] = None) -> Optional[dict]:
    """Get a normalized quote for a single coin via ``/simple/price``."""
    resolved_id = coin_id or resolve_coin_id(symbol)
    if not resolved_id:
        return None
    try:
        data = get_coingecko_client().get_coin_price(resolved_id)
    except CoinGeckoError:
        return None

    coin_data = data.get(resolved_id) or {}
    price = coin_data.get('usd')
    if price is None:
        return None
    change_pct = coin_data.get('usd_24h_change') or 0.0
    price = float(price)
    previous_close = price / (1 + float(change_pct) / 100) if change_pct else price
    return {
        "symbol": symbol if symbol.endswith("-USD") else f"{symbol.upper()}-USD",
        "price": round(price, 6),
        "previous_close": round(previous_close, 6),
        "change": round(price - previous_close, 6),
        "change_pct": round(float(change_pct) / 100, 6),
        "volume": coin_data.get('usd_24h_vol'),
        "market_cap": coin_data.get('usd_market_cap'),
        "open": None,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "source": "coingecko",
        "coingecko_id": resolved_id
    }


def get_coin_history(symbol: str, timeframe: str) -> List[Dict]:
    """Get real CoinGecko OHLCV history for a Yahoo-style crypto symbol."""
    coin_id = resolve_coin_id(symbol)
    if not coin_id:
        raise CoinGeckoError(f"Could not resolve CoinGecko id for {symbol}")
    return get_coingecko_client().get_coin_history(coin_id, timeframe)


def normalize_ohlc(raw_candles: List[list]) -> List[Dict]:
    """Convert CoinGecko OHLC arrays to API candle dictionaries."""
    candles: List[Dict] = []
    for row in raw_candles or []:
        if not isinstance(row, (list, tuple)) or len(row) < 5:
            continue
        try:
            timestamp = datetime.fromtimestamp(float(row[0]) / 1000, tz=timezone.utc)
            candles.append({
                "timestamp": timestamp.isoformat().replace('+00:00', 'Z'),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": 0.0
            })
        except (TypeError, ValueError, OSError):
            continue
    return candles


def market_chart_to_ohlc(market_data: dict, timeframe: str) -> List[Dict]:
    """Aggregate CoinGecko market chart prices into OHLCV candles."""
    bucket = TIMEFRAME_BUCKET_SECONDS.get(timeframe, 86400)
    prices = (market_data or {}).get('prices') or []
    volumes = (market_data or {}).get('total_volumes') or []

    volume_by_bucket: Dict[int, float] = {}
    for item in volumes:
        if not isinstance(item, (list, tuple)) or len(item) < 2 or item[1] is None:
            continue
        key = int(int(item[0]) / 1000 // bucket * bucket)
        volume_by_bucket[key] = volume_by_bucket.get(key, 0.0) + float(item[1])

    grouped: Dict[int, Dict[str, float]] = {}
    for item in prices:
        if not isinstance(item, (list, tuple)) or len(item) < 2 or item[1] is None:
            continue
        key = int(int(item[0]) / 1000 // bucket * bucket)
        price = float(item[1])
        candle = grouped.setdefault(key, {"open": price, "high": price, "low": price, "close": price})
        candle["high"] = max(candle["high"], price)
        candle["low"] = min(candle["low"], price)
        candle["close"] = price

    return [
        {
            "timestamp": datetime.fromtimestamp(key, tz=timezone.utc).isoformat().replace('+00:00', 'Z'),
            "open": round(candle["open"], 8),
            "high": round(candle["high"], 8),
            "low": round(candle["low"], 8),
            "close": round(candle["close"], 8),
            "volume": round(volume_by_bucket.get(key, 0.0), 2)
        }
        for key, candle in sorted(grouped.items())
    ]


def get_top_cryptos(limit: int = 300) -> List[dict]:
    """Get top cryptocurrencies by market cap."""
    return get_coingecko_client().get_all_coins_data(limit=limit)


def get_crypto_price(coin_id: str, symbol: str) -> Optional[dict]:
    """Get a normalized current price for a coin id or symbol."""
    resolved_id = resolve_coin_id(coin_id or symbol) or coin_id
    quote = get_coin_quote(symbol, resolved_id)
    if not quote:
        return None
    return {
        "symbol": quote["symbol"],
        "name": resolved_id,
        "price": quote["price"],
        "change_pct": quote["change_pct"] * 100,
        "market_cap": quote["market_cap"],
        "volume_24h": quote["volume"],
        "last_updated": quote["as_of"],
        "source": "coingecko"
    }
