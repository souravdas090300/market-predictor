/**
 * Admin Login Page - Separate from regular user login
 * Only for admin/superuser authentication
 */

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function AdminLoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    // If already logged in as admin, redirect to admin dashboard
    const token = localStorage.getItem('auth-token');
    const userRole = localStorage.getItem('user-role');
    
    if (token && (userRole === 'admin' || userRole === 'superuser')) {
      router.push('/admin');
    }
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Call admin login endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Admin login failed');
        setLoading(false);
        return;
      }

      // Save admin tokens and user data
      localStorage.setItem('auth-token', data.access_token);
      localStorage.setItem('user-role', 'admin'); // Admin role
      localStorage.setItem('user-data', JSON.stringify({
        id: data.user_id,
        username: formData.username,
        role: 'admin',
        is_superuser: true
      }));

      // Redirect to admin dashboard
      router.push('/admin');
    } catch (err) {
      console.error('Admin login error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      backgroundColor: '#0F172A',
      color: '#F9FAFB',
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '2rem'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '450px',
        backgroundColor: 'rgba(31, 41, 55, 0.8)',
        border: '1px solid #2D3748',
        borderRadius: '12px',
        padding: '3rem',
        backdropFilter: 'blur(10px)'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Link href="/">
            <div style={{
              fontSize: '2rem',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #EF4444 0%, #F59E0B 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              cursor: 'pointer',
              marginBottom: '1rem'
            }}>
              🛡️ Admin Panel
            </div>
          </Link>
          <h1 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '0.5rem' }}>Admin Access</h1>
          <p style={{ color: '#D1D5DB' }}>Secure administrator login</p>
        </div>

        {/* Security Notice */}
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #EF4444',
          color: '#FCA5A5',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1.5rem',
          fontSize: '0.85rem'
        }}>
          <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>⚠️ Admin Access Only</div>
          <div>This login is restricted to administrators. Regular users should use the standard login page.</div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.2)',
            border: '1px solid #EF4444',
            color: '#FCA5A5',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1.5rem'
          }}>
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Username */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', fontSize: '0.95rem' }}>
              Admin Username
            </label>
            <input
              type="text"
              placeholder="Enter admin username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#1F2937',
                color: '#F9FAFB',
                border: '1px solid #2D3748',
                borderRadius: '8px',
                fontSize: '1rem',
                transition: 'all 0.3s ease'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#EF4444';
                e.target.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#2D3748';
                e.target.style.boxShadow = 'none';
              }}
              disabled={loading}
              required
            />
          </div>

          {/* Password */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', fontSize: '0.95rem' }}>
              Admin Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  paddingRight: '2.5rem',
                  backgroundColor: '#1F2937',
                  color: '#F9FAFB',
                  border: '1px solid #2D3748',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  transition: 'all 0.3s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#EF4444';
                  e.target.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#2D3748';
                  e.target.style.boxShadow = 'none';
                }}
                disabled={loading}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: '#D1D5DB',
                  cursor: 'pointer',
                  fontSize: '1.2rem'
                }}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '0.75rem',
              backgroundColor: '#EF4444',
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '700',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.backgroundColor = '#DC2626';
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 10px 25px rgba(239, 68, 68, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#EF4444';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            {loading ? 'Authenticating...' : 'Admin Login'}
          </button>
        </form>

        {/* Divider */}
        <div style={{ position: 'relative', margin: '2rem 0' }}>
          <div style={{ height: '1px', backgroundColor: '#2D3748' }} />
          <div style={{
            position: 'absolute',
            left: '50%',
            top: '-10px',
            transform: 'translateX(-50%)',
            backgroundColor: '#0F172A',
            padding: '0 0.5rem',
            color: '#D1D5DB',
            fontSize: '0.85rem'
          }}>
            OR
          </div>
        </div>

        {/* Regular User Login Link */}
        <p style={{ textAlign: 'center', color: '#D1D5DB', marginBottom: '1rem' }}>
          Not an admin?{' '}
          <Link href="/auth/login">
            <span style={{ color: '#3B82F6', fontWeight: '600', cursor: 'pointer' }}>
              User Login
            </span>
          </Link>
        </p>

        {/* Back to Home */}
        <Link href="/">
          <div style={{
            textAlign: 'center',
            color: '#6B7280',
            fontSize: '0.9rem',
            cursor: 'pointer',
            transition: 'color 0.3s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#D1D5DB'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}
          >
            ← Back to home
          </div>
        </Link>
      </div>
    </div>
  );
}