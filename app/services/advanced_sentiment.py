"""Advanced Sentiment Analysis Service with comprehensive market sentiment features."""
import re
import random
import asyncio
from datetime import datetime, timedelta, timezone as tz
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
import pandas as pd

from . import sentiment as base_sentiment


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    VERY_BULLISH = "VERY_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    VERY_BEARISH = "VERY_BEARISH"


class FearGreedLabel(Enum):
    """Fear & Greed index classifications."""
    EXTREME_GREED = "EXTREME_GREED"
    GREED = "GREED"
    NEUTRAL = "NEUTRAL"
    FEAR = "FEAR"
    EXTREME_FEAR = "EXTREME_FEAR"


class Platform(Enum):
    """Social media platforms."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    DISCORD = "discord"


@dataclass
class NewsSentiment:
    """Sentiment analysis result for news articles."""
    headline: str
    source: str
    url: str
    published_at: datetime
    sentiment: float
    relevance_score: float
    weight: float


@dataclass
class SocialMediaPost:
    """Social media post data."""
    author: str
    content: str
    likes: int
    shares: int
    comments: int
    sentiment: float
    timestamp: datetime
    engagement: int


@dataclass
class SocialMediaSentimentResult:
    """Social media sentiment analysis result."""
    symbol: str
    platform: str
    overall_sentiment: float
    sentiment_label: str
    total_posts: int
    bullish_count: int
    bearish_count: int
    total_engagement: int
    avg_engagement: float
    top_posts: List[Dict[str, Any]]
    sentiment_trend: str
    virality: float
    timestamp: datetime


@dataclass
class NewsSentimentResult:
    """News sentiment analysis result."""
    symbol: str
    overall_sentiment: float
    sentiment_label: str
    strength: float
    bullish_count: int
    bearish_count: int
    neutral_count: int
    total_articles: int
    articles: List[NewsSentiment]
    timestamp: datetime
    impact_score: float


@dataclass
class FearGreedIndex:
    """Fear & Greed index result."""
    index: float
    classification: str
    components: Dict[str, float]
    timestamp: datetime
    history: List[Dict[str, Any]]


@dataclass
class EarningsSentimentResult:
    """Earnings call sentiment analysis result."""
    symbol: str
    overall_sentiment: float
    sentiment_label: str
    key_points: List[Dict[str, Any]]
    confidence: float
    timestamp: datetime


class AdvancedSentimentAnalyzer:
    """Advanced sentiment analyzer with comprehensive market sentiment features."""
    
    def __init__(self):
        """Initialize the advanced sentiment analyzer."""
        self.sentiment_cache: Dict[str, Tuple[NewsSentimentResult, datetime]] = {}
        self.news_cache: Dict[str, Tuple[List[Dict], datetime]] = {}
        self.social_media_cache: Dict[str, Tuple[SocialMediaSentimentResult, datetime]] = {}
        self.fear_greed_cache: Optional[Tuple[FearGreedIndex, datetime]] = None
        
        # Source bias weights (lower = more credible)
        self.source_biases = {
            'Reuters': 0.05,
            'Bloomberg': 0.05,
            'AP': 0.05,
            'WSJ': 0.08,
            'CNN': 0.10,
            'CNBC': 0.10,
            'Twitter': 0.30,
            'Reddit': 0.25,
            'Yahoo Finance': 0.12,
            'MarketWatch': 0.15,
            'Seeking Alpha': 0.18
        }
        
        # Enhanced sentiment keywords
        self.positive_keywords = {
            'bullish', 'positive', 'strong', 'gain', 'profit', 'surge', 'jump',
            'rally', 'outperform', 'beat', 'growth', 'up', 'rise', 'advance',
            'boost', 'triumph', 'excellent', 'great', 'amazing', 'surge',
            'outstanding', 'breakthrough', 'momentum', 'optimistic', 'upside',
            'expansion', 'revenue', 'earnings', 'dividend', 'shareholder',
            'acquisition', 'partnership', 'innovation', 'leader', 'dominant'
        }
        
        self.negative_keywords = {
            'bearish', 'negative', 'weak', 'loss', 'fall', 'crash', 'plunge',
            'decline', 'underperform', 'miss', 'downturn', 'down', 'drop',
            'retreat', 'slump', 'disaster', 'terrible', 'awful', 'poor',
            'concern', 'risk', 'threat', 'lawsuit', 'investigation', 'fraud',
            'bankruptcy', 'default', 'delisting', 'suspension', 'violation',
            'regulatory', 'scrutiny', 'downgrade', 'cut', 'layoff', 'restructuring'
        }
    
    async def analyze_news_sentiment(
        self,
        symbol: str,
        news_articles: Optional[List[Dict]] = None,
        asset_class: Optional[str] = None
    ) -> NewsSentimentResult:
        """
        Analyze sentiment from news articles.
        
        Args:
            symbol: Asset symbol
            news_articles: List of news articles (if None, will fetch)
            asset_class: Asset class for class-specific sentiment
        
        Returns:
            NewsSentimentResult with comprehensive analysis
        """
        cache_key = f"news_{symbol}_{asset_class or 'default'}"
        
        # Check cache
        if cache_key in self.sentiment_cache:
            cached_result, cache_time = self.sentiment_cache[cache_key]
            if (datetime.now(tz.utc) - cache_time).total_seconds() < 3600:  # 1 hour cache
                return cached_result
        
        try:
            # Fetch news if not provided
            if news_articles is None:
                news_articles = await self._fetch_news(symbol)
            
            if not news_articles:
                return NewsSentimentResult(
                    symbol=symbol,
                    overall_sentiment=0.0,
                    sentiment_label=SentimentLabel.NEUTRAL.value,
                    strength=0.0,
                    bullish_count=0,
                    bearish_count=0,
                    neutral_count=0,
                    total_articles=0,
                    articles=[],
                    timestamp=datetime.now(tz.utc),
                    impact_score=0.0
                )
            
            # Analyze each article
            sentiments = []
            for article in news_articles:
                headline = article.get('title', '')
                description = article.get('description', '')
                full_text = f"{headline} {description}"
                
                # Use base sentiment analyzer for accuracy
                text_sentiment = base_sentiment.lexicon_score(full_text, asset_class)
                
                # Calculate relevance
                relevance = self._calculate_relevance(headline, symbol)
                
                # Get source bias
                source = article.get('source', 'Unknown')
                source_bias = self.source_biases.get(source, 0.15)
                
                # Calculate weight
                weight = relevance * (1 - source_bias)
                
                news_sentiment = NewsSentiment(
                    headline=headline,
                    source=source,
                    url=article.get('url', ''),
                    published_at=self._parse_datetime(article.get('publishedAt')),
                    sentiment=text_sentiment,
                    relevance_score=relevance,
                    weight=weight
                )
                sentiments.append(news_sentiment)
            
            # Calculate weighted overall sentiment
            total_weight = sum(s.weight for s in sentiments)
            overall_sentiment = (
                sum(s.sentiment * s.weight for s in sentiments) / total_weight
                if total_weight > 0 else 0
            )
            
            # Count sentiments
            bullish_count = sum(1 for s in sentiments if s.sentiment > 0.1)
            bearish_count = sum(1 for s in sentiments if s.sentiment < -0.1)
            neutral_count = sum(1 for s in sentiments if abs(s.sentiment) <= 0.1)
            
            # Calculate impact score
            impact_score = self._calculate_news_impact(sentiments)
            
            result = NewsSentimentResult(
                symbol=symbol,
                overall_sentiment=round(overall_sentiment, 2),
                sentiment_label=self._get_sentiment_label(overall_sentiment).value,
                strength=abs(overall_sentiment),
                bullish_count=bullish_count,
                bearish_count=bearish_count,
                neutral_count=neutral_count,
                total_articles=len(sentiments),
                articles=sentiments[:10],  # Top 10 articles
                timestamp=datetime.now(tz.utc),
                impact_score=round(impact_score, 2)
            )
            
            # Cache result
            self.sentiment_cache[cache_key] = (result, datetime.now(tz.utc))
            
            return result
            
        except Exception as e:
            return NewsSentimentResult(
                symbol=symbol,
                overall_sentiment=0.0,
                sentiment_label=SentimentLabel.NEUTRAL.value,
                strength=0.0,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
                total_articles=0,
                articles=[],
                timestamp=datetime.now(tz.utc),
                impact_score=0.0
            )
    
    async def analyze_social_media_sentiment(
        self,
        symbol: str,
        platform: str = Platform.TWITTER.value
    ) -> SocialMediaSentimentResult:
        """
        Analyze social media sentiment from various platforms.
        
        Args:
            symbol: Asset symbol
            platform: Social media platform
        
        Returns:
            SocialMediaSentimentResult with comprehensive analysis
        """
        cache_key = f"social_{symbol}_{platform}"
        
        # Check cache
        if cache_key in self.social_media_cache:
            cached_result, cache_time = self.social_media_cache[cache_key]
            if (datetime.now(tz.utc) - cache_time).total_seconds() < 1800:  # 30 min cache
                return cached_result
        
        try:
            # Fetch social media posts
            posts = await self._fetch_social_media_posts(symbol, platform)
            
            if not posts:
                return SocialMediaSentimentResult(
                    symbol=symbol,
                    platform=platform,
                    overall_sentiment=0.0,
                    sentiment_label=SentimentLabel.NEUTRAL.value,
                    total_posts=0,
                    bullish_count=0,
                    bearish_count=0,
                    total_engagement=0,
                    avg_engagement=0.0,
                    top_posts=[],
                    sentiment_trend='STABLE',
                    virality=0.0,
                    timestamp=datetime.now(tz.utc)
                )
            
            # Analyze each post
            sentiments = []
            for post in posts:
                text = post.get('text', '')
                text_sentiment = self._calculate_text_sentiment(text)
                
                engagement = (
                    post.get('likes', 0) + 
                    post.get('shares', 0) + 
                    post.get('comments', 0)
                )
                
                social_post = SocialMediaPost(
                    author=post.get('author', 'unknown'),
                    content=text,
                    likes=post.get('likes', 0),
                    shares=post.get('shares', 0),
                    comments=post.get('comments', 0),
                    sentiment=text_sentiment,
                    timestamp=self._parse_datetime(post.get('timestamp')),
                    engagement=engagement
                )
                sentiments.append(social_post)
            
            # Calculate engagement-weighted sentiment
            total_engagement = sum(s.engagement for s in sentiments)
            overall_sentiment = (
                sum(s.sentiment * s.engagement for s in sentiments) / total_engagement
                if total_engagement > 0 else
                sum(s.sentiment for s in sentiments) / len(sentiments)
            )
            
            # Count sentiments
            bullish_count = sum(1 for s in sentiments if s.sentiment > 0.1)
            bearish_count = sum(1 for s in sentiments if s.sentiment < -0.1)
            
            # Calculate average engagement
            avg_engagement = total_engagement / len(sentiments) if sentiments else 0
            
            # Get top posts by engagement
            top_posts = sorted(
                [{'author': s.author, 'content': s.content, 'sentiment': s.sentiment, 
                  'engagement': s.engagement, 'timestamp': s.timestamp.isoformat()}
                 for s in sentiments],
                key=lambda x: x['engagement'],
                reverse=True
            )[:5]
            
            # Calculate sentiment trend
            sentiment_trend = self._calculate_sentiment_trend(sentiments)
            
            # Calculate virality
            virality = self._calculate_virality(sentiments)
            
            result = SocialMediaSentimentResult(
                symbol=symbol,
                platform=platform,
                overall_sentiment=round(overall_sentiment, 2),
                sentiment_label=self._get_sentiment_label(overall_sentiment).value,
                total_posts=len(sentiments),
                bullish_count=bullish_count,
                bearish_count=bearish_count,
                total_engagement=total_engagement,
                avg_engagement=round(avg_engagement, 2),
                top_posts=top_posts,
                sentiment_trend=sentiment_trend,
                virality=round(virality, 2),
                timestamp=datetime.now(tz.utc)
            )
            
            # Cache result
            self.social_media_cache[cache_key] = (result, datetime.now(tz.utc))
            
            return result
            
        except Exception as e:
            return SocialMediaSentimentResult(
                symbol=symbol,
                platform=platform,
                overall_sentiment=0.0,
                sentiment_label=SentimentLabel.NEUTRAL.value,
                total_posts=0,
                bullish_count=0,
                bearish_count=0,
                total_engagement=0,
                avg_engagement=0.0,
                top_posts=[],
                sentiment_trend='STABLE',
                virality=0.0,
                timestamp=datetime.now(tz.utc)
            )
    
    async def calculate_fear_greed_index(self) -> FearGreedIndex:
        """
        Calculate Fear & Greed Index based on market components.
        
        Returns:
            FearGreedIndex with comprehensive analysis
        """
        # Check cache
        if self.fear_greed_cache:
            cached_result, cache_time = self.fear_greed_cache
            if (datetime.now(tz.utc) - cache_time).total_seconds() < 3600:  # 1 hour cache
                return cached_result
        
        try:
            # Calculate components (mock implementation - integrate with real data sources)
            components = {
                'market_momentum': self._get_random_sentiment(-1, 1),
                'volatility': self._get_random_sentiment(-1, 1),
                'volume': self._get_random_sentiment(-1, 1),
                'breadth': self._get_random_sentiment(-1, 1),
                'dominance': self._get_random_sentiment(-1, 1)
            }
            
            # Component weights
            weights = {
                'market_momentum': 0.25,
                'volatility': 0.25,
                'volume': 0.20,
                'breadth': 0.15,
                'dominance': 0.15
            }
            
            # Calculate weighted index
            index = sum(components[key] * weights[key] for key in components)
            
            # Normalize to 0-100 scale
            normalized_index = ((index + 1) / 2) * 100
            
            # Get historical data
            history = await self._get_fear_greed_history(7)
            
            result = FearGreedIndex(
                index=round(normalized_index, 2),
                classification=self._get_fear_greed_label(normalized_index).value,
                components=components,
                timestamp=datetime.now(tz.utc),
                history=history
            )
            
            # Cache result
            self.fear_greed_cache = (result, datetime.now(tz.utc))
            
            return result
            
        except Exception as e:
            return FearGreedIndex(
                index=50.0,
                classification=FearGreedLabel.NEUTRAL.value,
                components={},
                timestamp=datetime.now(tz.utc),
                history=[]
            )
    
    async def analyze_earnings_sentiment(
        self,
        symbol: str,
        transcript_text: str
    ) -> EarningsSentimentResult:
        """
        Analyze sentiment from earnings call transcripts.
        
        Args:
            symbol: Asset symbol
            transcript_text: Earnings call transcript text
        
        Returns:
            EarningsSentimentResult with comprehensive analysis
        """
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', transcript_text)
            
            # Define earnings-specific keywords
            keywords = {
                'growth': ['growth', 'expand', 'increase', 'beat', 'exceed', 'strong', 
                          'outperform', 'record', 'excellent', 'impressive', 'robust'],
                'decline': ['decline', 'decrease', 'miss', 'challenge', 'weak', 'difficult',
                           'struggle', 'pressure', 'concern', 'headwind', 'risk'],
                'neutral': ['maintain', 'stable', 'consistent', 'steady', 'flat', 'unchanged']
            }
            
            keyword_sentiments = {}
            
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                if not sentence_lower:
                    continue
                
                sentiment_score = 0.0
                
                # Check for growth keywords
                for keyword in keywords['growth']:
                    if keyword in sentence_lower:
                        sentiment_score += 0.2
                
                # Check for decline keywords
                for keyword in keywords['decline']:
                    if keyword in sentence_lower:
                        sentiment_score -= 0.2
                
                # Store if sentiment is significant
                if abs(sentiment_score) > 0:
                    text_preview = sentence[:50] + '...' if len(sentence) > 50 else sentence
                    keyword_sentiments[text_preview] = sentiment_score
            
            # Calculate overall sentiment
            if keyword_sentiments:
                overall_sentiment = sum(keyword_sentiments.values()) / len(keyword_sentiments)
            else:
                overall_sentiment = 0.0
            
            # Clamp to [-1, 1]
            overall_sentiment = max(-1.0, min(1.0, overall_sentiment))
            
            # Get key points
            key_points = sorted(
                [{'text': text, 'sentiment': score} for text, score in keyword_sentiments.items()],
                key=lambda x: abs(x['sentiment']),
                reverse=True
            )[:10]
            
            result = EarningsSentimentResult(
                symbol=symbol,
                overall_sentiment=round(overall_sentiment, 2),
                sentiment_label=self._get_sentiment_label(overall_sentiment).value,
                key_points=key_points,
                confidence=abs(overall_sentiment),
                timestamp=datetime.now(tz.utc)
            )
            
            return result
            
        except Exception as e:
            return EarningsSentimentResult(
                symbol=symbol,
                overall_sentiment=0.0,
                sentiment_label=SentimentLabel.NEUTRAL.value,
                key_points=[],
                confidence=0.0,
                timestamp=datetime.now(tz.utc)
            )
    
    def _calculate_text_sentiment(self, text: str) -> float:
        """Calculate sentiment from text using keyword analysis."""
        lower_text = text.lower()
        
        score = 0.0
        
        # Check positive keywords
        for keyword in self.positive_keywords:
            if keyword in lower_text:
                score += 0.1
        
        # Check negative keywords
        for keyword in self.negative_keywords:
            if keyword in lower_text:
                score -= 0.1
        
        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, score))
    
    def _calculate_relevance(self, headline: str, symbol: str) -> float:
        """Calculate relevance of news headline to symbol."""
        lower_headline = headline.lower()
        lower_symbol = symbol.lower()
        
        relevance = 0.0
        
        if lower_symbol in lower_headline:
            relevance += 1.0
        if 'stock' in lower_headline:
            relevance += 0.3
        if 'price' in lower_headline:
            relevance += 0.2
        if 'earnings' in lower_headline:
            relevance += 0.3
        if 'market' in lower_headline:
            relevance += 0.1
        
        return min(1.0, relevance)
    
    def _calculate_news_impact(self, sentiments: List[NewsSentiment]) -> float:
        """Calculate news impact score based on sentiment recency and strength."""
        if not sentiments:
            return 0.0
        
        # Average absolute sentiment
        avg_sentiment = sum(abs(s.sentiment) for s in sentiments) / len(sentiments)
        
        # Recent articles (last 24 hours)
        now = datetime.now(tz.utc)
        recent_count = sum(
            1 for s in sentiments
            if (now - s.published_at).total_seconds() < 86400
        )
        
        # Calculate impact score
        impact_score = (avg_sentiment * 0.6) + (recent_count / len(sentiments) * 0.4)
        
        return round(impact_score, 2)
    
    def _calculate_sentiment_trend(self, sentiments: List[SocialMediaPost]) -> str:
        """Calculate sentiment trend over time."""
        if len(sentiments) < 2:
            return 'STABLE'
        
        # Split into recent and older posts
        mid_point = len(sentiments) // 2
        recent = sentiments[:mid_point]
        older = sentiments[mid_point:]
        
        recent_avg = sum(s.sentiment for s in recent) / len(recent) if recent else 0
        older_avg = sum(s.sentiment for s in older) / len(older) if older else 0
        
        if recent_avg > older_avg + 0.1:
            return 'IMPROVING'
        elif recent_avg < older_avg - 0.1:
            return 'DETERIORATING'
        else:
            return 'STABLE'
    
    def _calculate_virality(self, sentiments: List[SocialMediaPost]) -> float:
        """Calculate virality score based on engagement."""
        if not sentiments:
            return 0.0
        
        avg_engagement = sum(s.engagement for s in sentiments) / len(sentiments)
        
        # Scale to 0-100
        virality = min(100.0, (avg_engagement / 1000) * 100)
        
        return round(virality, 2)
    
    def _get_sentiment_label(self, score: float) -> SentimentLabel:
        """Get sentiment label from score."""
        if score > 0.3:
            return SentimentLabel.VERY_BULLISH
        elif score > 0.1:
            return SentimentLabel.BULLISH
        elif score > -0.1:
            return SentimentLabel.NEUTRAL
        elif score > -0.3:
            return SentimentLabel.BEARISH
        else:
            return SentimentLabel.VERY_BEARISH
    
    def _get_fear_greed_label(self, index: float) -> FearGreedLabel:
        """Get Fear/Greed label from index."""
        if index >= 80:
            return FearGreedLabel.EXTREME_GREED
        elif index >= 60:
            return FearGreedLabel.GREED
        elif index >= 40:
            return FearGreedLabel.NEUTRAL
        elif index >= 20:
            return FearGreedLabel.FEAR
        else:
            return FearGreedLabel.EXTREME_FEAR
    
    async def _fetch_news(self, symbol: str) -> List[Dict]:
        """Fetch news articles for symbol (mock implementation)."""
        # In production, integrate with NewsAPI, Bloomberg, etc.
        # This is a mock implementation
        mock_news = [
            {
                'title': f'{symbol} Beats Earnings Expectations',
                'description': 'Strong quarterly results exceed analyst estimates',
                'source': 'Bloomberg',
                'url': f'https://example.com/{symbol.lower()}-earnings',
                'publishedAt': (datetime.now(tz.utc) - timedelta(hours=2)).isoformat()
            },
            {
                'title': f'Analysts Upgrade {symbol} Price Target',
                'description': 'Positive outlook with strong growth prospects',
                'source': 'Reuters',
                'url': f'https://example.com/{symbol.lower()}-upgrade',
                'publishedAt': (datetime.now(tz.utc) - timedelta(hours=4)).isoformat()
            },
            {
                'title': f'{symbol} Announces New Partnership',
                'description': 'Strategic alliance to expand market presence',
                'source': 'CNBC',
                'url': f'https://example.com/{symbol.lower()}-partnership',
                'publishedAt': (datetime.now(tz.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        return mock_news
    
    async def _fetch_social_media_posts(
        self,
        symbol: str,
        platform: str
    ) -> List[Dict]:
        """Fetch social media posts for symbol (mock implementation)."""
        # In production, integrate with Twitter API, Reddit API, etc.
        await asyncio.sleep(0)  # Make it truly async
        mock_posts = [
            {
                'author': 'trader123',
                'text': f'{symbol} looking bullish! Strong technical setup #trading',
                'likes': 150,
                'shares': 45,
                'comments': 23,
                'timestamp': datetime.now(tz.utc).isoformat()
            },
            {
                'author': 'analyst456',
                'text': f'{symbol} could see resistance at current levels, be careful',
                'likes': 89,
                'shares': 12,
                'comments': 18,
                'timestamp': (datetime.now(tz.utc) - timedelta(hours=2)).isoformat()
            },
            {
                'author': 'investor789',
                'text': f'Long {symbol} for the long term, great fundamentals',
                'likes': 234,
                'shares': 67,
                'comments': 45,
                'timestamp': (datetime.now(tz.utc) - timedelta(hours=4)).isoformat()
            }
        ]
        return mock_posts
    
    async def _get_fear_greed_history(self, days: int) -> List[Dict[str, Any]]:
        """Get Fear/Greed index history (mock implementation)."""
        history = []
        for i in range(days, -1, -1):
            date = datetime.now(tz.utc) - timedelta(days=i)
            history.append({
                'date': date.isoformat(),
                'index': round(50 + random.uniform(-15, 15), 2)
            })
        return history
    
    def _get_random_sentiment(self, min_val: float, max_val: float) -> float:
        """Get random sentiment value in range."""
        return random.uniform(min_val, max_val)
    
    def _parse_datetime(self, date_str: Optional[str]) -> datetime:
        """Parse datetime string to datetime object."""
        if not date_str:
            return datetime.now(tz.utc)
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                # Try common formats
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return datetime.now(tz.utc)
    
    async def calculate_sentiment_correlation(
        self,
        historical_data: pd.DataFrame,
        sentiment_history: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate correlation between sentiment and price movements.
        
        Args:
            historical_data: DataFrame with OHLC price data
            sentiment_history: List of sentiment history data
        
        Returns:
            Correlation coefficient between sentiment and price
        """
        if len(historical_data) < 2 or len(sentiment_history) < 2:
            return 0.0
        
        try:
            # Calculate price returns
            price_returns = []
            for i in range(1, len(historical_data)):
                ret = (historical_data['close'].iloc[i] - historical_data['close'].iloc[i-1]) / \
                      historical_data['close'].iloc[i-1]
                price_returns.append(ret)
            
            # Calculate sentiment changes
            sentiment_changes = []
            for i in range(1, len(sentiment_history)):
                change = sentiment_history[i]['index'] - sentiment_history[i-1]['index']
                sentiment_changes.append(change)
            
            if not price_returns or not sentiment_changes:
                return 0.0
            
            # Use minimum length
            min_length = min(len(price_returns), len(sentiment_changes))
            prices = price_returns[:min_length]
            sentiments = sentiment_changes[:min_length]
            
            # Calculate correlation
            if len(prices) < 2:
                return 0.0
            
            price_avg = np.mean(prices)
            sentiment_avg = np.mean(sentiments)
            
            numerator = sum((p - price_avg) * (s - sentiment_avg) for p, s in zip(prices, sentiments))
            price_sq_sum = sum((p - price_avg) ** 2 for p in prices)
            sentiment_sq_sum = sum((s - sentiment_avg) ** 2 for s in sentiments)
            
            denominator = np.sqrt(price_sq_sum * sentiment_sq_sum)
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return round(correlation, 3)
            
        except Exception as e:
            return 0.0
    
    def clear_cache(self):
        """Clear all sentiment caches."""
        self.sentiment_cache.clear()
        self.news_cache.clear()
        self.social_media_cache.clear()
        self.fear_greed_cache = None


