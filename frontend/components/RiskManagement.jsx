import React, { useState } from 'react';
import { Shield, AlertTriangle, Activity, Settings, Play, Loader2, TrendingDown } from 'lucide-react';
import axios from 'axios';

const RiskManagement = () => {
  const [activeTab, setActiveTab] = useState('limits');
  const [riskLimits, setRiskLimits] = useState({
    max_position_size: 10000,
    max_daily_loss: 1000,
    max_drawdown: 0.15,
    max_correlation: 0.7,
    max_leverage: 2,
    stop_loss_percent: 0.05
  });
  const [varResult, setVarResult] = useState(null);
  const [cvarResult, setCvarResult] = useState(null);
  const [stressTestResults, setStressTestResults] = useState(null);
  const [monitoringActive, setMonitoringActive] = useState(false);
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://market-predictor-production-0f87.up.railway.app');

  const calculateVaR = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/risk/var`, {
        portfolio: { total_value: 50000, positions: [] },
        confidence_level: 0.95
      });
      setVarResult(response.data);
    } catch (error) {
      console.error('Failed to calculate VaR:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateCVaR = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/risk/cvar`, {
        portfolio: { total_value: 50000, positions: [] },
        confidence_level: 0.95
      });
      setCvarResult(response.data);
    } catch (error) {
      console.error('Failed to calculate CVaR:', error);
    } finally {
      setLoading(false);
    }
  };

  const runStressTest = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/risk/stress-test`, {
        portfolio: { total_value: 50000, positions: [] },
        scenarios: [
          { name: 'Market Crash 20%', impact: -0.20 },
          { name: 'Interest Rate Rise', impact: -0.05 },
          { name: 'Sector Rotation', impact: -0.03 }
        ]
      });
      setStressTestResults(response.data);
    } catch (error) {
      console.error('Failed to run stress test:', error);
    } finally {
      setLoading(false);
    }
  };

  const setRiskLimitsAPI = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/api/v2/risk/limits`, riskLimits);
      alert('Risk limits updated successfully!');
    } catch (error) {
      console.error('Failed to set risk limits:', error);
      alert('Failed to update risk limits');
    } finally {
      setLoading(false);
    }
  };

  const toggleMonitoring = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/api/v2/risk/monitor`, {
        portfolio: { total_value: 50000, positions: [] },
        alert_level: 'warning'
      });
      setMonitoringActive(!monitoringActive);
    } catch (error) {
      console.error('Failed to toggle monitoring:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('limits')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'limits'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Settings className="w-4 h-4 inline mr-2" />
          Risk Limits
        </button>
        <button
          onClick={() => setActiveTab('var')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'var'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Activity className="w-4 h-4 inline mr-2" />
          VaR & CVaR
        </button>
        <button
          onClick={() => setActiveTab('stress')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'stress'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <AlertTriangle className="w-4 h-4 inline mr-2" />
          Stress Testing
        </button>
        <button
          onClick={() => setActiveTab('monitor')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'monitor'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Shield className="w-4 h-4 inline mr-2" />
          Monitor
        </button>
      </div>

      {/* Risk Limits Tab */}
      {activeTab === 'limits' && (
        <div className="space-y-4">
          <div className="bg-white border rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-4">Configure Risk Limits</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Position Size ($)
                </label>
                <input
                  type="number"
                  value={riskLimits.max_position_size}
                  onChange={(e) => setRiskLimits({ ...riskLimits, max_position_size: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Daily Loss ($)
                </label>
                <input
                  type="number"
                  value={riskLimits.max_daily_loss}
                  onChange={(e) => setRiskLimits({ ...riskLimits, max_daily_loss: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Drawdown (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={riskLimits.max_drawdown * 100}
                  onChange={(e) => setRiskLimits({ ...riskLimits, max_drawdown: parseFloat(e.target.value) / 100 })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Correlation
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={riskLimits.max_correlation}
                  onChange={(e) => setRiskLimits({ ...riskLimits, max_correlation: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Leverage
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={riskLimits.max_leverage}
                  onChange={(e) => setRiskLimits({ ...riskLimits, max_leverage: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Stop Loss (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={riskLimits.stop_loss_percent * 100}
                  onChange={(e) => setRiskLimits({ ...riskLimits, stop_loss_percent: parseFloat(e.target.value) / 100 })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>

            <button
              onClick={setRiskLimitsAPI}
              disabled={loading}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Limits'}
            </button>
          </div>
        </div>
      )}

      {/* VaR & CVaR Tab */}
      {activeTab === 'var' && (
        <div className="space-y-4">
          <div className="flex gap-4">
            <button
              onClick={calculateVaR}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
              Calculate VaR
            </button>
            <button
              onClick={calculateCVaR}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingDown className="w-4 h-4" />}
              Calculate CVaR
            </button>
          </div>

          {varResult && (
            <div className="bg-white border rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-4">Value at Risk (VaR)</h3>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Confidence Level</p>
                  <p className="text-2xl font-bold">{(varResult.confidence_level * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">VaR Amount</p>
                  <p className="text-2xl font-bold text-red-600">${Math.abs(varResult.var).toLocaleString()}</p>
                </div>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{varResult.interpretation}</p>
              </div>
            </div>
          )}

          {cvarResult && (
            <div className="bg-white border rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-4">Conditional Value at Risk (CVaR)</h3>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Confidence Level</p>
                  <p className="text-2xl font-bold">{(cvarResult.confidence_level * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">CVaR Amount</p>
                  <p className="text-2xl font-bold text-red-600">${Math.abs(cvarResult.cvar).toLocaleString()}</p>
                </div>
              </div>

              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <p className="text-sm text-orange-800">{cvarResult.interpretation}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Stress Testing Tab */}
      {activeTab === 'stress' && (
        <div className="space-y-4">
          <button
            onClick={runStressTest}
            disabled={loading}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Run Stress Test
          </button>

          {stressTestResults && (
            <div className="bg-white border rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-4">Stress Test Results</h3>

              <div className="space-y-3">
                {stressTestResults.scenarios.map((scenario, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border ${
                      scenario.portfolio_impact < -5000
                        ? 'bg-red-50 border-red-200'
                        : scenario.portfolio_impact < -2000
                        ? 'bg-orange-50 border-orange-200'
                        : 'bg-yellow-50 border-yellow-200'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{scenario.name}</span>
                      <span className={`font-bold ${
                        scenario.portfolio_impact < -5000 ? 'text-red-600' :
                        scenario.portfolio_impact < -2000 ? 'text-orange-600' : 'text-yellow-600'
                      }`}>
                        ${scenario.portfolio_impact.toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Monitor Tab */}
      {activeTab === 'monitor' && (
        <div className="space-y-4">
          <div className="bg-white border rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-lg">Real-time Risk Monitoring</h3>
              <button
                onClick={toggleMonitoring}
                disabled={loading}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                  monitoringActive
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                {monitoringActive ? 'Stop Monitoring' : 'Start Monitoring'}
              </button>
            </div>

            {monitoringActive ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="font-medium">Monitoring Active</span>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500">Position Risk</p>
                    <p className="text-xl font-bold text-green-600">Normal</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500">Portfolio Risk</p>
                    <p className="text-xl font-bold text-yellow-600">Moderate</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500">Market Risk</p>
                    <p className="text-xl font-bold text-green-600">Low</p>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Check Frequency:</strong> Every 5 minutes
                  </p>
                  <p className="text-sm text-blue-800 mt-1">
                    <strong>Alert Level:</strong> Warning
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Risk monitoring is currently inactive.</p>
                <p className="text-sm text-gray-500 mt-1">Click "Start Monitoring" to enable real-time risk checks.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskManagement;
