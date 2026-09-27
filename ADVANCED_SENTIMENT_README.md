# Advanced Sentiment Analysis Service

This document describes the advanced sentiment analysis service implementation for the market predictor platform.

## Overview

The advanced sentiment analysis service provides comprehensive market sentiment analysis with the following features:

- **News Sentiment Analysis**: Analyze news articles with source credibility weighting
- **Social Media Sentiment**: Track sentiment across Twitter, Reddit, and other platforms
- **Fear & Greed Index**: Calculate market-wide sentiment indicators
- **Earnings Call Analysis**: Extract sentiment from earnings call transcripts
- **Sentiment Correlation**: Analyze correlation between sentiment and price movements
- **Caching System**: Efficient caching to reduce API calls and improve performance

## API Endpoints

### 1. Comprehensive Sentiment Analysis
**Endpoint**: `POST /api/sentiment/advanced`

Get comprehensive sentiment analysis including news, social media, and Fear/Greed index.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "asset_class": "stock",
  "include_social": true,
  "include_fear_greed": true
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "news_sentiment": {
    "overall_sentiment": 0.35,
    "sentiment_label": "BULLISH",
    "strength": 0.35,
    "bullish_count": 8,
    "bearish_count": 2,
    "total_articles": 12,
    "impact_score": 0.72
  },
  "social_sentiment": {
    "overall_sentiment": 0.42,
    "sentiment_label": "BULLISH",
    "total_posts": 156,
    "virality": 45.2,
    "sentiment_trend": "IMPROVING"
  },
  "fear_greed_index": {
    "index": 65.0,
    "classification": "GREED",
    "components": {
      "market_momentum": 0.3,
      "volatility": -0.1,
      "volume": 0.2,
      "breadth": 0.15,
      "dominance": 0.1
    }
  },
  "combined_sentiment": 0.39,
  "combined_label": "BULLISH",
  "timestamp": "2026-09-27T12:00:00Z"
}
```

### 2. News Sentiment Analysis
**Endpoint**: `POST /api/sentiment/news`

Get detailed news sentiment analysis with article-level breakdown.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "asset_class": "stock"
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "overall_sentiment": 0.35,
  "sentiment_label": "BULLISH",
  "strength": 0.35,
  "bullish_count": 8,
  "bearish_count": 2,
  "neutral_count": 2,
  "total_articles": 12,
  "impact_score": 0.72,
  "articles": [
    {
      "headline": "AAPL Beats Earnings Expectations",
      "source": "Bloomberg",
      "sentiment": 0.8,
      "relevance_score": 1.0,
      "published_at": "2026-09-27T10:00:00Z"
    }
  ],
  "timestamp": "2026-09-27T12:00:00Z"
}
```

### 3. Social Media Sentiment
**Endpoint**: `POST /api/sentiment/social`

Get social media sentiment analysis from various platforms.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "platform": "twitter"
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "platform": "twitter",
  "overall_sentiment": 0.42,
  "sentiment_label": "BULLISH",
  "total_posts": 156,
  "bullish_count": 89,
  "bearish_count": 45,
  "total_engagement": 12450,
  "avg_engagement": 79.8,
  "top_posts": [
    {
      "author": "trader123",
      "content": "AAPL looking bullish! Strong technical setup",
      "sentiment": 0.5,
      "engagement": 450,
      "timestamp": "2026-09-27T11:30:00Z"
    }
  ],
  "sentiment_trend": "IMPROVING",
  "virality": 45.2,
  "timestamp": "2026-09-27T12:00:00Z"
}
```

### 4. Fear & Greed Index
**Endpoint**: `GET /api/sentiment/fear-greed`

Get current Fear & Greed index with historical data.

**Response**:
```json
{
  "index": 65.0,
  "classification": "GREED",
  "components": {
    "market_momentum": 0.3,
    "volatility": -0.1,
    "volume": 0.2,
    "breadth": 0.15,
    "dominance": 0.1
  },
  "history": [
    {
      "date": "2026-09-27T00:00:00Z",
      "index": 65.0
    },
    {
      "date": "2026-09-26T00:00:00Z",
      "index": 58.0
    }
  ],
  "timestamp": "2026-09-27T12:00:00Z"
}
```

### 5. Earnings Sentiment Analysis
**Endpoint**: `POST /api/sentiment/earnings`

Analyze sentiment from earnings call transcripts.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "transcript_text": "Our company showed strong growth this quarter. We exceeded expectations with record revenue..."
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "overall_sentiment": 0.45,
  "sentiment_label": "BULLISH",
  "key_points": [
    {
      "text": "Our company showed strong growth this quarter",
      "sentiment": 0.4
    },
    {
      "text": "We exceeded expectations with record revenue",
      "sentiment": 0.6
    }
  ],
  "confidence": 0.45,
  "timestamp": "2026-09-27T12:00:00Z"
}
```

