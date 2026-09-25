'use client';

import { useState } from 'react';
import { Play, Settings, BarChart3, Download, RefreshCw } from 'lucide-react';

export default function ModelTrainingPage() {
  const [training, setTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [config, setConfig] = useState({
    symbol: 'AAPL',
    lookback_days: 252,
    model_type: 'xgboost',
    validation_method: 'walk_forward',
    test_size: 0.2,
    features: ['rsi', 'macd', 'moving_averages', 'bollinger', 'volume'],
  });

  const [results, setResults] = useState<any>(null);

  const handleTrain = async () => {
    setTraining(true);
    setProgress(0);
    
    // Simulate training progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 5;
      });
    }, 200);

    // Simulate training completion
    setTimeout(() => {
      setResults({
        model_id: 'model_' + Date.now(),
        symbol: config.symbol,
        training_status: 'completed',
        accuracy: 0.58,
        feature_importance: [
          { feature: 'RSI', importance: 0.25 },
          { feature: 'MACD', importance: 0.20 },
          { feature: 'Moving Averages', importance: 0.18 },
          { feature: 'Bollinger Bands', importance: 0.15 },
          { feature: 'Volume', importance: 0.12 },
          { feature: 'Volatility', importance: 0.10 },
        ],
        training_time: 45.2,
        trained_at: new Date().toISOString(),
      });
      setTraining(false);
      clearInterval(interval);
    }, 4000);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Model Training</h1>
        <p className="text-slate-400">Train and optimize machine learning models for market prediction</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Training Configuration */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <Settings className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Training Configuration</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Symbol</label>
              <input
                type="text"
                value={config.symbol}
                onChange={(e) => setConfig({ ...config, symbol: e.target.value.toUpperCase() })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Lookback Days</label>
              <input
                type="number"
                value={config.lookback_days}
                onChange={(e) => setConfig({ ...config, lookback_days: parseInt(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Model Type</label>
              <select
                value={config.model_type}
                onChange={(e) => setConfig({ ...config, model_type: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="xgboost">XGBoost</option>
                <option value="lightgbm">LightGBM</option>
                <option value="random_forest">Random Forest</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Validation Method</label>
              <select
                value={config.validation_method}
                onChange={(e) => setConfig({ ...config, validation_method: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="walk_forward">Walk Forward</option>
                <option value="time_series_split">Time Series Split</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Test Size</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="0.5"
                value={config.test_size}
                onChange={(e) => setConfig({ ...config, test_size: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Features</label>
              <div className="space-y-2">
                {['rsi', 'macd', 'moving_averages', 'bollinger', 'volume', 'volatility'].map((feature) => (
                  <label key={feature} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={config.features.includes(feature)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setConfig({ ...config, features: [...config.features, feature] });
                        } else {
                          setConfig({ ...config, features: config.features.filter(f => f !== feature) });
                        }
                      }}
                      className="rounded"
                    />
                    <span className="text-white capitalize">{feature.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={handleTrain}
              disabled={training}
              className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {training ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Training... {progress}%
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Training
                </>
              )}
            </button>
          </div>
        </div>

        {/* Training Results */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <BarChart3 className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Training Results</h2>
          </div>

          {training ? (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Training Progress</span>
                  <span className="text-white">{progress}%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
              <p className="text-slate-400 text-sm">Training model on {config.symbol} with learning rate {config.features.learning_rate}</p>
            </div>
          
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-400">Start training to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
