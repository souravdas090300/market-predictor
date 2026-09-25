'use client';

import { useState } from 'react';
import { BarChart3, TrendingUp, Target, Award, AlertCircle } from 'lucide-react';

export default function ModelPerformancePage() {
  const [selectedModel, setSelectedModel] = useState('xgboost_aapl');
  const [timeRange, setTimeRange] = useState('30d');

  const performanceData = {
    models: [
      { id: 'xgboost_aapl', name: 'XGBoost - AAPL', accuracy: 0.58, sharpe: 1.8, maxDrawdown: -0.08 },
      { id: 'lightgbm_msft', name: 'LightGBM - MSFT', accuracy: 0.55, sharpe: 1.5, maxDrawdown: -0.12 },
      { id: 'rf_googl', name: 'Random Forest - GOOGL', accuracy: 0.52, sharpe: 1.2, maxDrawdown: -0.15 },
    ],
    predictions: [
      { date: '2024-01-01', symbol: 'AAPL', predicted: 'bullish', actual: 'bullish', confidence: 0.65 },
      { date: '2024-01-02', symbol: 'AAPL', predicted: 'bullish', actual: 'bearish', confidence: 0.58 },
      { date: '2024-01-03', symbol: 'AAPL', predicted: 'neutral', actual: 'neutral', confidence: 0.51 },
      { date: '2024-01-04', symbol: 'AAPL', predicted: 'bearish', actual: 'bearish', confidence: 0.62 },
    ],
  };

  const selectedModelData = performanceData.models.find(m => m.id === selectedModel) || performanceData.models[0];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Model Performance</h1>
        <p className="text-slate-400">Track and analyze your prediction model performance</p>
      </div>

      {/* Model Selection */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Select Model</h2>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {performanceData.models.map(model => (
              <option key={model.id} value={model.id}>{model.name}</option>
            ))}
          </select>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-green-500" />
              <span className="text-slate-400 text-sm">Accuracy</span>
            </div>
            <p className="text-2xl font-bold text-white">{(selectedModelData.accuracy * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span className="text-slate-400 text-sm">Sharpe Ratio</span>
            </div>
            <p className="text-2xl font-bold text-white">{selectedModelData.sharpe.toFixed(2)}</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-slate-400 text-sm">Max Drawdown</span>
            </div>
            <p className="text-2xl font-bold text-white">{(selectedModelData.maxDrawdown * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
        <h3 className="text-white font-medium mb-3">Recent Predictions</h3>
        <div className="space-y-3">
          {performanceData.predictions.slice(0, 5).map((pred, index) => (
            <div key={index} className="bg-slate-900/50 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{pred.symbol}</span>
                <span className={pred.predicted === pred.actual ? "text-green-400 text-sm" : "text-red-400 text-sm"}>
                  {pred.predicted === pred.actual ? "Correct" : "Incorrect"}
                </span>
              </div>
              <p className="text-slate-400 text-xs">Confidence: {(pred.confidence * 100).toFixed(0)}%</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
