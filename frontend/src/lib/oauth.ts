import { authAPI } from './api';

export class OAuthManager {
  private static readonly GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';
  private static readonly GITHUB_CLIENT_ID = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || '';
  private static readonly REDIRECT_URI = typeof window !== 'undefined' 
    ? `${window.location.origin}/auth/callback` 
    : 'http://localhost:3000/auth/callback';

  static initiateGoogleOAuth(): void {
    if (!this.GOOGLE_CLIENT_ID) {
      console.error('Google OAuth client ID not configured');
      return;
    }

    const scope = 'openid profile email';
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${this.GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(this.REDIRECT_URI)}&response_type=code&scope=${encodeURIComponent(scope)}`;
    
    window.location.href = authUrl;
  }

  static initiateGitHubOAuth(): void {
    if (!this.GITHUB_CLIENT_ID) {
      console.error('GitHub OAuth client ID not configured');
      return;
    }

    const scope = 'user:email';
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${this.GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(this.REDIRECT_URI)}&scope=${encodeURIComponent(scope)}`;
    
    window.location.href = authUrl;
  }

  static async handleOAuthCallback(provider: string, code: string): Promise<any> {
    try {
      const response = await authAPI.oauthCallback(provider, code, this.REDIRECT_URI);
      return response;
    } catch (error) {
      console.error('OAuth callback failed:', error);
      throw error;
    }
  }

  static isConfigured(provider: 'google' | 'github'): boolean {
    if (provider === 'google') {
      return !!this.GOOGLE_CLIENT_ID;
    }
    return !!this.GITHUB_CLIENT_ID;
  }
}

export default OAuthManager;
