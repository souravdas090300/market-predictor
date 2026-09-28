/**
 * User Dashboard
 * Protected route for authenticated users
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('auth-token');
    const userData = localStorage.getItem('user-data');

    if (!token) {
      router.push('/auth/login');
      return;
    }

    try {
      setUser(JSON.parse(userData || '{}'));
    } catch (e) {
      console.error('Failed to parse user data', e);
    }

    setLoading(false);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('auth-token');
    localStorage.removeItem('user-role');
    localStorage.removeItem('user-data');
    router.push('/');
  };

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
        Loading dashboard...
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
        <h1 style={{ fontSize: '1.8rem', fontWeight: '700' }}>📈 Market Dashboard</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontWeight: '600' }}>{user.username || user.email}</div>
            <div style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
              {localStorage.getItem('user-role')}
            </div>
          </div>
          <button
            onClick={handleLogout}
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
      <div style={{ padding: '2rem' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '2rem' }}>
            Welcome back, {user.username || 'Trader'}!
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
            <StatCard number="12" label="Watchlist Items" color="#3B82F6" />
            <StatCard number="5" label="Active Alerts" color="#10B981" />
            <StatCard number="89%" label="Accuracy" color="#FBBF24" />
            <StatCard number="$12,450" label="Portfolio Value" color="#10B981" />
          </div>

          <div style={{ border: '1px solid #2D3748', padding: '2rem', borderRadius: '8px', textAlign: 'center', color: '#D1D5DB' }}>
            <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>📊 Market Analysis Tools</p>
            <p>Your trading dashboard features will appear here.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ number, label, color }) {
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
      <div style={{ color: '#D1D5DB', fontSize: '0.9rem' }}>
        {label}
      </div>
    </div>
  );
}
