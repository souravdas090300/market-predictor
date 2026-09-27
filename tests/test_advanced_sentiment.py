"""Tests for the advanced sentiment analysis service."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone as tz
from app.services import advanced_sentiment


def test_advanced_sentiment_analyzer_initialization():
    """Test advanced sentiment analyzer initialization."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    assert analyzer.sentiment_cache == {}
    assert analyzer.news_cache == {}
    assert analyzer.social_media_cache == {}
    assert analyzer.fear_greed_cache is None
    assert 'Reuters' in analyzer.source_biases
    assert 'Bloomberg' in analyzer.source_biases


def test_calculate_text_sentiment():
    """Test text sentiment calculation."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # Positive text
    positive_text = "Strong growth and excellent profits for the company"
    sentiment = analyzer._calculate_text_sentiment(positive_text)
    assert sentiment > 0
    
    # Negative text
    negative_text = "Terrible losses and weak performance"
    sentiment = analyzer._calculate_text_sentiment(negative_text)
    assert sentiment < 0
    
    # Neutral text
    neutral_text = "The company reported its quarterly results"
    sentiment = analyzer._calculate_text_sentiment(neutral_text)
    assert -0.5 <= sentiment <= 0.5


def test_calculate_relevance():
    """Test news relevance calculation."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # High relevance
    high_relevance = analyzer._calculate_relevance("AAPL stock price surges", "AAPL")
    assert high_relevance > 0.8
    
    # Low relevance
    low_relevance = analyzer._calculate_relevance("Market analysis report", "AAPL")
    assert low_relevance < 0.5


def test_get_sentiment_label():
    """Test sentiment label mapping."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    assert analyzer._get_sentiment_label(0.5) == advanced_sentiment.SentimentLabel.VERY_BULLISH
    assert analyzer._get_sentiment_label(0.2) == advanced_sentiment.SentimentLabel.BULLISH
    assert analyzer._get_sentiment_label(0.0) == advanced_sentiment.SentimentLabel.NEUTRAL
    assert analyzer._get_sentiment_label(-0.2) == advanced_sentiment.SentimentLabel.BEARISH
    assert analyzer._get_sentiment_label(-0.5) == advanced_sentiment.SentimentLabel.VERY_BEARISH


def test_get_fear_greed_label():
    """Test Fear/Greed label mapping."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    assert analyzer._get_fear_greed_label(85) == advanced_sentiment.FearGreedLabel.EXTREME_GREED
    assert analyzer._get_fear_greed_label(65) == advanced_sentiment.FearGreedLabel.GREED
    assert analyzer._get_fear_greed_label(50) == advanced_sentiment.FearGreedLabel.NEUTRAL
    assert analyzer._get_fear_greed_label(30) == advanced_sentiment.FearGreedLabel.FEAR
    assert analyzer._get_fear_greed_label(10) == advanced_sentiment.FearGreedLabel.EXTREME_FEAR


def test_news_sentiment_analysis():
    """Test news sentiment analysis."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # Mock news articles
    news_articles = [
        {
            'title': 'AAPL Beats Earnings Expectations',
            'description': 'Strong quarterly results',
            'source': 'Bloomberg',
            'url': 'https://example.com/news1',
            'publishedAt': datetime.now(tz.utc).isoformat()
        },
        {
            'title': 'Market concerns about tech sector',
            'description': 'Investors worried about valuations',
            'source': 'Reuters',
            'url': 'https://example.com/news2',
            'publishedAt': (datetime.now(tz.utc) - timedelta(hours=4)).isoformat()
        }
    ]
    
    result = asyncio.run(analyzer.analyze_news_sentiment('AAPL', news_articles))
    
    assert result.symbol == 'AAPL'
    assert result.total_articles == 2
    assert result.sentiment_label in ['VERY_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'VERY_BEARISH']
    assert result.impact_score >= 0


def test_news_sentiment_with_no_articles():
    """Test news sentiment analysis with no articles."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    result = asyncio.run(analyzer.analyze_news_sentiment('AAPL', []))
    
    assert result.symbol == 'AAPL'
    assert result.total_articles == 0
    assert result.overall_sentiment == 0.0
    assert result.sentiment_label == 'NEUTRAL'


