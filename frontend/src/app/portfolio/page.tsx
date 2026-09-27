'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { Wallet, TrendingUp, TrendingDown, PieChart, Plus, Minus, RefreshCw } from 'lucide-react';

interface Holding {
  symbol: string;
  name: string;
  quantity: number;
  averageCost: number;
  currentPrice: number;
  currentValue: number;
  profitLoss: number;
  profitLossPercent: number;
}

interface PortfolioSummary {
  totalValue: number;
  totalCost: number;
  totalProfitLoss: number;
  totalProfitLossPercent: number;
  dayChange: number;
  dayChangePercent: number;
}

export default function PortfolioPage() {
  const { user } = useStore();
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newHolding, setNewHolding] = useState({
    symbol: '',
    quantity: 0,
    averageCost: 0,
  });

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    // Mock data - replace with actual API call
    setTimeout(() => {
      const mockHoldings: Holding[] = [
        {
          symbol: 'AAPL',
          name: 'Apple Inc.',
          quantity: 10,
          averageCost: 150,
          currentPrice: 175,
          currentValue: 1750,
          profitLoss: 250,
          profitLossPercent: 16.67,
        },
        {
          symbol: 'MSFT',
          name: 'Microsoft Corporation',
          quantity: 5,
          averageCost: 300,
          currentPrice: 330,
          currentValue: 1650,
          profitLoss: 150,
          profitLossPercent: 10,
        },
        {
          symbol: 'BTC-USD',
          name: 'Bitcoin',
          quantity: 0.5,
          averageCost: 30000,
          currentPrice: 35000,
          currentValue: 17500,
          profitLoss: 2500,
          profitLossPercent: 16.67,
        },
      ];

      setHoldings(mockHoldings);
      setSummary({
        totalValue: mockHoldings.reduce((sum, h) => sum + h.currentValue, 0),
        totalCost: mockHoldings.reduce((sum, h) => sum + (h.quantity * h.averageCost), 0),
        totalProfitLoss: mockHoldings.reduce((sum, h) => sum + h.profitLoss, 0),
        totalProfitLossPercent: 14.44,
        dayChange: 320,
        dayChangePercent: 1.2,
      });
      setLoading(false);
    }, 500);
  };

  const handleAddHolding = () => {
    if (!newHolding.symbol || !newHolding.quantity || !newHolding.averageCost) return;

    const holding: Holding = {
      symbol: newHolding.symbol.toUpperCase(),
      name: newHolding.symbol.toUpperCase(),
      quantity: newHolding.quantity,
      averageCost: newHolding.averageCost,
      currentPrice: newHolding.averageCost, // Would get from API
      currentValue: newHolding.quantity * newHolding.averageCost,
      profitLoss: 0,
      profitLossPercent: 0,
    };

    setHoldings([...holdings, holding]);
    setNewHolding({ symbol: '', quantity: 0, averageCost: 0 });
    setShowAddForm(false);
  };

  const handleRemoveHolding = (symbol: string) => {
    setHoldings(holdings.filter(h => h.symbol !== symbol));
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-slate-400 mb-6">Please sign in to access portfolio</p>
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
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Portfolio</h1>
            <p className="text-slate-400">Track your investment performance</p>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={loadPortfolio}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <RefreshCw className="w-5 h-5 text-slate-300" />
            </button>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Holding
            </button>
          </div>
        </div>

        {showAddForm && (
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">Add New Holding</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Symbol</label>
                <input
                  type="text"
                  value={newHolding.symbol}
                  onChange={(e) => setNewHolding({ ...newHolding, symbol: e.target.value.toUpperCase() })}
                  placeholder="AAPL, BTC-USD, etc."
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Quantity</label>
                <input
                  type="number"
                  value={newHolding.quantity}
                  onChange={(e) => setNewHolding({ ...newHolding, quantity: parseFloat(e.target.value) || 0 })}
                  placeholder="Number of shares/coins"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Average Cost ($)</label>
                <input
                  type="number"
                  value={newHolding.averageCost}
                  onChange={(e) => setNewHolding({ ...newHolding, averageCost: parseFloat(e.target.value) || 0 })}
                  placeholder="Purchase price"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-4">
              <button
                onClick={handleAddHolding}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Add Holding
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-slate-400">Loading portfolio...</p>
          </div>
        ) : (
          <>
            {/* Portfolio Summary */}
            {summary && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Wallet className="w-4 h-4 text-green-500" />
                    <span className="text-slate-400 text-sm">Total Value</span>
                  </div>
                  <p className="text-2xl font-bold text-white">${summary.totalValue.toLocaleString()}</p>
                </div>
                
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-slate-400 text-sm">Total P/L</span>
                  </div>
                  <p className={`text-2xl font-bold ${summary.totalProfitLoss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${summary.totalProfitLoss.toLocaleString()}
                  </p>
                  <p className={`text-sm ${summary.totalProfitLossPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {summary.totalProfitLossPercent >= 0 ? '+' : ''}{summary.totalProfitLossPercent.toFixed(2)}%
                  </p>
                </div>
                
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <PieChart className="w-4 h-4 text-blue-500" />
                    <span className="text-slate-400 text-sm">Day Change</span>
                  </div>
                  <p className={`text-2xl font-bold ${summary.dayChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${summary.dayChange.toLocaleString()}
                  </p>
                  <p className={`text-sm ${summary.dayChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {summary.dayChangePercent >= 0 ? '+' : ''}{summary.dayChangePercent.toFixed(2)}%
                  </p>
                </div>
                
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Wallet className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-400 text-sm">Total Cost</span>
                  </div>
                  <p className="text-2xl font-bold text-white">${summary.totalCost.toLocaleString()}</p>
                </div>
              </div>
            )}

            {/* Holdings Table */}
            <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
              <div className="p-4 border-b border-slate-700">
                <h3 className="text-lg font-semibold text-white">Holdings</h3>
              </div>
              
              {holdings.length === 0 ? (
                <div className="text-center py-12">
                  <Wallet className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">No holdings yet</p>
                  <p className="text-slate-500 text-sm">Add your first investment to get started</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-900/50">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Symbol</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Quantity</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Avg Cost</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Current Price</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Value</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">P/L</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">P/L %</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {holdings.map((holding) => (
                        <tr key={holding.symbol} className="border-t border-slate-700">
                          <td className="px-4 py-3">
                            <div>
                              <p className="text-white font-medium">{holding.symbol}</p>
                              <p className="text-slate-400 text-sm">{holding.name}</p>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-white">{holding.quantity}</td>
                          <td className="px-4 py-3 text-white">${holding.averageCost.toFixed(2)}</td>
                          <td className="px-4 py-3 text-white">${holding.currentPrice.toFixed(2)}</td>
                          <td className="px-4 py-3 text-white">${holding.currentValue.toLocaleString()}</td>
                          <td className={`px-4 py-3 ${holding.profitLoss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            ${holding.profitLoss.toLocaleString()}
                          </td>
                          <td className={`px-4 py-3 ${holding.profitLossPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {holding.profitLossPercent >= 0 ? '+' : ''}{holding.profitLossPercent.toFixed(2)}%
                          </td>
                          <td className="px-4 py-3">
                            <button
                              onClick={() => handleRemoveHolding(holding.symbol)}
                              className="p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
