# 🚀 Deployment Guide - Admin Access & Landing Page Fix

## Issues Fixed

✅ **Admin Page Access Denied** → Now properly checks JWT token + user role
✅ **Sign-In on Home Page** → Now shows stunning landing page first
✅ **Role Not Saved** → Now saves user role to localStorage
✅ **Admin Route Protection** → Added middleware for role-based access control

---

## File Structure

```
frontend/
├── pages/
│   ├── index.jsx              ← STUNNING LANDING PAGE (NEW!)
│   ├── admin.jsx              ← FIXED ADMIN DASHBOARD
│   ├── dashboard.jsx          ← User dashboard
│   └── auth/
│       ├── login.jsx          ← FIXED LOGIN (saves role)
│       └── signup.jsx         ← Sign up page
├── middleware.ts              ← ROLE-BASED ACCESS CONTROL (NEW!)
└── lib/AuthContext.jsx        ← Auth state management

backend/
├── routes/
│   └── auth_fixed.py          ← FIXED AUTH ENDPOINTS (NEW!)
└── ... other routes
```

---

## Step-by-Step Deployment

### 1. Update Backend (Python/FastAPI)

**File:** `backend/routes/auth_fixed.py`

```bash
# Copy to your existing backend
cp backend/routes/auth_fixed.py your-project/backend/routes/auth.py

# Or merge the endpoints into your existing auth routes
```

**Key Changes in Backend:**

```python
# ✅ Include role in JWT token
def create_access_token(data: dict):
    to_encode = {
        "sub": user["username"],
        "user_id": user["id"],
        "role": user["role"],  # IMPORTANT!
        "email": user["email"]
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Return user role in login response
@router.post("/login")
async def login(credentials: LoginRequest):
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]  # CRITICAL!
        }
    }

# ✅ Test admin login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response should include: "role": "admin"
```

**Update your `/api/auth/login` endpoint to:**

```python
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "admin_001",
    "username": "admin",
    "email": "admin@marketpredictor.com",
    "role": "admin"  # ← THIS IS CRITICAL!
  }
}
```

---

### 2. Update Frontend (Next.js)

**Step 1: Replace Pages**

```bash
# 1. Replace landing page
cp frontend/pages/index.jsx your-project/pages/index.jsx

# 2. Replace login page
cp frontend/pages/auth/login.jsx your-project/pages/auth/login.jsx

# 3. Replace admin page
cp frontend/pages/admin.jsx your-project/pages/admin.jsx
```

**Step 2: Add Middleware**

```bash
# Add to your Next.js project (create if doesn't exist)
cp frontend/middleware.ts your-project/middleware.ts
```

**Step 3: Update `next.config.js`**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Ensure middleware runs
  experimental: {
    // If you're using Next.js 12 or below
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Redirect www to non-www
  async redirects() {
    return [];
  },
};

module.exports = nextConfig;
```

**Step 4: Update Login Handler**

The login page now properly saves the role:

```javascript
// frontend/pages/auth/login.jsx
const handleSubmit = async (e) => {
  // ... login logic
  
  // ✅ CRITICAL: Save role!
  localStorage.setItem('auth-token', data.access_token);
  localStorage.setItem('user-role', data.user.role);  // ← SAVE ROLE!
  localStorage.setItem('user-data', JSON.stringify(data.user));

  // Redirect based on role
  if (data.user.role === 'admin' || data.user.role === 'superuser') {
    router.push('/admin');  // Admin dashboard
  } else {
    router.push('/dashboard');  // User dashboard
  }
};
```

---

### 3. Test the Setup

**Test 1: Landing Page**

```bash
# Open your app
http://localhost:3000

# ✅ Should show stunning landing page
# ✅ Should show "Sign In" & "Start Free Trial" buttons
# ✅ Should NOT redirect to login
```

**Test 2: Admin Login**

```bash
# Click "Sign In"
# Username: admin
# Password: admin123

# ✅ Should show admin dashboard at /admin
# ✅ Should see all admin tabs (Users, Subscriptions, Analytics, etc.)
```

**Test 3: Regular User Login**

```bash
# Click "Sign In"
# Username: demo
# Password: demo123

