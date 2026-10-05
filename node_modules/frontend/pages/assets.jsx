/**
 * Assets Library - Live Prices & Prediction Accuracy
 * Matches the design from screenshots
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AssetsLibrary() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState('crypto');
  const [selectedFilter, setSelectedFilter] = useState('popular');
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [assets, setAssets] = useState([]);
  const [assetDetail, setAssetDetail] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');
  const [loading, setLoading] = useState(false);
  const [ws, setWs] = useState(null);

  const categories = [
    { id: 'crypto', label: 'Crypto', icon: '₿' },
    { id: 'stock', label: 'Stocks', icon: '📈' },
    { id: 'forex', label: 'Forex', icon: '💱' },
    { id: 'commodity', label: 'Commodities', icon: '🪙' }
  ];

  const filters = [
    { id: 'popular', label: 'Most Popular' },
    { id: 'gainers', label: 'Top Gainers' },
    { id: 'losers', label: 'Top Losers' },
    { id: 'new', label: 'New' }
  ];

  const timeframes = [
    { id: '24h', label: '24H' },
    { id: '7d', label: '1W' },
    { id: '30d', label: '1M' },
    { id: '1y', label: '1Y' },
    { id: 'all', label: 'ALL' }
  ];

  // Fetch assets list
  useEffect(() => {
    fetchAssets();
  }, [selectedCategory, selectedFilter]);

  // Fetch asset detail when selected
  useEffect(() => {
    if (selectedAsset) {
      fetchAssetDetail(selectedAsset);
    }
  }, [selectedAsset, selectedTimeframe]);

  // WebSocket for live updates
  useEffect(() => {
    if (selectedAsset && !ws) {
      connectWebSocket(selectedAsset);
    }
    return () => {
      if (ws) {
        ws.close();
        setWs(null);
      }
    };
  }, [selectedAsset]);

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/v2/assets/list?category=${selectedCategory}&sort_by=${selectedFilter}&limit=20`
      );
      if (response.ok) {
        const data = await response.json();
        setAssets(data.assets || []);
      }
    } catch (error) {
      console.error('Error fetching assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssetDetail = async (symbol) => {
    try {
      const response = await fetch(`${API_URL}/api/v2/assets/detail/${symbol}`);
      if (response.ok) {
        const data = await response.json();
        setAssetDetail(data);
      }
    } catch (error) {
      console.error('Error fetching asset detail:', error);
    }
  };

  const connectWebSocket = (symbol) => {
    const wsUrl = `${API_URL.replace('http', 'ws')}/api/v2/assets/ws/price/${symbol}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'price_update') {
        // Update asset detail with new price
        setAssetDetail(prev => ({
          ...prev,
          price: {
            ...prev.price,
            current: data.current_price,
            bid: data.bid,
            ask: data.ask
          },
          change: {
            ...prev.change,
            change_24h_dollars: data.change_24h,
            change_24h_percent: data.change_percent_24h
          },
          updated_at: data.timestamp
        }));

        // Also update the asset in the list
        setAssets(prevAssets =>
          prevAssets.map(asset =>
            asset.symbol === symbol
              ? {
                  ...asset,
                  current_price: data.current_price,
                  change_24h: data.change_24h,
                  change_percent_24h: data.change_percent_24h,
                  updated_at: data.timestamp
                }
              : asset
          )
        );
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    setWs(websocket);
  };

  const formatPrice = (price, decimals = 2) => {
    if (price === null || price === undefined) return '$0.00';
    return `$${price.toFixed(decimals)}`;
  };

  const formatPercent = (percent) => {
    if (percent === null || percent === undefined) return '0.00%';
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent.toFixed(2)}%`;
  };

  const formatLargeNumber = (num) => {
    if (!num) return 'N/A';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${num.toFixed(2)}`;
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 80) return '#10B981'; // Green
    if (accuracy >= 60) return '#FBBF24'; // Yellow
    return '#EF4444'; // Red
  };

  if (selectedAsset && assetDetail) {
    // Detail View
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#0F172A', color: '#F9FAFB', padding: '20px' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
          <button
            onClick={() => setSelectedAsset(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#D1D5DB',
              cursor: 'pointer',
              fontSize: '24px',
              marginRight: '16px'
            }}
          >
            ←
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '32px' }}>{assetDetail.asset.icon}</span>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: '700', margin: 0 }}>{assetDetail.asset.name}</h1>
              <p style={{ fontSize: '14px', color: '#D1D5DB', margin: 0 }}>{assetDetail.asset.symbol}</p>
            </div>
          </div>
        </div>

        {/* Price Section */}
        <div style={{
          backgroundColor: '#1E293B',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
            <div>
              <div style={{ fontSize: '48px', fontWeight: '700', marginBottom: '8px' }}>
                {formatPrice(assetDetail.price.current, assetDetail.asset.decimals)}
              </div>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <span style={{
                  color: assetDetail.change.change_24h_percent >= 0 ? '#10B981' : '#EF4444',
                  fontSize: '18px',
                  fontWeight: '600'
                }}>
                  {formatPrice(assetDetail.change.change_24h_dollars)} ({formatPercent(assetDetail.change.change_24h_percent)})
                </span>
                <span style={{ color: '#6B7280', fontSize: '14px' }}>
                  24H
                </span>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '14px', color: '#D1D5DB', marginBottom: '4px' }}>
                High: <span style={{ color: '#10B981' }}>{formatPrice(assetDetail.change.high_24h)}</span>
              </div>
              <div style={{ fontSize: '14px', color: '#D1D5DB' }}>
                Low: <span style={{ color: '#EF4444' }}>{formatPrice(assetDetail.change.low_24h)}</span>
              </div>
            </div>
          </div>

          {/* Timeframe Selector */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
            {timeframes.map(tf => (
              <button
                key={tf.id}
                onClick={() => setSelectedTimeframe(tf.id)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: selectedTimeframe === tf.id ? '#3B82F6' : '#374151',
                  color: '#F9FAFB',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {tf.label}
              </button>
            ))}
          </div>

          {/* Chart Placeholder */}
          <div style={{
            height: '300px',
            backgroundColor: '#0F172A',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6B7280'
          }}>
            Chart data for {selectedTimeframe}
          </div>
        </div>

        {/* Market Data */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px'
        }}>
          <div style={{ backgroundColor: '#1E293B', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '14px', color: '#D1D5DB', marginBottom: '8px' }}>Market Cap</div>
            <div style={{ fontSize: '20px', fontWeight: '600' }}>
              {formatLargeNumber(assetDetail.market.market_cap)}
            </div>
          </div>
          <div style={{ backgroundColor: '#1E293B', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '14px', color: '#D1D5DB', marginBottom: '8px' }}>Volume 24H</div>
            <div style={{ fontSize: '20px', fontWeight: '600' }}>
              {formatLargeNumber(assetDetail.market.volume_24h)}
            </div>
          </div>
          {assetDetail.market.apy && (
            <div style={{ backgroundColor: '#1E293B', borderRadius: '12px', padding: '20px' }}>
              <div style={{ fontSize: '14px', color: '#D1D5DB', marginBottom: '8px' }}>APY</div>
              <div style={{ fontSize: '20px', fontWeight: '600', color: '#10B981' }}>
                {assetDetail.market.apy}%
              </div>
            </div>
          )}
        </div>

        {/* Prediction Accuracy */}
        <div style={{ backgroundColor: '#1E293B', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '20px' }}>Prediction Accuracy</h2>
          
          {timeframes.map(tf => {
            const timeframeData = assetDetail.predictions[`timeframe_${tf.id}`];
            if (!timeframeData) return null;
            
            return (
              <div key={tf.id} style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ fontSize: '16px', fontWeight: '600' }}>{tf.label} Accuracy</span>
                  <span style={{ fontSize: '14px', color: '#D1D5DB' }}>
                    Based on {timeframeData.predictions_tested} predictions tested
                  </span>
                </div>
                
                <div style={{ display: 'grid', gap: '12px' }}>
                  {[
                    { name: 'LSTM', accuracy: timeframeData.lstm_accuracy },
                    { name: 'ARIMA', accuracy: timeframeData.arima_accuracy },
                    { name: 'XGBoost', accuracy: timeframeData.xgboost_accuracy },
                    { name: 'Prophet', accuracy: timeframeData.prophet_accuracy }
                  ].map(model => (
                    <div key={model.name}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontSize: '14px' }}>{model.name}</span>
                        <span style={{ fontSize: '14px', fontWeight: '600', color: getAccuracyColor(model.accuracy) }}>
                          {model.accuracy.toFixed(1)}%
                        </span>
                      </div>
                      <div style={{ height: '8px', backgroundColor: '#374151', borderRadius: '4px', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${model.accuracy}%`,
                            backgroundColor: getAccuracyColor(model.accuracy),
                            transition: 'width 0.3s ease'
                          }}
                        />
                      </div>
                    </div>
                  ))}
                  
                  {/* Ensemble */}
                  <div style={{ marginTop: '8px', paddingTop: '12px', borderTop: '1px solid #374151' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '14px', fontWeight: '600' }}>Ensemble</span>
                      <span style={{ fontSize: '16px', fontWeight: '700', color: getAccuracyColor(timeframeData.ensemble_accuracy) }}>
                        {timeframeData.ensemble_accuracy.toFixed(1)}%
                      </span>
                    </div>
                    <div style={{ height: '12px', backgroundColor: '#374151', borderRadius: '4px', overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${timeframeData.ensemble_accuracy}%`,
                          backgroundColor: getAccuracyColor(timeframeData.ensemble_accuracy),
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '16px' }}>
          Last updated: {new Date(assetDetail.updated_at).toLocaleString()}
        </div>
      </div>
    );
  }

  // List View
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0F172A', color: '#F9FAFB', padding: '20px' }}>
      <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '24px' }}>Assets Library</h1>

      {/* Category Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', overflowX: 'auto' }}>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            style={{
              padding: '12px 24px',
              backgroundColor: selectedCategory === cat.id ? '#3B82F6' : '#1E293B',
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>{cat.icon}</span>
            {cat.label}
          </button>
        ))}
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', overflowX: 'auto' }}>
        {filters.map(filter => (
          <button
            key={filter.id}
            onClick={() => setSelectedFilter(filter.id)}
            style={{
              padding: '8px 16px',
              backgroundColor: selectedFilter === filter.id ? '#3B82F6' : '#1E293B',
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              whiteSpace: 'nowrap'
            }}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Assets Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6B7280' }}>Loading...</div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '16px'
        }}>
          {assets.map(asset => (
            <div
              key={asset.symbol}
              onClick={() => setSelectedAsset(asset.symbol)}
              style={{
                backgroundColor: '#1E293B',
                borderRadius: '12px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                border: '1px solid #374151'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = '#3B82F6'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#374151'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <span style={{ fontSize: '24px' }}>{asset.icon}</span>
                <div>
                  <div style={{ fontSize: '16px', fontWeight: '600' }}>{asset.name}</div>
                  <div style={{ fontSize: '12px', color: '#D1D5DB' }}>{asset.symbol}</div>
                </div>
                {asset.apy && (
                  <span style={{
                    marginLeft: 'auto',
                    padding: '4px 8px',
                    backgroundColor: '#10B981',
                    color: '#F9FAFB',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {asset.apy}% APY
                  </span>
                )}
              </div>

              <div style={{ fontSize: '24px', fontWeight: '700', marginBottom: '8px' }}>
                {formatPrice(asset.current_price)}
              </div>

              <div style={{
                color: asset.change_percent_24h >= 0 ? '#10B981' : '#EF4444',
                fontSize: '16px',
                fontWeight: '600',
                marginBottom: '12px'
              }}>
                {formatPercent(asset.change_percent_24h)}
              </div>

              {/* Prediction Accuracy Mini Bar */}
              <div style={{ marginBottom: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '12px', color: '#D1D5DB' }}>Prediction Accuracy</span>
                  <span style={{ fontSize: '12px', color: getAccuracyColor(asset.prediction_accuracy.ensemble) }}>
                    {asset.prediction_accuracy.ensemble.toFixed(1)}%
                  </span>
                </div>
                <div style={{ height: '4px', backgroundColor: '#374151', borderRadius: '2px', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${asset.prediction_accuracy.ensemble}%`,
                      backgroundColor: getAccuracyColor(asset.prediction_accuracy.ensemble)
                    }}
                  />
                </div>
              </div>

              <div style={{ fontSize: '12px', color: '#6B7280' }}>
                Updated: {new Date(asset.updated_at).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {assets.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6B7280' }}>
          No assets found for this category
        </div>
      )}
    </div>
  );
}
