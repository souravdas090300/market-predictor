'use client';

import { useState } from 'react';
import { Activity, CheckCircle, AlertTriangle, Clock } from 'lucide-react';

export default function StatusPage() {
  const [systemStatus] = useState({
    api: 'operational',
    database: 'operational',
    model: 'operational',
    lastUpdate: new Date().toISOString(),
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      default: return 'text-red-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational': return <CheckCircle className="w-5 h-5" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5" />;
      default: return <Clock className="w-5 h-5" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">System Status</h1>
        <p className="text-slate-400">Real-time system health and operational status</p>
      </div>

      {/* System Overview */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="w-6 h-6 text-slate-400" />
          <h2 className="text-xl font-semibold text-white">System Overview</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">API Status</span>
              <span className={getStatusColor(systemStatus.api)}>
                {getStatusIcon(systemStatus.api)}
              </span>
            </div>
            <p className="text-white font-medium capitalize">{systemStatus.api}</p>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">Database</span>
              <span className={getStatusColor(systemStatus.database)}>
                {getStatusIcon(systemStatus.database)}
              </span>
            </div>
            <p className="text-white font-medium capitalize">{systemStatus.database}</p>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">Model Service</span>
              <span className={getStatusColor(systemStatus.model)}>
                {getStatusIcon(systemStatus.model)}
              </span>
            </div>
            <p className="text-white font-medium capitalize">{systemStatus.model}</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
        <h3 className="text-white font-medium mb-3">Recent Activity</h3>
        <div className="space-y-3">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-green-500" />
                <span className="text-white text-sm">System Operational</span>
              </div>
              <span className="text-slate-400 text-xs">2 minutes ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
