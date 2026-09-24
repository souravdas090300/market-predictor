'use client';

import { useState } from 'react';
import { useStore } from '@/store/useStore';
import { Menu, Search, RefreshCw, User, LogOut, Settings, Moon, Sun, Activity, LayoutGrid } from 'lucide-react';

export default function Header() {
  const { 
    theme, 
    setTheme, 
    sidebarOpen, 
    setSidebarOpen, 
    user, 
    logout,
    currentSymbol,
    setCurrentSymbol 
  } = useStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleThemeToggle = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark');
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      setCurrentSymbol(searchQuery.trim().toUpperCase());
      setSearchQuery('');
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <header className="bg-slate-900 border-b border-slate-700 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5 text-slate-300" />
        </button>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-green-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">MP</span>
          </div>
          <span className="text-white font-semibold text-lg">Market Predictor</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search symbol (e.g., AAPL, BTC-USD)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 w-64"
          />
        </div>

        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-slate-300 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>

        <button
          onClick={handleThemeToggle}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
        >
          {theme === 'dark' ? (
            <Sun className="w-5 h-5 text-slate-300" />
          ) : (
            <Moon className="w-5 h-5 text-slate-300" />
          )}
        </button>

        <button
          onClick={() => window.location.href = '/assets'}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          title="All Assets Live Status"
        >
          <LayoutGrid className="w-5 h-5 text-slate-300" />
        </button>

        <button
          onClick={() => window.location.href = '/status'}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          title="System Status"
        >
          <Activity className="w-5 h-5 text-slate-300" />
        </button>

        {user ? (
          <div className="relative group">
            <button className="flex items-center gap-2 p-2 hover:bg-slate-800 rounded-lg transition-colors">
              <User className="w-5 h-5 text-slate-300" />
              <span className="text-white text-sm">{user.username}</span>
            </button>
            
            <div className="absolute right-0 top-full mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
              <div className="p-2">
                <button
                  onClick={() => window.location.href = '/settings'}
                  className="w-full flex items-center gap-2 px-3 py-2 text-left text-slate-300 hover:bg-slate-700 rounded-lg transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-3 py-2 text-left text-red-400 hover:bg-slate-700 rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <button
            onClick={() => window.location.href = '/login'}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
          >
            Login
          </button>
        )}
      </div>
    </header>
  );
}
