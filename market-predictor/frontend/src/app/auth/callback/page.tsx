'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import OAuthManager from '@/lib/oauth';
import { useStore } from '@/store/useStore';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

export default function OAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser, setAuthTokens } = useStore();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const provider = searchParams.get('provider') || 'google'; // Default to google if not specified
      
      if (!code) {
        setStatus('error');
        setMessage('No authorization code received');
        setTimeout(() => router.push('/auth/login'), 3000);
        return;
      }

      try {
        const response = await OAuthManager.handleOAuthCallback(provider, code);
        
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          
          setAuthTokens(response.access_token, response.refresh_token);
          setUser(response.user);
          
          setStatus('success');
          setMessage('Successfully signed in!');
          setTimeout(() => router.push('/'), 1500);
        } else {
          throw new Error('No access token received');
        }
      } catch (error) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        setMessage('Authentication failed. Please try again.');
        setTimeout(() => router.push('/auth/login'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, router, setUser, setAuthTokens]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 text-center">
          {status === 'loading' && (
            <div className="space-y-4">
              <Loader2 className="w-16 h-16 text-green-500 mx-auto animate-spin" />
              <h2 className="text-xl font-semibold text-white">Authenticating...</h2>
              <p className="text-slate-400">Please wait while we complete the sign-in process</p>
            </div>
          )}

          {status === 'success' && (
            <div className="space-y-4">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              <h2 className="text-xl font-semibold text-white">Success!</h2>
              <p className="text-slate-400">{message}</p>
              <p className="text-slate-500 text-sm">Redirecting to dashboard...</p>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-4">
              <XCircle className="w-16 h-16 text-red-500 mx-auto" />
              <h2 className="text-xl font-semibold text-white">Authentication Failed</h2>
              <p className="text-slate-400">{message}</p>
              <p className="text-slate-500 text-sm">Redirecting to login page...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
