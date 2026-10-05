/**
 * Asset Detail Component with Interactive Charts
 * Shows real price data with timeframe selector (24H, 1W, 1M, 6M, 1Y, 5Y, ALL)
 * Uses Recharts for candlestick/line charts with real OHLCV data
 */

import React, { useState, useEffect } from 'react';
import { LineChart, Line, CandleStick, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, Bar, Area, AreaChart } from 'recharts';
import axios from 'axios';

const TIMEFRAMES = {
  '24H': { label: '24 Hours', interval: '5min', days: 1 },
  '1W': { label: '1 Week', interval: 'hourly', days: 7 },
  '1M': { label: '1 Month', interval: 'daily', days: 30 },
  '6M': { label: '6 Months', interval: 'daily', days: 180 },
  '1Y': { label: '1 Year', interval: 'weekly', days: 365 },
  '5Y': { label: '5 Years', interval: 'monthly', days: 1825 },
  'ALL': { label: 'All Time', interval: 'monthly', days: null }
};

const styles = {
  container: {
    backgroundColor: '#0F172A',
    color: '#F9FAFB',
    minHeight: '100vh',
    padding: '1rem'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: 'rgba(45, 55, 72, 0.5)',
    borderRadius: '8px',
    border: '1px solid #2D3748'
  },
  backButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#3B82F6',
    color: '#F9FAFB',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9rem'
  },
  assetInfo: {
    flex: 1
  },
  price: {
    fontSize: '2rem',
    fontWeight: '700',
    color: '#10B981'
  },
  change: {
    fontSize: '1.1rem',
    marginLeft: '1rem'
  },
  positive: { color: '#10B981' },
  negative: { color: '#EF4444' },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '1rem',
    marginTop: '1rem'
  },
  stat: {
    padding: '0.5rem',
    backgroundColor: 'rgba(45, 55, 72, 0.3)',
    borderRadius: '4px'
  },
  statLabel: {
    fontSize: '0.8rem',
    color: '#D1D5DB'
  },
  statValue: {
    fontSize: '1rem',
    fontWeight: '600',
    color: '#F9FAFB'
  },
  timeframeSelector: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '1.5rem',
    flexWrap: 'wrap'
  },
  timeframeBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: '#1E293B',
    color: '#D1D5DB',
    border: '1px solid #2D3748',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.85rem'
  },
  timeframeBtnActive: {
    backgroundColor: '#3B82F6',
    color: '#F9FAFB',
    borderColor: '#3B82F6'
  },
  chartContainer: {
    backgroundColor: 'rgba(45, 55, 72, 0.3)',
    borderRadius: '8px',
    padding: '1.5rem',
    border: '1px solid #2D3748'
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
    color: '#D1D5DB'
  },
  error: {
    textAlign: 'center',
    padding: '3rem',
    color: '#EF4444'
  },
  volumeChart: {
    marginTop: '2rem'
  },
  chartStats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
    gap: '1rem',
    marginTop: '1.5rem',
    padding: '1rem',
    backgroundColor: 'rgba(45, 55, 72, 0.3)',
    borderRadius: '6px'
  },
  tooltip: {
    backgroundColor: '#1E293B',
    border: '1px solid #3B82F6',
    borderRadius: '6px',
    padding: '0.75rem',
    fontSize: '0.85rem'
  }
};

