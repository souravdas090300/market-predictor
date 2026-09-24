'use client';

import { useState, useEffect } from 'react';
import { Activity, Server, Database, Cpu, Memory, Network, Clock, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { statusAPI } from '@/lib/api';

interface SystemStatus {
  overall: 'healthy' | 'degraded' | 'down';
  uptime: number;
  last_check: string;
  services: {
    api: { status: 'up' | 'down' | 'degraded'; response_time: number; last_check: string };
    database: { status: 'up' | 'down' | 'degraded'; response_time: number; last_check: string };
    cache: { status: 'up' | 'down' | 'degraded'; response_time: number; last_check: string };
    ml_model: { status: 'up' | 'down' | 'degraded'; response_time: number; last_check: string };
    data_feed: { status: 'up' | 'down' | 'degraded'; response_time: number; last_check: string };
  };
  metrics: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_in: number;
    network_out: number;
    active_connections: number;
    requests_per_minute: number;
    error_rate: number;
  };
  incidents: Array<{
    id: string;
    type: 'info' | 'warning' | 'error';
    message: string;
    timestamp: string;
    resolved: boolean;
  }>;
  system_info?: {
    version: string;
    python_version: string;
    platform: string;
  };
}

export default function StatusPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    
    if (autoRefresh) {
      const interval = setInterval(loadStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadStatus = async () => {
    try {
      setError(null);
      const data = await statusAPI.getSystemStatus();
      setStatus(data);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load status:', err);
      setError(err.response?.data?.detail || 'Failed to load system status');
      setLoading(false);
    }
  };

  const getStatusIcon = (serviceStatus: 'up' | 'down' | 'degraded') => {
    switch (serviceStatus) {
      case 'up': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'down': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (serviceStatus: 'up' | 'down' | 'degraded') => {
    switch (serviceStatus) {
      case 'up': return 'text-green-400 bg-green-600/20 border-green-500';
      case 'down': return 'text-red-400 bg-red-600/20 border-red-500';
      case 'degraded': return 'text-yellow-400 bg-yellow-600/20 border-yellow-500';
    }
  };

  const getOverallStatus = () => {
    if (!status) return { icon: <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />, color: 'text-slate-400', bg: 'bg-slate-600/20', border: 'border-slate-500' };
    
    switch (status.overall) {
      case 'healthy': return { icon: <CheckCircle className="w-8 h-8 text-green-500" />, color: 'text-green-400', bg: 'bg-green-600/20', border: 'border-green-500' };
      case 'degraded': return { icon: <AlertTriangle className="w-8 h-8 text-yellow-500" />, color: 'text-yellow-400', bg: 'bg-yellow-600/20', border: 'border-yellow-500' };
      case 'down': return { icon: <XCircle className="w-8 h-8 text-red-500" />, color: 'text-red-400', bg: 'bg-red-600/20', border: 'border-red-500' };
    }
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">System Status</h1>
          <p className="text-slate-400">Real-time monitoring of Market Predictor services</p>
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
            onClick={loadStatus}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {error ? (
        <div className="bg-red-600/20 border border-red-500 rounded-lg p-6 mb-6">
          <div className="flex items-center gap-3">
            <XCircle className="w-6 h-6 text-red-500" />
            <div>
              <h3 className="text-white font-semibold">Error Loading Status</h3>
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          </div>
        </div>
      ) : null}

      {loading ? (
        <div className="text-center py-12">
          <RefreshCw className="w-16 h-16 text-slate-600 mx-auto mb-4 animate-spin" />
          <p className="text-slate-400">Loading system status...</p>
        </div>
      ) : status ? (
        <div className="space-y-6">
          {/* Overall Status */}
          <div className={`bg-slate-800/50 rounded-lg border p-8 ${overallStatus.border}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {overallStatus.icon}
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    All Systems {status.overall === 'healthy' ? 'Operational' : status.overall === 'degraded' ? 'Degraded' : 'Down'}
                  </h2>
                  <p className="text-slate-400 mt-1">
                    Last checked: {new Date(status.last_check).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className={`text-3xl font-bold ${overallStatus.color}`}>
                  {status.uptime.toFixed(2)}%
                </div>
                <p className="text-slate-400 text-sm">Uptime (30d)</p>
              </div>
            </div>
          </div>

          {/* Service Status */}
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Service Status</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Server className="w-5 h-5 text-slate-400" />
                    <span className="text-white font-medium">API Server</span>
                  </div>
                  {getStatusIcon(status.services.api.status)}
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(status.services.api.status)}`}>
                      {status.services.api.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Response Time</span>
                    <span className="text-white font-mono">{status.services.api.response_time}ms</span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-cent
