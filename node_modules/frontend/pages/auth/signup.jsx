/**
 * Sign Up Page
 */

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Registration failed');
        setLoading(false);
        return;
      }

      // Registration successful - redirect to login page
      setError('');
      setSuccess('Registration successful! Redirecting to login...');
      setLoading(false);
      
      // Show success message and redirect
      setTimeout(() => {
        router.push('/auth/login');
      }, 2000);
    } catch (err) {
      console.error('Signup error:', err);
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
              background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              cursor: 'pointer',
              marginBottom: '1rem'
            }}>
              📈 Market Predictor Pro
            </div>
          </Link>
          <h1 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '0.5rem' }}>Create Account</h1>
          <p style={{ color: '#D1D5DB' }}>Sign up to start predicting market trends</p>
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

        {/* Success Message */}
        {success && (
          <div style={{
            backgroundColor: 'rgba(16, 185, 129, 0.2)',
            border: '1px solid #10B981',
            color: '#6EE7B7',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1.5rem'
          }}>
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Username */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', fontSize: '0.95rem' }}>
              Username
            </label>
            <input
              type="text"
              placeholder="Choose a username"
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
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#2D3748';
                e.target.style.boxShadow = 'none';
              }}
              disabled={loading}
              required
              minLength={3}
            />
          </div>

          {/* Email */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', fontSize: '0.95rem' }}>
              Email
            </label>
            <input
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
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
              Password
            </label>
            <input
              type="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#2D3748';
                e.target.style.boxShadow = 'none';
              }}
              disabled={loading}
              required
              minLength={8}
            />
          </div>

          {/* Confirm Password */}
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', fontSize: '0.95rem' }}>
              Confirm Password
            </label>
            <input
              type="password"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
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
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#2D3748';
                e.target.style.boxShadow = 'none';
              }}
              disabled={loading}
              required
              minLength={8}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '0.75rem',
              backgroundColor: '#10B981',
              color: '#0F172A',
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
                e.target.style.backgroundColor = '#059669';
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 10px 25px rgba(16, 185, 129, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#10B981';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            {loading ? 'Creating account...' : 'Create Account'}
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

        {/* Sign In Link */}
        <p style={{ textAlign: 'center', color: '#D1D5DB', marginBottom: '1rem' }}>
          Already have an account?{' '}
          <Link href="/auth/login">
            <span style={{ color: '#3B82F6', fontWeight: '600', cursor: 'pointer' }}>
              Sign in
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
