# Google OAuth Setup Guide

This guide will help you configure Google Sign-in and Sign-up for local testing and production.

---

## 📋 Current Status

### ✅ What's Already Done:
- Google Cloud project created: `market-predictor`
- OAuth 2.0 Client ID created
- Publishing status: Testing
- User type: External
- Backend has OAuth user management support in `app/auth/__init__.py`

### ❌ What Needs to Be Done:
- Add Google Client ID and Client Secret to environment variables
- Implement Google OAuth flow in backend API
- Add Google Sign-in buttons to frontend
- Configure Google Cloud with local redirect URIs
- Install required Python packages

---

## 🔧 Step 1: Configure Google Cloud Console

### **Add Local Redirect URIs**

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Select your project: `market-predictor`

2. **Edit OAuth 2.0 Client ID**
   - Click on your OAuth 2.0 Client ID
   - Scroll to "Authorized redirect URIs"

3. **Add Local Development URIs**
   - Click "Add URI"
   - Add: `http://localhost:3000/auth/callback/google`
   - Add: `http://127.0.0.1:3000/auth/callback/google`
   - Add: `http://localhost:8000/api/auth/oauth/callback` (for backend testing)
   - Click "Save"

4. **Copy Credentials**
   - Copy the **Client ID**
   - Copy the **Client Secret**
   - Keep these safe - you'll need them in the next step

---

## 🔧 Step 2: Add Environment Variables

### **For Local Development (.env.dev)**

Add these variables to your `.env.dev` file:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google
```

Replace:
- `your-google-client-id-here` with your actual Google Client ID
- `your-google-client-secret-here` with your actual Google Client Secret

### **For Production (Railway)**

Add these variables to Railway dashboard:

```bash
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=https://market-predictor-eta.vercel.app/auth/callback/google
```

### **For Production (Vercel)**

Add these variables to Vercel dashboard:

```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-here
NEXT_PUBLIC_API_URL=https://your-railway-app-url.railway.app
```

---

## 🔧 Step 3: Install Required Python Packages

```bash
cd C:\Users\dasau\market-predictor
pip install google-auth google-auth-oauthlib google-auth-httplib2 requests
```

---

## 🔧 Step 4: Implement Google OAuth in Backend

### **Create OAuth Configuration**

Create a new file `app/oauth/google.py`:

```python
"""Google OAuth implementation."""
import os
import json
import requests
from typing import Dict, Any, Optional
from ..core import config

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google")

# Google OAuth Endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_auth_url(state: Optional[str] = None) -> str:
    """Generate Google OAuth authorization URL."""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    if state:
        params["state"] = state
    
    from urllib.parse import urlencode
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token."""
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()


def get_google_user_info(access_token: str) -> Dict[str, Any]:
    """Get user information from Google using access token."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    response.raise_for_status()
    return response.json()
```

### **Update Backend API Endpoints**

Update `app/api/__init__.py` to implement the OAuth endpoints (around lines 3958-3980):

```python
from app.oauth.google import get_google_auth_url, exchange_code_for_token, get_google_user_info