# ✅ Should redirect to /dashboard
# ✅ Should NOT have access to /admin
```

**Test 4: Admin Route Protection**

```bash
# Try to access /admin without login
# ✅ Should redirect to /auth/login

# Login as demo user
# Try to access /admin
# ✅ Should redirect to /dashboard
```

---

## Backend Setup on Railway

### 1. Deploy Python Backend

```bash
# Your backend is already deployed
# Ensure these endpoints exist:
GET  /api/auth/verify-token
POST /api/auth/login
POST /api/auth/register
POST /api/auth/promote-admin/{username}
```

### 2. Test Backend from Frontend

Update the API URL in login page:

```javascript
// frontend/pages/auth/login.jsx

// Change this:
const response = await fetch('http://localhost:8000/api/auth/login', {

// To this (your Railway URL):
const response = await fetch('https://your-railway-app.up.railway.app/api/auth/login', {
```

Or set environment variable:

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

### 3. Add CORS Headers

In your FastAPI backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Deployment Checklist

### Frontend (Vercel)

- [ ] Copy `frontend/pages/index.jsx` → `pages/index.jsx`
- [ ] Copy `frontend/pages/admin.jsx` → `pages/admin.jsx`
- [ ] Copy `frontend/pages/auth/login.jsx` → `pages/auth/login.jsx`
- [ ] Copy `frontend/middleware.ts` → `middleware.ts`
- [ ] Update `NEXT_PUBLIC_API_URL` environment variable
- [ ] Deploy to Vercel

### Backend (Railway)

- [ ] Update auth routes to return user role in login response
- [ ] Add CORS middleware for Vercel domain
- [ ] Ensure admin user exists:
  ```python
  # In your database or seed file
  admin_user = {
      "username": "admin",
      "email": "admin@marketpredictor.com",
      "password": "hashed_password",
      "role": "admin"  # ← MUST BE "admin"
  }
  ```
- [ ] Deploy to Railway

---

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=https://your-railway-api.up.railway.app
NEXT_PUBLIC_APP_URL=https://your-vercel-app.vercel.app
```

### Backend (.env)

```env
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
```

---

## Troubleshooting

### Issue: Admin page still shows "Access Denied"

**Solution:**
1. Check if JWT token includes `role` field:
   ```bash
   # Decode token at jwt.io
   # Look for "role": "admin"
   ```

2. Check localStorage:
   ```javascript
   console.log(localStorage.getItem('user-role'))
   // Should print: "admin"
   ```

3. Verify backend returns role:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}' | jq .user.role
   # Should return: "admin"
   ```

### Issue: Landing page still shows login

**Solution:**
1. Clear browser cache: `Ctrl+Shift+Delete`
2. Delete Next.js cache: `rm -rf .next`
3. Rebuild: `npm run dev`

### Issue: CORS errors on login

**Solution:**
1. Add CORS headers to your FastAPI backend:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-vercel-url"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Update API URL in frontend:
   ```javascript
   const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
   const response = await fetch(`${API_URL}/api/auth/login`, ...)
   ```

---

## Production URLs

Once deployed:

- **Landing Page:** https://your-app.vercel.app/
- **Login:** https://your-app.vercel.app/auth/login
- **Admin Dashboard:** https://your-app.vercel.app/admin
- **User Dashboard:** https://your-app.vercel.app/dashboard

---

## Key Files Changed

| File | Change | Status |
|------|--------|--------|
| `pages/index.jsx` | Stunning landing page | ✅ NEW |
| `pages/admin.jsx` | Fixed admin dashboard | ✅ UPDATED |
| `pages/auth/login.jsx` | Saves role to localStorage | ✅ UPDATED |
| `middleware.ts` | Role-based access control | ✅ NEW |
| `backend/auth_fixed.py` | Returns role in login response | ✅ UPDATED |

---

## Support

If issues persist:

1. Check backend logs on Railway:
   ```bash
   # View recent logs
   railway logs
   ```

2. Check frontend errors:
   ```javascript
   // Open browser console (F12)
   // Look for network errors in Network tab
   ```

3. Test API directly:
   ```bash
   curl http://your-railway-api.up.railway.app/api/auth/login \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

---

**Deployment Status: ✅ READY**
