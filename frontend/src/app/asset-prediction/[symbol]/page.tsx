'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { 
  useAssetDetails,
  useAssetAllPredictions,
  useAssetHistoricalData,
  formatPrice, 
  formatPercentage, 
  getTrendColor,
  getTrendIcon 
} from '@/hooks/useAssetPrediction';
import { 
  TrendingUp, 
  TrendingDown, 
  RefreshCw,
  ArrowLeft,
  DollarSign,
  Bitcoin,
  Globe,
  Box,
  Activity,
  BarChart3,
  Clock
} from 'lucide-react';
import Link from 'next/link';

const TIMEFRAMES = [
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
];

export default function AssetPredictionPage() {
  const params = useParams();
  const symbol = params.symbol as string;
  const { user } = useStore();
  
  const { data: asset, loading: assetLoading, refetch: refetchAsset } = useAssetDetails(symbol);
  const { data: predictions, loading: predictionsLoading, refetch: refetchPredictions } = useAssetAllPredictions(symbol);
  const { data: historical, loading: historicalLoading } = useAssetHistoricalData(symbol, '1d');
  
  const [selectedTimeframe, setSelectedTimeframe] = useState('1d');

  const CLASS_ICONS = {
    stock: DollarSign,
    crypto: Bitcoin,
    forex: Globe,
    commodity: Box,
  };

  const getClassIcon = (assetClass: string) => {
    const Icon = CLASS_ICONS[assetClass as keyof typeof CLASS_ICONS];
    return Icon ? <Icon className="w-4 h-4 text-slate-400" /> : null;
  };

  const selectedPrediction = predictions?.find(p => p.timeframe === selectedTimeframe);

  const handleRefresh = () => {
    refetchAsset();
    refetchPredictions();
  };

  if (assetLoading && !asset) {
    return (
      <DashboardLayout>
        <MobileNav />
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  if (!asset) {
    return (
      <DashboardLayout>
        <MobileNav />
        <div className="p-6 max-w-7xl mx-auto">
          <div className="text-center py-12">
            <p className="text-slate-400 mb-4">Asset not found</p>
            <Link href="/assets-predictions" className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
              Back to Assets
            </Link>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <MobileNav />
      
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link href="/assets-predictions" className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
              <ArrowLeft className="w-5 h-5 text-slate-300" />
            </Link>
            <div>
              <div className="flex items-center gap-3 mb-1">
                {getClassIcon(asset.class)}
                <h1 className="text-3xl font-bold text-white">{asset.symbol}</h1>
              </div>
              <p className="text-slate-400">{asset.name}</p>
            </div>
          </div>
          
          <button
            onClick={handleRefresh}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            disabled={assetLoading || predictionsLoading}
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${(assetLoading || predictionsLoading) ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Current Price Card */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <p className="text-slate-400 text-sm mb-1">Current Price</p>
              <p className="text-3xl font-bold text-white">{formatPrice(asset.price, asset.symbol)}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">24h Change</p>
              <p className={`text-2xl font-bold ${asset.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatPercentage(asset.change_pct)}
              </p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">24h High</p>
              <p className="text-2xl font-bold text-white">{formatPrice(asset.high_24h, asset.symbol)}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">24h Low</p>
              <p className="text-2xl font-bold text-white">{formatPrice(asset.low_24h, asset.symbol)}</p>
            </div>
          </div>
        </div>

        {/* Timeframe Selector */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-4 h-4 text-slate-400" />
            <h3 className="text-white font-semibold">Prediction Timeframe</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf.value}
                onClick={() => setSelectedTimeframe(tf.value)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedTimeframe === tf.value
                    ? 'bg-green-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>

        {/* Prediction Details */}
        {selectedPrediction ? (
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
            <div className="flex items-center gap-2 mb-6">
              <Activity className="w-5 h-5 text-green-400" />
              <h3 className="text-xl font-bold text-white">
                AI Price Forecast - {TIMEFRAMES.find(tf => tf.value === selectedTimeframe)?.label}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Predicted Price</p>
                <p className="text-2xl font-bold text-white">{formatPrice(selectedPrediction.predicted_price, asset.symbol)}</p>
                <p className={`text-sm mt-1 ${selectedPrediction.predicted_change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatPercentage(selectedPrediction.predicted_change_pct)}
                </p>
              </div>
              
              <div className="bg-slate-900/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Confidence</p>
                <p className="text-2xl font-bold text-white">{selectedPrediction.confidence}%</p>
                <p className="text-sm text-slate-400 mt-1">AI Model Accuracy</p>
              </div>
              
              <div className="bg-slate-900/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Trend</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getTrendIcon(selectedPrediction.trend)}</span>
                  <p className={`text-2xl font-bold ${getTrendColor(selectedPrediction.trend)}`}>
                    {selectedPrediction.trend.toUpperCase()}
                  </p>
                </div>
              </div>
            </div>

            {/* Price Range */}
            <div className="bg-slate-900/50 rounded-lg p-4 mb-6">
              <h4 className="text-white font-semibold mb-4">Expected Price Range</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-slate-400 text-sm">Expected High</p>
                  <p className="text-lg font-bold text-green-400">{formatPrice(selectedPrediction.expected_high, asset.symbol)}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Expected Average</p>
                  <p className="text-lg font-bold text-white">{formatPrice(selectedPrediction.expected_average, asset.symbol)}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">Expected Low</p>
                  <p className="text-lg font-bold text-red-400">{formatPrice(selectedPrediction.expected_low, asset.symbol)}</p>
                </div>
              </div>
            </div>

            {/* Confidence Interval */}
            <div className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-white font-semibold mb-4">Confidence Interval ({selectedPrediction.confidence}%)</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Lower Bound</span>
                  <span className="text-white font-semibold">{formatPrice(selectedPrediction.confidence_interval.low, asset.symbol)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Upper Bound</span>
                  <span className="text-white font-semibold">{formatPrice(selectedPrediction.confidence_interval.high, asset.symbol)}</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
            <p className="text-slate-400">Loading prediction data...</p>
          </div>
        )}

        {/* All Timeframes Summary */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="w-5 h-5 text-green-400" />
            <h3 className="text-xl font-bold text-white">All Timeframes Summary</h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Timeframe</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Predicted Price</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Change %</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Confidence</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Trend</th>
                </tr>
              </thead>
              <tbody>
                {predictions?.map((prediction) => (
                  <tr key={prediction.timeframe} className="border-b border-slate-700 hover:bg-slate-700/50">
                    <td className="px-4 py-3 text-white font-medium">
                      {TIMEFRAMES.find(tf => tf.value === prediction.timeframe)?.label}
                    </td>
                    <td className="px-4 py-3 text-white">
                      {formatPrice(prediction.predicted_price, asset.symbol)}
                    </td>
                    <td className={`px-4 py-3 font-semibold ${prediction.predicted_change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatPercentage(prediction.predicted_change_pct)}
                    </td>
                    <td className="px-4 py-3 text-white">{prediction.confidence}%</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 ${getTrendColor(prediction.trend)}`}>
                        {getTrendIcon(prediction.trend)}
                        {prediction.trend.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Historical Data Preview */}
        {historical && (
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
            <div className="flex items-center gap-2 mb-6">
              <Activity className="w-5 h-5 text-green-400" />
              <h3 className="text-xl font-bold text-white">Recent Price History</h3>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Date</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Price</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {historical.data.slice(-10).map((data, index) => (
                    <tr key={index} className="border-b border-slate-700 hover:bg-slate-700/50">
                      <td className="px-4 py-3 text-white">
                        {new Date(data.timestamp).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-white">
                        {formatPrice(data.price, asset.symbol)}
                      </td>
                      <td className="px-4 py-3 text-white">
                        {data.volume.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}