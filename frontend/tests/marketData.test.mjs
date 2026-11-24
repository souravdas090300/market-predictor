import assert from 'node:assert/strict';
import test from 'node:test';

import { normalizeNewsResponse, normalizePriceHistory } from '../lib/marketData.mjs';

test('normalizes Yahoo-style news payloads for the dashboard', () => {
  const result = normalizeNewsResponse({
    symbol: 'AAPL',
    news: [{
      title: 'Apple shares surge on strong growth',
      source: 'Yahoo Finance',
      published: '2026-11-24T10:00:00Z',
      link: 'https://finance.yahoo.com/news/aapl',
      sentiment: 'positive'
    }],
    sentiment_summary: { sentiment_trend: 'bullish', overall_sentiment: 0.62, total_articles: 1 },
    sentiment: { overall_sentiment: 'bullish', sentiment_score: 0.62 },
    sources: ['Yahoo Finance']
  });

  assert.equal(result.articles.length, 1);
  assert.equal(result.articles[0].source, 'Yahoo Finance');
  assert.equal(result.articles[0].url, 'https://finance.yahoo.com/news/aapl');
  assert.equal(result.articles[0].sentiment, 'positive');
  assert.equal(result.sentiment.overall_sentiment, 'bullish');
  assert.equal(result.sentiment.sentiment_score, 0.62);
});

test('normalizes CoinGecko candle payloads and exposes the provider', () => {
  const result = normalizePriceHistory({
    symbol: 'BTC-USD',
    data_source: 'coingecko',
    current: {
      price: 65000,
      change24h: 1200,
      changePercent: 1.88,
      high24h: 66000,
      low24h: 64000,
      volume24h: 28000000000,
      marketCap: 1280000000000,
      source: 'coingecko'
    },
    historical: [{
      timestamp: '2026-11-24T00:00:00Z',
      open: 64000,
      high: 65500,
      low: 63800,
      close: 65000,
      volume: 1000
    }]
  }, '1M');

  assert.equal(result.dataSource, 'coingecko');
  assert.equal(result.assetInfo.price, 65000);
  assert.equal(result.chartData.length, 1);
  assert.equal(result.chartData[0].price, 65000);
  assert.equal(result.chartData[0].volume, 1000);
});
