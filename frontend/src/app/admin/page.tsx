'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import DashboardLayout from '@/components/DashboardLayout';
import MobileNav from '@/components/MobileNav';
import { Users, Settings, Shield, Key, ToggleLeft, ToggleRight, Search, Edit, Ban, Check, FileText, DollarSign, Activity, Lock, BarChart3 } from 'lucide-react';

interface User {
  id: string;
  username: string;
  email: string;
  roles: string[];
  subscription: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'suspended' | 'banned';
  created_at: string;
  last_login: string;
}

interface SystemConfig {
  maintenance_mode: boolean;
  registration_enabled: boolean;
  max_free_requests: number;
  pro_request_limit: number;
}

export default function AdminPage() {
  const { user } = useStore();
  const [users, setUsers] = useState<User[]>([]);
  const [config, setConfig] = useState<SystemConfig>({
    maintenance_mode: false,
    registration_enabled: true,
    max_free_requests: 100,
    pro_request_limit: 1000,
  });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'users' | 'settings' | 'api' | 'audit' | 'billing' | 'features' | '2fa' | 'activity'>('users');

  useEffect(() => {
    if (user?.roles?.includes('admin') || user?.roles?.includes('superuser')) {
      loadAdminData();
    }
  }, [user]);

  const loadAdminData = async () => {
    // Mock data - replace with actual API calls
    setTimeout(() => {
      setUsers([
        {
          id: '1',
          username: 'john_doe',
          email: 'john@example.com',
          roles: ['user'],
          subscription: 'pro',
          status: 'active',
          created_at: '2024-01-15T10:30:00Z',
          last_login: '2024-09-25T08:15:00Z',
        },
        {
          id: '2',
          username: 'jane_smith',
          email: 'jane@example.com',
          roles: ['user'],
          subscription: 'free',
          status: 'active',
          created_at: '2024-02-20T14:45:00Z',
          last_login: '2024-09-24T16:30:00Z',
        },
        {
          id: '3',
          username: 'admin_user',
          email: 'admin@example.com',
          roles: ['admin'],
          subscription: 'enterprise',
          status: 'active',
          created_at: '2024-01-01T09:00:00Z',
          last_login: '2024-09-25T09:00:00Z',
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const handleToggleUserStatus = (userId: string) => {
    setUsers(users.map(u => 
      u.id === userId 
        ? { ...u, status: u.status === 'active' ? 'suspended' : 'active' }
        : u
    ));
  };

  const handleBanUser = (userId: string) => {
    setUsers(users.map(u => 
      u.id === userId 
        ? { ...u, status: 'banned' }
        : u
    ));
  };

  const handleUpdateRole = (userId: string, newRole: string) => {
    setUsers(users.map(u =>
      u.id === userId
        ? { ...u, roles: [newRole] }
        : u
    ));
  };

  const handleUpdateSubscription = (userId: string, newSub: string) => {
    setUsers(users.map(u => 
      u.id === userId 
        ? { ...u, subscription: newSub as 'free' | 'pro' | 'enterprise' }
        : u
    ));
  };

  const handleConfigChange = (key: keyof SystemConfig, value: any) => {
    setConfig({ ...config, [key]: value });
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!user || (!user.roles?.includes('admin') && !user.roles?.includes('superuser'))) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-slate-400 mb-6">Admin access required</p>
          <a href="/" className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
            Go to Dashboard
          </a>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <MobileNav />
      
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
          <p className="text-slate-400">Manage users, settings, and system configuration</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-700 overflow-x-auto">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'users' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            Users
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'settings' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Settings className="w-4 h-4 inline mr-2" />
            Settings
          </button>
          <button
            onClick={() => setActiveTab('api')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'api' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Key className="w-4 h-4 inline mr-2" />
            API Keys
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'audit' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Audit Logs
          </button>
          <button
            onClick={() => setActiveTab('billing')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'billing' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <DollarSign className="w-4 h-4 inline mr-2" />
            Billing
          </button>
          <button
            onClick={() => setActiveTab('features')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'features' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Features
          </button>
          <button
            onClick={() => setActiveTab('2fa')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === '2fa' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Lock className="w-4 h-4 inline mr-2" />
            2FA
          </button>
          <button
            onClick={() => setActiveTab('activity')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'activity' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Activity className="w-4 h-4 inline mr-2" />
            Activity
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-slate-400">Loading admin data...</p>
          </div>
        ) : (
          <>
            {activeTab === 'users' && (
              <div className="space-y-6">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                {/* Users Table */}
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-900/50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">User</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Role</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Subscription</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Status</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Last Login</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredUsers.map((user) => (
                          <tr key={user.id} className="border-t border-slate-700">
                            <td className="px-4 py-3">
                              <div>
                                <p className="text-white font-medium">{user.username}</p>
                                <p className="text-slate-400 text-sm">{user.email}</p>
                              </div>
                            </td>
                            <td className="px-4 py-3">
                              <select
                                value={user.roles[0] || 'user'}
                                onChange={(e) => handleUpdateRole(user.id, e.target.value)}
                                className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none"
                              >
                                <option value="user">User</option>
                                <option value="admin">Admin</option>
                                <option value="superuser">Superuser</option>
                              </select>
                            </td>
                            <td className="px-4 py-3">
                              <select
                                value={user.subscription}
                                onChange={(e) => handleUpdateSubscription(user.id, e.target.value)}
                                className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none"
                              >
                                <option value="free">Free</option>
                                <option value="pro">Pro</option>
                                <option value="enterprise">Enterprise</option>
                              </select>
                            </td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                user.status === 'active' ? 'bg-green-600/20 text-green-400' :
                                user.status === 'suspended' ? 'bg-yellow-600/20 text-yellow-400' :
                                'bg-red-600/20 text-red-400'
                              }`}>
                                {user.status}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-slate-400 text-sm">
                              {new Date(user.last_login).toLocaleDateString()}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex gap-2">
                                <button
                                  onClick={() => handleToggleUserStatus(user.id)}
                                  className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                  title={user.status === 'active' ? 'Suspend' : 'Activate'}
                                >
                                  {user.status === 'active' ? <ToggleLeft className="w-4 h-4" /> : <ToggleRight className="w-4 h-4" />}
                                </button>
                                <button
                                  onClick={() => handleBanUser(user.id)}
                                  className="p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors"
                                  title="Ban User"
                                >
                                  <Ban className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">System Configuration</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">Maintenance Mode</p>
                        <p className="text-slate-400 text-sm">Disable access for non-admin users</p>
                      </div>
                      <button
                        onClick={() => handleConfigChange('maintenance_mode', !config.maintenance_mode)}
                        className={`p-2 rounded-lg transition-colors ${
                          config.maintenance_mode ? 'bg-green-600' : 'bg-slate-700'
                        }`}
                      >
                        {config.maintenance_mode ? <ToggleRight className="w-5 h-5 text-white" /> : <ToggleLeft className="w-5 h-5 text-slate-400" />}
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">Registration Enabled</p>
                        <p className="text-slate-400 text-sm">Allow new user registrations</p>
                      </div>
                      <button
                        onClick={() => handleConfigChange('registration_enabled', !config.registration_enabled)}
                        className={`p-2 rounded-lg transition-colors ${
                          config.registration_enabled ? 'bg-green-600' : 'bg-slate-700'
                        }`}
                      >
                        {config.registration_enabled ? <ToggleRight className="w-5 h-5 text-white" /> : <ToggleLeft className="w-5 h-5 text-slate-400" />}
                      </button>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Max Free Requests (per hour)</label>
                      <input
                        type="number"
                        value={config.max_free_requests}
                        onChange={(e) => handleConfigChange('max_free_requests', parseInt(e.target.value))}
                        className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Pro Request Limit (per hour)</label>
                      <input
                        type="number"
                        value={config.pro_request_limit}
                        onChange={(e) => handleConfigChange('pro_request_limit', parseInt(e.target.value))}
                        className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  </div>
                  
                  <button className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Save Changes
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">API Key Management</h3>
                <p className="text-slate-400 mb-4">Manage API keys for external integrations</p>
                
                <div className="space-y-4">
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">Production API Key</span>
                      <span className="text-green-400 text-sm">Active</span>
                    </div>
                    <code className="text-slate-400 text-sm">mp_prod_******************************</code>
                  </div>
                  
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">Test API Key</span>
                      <span className="text-yellow-400 text-sm">Test Mode</span>
                    </div>
                    <code className="text-slate-400 text-sm">mp_test_******************************</code>
                  </div>
                </div>
                
                <button className="mt-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors">
                  Generate New Key
                </button>
              </div>
            )}

            {activeTab === 'audit' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Audit Logs</h3>
                  <p className="text-slate-400 mb-4">Track all admin actions and security events</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Total Events</p>
                      <p className="text-2xl font-bold text-white">1,234</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Critical Events</p>
                      <p className="text-2xl font-bold text-red-400">3</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">This Week</p>
                      <p className="text-2xl font-bold text-green-400">156</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">User login attempt</p>
                        <p className="text-slate-400 text-sm">admin_user • 2 hours ago</p>
                      </div>
                      <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-xs">Success</span>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">Rate limit updated</p>
                        <p className="text-slate-400 text-sm">admin_user • 5 hours ago</p>
                      </div>
                      <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded text-xs">Config</span>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">Failed login attempt</p>
                        <p className="text-slate-400 text-sm">unknown • 1 day ago</p>
                      </div>
                      <span className="px-2 py-1 bg-red-600/20 text-red-400 rounded text-xs">Warning</span>
                    </div>
                  </div>
                  
                  <button className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Export Logs
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'billing' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Billing Analytics</h3>
                  <p className="text-slate-400 mb-4">Revenue, churn, and LTV metrics</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Monthly Revenue</p>
                      <p className="text-2xl font-bold text-white">$12,450</p>
                      <p className="text-green-400 text-sm">+15% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Churn Rate</p>
                      <p className="text-2xl font-bold text-white">2.3%</p>
                      <p className="text-green-400 text-sm">-0.5% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Avg LTV</p>
                      <p className="text-2xl font-bold text-white">$348</p>
                      <p className="text-green-400 text-sm">+12% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Active Subscriptions</p>
                      <p className="text-2xl font-bold text-white">456</p>
                      <p className="text-green-400 text-sm">+23 new this month</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-white font-medium">Revenue by Tier</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Enterprise</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-green-500" style={{ width: '60%' }}></div>
                          </div>
                          <span className="text-white text-sm">$7,470</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Pro</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: '30%' }}></div>
                          </div>
                          <span className="text-white text-sm">$3,735</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Basic</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-yellow-500" style={{ width: '10%' }}></div>
                          </div>
                          <span className="text-white text-sm">$1,245</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <button className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Generate Report
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'features' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Feature Limits</h3>
                  <p className="text-slate-400 mb-4">Configure feature access by subscription tier</p>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-900/50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Feature</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Free</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Basic</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Pro</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Enterprise</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-t border-slate-700">
                          <td className="px-4 py-3 text-white">API Requests/hr</td>
                          <td className="px-4 py-3 text-slate-400">100</td>
                          <td className="px-4 py-3 text-slate-400">1,000</td>
                          <td className="px-4 py-3 text-slate-400">10,000</td>
                          <td className="px-4 py-3 text-green-400">Unlimited</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-4 py-3 text-white">Predictions/day</td>
                          <td className="px-4 py-3 text-slate-400">50</td>
                          <td className="px-4 py-3 text-slate-400">500</td>
                          <td className="px-4 py-3 text-slate-400">5,000</td>
                          <td className="px-4 py-3 text-green-400">Unlimited</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-4 py-3 text-white">Watchlist Size</td>
                          <td className="px-4 py-3 text-slate-400">10</td>
                          <td className="px-4 py-3 text-slate-400">50</td>
                          <td className="px-4 py-3 text-slate-400">200</td>
                          <td className="px-4 py-3 text-green-400">Unlimited</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-4 py-3 text-white">Real-time Data</td>
                          <td className="px-4 py-3 text-red-400">✗</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-4 py-3 text-white">API Access</td>
                          <td className="px-4 py-3 text-red-400">✗</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-4 py-3 text-white">Custom Models</td>
                          <td className="px-4 py-3 text-red-400">✗</td>
                          <td className="px-4 py-3 text-red-400">✗</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                          <td className="px-4 py-3 text-green-400">✓</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  
                  <button className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Update Limits
                  </button>
                </div>
              </div>
            )}

            {activeTab === '2fa' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Two-Factor Authentication</h3>
                  <p className="text-slate-400 mb-4">Manage 2FA for superuser accounts</p>
                  
                  <div className="space-y-4">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium">Your 2FA Status</span>
                        <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-xs">Enabled</span>
                      </div>
                      <p className="text-slate-400 text-sm">TOTP (Google Authenticator)</p>
                      <p className="text-slate-400 text-sm">Last used: 2 hours ago</p>
                    </div>
                    
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <h4 className="text-white font-medium mb-2">Backup Codes</h4>
                      <p className="text-slate-400 text-sm mb-3">8 remaining backup codes</p>
                      <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm">
                        Regenerate Backup Codes
                      </button>
                    </div>
                    
                    <div className="bg-yellow-600/10 border border-yellow-600/30 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-yellow-400 mt-0.5" />
                        <div>
                          <p className="text-yellow-400 font-medium">Security Recommendation</p>
                          <p className="text-slate-400 text-sm">Enable 2FA for all superuser accounts to enhance security.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex gap-2">
                    <button className="px-4 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors">
                      Disable 2FA
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'activity' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Activity Analytics</h3>
                  <p className="text-slate-400 mb-4">User engagement and activity metrics</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Daily Active Users</p>
                      <p className="text-2xl font-bold text-white">234</p>
                      <p className="text-green-400 text-sm">+12% from yesterday</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Weekly Active Users</p>
                      <p className="text-2xl font-bold text-white">567</p>
                      <p className="text-green-400 text-sm">+8% from last week</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Stickiness Ratio</p>
                      <p className="text-2xl font-bold text-white">41%</p>
                      <p className="text-green-400 text-sm">+3% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-sm">Avg Session Duration</p>
                      <p className="text-2xl font-bold text-white">18m</p>
                      <p className="text-green-400 text-sm">+2m from last week</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-white font-medium">Most Used Features</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Predictions</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-green-500" style={{ width: '75%' }}></div>
                          </div>
                          <span className="text-white text-sm">75%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Watchlist</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: '60%' }}></div>
                          </div>
                          <span className="text-white text-sm">60%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Signals</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-yellow-500" style={{ width: '45%' }}></div>
                          </div>
                          <span className="text-white text-sm">45%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Charts</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-purple-500" style={{ width: '30%' }}></div>
                          </div>
                          <span className="text-white text-sm">30%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <h4 className="text-white font-medium mb-3">Peak Activity Time</h4>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400">Most active: <span className="text-white font-medium">Tuesday 2-4 PM</span></p>
                      <p className="text-slate-400">Peak hour: <span className="text-white font-medium">3 PM (UTC)</span></p>
                    </div>
                  </div>
                  
                  <button className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    View Detailed Analytics
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
