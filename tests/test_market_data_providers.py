"""Offline tests for Yahoo news and CoinGecko integrations."""
import asyncio
import time
from types import SimpleNamespace

import pytest

from app.core import coingecko, data
from app.services import advanced_sentiment, news
from app.routes import assets_historical, phase1_5, phase11_18


def test_yahoo_news_fetch_normalizes_yfinance_payload(monkeypatch):
    published = int(time.time()) - 3600
    fake_items = [{
        'title': 'Apple shares surge on strong growth',
        'publisher': 'Yahoo Finance',
        'link': 'https://finance.yahoo.com/news/aapl-surges',
        'providerPublishTime': published,
        'summary': '<p>Strong quarterly growth lifts shares.</p>'
    }]

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol
            self.news = fake_items

    monkeypatch.setattr(news.yfinance, 'Ticker', FakeTicker)
    monkeypatch.setattr(news.NewsAggregator, '_fetch_google_news', lambda self, terms, limit: [])
    monkeypatch.setattr(news.NewsAggregator, '_fetch_bloomberg_news', lambda self, terms, limit: [])
    news.clear_cache()

    articles = news.NewsAggregator().fetch_news('AAPL', 'stock', 5)

    assert len(articles) == 1
    assert articles[0]['source'] == 'Yahoo Finance'
    assert articles[0]['provider'] == 'Yahoo Finance'
    assert '<p>' not in articles[0]['summary']
    assert articles[0]['published'].endswith('+00:00')


def test_get_news_with_sentiment_exposes_frontend_shape(monkeypatch):
    articles = [{
        'title': 'Nvidia surges to record high',
        'summary': 'Strong growth and bullish guidance',
        'source': 'Yahoo Finance',
        'link': 'https://example.com/nvda',
        'published': '2026-11-24T10:00:00+00:00'
    }]
    monkeypatch.setattr(news.NewsAggregator, 'fetch_news', lambda self, *args: articles)

    result = news.get_news_with_sentiment('NVDA', 'stock', 10)

    assert result['news'][0]['sentiment'] == 'positive'
    assert result['articles'] == result['news']
    assert result['sentiment']['total_articles'] == 1
    assert result['sentiment']['sentiment_trend'] in {'bullish', 'neutral', 'bearish'}


def test_advanced_sentiment_uses_real_news_service(monkeypatch):
    fetched = [{
        'title': 'Tesla rallies after upgrade',
        'summary': 'Analysts upgraded the stock',
        'source': 'Yahoo Finance',
        'link': 'https://example.com/tsla',
        'published': '2026-11-24T10:00:00+00:00'
    }]
    monkeypatch.setattr(news.NewsAggregator, 'fetch_news', lambda self, *args: fetched)

    result = asyncio.run(
        advanced_sentiment.AdvancedSentimentAnalyzer()._fetch_news('TSLA')
    )

    assert result[0]['description'] == 'Analysts upgraded the stock'
    assert result[0]['url'] == 'https://example.com/tsla'
    assert result[0]['source'] == 'Yahoo Finance'


def test_news_endpoint_returns_real_payload_not_demo(monkeypatch):
    from fastapi.testclient import TestClient
    from app.api import app

    monkeypatch.setattr(
        phase1_5.news_service,
        'get_news_with_sentiment',
        lambda symbol, asset_class, max_articles: {
            'symbol': symbol,
            'news': [{'title': 'Real Yahoo headline', 'source': 'Yahoo Finance', 'date': '2026-11-24T10:00:00Z'}],
            'articles': [{'title': 'Real Yahoo headline', 'source': 'Yahoo Finance', 'date': '2026-11-24T10:00:00Z'}],
            'sentiment': {
                'total_articles': 1, 'positive': 1, 'negative': 0, 'neutral': 0,
                'overall_sentiment': 0.5, 'sentiment_trend': 'bullish', 'confidence': 50
            },
            'sources': ['Yahoo Finance'],
            'fetched_at': '2026-11-24T10:00:00Z'
        }
    )

    response = TestClient(app).get('/api/news/AAPL')

    assert response.status_code == 200
    payload = response.json()
    assert payload['news'][0]['title'] == 'Real Yahoo headline'
    assert 'Reports Strong Q3 Earnings' not in response.text
    assert payload['sentiment']['overall_sentiment'] == 'bullish'


