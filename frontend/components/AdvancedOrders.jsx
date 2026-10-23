/**
 * Advanced Orders Component
 * Features: Stop-Loss, Stop-Limit, Trailing Stop orders
 */

import React, { useState } from 'react';

export default function AdvancedOrders({ symbol, currentPrice, API_URL }) {
  const [orderType, setOrderType] = useState('stop-loss');
  const [side, setSide] = useState('sell');
  const [quantity, setQuantity] = useState('');
  const [stopPrice, setStopPrice] = useState('');
  const [limitPrice, setLimitPrice] = useState('');
  const [trailAmount, setTrailAmount] = useState('');
  const [trailType, setTrailType] = useState('amount');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let endpoint;
      let body;

      switch (orderType) {
        case 'stop-loss':
          endpoint = '/api/v2/orders/stop-loss';
          body = {
            symbol,
            side,
            quantity: parseFloat(quantity),
            stop_price: parseFloat(stopPrice),
            price: limitPrice ? parseFloat(limitPrice) : null
          };
          break;
        case 'stop-limit':
          endpoint = '/api/v2/orders/stop-limit';
          body = {
            symbol,
            side,
            quantity: parseFloat(quantity),
            stop_price: parseFloat(stopPrice),
            limit_price: parseFloat(limitPrice)
          };
          break;
        case 'trailing-stop':
          endpoint = '/api/v2/orders/trailing-stop';
          body = {
            symbol,
            side,
            quantity: parseFloat(quantity),
            trail_amount: parseFloat(trailAmount),
            trail_type: trailType
          };
          break;
        default:
          throw new Error('Invalid order type');
      }

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.detail || 'Order failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getOrderDescription = () => {
    switch (orderType) {
      case 'stop-loss':
        return 'Triggered when price reaches stop price, executes as market order';
      case 'stop-limit':
        return 'Triggered when price reaches stop price, becomes limit order at limit price';
      case 'trailing-stop':
        return 'Stop price adjusts as price moves in your favor by trail amount';
      default:
        return '';
    }
  };

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1.5rem' }}>
      <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '1.5rem' }}>
        🎯 Advanced Orders - {symbol}
      </h3>

      {/* Order Type Selection */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>Order Type</div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {['stop-loss', 'stop-limit', 'trailing-stop'].map(type => (
            <button
              key={type}
              onClick={() => {
                setOrderType(type);
                setResult(null);
                setError(null);
              }}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: orderType === type ? '#3B82F6' : '#1E293B',
                color: '#F9FAFB',
                border: '1px solid #2D3748',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: '600',
                textTransform: 'capitalize'
              }}
            >
              {type.replace('-', ' ')}
            </button>
          ))}
        </div>
        <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '0.5rem' }}>
          {getOrderDescription()}
        </div>
      </div>

      {/* Order Form */}
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {/* Side */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
              Side
            </label>
            <select
              value={side}
              onChange={(e) => setSide(e.target.value)}
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
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>

          {/* Quantity */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
              Quantity
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#1E293B',
                color: '#F9FAFB',
                border: '1px solid #2D3748',
                borderRadius: '6px',
                fontSize: '0.9rem'
              }}
            />
          </div>

          {/* Stop Price */}
          {(orderType === 'stop-loss' || orderType === 'stop-limit') && (
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
                Stop Price
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={stopPrice}
                onChange={(e) => setStopPrice(e.target.value)}
                required
                placeholder={currentPrice ? `$${currentPrice.toFixed(2)}` : ''}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: '#1E293B',
                  color: '#F9FAFB',
                  border: '1px solid #2D3748',
                  borderRadius: '6px',
                  fontSize: '0.9rem'
                }}
              />
            </div>
          )}

          {/* Limit Price (for stop-limit) */}
          {orderType === 'stop-limit' && (
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
                Limit Price
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={limitPrice}
                onChange={(e) => setLimitPrice(e.target.value)}
                required
                placeholder="Limit execution price"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: '#1E293B',
                  color: '#F9FAFB',
                  border: '1px solid #2D3748',
                  borderRadius: '6px',
                  fontSize: '0.9rem'
                }}
              />
            </div>
          )}

          {/* Trail Amount (for trailing stop) */}
          {orderType === 'trailing-stop' && (
            <>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
                  Trail Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={trailAmount}
                  onChange={(e) => setTrailAmount(e.target.value)}
                  required
                  placeholder={trailType === 'percentage' ? 'e.g., 5 for 5%' : 'e.g., 10.50'}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: '#1E293B',
                    color: '#F9FAFB',
                    border: '1px solid #2D3748',
                    borderRadius: '6px',
                    fontSize: '0.9rem'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
                  Trail Type
                </label>
                <select
                  value={trailType}
                  onChange={(e) => setTrailType(e.target.value)}
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
                  <option value="amount">Amount ($)</option>
                  <option value="percentage">Percentage (%)</option>
                </select>
              </div>
            </>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: loading ? '#6B7280' : '#10B981',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: '700',
            fontSize: '0.9rem'
          }}
        >
          {loading ? 'Placing Order...' : `Place ${orderType.replace('-', ' ').toUpperCase()} Order`}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div style={{
          marginTop: '1.5rem',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid #10B981',
          borderRadius: '6px',
          padding: '1rem'
        }}>
          <div style={{ fontSize: '0.85rem', color: '#10B981', fontWeight: '600', marginBottom: '0.5rem' }}>
            ✅ Order Placed Successfully
          </div>
          <div style={{ fontSize: '0.8rem', color: '#D1D5DB' }}>
            Order ID: <span style={{ fontFamily: 'monospace', color: '#F9FAFB' }}>{result.order?.id}</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: '#D1D5DB', marginTop: '0.25rem' }}>
            Status: <span style={{ color: '#FBBF24', fontWeight: '600' }}>{result.order?.status?.toUpperCase()}</span>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          marginTop: '1.5rem',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #EF4444',
          borderRadius: '6px',
          padding: '1rem',
          color: '#EF4444',
          fontSize: '0.85rem'
        }}>
          ❌ {error}
        </div>
      )}

      {/* Order Info */}
      <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#1E293B', borderRadius: '6px' }}>
        <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#D1D5DB', marginBottom: '0.5rem' }}>
          Order Details
        </div>
        <div style={{ fontSize: '0.8rem', color: '#9CA3AF', lineHeight: '1.6' }}>
          <div>Symbol: <span style={{ color: '#F9FAFB' }}>{symbol}</span></div>
          <div>Current Price: <span style={{ color: '#F9FAFB' }}>{currentPrice ? `$${currentPrice.toFixed(2)}` : 'N/A'}</span></div>
          {orderType === 'stop-loss' && (
            <div>Trigger: Market order when price hits stop price</div>
          )}
          {orderType === 'stop-limit' && (
            <div>Trigger: Limit order when price hits stop price</div>
          )}
          {orderType === 'trailing-stop' && (
            <div>Trigger: Stop price trails by {trailType === 'percentage' ? '%' : '$'}{trailAmount}</div>
          )}
        </div>
      </div>
    </div>
  );
}
