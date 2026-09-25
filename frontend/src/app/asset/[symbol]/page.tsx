'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { signalAPI, quoteAPI } from '@/lib/api';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign,
  Volume2,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  AlertTriangle,
  Calendar,
  BarChart3,
  LineChart,
  Settings,
  Star,
  Clock
} from 'lucide-react';

interface AssetDetail {
  symbol: string;
  name: string;
  class: 'stock' | 'crypto' | 'forex' | 'commodity';
  signal: 'bullish' | 'bearish' | 'neutral';
  probability_up: number;
  conviction: number;
  live_price: number;
  change_pct: number;
  volume: number;
  high_24h: number;
  low_24h: number;
  market_cap?: number;
  indicators: {
    rsi_14: number;
    macd_hist_pct: number;
    vs_sma_50_pct: number;
    vs_sma_200_pct: number;
    volatility_24h: number;
  };
  candles: Array<{
    d: string;
    o: number;
    h: number;
    l: number;
    c: number;
  }>;
  candle_patterns: Array<{
    date: string;
    pattern: string;
    bias: 'bullish' | 'bearish' | 'neutral';
    meaning: string;
  }>;
  similar_assets: Array<{
    symbol: string;
    name: string;
    correlation: number;
  }>;
}

export default function AssetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const symbol = params.symbol as string;
  const { watchlist, addToWatchlist, removeFromWatchlist } = useStore();
  
  const [asset, setAsset] = useState<AssetDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y'>('6M');
  const [isWatchlisted, setIsWatchlisted] = useState(false);

  useEffect(() => {
    if (symbol) {
      loadAssetDetail();
      checkWatchlistStatus();
    }
  }, [symbol, timeframe]);

  const loadAssetDetail = async () => {
    try {
      setLoading(true);
      const signal = await signalAPI.getSignal(symbol, true, false);
      const quote = await quoteAPI.getQuote(symbol);
      
      setAsset({
        symbol: signal.symbol,
        name: signal.name,
        class: signal.class,
        signal: signal.signal,
        probability_up: signal.probability_up,
        conviction: signal.conviction,
        live_price: quote?.price || signal.candles?.[signal.candles.length - 1]?.c || 0,
        change_pct: quote?.change_pct || 0,
        volume: 0,
        high_24h: 0,
        low_24h: 0,
        market_cap: undefined,
        indicators: signal.indicators,
        candles: signal.candles || [],
        candle_patterns: signal.candle_patterns || [],
        similar_assets: [],
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to load asset detail:', error);
      setLoading(false);
    }
  };

  const checkWatchlistStatus = () => {
    const inWatchlist = watchlist.some(w => w.symbol === symbol);
    setIsWatchlisted(inWatchlist);
  };

  const toggleWatchlist = () => {
    if (isWatchlisted) {
      removeFromWatchlist(symbol);
    } else if (asset) {
      addToWatchlist({
        symbol: asset.symbol,
        name: asset.name,
        class: asset.class,
        query: asset.symbol,
      });
    }
    setIsWatchlisted(!isWatchlisted);
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish': return 'text-green-400 bg-green-600/20 border-green-500';
      case 'bearish': return 'text-red-400 bg-red-600/20 border-red-500';
      default: return 'text-yellow-400 bg-yellow-600/20 border-yellow-500';
    }
  };

  const getRSIStatus = (rsi: number) => {
    if (rsi >= 70) return { status: 'Overbought', color: 'text-red-400' };
    if (rsi <= 30) return { status: 'Oversold', color: 'text-green-400' };
    return { status: 'Neutral', color: 'text-yellow-400' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-400">Asset not found</p>
          <button 
            onClick={() => router.push('/assets')}
            className="mt-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white"
          >
            Back to Assets
          </button>
        </div>
      </div>
    );
  }

  const rsiStatus = getRSIStatus(asset.indicators.rsi_14);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button 
          onClick={() => router.push('/assets')}
          className="text-slate-400 hover:text-white mb-4 flex items-center gap-2"
        >
          ← Back to Assets
        </button>
        
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold text-white">{asset.symbol}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getSignalColor(asset.signal)}`}>
                {asset.signal.toUpperCase()}
              </span>
            </div>
            <p className="text-xl text-slate-300">{asset.name}</p>
            <p className="text-slate-500 capitalize">{asset.class}</p>
          </div>
          
          <button
            onClick={toggleWatchlist}
            className={`p-3 rounded-lg transition-colors ${
              isWatchlisted ? 'bg-yellow-600 text-white' : 'bg-slate-700 text-slate-300'
            }`}
          >
            <Star className={`w-6 h-6 ${isWatchlisted ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>

      {/* Price Information */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Current Price</h3>
            <DollarSign className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            ${asset.live_price.toFixed(2)}
          </div>
          <div className={`flex items-center gap-2 ${asset.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {asset.change_pct >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
            <span className="font-semibold">{Math.abs(asset.change_pct).toFixed(2)}%</span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Signal Strength</h3>
            <Activity className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {(asset.probability_up * 100).toFixed(1)}%
          </div>
          <div className="text-slate-400">
            Conviction: {asset.conviction.toFixed(2)}
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">RSI (14)</h3>
            <BarChart3 className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {asset.indicators.rsi_14.toFixed(1)}
          </div>
          <div className={rsiStatus.color}>
            {rsiStatus.status}
          </div>
        </div>
      </div>

      {/* Technical Indicators */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
        <h2 className="text-2xl font-bold text-white mb-6">Technical Indicators</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">RSI (14)</div>
            <div className="text-xl font-bold text-white">{asset.indicators.rsi_14.toFixed(1)}</div>
            <div className={`text-sm ${rsiStatus.color}`}>{rsiStatus.status}</div>
          </div>
          
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">MACD Histogram</div>
            <div className="text-xl font-bold text-white">{(asset.indicators.macd_hist_pct * 100).toFixed(3)}%</div>
            <div className={`text-sm ${asset.indicators.macd_hist_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {asset.indicators.macd_hist_pct >= 0 ? 'Bullish' : 'Bearish'}
            </div>
          </div>
          
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">vs SMA 50</div>
            <div className="text-xl font-bold text-white">{(asset.indicators.vs_sma_50_pct * 100).toFixed(2)}%</div>
            <div className={`text-sm ${asset.indicators.vs_sma_50_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {asset.indicators.vs_sma_50_pct >= 0 ? 'Above' : 'Below'}
            </div>
          </div>
          
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">vs SMA 200</div>
            <div className="text-xl font-bold text-white">{(asset.indicators.vs_sma_200_pct * 100).toFixed(2)}%</div>
            <div className={`text-sm ${asset.indicators.vs_sma_200_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {asset.indicators.vs_sma_200_pct >= 0 ? 'Above' : 'Below'}
            </div>
          </div>
        </div>
      </div>

      {/* Candle Patterns */}
      {asset.candle_patterns.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Recent Candle Patterns</h2>
          <div className="space-y-3">
            {asset.candle_patterns.map((pattern, index) => (
              <div key={index} className="bg-slate-900/50 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    pattern.bias === 'bullish' ? 'bg-green-600/20 text-green-400' :
                    pattern.bias === 'bearish' ? 'bg-red-600/20 text-red-400' :
                    'bg-yellow-600/20 text-yellow-400'
                  }`}>
                    {pattern.pattern.replace('_', ' ')}
                  </div>
                  <div className="text-slate-400">{pattern.date}</div>
                </div>
                <div className="text-slate-300 text-sm max-w-md">{pattern.meaning}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Similar Assets */}
      {asset.similar_assets.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Similar Assets</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {asset.similar_assets.map((similar, index) => (
              <div 
                key={index}
                onClick={() => router.push(`/asset/${similar.symbol}`)}
                className="bg-slate-900/50 rounded-lg p-4 cursor-pointer hover:bg-slate-900 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold text-white">{similar.symbol}</div>
                  <div className="text-slate-400">{(similar.correlation * 100).toFixed(0)}%</div>
                </div>
                <div className="text-slate-400 text-sm">{similar.name}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}