## Sentiment Labels

### News/Social Media Sentiment
- **VERY_BULLISH**: Score > 0.3
- **BULLISH**: Score > 0.1
- **NEUTRAL**: Score between -0.1 and 0.1
- **BEARISH**: Score < -0.1
- **VERY_BEARISH**: Score < -0.3

### Fear & Greed Index
- **EXTREME_GREED**: Index ≥ 80
- **GREED**: Index ≥ 60
- **NEUTRAL**: Index ≥ 40
- **FEAR**: Index ≥ 20
- **EXTREME_FEAR**: Index < 20

## Source Credibility Weights

The service applies credibility weights to news sources:

| Source | Bias Weight | Credibility |
|--------|-------------|-------------|
| Reuters | 0.05 | Very High |
| Bloomberg | 0.05 | Very High |
| AP | 0.05 | Very High |
| WSJ | 0.08 | High |
| CNN | 0.10 | Medium-High |
| CNBC | 0.10 | Medium-High |
| Yahoo Finance | 0.12 | Medium |
| MarketWatch | 0.15 | Medium-Low |
| Seeking Alpha | 0.18 | Low-Medium |
| Twitter | 0.30 | Low |
| Reddit | 0.25 | Low |

Lower bias weight = higher credibility in sentiment calculations.

## Usage Examples

### Python API Usage

```python
import asyncio
from app.services.advanced_sentiment import AdvancedSentimentAnalyzer, get_comprehensive_sentiment

# Initialize analyzer
analyzer = AdvancedSentimentAnalyzer()

# Analyze news sentiment
news_result = await analyzer.analyze_news_sentiment('AAPL', asset_class='stock')
print(f"News Sentiment: {news_result.overall_sentiment} ({news_result.sentiment_label})")

# Analyze social media sentiment
social_result = await analyzer.analyze_social_media_sentiment('AAPL', platform='twitter')
print(f"Social Sentiment: {social_result.overall_sentiment} ({social_result.sentiment_label})")
print(f"Virality Score: {social_result.virality}")

# Get Fear & Greed index
fear_greed = await analyzer.calculate_fear_greed_index()
print(f"Fear/Greed Index: {fear_greed.index} ({fear_greed.classification})")

# Analyze earnings transcript
earnings_result = await analyzer.analyze_earnings_sentiment(
    'AAPL', 
    "Strong growth this quarter with record revenue..."
)
print(f"Earnings Sentiment: {earnings_result.overall_sentiment}")

# Get comprehensive sentiment
comprehensive = await get_comprehensive_sentiment('AAPL', include_social=True)
print(f"Combined Sentiment: {comprehensive['combined_sentiment']}")
```

### Sentiment Correlation Analysis

