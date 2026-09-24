"""News aggregation and sentiment analysis module."""
import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import time


class NewsAggregator:
    """Aggregate news from multiple sources."""
    
    def __init__(self):
        self.sources = {
            'google': 'https://news.google.com/rss/search?q=',
            'yahoo': 'https://news.yahoo.com/rss/',
            'bloomberg': 'https://www.bloomberg.com/feed'
        }
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def fetch_news(self, symbol: str, asset_class: str = 'stock', max_articles: int = 20) -> List[Dict]:
        """
        Fetch news for a specific symbol.
        
        Args:
            symbol: Asset symbol
            asset_class: Type of asset (stock, crypto, forex, commodity)
            max_articles: Maximum number of articles to return
        
        Returns:
            List of news articles with metadata
        """
        cache_key = f"{symbol}_{asset_class}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        articles = []
        
        # Add search terms based on asset class
        search_terms = self._get_search_terms(symbol, asset_class)
        
        # Fetch from multiple sources
        for source in self.sources:
            try:
                if source == 'google':
                    articles.extend(self._fetch_google_news(search_terms, max_articles // 3))
                elif source == 'yahoo':
                    articles.extend(self._fetch_yahoo_news(symbol, max_articles // 3))
                elif source == 'bloomberg':
                    articles.extend(self._fetch_bloomberg_news(search_terms, max_articles // 3))
            except Exception as e:
                print(f"Error fetching from {source}: {e}")
                continue
        
        # Sort by date and limit
        articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        articles = articles[:max_articles]
        
        # Cache results
        self.cache[cache_key] = (time.time(), articles)
        
        return articles
    
    def _get_search_terms(self, symbol: str, asset_class: str) -> str:
        """Generate search terms based on asset class."""
        if asset_class == 'stock':
            return f"{symbol} stock market"
        elif asset_class == 'crypto':
            return f"{symbol} cryptocurrency"
        elif asset_class == 'forex':
            return f"{symbol} forex trading"
        elif asset_class == 'commodity':
            return f"{symbol} commodities futures"
        else:
            return symbol
    
    def _fetch_google_news(self, search_terms: str, max_articles: int) -> List[Dict]:
        """Fetch news from Google News RSS."""
        url = f"{self.sources['google']}{search_terms}"
        
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_articles]:
                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': 'Google News',
                    'summary': entry.get('summary', '')
                })
            
            return articles
        except Exception as e:
            print(f"Google News error: {e}")
            return []
    
    def _fetch_yahoo_news(self, symbol: str, max_articles: int) -> List[Dict]:
        """Fetch news from Yahoo Finance."""
        # Yahoo Finance doesn't have a direct RSS for symbols
        # This is a placeholder for implementation
        return []
    
    def _fetch_bloomberg_news(self, search_terms: str, max_articles: int) -> List[Dict]:
        """Fetch news from Bloomberg."""
        try:
            feed = feedparser.parse(self.sources['bloomberg'])
            articles = []
            
            for entry in feed.entries[:max_articles]:
                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': 'Bloomberg',
                    'summary': entry.get('summary', '')
                })
            
            return articles
        except Exception as e:
            print(f"Bloomberg error: {e}")
            return []
    
    def analyze_news_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Analyze sentiment of news articles.
        
        Args:
            articles: List of news articles
        
        Returns:
            Dictionary with sentiment analysis
        """
        if not articles:
            return {
                'total_articles': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'overall_sentiment': 0.0,
                'sentiment_trend': 'neutral'
            }
        
        positive_words = [
            'surge', 'gain', 'rise', 'increase', 'growth', 'profit', 'strong', 'boost',
            'upgrade', 'recovery', 'bullish', 'outperform', 'beat', 'record', 'high'
        ]
        
        negative_words = [
            'fall', 'drop', 'decline', 'decrease', 'loss', 'weak', 'crash', 'fear',
            'downgrade', 'recession', 'bearish', 'underperform', 'miss', 'low', 'risk'
        ]
        
        positive_count = 0
        negative_count = 0
        total_words = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            text = f"{title} {summary}"
            
            words = text.split()
            total_words += len(words)
            
            for word in words:
                if word in positive_words:
                    positive_count += 1
                elif word in negative_words:
                    negative_count += 1
        
        neutral_count = len(articles) - positive_count - negative_count
        
        # Calculate sentiment score (-1 to 1)
        if positive_count + negative_count > 0:
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            sentiment_score = 0
        
        # Determine trend
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
            'neutral': neutral_count,
            'overall_sentiment': sentiment_score,
            'sentiment_trend': trend,
            'confidence': min(abs(sentiment_score) * 100, 100)
        }


def get_news_with_sentiment(symbol: str, asset_class: str = 'stock') -> Dict:
    """
    Get news with sentiment analysis for a symbol.
    
    Args:
        symbol: Asset symbol
        asset_class: Type of asset
    
    Returns:
        Dictionary with news and sentiment data
    """
    aggregator = NewsAggregator()
    articles = aggregator.fetch_news(symbol, asset_class)
    sentiment = aggregator.analyze_news_sentiment(articles)
    
    return {
        'symbol': symbol,
        'asset_class': asset_class,
        'articles': articles,
        'sentiment': sentiment,
        'fetched_at': datetime.utcnow().isoformat()
    }