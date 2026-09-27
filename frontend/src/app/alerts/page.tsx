'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { Bell, Plus, Trash2, Check, X, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface Alert {
  id: string;
  symbol: string;
  type: 'price' | 'signal';
  condition: 'above' | 'below' | 'equals';
  value: number;
  enabled: boolean;
  triggered: boolean;
  created_at: string;
}

export default function AlertsPage() {
  const { user } = useStore();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAlert, setNewAlert] = useState({
    symbol: '',
    type: 'price' as 'price' | 'signal',
    condition: 'above' as 'above' | 'below' | 'equals',
    value: 0,
  });

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    // Mock data - replace with actual API call
    setTimeout(() => {
      setAlerts([
        {
          id: '1',
          symbol: 'AAPL',
          type: 'price',
          condition: 'above',
          value: 150,
          enabled: true,
          triggered: false,
          created_at: '2024-01-15T10:30:00Z',
        },
        {
          id: '2',
          symbol: 'BTC-USD',
          type: 'signal',
          condition: 'equals',
          value: 1,
          enabled: true,
          triggered: false,
          created_at: '2024-01-16T14:45:00Z',
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const handleAddAlert = () => {
    if (!newAlert.symbol || !newAlert.value) return;

    const alert: Alert = {
      id: Date.now().toString(),
      ...newAlert,
      enabled: true,
      triggered: false,
      created_at: new Date().toISOString(),
    };

    setAlerts([...alerts, alert]);
    setNewAlert({
      symbol: '',
      type: 'price',
      condition: 'above',
      value: 0,
    });
    setShowAddForm(false);
  };

  const handleDeleteAlert = (id: string) => {
    setAlerts(alerts.filter(alert => alert.id !== id));
  };

  const handleToggleAlert = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, enabled: !alert.enabled } : alert
    ));
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'price': return <Bell className="w-4 h-4" />;
      case 'signal': return <AlertTriangle className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case 'above': return 'text-green-400';
      case 'below': return 'text-red-400';
      case 'equals': return 'text-yellow-400';
      default: return 'text-slate-400';
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-slate-400 mb-6">Please sign in to access alerts</p>
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
            <h1 className="text-2xl font-bold text-white">Price & Signal Alerts</h1>
            <p className="text-slate-400">Set up notifications for price movements and signal changes</p>
          </div>
          
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Alert
          </button>
        </div>

        {showAddForm && (
          <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">Create New Alert</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Symbol</label>
                <input
                  type="text"
                  value={newAlert.symbol}
                  onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value.toUpperCase() })}
                  placeholder="AAPL, BTC-USD, etc."
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Type</label>
                <select
                  value={newAlert.type}
                  onChange={(e) => setNewAlert({ ...newAlert, type: e.target.value as 'price' | 'signal' })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="price">Price Alert</option>
                  <option value="signal">Signal Alert</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Condition</label>
                <select
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert({ ...newAlert, condition: e.target.value as 'above' | 'below' | 'equals' })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="above">Above</option>
                  <option value="below">Below</option>
                  <option value="equals">Equals</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Value</label>
                <input
                  type="number"
                  value={newAlert.value}
                  onChange={(e) => setNewAlert({ ...newAlert, value: parseFloat(e.target.value) || 0 })}
                  placeholder="Price or signal value"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-4">
              <button
                onClick={handleAddAlert}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Create Alert
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
            <p className="text-slate-400">Loading alerts...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No alerts set up yet</p>
            <p className="text-slate-500 text-sm">Create your first alert to get notified</p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`bg-slate-800/50 rounded-lg border p-4 transition-colors ${
                  alert.enabled ? 'border-slate-700' : 'border-slate-800 opacity-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${alert.enabled ? 'bg-slate-700' : 'bg-slate-800'}`}>
                      {getAlertIcon(alert.type)}
                    </div>
                    
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-white font-semibold">{alert.symbol}</span>
                        <span className="text-slate-400 text-sm">•</span>
                        <span className="text-slate-400 text-sm capitalize">{alert.type}</span>
                      </div>
                      <p className="text-slate-400 text-sm">
                        {alert.condition} <span className={getConditionColor(alert.condition)}>${alert.value}</span>
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {alert.triggered && (
                      <span className="px-2 py-1 bg-yellow-600/20 text-yellow-400 text-xs rounded-full">
                        Triggered
                      </span>
                    )}
                    
                    <button
                      onClick={() => handleToggleAlert(alert.id)}
                      className={`p-2 rounded-lg transition-colors ${
                        alert.enabled ? 'bg-green-600/20 text-green-400' : 'bg-slate-700 text-slate-400'
                      }`}
                    >
                      {alert.enabled ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                    </button>
                    
                    <button
                      onClick={() => handleDeleteAlert(alert.id)}
                      className="p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
