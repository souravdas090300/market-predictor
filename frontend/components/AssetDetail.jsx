/**
 * Asset Detail Component with Interactive Charts
 * Shows real price data with timeframe selector (24H, 1W, 1M, 6M, 1Y, 5Y, ALL)
 * Uses Recharts for candlestick/line charts with real OHLCV data
 */

import React, { useState, useEffect } from 'react';
import { LineChart, Line, CandleStick, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, Bar, Area, AreaChart } from 'recharts';
import axios from 'axios';
import '../styles/AssetDetail.css';

const TIMEFRAMES = {
  '24H': { label: '24 Hours', interval: '5min', days: 1 },
  '1W': { label: '1 Week', interval: 'hourly', days: 7 },
  '1M': { label: '1 Month', interval: 'daily', days: 30 },
  '6M': { label: '6 Months', interval: 'daily', days: 180 },
  '1Y': { label: '1 Year', interval: 'weekly', days: 365 },
  '5Y': { label: '5 Years', interval: 'monthly', days: 1825 },
  'ALL': { label: 'All Time', interval: 'monthly', days: null }
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

  // Fetch historical price data
  useEffect(() => {
    fetchPriceData();
  }, [selectedTimeframe, symbol, category]);

  const fetchPriceData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const timeframeConfig = TIMEFRAMES[selectedTimeframe];
      
      // Call backend to get historical data
      const response = await axios.get(
        `/api/v1/assets/price-history/${symbol}`,
        {
          params: {
            timeframe: selectedTimeframe,
            category: category,
            interval: timeframeConfig.interval,
            limit: getLimitForTimeframe(selectedTimeframe)
          }
        }
      );

      const { historical, current } = response.data;

      // Update asset info
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

      // Format data for chart
      const formattedData = formatChartData(historical, selectedTimeframe);
      setChartData(formattedData);
    } catch (err) {
      console.error('Error fetching price data:', err);
      setError('Failed to load price data. Please try again.');
      // Fallback to demo data for testing
      setChartData(generateDemoData(selectedTimeframe));
    } finally {
      setLoading(false);
    }
  };

  const getLimitForTimeframe = (timeframe) => {
    switch (timeframe) {
      case '24H': return 288; // 5-min candles
      case '1W': return 168; // hourly candles
      case '1M': return 30;  // daily candles
      case '6M': return 26;  // weekly candles
      case '1Y': return 52;  // weekly candles
      case '5Y': return 60;  // monthly candles
      case 'ALL': return 200; // monthly candles
      default: return 100;
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
      // For line chart fallback
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
    // Generate demo data if API fails
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

  const getChangeColor = (value) => {
    return value >= 0 ? '#10B981' : '#EF4444'; // Green or Red
  };

  const getChartColor = (value) => {
    return value >= 0 ? '#10B981' : '#EF4444';
  };

  // Custom tooltip for chart
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-date">{data.timestamp}</p>
          <p className="tooltip-open">Open: ${data.open?.toFixed(2)}</p>
          <p className="tooltip-high">High: ${data.high?.toFixed(2)}</p>
          <p className="tooltip-low">Low: ${data.low?.toFixed(2)}</p>
          <p className="tooltip-close">Close: ${data.close?.toFixed(2)}</p>
          <p className="tooltip-volume">Volume: {(data.volume / 1000000).toFixed(2)}M</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="asset-detail-container">
      {/* Header */}
      <div className="detail-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        
        <div className="asset-info">
          <h1>{assetInfo.name} ({symbol})</h1>
          <div className="price-info">
            <span className="current-price">${assetInfo.price?.toFixed(2)}</span>
            <span className={`change-24h ${assetInfo.change24h >= 0 ? 'positive' : 'negative'}`}>
              {assetInfo.change24h >= 0 ? '+' : ''}{assetInfo.change24h?.toFixed(2)} 
              ({assetInfo.changePercent >= 0 ? '+' : ''}{assetInfo.changePercent?.toFixed(2)}%)
            </span>
          </div>

          {/* Stats Grid */}
          <div className="stats-grid">
            <div className="stat">
              <span className="stat-label">24H High</span>
              <span className="stat-value">${assetInfo.high?.toFixed(2)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">24H Low</span>
              <span className="stat-value">${assetInfo.low?.toFixed(2)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">24H Volume</span>
              <span className="stat-value">{(assetInfo.volume / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="stat">
              <span className="stat-label">Market Cap</span>
              <span className="stat-value">${(assetInfo.marketCap / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>

      {/* Timeframe Selector */}
      <div className="timeframe-selector">
        {Object.entries(TIMEFRAMES).map(([key, value]) => (
          <button
            key={key}
            className={`timeframe-btn ${selectedTimeframe === key ? 'active' : ''}`}
            onClick={() => setSelectedTimeframe(key)}
          >
            {key}
          </button>
        ))}
      </div>

      {/* Chart Section */}
      <div className="chart-container">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading price data...</p>
          </div>
        ) : error ? (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={fetchPriceData}>Retry</button>
          </div>
        ) : chartData.length > 0 ? (
          <>
            {/* Area Chart for price trend */}
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

            {/* Volume Chart */}
            <div className="volume-chart">
              <h3>24H Volume</h3>
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

            {/* Chart Statistics */}
            <div className="chart-stats">
              <div className="stat-box">
                <span className="stat-label">Open</span>
                <span className="stat-value">${chartData[0]?.open?.toFixed(2)}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">High</span>
                <span className="stat-value">${Math.max(...chartData.map(d => d.high))?.toFixed(2)}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Low</span>
                <span className="stat-value">${Math.min(...chartData.map(d => d.low))?.toFixed(2)}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Close</span>
                <span className="stat-value">${chartData[chartData.length - 1]?.close?.toFixed(2)}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Avg Volume</span>
                <span className="stat-value">
                  {(chartData.reduce((sum, d) => sum + d.volume, 0) / chartData.length / 1000000).toFixed(2)}M
                </span>
              </div>
            </div>
          </>
        ) : (
          <div className="no-data">
            <p>No price data available</p>
          </div>
        )}
      </div>
    </div>
  );
}
