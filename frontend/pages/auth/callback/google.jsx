/**
 * Google OAuth Callback Page
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function GoogleCallbackPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const { code, state } = router.query;

      if (!code) {
        setError('No authorization code received');
        setLoading(false);
        return;
      }

      try {
        // Send code to backend
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/oauth/callback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            provider: 'google',
            code: code,
            redirect_uri: window.location.origin + '/auth/callback/google'
          })
        });

        const data = await response.json();

        if (!response.ok) {
          setError(data.detail || 'OAuth callback failed');
          setLoading(false);
          return;
        }

        // Save the token and user data
        localStorage.setItem('auth-token', data.access_token);
        localStorage.setItem('user-role', data.user.role);
        localStorage.setItem('user-data', JSON.stringify(data.user));

        // Redirect to dashboard
        router.push('/dashboard');
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError('An error occurred. Please try again.');
        setLoading(false);
      }
    };

    if (router.query.code) {
      handleCallback();
    }
  }, [router.query, router]);

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
        backdropFilter: 'blur(10px)',
        textAlign: 'center'
      }}>
        {loading ? (
          <>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔄</div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem' }}>
              Signing in with Google...
            </h2>
            <p style={{ color: '#D1D5DB' }}>
              Please wait while we complete the authentication.
            </p>
          </>
        ) : error ? (
          <>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem' }}>
              Authentication Failed
            </h2>
            <p style={{ color: '#EF4444', marginBottom: '1.5rem' }}>
              {error}
            </p>
            <button
              onClick={() => router.push('/auth/login')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#3B82F6',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Back to Login
            </button>
          </>
        ) : null}
      </div>
    </div>
  );
}
