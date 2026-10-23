/**
 * Paper Trading Component
 * Practice trading with virtual money
 */

import React, { useState, useEffect } from 'react';

export default function PaperTrading({ symbol, currentPrice, API_URL }) {
  const [account, setAccount] = useState(null);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [side, setSide] = useState('buy');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const fetchAccount = async () => {
    try {
      const response = await fetch(`${API_URL}/api/paper/account`);
      if (response.ok) {
        const data = await response.json();
        setAccount(data.account);
      }
    } catch (err) {
      console.error('Error fetching paper account:', err);
    }
  };

  const fetchTrades = async () => {
    try {
      const response = await fetch(`${API_URL}/api/paper/trades?limit=20`);
      if (response.ok) {
        const data = await response.json();
        setTrades(data.trades || []);
      }
    } catch (err) {
      console.error('Error fetching paper trades:', err);
    }
  };

  const executeTrade = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/api/paper/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          side,
          quantity: parseFloat(quantity),
          price: parseFloat(price)
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Trade executed successfully!');
        setAccount(data.account);
        fetchTrades();
        setQuantity('');
      } else {
        setError(data.error || 'Trade failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetAccount = async () => {
    if (!confirm('Are you sure you want to reset your paper trading account?')) return;

    try {
      const response = await fetch(`${API_URL}/api/paper/reset`, {
        method: 'POST'
      });

      const data = await response.json();

      if (response.ok) {
        setAccount(data.account);
        setTrades([]);
        setSuccess('Account reset successfully!');
      }
    } catch (err) {
      setError('Failed to reset account');
    }
  };

  useEffect(() => {
    fetchAccount();
    fetchTrades();
  }, []);

  useEffect(() => {
    if (currentPrice) {
      setPrice(currentPrice.toFixed(2));
    }
  }, [currentPrice]);

  if (!account) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#D1D5DB' }}>
        Loading paper trading account...
      </div>
    );
  }

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700' }}>
          🎮 Paper Trading
        </h3>
        <button
          onClick={resetAccount}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#EF4444',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}
        >
          Reset Account
        </button>
      </div>

      {/* Account Summary */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
          <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Balance</div>
          <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#10B981' }}>
            ${account.balance?.toLocaleString() || '0'}
          </div>
        </div>
        <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
          <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Portfolio Value</div>
          <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3B82F6' }}>
            ${account.portfolio_value?.toLocaleString() || '0'}
          </div>
        </div>
        <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
          <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Total Value</div>
          <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#F9FAFB' }}>
            ${account.total_value?.toLocaleString() || '0'}
          </div>
        </div>
        <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
          <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Total Return</div>
          <div style={{
            fontSize: '1.2rem',
            fontWeight: '700',
            color: account.total_return >= 0 ? '#10B981' : '#EF4444'
          }}>
            {account.total_return >= 0 ? '+' : ''}{account.total_return?.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Holdings */}
      {Object.keys(account.holdings || {}).length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: '#D1D5DB' }}>
            Current Holdings
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {Object.entries(account.holdings).map(([sym, qty]) => (
              <div
                key={sym}
                style={{
                  backgroundColor: '#1E293B',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  fontSize: '0.85rem'
                }}
              >
                <span style={{ fontWeight: '600', color: '#F9FAFB' }}>{sym}</span>
                <span style={{ color: '#9CA3AF', marginLeft: '0.5rem' }}>
                  {qty.toFixed(4)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Trade Form */}
      <div style={{
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        border: '1px solid #3B82F6',
        borderRadius: '8px',
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#3B82F6' }}>
          Execute Trade - {symbol}
        </h4>
        <form onSubmit={executeTrade}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
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

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
                Price
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
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

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.5rem' }}>
                Total
              </label>
              <div style={{
                padding: '0.75rem',
                backgroundColor: '#0F172A',
                color: '#F9FAFB',
                border: '1px solid #2D3748',
                borderRadius: '6px',
                fontSize: '0.9rem',
                fontFamily: 'monospace'
              }}>
                ${(parseFloat(quantity || 0) * parseFloat(price || 0)).toFixed(2)}
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: loading ? '#6B7280' : (side === 'buy' ? '#10B981' : '#EF4444'),
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '700',
              fontSize: '0.9rem'
            }}
          >
            {loading ? 'Executing...' : `${side.toUpperCase()} ${symbol}`}
          </button>
        </form>

        {success && (
          <div style={{
            marginTop: '1rem',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid #10B981',
            borderRadius: '6px',
            padding: '0.75rem',
            color: '#10B981',
            fontSize: '0.85rem'
          }}>
            ✅ {success}
          </div>
        )}

        {error && (
          <div style={{
            marginTop: '1rem',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid #EF4444',
            borderRadius: '6px',
            padding: '0.75rem',
            color: '#EF4444',
            fontSize: '0.85rem'
          }}>
            ❌ {error}
          </div>
        )}
      </div>

      {/* Trade History */}
      <div>
        <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: '#D1D5DB' }}>
          Trade History ({trades.length} trades)
        </h4>
        {trades.length === 0 ? (
          <div style={{ padding: '1rem', color: '#6B7280', fontSize: '0.85rem' }}>
            No trades yet. Start trading to see your history here.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #2D3748' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9CA3AF' }}>Symbol</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9CA3AF' }}>Side</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Quantity</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Price</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Total</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {trades.slice().reverse().map((trade, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #1E293B' }}>
                    <td style={{ padding: '0.75rem', color: '#F9FAFB', fontWeight: '600' }}>
                      {trade.symbol}
                    </td>
                    <td style={{ padding: '0.75rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        backgroundColor: trade.side === 'buy' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        color: trade.side === 'buy' ? '#10B981' : '#EF4444',
                        fontSize: '0.75rem',
                        fontWeight: '700'
                      }}>
                        {trade.side.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace' }}>
                      {trade.quantity}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace' }}>
                      ${trade.price?.toFixed(2)}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#10B981' }}>
                      ${trade.total?.toFixed(2)}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF', fontSize: '0.75rem' }}>
                      {new Date(trade.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
