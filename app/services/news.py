"""News aggregation and sentiment analysis module.

Yahoo Finance headlines are fetched through ``yfinance.Ticker(...).news``,
which is the symbol-specific Yahoo Finance news feed. Google News and
Bloomberg RSS are used as supplementary sources.
"""
from __future__ import annotations

import calendar
import logging
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timezone
from html import unescape
from threading import Lock
from typing import Any, Dict, List, Optional

import feedparser
import requests
import yfinance as yfinance
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Aggregate symbol-specific news from Yahoo Finance and RSS sources."""

    DEFAULT_CACHE_DURATION = 300
    REQUEST_TIMEOUT = 10

    def __init__(self, cache_duration: int = DEFAULT_CACHE_DURATION, yahoo_timeout: int = REQUEST_TIMEOUT):
        self.sources = {
            'google': 'https://news.google.com/rss/search',
            'yahoo': 'https://finance.yahoo.com/quote/',
            'bloomberg': 'https://www.bloomberg.com/feed'
        }
        self.cache_duration = cache_duration
        self.yahoo_timeout = yahoo_timeout
        self.cache: Dict[str, tuple[float, List[Dict]]] = {}

    def fetch_news(
        self,
        symbol: str,
        asset_class: str = 'stock',
        max_articles: int = 20
    ) -> List[Dict]:
        """Fetch, normalize, and deduplicate news for a symbol."""
        max_articles = max(1, min(max_articles, 50))
        symbol = (symbol or '').strip().upper()
        cache_key = f"{symbol}|{asset_class}|{max_articles}"

        cached = _cache_get(cache_key, self.cache_duration)
        if cached is not None:
            return cached

        search_terms = self._get_search_terms(symbol, asset_class)
        per_source = max(1, (max_articles + 2) // 3)
        articles: List[Dict] = []

        # Yahoo Finance is the primary, symbol-specific source.
        for source in ('yahoo', 'google', 'bloomberg'):
            try:
                if source == 'yahoo':
                    articles.extend(self._fetch_yahoo_news(symbol, per_source))
                elif source == 'google':
                    articles.extend(self._fetch_google_news(search_terms, per_source))
                elif source == 'bloomberg':
                    articles.extend(self._fetch_bloomberg_news(search_terms, per_source))
            except Exception as exc:  # pragma: no cover - defensive per-source isolation
                logger.warning("Error fetching news from %s: %s", source, exc)

        unique = _dedupe_articles(articles)
        unique.sort(key=lambda article: article.get('published') or '', reverse=True)
        result = unique[:max_articles]
        _cache_set(cache_key, result)
        return result

    def _get_search_terms(self, symbol: str, asset_class: str) -> str:
        """Generate search terms based on asset class."""
        suffixes = {
            'stock': 'stock market',
            'crypto': 'cryptocurrency',
            'forex': 'forex trading',
            'commodity': 'commodities futures'
        }
        suffix = suffixes.get((asset_class or '').lower())
        return f"{symbol} {suffix}".strip() if suffix else symbol

    def _fetch_yahoo_news(self, symbol: str, max_articles: int) -> List[Dict]:
        """Fetch symbol-specific headlines from Yahoo Finance via yfinance."""
        if not symbol:
            return []

        try:
            executor = ThreadPoolExecutor(max_workers=1)
            try:
                future = executor.submit(lambda: yfinance.Ticker(symbol).news)
                raw_news = future.result(timeout=self.yahoo_timeout) or []
            except FutureTimeoutError:
                logger.warning("Yahoo Finance news timed out for %s", symbol)
                return []
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
        except Exception as exc:
            logger.warning("Yahoo Finance news error for %s: %s", symbol, exc)
            return []

        articles: List[Dict] = []
        for item in raw_news[:max_articles]:
            if not isinstance(item, dict):
                continue
            published_ts = item.get('providerPublishTime')
            published = ''
            if published_ts:
                try:
                    published = datetime.fromtimestamp(float(published_ts), tz=timezone.utc).isoformat()
                except (TypeError, ValueError, OSError):
                    published = ''
            articles.append({
                'title': _clean_text(item.get('title') or ''),
                'link': item.get('link') or item.get('url') or '',
                'published': published,
                'source': item.get('publisher') or 'Yahoo Finance',
                'provider': 'Yahoo Finance',
                'summary': _clean_text(item.get('summary') or '')
            })
        return articles

    def _fetch_google_news(self, search_terms: str, max_articles: int) -> List[Dict]:
        """Fetch news from Google News RSS."""
        query = urllib.parse.quote_plus(f"{search_terms} when:7d")
        url = (
            f"{self.sources['google']}?q={query}"
            "&hl=en-US&gl=US&ceid=US:en"
        )
        feed = self._fetch_rss(url)
        return [
            {
                'title': _clean_text(entry.get('title', '')),
                'link': entry.get('link', ''),
                'published': _entry_published(entry),
                'source': 'Google News',
                'provider': 'Google News',
                'summary': _clean_text(entry.get('summary', ''))
            }
            for entry in feed.entries[:max_articles]
        ]

    def _fetch_bloomberg_news(self, search_terms: str, max_articles: int) -> List[Dict]:
        """Fetch news from Bloomberg's public RSS feed."""
        feed = self._fetch_rss(self.sources['bloomberg'])
        return [
            {
                'title': _clean_text(entry.get('title', '')),
                'link': entry.get('link', ''),
                'published': _entry_published(entry),
                'source': 'Bloomberg',
                'provider': 'Bloomberg',
                'summary': _clean_text(entry.get('summary', ''))
            }
            for entry in feed.entries[:max_articles]
        ]

    def _fetch_rss(self, url: str):
        """Fetch and parse an RSS feed with a bounded timeout."""
        response = requests.get(
            url,
            timeout=self.REQUEST_TIMEOUT,
            headers={'User-Agent': 'Market-Predictor/1.0 (+news aggregation)', 'Accept': 'application/rss+xml, application/xml, text/xml, */*'}
        )
        response.raise_for_status()
        return feedparser.parse(response.content)

    def analyze_news_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze sentiment of news articles."""
        if not articles:
            return {
                'total_articles': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'overall_sentiment': 0.0,
                'sentiment_trend': 'neutral',
                'confidence': 0.0
            }

        positive_words = {
            'surge', 'gains', 'gain', 'rises', 'rise', 'increased', 'increase', 'growth',
            'profit', 'strong', 'boost', 'boosts', 'upgrades', 'upgrade', 'recovery',
            'bullish', 'outperform', 'beats', 'beat', 'record', 'high', 'rally', 'jump'
        }
        negative_words = {
            'fall', 'falls', 'drop', 'drops', 'decline', 'decrease', 'loss', 'losses',
            'weak', 'crash', 'fear', 'downgrade', 'downgrades', 'recession', 'bearish',
            'underperform', 'miss', 'misses', 'low', 'risk', 'risks', 'plunge', 'slump'
        }

        positive_count = 0
        negative_count = 0
        for article in articles:
            if not isinstance(article, dict):
                continue
            text = f"{article.get('title', '') or ''} {article.get('summary', '') or ''}".lower()
            for word in text.split():
                cleaned = word.strip('.,!?:;"()[]{}')
                if cleaned in positive_words:
                    positive_count += 1
                elif cleaned in negative_words:
                    negative_count += 1

        total_mentioned = positive_count + negative_count
        sentiment_score = (positive_count - negative_count) / total_mentioned if total_mentioned else 0.0
        if sentiment_score > 0.2:
            trend = 'bullish'
        elif sentiment_score < -0.2:
            trend = 'bearish'
        else:
            trend = 'neutral'

        return {
            'total_articles': len(articles),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': max(0, len(articles) - total_mentioned),
            'overall_sentiment': round(sentiment_score, 4),
            'sentiment_trend': trend,
            'confidence': round(min(abs(sentiment_score) * 100, 100), 2)
        }


# Module-level cache shared by all requests. The instance cache is retained for
# callers that construct their own aggregator.
_news_cache: Dict[str, tuple[float, List[Dict]]] = {}
_cache_lock = Lock()


def _cache_get(key: str, ttl: int) -> Optional[List[Dict]]:
    with _cache_lock:
        cached = _news_cache.get(key)
        if cached and time.time() - cached[0] < ttl:
            return [dict(article) for article in cached[1]]
    return None


def _cache_set(key: str, articles: List[Dict]) -> None:
    with _cache_lock:
        _news_cache[key] = (time.time(), [dict(article) for article in articles])


def clear_cache() -> None:
    """Clear the shared news cache (useful for tests and cache endpoints)."""
    with _cache_lock:
        _news_cache.clear()


def _clean_text(value: str) -> str:
    if not value:
        return ''
    soup = BeautifulSoup(str(value), 'html.parser')
    return unescape(soup.get_text(' ', strip=True))


def _entry_published(entry: Any) -> str:
    published = getattr(entry, 'published', None) or ''
    if getattr(entry, 'published_parsed', None):
        try:
            published = datetime.fromtimestamp(
                calendar.timegm(entry.published_parsed), tz=timezone.utc
            ).isoformat()
        except (TypeError, ValueError, OSError):
            pass
    return str(published)


def _dedupe_articles(articles: List[Dict]) -> List[Dict]:
    seen: set[tuple[str, str]] = set()
    unique: List[Dict] = []
    for article in articles:
        if not article.get('title'):
            continue
        key = (article['title'].strip().lower(), (article.get('link') or '').strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique


def get_news_with_sentiment(
    symbol: str,
    asset_class: str = 'stock',
    max_articles: int = 20
) -> Dict:
    """Get normalized news with sentiment analysis for a symbol."""
    aggregator = NewsAggregator()
    articles = aggregator.fetch_news(symbol, asset_class, max_articles)
    sentiment = aggregator.analyze_news_sentiment(articles)

    labeled_articles = []
    for article in articles:
        item = dict(article)
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        positive = any(word in text for word in ('surge', 'gain', 'rise', 'growth', 'beat', 'upgrade', 'strong', 'rally'))
        negative = any(word in text for word in ('fall', 'drop', 'decline', 'loss', 'miss', 'downgrade', 'risk', 'crash'))
        item['sentiment'] = 'positive' if positive and not negative else 'negative' if negative and not positive else 'neutral'
        labeled_articles.append(item)

    return {
        'symbol': (symbol or '').upper(),
        'asset_class': asset_class,
        'news': labeled_articles,
        'articles': labeled_articles,
        'sentiment': sentiment,
        'sources': sorted({article.get('provider') or article.get('source') or 'Unknown' for article in labeled_articles}),
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }
