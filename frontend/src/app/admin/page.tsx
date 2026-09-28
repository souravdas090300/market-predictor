'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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
  const router = useRouter();
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
    // Check if user has admin role
    if (!user || !user.roles?.includes('admin')) {
      router.push('/');
      return;
    }
    loadAdminData();
  }, [user, router]);

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

  const filteredUsers = users.filter((u) =>
    u.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!user || !user.roles?.includes('admin')) {
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
      
      <div className="p-4 md:p-6">
        <div className="mb-6">
          <h1 className="text-xl md:text-2xl font-bold text-white">Admin Panel</h1>
          <p className="text-slate-400 text-sm md:text-base">Manage users, settings, and system configuration</p>
        </div>

        {/* Tabs - Mobile: Horizontal scroll, Desktop: Normal */}
        <div className="flex gap-2 mb-6 border-b border-slate-700 overflow-x-auto pb-2 md:pb-0 scrollbar-hide mobile-scroll">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === 'users' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">Users</span>
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === 'settings' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Settings className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">Settings</span>
          </button>
          <button
            onClick={() => setActiveTab('api')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === 'api' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Key className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">API Keys</span>
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === 'audit' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">Audit Logs</span>
          </button>
          <button
            onClick={() => setActiveTab('billing')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === 'billing' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <DollarSign className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">Billing</span>
          </button>
          <button
            onClick={() => setActiveTab('features')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === 'features' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">Features</span>
          </button>
          <button
            onClick={() => setActiveTab('2fa')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
              activeTab === '2fa' 
                ? 'text-green-400 border-b-2 border-green-400' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Lock className="w-4 h-4 inline mr-1 md:mr-2" />
            <span className="hidden sm:inline">2FA</span>
          </button>
          <button
            onClick={() => setActiveTab('activity')}
            className={`px-3 py-2 md:px-4 md:py-2 font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
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
            <p className="text-slate-400 text-sm md:text-base">Loading admin data...</p>
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
                    className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                  />
                </div>

                {/* Users Table - Mobile friendly */}
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
                  {/* Desktop Table */}
                  <div className="hidden md:block overflow-x-auto">
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

                  {/* Mobile Card View */}
                  <div className="md:hidden space-y-4 p-4">
                    {filteredUsers.map((user) => (
                      <div key={user.id} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <p className="text-white font-medium">{user.username}</p>
                            <p className="text-slate-400 text-sm">{user.email}</p>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            user.status === 'active' ? 'bg-green-600/20 text-green-400' :
                            user.status === 'suspended' ? 'bg-yellow-600/20 text-yellow-400' :
                            'bg-red-600/20 text-red-400'
                          }`}>
                            {user.status}
                          </span>
                        </div>
                        
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-slate-400 text-sm">Role:</span>
                            <select
                              value={user.roles[0] || 'user'}
                              onChange={(e) => handleUpdateRole(user.id, e.target.value)}
                              className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none"
                            >
                              <option value="user">User</option>
                              <option value="admin">Admin</option>
                              <option value="superuser">Superuser</option>
                            </select>
                          </div>
                          
                          <div className="flex justify-between items-center">
                            <span className="text-slate-400 text-sm">Subscription:</span>
                            <select
                              value={user.subscription}
                              onChange={(e) => handleUpdateSubscription(user.id, e.target.value)}
                              className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm focus:outline-none"
                            >
                              <option value="free">Free</option>
                              <option value="pro">Pro</option>
                              <option value="enterprise">Enterprise</option>
                            </select>
                          </div>
                          
                          <div className="flex justify-between items-center">
                            <span className="text-slate-400 text-sm">Last Login:</span>
                            <span className="text-slate-300 text-sm">{new Date(user.last_login).toLocaleDateString()}</span>
                          </div>
                          
                          <div className="flex gap-2 pt-2">
                            <button
                              onClick={() => handleToggleUserStatus(user.id)}
                              className="flex-1 p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                              {user.status === 'active' ? <ToggleLeft className="w-4 h-4" /> : <ToggleRight className="w-4 h-4" />}
                              <span className="text-sm">{user.status === 'active' ? 'Suspend' : 'Activate'}</span>
                            </button>
                            <button
                              onClick={() => handleBanUser(user.id)}
                              className="flex-1 p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors flex items-center justify-center gap-2"
                            >
                              <Ban className="w-4 h-4" />
                              <span className="text-sm">Ban</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">System Configuration</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-white font-medium text-sm md:text-base">Maintenance Mode</p>
                        <p className="text-slate-400 text-xs md:text-sm">Disable access for non-admin users</p>
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
                      <div className="flex-1">
                        <p className="text-white font-medium text-sm md:text-base">Registration Enabled</p>
                        <p className="text-slate-400 text-xs md:text-sm">Allow new user registrations</p>
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
                        className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Pro Request Limit (per hour)</label>
                      <input
                        type="number"
                        value={config.pro_request_limit}
                        onChange={(e) => handleConfigChange('pro_request_limit', parseInt(e.target.value))}
                        className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                      />
                    </div>
                  </div>
                  
                  <button className="mt-4 w-full md:w-auto px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Save Changes
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                <h3 className="text-lg font-semibold text-white mb-4">API Key Management</h3>
                <p className="text-slate-400 mb-4 text-sm md:text-base">Manage API keys for external integrations</p>
                
                <div className="space-y-4">
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium text-sm md:text-base">Production API Key</span>
                      <span className="text-green-400 text-sm">Active</span>
                    </div>
                    <code className="text-slate-400 text-xs md:text-sm break-all">mp_prod_******************************</code>
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
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Audit Logs</h3>
                  <p className="text-slate-400 mb-4 text-sm md:text-base">Track all admin actions and security events</p>
                  
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
                      <div className="flex-1 min-w-0">
                        <p className="text-white font-medium text-sm md:text-base truncate">User login attempt</p>
                        <p className="text-slate-400 text-xs md:text-sm truncate">admin_user • 2 hours ago</p>
                      </div>
                      <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-xs ml-2 flex-shrink-0">Success</span>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-white font-medium text-sm md:text-base truncate">Rate limit updated</p>
                        <p className="text-slate-400 text-xs md:text-sm truncate">admin_user • 5 hours ago</p>
                      </div>
                      <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded text-xs ml-2 flex-shrink-0">Config</span>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-white font-medium text-sm md:text-base truncate">Failed login attempt</p>
                        <p className="text-slate-400 text-xs md:text-sm truncate">unknown • 1 day ago</p>
                      </div>
                      <span className="px-2 py-1 bg-red-600/20 text-red-400 rounded text-xs ml-2 flex-shrink-0">Warning</span>
                    </div>
                  </div>
                  
                  <button className="mt-4 w-full md:w-auto px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Export Logs
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'billing' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Billing Analytics</h3>
                  <p className="text-slate-400 mb-4 text-sm md:text-base">Revenue, churn, and LTV metrics</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Monthly Revenue</p>
                      <p className="text-xl md:text-2xl font-bold text-white">$12,450</p>
                      <p className="text-green-400 text-xs md:text-sm">+15% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Churn Rate</p>
                      <p className="text-xl md:text-2xl font-bold text-white">2.3%</p>
                      <p className="text-green-400 text-xs md:text-sm">-0.5% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Avg LTV</p>
                      <p className="text-xl md:text-2xl font-bold text-white">$348</p>
                      <p className="text-green-400 text-xs md:text-sm">+12% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Active Subscriptions</p>
                      <p className="text-xl md:text-2xl font-bold text-white">456</p>
                      <p className="text-green-400 text-xs md:text-sm">+23 new this month</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-white font-medium text-sm md:text-base">Revenue by Tier</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Enterprise</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-green-500" style={{ width: '60%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">$7,470</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Pro</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: '30%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">$3,735</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Basic</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-yellow-500" style={{ width: '10%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">$1,245</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <button className="mt-4 w-full md:w-auto px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Generate Report
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'features' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Feature Limits</h3>
                  <p className="text-slate-400 mb-4 text-sm md:text-base">Configure feature access by subscription tier</p>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-900/50">
                        <tr>
                          <th className="px-2 md:px-4 py-3 text-left text-xs md:text-sm font-medium text-slate-400">Feature</th>
                          <th className="px-2 md:px-4 py-3 text-left text-xs md:text-sm font-medium text-slate-400">Free</th>
                          <th className="px-2 md:px-4 py-3 text-left text-xs md:text-sm font-medium text-slate-400">Basic</th>
                          <th className="px-2 md:px-4 py-3 text-left text-xs md:text-sm font-medium text-slate-400">Pro</th>
                          <th className="px-2 md:px-4 py-3 text-left text-xs md:text-sm font-medium text-slate-400">Enterprise</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-t border-slate-700">
                          <td className="px-2 md:px-4 py-3 text-white text-xs md:text-sm">API Requests/hr</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">100</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">1,000</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">10,000</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">Unlimited</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-2 md:px-4 py-3 text-white text-xs md:text-sm">Predictions/day</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">50</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">500</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">5,000</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">Unlimited</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-2 md:px-4 py-3 text-white text-xs md:text-sm">Watchlist Size</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">10</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">50</td>
                          <td className="px-2 md:px-4 py-3 text-slate-400 text-xs md:text-sm">200</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">Unlimited</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-2 md:px-4 py-3 text-white text-xs md:text-sm">Real-time Data</td>
                          <td className="px-2 md:px-4 py-3 text-red-400 text-xs md:text-sm">✗</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-2 md:px-4 py-3 text-white text-xs md:text-sm">API Access</td>
                          <td className="px-2 md:px-4 py-3 text-red-400 text-xs md:text-sm">✗</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                        </tr>
                        <tr className="border-t border-slate-700">
                          <td className="px-2 md:px-4 py-3 text-white text-xs md:text-sm">Custom Models</td>
                          <td className="px-2 md:px-4 py-3 text-red-400 text-xs md:text-sm">✗</td>
                          <td className="px-2 md:px-4 py-3 text-red-400 text-xs md:text-sm">✗</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                          <td className="px-2 md:px-4 py-3 text-green-400 text-xs md:text-sm">✓</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  
                  <button className="mt-4 w-full md:w-auto px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                    Update Limits
                  </button>
                </div>
              </div>
            )}

            {activeTab === '2fa' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Two-Factor Authentication</h3>
                  <p className="text-slate-400 mb-4 text-sm md:text-base">Manage 2FA for superuser accounts</p>
                  
                  <div className="space-y-4">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium text-sm md:text-base">Your 2FA Status</span>
                        <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-xs">Enabled</span>
                      </div>
                      <p className="text-slate-400 text-xs md:text-sm">TOTP (Google Authenticator)</p>
                      <p className="text-slate-400 text-xs md:text-sm">Last used: 2 hours ago</p>
                    </div>
                    
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <h4 className="text-white font-medium text-sm md:text-base mb-2">Backup Codes</h4>
                      <p className="text-slate-400 text-xs md:text-sm mb-3">8 remaining backup codes</p>
                      <button className="w-full md:w-auto px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm">
                        Regenerate Backup Codes
                      </button>
                    </div>
                    
                    <div className="bg-yellow-600/10 border border-yellow-600/30 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-yellow-400 font-medium text-sm md:text-base">Security Recommendation</p>
                          <p className="text-slate-400 text-xs md:text-sm">Enable 2FA for all superuser accounts to enhance security.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex gap-2 flex-col md:flex-row">
                    <button className="w-full md:w-auto px-4 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors">
                      Disable 2FA
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'activity' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-4 md:p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Activity Analytics</h3>
                  <p className="text-slate-400 mb-4 text-sm md:text-base">User engagement and activity metrics</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Daily Active Users</p>
                      <p className="text-xl md:text-2xl font-bold text-white">234</p>
                      <p className="text-green-400 text-xs md:text-sm">+12% from yesterday</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Weekly Active Users</p>
                      <p className="text-xl md:text-2xl font-bold text-white">567</p>
                      <p className="text-green-400 text-xs md:text-sm">+8% from last week</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Stickiness Ratio</p>
                      <p className="text-xl md:text-2xl font-bold text-white">41%</p>
                      <p className="text-green-400 text-xs md:text-sm">+3% from last month</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Avg Session Duration</p>
                      <p className="text-xl md:text-2xl font-bold text-white">18m</p>
                      <p className="text-green-400 text-xs md:text-sm">+2m from last week</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-white font-medium text-sm md:text-base">Most Used Features</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Predictions</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-green-500" style={{ width: '75%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">75%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Watchlist</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: '60%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">60%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Signals</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-yellow-500" style={{ width: '45%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">45%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-xs md:text-sm">Charts</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 md:w-32 h-2 bg-slate-700 rounded overflow-hidden">
                            <div className="h-full bg-purple-500" style={{ width: '30%' }}></div>
                          </div>
                          <span className="text-white text-xs md:text-sm">30%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <h4 className="text-white font-medium text-sm md:text-base mb-3">Peak Activity Time</h4>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-slate-400 text-xs md:text-sm">Most active: <span className="text-white font-medium text-sm md:text-base">Tuesday 2-4 PM</span></p>
                      <p className="text-slate-400 text-xs md:text-sm">Peak hour: <span className="text-white font-medium text-sm md:text-base">3 PM (UTC)</span></p>
                    </div>
                  </div>
                  
                  <button className="mt-4 w-full md:w-auto px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
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
