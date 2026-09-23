# Access Control and User Management Guide

## Overview

The Market Predictor application has a unified access control system:

- **Main Dashboard (Port 8000)**: Requires user authentication (regular users)
- **Admin Dashboard (Port 8000, /admin path)**: Requires superuser authentication only

## User Roles

### Regular User
- **Access**: Main dashboard (port 8000)
- **Features**: Market predictions, technical indicators, material analysis, profile management
- **Subscription**: Free, Basic, Pro, or Enterprise plans
- **Creation**: Via registration form or OAuth

### Superuser (Admin)
- **Access**: Both main dashboard (port 8000) and admin dashboard (port 8001)
- **Features**: All user features PLUS admin functions
- **Capabilities**: 
  - Rate limiting control
  - System statistics
  - Batch prediction management
  - User management (grant/revoke superuser)
  - Maintenance mode
- **Creation**: Via script or by existing superuser

## Authentication Flow

### Main Dashboard (Port 8000)

1. **Unauthenticated Access**: Redirected to `/login.html`
2. **Login**: `POST /api/auth/login` with username/password
3. **Registration**: `POST /api/auth/register` to create account
4. **Protected Pages**: Check JWT token in localStorage
5. **Profile**: Access user profile and subscription

### Admin Dashboard (Port 8000, /admin)

1. **Unauthenticated Access**: Redirected to admin login form
2. **Login**: `POST /auth/login` on port 8001
3. **Superuser Check**: Verified against user's `is_superuser` flag
4. **Access Denied**: Non-superusers get 403 error
5. **Admin Functions**: Only accessible to superusers

## User Model Structure

```json
{
  "user_id": "unique_id",
  "username": "username",
  "email": "user@example.com",
  "hashed_password": "argon2_hash",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "is_active": true,
  "disabled": false,
  "roles": ["user"],
  "is_superuser": false,
  "preferences": {
    "default_horizon": 5,
    "confidence_threshold": 0.6,
    "auto_refresh": 0,
    "notifications_enabled": false,
    "sound_enabled": false
  },
  "subscription": {
    "plan": "free",
    "status": "active",
    "start_date": "2024-01-01T00:00:00",
    "expiry_date": null,
    "auto_renew": false
  },
  "profile": {
    "first_name": null,
    "last_name": null,
    "avatar_url": null,
    "bio": null,
    "location": null,
    "website": null
  },
  "oauth_providers": {},
  "email_verified": false,
  "last_login": null
}
```

## Setup Instructions

### 1. Create Superuser Account

Run the setup script to create the default superuser:

```bash
python scripts/setup_superuser.py
```

This creates:
- **Username**: `admin`
- **Email**: `admin@marketpredictor.local`
- **Password**: `admin123`
- **Role**: Superuser

⚠️ **IMPORTANT**: Change the default password before production!

### 2. Create Additional Superusers

#### Option A: Via Admin Dashboard
1. Login to admin dashboard: http://localhost:8000/admin
2. Go to "Users" tab
3. Enter username and click "Add Admin"
4. This grants superuser privileges to the user

#### Option B: Via Script
```bash
python scripts/create_superuser.py
```

#### Option C: Programmatically
```python
from app.auth import user_manager

# Create user
user_data = user_manager.create_user("john", "john@example.com", "password123")

# Set as superuser
user_manager.set_superuser(user_data["user_id"], True)
```

### 3. Revoke Superuser Access

#### Via Admin Dashboard
1. Login to admin dashboard
2. Go to "Users" tab
3. Click "Remove" next to username
4. This revokes superuser privileges

#### Programmatically
```python
from app.auth import user_manager

# Find user by username
user_id = None
for uid, user in user_manager.users.items():
    if user["username"] == "john":
        user_id = uid
        break

# Revoke superuser
if user_id:
    user_manager.set_superuser(user_id, False)
```

## Access URLs

### Main Dashboard (Port 8000)
- **Login**: http://localhost:8000/login.html
- **Register**: http://localhost:8000/register.html
- **Dashboard**: http://localhost:8000/index.html (requires authentication)
- **Profile**: http://localhost:8000/profile.html (requires authentication)

### Admin Dashboard (Port 8000, /admin)
- **Login**: http://localhost:8000/admin (shows login form)
- **Dashboard**: http://localhost:8000/admin (requires superuser authentication)

## Starting the Applications

### Single Server (Port 8000)
The main application now serves both the main dashboard and admin dashboard on a single port:

```bash
uvicorn app.api:app --reload --port 8000
```