# Global instance
advanced_sentiment_analyzer = AdvancedSentimentAnalyzer()


async def get_comprehensive_sentiment(
    symbol: str,
    asset_class: Optional[str] = None,
    include_social: bool = True,
    include_fear_greed: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive sentiment analysis for a symbol.
    
    Args:
        symbol: Asset symbol
        asset_class: Asset class for class-specific sentiment
        include_social: Include social media analysis
        include_fear_greed: Include Fear/Greed index
    
    Returns:
        Dictionary with comprehensive sentiment analysis
    """
    analyzer = AdvancedSentimentAnalyzer()
    
    # Analyze news sentiment
    news_sentiment = await analyzer.analyze_news_sentiment(symbol, asset_class=asset_class)
    
    result = {
        'symbol': symbol,
        'news_sentiment': {
            'overall_sentiment': news_sentiment.overall_sentiment,
            'sentiment_label': news_sentiment.sentiment_label,
            'strength': news_sentiment.strength,
            'bullish_count': news_sentiment.bullish_count,
            'bearish_count': news_sentiment.bearish_count,
            'total_articles': news_sentiment.total_articles,
            'impact_score': news_sentiment.impact_score
        }
    }
    
    # Add social media sentiment if requested
    if include_social:
        social_sentiment = await analyzer.analyze_social_media_sentiment(symbol)
        result['social_sentiment'] = {
            'overall_sentiment': social_sentiment.overall_sentiment,
            'sentiment_label': social_sentiment.sentiment_label,
            'total_posts': social_sentiment.total_posts,
            'virality': social_sentiment.virality,
            'sentiment_trend': social_sentiment.sentiment_trend
        }
    
    # Add Fear/Greed index if requested
    if include_fear_greed:
        fear_greed = await analyzer.calculate_fear_greed_index()
        result['fear_greed_index'] = {
            'index': fear_greed.index,
            'classification': fear_greed.classification,
            'components': fear_greed.components
        }
    
    # Calculate combined sentiment score
    combined_score = news_sentiment.overall_sentiment
    if include_social:
        combined_score = (combined_score + social_sentiment.overall_sentiment) / 2
    
    result['combined_sentiment'] = round(combined_score, 2)
    result['combined_label'] = analyzer._get_sentiment_label(combined_score).value
    result['timestamp'] = datetime.now(tz.utc).isoformat()
    
    return result