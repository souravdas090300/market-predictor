'use client';

import { useState, useEffect } from 'react';
import { Newspaper, Filter, Search, ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function NewsPage() {
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState('AAPL');
  const [assetClass, setAssetClass] = useState('stock');
  const [maxArticles, setMaxArticles] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'negative' | 'neutral'>('all');
  const [news, setNews] = useState<any[]>([]);

  useEffect(() => {
    loadNews();
  }, [symbol, assetClass, maxArticles]);

  const loadNews = async () => {
    setLoading(true);
    
    // Simulate news loading
    setTimeout(() => {
      const mockNews = Array.from({ length: maxArticles }, (_, i) => ({
        title: [
          'Apple Stock Surges on Strong Earnings Report',
          'Tech Sector Faces Headwinds Amid Fed Rate Hikes',
          'Analysts Upgrade AAPL Price Target to $200',
          'Apple Announces New Product Line, Investors React',
          'Market Volatility Increases as Investors Await CPI Data',
          'iPhone Sales Beat Expectations in Q3',
          'Apple Faces Supply Chain Challenges in China',
          'Dividend Increase Announced for Shareholders',
          'Competitor Launches Rival Product, Market Share Battle Looms',
          'Apple Stock Shows Resilience Amid Market Downturn',
        ][i % 10],
        link: '#',
        source: ['Reuters', 'Bloomberg', 'CNBC', 'WSJ', 'FT'][i % 5],
        published_date: new Date(Date.now() - i * 3600000).toISOString(),
        sentiment: (Math.random() - 0.5) * 2,
        summary: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
      }));
      
      setNews(mockNews);
      setLoading(false);
    }, 1000);
  };

  const filteredNews = news.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.summary?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesSentiment = sentimentFilter === 'all' ||
                            (sentimentFilter === 'positive' && item.sentiment > 0.2) ||
                            (sentimentFilter === 'negative' && item.sentiment < -0.2) ||
                            (sentimentFilter === 'neutral' && Math.abs(item.sentiment) <= 0.2);
    
    return matchesSearch && matchesSentiment;
  });

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.2) return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (sentiment < -0.2) return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-yellow-500" />;
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.2) return 'text-green-400';
    if (sentiment < -0.2) return 'text-red-400';
    return 'text-yellow-400';
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">News Feed</h1>
        <p className="text-slate-400">Latest market news with sentiment analysis</p>
      </div>

      {/* Filters */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Filter className="w-5 h-5 text-slate-400" />
          <h2 className="text-lg font-semibold text-white">Filters</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Asset Class</label>
            <select
              value={assetClass}
              onChange={(e) => setAssetClass(e.target.value)}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="stock">Stocks</option>
              <option value="crypto">Crypto</option>
              <option value="forex">Forex</option>
              <option value="commodity">Commodities</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Max Articles</label>
            <input
              type="number"
              min="1"
              max="50"
              value={maxArticles}
              onChange={(e) => setMaxArticles(parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Sentiment</label>
            <select
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value as any)}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="all">All</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search news..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        <button
          onClick={loadNews}
          disabled={loading}
          className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'Apply Filters'}
        </button>
      </div>

      {/* News List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 text-slate-600 mx-auto mb-4 animate-pulse" />
            <p className="text-slate-400">Loading news...</p>
          </div>
        ) : filteredNews.length === 0 ? (
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No news found matching your criteria</p>
          </div>
        ) : (
          filteredNews.map((item, index) => (
            <div key={index} className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 hover:bg-slate-800 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {getSentimentIcon(item.sentiment)}
                    <span className={`text-sm font-medium ${getSentimentColor(item.sentiment)}`}>
                      {item.sentiment.toFixed(2)}
                    </span>
                    <span className="text-slate-400 text-sm">•</span>
                    <span className="text-slate-400 text-sm">{new Date(item.published_date).toLocaleDateString()}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                  <p className="text-slate-400 text-sm mb-3">{item.summary}</p>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-slate-500">{item.source}</span>
                    <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 flex items-center gap-1">
                      Read more <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}