"""Data access: daily prices (yfinance), live quotes, and recent news (Google News RSS)."""
from __future__ import annotations

import calendar
import time
import urllib.parse
from datetime import datetime, timezone

import pandas as pd

from . import config

_price_cache: dict[str, tuple[float, pd.DataFrame]] = {}
_quote_cache: dict[str, tuple[float, dict | None]] = {}


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=str.lower)
    cols = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
    df = df[cols]
    if "volume" not in df.columns:
        df["volume"] = 0.0
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df[~df.index.duplicated(keep="last")].sort_index().dropna(subset=["close"])


def get_prices(symbol: str, period: str = config.HISTORY_PERIOD) -> pd.DataFrame:
    """Daily OHLCV with lowercase columns and a tz-naive DatetimeIndex."""
    import yfinance as yf

    key = f"{symbol}|{period}|1d"
    hit = _price_cache.get(key)
    if hit and time.time() - hit[0] < config.API_CACHE_SECONDS:
        return hit[1].copy()

    df = yf.Ticker(symbol).history(period=period, interval="1d", auto_adjust=True)
    if df is None or df.empty:
        raise ValueError(f"No price data returned for '{symbol}'. Check the symbol.")
    df = _normalize_ohlcv(df)
    if len(df) < 400:
        raise ValueError(
            f"Only {len(df)} days of history for '{symbol}'; need at least 400 to train."
        )
    _price_cache[key] = (time.time(), df)
    return df.copy()


def get_live_quote(symbol: str) -> dict | None:
    """Latest traded price from Yahoo. Never used as a training row.

    Returns None on failure so the daily model still works offline / in tests.
    """
    now = time.time()
    hit = _quote_cache.get(symbol)
    if hit and now - hit[0] < config.LIVE_QUOTE_CACHE_SECONDS:
        return hit[1]

    quote = None
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        price = prev = None
        try:
            fi = ticker.fast_info
            last = fi.get("last_price") if hasattr(fi, "get") else getattr(fi, "last_price", None)
            prev_c = fi.get("previous_close") if hasattr(fi, "get") else getattr(fi, "previous_close", None)
            if last is not None:
                price = float(last)
            if prev_c is not None:
                prev = float(prev_c)
        except Exception:
            pass

        if price is None:
            hist = ticker.history(period="5d", interval="1d", auto_adjust=True)
            if hist is not None and not hist.empty:
                hist = _normalize_ohlcv(hist)
                price = float(hist["close"].iloc[-1])
                prev = float(hist["close"].iloc[-2]) if len(hist) > 1 else price

        if price is not None:
            prev = prev if prev is not None else price
            quote = {
                "symbol": symbol,
                "price": round(price, 6),
                "previous_close": round(prev, 6),
                "change": round(price - prev, 6),
                "change_pct": round((price - prev) / prev, 6) if prev else 0.0,
                "as_of": datetime.now(timezone.utc).isoformat(),
                "source": "yahoo",
            }
    except Exception:
        quote = None

    _quote_cache[symbol] = (now, quote)
    return quote


def get_quotes(symbols: list[str]) -> dict[str, dict | None]:
    return {s: get_live_quote(s) for s in symbols}


def get_news(query: str, max_items: int = 30) -> list[dict]:
    """Recent headlines for a search query. Returns [] on any failure."""
    try:
        import feedparser

        q = urllib.parse.quote_plus(f"{query} when:7d")
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:max_items]:
            ts = None
            if getattr(e, "published_parsed", None):
                ts = datetime.fromtimestamp(calendar.timegm(e.published_parsed), tz=timezone.utc)
            source = getattr(getattr(e, "source", None), "title", "") or ""
            items.append({"title": e.title, "source": source, "published": ts, "link": e.link})
        return items
    except Exception:
        return []
