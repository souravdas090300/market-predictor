'use client';

import { useState } from 'react';
import { Calculator, Shield, TrendingUp, AlertTriangle } from 'lucide-react';

export default function RiskCalculatorPage() {
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({
    symbol: 'AAPL',
    entry_price: 150,
    stop_loss: 145,
    take_profit: 160,
    account_balance: 100000,
    max_risk_percent: 2,
  });

  const [results, setResults] = useState<any>(null);

  const handleCalculate = async () => {
    setLoading(true);
    
    // Simulate calculation
    setTimeout(() => {
      const riskAmount = params.entry_price - params.stop_loss;
      const potentialProfit = params.take_profit - params.entry_price;
      const riskPercent = (riskAmount / params.entry_price) * 100;
      const maxRiskAmount = (params.account_balance * params.max_risk_percent) / 100;
      const positionSize = maxRiskAmount / riskAmount;
      const riskRewardRatio = potentialProfit / riskAmount;

      setResults({
        symbol: params.symbol,
        entry_price: params.entry_price,
        stop_loss: params.stop_loss,
        take_profit: params.take_profit,
        position_size: positionSize,
        risk_amount: riskAmount * positionSize,
        risk_percent: riskPercent,
        potential_profit: potentialProfit * positionSize,
        potential_loss: riskAmount * positionSize,
        risk_reward_ratio: riskRewardRatio,
        recommended_position_size: positionSize,
        max_position_size: positionSize * 1.5,
      });
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Risk Calculator</h1>
        <p className="text-slate-400">Calculate position sizes and risk metrics for your trades</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Parameters */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <Calculator className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Trade Parameters</h2>
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
              <label className="block text-sm font-medium text-slate-300 mb-2">Entry Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={params.entry_price}
                onChange={(e) => setParams({ ...params, entry_price: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Stop Loss ($)</label>
              <input
                type="number"
                step="0.01"
                value={params.stop_loss}
                onChange={(e) => setParams({ ...params, stop_loss: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Take Profit ($)</label>
              <input
                type="number"
                step="0.01"
                value={params.take_profit}
                onChange={(e) => setParams({ ...params, take_profit: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Account Balance ($)</label>
              <input
                type="number"
                step="0.01"
                value={params.account_balance}
                onChange={(e) => setParams({ ...params, account_balance: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Max Risk (%)</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="10"
                value={params.max_risk_percent}
                onChange={(e) => setParams({ ...params, max_risk_percent: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <button
              onClick={handleCalculate}
              disabled={loading}
              className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate Risk'}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Risk Analysis</h2>
          </div>

          {results ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-slate-400 text-sm mb-1">Position Size</p>
                  <p className="text-white font-semibold text-xl">{results.position_size.toFixed(2)}</p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-slate-400 text-sm mb-1">Risk Amount</p>
                  <p className="text-red-400 font-semibold text-xl">${results.risk_amount.toFixed(2)}</p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-slate-400 text-sm mb-1">Risk %</p>
                  <p className="text-white font-semibold text-xl">{results.risk_percent.toFixed(2)}%</p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-slate-400 text-sm mb-1">Risk/Reward</p>
                  <p className="text-green-400 font-semibold text-xl">{results.risk_reward_ratio.toFixed(2)}</p>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-300">Potential Profit</span>
                  <span className="text-green-400 font-semibold">${results.potential_profit.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-300">Potential Loss</span>
                  <span className="text-red-400 font-semibold">${results.potential_loss.toFixed(2)}</span>
                </div>
                <di
