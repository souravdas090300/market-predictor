/**
 * Ensemble ML Predictions Component
 * Displays predictions from multiple ML models (LSTM, ARIMA, XGBoost, Prophet)
 */

import React, { useState, useEffect } from 'react';

export default function EnsemblePredictions({ symbol, API_URL }) {
  const [loading, setLoading] = useState(false);
  const [ensembleData, setEnsembleData] = useState(null);
  const [selectedDays, setSelectedDays] = useState(7);
  const [selectedHorizon, setSelectedHorizon] = useState('24h');
  const [mode, setMode] = useState('short-term'); // 'short-term' or 'long-term'
  const [anomalies, setAnomalies] = useState(null);
  const [patterns, setPatterns] = useState(null);

  const horizons = ['1h', '2h', '4h', '6h', '12h', '24h', '7d', '30d'];
  const dayOptions = [3, 5, 7, 14, 30];

  const fetchEnsemblePrediction = async () => {
    setLoading(true);
    try {
      if (mode === 'short-term') {
        const response = await fetch(`${API_URL}/api/v2/predictions/ensemble/short-term`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbol, horizon: selectedHorizon })
        });
        if (response.ok) {
          const data = await response.json();
          setEnsembleData(data);
        }
      } else {
        const response = await fetch(`${API_URL}/api/v2/predictions/ensemble`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbol, days: selectedDays })
        });
        if (response.ok) {
          const data = await response.json();
          setEnsembleData(data);
        }
      }
    } catch (error) {
      console.error('Error fetching ensemble prediction:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnomalies = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v2/predictions/anomalies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, days: selectedDays })
      });
      if (response.ok) {
        const data = await response.json();
        setAnomalies(data);
      }
    } catch (error) {
      console.error('Error fetching anomalies:', error);
    }
  };

  const fetchPatterns = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v2/predictions/patterns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, days: selectedDays })
      });
      if (response.ok) {
        const data = await response.json();
        setPatterns(data);
      }
    } catch (error) {
      console.error('Error fetching patterns:', error);
    }
  };

  useEffect(() => {
    if (symbol) {
      fetchEnsemblePrediction();
      fetchAnomalies();
      fetchPatterns();
    }
  }, [symbol, mode, selectedDays, selectedHorizon]);

  if (!symbol) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#D1D5DB' }}>
        Select a symbol to view ensemble predictions
      </div>
    );
  }

  return (
    <div style={{ border: '1px solid #2D3748', borderRadius: '8px', padding: '1.5rem' }}>
      <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '1.5rem' }}>
        🤖 Ensemble ML Predictions - {symbol}
      </h3>

      {/* Mode Toggle */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <button
            onClick={() => setMode('short-term')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: mode === 'short-term' ? '#3B82F6' : '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.85rem'
            }}
          >
            Short-Term
          </button>
          <button
            onClick={() => setMode('long-term')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: mode === 'long-term' ? '#3B82F6' : '#1E293B',
              color: '#F9FAFB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.85rem'
            }}
          >
            Long-Term
          </button>
        </div>

        {mode === 'short-term' ? (
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {horizons.map(h => (
              <button
                key={h}
                onClick={() => setSelectedHorizon(h)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: selectedHorizon === h ? '#10B981' : '#1E293B',
                  color: '#F9FAFB',
                  border: '1px solid #2D3748',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                {h}
              </button>
            ))}
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {dayOptions.map(d => (
              <button
                key={d}
                onClick={() => setSelectedDays(d)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: selectedDays === d ? '#10B981' : '#1E293B',
                  color: '#F9FAFB',
                  border: '1px solid #2D3748',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                {d} Days
              </button>
            ))}
          </div>
        )}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#D1D5DB' }}>
          Loading ensemble predictions...
        </div>
      ) : ensembleData ? (
        <div>
          {/* Main Prediction Card */}
          <div style={{
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid #10B981',
            borderRadius: '8px',
            padding: '1.5rem',
            marginBottom: '1.5rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.85rem', color: '#10B981', fontWeight: '600', marginBottom: '0.25rem' }}>
                  ENSEMBLE PREDICTION
                </div>
                <div style={{ fontSize: '0.75rem', color: '#D1D5DB' }}>
                  Confidence: {ensembleData.ensemble_prediction?.confidence || ensembleData.confidence}%
                </div>
              </div>
              <div style={{
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                backgroundColor: ensembleData.ensemble_prediction?.direction === 'up' || ensembleData.consensus === 'bullish' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                color: ensembleData.ensemble_prediction?.direction === 'up' || ensembleData.consensus === 'bullish' ? '#10B981' : '#EF4444',
                fontWeight: '700',
                fontSize: '1rem'
              }}>
                {ensembleData.ensemble_prediction?.direction?.toUpperCase() || ensembleData.consensus?.toUpperCase()}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Current Price</div>
                <div style={{ fontSize: '1.1rem', fontWeight: '700', fontFamily: 'monospace' }}>
                  ${ensembleData.current_price?.toFixed(2) || 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Predicted Price</div>
                <div style={{ fontSize: '1.1rem', fontWeight: '700', fontFamily: 'monospace', color: '#10B981' }}>
                  ${ensembleData.ensemble_prediction?.predicted_price?.toFixed(2) || 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Expected Change</div>
                <div style={{
                  fontSize: '1.1rem',
                  fontWeight: '700',
                  fontFamily: 'monospace',
                  color: (ensembleData.ensemble_prediction?.change_percent || 0) >= 0 ? '#10B981' : '#EF4444'
                }}>
                  {(ensembleData.ensemble_prediction?.change_percent || 0) >= 0 ? '+' : ''}{(ensembleData.ensemble_prediction?.change_percent || 0).toFixed(2)}%
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>Risk Level</div>
                <div style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: ensembleData.risk_assessment === 'moderate' ? '#FBBF24' : '#EF4444'
                }}>
                  {ensembleData.risk_assessment?.toUpperCase() || 'MODERATE'}
                </div>
              </div>
            </div>
          </div>

          {/* Individual Model Predictions */}
          {ensembleData.model_predictions && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                Individual Model Predictions
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {Object.entries(ensembleData.model_predictions).map(([model, data]) => (
                  <div
                    key={model}
                    style={{
                      backgroundColor: '#1E293B',
                      border: '1px solid #2D3748',
                      borderRadius: '6px',
                      padding: '1rem'
                    }}
                  >
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: '#3B82F6' }}>
                      {model.toUpperCase()}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginBottom: '0.25rem' }}>
                      Predicted: ${data.predicted_price?.toFixed(2)}
                    </div>
                    <div style={{
                      fontSize: '0.9rem',
                      fontWeight: '600',
                      color: data.change_percent >= 0 ? '#10B981' : '#EF4444',
                      fontFamily: 'monospace'
                    }}>
                      {data.change_percent >= 0 ? '+' : ''}{data.change_percent?.toFixed(2)}%
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#6B7280', marginTop: '0.25rem' }}>
                      Weight: {(data.weight * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Long-term Predictions Table */}
          {mode === 'long-term' && ensembleData.predictions && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                Prediction Timeline
              </h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #2D3748' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9CA3AF' }}>Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Ensemble</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>LSTM</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>ARIMA</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>XGBoost</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Prophet</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ensembleData.predictions.map((pred, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid #1E293B' }}>
                        <td style={{ padding: '0.75rem', color: '#F9FAFB' }}>{pred.date}</td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#10B981' }}>
                          ${pred.ensemble_price?.toFixed(2)}
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#D1D5DB' }}>
                          ${pred.lstm_price?.toFixed(2)}
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#D1D5DB' }}>
                          ${pred.arima_price?.toFixed(2)}
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#D1D5DB' }}>
                          ${pred.xgboost_price?.toFixed(2)}
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', color: '#D1D5DB' }}>
                          ${pred.prophet_price?.toFixed(2)}
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', color: '#9CA3AF' }}>
                          {(pred.ensemble_confidence * 100).toFixed(0)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Anomalies */}
          {anomalies && anomalies.anomalies_detected && anomalies.anomalies_detected.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                🚨 Detected Anomalies
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {anomalies.anomalies_detected.map((anomaly, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: anomaly.severity === 'high' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(251, 191, 36, 0.1)',
                      border: `1px solid ${anomaly.severity === 'high' ? '#EF4444' : '#FBBF24'}`,
                      borderRadius: '6px',
                      padding: '0.75rem'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#F9FAFB' }}>
                        {anomaly.date}
                      </div>
                      <div style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        backgroundColor: anomaly.severity === 'high' ? '#EF4444' : '#FBBF24',
                        color: '#0F172A',
                        fontSize: '0.7rem',
                        fontWeight: '700'
                      }}>
                        {anomaly.severity.toUpperCase()}
                      </div>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#D1D5DB', marginTop: '0.25rem' }}>
                      Z-Score: {anomaly.z_score?.toFixed(2)} | Return: {(anomaly.daily_return * 100).toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Patterns */}
          {patterns && patterns.patterns && patterns.patterns.length > 0 && (
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#D1D5DB' }}>
                📊 Detected Patterns
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {patterns.patterns.map((pattern, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: pattern.signal === 'bullish' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      border: `1px solid ${pattern.signal === 'bullish' ? '#10B981' : '#EF4444'}`,
                      borderRadius: '6px',
                      padding: '1rem'
                    }}
                  >
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.5rem', color: '#F9FAFB' }}>
                      {pattern.name}
                    </div>
                    <div style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      backgroundColor: pattern.signal === 'bullish' ? '#10B981' : '#EF4444',
                      color: '#0F172A',
                      fontSize: '0.75rem',
                      fontWeight: '700',
                      display: 'inline-block'
                    }}>
                      {pattern.signal.toUpperCase()}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginTop: '0.5rem' }}>
                      Confidence: {(pattern.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#D1D5DB' }}>
          No prediction data available
        </div>
      )}
    </div>
  );
}