This serves:
- **Main Dashboard**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/*

## Default Credentials

### Superuser (Admin)
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Both main and admin dashboards

### Demo User
- **Username**: `demo`
- **Password**: `demo123`
- **Access**: Main dashboard only (not superuser by default)

## Security Best Practices

### Production Deployment

1. **Change Default Passwords**
   ```bash
   # Change admin password immediately
   python scripts/create_superuser.py
   ```

2. **Remove Demo Account**
   ```python
   from app.auth import user_manager
   
   # Find and disable demo user
   for uid, user in user_manager.users.items():
       if user["username"] == "demo":
           user_manager.disable_user(uid)
   ```

3. **Use HTTPS**
   - Configure SSL certificates for both ports
   - Update CORS origins to use HTTPS

4. **Restrict Admin Access**
   - Use firewall rules to restrict port 8001
   - Implement IP whitelisting for admin access
   - Require VPN for admin dashboard access

5. **Enable Rate Limiting**
   - Keep rate limiting enabled on admin endpoints
   - Monitor rate limit violations
   - Adjust limits based on usage patterns

6. **Security Logging**
   - Monitor security logs in `logs/security.log`
   - Set up alerts for suspicious activity
   - Regularly review admin actions

## API Access Control

### Main Dashboard API (Port 8000)
- **Public Endpoints**: Login, register, health check
- **User Endpoints**: Require JWT authentication
- **Rate Limiting**: Applied to all endpoints

### Admin Dashboard API (Port 8000, /admin)
- **All Endpoints**: Require superuser authentication
- **Additional Check**: `is_superuser` flag verification
- **Higher Rate Limits**: Admin endpoints have separate rate limits

## Troubleshooting

### Cannot Access Main Dashboard
1. **Issue**: Redirected to login page
   - **Solution**: Login at `/login.html` or register new account

2. **Issue**: Token expired
   - **Solution**: Refresh token or login again

### Cannot Access Admin Dashboard
1. **Issue**: "Superuser access required" error
   - **Solution**: Ensure user has `is_superuser: true` flag

2. **Issue**: "Invalid credentials" error
   - **Solution**: Verify username and password, check if user exists

3. **Issue**: Login form not showing
   - **Solution**: Check admin server is running on port 8001

### Superuser Not Working
1. **Issue**: User not recognized as superuser
   - **Solution**: Run `user_manager.set_superuser(user_id, True)`

2. **Issue**: Cannot grant superuser to other users
   - **Solution**: Ensure you're logged in as superuser on admin dashboard

## User Management

### Check User Status
```python
from app.auth import user_manager

# Get user by username
user = None
for uid, u in user_manager.users.items():
    if u["username"] == "admin":
        user = u
        break

if user:
    print(f"Is Superuser: {user.get('is_superuser', False)}")
    print(f"Roles: {user.get('roles', [])}")
```

### List All Superusers
```python
from app.auth import user_manager

superusers = [
    user for user in user_manager.users.values()
    if user.get("is_superuser", False)
]

for user in superusers:
    print(f"{user['username']} ({user['email']})")
```

### Check User Subscription
```python
from app.auth import user_manager

# Get subscription status
subscription = user_manager.get_subscription_status(user_id)
print(f"Plan: {subscription['plan']}")
print(f"Status: {subscription['status']}")
print(f"Expiry: {subscription.get('expiry_date', 'Never')}")
```

## OAuth Integration

The system supports OAuth providers (Google, GitHub, etc.):

### Current Status
- Infrastructure in place in `app/auth/__init__.py`
- API endpoints created in `app/api/__init__.py`
- Returns 501 (Not Implemented) until configured

### Implementation Required
1. Register OAuth application with provider (Google, GitHub, etc.)
2. Add client ID and secret to `.env` file
3. Implement OAuth flow in callback handler
4. Update `create_user_from_oauth` to handle provider-specific data

## Subscription Management

### Subscription Plans
- **Free**: No expiry, basic features
- **Basic**: 30-day duration, enhanced features
- **Pro**: 30-day duration, full features
- **Enterprise**: Custom duration, all features

### Update Subscription
```python
from app.auth import user_manager

# Update subscription
subscription = user_manager.update_subscription(
    user_id=user_id,
    plan="pro",
    duration_days=30
)
```

### Check Subscription Status
```python
from app.auth import user_manager

# Get status (auto-checks expiry)
status = user_manager.get_subscription_status(user_id)
if status["status"] == "expired":
    # Handle expired subscription
    pass
```

## Conclusion

The access control system is now properly organized:

- **Main Dashboard**: User authentication required for all pages
- **Admin Dashboard**: Superuser authentication required for all functions
- **Clear Separation**: Different ports, different authentication requirements
- **User Management**: Comprehensive user and subscription tracking
- **Security**: Proper role-based access control with logging

All pages are now properly secured according to their intended access level.
