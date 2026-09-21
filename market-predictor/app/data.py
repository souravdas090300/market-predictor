"""Data access: daily prices (yfinance) and recent news headlines (Google News RSS)."""
from __future__ import annotations

import calendar
import urllib.parse
from datetime import datetime, timezone

import pandas as pd

from . import config


def get_prices(symbol: str, period: str = config.HISTORY_PERIOD) -> pd.DataFrame:
    """Daily OHLCV with lowercase columns and a tz-naive DatetimeIndex."""
    import yfinance as yf

    df = yf.Ticker(symbol).history(period=period, interval="1d", auto_adjust=True)
    if df is None or df.empty:
        raise ValueError(f"No price data returned for '{symbol}'. Check the symbol.")
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[~df.index.duplicated(keep="last")].sort_index().dropna(subset=["close"])
    if len(df) < 400:
        raise ValueError(
            f"Only {len(df)} days of history for '{symbol}'; need at least 400 to train."
        )
    return df


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
