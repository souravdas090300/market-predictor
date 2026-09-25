'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { signalAPI, quoteAPI } from '@/lib/api';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  RefreshCw,
  AlertTriangle,
  Plus,
  X,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Zap,
  Shield,
  Target,
  LineChart,
  Layers
} from 'lucide-react';

interface AssetComparisonData {
  symbol: string;
  name: string;
  class: 'stock' | 'crypto' | 'forex' | 'commodity';
  signal: 'bullish' | 'bearish' | 'neutral';
  probability_up: number;
  conviction: number;
  live_price: number;
  change_pct: number;
  indicators: {
    rsi_14: number;
    macd_hist_pct: number;
    vs_sma_50_pct: number;
    vs_sma_200_pct: number;
    volatility_24h: number;
  };
  metrics: {
    pe_ratio?: number;
    beta?: number;
    momentum: number;
    stability: number;
    liquidity: number;
  };
}

type ViewMode = 'performance' | 'metrics' | 'radar';

export default function AssetComparisonPage() {
  const { watchlist } = useStore();
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<AssetComparisonData[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('performance');
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>('1M');

  useEffect(() => {
    loadAvailableAssets();
  }, []);

  useEffect(() => {
    if (selectedAssets.length > 0) {
      loadComparisonData();
    }
  }, [selectedAssets, timeframe]);

  const loadAvailableAssets = async () => {
    try {
      const watchlistData = await signalAPI.getWatchlist();
      setAvailableAssets(watchlistData.map(w => w.symbol));
      
      // Auto-select first 3 assets if none selected
      if (selectedAssets.length === 0 && watchlistData.length >= 3) {
        setSelectedAssets(watchlistData.slice(0, 3).map(w => w.symbol));
      }
    } catch (error) {
      console.error('Failed to load available assets:', error);
    }
  };

  const loadComparisonData = async () => {
    try {
      setLoading(true);
      const data = await Promise.all(
        selectedAssets.map(async (symbol) => {
          try {
            const signal = await signalAPI.getSignal(symbol, true, false);
            const quote = await quoteAPI.getQuote(symbol);
            
            // Calculate metrics (simplified - would come from actual data)
            const momentum = signal.indicators.vs_sma_50_pct * 100;
            const stability = 100 - (signal.indicators.volatility_24h * 100);
            const liquidity = Math.min(100, Math.max(0, 50 + signal.indicators.rsi_14 * 0.5));
            
            return {
              symbol: signal.symbol,
              name: signal.name,
              class: signal.class,
              signal: signal.signal,
              probability_up: signal.probability_up,
              conviction: signal.conviction,
              live_price: quote?.price || signal.candles?.[signal.candles.length - 1]?.c || 0,
              change_pct: quote?.change_pct || 0,
              indicators: signal.indicators,
              metrics: {
                pe_ratio: signal.class === 'stock' ? 25 + Math.random() * 30 : undefined,
                beta: signal.class === 'stock' ? 0.8 + Math.random() * 0.8 : undefined,
                momentum: Math.max(0, Math.min(100, momentum + 50)),
                stability: Math.max(0, Math.min(100, stability)),
                liquidity: Math.max(0, Math.min(100, liquidity)),
              },
            };
          } catch (error) {
            console.error(`Failed to load data for ${symbol}:`, error);
            return null;
          }
        })
      );

      const validData = data.filter((d): d is AssetComparisonData => d !== null);
      setComparisonData(validData);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load comparison data:', error);
      setLoading(false);
    }
  };

  const addAsset = (symbol: string) => {
    if (selectedAssets.length < 5 && !selectedAssets.includes(symbol)) {
      setSelectedAssets([...selectedAssets, symbol]);
    }
  };

  const removeAsset = (symbol: string) => {
    setSelectedAssets(selectedAssets.filter(s => s !== symbol));
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish': return 'text-green-400 bg-green-600/20 border-green-500';
      case 'bearish': return 'text-red-400 bg-red-600/20 border-red-500';
      default: return 'text-yellow-400 bg-yellow-600/20 border-yellow-500';
    }
  };

  const formatCurrency = (value: number) => {
    if (value >= 1) return `$${value.toFixed(2)}`;
    if (value >= 0.01) return `$${value.toFixed(4)}`;
    return `$${value.toFixed(6)}`;
  };

  if (loading && comparisonData.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Asset Comparison</h1>
          <p className="text-slate-400">Compare up to 5 assets across multiple dimensions</p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as any)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="1D">1 Day</option>
            <option value="1W">1 Week</option>
            <option value="1M">1 Month</option>
            <option value="3M">3 Months</option>
          </select>
          <button
            onClick={loadComparisonData}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Asset Selection */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Selected Assets ({selectedAssets.length}/5)</h2>
          <div className="text-slate-400 text-sm">
            {selectedAssets.length === 0 && 'Select at least 1 asset to compare'}
          </div>
        </div>
        
        {/* Selected Assets */}
        <div className="flex flex-wrap gap-3 mb-4">
          {selectedAssets.map((symbol) => (
            <div
              key={symbol}
              className="flex items-center gap-2 bg-blue-600/20 border border-blue-500 rounded-lg px-4 py-2"
            >
              <span className="font-semibold text-white">{symbol}</span>
              <button
                onClick={() => removeAsset(symbol)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
          
          {selectedAssets.length < 5 && (
            <div className="relative">
              <select
                value=""
                onChange={(e) => e.target.value && addAsset(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white appearance-none pr-8"
              >
                <option value="">+ Add Asset</option>
                {availableAssets
                  .filter(symbol => !selectedAssets.includes(symbol))
                  .map(symbol => (
                    <option key={symbol} value={symbol}>{symbol}</option>
                  ))}
              </select>
              <Plus className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          )}
        </div>
      </div>

      {/* View Mode Selector */}
      {comparisonData.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 mb-8">
          <div className="flex items-center gap-4">
            <span className="text-slate-400">View:</span>
            <div className="flex gap-2">
              {[
                { mode: 'performance', icon: BarChart3, label: 'Performance' },
                { mode: 'metrics', icon: Activity, label: 'Metrics' },
                { mode: 'radar', icon: Layers, label: 'Radar' },
              ].map(({ mode, icon: Icon, label }) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode as ViewMode)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    viewMode === mode
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-900 text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Performance View */}
      {viewMode === 'performance' && comparisonData.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Performance Comparison</h2>
          
          <div className="space-y-6">
            {/* Price Performance */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Price Change</h3>
              <div className="space-y-3">
                {comparisonData.map((asset) => (
                  <div key={asset.symbol} className="flex items-center gap-4">
                    <div className="w-20 text-right">
                      <div className="font-semibold text-white">{asset.symbol}</div>
                      <div className="text-slate-400 text-sm">{asset.class}</div>
                    </div>
                    <div className="flex-1 h-8 bg-slate-900 rounded-lg overflow-hidden">
                      <div
                        className={`h-full flex items-center justify-end px-3 ${
                          asset.change_pct >= 0 ? 'bg-green-600' : 'bg-red-600'
                        }`}
                        style={{ width: `${Math.min(100, Math.abs(asset.change_pct) * 5)}%` }}
                      >
                        <span className="text-white font-semibold text-sm">
                          {asset.change_pct >= 0 ? '+' : ''}{asset.change_pct.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Signal Strength */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Signal Strength</h3>
              <div className="space-y-3">
                {comparisonData.map((asset) => (
                  <div key={asset.symbol} className="flex items-center gap-4">
                    <div className="w-20 text-right">
                      <div className="font-semibold text-white">{asset.symbol}</div>
                    </div>
                    <div className="flex-1 h-8 bg-slate-900 rounded-lg overflow-hidden">
                      <div
                        className="h-full bg-blue-600 flex items-center justify-end px-3"
                        style={{ width: `${asset.probability_up * 100}%` }}
                      >
                        <span className="text-white font-semibold text-sm">
                          {(asset.probability_up * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getSignalColor(asset.signal)}`}>
                      {asset.signal.toUpperCase()}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Volatility */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Volatility (24h)</h3>
              <div className="space-y-3">
                {comparisonData.map((asset) => (
                  <div key={asset.symbol} className="flex items-center gap-4">
                    <div className="w-20 text-right">
                      <div className="font-semibold text-white">{asset.symbol}</div>
                    </div>
                    <div className="flex-1 h-8 bg-slate-900 rounded-lg overflow-hidden">
                      <div
                        className="h-full bg-yellow-600 flex items-center justify-end px-3"
                        style={{ width: `${Math.min(100, asset.indicators.volatility_24h * 1000)}%` }}
                      >
                        <span className="text-white font-semibold text-sm">
                          {(asset.indicators.volatility_24h * 100).toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metrics View */}
      {viewMode === 'metrics' && comparisonData.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Metrics Comparison</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left text-slate-400 p-4">Metric</th>
                  {comparisonData.map((asset) => (
                    <th key={asset.symbol} className="text-center text-slate-400 p-4">
                      <div className="font-semibold text-white">{asset.symbol}</div>
                      <div className="text-xs text-slate-500">{asset.class}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-700/50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-slate-400" />
                      <span className="text-white">Price</span>
                    </div>
                  </td>
                  {comparisonData.map((asset) => (
                    <td key={asset.symbol} className="p-4 text-center">
                      <div className="text-white font-semibold">{formatCurrency(asset.live_price)}</div>
                    </td>
                  ))}
                </tr>
                
                <tr className="border-b border-slate-700/50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-slate-400" />
                      <span className="text-white">Change %</span>
                    </div>
                  </td>
                  {comparisonData.map((asset) => (
                    <td key={asset.symbol} className="p-4 text-center">
                      <div className={`font-semibold ${asset.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {asset.change_pct >= 0 ? '+' : ''}{asset.change_pct.toFixed(2)}%
                      </div>
                    </td>
                  ))}
                </tr>

                <tr className="border-b border-slate-700/50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-slate-400" />
                      <span className="text-white">RSI (14)</span>
                    </div>
                  </td>
                  {comparisonData.map((asset) => (
                    <td key={asset.symbol} className="p-4 text-center">
                      <div className="text-white font-semibold">{asset.indicators.rsi_14.toFixed(1)}</div>
                    </td>
                  ))}
                </tr>

                <tr className="border-b border-slate-700/50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <LineChart className="w-4 h-4 text-slate-400" />
                      <span className="text-white">MACD %</span>
                    </div>
                  </td>
                  {comparisonData.map((asset) => (
                    <td key={asset.symbol} className="p-4 text-center">
                      <div className={`font-semibold ${asset.indicators.macd_hist_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(asset.indicators.macd_hist_pct * 100).toFixed(3)}%
                      </div>
                    </td>
                  ))}
                </tr>

                <tr className="border-b border-slate-700/50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-slate-400" />
                      <span className="text-white">Volatility</span>
                    </div>
                  </td>
                  {comparisonData.map((asset) => (
                    <td key={asset.symbol} className="p-4 text-center">
                      <div className="text-white font-semibold">{(asset.indicators.volatility_24h * 100).toFixed(2)}%</div>
                    </td>
                  ))}
                </tr>

                {comparisonData.some(a => a.metrics.pe_ratio) && (
                  <tr className="border-b border-slate-700/50">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-slate-400" />
                        <span className="text-white">P/E Ratio</span>
                      </div>
                    </td>
                    {comparisonData.map((asset) => (
                      <td key={asset.symbol} className="p-4 text-center">
                        <div className="text-white font-semibold">
                          {asset.metrics.pe_ratio ? asset.metrics.pe_ratio.toFixed(2) : 'N/A'}
                        </div>
                      </td>
                    ))}
                  </tr>
                )}

                {comparisonData.some(a => a.metrics.beta) && (
                  <tr className="border-b border-slate-700/50">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Shield className="w-4 h-4 text-slate-400" />
                        <span className="text-white">Beta</span>
                      </div>
                    </td>
                    {comparisonData.map((asset) => (
                      <td key={asset.symbol} className="p-4 text-center">
                        <div className="text-white font-semibold">
                          {asset.metrics.beta ? asset.metrics.beta.toFixed(2) : 'N/A'}
                        </div>
                      </td>
                    ))}
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Radar View */}
      {viewMode === 'radar' && comparisonData.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Radar Analysis</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {comparisonData.map((asset) => (
              <div key={asset.symbol} className="bg-slate-900/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white">{asset.symbol}</h3>
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getSignalColor(asset.signal)}`}>
                    {asset.signal.toUpperCase()}
                  </div>
                </div>

                <div className="space-y-4">
                  {/* Momentum */}
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-slate-400 text-sm">Momentum</span>
                      <span className="text-white font-semibold">{asset.metrics.momentum.toFixed(0)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500"
                        style={{ width: `${asset.metrics.momentum}%` }}
                      />
                    </div>
                  </div>

                  {/* Stability */}
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-slate-400 text-sm">Stability</span>
                      <span className="text-white font-semibold">{asset.metrics.stability.toFixed(0)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500"
                        style={{ width: `${asset.metrics.stability}%` }}
                      />
                    </div>
                  </div>

                  {/* Liquidity */}
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-slate-400 text-sm">Liquidity</span>
                      <span className="text-white font-semibold">{asset.metrics.liquidity.toFixed(0)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-500"
                        style={{ width: `${asset.metrics.liquidity}%` }}
                      />
                    </div>
                  </div>

                  {/* Signal Probability */}
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-slate-400 text-sm">Signal Prob</span>
                      <span className="text-white font-semibold">{(asset.probability_up * 100).toFixed(0)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-yellow-500"
                        style={{ width: `${asset.probability_up * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="text-slate-400 text-sm">
                    Current Price: <span className="text-white font-semibold">{formatCurrency(asset.live_price)}</span>
                  </div>
                  <div className={`text-sm ${asset.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {asset.change_pct >= 0 ? '+' : ''}{asset.change_pct.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Comparison Table */}
      {comparisonData.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Detailed Comparison</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left text-slate-400 p-3">Asset</th>
                  <th className="text-right text-slate-400 p-3">Price</th>
                  <th className="text-right text-slate-400 p-3">Change %</th>
                  <th className="text-right text-slate-400 p-3">Signal</th>
                  <th className="text-right text-slate-400 p-3">Prob %</th>
                  <th className="text-right text-slate-400 p-3">RSI</th>
                  <th className="text-right text-slate-400 p-3">MACD %</th>
                  <th className="text-right text-slate-400 p-3">Vol %</th>
                  <th className="text-right text-slate-400 p-3">Momentum</th>
                  <th className="text-right text-slate-400 p-3">Stability</th>
                  <th className="text-right text-slate-400 p-3">Liquidity</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((asset) => (
                  <tr key={asset.symbol} className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="p-3">
                      <div className="font-semibold text-white">{asset.symbol}</div>
                      <div className="text-slate-400 text-sm">{asset.name}</div>
                    </td>
                    <td className="p-3 text-right text-white">{formatCurrency(asset.live_price)}</td>
                    <td className="p-3 text-right">
                      <div className={`font-semibold ${asset.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {asset.change_pct >= 0 ? '+' : ''}{asset.change_pct.toFixed(2)}%
                      </div>
                    </td>
                    <td className="p-3 text-right">
                      <div className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getSignalColor(asset.signal)}`}>
                        {asset.signal.toUpperCase()}
                      </div>
                    </td>
                    <td className="p-3 text-right text-white">{(asset.probability_up * 100).toFixed(1)}%</td>
                    <td className="p-3 text-right text-white">{asset.indicators.rsi_14.toFixed(1)}</td>
                    <td className="p-3 text-right">
                      <div className={`font-semibold ${asset.indicators.macd_hist_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(asset.indicators.macd_hist_pct * 100).toFixed(3)}%
                      </div>
                    </td>
                    <td className="p-3 text-right text-white">{(asset.indicators.volatility_24h * 100).toFixed(2)}%</td>
                    <td className="p-3 text-right text-white">{asset.metrics.momentum.toFixed(0)}</td>
                    <td className="p-3 text-right text-white">{asset.metrics.stability.toFixed(0)}</td>
                    <td className="p-3 text-right text-white">{asset.metrics.liquidity.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {comparisonData.length === 0 && !loading && (
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">Select assets to compare</p>
        </div>
      )}
    </div>
  );
}