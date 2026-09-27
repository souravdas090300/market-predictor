'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { 
  useAssetsList, 
  formatPrice, 
  formatPercentage, 
  getTrendColor,
  getTrendIcon 
} from '@/hooks/useAssetPrediction';
import { 
  TrendingUp, 
  TrendingDown, 
  Search, 
  Filter, 
  ArrowUpDown, 
  RefreshCw,
  DollarSign,
  Bitcoin,
  Globe,
  Box,
  ChevronRight
} from 'lucide-react';
import Link from 'next/link';

export default function AssetsPredictionsPage() {
  const { user } = useStore();
  const { data: assets, loading, error, refetch } = useAssetsList();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filterClass, setFilterClass] = useState<'all' | 'stock' | 'crypto' | 'forex' | 'commodity'>('all');
  const [sortBy, setSortBy] = useState<'symbol' | 'price' | 'change' | 'volume'>('change');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const CLASS_ICONS = {
    stock: DollarSign,
    crypto: Bitcoin,
    forex: Globe,
    commodity: Box,
  };

  const CLASS_LABELS = {
    stock: 'Stocks',
    crypto: 'Crypto',
    forex: 'Forex',
    commodity: 'Commodities',
  };

  const getFilteredAndSortedAssets = () => {
    let filtered = [...(assets || [])];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(asset => 
        asset.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply class filter
    if (filterClass !== 'all') {
      filtered = filtered.filter(asset => asset.class === filterClass);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'symbol':
          comparison = a.symbol.localeCompare(b.symbol);
          break;
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'change':
          comparison = a.change_pct - b.change_pct;
          break;
        case 'volume':
          comparison = a.volume - b.volume;
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  };

  const filteredAssets = getFilteredAndSortedAssets();

  const handleSort = (field: 'symbol' | 'price' | 'change' | 'volume') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getClassIcon = (assetClass: string) => {
    const Icon = CLASS_ICONS[assetClass as keyof typeof CLASS_ICONS];
    return Icon ? <Icon className="w-4 h-4 text-slate-400" /> : null;
  };

  return (
    <DashboardLayout>
      <MobileNav />
      
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Asset Predictions</h1>
            <p className="text-slate-400">AI-powered price forecasts for all tracked assets</p>
          </div>
          
          <button
            onClick={() => refetch()}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            disabled={loading}
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${loading ? 'animate-spin' : ''}`} />
          </button>
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
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Class Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={filterClass}
                onChange={(e) => setFilterClass(e.target.value as any)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="all">All Classes</option>
                <option value="stock">Stocks</option>
                <option value="crypto">Crypto</option>
                <option value="forex">Forex</option>
                <option value="commodity">Commodities</option>
              </select>
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <ArrowUpDown className="w-4 h-4 text-slate-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="change">Change %</option>
                <option value="price">Price</option>
                <option value="volume">Volume</option>
                <option value="symbol">Symbol</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400">No assets found matching your criteria</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Class Headers */}
            {Object.entries(CLASS_LABELS).map(([classKey, label]) => {
              const classAssets = filteredAssets.filter(a => a.class === classKey);
              if (classAssets.length === 0) return null;
              
              return (
                <div key={classKey}>
                  <div className="flex items-center gap-2 mb-3">
                    {getClassIcon(classKey)}
                    <h2 className="text-lg font-semibold text-white">{label}</h2>
                    <span className="text-slate-400 text-sm">({classAssets.length} assets)</span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {classAssets.map((asset) => (
                      <Link
                        key={asset.symbol}
                        href={`/asset-prediction/${asset.symbol}`}
                        className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 hover:border-green-500 transition-colors cursor-pointer"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            {getClassIcon(asset.class)}
                            <div>
                              <h3 className="text-white font-semibold">{asset.symbol}</h3>
                              <p className="text-slate-400 text-sm">{asset.name}</p>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-slate-400" />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          <div>
                            <p className="text-slate-400 text-sm">Price</p>
                            <p className="text-white font-semibold">{formatPrice(asset.price, asset.symbol)}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">24h Change</p>
                            <p className={`font-semibold ${asset.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {formatPercentage(asset.change_pct)}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-400">
                            {asset.change_pct >= 0 ? getTrendIcon('bullish') : getTrendIcon('bearish')} AI Forecast
                          </span>
                          <span className="text-green-400 text-xs">View Predictions →</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}