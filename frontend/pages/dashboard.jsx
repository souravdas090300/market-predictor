/**
 * User Dashboard
 * Protected route for authenticated users with full feature implementation
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('watchlist');
  const [watchlist, setWatchlist] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [signalData, setSignalData] = useState(null);
  const [newsData, setNewsData] = useState([]);
  const [sentimentData, setSentimentData] = useState(null);
  const [technicalIndicators, setTechnicalIndicators] = useState(null);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [backtestResults, setBacktestResults] = useState(null);
  const [loadingData, setLoadingData] = useState(false);
  const [shortTermPrediction, setShortTermPrediction] = useState(null);
  const [selectedHorizon, setSelectedHorizon] = useState('6h');
  const [searchQuery, setSearchQuery] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const token = localStorage.getItem('auth-token');
    const userData = localStorage.getItem('user-data');

    if (!token) {
      router.push('/auth/login');
      return;
    }

    try {
      setUser(JSON.parse(userData || '{}'));
    } catch (e) {
      console.error('Failed to parse user data', e);
    }

    setLoading(false);
    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    setLoadingData(true);
    try {
      // Load all assets from assets/all endpoint to get the full list
      const assetsRes = await fetch(`${API_URL}/api/assets/all`);
      if (assetsRes.ok) {
        const assetsData = await assetsRes.json();
        console.log('Loaded assets:', assetsData.assets?.length || 0, 'assets');
        setWatchlist(assetsData.assets || []);
      } else {
        console.error('Failed to load assets/all, status:', assetsRes.status);
        // Fallback to watchlist endpoint
        const watchlistRes = await fetch(`${API_URL}/api/watchlist`);
        if (watchlistRes.ok) {
          const watchlistData = await watchlistRes.json();
          console.log('Loaded watchlist fallback:', watchlistData?.length || 0, 'assets');
          setWatchlist(watchlistData);
        }
      }

      // Load portfolio
      const portfolioRes = await fetch(`${API_URL}/api/portfolio`);
      if (portfolioRes.ok) {
        const portfolioData = await portfolioRes.json();
        setPortfolio(portfolioData.portfolio);
      }

      // Load alerts
      const alertsRes = await fetch(`${API_URL}/api/alerts`);
      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Set fallback data on error
      setWatchlist([
        {"symbol": "AAPL", "name": "Apple", "class": "stock", "query": "Apple AAPL stock"},
        {"symbol": "BTC-USD", "name": "Bitcoin", "class": "crypto", "query": "Bitcoin price"},
        {"symbol": "EURUSD=X", "name": "EUR/USD", "class": "forex", "query": "EUR USD forex"}
      ]);
    } finally {
      setLoadingData(false);
    }
  };

  const loadSymbolData = async (symbol) => {
    if (!symbol) return;
    
    setLoadingData(true);
    try {
      // Load signal data
      const signalRes = await fetch(`${API_URL}/api/signal/${symbol}`);
      if (signalRes.ok) {
        const signal = await signalRes.json();
        setSignalData(signal);
      }

      // Load news
      const newsRes = await fetch(`${API_URL}/api/news/${symbol}`);
      if (newsRes.ok) {
        const news = await newsRes.json();
        setNewsData(news.news || []);
      }

      // Load sentiment
      const sentimentRes = await fetch(`${API_URL}/api/sentiment/${symbol}`);
      if (sentimentRes.ok) {
        const sentiment = await sentimentRes.json();
        setSentimentData(sentiment);
      }

      // Load technical indicators
      const indicatorsRes = await fetch(`${API_URL}/api/technical-indicators/${symbol}`);
      if (indicatorsRes.ok) {
        const indicators = await indicatorsRes.json();
        setTechnicalIndicators(indicators.indicators);
      }
    } catch (error) {
      console.error('Error loading symbol data:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const runBacktest = async (symbol, strategy) => {
    setLoadingData(true);
    try {
      const response = await fetch(`${API_URL}/api/v2/backtest/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          strategy,
          start_date: '2023-01-01',
          end_date: '2024-01-01',
          initial_capital: 10000
        })
      });
      
      if (response.ok) {
        const results = await response.json();
        setBacktestResults(results);
      }
    } catch (error) {
      console.error('Error running backtest:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const calculateRisk = async () => {
    if (!portfolio) return;
    
    setLoadingData(true);
    try {
      const response = await fetch(`${API_URL}/api/risk-calculator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portfolio, risk_level: 'moderate' })
      });
      
      if (response.ok) {
        const risk = await response.json();
        setRiskMetrics(risk.risk_metrics);
      }
    } catch (error) {
      console.error('Error calculating risk:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const loadShortTermPrediction = async (symbol, horizon) => {
    if (!symbol) return;
    
    setLoadingData(true);
    try {
      // Map frontend horizon values to API timeframe values
      const horizonToTimeframe = {
        '1h': '1h',
        '2h': '2h',
        '3h': '3h',
        '4h': '4h',
        '5h': '5h',
        '6h': '6h',
        '8h': '8h',
        '12h': '12h',
        '24h': '1d',
        '7d': '1w',
        '30d': '1m'
      };
      
      const timeframe = horizonToTimeframe[horizon] || '1d';
      
      const response = await fetch(`${API_URL}/api/predictions/${symbol}?timeframe=${timeframe}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const prediction = await response.json();
        // Transform API response to match frontend expectations
        setShortTermPrediction({
          symbol: prediction.symbol,
          horizon: horizon,
          current_price: prediction.current_price,
          prediction: {
            direction: prediction.trend === 'bullish' ? 'up' : prediction.trend === 'bearish' ? 'down' : 'neutral',
            predicted_price: prediction.predicted_price,
            change: prediction.predicted_price - prediction.current_price,
            change_percent: prediction.predicted_change_pct,
            confidence: prediction.confidence / 100,
            factors: {
              technical_indicators: 'RSI, MACD, Moving Averages',
              sentiment_analysis: 'News sentiment analysis',
              market_trend: 'Overall market direction',
              volatility: 'Price volatility metrics'
            }
          },
          risk_assessment: prediction.trend === 'bullish' ? 'low' : prediction.trend === 'bearish' ? 'high' : 'moderate'
        });
      } else {
        console.error('Prediction API error:', response.status);
      }
    } catch (error) {
      console.error('Error loading short-term prediction:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth-token');
    localStorage.removeItem('user-role');
    localStorage.removeItem('user-data');
    router.push('/');
  };

  if (loading) {
    return (
      <div style={{
        backgroundColor: '#0F172A',
        color: '#F9FAFB',
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '1.2rem'
      }}>
        Loading dashboard...
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div style={{ backgroundColor: '#0F172A', color: '#F9FAFB', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{
        borderBottom: '1px solid #2D3748',
        padding: '1rem 1.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        backdropFilter: 'blur(10px)',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <h1 style={{ fontSize: '1.4rem', fontWeight: '700' }}>📈 Market Predictor Pro</h1>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{user.username || user.email}</div>
            <div style={{ fontSize: '0.75rem', color: '#D1D5DB' }}>
              {localStorage.getItem('user-role') || 'user'}
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#EF4444',
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.85rem'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ padding: '1rem' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: '700', marginBottom: '1.5rem' }}>
            Welcome back, {user.username || 'Trader'}!
          </h2>

          {/* Stats Cards */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
            gap: '1rem', 
            marginBottom: '1.5rem' 
          }}>
            <StatCard 
              number={watchlist.length || 0} 
              label="Watchlist Items" 
              color="#3B82F6" 
            />
            <StatCard 
              number={alerts.length || 0} 
              label="Active Alerts" 
              color="#10B981" 
            />
            <StatCard 
              number={portfolio ? `${((portfolio.total_value || 0) / 1000).toFixed(1)}k` : '$0'} 
              label="Portfolio Value" 
              color="#10B981" 
            />
            <StatCard 
              number={portfolio ? portfolio.holdings?.length || 0 : 0} 
              label="Holdings" 
              color="#FBBF24" 
            />
          </div>

          {/* Navigation Tabs */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ 
              display: 'flex', 
              gap: '0.25rem', 
              borderBottom: '1px solid #2D3748', 
              paddingBottom: '0.5rem',
              overflowX: 'auto',
              WebkitOverflowScrolling: 'touch'
            }}>
              {['watchlist', 'portfolio', 'signals', 'prediction', 'analysis', 'backtesting', 'alerts'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: activeTab === tab ? '#3B82F6' : 'transparent',
                    color: activeTab === tab ? '#F9FAFB' : '#D1D5DB',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    textTransform: 'capitalize',
                    fontSize: '0.85rem',
                    whiteSpace: 'nowrap',
                    flexShrink: 0
                  }}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          {loadingData ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#D1D5DB' }}>
              Loading data...
            </div>
          ) : (
            <>
              {activeTab === 'watchlist' && (
                <WatchlistComponent 
                  watchlist={watchlist} 
                  onSelectSymbol={loadSymbolData}
                  selectedSymbol={selectedSymbol}
                />
              )}
              
              {activeTab === 'portfolio' && (
                <PortfolioComponent 
                  portfolio={portfolio} 
                  onCalculateRisk={calculateRisk}
                  riskMetrics={riskMetrics}
                />
              )}
              
              {activeTab === 'signals' && (
                <SignalsComponent 
                  watchlist={watchlist}
                  selectedSymbol={selectedSymbol}
                  onSelectSymbol={setSelectedSymbol}
                  signalData={signalData}
                  onLoadSignal={loadSymbolData}
                />
              )}
              
              {activeTab === 'analysis' && (
                <AnalysisComponent 
                  watchlist={watchlist}
                  selectedSymbol={selectedSymbol}
                  newsData={newsData}
                  sentimentData={sentimentData}
                  technicalIndicators={technicalIndicators}
                  onSelectSymbol={setSelectedSymbol}
                  onLoadData={loadSymbolData}
                />
              )}
              
              {activeTab === 'prediction' && (
                <ShortTermPredictionComponent 
                  watchlist={watchlist}
                  selectedSymbol={selectedSymbol}
                  onSelectSymbol={setSelectedSymbol}
                  selectedHorizon={selectedHorizon}
                  onSelectHorizon={setSelectedHorizon}
                  shortTermPrediction={shortTermPrediction}
                  onLoadPrediction={loadShortTermPrediction}
                />
              )}
              
              {activeTab === 'backtesting' && (
                <BacktestingComponent 
                  watchlist={watchlist}
                  onRunBacktest={runBacktest}
                  backtestResults={backtestResults}
                />
              )}
              
              {activeTab === 'alerts' && (
                <AlertsComponent 
                  alerts={alerts}
                  onRefresh={loadDashboardData}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// Watchlist Component
function WatchlistComponent({ watchlist, onSelectSymbol, selectedSymbol }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');

  const filteredAssets = watchlist.filter(item => {
    const symbol = (item.symbol || '').toLowerCase();
    const name = (item.name || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    const category = item.class || item.category || 'stock';
    
    const matchesSearch = symbol.includes(query) || name.includes(query);
    const matchesCategory = filterCategory === 'all' || category === filterCategory;
    
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', 'stock', 'crypto', 'forex', 'commodity'];

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '1rem' }}>📋 Asset Library ({watchlist.length} assets)</h3>
      
      {/* Search and Filter */}
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search assets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            flex: 1,
            minWidth: '200px',
            padding: '0.75rem',
            backgroundColor: '#1E293B',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px',
            fontSize: '0.9rem'
          }}
        />
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          style={{
            padding: '0.75rem',
            backgroundColor: '#1E293B',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px',
            fontSize: '0.9rem'
          }}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
          ))}
        </select>
      </div>
      
      {/* Results count */}
      <div style={{ marginBottom: '0.75rem', fontSize: '0.85rem', color: '#D1D5DB' }}>
        Showing {filteredAssets.length} of {watchlist.length} assets
        {filteredAssets.length > 200 && (
          <span style={{ color: '#FBBF24', marginLeft: '0.5rem' }}>
            (Use search to narrow results)
          </span>
        )}
      </div>
      
      {filteredAssets.length === 0 ? (
        <p style={{ color: '#D1D5DB' }}>No assets found matching your search</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.75rem' }}>
          {filteredAssets.map((item, index) => {
            const symbol = item.symbol || item.symbol;
            const name = item.name || item.name;
            const assetClass = item.class || item.category || 'stock';
            
            return (
              <div
                key={index}
                onClick={() => onSelectSymbol(symbol)}
                style={{
                  border: '1px solid #2D3748',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  backgroundColor: selectedSymbol === symbol ? 'rgba(59, 130, 246, 0.2)' : 'rgba(45, 55, 72, 0.3)',
                  transition: 'background-color 0.2s'
                }}
              >
                <div style={{ fontWeight: '700', fontSize: '1rem', marginBottom: '0.25rem' }}>
                  {symbol}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>
                  {name}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#9CA3AF', marginTop: '0.25rem' }}>
                  {assetClass}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// Portfolio Component
function PortfolioComponent({ portfolio, onCalculateRisk, riskMetrics }) {
  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>💼 Portfolio</h3>
        <button
          onClick={onCalculateRisk}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#3B82F6',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.85rem'
          }}
        >
          Calculate Risk
        </button>
      </div>
      
      {portfolio ? (
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#10B981', marginBottom: '0.25rem' }}>
              ${portfolio.total_value?.toLocaleString() || '0'}
            </div>
            <div style={{ color: '#D1D5DB', fontSize: '0.9rem' }}>Total Portfolio Value</div>
          </div>
          
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>Holdings</h4>
          {portfolio.holdings?.length > 0 ? (
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {portfolio.holdings.map((holding, index) => (
                <div
                  key={index}
                  style={{
                    border: '1px solid #2D3748',
                    padding: '0.75rem',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(45, 55, 72, 0.3)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '0.5rem'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: '700', fontSize: '1rem' }}>{holding.symbol}</div>
                    <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
                      {holding.quantity} shares @ ${holding.price?.toFixed(2)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: '700', color: '#10B981', fontSize: '1rem' }}>
                      ${holding.value?.toLocaleString() || '0'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#D1D5DB' }}>No holdings in portfolio</p>
          )}
          
          {riskMetrics && (
            <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px', border: '1px solid #EF4444' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: '#EF4444' }}>⚠️ Risk Analysis</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Value at Risk (95%)</div>
                  <div style={{ fontWeight: '700', fontSize: '1rem' }}>${(riskMetrics.at_risk || 0).toLocaleString()}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Max Loss</div>
                  <div style={{ fontWeight: '700', fontSize: '1rem' }}>{((riskMetrics.max_loss || 0) * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Max Drawdown</div>
                  <div style={{ fontWeight: '700', fontSize: '1rem' }}>{((riskMetrics.drawdown || 0) * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <p style={{ color: '#D1D5DB' }}>No portfolio data available</p>
      )}
    </div>
  );
}

// Signals Component
function SignalsComponent({ watchlist, selectedSymbol, onSelectSymbol, signalData, onLoadSignal }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAssets = watchlist.filter(item => {
    const symbol = (item.symbol || '').toLowerCase();
    const name = (item.name || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    return symbol.includes(query) || name.includes(query);
  });

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '1rem' }}>📊 Market Signals</h3>
      
      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Search assets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#1E293B',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px',
            fontSize: '0.9rem',
            marginBottom: '0.75rem'
          }}
        />
        <select
          value={selectedSymbol}
          onChange={(e) => {
            onSelectSymbol(e.target.value);
            onLoadSignal(e.target.value);
          }}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#1E293B',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px',
            fontSize: '0.9rem'
          }}
        >
          <option value="">Select a symbol...</option>
          {filteredAssets.map((item, index) => {
            const symbol = item.symbol || item.symbol;
            const name = item.name || item.name;
            return (
              <option key={index} value={symbol}>{symbol} - {name}</option>
            );
          })}
        </select>
        {filteredAssets.length > 200 && (
          <div style={{ fontSize: '0.75rem', color: '#FBBF24', marginTop: '0.5rem' }}>
            {filteredAssets.length} results. Use search to narrow down.
          </div>
        )}
      </div>
      
      {signalData ? (
        <div>
          <div style={{
            padding: '1rem',
            borderRadius: '8px',
            backgroundColor: signalData.signal === 'bullish' ? 'rgba(16, 185, 129, 0.2)' : 
                           signalData.signal === 'bearish' ? 'rgba(239, 68, 68, 0.2)' : 
                           'rgba(251, 191, 36, 0.2)',
            border: `1px solid ${signalData.signal === 'bullish' ? '#10B981' : 
                              signalData.signal === 'bearish' ? '#EF4444' : '#FBBF24'}`,
            marginBottom: '1rem'
          }}>
            <div style={{ fontSize: '1.3rem', fontWeight: '700', marginBottom: '0.5rem', textTransform: 'capitalize' }}>
              {signalData.signal} Signal
            </div>
            <div style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>
              Probability: {((signalData.probability_up || 0) * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
              Confidence: {signalData.confidence ? (signalData.confidence * 100).toFixed(1) + '%' : 'N/A'}
            </div>
          </div>
          
          {signalData.live && (
            <div style={{ marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem' }}>Live Price</h4>
              <div style={{ fontSize: '1.3rem', fontWeight: '700' }}>
                ${signalData.live.price?.toFixed(2) || 'N/A'}
              </div>
              <div style={{ color: signalData.live.change >= 0 ? '#10B981' : '#EF4444', fontSize: '0.9rem' }}>
                {signalData.live.change >= 0 ? '+' : ''}{signalData.live.change?.toFixed(2) || 0} 
                ({signalData.live.change_pct >= 0 ? '+' : ''}{(signalData.live.change_pct * 100)?.toFixed(2) || 0}%)
              </div>
            </div>
          )}
        </div>
      ) : (
        <p style={{ color: '#D1D5DB' }}>Select a symbol to view signals</p>
      )}
    </div>
  );
}

// Analysis Component
function AnalysisComponent({ watchlist, selectedSymbol, newsData, sentimentData, technicalIndicators, onSelectSymbol, onLoadData }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAssets = watchlist.filter(item => {
    const symbol = (item.symbol || '').toLowerCase();
    const name = (item.name || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    return symbol.includes(query) || name.includes(query);
  });

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '1rem' }}>🔬 Market Analysis</h3>
      
      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Search assets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#1E293B',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px',
            fontSize: '0.9rem',
            marginBottom: '0.5rem'
          }}
        />
        <select
          value={selectedSymbol}
          onChange={(e) => onSelectSymbol(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#1E293B',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px',
            fontSize: '0.9rem',
            marginBottom: '0.75rem'
          }}
        >
          <option value="">Select a symbol...</option>
          {filteredAssets.map((item, index) => {
            const symbol = item.symbol || item.symbol;
            const name = item.name || item.name;
            return (
              <option key={index} value={symbol}>{symbol} - {name}</option>
            );
          })}
        </select>
        {filteredAssets.length > 200 && (
          <div style={{ fontSize: '0.75rem', color: '#FBBF24', marginBottom: '0.5rem' }}>
            {filteredAssets.length} results. Use search to narrow down.
          </div>
        )}
        <button
          onClick={() => onLoadData(selectedSymbol)}
          disabled={!selectedSymbol}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3B82F6',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: selectedSymbol ? 'pointer' : 'not-allowed',
            fontWeight: '600',
            fontSize: '0.9rem',
            opacity: selectedSymbol ? 1 : 0.5
          }}
        >
          Analyze
        </button>
      </div>
      
      {sentimentData && (
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>😊 Sentiment Analysis</h4>
          <div style={{
            padding: '0.75rem',
            borderRadius: '6px',
            backgroundColor: sentimentData.overall_sentiment === 'bullish' ? 'rgba(16, 185, 129, 0.2)' : 
                           sentimentData.overall_sentiment === 'bearish' ? 'rgba(239, 68, 68, 0.2)' : 
                           'rgba(251, 191, 36, 0.2)',
            border: `1px solid ${sentimentData.overall_sentiment === 'bullish' ? '#10B981' : 
                              sentimentData.overall_sentiment === 'bearish' ? '#EF4444' : '#FBBF24'}`
          }}>
            <div style={{ fontSize: '1.1rem', fontWeight: '700', textTransform: 'capitalize', marginBottom: '0.5rem' }}>
              {sentimentData.overall_sentiment}
            </div>
            <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
              Score: {(sentimentData.sentiment_score * 100)?.toFixed(1) || 0}%
            </div>
          </div>
        </div>
      )}
      
      {newsData && newsData.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>📰 Recent News</h4>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {newsData.map((news, index) => (
              <div
                key={index}
                style={{
                  padding: '0.75rem',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(45, 55, 72, 0.3)',
                  border: '1px solid #2D3748'
                }}
              >
                <div style={{ fontWeight: '600', fontSize: '0.9rem', marginBottom: '0.5rem' }}>{news.title}</div>
                <div style={{ fontSize: '0.8rem', color: '#D1D5DB', marginBottom: '0.5rem' }}>
                  {news.source} • {new Date(news.date).toLocaleDateString()}
                </div>
                <div style={{
                  fontSize: '0.75rem',
                  color: news.sentiment === 'positive' ? '#10B981' : 
                         news.sentiment === 'negative' ? '#EF4444' : '#FBBF24',
                  textTransform: 'capitalize'
                }}>
                  {news.sentiment}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {technicalIndicators && (
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>📈 Technical Indicators</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem' }}>
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>RSI (14)</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>{technicalIndicators.rsi_14?.toFixed(2) || 'N/A'}</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>MACD</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>{technicalIndicators.macd?.line?.toFixed(2) || 'N/A'}</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>SMA (20)</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>{technicalIndicators.sma_20?.toFixed(2) || 'N/A'}</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>EMA (12)</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>{technicalIndicators.ema_12?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Backtesting Component
function BacktestingComponent({ watchlist, onRunBacktest, backtestResults }) {
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState('momentum');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAssets = watchlist.filter(item => {
    const symbol = (item.symbol || '').toLowerCase();
    const name = (item.name || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    return symbol.includes(query) || name.includes(query);
  });

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '1rem' }}>🔄 Backtesting</h3>
      
      <div style={{ display: 'grid', gap: '0.75rem', marginBottom: '1rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: '#D1D5DB' }}>Symbol</label>
          <input
            type="text"
            placeholder="Search assets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              fontSize: '0.9rem',
              marginBottom: '0.5rem'
            }}
          />
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              fontSize: '0.9rem'
            }}
          >
            <option value="">Select a symbol...</option>
            {filteredAssets.map((item, index) => {
              const symbol = item.symbol || item.symbol;
              return (
                <option key={index} value={symbol}>{symbol}</option>
              );
            })}
          </select>
          {filteredAssets.length > 200 && (
            <div style={{ fontSize: '0.75rem', color: '#FBBF24', marginTop: '0.5rem' }}>
              {filteredAssets.length} results. Use search to narrow down.
            </div>
          )}
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: '#D1D5DB' }}>Strategy</label>
          <select
            value={selectedStrategy}
            onChange={(e) => setSelectedStrategy(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              fontSize: '0.9rem'
            }}
          >
            <option value="momentum">Momentum</option>
            <option value="mean_reversion">Mean Reversion</option>
            <option value="breakout">Breakout</option>
            <option value="macd">MACD Crossover</option>
          </select>
        </div>
        
        <button
          onClick={() => onRunBacktest(selectedSymbol, selectedStrategy)}
          disabled={!selectedSymbol}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3B82F6',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: selectedSymbol ? 'pointer' : 'not-allowed',
            fontWeight: '600',
            fontSize: '0.9rem',
            opacity: selectedSymbol ? 1 : 0.5
          }}
        >
          Run Backtest
        </button>
      </div>
      
      {backtestResults && (
        <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>📊 Backtest Results</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Total Return</div>
              <div style={{ fontWeight: '700', fontSize: '1rem', color: '#10B981' }}>
                {((backtestResults.total_return || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Sharpe Ratio</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>
                {backtestResults.sharpe_ratio?.toFixed(2) || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Max Drawdown</div>
              <div style={{ fontWeight: '700', fontSize: '1rem', color: '#EF4444' }}>
                {((backtestResults.max_drawdown || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Win Rate</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>
                {((backtestResults.win_rate || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Total Trades</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>
                {backtestResults.trade_count || 0}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Alerts Component
function AlertsComponent({ alerts, onRefresh }) {
  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>🔔 Alerts</h3>
        <button
          onClick={onRefresh}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#3B82F6',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.85rem'
          }}
        >
          Refresh
        </button>
      </div>
      
      {alerts.length === 0 ? (
        <p style={{ color: '#D1D5DB' }}>No active alerts</p>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {alerts.map((alert, index) => (
            <div
              key={index}
              style={{
                padding: '0.75rem',
                borderRadius: '6px',
                backgroundColor: 'rgba(45, 55, 72, 0.3)',
                border: '1px solid #2D3748',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '0.5rem'
              }}
            >
              <div>
                <div style={{ fontWeight: '700', fontSize: '1rem' }}>{alert.symbol}</div>
                <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
                  {alert.type} • ${alert.trigger}
                </div>
              </div>
              <div style={{
                padding: '0.25rem 0.75rem',
                borderRadius: '4px',
                backgroundColor: alert.status === 'active' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                color: alert.status === 'active' ? '#10B981' : '#EF4444',
                fontSize: '0.8rem',
                fontWeight: '600',
                textTransform: 'capitalize'
              }}>
                {alert.status}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Short-Term Prediction Component
function ShortTermPredictionComponent({ watchlist, selectedSymbol, onSelectSymbol, selectedHorizon, onSelectHorizon, shortTermPrediction, onLoadPrediction }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAssets = watchlist.filter(item => {
    const symbol = (item.symbol || '').toLowerCase();
    const name = (item.name || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    return symbol.includes(query) || name.includes(query);
  });

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '1rem' }}>⏰ Predictions</h3>
      
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ marginBottom: '0.75rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: '#D1D5DB' }}>Select Asset</label>
          <input
            type="text"
            placeholder="Search assets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              fontSize: '0.9rem',
              marginBottom: '0.5rem'
            }}
          />
          <select
            value={selectedSymbol}
            onChange={(e) => onSelectSymbol(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              fontSize: '0.9rem'
            }}
          >
            <option value="">Select a symbol...</option>
            {filteredAssets.map((item, index) => {
              const symbol = item.symbol || item.symbol;
              const name = item.name || item.name;
              return (
                <option key={index} value={symbol}>{symbol} - {name}</option>
              );
            })}
          </select>
          {filteredAssets.length > 200 && (
            <div style={{ fontSize: '0.75rem', color: '#FBBF24', marginTop: '0.5rem' }}>
              {filteredAssets.length} results. Use search to narrow down.
            </div>
          )}
        </div>
        
        <div style={{ marginBottom: '0.75rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: '#D1D5DB' }}>Time Horizon</label>
          <select
            value={selectedHorizon}
            onChange={(e) => onSelectHorizon(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              fontSize: '0.9rem'
            }}
          >
            <option value="1h">1 Hour</option>
            <option value="2h">2 Hours</option>
            <option value="3h">3 Hours</option>
            <option value="4h">4 Hours</option>
            <option value="5h">5 Hours</option>
            <option value="6h">6 Hours</option>
            <option value="8h">8 Hours</option>
            <option value="12h">12 Hours</option>
            <option value="24h">24 Hours</option>
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
          </select>
        </div>
        
        <button
          onClick={() => onLoadPrediction(selectedSymbol, selectedHorizon)}
          disabled={!selectedSymbol}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3B82F6',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: selectedSymbol ? 'pointer' : 'not-allowed',
            fontWeight: '600',
            fontSize: '0.9rem',
            opacity: selectedSymbol ? 1 : 0.5
          }}
        >
          Predict
        </button>
      </div>
      
      {shortTermPrediction && (
        <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>📊 Prediction Results</h4>
          
          <div style={{
            padding: '1rem',
            borderRadius: '6px',
            backgroundColor: shortTermPrediction.prediction.direction === 'up' ? 'rgba(16, 185, 129, 0.2)' : 
                           shortTermPrediction.prediction.direction === 'down' ? 'rgba(239, 68, 68, 0.2)' : 
                           'rgba(251, 191, 36, 0.2)',
            border: `1px solid ${shortTermPrediction.prediction.direction === 'up' ? '#10B981' : 
                              shortTermPrediction.prediction.direction === 'down' ? '#EF4444' : '#FBBF24'}`,
            marginBottom: '1rem'
          }}>
            <div style={{ fontSize: '1.2rem', fontWeight: '700', textTransform: 'capitalize', marginBottom: '0.5rem' }}>
              {shortTermPrediction.prediction.direction} ({shortTermPrediction.horizon})
            </div>
            <div style={{ fontSize: '0.9rem', color: '#D1D5DB', marginBottom: '0.25rem' }}>
              Current: ${shortTermPrediction.current_price?.toFixed(2) || 'N/A'}
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.25rem' }}>
              Predicted: ${shortTermPrediction.prediction.predicted_price?.toFixed(2) || 'N/A'}
            </div>
            <div style={{ fontSize: '0.9rem', color: shortTermPrediction.prediction.change >= 0 ? '#10B981' : '#EF4444' }}>
              {shortTermPrediction.prediction.change >= 0 ? '+' : ''}${shortTermPrediction.prediction.change?.toFixed(2) || 0} 
              ({shortTermPrediction.prediction.change_percent >= 0 ? '+' : ''}{shortTermPrediction.prediction.change_percent?.toFixed(2) || 0}%)
            </div>
            <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
              Confidence: {(shortTermPrediction.prediction.confidence * 100)?.toFixed(1)}%
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem' }}>
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Risk Level</div>
              <div style={{ fontWeight: '700', fontSize: '1rem', textTransform: 'capitalize' }}>
                {shortTermPrediction.risk_assessment}
              </div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(45, 55, 72, 0.3)' }}>
              <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>Timeframe</div>
              <div style={{ fontWeight: '700', fontSize: '1rem' }}>
                {shortTermPrediction.horizon}
              </div>
            </div>
          </div>
          
          <div style={{ marginTop: '1rem', padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(59, 130, 246, 0.1)', border: '1px solid #3B82F6' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.5rem', color: '#3B82F6' }}>🔍 Analysis Factors</h4>
            <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
              {shortTermPrediction.prediction.factors?.technical_indicators}, {shortTermPrediction.prediction.factors?.sentiment_analysis}, {shortTermPrediction.prediction.factors?.market_trend}, {shortTermPrediction.prediction.factors?.volatility}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ number, label, color }) {
  return (
    <div style={{
      border: '1px solid #2D3748',
      padding: '1rem',
      borderRadius: '8px',
      backgroundColor: 'rgba(45, 55, 72, 0.3)',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '1.5rem', fontWeight: '700', color, marginBottom: '0.25rem' }}>
        {number}
      </div>
      <div style={{ color: '#D1D5DB', fontSize: '0.8rem' }}>
        {label}
      </div>
    </div>
  );
}
