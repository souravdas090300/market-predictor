'use client';

import { useState } from 'react';
import { Zap, Target, BarChart3, TrendingUp } from 'lucide-react';

export default function StrategyOptimizerPage() {
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({
    symbol: 'AAPL',
    strategy_type: 'momentum',
    lookback_min: 5,
    lookback_max: 20,
    holding_min: 1,
    holding_max: 10,
  });

  const [results, setResults] = useState<any>(null);

  const handleOptimize = async () => {
    setLoading(true);
    
    // Simulate optimization
    setTimeout(() => {
      setResults({
        symbol: params.symbol,
        strategy_type: params.strategy_type,
        best_parameters: {
          lookback_period: 12,
          holding_period: 5,
          threshold: 0.02,
        },
        performance: {
          total_return: 0.25,
          win_rate: 0.62,
          max_drawdown: -0.08,
          sharpe_ratio: 1.8,
        },
        backtest_results: Array.from({ length: 10 }, (_, i) => ({
          date: new Date(Date.now() - (10 - i) * 86400000).toISOString().split('T')[0],
          signal: i % 3 === 0 ? 'BUY' : i % 3 === 1 ? 'SELL' : 'HOLD',
          entry_price: 150 + Math.random() * 10,
          exit_price: 155 + Math.random() * 10,
          return: (Math.random() - 0.3) * 0.1,
        })),
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Strategy Optimizer</h1>
        <p className="text-slate-400">Optimize trading strategy parameters using historical data</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Optimization Parameters */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Optimization Parameters</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Symbol</label>
              <input
                type="text"
                value={params.symbol}
                onChange={(e) => setParams({ ...params, symbol: e.target.value.toUpperCase() })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Strategy Type</label>
              <select
                value={params.strategy_type}
                onChange={(e) => setParams({ ...params, strategy_type: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="momentum">Momentum</option>
                <option value="mean_reversion">Mean Reversion</option>
                <option value="breakout">Breakout</option>
                <option value="trend_following">Trend Following</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Min Lookback</label>
                <input
                  type="number"
                  value={params.lookback_min}
                  onChange={(e) => setParams({ ...params, lookback_min: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Max Lookback</label>
                <input
                  type="number"
                  value={params.lookback_max}
                  onChange={(e) => setParams({ ...params, lookback_max: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Min Holding</label>
                <input
                  type="number"
                  value={params.holding_min}
                  onChange={(e) => setParams({ ...params, holding_min: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Max Holding</label>
                <input
                  type="number"
                  value={params.holding_max}
                  onChange={(e) => setParams({ ...params, holding_max: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <button
              onClick={handleOptimize}
              disabled={loading}
              className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Target className="w-5 h-5" />
              {loading ? 'Optimizing...' : 'Run Optimization'}
            </button>
          </div>
        </div>

        {/* Optimization Results */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <BarChart3 className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Optimization Results</h2>
          </div>

          {results ? (
            <div className="space-y-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-3">Optimal Parameters</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-slate-400 text-sm">Lookback Period</p>
                    <p className="text-white font-semibold">{results.best_parameters.lookback_period} days</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Holding Period</p>
                    <p className="text-white font-semibold">{results.best_parameters.holding_period} days</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Threshold</p>
                    <p className="text-white font-semibold">{(results.best_parameters.threshold * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-3">Performance Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-slate-400 text-sm">Total Return</p>
                    <p className="text-green-400 font-semibold text-xl">{(results.performance.total_return * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Win Rate</p>
                    <p className="text-green-400 font-semibold text-xl">{(results.performance.win_rate * 100).toFixed(1)}%</p
