/**
 * Portfolio Optimization Component
 * Features: Efficient Frontier, Rebalancing, Tax-Loss Harvesting
 */

import React, { useState, useEffect } from 'react';

export default function PortfolioOptimization({ portfolio, API_URL }) {
  const [activeTab, setActiveTab] = useState('analyze');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [rebalancing, setRebalancing] = useState(null);
  const [efficientFrontier, setEfficientFrontier] = useState(null);
  const [taxLoss, setTaxLoss] = useState(null);
  const [selectedSymbols, setSelectedSymbols] = useState([]);

  useEffect(() => {
    if (portfolio && portfolio.holdings) {
      const symbols = portfolio.holdings.map(h => h.symbol);
      setSelectedSymbols(symbols);
    }
  }, [portfolio]);

  const analyzePortfolio = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v2/portfolio/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ holdings: portfolio?.holdings || [] })
      });
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
      }
    } catch (error) {
      console.error('Error analyzing portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateRebalancing = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v2/portfolio/rebalance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_allocation: portfolio?.allocations || {}
        })
      });
      if (response.ok) {
        const data = await response.json();
        setRebalancing(data);
      }
    } catch (error) {
      console.error('Error calculating rebalancing:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateEfficientFrontier = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v2/portfolio/efficient-frontier`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbols: selectedSymbols })
      });
      if (response.ok) {
        const data = await response.json();
        setEfficientFrontier(data);
      }
    } catch (error) {
      console.error('Error calculating efficient frontier:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateTaxLossHarvesting = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v2/portfolio/tax-loss-harvesting`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portfolio })
      });
      if (response.ok) {
        const data = await response.json();
        setTaxLoss(data);
      }
    } catch (error) {
      console.error('Error calculating tax-loss harvesting:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'analyze') analyzePortfolio();
    if (activeTab === 'rebalance') calculateRebalancing();
    if (activeTab === 'frontier') calculateEfficientFrontier();
    if (activeTab === 'tax') calculateTaxLossHarvesting();
  }, [activeTab]);

  if (!portfolio) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#D1D5DB' }}>
        No portfolio data available
      </div>
    );
  }

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1.5rem' }}>
      <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '1.5rem' }}>
        📊 Portfolio Optimization
      </h3>

      {/* Tabs */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #2D3748', paddingBottom: '0.5rem' }}>
          {['analyze', 'rebalance', 'frontier', 'tax'].map(tab => (
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
                fontSize: '0.85rem',
                textTransform: 'capitalize'
              }}
            >
              {tab === 'tax' ? 'Tax-Loss Harvesting' : tab}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#D1D5DB' }}>
          Loading optimization data...
        </div>
      ) : (
        <>
          {/* Portfolio Analysis */}
          {activeTab === 'analyze' && analysis && (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Total Value</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#F9FAFB' }}>
                    ${analysis.total_value?.toLocaleString() || 'N/A'}
                  </div>
                </div>
                <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Diversification Score</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#10B981' }}>
                    {(analysis.diversification_score * 100)?.toFixed(0)}%
                  </div>
                </div>
                <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Risk Level</div>
                  <div style={{
                    fontSize: '1.2rem',
                    fontWeight: '700',
                    color: analysis.risk_level === 'low' ? '#10B981' : analysis.risk_level === 'moderate' ? '#FBBF24' : '#EF4444'
                  }}>
                    {analysis.risk_level?.toUpperCase() || 'MODERATE'}
                  </div>
                </div>
                <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Est. Annual Return</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#10B981' }}>
                    {(analysis.estimated_return * 100)?.toFixed(1)}%
                  </div>
                </div>
                <div style={{ backgroundColor: '#1E293B', padding: '1rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Est. Volatility</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#FBBF24' }}>
                    {(analysis.estimated_volatility * 100)?.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Holdings Breakdown */}
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                  Current Holdings
                </h4>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #2D3748' }}>
                        <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9CA3AF' }}>Symbol</th>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Quantity</th>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Price</th>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Value</th>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Allocation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.holdings?.map((holding, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #1E293B' }}>
                          <td style={{ padding: '0.75rem', color: '#F9FAFB', fontWeight: '600' }}>
                            {holding.symbol}
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace' }}>
                            {holding.quantity}
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace' }}>
                            ${holding.price?.toFixed(2)}
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#10B981' }}>
                            ${(holding.quantity * holding.price)?.toLocaleString()}
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', color: '#D1D5DB' }}>
                            {((holding.quantity * holding.price) / analysis.total_value * 100)?.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Rebalancing */}
          {activeTab === 'rebalance' && rebalancing && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                  Rebalancing Recommendations
                </h4>
                <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', border: '1px solid #3B82F6', borderRadius: '6px', padding: '1rem', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>
                    Estimated Transaction Cost
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#F9FAFB' }}>
                    ${rebalancing.estimated_cost?.toLocaleString() || 'N/A'}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {rebalancing.recommendations?.map((rec, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: rec.action === 'buy' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      border: `1px solid ${rec.action === 'buy' ? '#10B981' : '#EF4444'}`,
                      borderRadius: '6px',
                      padding: '1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: '700', color: '#F9FAFB', marginBottom: '0.25rem' }}>
                        {rec.symbol}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
                        Current: {rec.current}% | Target: {rec.target}%
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '6px',
                        backgroundColor: rec.action === 'buy' ? '#10B981' : '#EF4444',
                        color: '#0F172A',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        marginBottom: '0.25rem'
                      }}>
                        {rec.action.toUpperCase()} {rec.quantity}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
                        {rec.action === 'buy' ? 'Add to portfolio' : 'Reduce position'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Efficient Frontier */}
          {activeTab === 'frontier' && efficientFrontier && (
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                Efficient Frontier Analysis
              </h4>

              {/* Optimal Portfolio */}
              {efficientFrontier.optimal_portfolio && (
                <div style={{
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid #10B981',
                  borderRadius: '6px',
                  padding: '1.5rem',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{ fontSize: '0.85rem', color: '#10B981', fontWeight: '600', marginBottom: '1rem' }}>
                    OPTIMAL PORTFOLIO
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Expected Return</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#10B981' }}>
                        {(efficientFrontier.optimal_portfolio.return * 100)?.toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Volatility</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#FBBF24' }}>
                        {(efficientFrontier.optimal_portfolio.volatility * 100)?.toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Sharpe Ratio</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#3B82F6' }}>
                        {efficientFrontier.optimal_portfolio.sharpe?.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Frontier Points */}
              <div>
                <h5 style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.75rem', color: '#D1D5DB' }}>
                  Risk-Return Options
                </h5>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #2D3748' }}>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Return</th>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Volatility</th>
                        <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Sharpe</th>
                      </tr>
                    </thead>
                    <tbody>
                      {efficientFrontier.frontier_points?.map((point, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #1E293B' }}>
                          <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#10B981' }}>
                            {(point.return * 100)?.toFixed(1)}%
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#FBBF24' }}>
                            {(point.volatility * 100)?.toFixed(1)}%
                          </td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#3B82F6' }}>
                            {point.sharpe?.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Tax-Loss Harvesting */}
          {activeTab === 'tax' && taxLoss && (
            <div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                  Tax-Loss Harvesting Opportunities
                </h4>
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10B981', borderRadius: '6px', padding: '1rem', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>
                    Total Tax Benefit
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#10B981' }}>
                    ${taxLoss.total_tax_benefit?.toLocaleString() || 'N/A'}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {taxLoss.harvesting_opportunities?.map((opp, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid #EF4444',
                      borderRadius: '6px',
                      padding: '1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: '700', color: '#F9FAFB', marginBottom: '0.25rem' }}>
                        {opp.symbol}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
                        Unrealized Loss: <span style={{ color: '#EF4444', fontWeight: '600' }}>
                          ${opp.unrealized_loss?.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '6px',
                        backgroundColor: '#10B981',
                        color: '#0F172A',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        marginBottom: '0.25rem'
                      }}>
                        Tax Benefit: ${opp.tax_benefit?.toLocaleString()}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
                        Consider selling for tax offset
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {(!taxLoss.harvesting_opportunities || taxLoss.harvesting_opportunities.length === 0) && (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#D1D5DB' }}>
                  No tax-loss harvesting opportunities available
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