@app.get("/api/auth/oauth/google")
@limiter.limit("20/minute")
def google_oauth_redirect(request: Request):
    """Redirect to Google OAuth."""
    from urllib.parse import urlencode
    import secrets
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session (you'll need session middleware)
    # For now, we'll skip session storage and use query parameter
    
    auth_url = get_google_auth_url(state=state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@app.post("/api/auth/oauth/callback")
@limiter.limit("10/minute")
def oauth_callback(request: Request, body: OAuthCallbackRequest):
    """Handle OAuth callback from Google."""
    # Verify provider
    if body.provider != "google":
        raise HTTPException(
            status_code=400,
            detail="Only Google OAuth is currently supported"
        )
    
    try:
        # Exchange code for token
        token_data = exchange_code_for_token(body.code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Failed to obtain access token from Google"
            )
        
        # Get user info from Google
        user_info = get_google_user_info(access_token)
        
        # Extract user data
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        given_name = user_info.get("given_name")
        family_name = user_info.get("family_name")
        picture = user_info.get("picture")
        
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email is required from Google OAuth"
            )
        
        # Check if user exists by OAuth
        existing_user = user_manager.find_user_by_oauth("google", google_id)
        
        if existing_user:
            # User exists, log them in
            # Generate JWT token
            from datetime import timedelta
            from jose import jwt
            
            access_token_expires = timedelta(minutes=60)
            access_token = jwt.encode(
                {
                    "sub": existing_user["user_id"],
                    "username": existing_user["username"],
                    "role": existing_user["roles"][0] if existing_user["roles"] else "user",
                    "exp": datetime.now(timezone.utc) + access_token_expires
                },
                config.SECRET_KEY,
                algorithm="HS256"
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "user_id": existing_user["user_id"],
                    "username": existing_user["username"],
                    "email": existing_user["email"],
                    "role": existing_user["roles"][0] if existing_user["roles"] else "user",
                    "avatar_url": existing_user.get("profile", {}).get("avatar_url")
                }
            }
        else:
            # Create new user from OAuth
            profile_data = {
                "first_name": given_name,
                "last_name": family_name,
                "avatar_url": picture,
                "location": None
            }
            
            new_user = user_manager.create_user_from_oauth(
                provider="google",
                provider_user_id=google_id,
                email=email,
                profile_data=profile_data
            )
            
            # Generate JWT token
            from datetime import timedelta
            from jose import jwt
            
            access_token_expires = timedelta(minutes=60)
            access_token = jwt.encode(
                {
                    "sub": new_user["user_id"],
                    "username": new_user["username"],
                    "role": new_user["roles"][0] if new_user["roles"] else "user",
                    "exp": datetime.now(timezone.utc) + access_token_expires
                },
                config.SECRET_KEY,
                algorithm="HS256"
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "user_id": new_user["user_id"],
                    "username": new_user["username"],
                    "email": new_user["email"],
                    "role": new_user["roles"][0] if new_user["roles"] else "user",
                    "avatar_url": new_user.get("profile", {}).get("avatar_url")
                }
            }
            
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Google: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth error: {str(e)}"
        )
```

---

## 🔧 Step 5: Add Google Sign-in Button to Frontend

### **Update Login Page (frontend/pages/auth/login.jsx)**

Add Google Sign-in button after the form (around line 248):

```jsx
{/* Google Sign-in Button */}
<button
  type="button"
  onClick={handleGoogleSignIn}
  disabled={loading}
  style={{
    width: '100%',
    padding: '0.75rem',
    backgroundColor: '#FFFFFF',
    color: '#0F172A',
    border: '1px solid #D1D5DB',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: loading ? 'not-allowed' : 'pointer',
    opacity: loading ? 0.6 : 1,
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem'
  }}
  onMouseEnter={(e) => {
    if (!loading) {
      e.target.style.backgroundColor = '#F3F4F6';
      e.target.style.transform = 'translateY(-2px)';
    }
  }}
  onMouseLeave={(e) => {
    e.target.style.backgroundColor = '#FFFFFF';
    e.target.style.transform = 'translateY(0)';
  }}
>
  <svg width="20" height="20" viewBox="0 0 24 24">
    <path
      fill="#4285F4"
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
    />
    <path
      fill="#34A853"
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
    />
    <path
      fill="#FBBC05"
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
    />
    <path
      fill="#EA4335"
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
    />
  </svg>
  Sign in with Google
