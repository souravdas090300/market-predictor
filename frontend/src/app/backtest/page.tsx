'use client';

import { useState } from 'react';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { Play, BarChart3, TrendingUp, TrendingDown, Target, Award, Settings } from 'lucide-react';

interface BacktestConfig {
  symbol: string;
  strategy: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  positionSize: number;
  stopLoss: number;
  takeProfit: number;
}

interface BacktestResult {
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  averageWin: number;
  averageLoss: number;
  profitFactor: number;
}

export default function BacktestPage() {
  const { user } = useStore();
  const [config, setConfig] = useState<BacktestConfig>({
    symbol: 'AAPL',
    strategy: 'momentum',
    startDate: '2023-01-01',
    endDate: '2024-01-01',
    initialCapital: 10000,
    positionSize: 1,
    stopLoss: 5,
    takeProfit: 10,
  });
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<BacktestResult | null>(null);

  const strategies = [
    { id: 'momentum', name: 'Momentum Strategy', description: 'Buy when price above SMA' },
    { id: 'mean_reversion', name: 'Mean Reversion', description: 'Buy when price below Bollinger Bands' },
    { id: 'breakout', name: 'Breakout Strategy', description: 'Trade price breakouts' },
    { id: 'trend_following', name: 'Trend Following', description: 'Follow MACD trends' },
  ];

  const handleRunBacktest = async () => {
    setRunning(true);
    // Simulate backtest - replace with actual API call
    setTimeout(() => {
      setResults({
        totalReturn: 0.23,
        sharpeRatio: 1.8,
        maxDrawdown: -0.12,
        winRate: 0.58,
        totalTrades: 45,
        winningTrades: 26,
        losingTrades: 19,
        averageWin: 0.045,
        averageLoss: -0.032,
        profitFactor: 2.1,
      });
      setRunning(false);
    }, 2000);
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-slate-400 mb-6">Please sign in to access backtesting</p>
          <a href="/auth/login" className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
            Sign In
          </a>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <MobileNav />
      
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Strategy Backtesting</h1>
          <p className="text-slate-400">Test trading strategies with historical data</p>
        </div>

        {/* Configuration */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Settings className="w-5 h-5 text-slate-400" />
            <h3 className="text-lg font-semibold text-white">Backtest Configuration</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
              <label className="block text-sm font-medium text-slate-300 mb-2">Strategy</label>
              <select
                value={config.strategy}
                onChange={(e) => setConfig({ ...config, strategy: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {strategies.map(strategy => (
                  <option key={strategy.id} value={strategy.id}>{strategy.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Start Date</label>
              <input
                type="date"
                value={config.startDate}
                onChange={(e) => setConfig({ ...config, startDate: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">End Date</label>
              <input
                type="date"
                value={config.endDate}
                onChange={(e) => setConfig({ ...config, endDate: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Initial Capital ($)</label>
              <input
                type="number"
                value={config.initialCapital}
                onChange={(e) => setConfig({ ...config, initialCapital: parseFloat(e.target.value) || 0 })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Position Size</label>
              <input
                type="number"
                value={config.positionSize}
                onChange={(e) => setConfig({ ...config, positionSize: parseFloat(e.target.value) || 0 })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Stop Loss (%)</label>
              <input
                type="number"
                value={config.stopLoss}
                onChange={(e) => setConfig({ ...config, stopLoss: parseFloat(e.target.value) || 0 })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Take Profit (%)</label>
              <input
                type="number"
                value={config.takeProfit}
                onChange={(e) => setConfig({ ...config, takeProfit: parseFloat(e.target.value) || 0 })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>
          
          <button
            onClick={handleRunBacktest}
            disabled={running}
            className="mt-4 flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {running ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Running Backtest...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Backtest
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-slate-400" />
              <h3 className="text-lg font-semibold text-white">Backtest Results</h3>
            </div>
            
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-slate-400 text-sm">Total Return</span>
                </div>
                <p className="text-2xl font-bold text-white">{(results.totalReturn * 100).toFixed(1)}%</p>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-blue-500" />
                  <span className="text-slate-400 text-sm">Sharpe Ratio</span>
                </div>
                <p className="text-2xl font-bold text-white">{results.sharpeRatio.toFixed(2)}</p>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="w-4 h-4 text-red-500" />
                  <span className="text-slate-400 text-sm">Max Drawdown</span>
                </div>
                <p className="text-2xl font-bold text-white">{(results.maxDrawdown * 100).toFixed(1)}%</p>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="w-4 h-4 text-yellow-500" />
                  <span className="text-slate-400 text-sm">Win Rate</span>
                </div>
                <p className="text-2xl font-bold text-white">{(results.winRate * 100).toFixed(1)}%</p>
              </div>
            </div>
            
            {/* Detailed Stats */}
            <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
              <h4 className="text-white font-medium mb-4">Trade Statistics</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-slate-400 text-sm">Total Trades</p>
                  <p className="text-xl font-bold text-white">{results.totalTrades}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Winning Trades</p>
                  <p className="text-xl font-bold text-green-400">{results.winningTrades}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Losing Trades</p>
                  <p className="text-xl font-bold text-red-400">{results.losingTrades}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Profit Factor</p>
                  <p className="text-xl font-bold text-white">{results.profitFactor.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Average Win</p>
                  <p className="text-xl font-bold text-green-400">{(results.averageWin * 100).toFixed(2)}%</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Average Loss</p>
                  <p className="text-xl font-bold text-red-400">{(results.averageLoss * 100).toFixed(2)}%</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