def test_social_media_sentiment_analysis():
    """Test social media sentiment analysis."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # Mock social media posts
    mock_posts = [
        {
            'author': 'trader123',
            'text': 'AAPL looking bullish! Strong technical setup',
            'likes': 150,
            'shares': 45,
            'comments': 23,
            'timestamp': datetime.now(tz.utc).isoformat()
        },
        {
            'author': 'analyst456',
            'text': 'AAPL could see resistance at current levels',
            'likes': 89,
            'shares': 12,
            'comments': 18,
            'timestamp': (datetime.now(tz.utc) - timedelta(hours=2)).isoformat()
        }
    ]
    
    # Patch the fetch method with async function
    async def mock_fetch(symbol, platform):
        return mock_posts
    
    original_fetch = analyzer._fetch_social_media_posts
    analyzer._fetch_social_media_posts = mock_fetch
    
    result = asyncio.run(analyzer.analyze_social_media_sentiment('AAPL'))
    
    assert result.symbol == 'AAPL'
    assert result.total_posts == 2
    assert result.sentiment_label in ['VERY_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'VERY_BEARISH']
    assert result.virality >= 0
    
    # Restore original method
    analyzer._fetch_social_media_posts = original_fetch


def test_fear_greed_index_calculation():
    """Test Fear & Greed index calculation."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    result = asyncio.run(analyzer.calculate_fear_greed_index())
    
    assert 0 <= result.index <= 100
    assert result.classification in ['EXTREME_GREED', 'GREED', 'NEUTRAL', 'FEAR', 'EXTREME_FEAR']
    assert len(result.history) > 0
    assert 'market_momentum' in result.components


def test_earnings_sentiment_analysis():
    """Test earnings call sentiment analysis."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    transcript = """
    Our company showed strong growth this quarter. We exceeded expectations 
    with record revenue. However, we face some challenges in the supply chain. 
    Despite the headwinds, we remain optimistic about the future. Our profit 
    margins improved significantly.
    """
    
    result = asyncio.run(analyzer.analyze_earnings_sentiment('AAPL', transcript))
    
    assert result.symbol == 'AAPL'
    assert result.sentiment_label in ['VERY_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'VERY_BEARISH']
    assert 0 <= result.confidence <= 1
    assert isinstance(result.key_points, list)


def test_sentiment_correlation_calculation():
    """Test sentiment-price correlation calculation."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # Create mock price data
    dates = pd.date_range(end=datetime.now(tz.utc), periods=50)
    prices = np.cumprod(1 + np.random.normal(0.001, 0.02, 50)) * 100
    historical_data = pd.DataFrame({
        'close': prices,
        'open': prices * (1 + np.random.normal(0, 0.005, 50)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.01, 50))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.01, 50)))
    }, index=dates)
    
    # Create mock sentiment history
    sentiment_history = [
        {'date': dates[i].isoformat(), 'index': 50 + np.random.uniform(-10, 10)}
        for i in range(50)
    ]
    
    correlation = asyncio.run(analyzer.calculate_sentiment_correlation(historical_data, sentiment_history))
    
    assert -1 <= correlation <= 1


def test_cache_functionality():
    """Test sentiment cache functionality."""
    import asyncio
    
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # First call should populate cache
    result1 = asyncio.run(analyzer.analyze_news_sentiment('AAPL', []))
    
    # Second call should use cache
    result2 = asyncio.run(analyzer.analyze_news_sentiment('AAPL', []))
    
    assert result1.overall_sentiment == result2.overall_sentiment
    
    # Clear cache
    analyzer.clear_cache()
    assert analyzer.sentiment_cache == {}


def test_sentiment_trend_calculation():
    """Test sentiment trend calculation."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # Create posts with improving sentiment
    posts = [
        advanced_sentiment.SocialMediaPost(
            author='user1', content='Negative sentiment', likes=10, shares=5,
            comments=2, sentiment=-0.5, timestamp=datetime.now(tz.utc), engagement=17
        ),
        advanced_sentiment.SocialMediaPost(
            author='user2', content='Positive sentiment', likes=20, shares=10,
            comments=5, sentiment=0.5, timestamp=datetime.now(tz.utc), engagement=35
        )
    ]
    
    trend = analyzer._calculate_sentiment_trend(posts)
    assert trend in ['IMPROVING', 'DETERIORATING', 'STABLE']


def test_virality_calculation():
    """Test virality score calculation."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # High engagement posts
    high_virality_posts = [
        advanced_sentiment.SocialMediaPost(
            author='user1', content='Viral content', likes=1000, shares=500,
            comments=200, sentiment=0.5, timestamp=datetime.now(tz.utc), engagement=1700
        )
    ]
    
    virality = analyzer._calculate_virality(high_virality_posts)
    assert virality > 50  # Should be high due to high engagement
    
    # Low engagement posts
    low_virality_posts = [
        advanced_sentiment.SocialMediaPost(
            author='user1', content='Normal content', likes=5, shares=2,
            comments=1, sentiment=0.0, timestamp=datetime.now(tz.utc), engagement=8
        )
    ]
    
    virality = analyzer._calculate_virality(low_virality_posts)
    assert virality < 10  # Should be low due to low engagement