def test_coingecko_auth_headers_and_price_params(monkeypatch):
    monkeypatch.setenv('COINGECKO_API_TYPE', 'demo')
    client = coingecko.CoinGeckoClient(api_key='demo-key')
    assert client.base_url == coingecko.CoinGeckoClient.PUBLIC_BASE_URL
    assert client.session.headers['x-cg-demo-api-key'] == 'demo-key'

    pro_client = coingecko.CoinGeckoClient(api_key='pro-key', api_type='pro')
    assert pro_client.base_url == coingecko.CoinGeckoClient.PRO_BASE_URL
    assert pro_client.session.headers['x-cg-pro-api-key'] == 'pro-key'

    captured = {}

    def fake_get(endpoint, params=None, use_cache=True):
        captured.update({'endpoint': endpoint, 'params': params})
        return {'bitcoin': {'usd': 65000}}

    monkeypatch.setattr(client, '_get', fake_get)
    client.get_coin_price('bitcoin')

    assert captured['endpoint'] == '/simple/price'
    assert captured['params']['ids'] == 'bitcoin'


def test_coingecko_ohlc_and_market_chart_are_normalized(monkeypatch):
    client = coingecko.CoinGeckoClient()
    candles = [[1700000000000, 100, 110, 95, 105]]
    monkeypatch.setattr(client, 'get_coin_ohlc', lambda coin_id, days: candles)
    monkeypatch.setattr(client, 'get_coin_market_data', lambda coin_id, days, vs_currency='usd': {})

    result = client.get_coin_history('bitcoin', '1W')

    assert len(result) == 1
    assert result[0]['close'] == 105
    assert result[0]['volume'] == 0

    aggregated = coingecko.market_chart_to_ohlc({
        'prices': [[1700000000000, 100], [1700000300000, 110], [1700000600000, 105]],
        'total_volumes': [[1700000000000, 10], [1700000600000, 20]]
    }, '1M')

    assert len(aggregated) == 1
    assert aggregated[0]['open'] == 100
    assert aggregated[0]['high'] == 110
    assert aggregated[0]['close'] == 105
    assert aggregated[0]['volume'] == 30


def test_crypto_quote_uses_coin_id_when_outside_top_250(monkeypatch):
    data._crypto_cache.clear()
    data._crypto_market_cache.clear()
    coingecko.clear_client_cache()

    fake_client = SimpleNamespace(
        get_top_coins=lambda **kwargs: [{'symbol': 'eth', 'current_price': 3000}],
        get_coin_price=lambda coin_id: {
            'cardano': {'usd': 0.5, 'usd_24h_change': 2.0, 'usd_market_cap': 18000000000, 'usd_24h_vol': 400000000}
        }
    )
    monkeypatch.setattr(data.coingecko, 'get_coingecko_client', lambda: fake_client)
    monkeypatch.setattr(data.coingecko, 'resolve_coin_id', lambda symbol, client=None: 'cardano')
    monkeypatch.setattr(data, 'get_live_quote', lambda symbol: pytest.fail('Yahoo fallback should not be used'))

    quote = data.get_crypto_quote('ADA-USD')

    assert quote['source'] == 'coingecko'
    assert quote['price'] == 0.5
    assert quote['coingecko_id'] == 'cardano'


def test_price_history_uses_coingecko(monkeypatch):
    from fastapi.testclient import TestClient
    from app.api import app

    assets_historical.price_cache.clear()
    candles = [{
        'timestamp': '2026-11-24T00:00:00Z',
        'open': 64000, 'high': 65000, 'low': 63500, 'close': 64500, 'volume': 1000
    }]
    monkeypatch.setattr(assets_historical.coingecko, 'get_coin_history', lambda symbol, timeframe: candles)

    async def fake_current_price(symbol, category):
        return {'price': 64500, 'change24h': 500, 'changePercent': 0.78, 'high24h': 65000,
                'low24h': 63500, 'volume24h': 1000, 'marketCap': 1000000000, 'source': 'coingecko'}

    monkeypatch.setattr(assets_historical, 'get_current_price', fake_current_price)

    response = TestClient(app).get('/api/v1/assets/price-history/BTC-USD?timeframe=24H&category=crypto')

    assert response.status_code == 200
    payload = response.json()
    assert payload['data_source'] == 'coingecko'
    assert payload['historical'] == candles


def test_v2_news_sentiment_uses_real_service(monkeypatch):
    from fastapi.testclient import TestClient
    from app.api import app

    async def fake_sentiment(symbol):
        return {'symbol': symbol, 'overall_sentiment': 0.42, 'total_articles': 2}

    monkeypatch.setattr(phase11_18.advanced_sentiment, 'get_news_sentiment', fake_sentiment)

    response = TestClient(app).get('/api/v2/sentiment/news/AAPL')

    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['sentiment']['total_articles'] == 2