export default function AssetDetail({ symbol, category, onBack }) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('24H');
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assetInfo, setAssetInfo] = useState({
    name: '',
    price: 0,
    change24h: 0,
    changePercent: 0,
    high: 0,
    low: 0,
    volume: 0,
    marketCap: 0
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPriceData();
  }, [selectedTimeframe, symbol, category]);

  const fetchPriceData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://market-predictor-production.up.railway.app');
      
      const response = await axios.get(
        `${API_URL}/api/v1/assets/price-history/${symbol}`,
        {
          params: {
            timeframe: selectedTimeframe,
            category: category
          }
        }
      );

      const { historical, current } = response.data;

      setAssetInfo({
        name: response.data.name || symbol,
        price: current.price,
        change24h: current.change24h,
        changePercent: current.changePercent,
        high: current.high24h,
        low: current.low24h,
        volume: current.volume24h,
        marketCap: current.marketCap
      });

      const formattedData = formatChartData(historical, selectedTimeframe);
      setChartData(formattedData);
    } catch (err) {
      console.error('Error fetching price data:', err);
      setError('Failed to load price data. Using demo data.');
      setChartData(generateDemoData(selectedTimeframe));
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = (historical, timeframe) => {
    if (!historical || historical.length === 0) return [];

    return historical.map(candle => ({
      timestamp: formatTimestamp(candle.timestamp, timeframe),
      date: candle.timestamp,
      open: parseFloat(candle.open),
      high: parseFloat(candle.high),
      low: parseFloat(candle.low),
      close: parseFloat(candle.close),
      volume: parseFloat(candle.volume),
      price: parseFloat(candle.close)
    }));
  };

  const formatTimestamp = (timestamp, timeframe) => {
    const date = new Date(timestamp);
    
    switch (timeframe) {
      case '24H':
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      case '1W':
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      case '1M':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      case '6M':
      case '1Y':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      case '5Y':
      case 'ALL':
        return date.toLocaleDateString('en-US', { year: '2-digit', month: 'short' });
      default:
        return date.toLocaleDateString();
    }
  };

  const generateDemoData = (timeframe) => {
    const limit = getLimitForTimeframe(timeframe);
    const data = [];
    let basePrice = 45000 + Math.random() * 5000;

    for (let i = 0; i < limit; i++) {
      const change = (Math.random() - 0.5) * 1000;
      const open = basePrice;
      const close = basePrice + change;
      const high = Math.max(open, close) + Math.random() * 500;
      const low = Math.min(open, close) - Math.random() * 500;

      const date = new Date();
      if (timeframe === '24H') {
        date.setMinutes(date.getMinutes() - i * 5);
      } else if (timeframe === '1W') {
        date.setHours(date.getHours() - i);
      } else {
        date.setDate(date.getDate() - i);
      }

      data.unshift({
        timestamp: date.toISOString(),
        date: date,
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        volume: Math.random() * 1000000,
        price: parseFloat(close.toFixed(2))
      });

      basePrice = close;
    }

    return data;
  };

  const getLimitForTimeframe = (timeframe) => {
    switch (timeframe) {
      case '24H': return 288;
      case '1W': return 168;
      case '1M': return 30;
      case '6M': return 26;
      case '1Y': return 52;
      case '5Y': return 60;
      case 'ALL': return 200;
      default: return 100;
    }
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={styles.tooltip}>
          <p>{data.timestamp}</p>
          <p>Open: ${data.open?.toFixed(2)}</p>
          <p>High: ${data.high?.toFixed(2)}</p>
          <p>Low: ${data.low?.toFixed(2)}</p>
          <p>Close: ${data.close?.toFixed(2)}</p>
          <p>Volume: {(data.volume / 1000000).toFixed(2)}M</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button style={styles.backButton} onClick={onBack}>
          ← Back
        </button>
        
        <div style={styles.assetInfo}>
          <h1>{assetInfo.name} ({symbol})</h1>
          <div>
            <span style={styles.price}>${assetInfo.price?.toFixed(2)}</span>
            <span style={{...styles.change, ...(assetInfo.change24h >= 0 ? styles.positive : styles.negative)}}>
              {assetInfo.change24h >= 0 ? '+' : ''}{assetInfo.change24h?.toFixed(2)} 
              ({assetInfo.changePercent >= 0 ? '+' : ''}{assetInfo.changePercent?.toFixed(2)}%)
            </span>
          </div>

          <div style={styles.statsGrid}>
            <div style={styles.stat}>
              <div style={styles.statLabel}>24H High</div>
              <div style={styles.statValue}>${assetInfo.high?.toFixed(2)}</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.statLabel}>24H Low</div>
              <div style={styles.statValue}>${assetInfo.low?.toFixed(2)}</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.statLabel}>24H Volume</div>
              <div style={styles.statValue}>{(assetInfo.volume / 1000000000).toFixed(2)}B</div>
            </div>
            <div style={styles.stat}>
              <div style={styles.statLabel}>Market Cap</div>
              <div style={styles.statValue}>${(assetInfo.marketCap / 1000000000).toFixed(2)}B</div>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.timeframeSelector}>
        {Object.entries(TIMEFRAMES).map(([key, value]) => (
          <button
            key={key}
            style={{
              ...styles.timeframeBtn,
              ...(selectedTimeframe === key ? styles.timeframeBtnActive : {})
            }}
            onClick={() => setSelectedTimeframe(key)}
          >
            {key}
          </button>
        ))}
      </div>

      <div style={styles.chartContainer}>
        {loading ? (
          <div style={styles.loading}>
            <p>Loading price data...</p>
          </div>
        ) : error ? (
          <div style={styles.error}>
            <p>{error}</p>
            <button style={styles.backButton} onClick={fetchPriceData}>Retry</button>
          </div>
        ) : chartData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="timestamp" 
                  stroke="#9CA3AF"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  style={{ fontSize: '12px' }}
                  domain={['dataMin - 100', 'dataMax + 100']}
                  width={80}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="url(#colorPrice)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>

            <div style={styles.volumeChart}>
              <h3>Volume</h3>
              <ResponsiveContainer width="100%" height={150}>
                <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="timestamp" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                  <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} width={60} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="volume" fill="#8B5CF6" opacity={0.6} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div style={styles.chartStats}>
              <div style={styles.stat}>
                <div style={styles.statLabel}>Open</div>
                <div style={styles.statValue}>${chartData[0]?.open?.toFixed(2)}</div>
              </div>
              <div style={styles.stat}>
                <div style={styles.statLabel}>High</div>
                <div style={styles.statValue}>${Math.max(...chartData.map(d => d.high))?.toFixed(2)}</div>
              </div>
              <div style={styles.stat}>
                <div style={styles.statLabel}>Low</div>
                <div style={styles.statValue}>${Math.min(...chartData.map(d => d.low))?.toFixed(2)}</div>
              </div>
              <div style={styles.stat}>
                <div style={styles.statLabel}>Close</div>
                <div style={styles.statValue}>${chartData[chartData.length - 1]?.close?.toFixed(2)}</div>
              </div>
              <div style={styles.stat}>
                <div style={styles.statLabel}>Avg Volume</div>
                <div style={styles.statValue}>
                  {(chartData.reduce((sum, d) => sum + d.volume, 0) / chartData.length / 1000000).toFixed(2)}M
                </div>
              </div>
            </div>
          </>
        ) : (
          <div style={styles.loading}>
            <p>No price data available</p>
          </div>
        )}
      </div>
    </div>
  );
}