def test_news_impact_calculation():
    """Test news impact score calculation."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # High impact news (recent, strong sentiment)
    high_impact_news = [
        advanced_sentiment.NewsSentiment(
            headline='Major breakthrough announced',
            source='Reuters',
            url='https://example.com',
            published_at=datetime.now(tz.utc),
            sentiment=0.8,
            relevance_score=1.0,
            weight=0.9
        )
    ]
    
    impact = analyzer._calculate_news_impact(high_impact_news)
    assert impact > 0.5  # Should be high


def test_comprehensive_sentiment():
    """Test comprehensive sentiment analysis function."""
    import asyncio
    
    result = asyncio.run(advanced_sentiment.get_comprehensive_sentiment(
        symbol='AAPL',
        asset_class='stock',
        include_social=True,
        include_fear_greed=True
    ))
    
    assert result['symbol'] == 'AAPL'
    assert 'news_sentiment' in result
    assert 'social_sentiment' in result
    assert 'fear_greed_index' in result
    assert 'combined_sentiment' in result
    assert 'combined_label' in result


def test_parse_datetime():
    """Test datetime parsing."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # ISO format
    iso_dt = analyzer._parse_datetime('2026-09-27T12:00:00Z')
    assert isinstance(iso_dt, datetime)
    
    # String format
    str_dt = analyzer._parse_datetime('2026-09-27 12:00:00')
    assert isinstance(str_dt, datetime)
    
    # None/invalid
    invalid_dt = analyzer._parse_datetime(None)
    assert isinstance(invalid_dt, datetime)


def test_source_bias_weights():
    """Test source bias weights."""
    analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
    
    # More credible sources should have lower bias
    assert analyzer.source_biases['Reuters'] < analyzer.source_biases['Twitter']
    assert analyzer.source_biases['Bloomberg'] < analyzer.source_biases['Reddit']


def test_sentiment_enums():
    """Test sentiment enum values."""
    assert advanced_sentiment.SentimentLabel.VERY_BULLISH.value == 'VERY_BULLISH'
    assert advanced_sentiment.SentimentLabel.BULLISH.value == 'BULLISH'
    assert advanced_sentiment.SentimentLabel.NEUTRAL.value == 'NEUTRAL'
    assert advanced_sentiment.SentimentLabel.BEARISH.value == 'BEARISH'
    assert advanced_sentiment.SentimentLabel.VERY_BEARISH.value == 'VERY_BEARISH'
    
    assert advanced_sentiment.FearGreedLabel.EXTREME_GREED.value == 'EXTREME_GREED'
    assert advanced_sentiment.FearGreedLabel.GREED.value == 'GREED'
    assert advanced_sentiment.FearGreedLabel.NEUTRAL.value == 'NEUTRAL'
    assert advanced_sentiment.FearGreedLabel.FEAR.value == 'FEAR'
    assert advanced_sentiment.FearGreedLabel.EXTREME_FEAR.value == 'EXTREME_FEAR'


def test_dataclass_instances():
    """Test dataclass instance creation."""
    news_sentiment = advanced_sentiment.NewsSentiment(
        headline='Test headline',
        source='Test Source',
        url='https://example.com',
        published_at=datetime.now(tz.utc),
        sentiment=0.5,
        relevance_score=0.8,
        weight=0.75
    )
    
    assert news_sentiment.headline == 'Test headline'
    assert news_sentiment.sentiment == 0.5
    
    social_post = advanced_sentiment.SocialMediaPost(
        author='testuser',
        content='Test content',
        likes=100,
        shares=50,
        comments=25,
        sentiment=0.3,
        timestamp=datetime.now(tz.utc),
        engagement=175
    )
    
    assert social_post.author == 'testuser'
    assert social_post.engagement == 175


if __name__ == "__main__":
    pytest.main([__file__, "-v"])