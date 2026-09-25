'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { authAPI } from '@/lib/api';
import { 
  User, 
  Settings as SettingsIcon, 
  Bell, 
  Shield, 
  CreditCard, 
  Key,
  Globe,
  Moon,
  Sun,
  Save,
  Trash2
} from 'lucide-react';

export default function SettingsPage() {
  const { user, setUser, theme, setTheme } = useStore();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Profile settings
  const [profile, setProfile] = useState({
    first_name: user?.profile?.first_name || '',
    last_name: user?.profile?.last_name || '',
    bio: user?.profile?.bio || '',
    location: user?.profile?.location || '',
    website: user?.profile?.website || '',
  });

  // Notification settings
  const [notifications, setNotifications] = useState({
    email: user?.preferences?.notifications?.email || false,
    push: user?.preferences?.notifications?.push || false,
    price_alerts: user?.preferences?.notifications?.price_alerts || false,
    signal_alerts: user?.preferences?.notifications?.signal_alerts || false,
  });

  // General settings
  const [general, setGeneral] = useState({
    language: user?.preferences?.language || 'en',
    timezone: user?.preferences?.timezone || 'UTC',
    default_market: user?.preferences?.default_market || 'stock',
  });

  // API Keys
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyScopes, setNewKeyScopes] = useState(['read']);

  useEffect(() => {
    loadAPIKeys();
  }, []);

  const loadAPIKeys = async () => {
    try {
      const response = await authAPI.listAPIKeys();
      setApiKeys(response.api_keys || []);
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleProfileSave = async () => {
    setLoading(true);
    try {
      await authAPI.updateProfile(profile);
      showMessage('success', 'Profile updated successfully');
      
      // Update local user state
      if (user) {
        setUser({
          ...user,
          profile: { ...user.profile, ...profile }
        });
      }
    } catch (error) {
      showMessage('error', 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSave = async () => {
    setLoading(true);
    try {
      // In a real app, this would call an API endpoint
      showMessage('success', 'Notification preferences saved');
      
      if (user) {
        setUser({
          ...user,
          preferences: {
            ...user.preferences,
            notifications: notifications
          }
        });
      }
    } catch (error) {
      showMessage('error', 'Failed to save notification preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneralSave = async () => {
    setLoading(true);
    try {
      // In a real app, this would call an API endpoint
      showMessage('success', 'General settings saved');
      
      if (user) {
        setUser({
          ...user,
          preferences: {
            ...user.preferences,
            ...general
          }
        });
      }
    } catch (error) {
      showMessage('error', 'Failed to save general settings');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAPIKey = async () => {
    if (!newKeyName.trim()) return;
    
    setLoading(true);
    try {
      const newKey = await authAPI.createAPIKey(newKeyName, newKeyScopes);
      setApiKeys([...apiKeys, newKey]);
      setShowApiKeyModal(false);
      setNewKeyName('');
      setNewKeyScopes(['read']);
      showMessage('success', 'API key created successfully');
    } catch (error) {
      showMessage('error', 'Failed to create API key');
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeAPIKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) return;
    
    setLoading(true);
    try {
      await authAPI.revokeAPIKey(keyId);
      setApiKeys(apiKeys.filter(key => key.key_id !== keyId));
      showMessage('success', 'API key revoked successfully');
    } catch (error) {
      showMessage('error', 'Failed to revoke API key');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-slate-400">Manage your account preferences and settings</p>
      </div>

      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-600/20 border border-green-500' : 'bg-red-600/20 border border-red-500'
        }`}>
          <p className={`text-sm ${message.type === 'success' ? 'text-green-400' : 'text-red-400'}`}>
            {message.text}
          </p>
        </div>
      )}

      <div className="space-y-6">
        {/* Profile Settings */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <User className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Profile Settings</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">First Name</label>
              <input
                type="text"
                value={profile.first_name}
                onChange={(e) => setProfile({ ...profile, first_name: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Last Name</label>
              <input
                type="text"
                value={profile.last_name}
                onChange={(e) => setProfile({ ...profile, last_name: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-300 mb-2">Bio</label>
              <textarea
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Location</label>
              <input
                type="text"
                value={profile.location}
                onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Website</label>
              <input
                type="url"
                value={profile.website}
                onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