</button>
```

Add the handler function before the return statement:

```jsx
const handleGoogleSignIn = async () => {
  setLoading(true);
  setError('');

  try {
    // Get Google OAuth URL from backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/oauth/google`);
    const data = await response.json();

    if (!response.ok) {
      setError('Failed to initialize Google Sign-in');
      setLoading(false);
      return;
    }

    // Redirect to Google OAuth
    window.location.href = data.auth_url;
  } catch (err) {
    console.error('Google Sign-in error:', err);
    setError('An error occurred. Please try again.');
    setLoading(false);
  }
};
```

### **Update Signup Page (frontend/pages/auth/signup.jsx)**

Add the same Google Sign-in button to the signup page.

---

## 🔧 Step 6: Create OAuth Callback Page

Create a new file `frontend/pages/auth/callback/google.jsx`:

```jsx
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
```

---

## 🚀 Step 7: Test Locally

### **Start Backend Server**
```bash
cd C:\Users\dasau\market-predictor
python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### **Start Frontend Server**
```bash
cd C:\Users\dasau\market-predictor\frontend
npm run dev
```

### **Test Google Sign-in**
1. Open browser to: `http://localhost:3000/auth/login`
2. Click "Sign in with Google"
3. You should be redirected to Google's consent screen
4. Sign in with your Google account
5. You should be redirected back to your app
6. You should be logged in and redirected to the dashboard

---

## 📋 Step 8: Update Google Cloud for Production

### **Add Production Redirect URIs**

1. Go to Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. Add production redirect URIs:
   - `https://market-predictor-eta.vercel.app/auth/callback/google`
4. Click "Save"

---

## 🔒 Security Notes

### **Important Security Considerations:**

1. **Client Secret Security**
   - Never commit `GOOGLE_CLIENT_SECRET` to Git
   - Use environment variables only
   - Rotate secrets periodically

2. **State Parameter**
   - Implement proper CSRF protection using state parameter
   - Store state in session and verify on callback

3. **HTTPS in Production**
   - Always use HTTPS in production
   - Google requires HTTPS for OAuth redirect URIs

4. **Email Verification**
   - Google OAuth emails are pre-verified
   - Your app should mark these users as verified

5. **Rate Limiting**
   - Implement rate limiting on OAuth endpoints
   - Prevent OAuth abuse

---

## 🐛 Troubleshooting

### **Common Issues:**

1. **"redirect_uri_mismatch" Error**
   - Check that redirect URI in Google Cloud matches exactly
   - Include trailing slashes if needed
   - Check http vs https

2. **"invalid_client" Error**
   - Verify Client ID and Client Secret are correct
   - Check environment variables are loaded

3. **"access_denied" Error**
   - User denied consent
   - Check OAuth consent screen configuration
   - Ensure user is in test users list (for testing mode)

4. **"origin_mismatch" Error**
   - Check CORS configuration
   - Verify allowed origins in Railway/Vercel

---

## ✅ Summary

### **What You Need to Do:**

1. ✅ Add local redirect URIs to Google Cloud Console
2. ✅ Copy Google Client ID and Client Secret
3. ✅ Add environment variables to `.env.dev`
4. ✅ Install required Python packages
5. ✅ Create `app/oauth/google.py`
6. ✅ Update backend OAuth endpoints in `app/api/__init__.py`
7. ✅ Add Google Sign-in button to frontend
8. ✅ Create OAuth callback page
9. ✅ Test locally
10. ✅ Add production redirect URIs to Google Cloud
11. ✅ Add environment variables to Railway/Vercel

### **Files to Create/Modify:**

- `app/oauth/google.py` (new)
- `app/api/__init__.py` (modify OAuth endpoints)
- `frontend/pages/auth/login.jsx` (add Google button)
- `frontend/pages/auth/signup.jsx` (add Google button)
- `frontend/pages/auth/callback/google.jsx` (new)
- `.env.dev` (add Google credentials)

---

## 📖 Resources

- Google OAuth 2.0 Documentation: https://developers.google.com/identity/protocols/oauth2
- Google Cloud Console: https://console.cloud.google.com
- NextAuth.js (Alternative Approach): https://next-auth.js.org

---

This guide provides everything you need to implement Google Sign-in for both local testing and production! 🚀
