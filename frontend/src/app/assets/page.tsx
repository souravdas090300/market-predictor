'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { signalAPI, quoteAPI } from '@/lib/api';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Filter, 
  ArrowUpDown, 
  RefreshCw, 
  AlertTriangle,
  Activity,
  DollarSign,
  Bitcoin,
  Globe,
  Box,
  Search,
  Grid3x3,
  List
} from 'lucide-react';

interface AssetLiveStatus {
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
  last_update: string;
  indicators: {
    rsi_14: number;
    vs_sma_50_pct: number;
    volatility_24h: number;
  };
}

const CLASS_ICONS = {
  stock: DollarSign,
  crypto: Bitcoin,
  forex: Globe,
  commodity: Box,
};

const CLASS_LABELS = {
  stock: 'Shares',
  crypto: 'Crypto',
  forex: 'Forex',
  commodity: 'Commodities',
};

export default function AssetsLiveStatusPage() {
  const { watchlist, quotes, updateQuote } = useStore();
  const [assets, setAssets] = useState<AssetLiveStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filterClass, setFilterClass] = useState<'all' | 'stock' | 'crypto' | 'forex' | 'commodity'>('all');
  const [filterSignal, setFilterSignal] = useState<'all' | 'bullish' | 'bearish' | 'neutral'>('all');
  const [sortBy, setSortBy] = useState<'symbol' | 'price' | 'change' | 'signal'>('change');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadAllAssets();
    startLiveUpdates();
    
    if (autoRefresh) {
      const interval = setInterval(loadAllAssets, 10000); // Refresh every 10 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh, filterClass, filterSignal]);

  const loadAllAssets = async () => {
    try {
      setLoading(true);
      const watchlistData = await signalAPI.getWatchlist();
      
      const filteredWatchlist = filterClass === 'all' 
        ? watchlistData 
        : watchlistData.filter(w => w.class === filterClass);

      const assetsData = await Promise.all(
        filteredWatchlist.map(async (asset) => {
          try {
            const signal = await signalAPI.getSignal(asset.symbol, true, false);
            const quote = quotes[asset.symbol] || await quoteAPI.getQuote(asset.symbol);
            
            return {
              symbol: signal.symbol,
              name: signal.name,
              class: signal.class,
              signal: signal.signal,
              probability_up: signal.probability_up,
              conviction: signal.conviction,
              live_price: quote?.price || signal.candles?.[signal.candles.length - 1]?.c || 0,
              change_pct: quote?.change_pct || 0,
              volume: 0, // Would come from quote data
              high_24h: 0, // Would come from quote data
              low_24h: 0, // Would come from quote data
              market_cap: undefined,
              last_update: new Date().toISOString(),
              indicators: signal.indicators,
            };
          } catch (error) {
            console.error(`Failed to load data for ${asset.symbol}:`, error);
            return null;
          }
        })
      );

      const validAssets = assetsData.filter((a): a is AssetLiveStatus => a !== null);
      setAssets(validAssets);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load assets:', error);
      setLoading(false);
    }
  };

  const startLiveUpdates = () => {
    const symbols = watchlist.map(w => w.symbol);
    if (symbols.length === 0) return;

    const eventSource = quoteAPI.getLiveQuotes(symbols);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      Object.entries(data).forEach(([symbol, quote]: [string, any]) => {
        updateQuote(symbol, quote);
        
        // Update asset in local state
        setAssets(prev => prev.map(asset => 
          asset.symbol === symbol 
            ? { ...asset, live_price: quote.price, change_pct: quote.change_pct, last_update: new Date().toISOString() }
            : asset
        ));
      });
    };

    return () => eventSource.close();
  };

  const getFilteredAndSortedAssets = () => {
    let filtered = [...assets];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(asset => 
        asset.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply signal filter
    if (filterSignal !== 'all') {
      filtered = filtered.filter(asset => asset.signal === filterSignal);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'symbol':
          comparison = a.symbol.localeCompare(b.symbol);
          break;
        case 'price':
          comparison = a.live_price - b.live_price;
          break;
        case 'change':
          comparison = a.change_pct - b.change_pct;
          break;
        case 'signal':
          const signalOrder = { bullish: 3, neutral: 2, bearish: 1 };
          comparison = signalOrder[a.signal] - signalOrder[b.signal];
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  };

  const filteredAssets = getFilteredAndSortedAssets();

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'bullish': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'bearish': return <TrendingDown className="w-4 h-4 text-red-500" />;
      default: return <Minus className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish': return 'text-green-400 bg-green-600/20 border-green-500';
      case 'bearish': return 'text-red-400 bg-red-600/20 border-red-500';
      default: return 'text-yellow-400 bg-yellow-600/20 border-yellow-500';
    }
  };

  const getClassIcon = (assetClass: string) => {
    const Icon = CLASS_ICONS[assetClass as keyof typeof CLASS_ICONS];
    return Icon ? <Icon className="w-4 h-4 text-slate-400" /> : null;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">All Assets Live Status</h1>
          <p className="text-slate-400">Real-time monitoring of all tracked assets</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              autoRefresh ? 'bg-green-600 text-white' : 'bg-slate-700 text-slate-300'
            }`}
          >
            Auto-refresh: {autoRefresh ? 'ON' : 'OFF'}
          </button>
          <button
            onClick={loadAllAssets}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search assets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)} />
          </div>
          {/* View Mode Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode(viewMode === "grid" ? "list" : "grid")}
              className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            >
              {viewMode === "grid" ? <List className="w-4 h-4 text-slate-300" /> : <Grid3x3 className="w-4 h-4 text-slate-300" />}
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filteredAssets.length === 0 ? (
        <div className="text-center py-12">
          <AlertTriangle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No assets found matching your criteria</p>
        </div>
      ) : (
        <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" : "space-y-4"}>
          {filteredAssets.map((asset) => (
            <div key={asset.symbol} className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 hover:border-slate-600 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  {getClassIcon(asset.class)}
                  <div>
                    <h3 className="text-white font-semibold">{asset.symbol}</h3>
                    <p className="text-slate-400 text-sm">{asset.name}</p>
                  </div>
                </div>
                {getSignalIcon(asset.signal)}
              </div>
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <p className="text-slate-400 text-sm">Price</p>
                  <p className="text-white font-semibold">${asset.live_price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Change</p>
                  <p className={asset.change_pct >= 0 ? "text-green-400 font-semibold" : "text-red-400 font-semibold"}>
                    {asset.change_pct >= 0 ? "+" : ""}{asset.change_pct.toFixed(2)}%
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className={getSignalColor(asset.signal) + " px-2 py-1 rounded text-xs font-medium"}>
                  {asset.signal.toUpperCase()}
                </span>
                <span className="text-slate-500 text-xs">{new Date(asset.last_update).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
