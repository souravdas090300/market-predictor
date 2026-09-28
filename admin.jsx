/**
 * Admin Dashboard - Protected Route
 * Only accessible by users with admin or superuser role
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function AdminDashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    const token = localStorage.getItem('auth-token');
    const userRole = localStorage.getItem('user-role');
    const userData = localStorage.getItem('user-data');

    if (!token) {
      router.push('/auth/login');
      return;
    }

    // Check if user is admin
    if (userRole !== 'admin' && userRole !== 'superuser') {
      router.push('/dashboard');
      return;
    }

    try {
      setUser(JSON.parse(userData || '{}'));
    } catch (e) {
      console.error('Failed to parse user data', e);
    }

    setLoading(false);
  }, [router]);

  if (loading) {
    return (
      <div style={{
        backgroundColor: '#0F172A',
        color: '#F9FAFB',
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '1.2rem'
      }}>
        Loading admin panel...
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div style={{ backgroundColor: '#0F172A', color: '#F9FAFB', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{
        borderBottom: '1px solid #2D3748',
        padding: '1.5rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        backdropFilter: 'blur(10px)'
      }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: '700' }}>🛠️ Admin Dashboard</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontWeight: '600' }}>{user.username || user.email}</div>
            <div style={{ fontSize: '0.85rem', color: '#D1D5DB', textTransform: 'uppercase' }}>
              {localStorage.getItem('user-role')}
            </div>
          </div>
          <button
            onClick={() => {
              localStorage.removeItem('auth-token');
              localStorage.removeItem('user-role');
              localStorage.removeItem('user-data');
              router.push('/auth/login');
            }}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#EF4444',
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ display: 'flex', height: 'calc(100vh - 80px)' }}>
        {/* Sidebar */}
        <div style={{
          width: '250px',
          borderRight: '1px solid #2D3748',
          padding: '1.5rem 0',
          backgroundColor: 'rgba(31, 41, 55, 0.3)'
        }}>
          {[
            { id: 'dashboard', label: 'Dashboard', icon: '📊' },
            { id: 'users', label: 'Users', icon: '👥' },
            { id: 'subscriptions', label: 'Subscriptions', icon: '💳' },
            { id: 'analytics', label: 'Analytics', icon: '📈' },
            { id: 'settings', label: 'Settings', icon: '⚙️' },
            { id: 'audit', label: 'Audit Logs', icon: '🔒' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                width: '100%',
                padding: '1rem 1.5rem',
                backgroundColor: activeTab === tab.id ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                color: activeTab === tab.id ? '#3B82F6' : '#D1D5DB',
                border: 'none',
                borderLeft: activeTab === tab.id ? '3px solid #3B82F6' : '3px solid transparent',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontSize: '1rem'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  e.target.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span style={{ marginRight: '0.5rem' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div style={{ flex: 1, overflow: 'auto', padding: '2rem' }}>
          {activeTab === 'dashboard' && <DashboardTab />}
          {activeTab === 'users' && <UsersTab />}
          {activeTab === 'subscriptions' && <SubscriptionsTab />}
          {activeTab === 'analytics' && <AnalyticsTab />}
          {activeTab === 'settings' && <SettingsTab />}
          {activeTab === 'audit' && <AuditLogsTab />}
        </div>
      </div>
    </div>
  );
}

function DashboardTab() {
  return (
    <div>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '2rem' }}>Admin Overview</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <StatCard number="2,547" label="Total Users" trend="+12%" color="#10B981" />
        <StatCard number="$48.5K" label="Monthly Revenue" trend="+23%" color="#3B82F6" />
        <StatCard number="94.2%" label="Uptime" trend="-0.8%" color="#FBBF24" />
        <StatCard number="1,249" label="Active Sessions" trend="+5%" color="#10B981" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div style={{ border: '1px solid #2D3748', padding: '1.5rem', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Recent Activity</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <ActivityItem timestamp="2 hours ago" action="User registered" details="john@example.com" />
            <ActivityItem timestamp="5 hours ago" action="Payment processed" details="$99.00" />
            <ActivityItem timestamp="1 day ago" action="Subscription upgraded" details="john → Professional" />
          </div>
        </div>

        <div style={{ border: '1px solid #2D3748', padding: '1.5rem', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>System Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <StatusItem label="API Health" status="healthy" />
            <StatusItem label="Database" status="healthy" />
            <StatusItem label="Cache" status="warning" />
            <StatusItem label="Backups" status="healthy" />
          </div>
        </div>
      </div>
    </div>
  );
}

function UsersTab() {
  return (
    <div>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '2rem' }}>User Management</h2>

      <div style={{ border: '1px solid #2D3748', borderRadius: '8px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #2D3748', backgroundColor: 'rgba(45, 55, 72, 0.5)' }}>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Username</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Email</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Status</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Joined</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {[
              { username: 'john_trader', email: 'john@example.com', status: 'active', joined: '2024-01-15' },
              { username: 'sarah_invest', email: 'sarah@example.com', status: 'active', joined: '2024-02-20' },
              { username: 'mike_dev', email: 'mike@example.com', status: 'inactive', joined: '2024-03-10' }
            ].map((user, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #2D3748' }}>
                <td style={{ padding: '1rem' }}>{user.username}</td>
                <td style={{ padding: '1rem' }}>{user.email}</td>
                <td style={{ padding: '1rem' }}>
                  <span style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '4px',
                    backgroundColor: user.status === 'active' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                    color: user.status === 'active' ? '#10B981' : '#9CA3AF',
                    fontSize: '0.85rem',
                    fontWeight: '600'
                  }}>
                    {user.status}
                  </span>
                </td>
                <td style={{ padding: '1rem' }}>{user.joined}</td>
                <td style={{ padding: '1rem' }}>
                  <button style={{
                    padding: '0.25rem 0.75rem',
                    fontSize: '0.85rem',
                    backgroundColor: '#3B82F6',
                    color: '#F9FAFB',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginRight: '0.5rem'
                  }}>
                    View
                  </button>
                  <button style={{
                    padding: '0.25rem 0.75rem',
                    fontSize: '0.85rem',
                    backgroundColor: '#EF4444',
                    color: '#F9FAFB',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}>
                    Ban
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SubscriptionsTab() {
  return (
    <div>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '2rem' }}>Subscription Management</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <SubscriptionMetric title="Free Plan" count="1,247" color="#6B7280" />
        <SubscriptionMetric title="Professional" count="847" color="#3B82F6" />
        <SubscriptionMetric title="Enterprise" count="53" color="#10B981" />
        <SubscriptionMetric title="Churned" count="142" color="#EF4444" />
      </div>
    </div>
  );
}

function AnalyticsTab() {
  return (
    <div>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '2rem' }}>Platform Analytics</h2>
      <div style={{ border: '1px solid #2D3748', padding: '2rem', borderRadius: '8px', textAlign: 'center', color: '#D1D5DB' }}>
        📊 Analytics charts will be displayed here
      </div>
    </div>
  );
}

function SettingsTab() {
  return (
    <div>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '2rem' }}>System Settings</h2>

      <div style={{ maxWidth: '600px' }}>
        <div style={{ marginBottom: '2rem', border: '1px solid #2D3748', padding: '1.5rem', borderRadius: '8px' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            Maintenance Mode
          </label>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button style={{
              flex: 1,
              padding: '0.75rem',
              backgroundColor: 'rgba(16, 185, 129, 0.2)',
              color: '#10B981',
              border: '1px solid #10B981',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600'
            }}>
              Enable
            </button>
            <button style={{
              flex: 1,
              padding: '0.75rem',
              backgroundColor: 'transparent',
              color: '#D1D5DB',
              border: '1px solid #2D3748',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600'
            }}>
              Disable
            </button>
          </div>
        </div>

        <div style={{ border: '1px solid #2D3748', padding: '1.5rem', borderRadius: '8px' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            API Rate Limit (req/min)
          </label>
          <input type="number" defaultValue="100" style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#1F2937',
            color: '#F9FAFB',
            border: '1px solid #2D3748',
            borderRadius: '6px'
          }} />
        </div>
      </div>
    </div>
  );
}

function AuditLogsTab() {
  return (
    <div>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '2rem' }}>Audit Logs</h2>

      <div style={{ border: '1px solid #2D3748', borderRadius: '8px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #2D3748', backgroundColor: 'rgba(45, 55, 72, 0.5)' }}>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Timestamp</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Action</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>User</th>
              <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {[
              { timestamp: '2024-09-28 10:30', action: 'USER_BANNED', user: 'admin', details: 'Banned user: spam_account' },
              { timestamp: '2024-09-28 09:15', action: 'SUBSCRIPTION_UPGRADE', user: 'john_trader', details: 'Free → Professional' },
              { timestamp: '2024-09-28 08:45', action: 'SETTINGS_CHANGED', user: 'admin', details: 'Rate limit updated' }
            ].map((log, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #2D3748' }}>
                <td style={{ padding: '1rem' }}>{log.timestamp}</td>
                <td style={{ padding: '1rem' }}>
                  <span style={{ color: '#10B981', fontWeight: '600' }}>{log.action}</span>
                </td>
                <td style={{ padding: '1rem' }}>{log.user}</td>
                <td style={{ padding: '1rem', color: '#D1D5DB' }}>{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Helper Components
function StatCard({ number, label, trend, color }) {
  return (
    <div style={{
      border: '1px solid #2D3748',
      padding: '1.5rem',
      borderRadius: '8px',
      backgroundColor: 'rgba(45, 55, 72, 0.3)'
    }}>
      <div style={{ fontSize: '2rem', fontWeight: '700', color, marginBottom: '0.5rem' }}>
        {number}
      </div>
      <div style={{ color: '#D1D5DB', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
        {label}
      </div>
      <div style={{ color: trend.startsWith('+') ? '#10B981' : '#EF4444', fontSize: '0.85rem', fontWeight: '600' }}>
        {trend}
      </div>
    </div>
  );
}

function ActivityItem({ timestamp, action, details }) {
  return (
    <div style={{
      padding: '0.75rem',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderRadius: '4px',
      borderLeft: '3px solid #3B82F6'
    }}>
      <div style={{ fontWeight: '600', color: '#F9FAFB' }}>{action}</div>
      <div style={{ fontSize: '0.85rem', color: '#D1D5DB', marginTop: '0.25rem' }}>
        {details} • {timestamp}
      </div>
    </div>
  );
}

function StatusItem({ label, status }) {
  const statusColor = status === 'healthy' ? '#10B981' : status === 'warning' ? '#FBBF24' : '#EF4444';
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span>{label}</span>
      <div style={{
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        backgroundColor: statusColor,
        animation: status === 'healthy' ? 'none' : 'pulse 2s infinite'
      }} />
    </div>
  );
}

function SubscriptionMetric({ title, count, color }) {
  return (
    <div style={{
      border: '1px solid #2D3748',
      padding: '1.5rem',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '2rem', fontWeight: '700', color, marginBottom: '0.5rem' }}>
        {count}
      </div>
      <div style={{ color: '#D1D5DB' }}>{title}</div>
    </div>
  );
}
