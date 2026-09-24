'use client';

import { useStore } from '@/store/useStore';
import { TrendingUp, TrendingDown, Minus, DollarSign, Bitcoin, Globe, Box } from 'lucide-react';
import type { WatchlistItem } from '@/types';

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

export default function Sidebar() {
  const { sidebarOpen, watchlist, currentSymbol, setCurrentSymbol, quotes } = useStore();

  if (!sidebarOpen) return null;

  const groupedWatchlist = watchlist.reduce((acc, item) => {
    if (!acc[item.class]) {
      acc[item.class] = [];
    }
    acc[item.class].push(item);
    return acc;
  }, {} as Record<string, WatchlistItem[]>);

  const getSignalIcon = (symbol: string) => {
    const quote = quotes[symbol];
    if (!quote) return <Minus className="w-4 h-4 text-yellow-500" />;
    
    if (quote.change_pct > 0) {
      return <TrendingUp className="w-4 h-4 text-green-500" />;
    } else if (quote.change_pct < 0) {
      return <TrendingDown className="w-4 h-4 text-red-500" />;
    }
    return <Minus className="w-4 h-4 text-yellow-500" />;
  };

  const formatChange = (symbol: string) => {
    const quote = quotes[symbol];
    if (!quote) return '—';
    
    const sign = quote.change_pct >= 0 ? '+' : '';
    return `${sign}${quote.change_pct.toFixed(2)}%`;
  };

  return (
    <aside className="w-72 bg-slate-900 border-r border-slate-700 flex flex-col h-full">
      <div className="p-4 border-b border-slate-700">
        <h2 className="text-white font-semibold text-lg">Watchlist</h2>
        <p className="text-slate-400 text-sm mt-1">Real-time market signals</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {Object.entries(groupedWatchlist).map(([assetClass, items]) => {
          const Icon = CLASS_ICONS[assetClass as keyof typeof CLASS_ICONS];
          
          return (
            <div key={assetClass} className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Icon className="w-4 h-4 text-slate-400" />
                <h3 className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
                  {CLASS_LABELS[assetClass as keyof typeof CLASS_LABELS]}
                </h3>
              </div>
              
              <div className="space-y-2">
                {items.map((item) => (
                  <button
                    key={item.symbol}
                    onClick={() => setCurrentSymbol(item.symbol)}
                    className={`w-full p-3 rounded-lg transition-all ${
                      currentSymbol === item.symbol
                        ? 'bg-green-600/20 border border-green-500'
                        : 'bg-slate-800/50 hover:bg-slate-800 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getSignalIcon(item.symbol)}
                        <div className="text-left">
                          <div className="text-white font-medium text-sm">{item.name}</div>
                          <div className="text-slate-400 text-xs">{item.symbol}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-white font-mono text-sm">
                          {quotes[item.symbol] ? quotes[item.symbol].price.toFixed(4) : '—'}
                        </div>
                        <div className={`text-xs font-mono ${
                          quotes[item.symbol]?.change_pct >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {formatChange(item.symbol)}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-700">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-green-400 text-xs font-medium">Live</span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Real-time quotes updating every ~12s
          </p>
        </div>
      </div>
    </aside>
  );
}
