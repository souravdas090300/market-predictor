'use client';

import { useState } from 'react';
import { useStore } from '@/store/useStore';
import { Menu, X, Home, Settings, BarChart3, Newspaper, Calculator, Zap, Grid3x3, TrendingUp, Activity, LayoutGrid, Scale } from 'lucide-react';

export default function MobileNav() {
  const { sidebarOpen, setSidebarOpen, setCurrentSymbol } = useStore();
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { icon: Home, label: 'Dashboard', path: '/' },
    { icon: LayoutGrid, label: 'All Assets', path: '/assets' },
    { icon: Scale, label: 'Asset Comparison', path: '/asset-comparison' },
    { icon: BarChart3, label: 'Model Training', path: '/model-training' },
    { icon: Calculator, label: 'Risk Calculator', path: '/risk-calculator' },
    { icon: Zap, label: 'Strategy Optimizer', path: '/strategy-optimizer' },
    { icon: Grid3x3, label: 'Correlation', path: '/correlation' },
    { icon: Newspaper, label: 'News Feed', path: '/news' },
    { icon: Activity, label: 'Model Performance', path: '/model-performance' },
    { icon: Zap, label: 'System Status', path: '/status' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  const handleNav = (path: string) => {
    window.location.href = path;
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(true)}
        className="lg:hidden fixed bottom-4 right-4 z-50 p-3 bg-green-600 rounded-full shadow-lg"
      >
        <Menu className="w-6 h-6 text-white" />
      </button>

      {/* Mobile menu overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setIsOpen(false)} />
          
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-slate-900 border-l border-slate-700 p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-green-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">MP</span>
                </div>
                <span className="text-white font-semibold">Market Predictor</span>
              </div>
              <button onClick={() => setIsOpen(false)}>
                <X className="w-6 h-6 text-slate-400" />
              </button>
            </div>

            <nav className="space-y-2">
              {navItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => handleNav(item.path)}
                  className="w-full flex items-center gap-3 p-3 rounded-lg text-left hover:bg-slate-800 transition-colors"
                >
                  <item.icon className="w-5 h-5 text-slate-400" />
                  <span className="text-white">{item.label}</span>
                </button>
              ))}
            </nav>

            <div className="mt-8 pt-8 border-t border-slate-700">
              <p className="text-slate-400 text-sm mb-4">Quick Actions</p>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    setCurrentSymbol('AAPL');
                    setIsOpen(false);
                  }}
                  className="w-full p-3 bg-slate-800 rounded-lg text-left hover:bg-slate-700 transition-colors"
                >
                  <p className="text-white font-medium">Load AAPL</p>
                  <p className="text-slate-400 text-sm">Quick symbol load</p>
                </button>
                <button
                  onClick={() => {
                    setCurrentSymbol('BTC-USD');
                    setIsOpen(false);
                  }}
                  className="w-full p-3 bg-slate-800 rounded-lg text-left hover:bg-slate-700 transition-colors"
                >
                  <p className="text-white font-medium">Load BTC-USD</p>
                  <p className="text-slate-400 text-sm">Quick symbol load</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
