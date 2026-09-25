'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { signalAPI } from '@/lib/api';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  RefreshCw,
  AlertTriangle,
  Info,
  LineChart,
  Zap
} from 'lucide-react';

interface TechnicalIndicatorData {
  symbol: string;
  name: string;
  class: string;
  rsi_14: number;
  macd_hist_pct: number;
  vs_sma_50_pct: number;
  volatility_24h: number;
  signal: 'bullish' | 'bearish' | 'neutral';
  probability_up: number;
}

export default function TechnicalIndicatorsPage() {
  const { watchlist } = useStore();
  const [indicators, setIndicators] = useState<TechnicalIndicatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M'>('1M');

  useEffect(() => {
    loadTechnicalIndicators();
  }, [timeframe]);

  const loadTechnicalIndicators = async () => {
    try {
      setLoading(true);
      const watchlistData = await signalAPI.getWatchlist();
      
      const indicatorsData = await Promise.all(
        watchlistData.slice(0, 10).map(async (asset) => {
          try {
            const signal = await signalAPI.getSignal(asset.symbol, true, false);
            
            return {
              symbol: signal.symbol,
              name: signal.name,
              class: signal.class,
              rsi_14: signal.indicators.rsi_14,
              macd_hist_pct: signal.indicators.macd_hist_pct,
              vs_sma_50_pct: signal.indicators.vs_sma_50_pct,
              volatility_24h: signal.indicators.volatility_24h,
              signal: signal.signal,
              probability_up: signal.probability_up,
            };
          } catch (error) {
            console.error(`Failed to load indicators for ${asset.symbol}:`, error);
            return null;
          }
        })
      );

      const validIndicators = indicatorsData.filter((i): i is TechnicalIndicatorData => i !== null);
      setIndicators(validIndicators);
      if (validIndicators.length > 0) {
        setSelectedAsset(validIndicators[0].symbol);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to load technical indicators:', error);
      setLoading(false);
    }
  };

  const getRSIStatus = (rsi: number) => {
    if (rsi >= 70) return { status: 'Overbought', color: 'text-red-400', bg: 'bg-red-600/20' };
    if (rsi <= 30) return { status: 'Oversold', color: 'text-green-400', bg: 'bg-green-600/20' };
    return { status: 'Neutral', color: 'text-yellow-400', bg: 'bg-yellow-600/20' };
  };

  const getMACDStatus = (macd: number) => {
    if (macd > 0.001) return { status: 'Strong Bullish', color: 'text-green-400', bg: 'bg-green-600/20' };
    if (macd > 0) return { status: 'Bullish', color: 'text-green-300', bg: 'bg-green-600/10' };
    if (macd < -0.001) return { status: 'Strong Bearish', color: 'text-red-400', bg: 'bg-red-600/20' };
    return { status: 'Bearish', color: 'text-red-300', bg: 'bg-red-600/10' };
  };

  const selectedAssetData = indicators.find(i => i.symbol === selectedAsset);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Technical Indicators</h1>
          <p className="text-slate-400">Advanced technical analysis for all tracked assets</p>
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
          </select>
          <button
            onClick={loadTechnicalIndicators}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Educational Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-white">RSI (Relative Strength Index)</h3>
          </div>
          <p className="text-slate-400 text-sm">
            Measures momentum. Above 70 = overbought, below 30 = oversold.
          </p>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <LineChart className="w-5 h-5 text-green-400" />
            <h3 className="font-semibold text-white">MACD (Moving Average Convergence Divergence)</h3>
          </div>
          <p className="text-slate-400 text-sm">
            Trend-following momentum indicator. Positive = bullish, negative = bearish.
          </p>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            <h3 className="font-semibold text-white">Volatility</h3>
          </div>
          <p className="text-slate-400 text-sm">
            Measures price fluctuation. Higher volatility = greater risk/opportunity.
          </p>
        </div>
      </div>

      {/* Asset Selection */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Select Asset</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {indicators.map((indicator) => (
            <button
              key={indicator.symbol}
              onClick={() => setSelectedAsset(indicator.symbol)}
              className={`p-3 rounded-lg transition-colors ${
                selectedAsset === indicator.symbol
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="font-semibold">{indicator.symbol}</div>
              <div className="text-xs opacity-75">{indicator.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Detailed Analysis */}
      {selectedAssetData && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">
              {selectedAssetData.symbol} - {selectedAssetData.name}
            </h2>
            <div className={`px-4 py-2 rounded-full font-semibold ${
              selectedAssetData.signal === 'bullish' ? 'bg-green-600/20 text-green-400' :
              selectedAssetData.signal === 'bearish' ? 'bg-red-600/20 text-red-400' :
              'bg-yellow-600/20 text-yellow-400'
            }`}>
              {selectedAssetData.signal.toUpperCase()}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* RSI Analysis */}
            <div className="bg-slate-900/50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">RSI Analysis</h3>
                <Activity className="w-5 h-5 text-slate-400" />
              </div>
              
              <div className="mb-4">
                <div className="text-4xl font-bold text-white mb-2">
                  {selectedAssetData.rsi_14.toFixed(1)}
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getRSIStatus(selectedAssetData.rsi_14).bg} ${getRSIStatus(selectedAssetData.rsi_14).color}`}>
                  {getRSIStatus(selectedAssetData.rsi_14).status}
                </div>
              </div>

              <div className="relative h-4 bg-slate-700 rounded-full overflow-hidden mb-2">
                <div 
                  className="absolute h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                  style={{ width: '100%' }}
                />
                <div 
                  className="absolute h-full w-1 bg-white"
                  style={{ left: `${selectedAssetData.rsi_14}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-400">
                <span>0 (Oversold)</span>
                <span>50 (Neutral)</span>
                <span>100 (Overbought)</span>
              </div>
            </div>

            {/* MACD Analysis */}
            <div className="bg-slate-900/50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">MACD Analysis</h3>
                <LineChart className="w-5 h-5 text-slate-400" />
              </div>
              
              <div className="mb-4">
                <div className="text-4xl font-bold text-white mb-2">
                  {(selectedAssetData.macd_hist_pct * 100).toFixed(3)}%
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getMACDStatus(selectedAssetData.macd_hist_pct).bg} ${getMACDStatus(selectedAssetData.macd_hist_pct).color}`}>
                  {getMACDStatus(selectedAssetData.macd_hist_pct).status}
                </div>
              </div>

              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-400" />
                  <span className="text-slate-400">Positive = Bullish</span>
                </div>
                <div className="flex items-center gap-2">
                  <TrendingDown className="w-4 h-4 text-red-400" />
                  <span className="text-slate-400">Negative = Bearish</span>
                </div>
              </div>
            </div>

            {/* Moving Average Analysis */}
            <div className="bg-slate-900/50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Moving Average Analysis</h3>
                <BarChart3 className="w-5 h-5 text-slate-400" />
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400">vs SMA 50</span>
                    <span className={`font-semibold ${selectedAssetData.vs_sma_50_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(selectedAssetData.vs_sma_50_pct * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${selectedAssetData.vs_sma_50_pct >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ width: `${Math.abs(selectedAssetData.vs_sma_50_pct * 100)}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400">Signal Probability</span>
                    <span className="font-semibold text-white">
                      {(selectedAssetData.probability_up * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500"
                      style={{ width: `${selectedAssetData.probability_up * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Volatility Analysis */}
            <div className="bg-slate-900/50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Volatility Analysis</h3>
                <Zap className="w-5 h-5 text-slate-400" />
              </div>
              
              <div className="mb-4">
                <div className="text-4xl font-bold text-white mb-2">
                  {(selectedAssetData.volatility_24h * 100).toFixed(2)}%
                </div>
                <div className="text-slate-400">24-hour volatility</div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Info className="w-4 h-4 text-blue-400" />
                  <span className="text-slate-400">
                    Higher volatility indicates greater price swings and risk.
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  <span className="text-slate-400">
                    Consider position sizing based on volatility levels.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Overview Table */}
      <div className="mt-8 bg-slate-800/50 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-bold text-white mb-4">All Assets Overview</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left text-slate-400 p-3">Symbol</th>
                <th className="text-left text-slate-400 p-3">RSI</th>
                <th className="text-left text-slate-400 p-3">MACD</th>
                <th className="text-left text-slate-400 p-3">vs SMA 50</th>
                <th className="text-left text-slate-400 p-3">Volatility</th>
                <th className="text-left text-slate-400 p-3">Signal</th>
              </tr>
            </thead>
            <tbody>
              {indicators.map((indicator) => (
                <tr key={indicator.symbol} className="border-b border-slate-700/50 hover:bg-slate-900/30">
                  <td className="p-3">
                    <div className="font-semibold text-white">{indicator.symbol}</div>
                    <div className="text-slate-400 text-sm">{indicator.name}</div>
                  </td>
                  <td className="p-3">
                    <div className="text-white">{indicator.rsi_14.toFixed(1)}</div>
                    <div className={`text-xs ${getRSIStatus(indicator.rsi_14).color}`}>
                      {getRSIStatus(indicator.rsi_14).status}
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="text-white">{(indicator.macd_hist_pct * 100).toFixed(3)}%</div>
                    <div className={`text-xs ${getMACDStatus(indicator.macd_hist_pct).color}`}>
                      {getMACDStatus(indicator.macd_hist_pct).status}
                    </div>
                  </td>
                  <td className="p-3">
                    <div className={`text-white ${indicator.vs_sma_50_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(indicator.vs_sma_50_pct * 100).toFixed(2)}%
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="text-white">{(indicator.volatility_24h * 100).toFixed(2)}%</div>
                  </td>
                  <td className="p-3">
                    <div className={`px-2 py-1 rounded text-xs font-semibold ${
                      indicator.signal === 'bullish' ? 'bg-green-600/20 text-green-400' :
                      indicator.signal === 'bearish' ? 'bg-red-600/20 text-red-400' :
                      'bg-yellow-600/20 text-yellow-400'
                    }`}>
                      {indicator.signal.toUpperCase()}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}