'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { Gauge, Clock, AlertTriangle, CheckCircle, TrendingUp, RefreshCw } from 'lucide-react';

interface RateLimitInfo {
  endpoint: string;
  limit: number;
  remaining: number;
  reset: string;
  used: number;
  usedPercent: number;
}

export default function RateLimitsPage() {
  const { user } = useStore();
  const [rateLimits, setRateLimits] = useState<RateLimitInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRateLimits();
  }, []);

  const loadRateLimits = async () => {
    // Mock data - replace with actual API call
    setTimeout(() => {
      setRateLimits([
        {
          endpoint: '/api/signal',
          limit: 100,
          remaining: 75,
          reset: new Date(Date.now() + 3600000).toISOString(),
          used: 25,
          usedPercent: 25,
        },
        {
          endpoint: '/api/watchlist',
          limit: 200,
          remaining: 180,
          reset: new Date(Date.now() + 3600000).toISOString(),
          used: 20,
          usedPercent: 10,
        },
        {
          endpoint: '/api/material',
          limit: 50,
          remaining: 5,
          reset: new Date(Date.now() + 1800000).toISOString(),
          used: 45,
          usedPercent: 90,
        },
        {
          endpoint: '/api/bulk',
          limit: 10,
          remaining: 8,
          reset: new Date(Date.now() + 7200000).toISOString(),
          used: 2,
          usedPercent: 20,
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const getStatusColor = (usedPercent: number) => {
    if (usedPercent >= 90) return 'text-red-400 bg-red-600/20 border-red-500';
    if (usedPercent >= 70) return 'text-yellow-400 bg-yellow-600/20 border-yellow-500';
    return 'text-green-400 bg-green-600/20 border-green-500';
  };

  const getStatusIcon = (usedPercent: number) => {
    if (usedPercent >= 90) return <AlertTriangle className="w-4 h-4" />;
    if (usedPercent >= 70) return <Clock className="w-4 h-4" />;
    return <CheckCircle className="w-4 h-4" />;
  };

  const getTimeUntilReset = (reset: string) => {
    const resetTime = new Date(reset).getTime();
    const now = Date.now();
    const diff = resetTime - now;
    
    if (diff <= 0) return 'Reset now';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-slate-400 mb-6">Please sign in to access rate limits</p>
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
            <h1 className="text-2xl font-bold text-white">API Rate Limits</h1>
            <p className="text-slate-400">Monitor your API usage and rate limits</p>
          </div>
          
          <button
            onClick={loadRateLimits}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-slate-300" />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-slate-400">Loading rate limits...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Gauge className="w-4 h-4 text-green-500" />
                  <span className="text-slate-400 text-sm">Total Requests</span>
                </div>
                <p className="text-2xl font-bold text-white">
                  {rateLimits.reduce((sum, limit) => sum + limit.used, 0)}
                </p>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <span className="text-slate-400 text-sm">Total Limit</span>
                </div>
                <p className="text-2xl font-bold text-white">
                  {rateLimits.reduce((sum, limit) => sum + limit.limit, 0)}
                </p>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-yellow-500" />
                  <span className="text-slate-400 text-sm">Overall Usage</span>
                </div>
                <p className="text-2xl font-bold text-white">
                  {Math.round(
                    (rateLimits.reduce((sum, limit) => sum + limit.used, 0) / 
                     rateLimits.reduce((sum, limit) => sum + limit.limit, 0)) * 100
                  )}%
                </p>
              </div>
            </div>

            {/* Rate Limits Table */}
            <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
              <div className="p-4 border-b border-slate-700">
                <h3 className="text-lg font-semibold text-white">Endpoint Limits</h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-900/50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Endpoint</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Usage</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Limit</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Remaining</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Status</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Reset In</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rateLimits.map((limit) => (
                      <tr key={limit.endpoint} className="border-t border-slate-700">
                        <td className="px-4 py-3">
                          <code className="text-white font-mono text-sm">{limit.endpoint}</code>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-slate-700 rounded-full h-2 w-24">
                              <div
                                className={`h-2 rounded-full ${
                                  limit.usedPercent >= 90 ? 'bg-red-500' :
                                  limit.usedPercent >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                                }`}
                                style={{ width: `${limit.usedPercent}%` }}
                              />
                            </div>
                            <span className="text-white text-sm">{limit.usedPercent}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-white">{limit.limit}</td>
                        <td className="px-4 py-3 text-white">{limit.remaining}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(limit.usedPercent)}`}>
                            {getStatusIcon(limit.usedPercent)}
                            <span className="ml-1">
                              {limit.usedPercent >= 90 ? 'Critical' :
                               limit.usedPercent >= 70 ? 'Warning' : 'Good'}
                            </span>
                          </span>
                        </td>
                        <td className="px-4 py-3 text-white">
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4 text-slate-400" />
                            <span className="text-sm">{getTimeUntilReset(limit.reset)}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Usage Tips */}
            <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Usage Tips</h3>
              <ul className="space-y-2 text-slate-400">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                  <span>Cache API responses when possible to reduce request count</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                  <span>Use bulk endpoints for multiple symbol requests</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                  <span>Implement request throttling in your application</span>
                </li>
                <li className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                  <span>Monitor usage patterns to avoid hitting limits during peak times</span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
