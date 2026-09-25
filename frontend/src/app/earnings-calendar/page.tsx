'use client';

import { useState } from 'react';
import { 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  AlertCircle,
  Filter,
  RefreshCw,
  Info,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

interface EarningsEntry {
  symbol: string;
  name: string;
  date: string;
  quarter: string;
  eps_estimate: number;
  eps_actual?: number;
  revenue_estimate: number;
  revenue_actual?: number;
  surprise_pct?: number;
  guidance: 'positive' | 'negative' | 'neutral' | 'pending';
  report_time: 'AM' | 'PM' | 'TBD';
}

const MOCK_EARNINGS: EarningsEntry[] = [
  {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    date: '2024-10-24',
    quarter: 'Q4 2024',
    eps_estimate: 1.35,
    eps_actual: 1.42,
    revenue_estimate: 89000000000,
    revenue_actual: 94000000000,
    surprise_pct: 5.2,
    guidance: 'positive',
    report_time: 'PM'
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft Corporation',
    date: '2024-10-22',
    quarter: 'Q1 2025',
    eps_estimate: 2.65,
    eps_actual: 2.78,
    revenue_estimate: 54500000000,
    revenue_actual: 56500000000,
    surprise_pct: 4.9,
    guidance: 'positive',
    report_time: 'PM'
  },
  {
    symbol: 'GOOGL',
    name: 'Alphabet Inc.',
    date: '2024-10-25',
    quarter: 'Q3 2024',
    eps_estimate: 1.85,
    eps_actual: 1.72,
    revenue_estimate: 78000000000,
    revenue_actual: 74000000000,
    surprise_pct: -7.0,
    guidance: 'negative',
    report_time: 'PM'
  },
  {
    symbol: 'NVDA',
    name: 'NVIDIA Corporation',
    date: '2024-11-19',
    quarter: 'Q3 2025',
    eps_estimate: 0.72,
    revenue_estimate: 29000000000,
    guidance: 'pending',
    report_time: 'PM'
  },
  {
    symbol: 'TSLA',
    name: 'Tesla Inc.',
    date: '2024-10-20',
    quarter: 'Q3 2024',
    eps_estimate: 0.58,
    eps_actual: 0.51,
    revenue_estimate: 25500000000,
    revenue_actual: 23500000000,
    surprise_pct: -12.1,
    guidance: 'negative',
    report_time: 'PM'
  },
  {
    symbol: 'AMZN',
    name: 'Amazon.com Inc.',
    date: '2024-10-31',
    quarter: 'Q3 2024',
    eps_estimate: 0.82,
    revenue_estimate: 156000000000,
    guidance: 'pending',
    report_time: 'PM'
  },
  {
    symbol: 'META',
    name: 'Meta Platforms Inc.',
    date: '2024-10-30',
    quarter: 'Q3 2024',
    eps_estimate: 2.12,
    revenue_estimate: 40500000000,
    guidance: 'pending',
    report_time: 'PM'
  },
  {
    symbol: 'NFLX',
    name: 'Netflix Inc.',
    date: '2024-10-18',
    quarter: 'Q3 2024',
    eps_estimate: 4.15,
    eps_actual: 4.52,
    revenue_estimate: 9750000000,
    revenue_actual: 9850000000,
    surprise_pct: 8.9,
    guidance: 'positive',
    report_time: 'PM'
  }
];

export default function EarningsCalendarPage() {
  const [earnings, setEarnings] = useState<EarningsEntry[]>(MOCK_EARNINGS);
  const [filterPeriod, setFilterPeriod] = useState<'all' | 'week' | 'month'>('month');
  const [filterStatus, setFilterStatus] = useState<'all' | 'reported' | 'upcoming'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'surprise' | 'market_cap'>('date');

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const getFilteredEarnings = () => {
    let filtered = [...earnings];
    const now = new Date();
    const oneWeekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    const oneMonthLater = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

    // Apply time filter
    if (filterPeriod === 'week') {
      filtered = filtered.filter(e => {
        const date = new Date(e.date);
        return date >= now && date <= oneWeekLater;
      });
    } else if (filterPeriod === 'month') {
      filtered = filtered.filter(e => {
        const date = new Date(e.date);
        return date >= now && date <= oneMonthLater;
      });
    }

    // Apply status filter
    if (filterStatus === 'reported') {
      filtered = filtered.filter(e => e.eps_actual !== undefined);
    } else if (filterStatus === 'upcoming') {
      filtered = filtered.filter(e => e.eps_actual === undefined);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(a.date).getTime() - new Date(b.date).getTime();
        case 'surprise':
          const surpriseA = a.surprise_pct || 0;
          const surpriseB = b.surprise_pct || 0;
          return surpriseB - surpriseA;
        case 'market_cap':
          // Simplified - would use actual market cap
          return a.symbol.localeCompare(b.symbol);
        default:
          return 0;
      }
    });

    return filtered;
  };

  const filteredEarnings = getFilteredEarnings();

  const getGuidanceColor = (guidance: string) => {
    switch (guidance) {
      case 'positive': return 'text-green-400 bg-green-600/20';
      case 'negative': return 'text-red-400 bg-red-600/20';
      case 'neutral': return 'text-yellow-400 bg-yellow-600/20';
      default: return 'text-slate-400 bg-slate-600/20';
    }
  };

  const getSurpriseColor = (surprise: number) => {
    if (surprise > 5) return 'text-green-400';
    if (surprise > 0) return 'text-green-300';
    if (surprise < -5) return 'text-red-400';
    if (surprise < 0) return 'text-red-300';
    return 'text-slate-400';
  };

  const isUpcoming = (date: string) => {
    return new Date(date) > new Date();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Earnings Calendar</h1>
          <p className="text-slate-400">Track upcoming and reported earnings with EPS analysis</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => setEarnings([...MOCK_EARNINGS])}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-slate-300" />
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            <span className="text-slate-400">Total Entries</span>
          </div>
          <div className="text-2xl font-bold text-white">{earnings.length}</div>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-slate-400">Positive Surprises</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {earnings.filter(e => e.surprise_pct && e.surprise_pct > 0).length}
          </div>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-5 h-5 text-red-400" />
            <span className="text-slate-400">Negative Surprises</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {earnings.filter(e => e.surprise_pct && e.surprise_pct < 0).length}
          </div>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-yellow-400" />
            <span className="text-slate-400">Upcoming</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {earnings.filter(e => e.eps_actual === undefined).length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-8">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-slate-400">Time Period:</span>
          </div>
          <select
            value={filterPeriod}
            onChange={(e) => setFilterPeriod(e.target.value as any)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="all">All Time</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
          
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Status:</span>
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="all">All</option>
            <option value="reported">Reported</option>
            <option value="upcoming">Upcoming</option>
          </select>
          
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Sort by:</span>
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="date">Date</option>
            <option value="surprise">Surprise %</option>
            <option value="market_cap">Market Cap</option>
          </select>
        </div>
      </div>

      {/* Educational Info */}
      <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4 mb-8">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-400 mt-0.5" />
          <div className="text-slate-300 text-sm">
            <strong className="text-white">Earnings Calendar:</strong> Shows company earnings reports with EPS estimates vs actuals. 
            Positive surprises often lead to price increases, while negative surprises can cause declines. 
            Guidance indicates management's outlook for future performance.
          </div>
        </div>
      </div>

      {/* Earnings Table */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900/50">
                <th className="text-left text-slate-400 p-4">Company</th>
                <th className="text-left text-slate-400 p-4">Date</th>
                <th className="text-left text-slate-400 p-4">Quarter</th>
                <th className="text-right text-slate-400 p-4">EPS Estimate</th>
                <th className="text-right text-slate-400 p-4">EPS Actual</th>
                <th className="text-right text-slate-400 p-4">Surprise %</th>
                <th className="text-right text-slate-400 p-4">Revenue</th>
                <th className="text-center text-slate-400 p-4">Guidance</th>
              </tr>
            </thead>
            <tbody>
              {filteredEarnings.map((earning) => (
                <tr key={earning.symbol} className="border-b border-slate-700/50 hover:bg-slate-900/30">
                  <td className="p-4">
                    <div className="font-semibold text-white">{earning.symbol}</div>
                    <div className="text-slate-400 text-sm">{earning.name}</div>
                  </td>
                  <td className="p-4">
                    <div className="text-white">{new Date(earning.date).toLocaleDateString()}</div>
                    <div className="text-slate-400 text-sm">{earning.report_time}</div>
                  </td>
                  <td className="p-4 text-slate-300">{earning.quarter}</td>
                  <td className="p-4 text-right text-white">
                    ${earning.eps_estimate.toFixed(2)}
                  </td>
                  <td className="p-4 text-right">
                    {earning.eps_actual ? (
                      <div className="text-white">${earning.eps_actual.toFixed(2)}</div>
                    ) : (
                      <div className="text-slate-500">Pending</div>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    {earning.surprise_pct !== undefined ? (
                      <div className={`flex items-center justify-end gap-1 ${getSurpriseColor(earning.surprise_pct)}`}>
                        {earning.surprise_pct > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                        <span className="font-semibold">{Math.abs(earning.surprise_pct).toFixed(1)}%</span>
                      </div>
                    ) : (
                      <div className="text-slate-500">—</div>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    <div className="text-white">{formatCurrency(earning.revenue_estimate)}</div>
                    {earning.revenue_actual && (
                      <div className="text-slate-400 text-sm">{formatCurrency(earning.revenue_actual)}</div>
                    )}
                  </td>
                  <td className="p-4 text-center">
                    <div className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getGuidanceColor(earning.guidance)}`}>
                      {earning.guidance === 'pending' ? 'Pending' : earning.guidance.charAt(0).toUpperCase() + earning.guidance.slice(1)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredEarnings.length === 0 && (
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No earnings entries match your filters</p>
        </div>
      )}
    </div>
  );
}