```python
import pandas as pd
from app.services.advanced_sentiment import AdvancedSentimentAnalyzer

# Load historical price data
price_data = pd.read_csv('historical_prices.csv')

# Create sentiment history
sentiment_history = [
    {'date': '2026-09-27', 'index': 65.0},
    {'date': '2026-09-26', 'index': 58.0},
    # ... more data
]

# Calculate correlation
analyzer = AdvancedSentimentAnalyzer()
correlation = await analyzer.calculate_sentiment_correlation(price_data, sentiment_history)
print(f"Sentiment-Price Correlation: {correlation}")
```

## Performance Metrics

### News Impact Score
The news impact score combines:
- **Average Sentiment Strength**: 60% weight
- **Recency Factor**: 40% weight (recent articles within 24 hours)

### Social Media Virality
Virality score (0-100) based on:
- Average engagement (likes, shares, comments)
- Scaled to 0-100 range

### Sentiment Trend
Trend analysis classifies sentiment as:
- **IMPROVING**: Recent sentiment > older sentiment + 0.1
- **DETERIORATING**: Recent sentiment < older sentiment - 0.1
- **STABLE**: Otherwise

## Caching Strategy

The service implements intelligent caching:

- **News Sentiment**: 1 hour cache
- **Social Media Sentiment**: 30 minute cache
- **Fear/Greed Index**: 1 hour cache

Cache can be cleared manually:
```python
analyzer = AdvancedSentimentAnalyzer()
analyzer.clear_cache()
```

## Integration with Existing Services

The advanced sentiment service integrates with the existing sentiment analyzer:

```python
from app.services import sentiment as base_sentiment

# Uses base sentiment for accurate text analysis
# Leverages existing finance lexicon
# Supports class-specific sentiment (stock, crypto, commodity, forex)
```

## Customization

### Adding Custom Keywords

```python
analyzer = AdvancedSentimentAnalyzer()

# Add custom positive keywords
analyzer.positive_keywords.update(['breakthrough', 'innovation', 'revolutionary'])

# Add custom negative keywords
analyzer.negative_keywords.update(['scandal', 'controversy', 'lawsuit'])
```

### Adding Custom Sources

```python
analyzer = AdvancedSentimentAnalyzer()

# Add custom source bias
analyzer.source_biases['CustomSource'] = 0.12
```

## Best Practices

1. **Asset Class Specificity**: Always specify asset_class for accurate sentiment
2. **Cache Management**: Clear cache periodically for fresh data
3. **Source Verification**: Rely more on high-credibility sources
4. **Trend Analysis**: Consider sentiment trends, not just current values
5. **Correlation Context**: Use sentiment correlation with price history carefully
6. **Error Handling**: Always handle exceptions from API calls

## Testing

The service includes comprehensive test coverage:

```bash
# Run all advanced sentiment tests
python -m pytest tests/test_advanced_sentiment.py -v

# Run specific test
python -m pytest tests/test_advanced_sentiment.py::test_news_sentiment_analysis -v
```

## Performance Considerations

- **Async Operations**: All analysis functions are async for better performance
- **Caching**: Reduces redundant API calls and improves response times
- **Batch Processing**: Can analyze multiple articles/posts efficiently
- **Memory Usage**: Caching uses moderate memory; clear cache if needed

## Future Enhancements

Potential future improvements:

- Real-time sentiment streaming
- Machine learning-based sentiment models
- Multi-language support
- Advanced NLP techniques (BERT, GPT integration)
- Custom sentiment model training
- Real-time alert system for sentiment changes
- Sentiment-based trading signals
- Integration with more social platforms (LinkedIn, Facebook)
- Image and video sentiment analysis

## Integration Notes

The advanced sentiment service is designed to work seamlessly with:

- **Existing Sentiment Service**: Uses base sentiment for text analysis
- **News Service**: Can integrate with existing news fetching
- **API Infrastructure**: Follows existing rate limiting and security patterns
- **Data Models**: Compatible with existing data structures

## Support

For issues or questions about the advanced sentiment analysis service, please refer to the main project documentation or create an issue in the project repository.