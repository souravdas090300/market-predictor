/**
 * Shared normalizers for market data returned by the FastAPI backend.
 *
 * Keeping these pure makes the API differences testable without a DOM or a
 * running backend, and lets the dashboard and asset pages render one shape.
 */

const SENTIMENT_WORDS = {
  positive: ['positive', 'bullish', 'very_bullish', 'up', 'gain'],
  negative: ['negative', 'bearish', 'very_bearish', 'down', 'loss']
};

function normalizeSentiment(value) {
  if (typeof value === 'number') {
    if (value > 0.1) return 'positive';
    if (value < -0.1) return 'negative';
    return 'neutral';
  }
  const label = String(value || '').toLowerCase();
  if (SENTIMENT_WORDS.positive.includes(label)) return 'positive';
  if (SENTIMENT_WORDS.negative.includes(label)) return 'negative';
  return 'neutral';
}

function firstValue(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null && value !== '') return value;
  }
  return undefined;
}

export function normalizeNewsResponse(payload = {}) {
  const rawArticles = payload.news || payload.articles || [];
  const articles = rawArticles.map((article, index) => ({
    id: firstValue(article.id, `${article.link || article.url || index}`),
    title: firstValue(article.title, article.headline, 'Untitled headline'),
    source: firstValue(article.source, article.provider, 'Unknown source'),
    date: firstValue(article.date, article.published, article.published_at, article.publishedAt, ''),
    url: firstValue(article.url, article.link, article.href, ''),
    sentiment: normalizeSentiment(article.sentiment)
  }));

  const summary = payload.sentiment_summary || {};
  const frontendSentiment = payload.sentiment || {};
  const overall = String(firstValue(summary.sentiment_trend, frontendSentiment.overall_sentiment, 'neutral') || 'neutral').toLowerCase();
  const score = firstValue(
    frontendSentiment.sentiment_score,
    summary.overall_sentiment,
    0
  );
  const knownLabels = ['bullish', 'bearish', 'neutral', 'very_bullish', 'very_bearish'];
  const overallLabel = knownLabels.includes(overall) ? overall : normalizeSentiment(overall);

  return {
    symbol: payload.symbol || '',
    articles,
    sentiment: {
      overall_sentiment: overallLabel,
      sentiment_score: Number(score) || 0,
      total_articles: summary.total_articles ?? articles.length,
      sources: payload.sources || []
    },
    fetchedAt: payload.fetched_at || null
  };
}

function formatTimestamp(timestamp, timeframe) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return String(timestamp || '');

  switch (timeframe) {
    case '24H':
    case '1W':
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    case '1M':
    case '6M':
    case '1Y':
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    case '5Y':
    case 'ALL':
      return date.toLocaleDateString('en-US', { year: '2-digit', month: 'short' });
    default:
      return date.toLocaleDateString();
  }
}

function toNumber(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function normalizePriceHistory(payload = {}, timeframe = '1M') {
  const historical = payload.historical || [];
  const current = payload.current || {};

  const chartData = historical.map((candle) => ({
    timestamp: formatTimestamp(candle.timestamp, timeframe),
    date: candle.timestamp || '',
    open: toNumber(candle.open),
    high: toNumber(candle.high),
    low: toNumber(candle.low),
    close: toNumber(candle.close),
    volume: toNumber(candle.volume),
    price: toNumber(candle.close)
  }));

  return {
    chartData,
    assetInfo: {
      name: payload.name || payload.symbol || '',
      price: toNumber(current.price),
      change24h: toNumber(current.change24h),
      changePercent: toNumber(current.changePercent),
      high: toNumber(current.high24h),
      low: toNumber(current.low24h),
      volume: toNumber(current.volume24h),
      marketCap: toNumber(current.marketCap)
    },
    dataSource: payload.data_source || 'unknown',
    quoteSource: current.source || 'unknown'
  };
}
