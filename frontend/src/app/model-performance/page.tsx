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
      { date: '2024-01-05', symbol: 'AAPL', predicted: 'bullish', actual: 'bullish', confidence: 0.70 },
    ],
    featureImportance: [
      { feature: 'RSI', importance: 0.25, trend: 'up' },
      { feature: 'MACD', importance: 0.20, trend: 'stable' },
      { feature: 'Moving Averages', importance: 0.18, trend: 'down' },
      { feature: 'Bollinger Bands', importance: 0.15, trend: 'stable' },
      { feature: 'Volume', importance: 0.12, trend: 'up' },
      { feature: 'Volatility', importance: 0.10, trend: 'down' },
    ],
  };

  const selectedModelData = performanceData.models.find(m => m.id === selectedModel);

  const getPredictionBadge = (predicted: string, actual: string) => {
    const isCorrect = predicted === actual;
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${
        isCorrect ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
      }`}>
        {isCorrect ? '✓' : '✗'}
      </span>
    );
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Model Performance</h1>
        <p className="text-slate-400">Track and analyze machine learning model performance</p>
      </div>

      {/* Model Selection */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <BarChart3 className="w-5 h-5 text-slate-400" />
          <h2 className="text-lg font-semibold text-white">Select Model</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {performanceData.models.map((model) => (
            <button
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-4 rounded-lg border transition-all ${
                selectedModel === model.id
                  ? 'bg-green-600/20 border-green-500'
                  : 'bg-slate-900/50 border-slate-700 hover:border-slate-600'
              }`}
            >
              <h3 className="text-white font-medium mb-2">{model.name}</h3>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div>
                  <p className="text-slate-400">Accuracy</p>
                  <p className="text-green-400 font-semibold">{(model.accuracy * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-slate-400">Sharpe</p>
                  <p className="text-white font-semibold">{model.sharpe.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-slate-400">Max DD</p>
                  <p className="text-red-400 font-semibold">{(model.maxDrawdown * 100).toFixed(1)}%</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {selectedModelData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Metrics */}
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-5 h-5 text-slate-400" />
              <h2 className="text-xl font-semibold text-white">Performance Metrics</h2>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-green-500" />
                  <p className="text-slate-400 text-sm">Accuracy</p>
                </div>
                <p className="text-green-400 font-semibold text-2xl">{(selectedModelData.accuracy * 100).toFixed(1)}%</p>
                <p className="text-slate-500 text-xs mt-1">vs baseline 51.2%</p>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="w-4 h-4 text-yellow-500" />
                  <p className="text-slate-400 text-sm">Sharpe Ratio</p>
                </div>
                <p className="text-white font-semibold text-2xl">{selectedModelData.sharpe.toFixed(2)}</p>
                <p className="text-slate-500 text-xs mt-1">Risk-adjusted return</p>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <p className="text-slate-400 text-sm">Max Drawdown</p>
                </div>
                <p className="text-red-400 font-semibold text-2xl">{(selectedModelData.maxDrawdown * 100).toFixed(1)}%</p>
                <p className="text-slate-500 text-xs mt-1">Worst decline</p>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <p className="text-slate-400 text-sm">Win Rate</p>
                </div>
                <p className="text-blue-400 font-semibold text-2xl">{(selectedModelData.accuracy * 0.9).toFixed(1)}%</p>
                <p className="text-slate-500 text-xs mt-1">Successful trades</p>
              </div>
            </div>
          </div>

          {/* Feature Importance */}
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
            <div className="flex items-center gap-3 mb-6">
              <BarChart3 className="w-5 h-5 text-slate-400" />
              <h2 className="text-xl font-semibold text-white">Feature Importance</h2>
            </div>

            <div className="space-y-3">
              {performanceData.featureImportance.map((item) => (
                <div key={item.feature} className="flex items-center gap-3">
                  <span className="text-slate-300 text-sm w-32">{item.feature}</span>
                  <div className="flex-1 bg-slate-700 rounded-full h-3">
                    <div
                      className="bg-green-600 h-3 rounded-full transition-all"
                      style={{ width: `${item.importance * 100}%` }}
                    />
                  </div>
                  <span className="text-white text-sm w-12 text-right">{(item.importance * 100).toFixed(0)}%</span>
                  <span className={`text-xs ${
                    item.trend === 'up' ? 'text-green-400' : 
                    item.trend === 'down' ? 'text-red-400' : 'text-yellow-400'
                  }`}>
                    {item.trend === 'up' ? '↑' : item.trend === 'down' ? '↓' : '→'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Predictions */}
          <div className="lg:col-span-2 bg
