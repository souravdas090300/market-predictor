'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { signalAPI, quoteAPI } from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import CandlestickChart from '@/components/CandlestickChart';
import MobileNav from '@/components/MobileNav';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Download, FileText } from 'lucide-react';
import { pdfExporter } from '@/lib/pdfExport';

export default function DashboardPage() {
  const { 
    currentSymbol, 
    setCurrentSymbol, 
    watchlist, 
    setWatchlist, 
    currentSignal, 
    setCurrentSignal,
    quotes,
    updateQuote,
    user
  } = useStore();
  
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [materialText, setMaterialText] = useState('');
  const [materialResult, setMaterialResult] = useState<any>(null);

  useEffect(() => {
    loadWatchlist();
    startLiveQuotes();
  }, []);

  useEffect(() => {
    if (currentSymbol) {
      loadSignal(currentSymbol);
    }
  }, [currentSymbol]);

  const loadWatchlist = async () => {
    try {
      const data = await signalAPI.getWatchlist();
      setWatchlist(data);
      if (!currentSymbol && data.length > 0) {
        setCurrentSymbol(data[0].symbol);
      }
    } catch (error) {
      console.error('Failed to load watchlist:', error);
    }
  };

  const loadSignal = async (symbol: string) => {
    setLoading(true);
    try {
      const signal = await signalAPI.getSignal(symbol);
      setCurrentSignal(signal);
    } catch (error) {
      console.error('Failed to load signal:', error);
    } finally {
      setLoading(false);
    }
  };

  const startLiveQuotes = () => {
    const symbols = watchlist.map(w => w.symbol);
    if (symbols.length === 0) return;

    const eventSource = quoteAPI.getLiveQuotes(symbols);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      Object.entries(data).forEach(([symbol, quote]: [string, any]) => {
        updateQuote(symbol, quote);
      });
    };

    return () => eventSource.close();
  };

  const handleRefresh = async () => {
    if (!currentSymbol) return;
    setRefreshing(true);
    try {
      await loadSignal(currentSymbol);
    } finally {
      setRefreshing(false);
    }
  };

  const handleMaterialAnalysis = async () => {
    if (!currentSymbol || !materialText.trim()) return;
    
    try {
      const result = await signalAPI.getSignal(currentSymbol); // This would be material API in real implementation
      setMaterialResult({ combined: result });
    } catch (error) {
      console.error('Failed to analyze material:', error);
    }
  };

  const handleExportPDF = () => {
    if (currentSignal) {
      pdfExporter.addSignalReport(currentSignal);
      pdfExporter.save(`market-signal-${currentSignal.symbol}-${Date.now()}.pdf`);
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'bullish': return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'bearish': return <TrendingDown className="w-5 h-5 text-red-500" />;
      default: return <Minus className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish': return 'text-green-400 border-green-500 bg-green-600/20';
      case 'bearish': return 'text-red-400 border-red-500 bg-red-600/20';
      default: return 'text-yellow-400 border-yellow-500 bg-yellow-600/20';
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Welcome to Market Predictor</h1>
          <p className="text-slate-400 mb-6">Please sign in to access the dashboard</p>
          <a
            href="/auth/login"
            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
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
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {currentSignal?.name || currentSymbol || 'Market Dashboard'}
            </h1>
            <p className="text-slate-400">
              {currentSignal?.class || 'Select an asset'} • Last updated {currentSignal?.as_of || '—'}
            </p>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 text-slate-300 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={handleExportPDF}
              disabled={!currentSignal}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <Download className="w-5 h-5 text-slate-300" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 text-slate-600 mx-auto mb-4 animate-spin" />
            <p className="text-slate-400">Loading market data...</p>
          </div>
        ) : currentSignal ? (
          <div className="space-y-6">
            {/* Signal Overview */}
            <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  {getSignalIcon(currentSignal.signal)}
                  <div>
                    <h2 className="text-xl font-bold text-white">
                      {currentSignal.signal.toUpperCase()} SIGNAL
                    </h2>
                    <p className="text-slate-400">
                      P(up): {(currentSignal.probability_up * 100).toFixed(1)}% • 
                      Conviction: {(currentSignal.conviction * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
                
                <div className={`px-4 py-2 rounded-lg border ${getSignalColor(currentSignal.signal)}`}>
                  <span className="font-semibold">{currentSignal.signal.toUpperCase()}</span>
                </div>
              </div>

              {currentSignal.live && (
                <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm">Live Price</p>
                      <p className="text-2xl font-bold text-white font-mono">
                        ${currentSignal.live.price.toFixed(2)}
                      </p>
                    </div>
                    <div className={`text-right ${currentSignal.live.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      <p className="text-lg font-semibold">
                        {currentSignal.live.change_pct >= 0 ? '+' : ''}{currentSignal.live.change_pct.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <CandlestickChart signal={currentSignal} />
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <p className="text-slate-400 text-sm mb-1">P(up) 5 days</p>
                <p className="text-2xl font-bold text-white font-mono">
                  {(currentSignal?.probability_up * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <p className="text-slate-400 text-sm mb-1">Conviction</p>
                <p className="text-2xl font-bold text-white font-mono">
                  {(currentSignal?.conviction * 100).toFixed(0)}%
                </p>
              </div>
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <p className="text-slate-400 text-sm mb-1">RSI (14)</p>
                <p className="text-2xl font-bold text-white font-mono">
                  {currentSignal?.indicators?.rsi_14?.toFixed(1) || '—'}
                </p>
              </div>
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <p className="text-slate-400 text-sm mb-1">Volatility</p>
                <p className="text-2xl font-bold text-white font-mono">
                  {currentSignal?.indicators?.volatility_24h ? (currentSignal.indicators.volatility_24h * 100).toFixed(2) + '%' : '—'}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-400">Select an asset to view market data</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
