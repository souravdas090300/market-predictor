# Dashboard and Admin Separation Guide

## Overview

The Market Predictor application now consists of two completely separate applications:

### 1. Main Dashboard (Port 8000)
- **Purpose**: User-facing market prediction interface
- **URL**: http://localhost:8000
- **Access**: Public with optional authentication
- **API File**: `app/api/__init__.py`
- **Frontend**: `static/index.html`
- **Features**:
  - Market predictions for all assets
  - Technical indicators
  - Material analysis
  - Signal history
  - Portfolio metrics
  - Chart visualization

### 2. Admin Dashboard (Port 8000, /admin path)
- **Purpose**: Administrative interface for system management
- **URL**: http://localhost:8000/admin
- **Access**: Superuser-only authentication required
- **API Endpoints**: `/api/admin/*` (in main API)
- **Frontend**: `static/admin/index.html`
- **Features**:
  - Batch prediction management
  - Rate limiting control
  - System statistics
  - User management
  - Maintenance mode

## Complete Separation Benefits

### Security
- **Isolation**: Admin functions completely isolated from main application
- **Separate Authentication**: Admin users authenticate separately on admin port
- **Independent Rate Limiting**: Admin endpoints have separate rate limiting rules
- **Attack Surface**: Reduces attack surface by separating admin functions

### Operational
- **Independent Deployment**: Can be deployed on different servers
- **Separate Scaling**: Can scale admin and main applications independently
- **Maintenance**: Admin dashboard can be maintained without affecting main app
- **Monitoring**: Admin access can be monitored separately

### Development
- **Clear Boundaries**: Clear separation between user and admin functionality
- **Team Collaboration**: Different teams can work on each application
- **Testing**: Separate test suites for each application
- **Versioning**: Can version each application independently

## Starting the Applications

### Single Server (Recommended)
The main application now serves both dashboards on a single port:

```bash
uvicorn app.api:app --reload --port 8000
```

This serves:
- **Main Dashboard**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/* and http://localhost:8000/api/admin/*

## Access URLs

- **Main Dashboard**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin

## Authentication

### Main Dashboard
- Optional authentication for regular users
- Demo user: `demo` / `demo123`
- Public access to prediction endpoints
- Authentication via `POST /api/auth/login`

### Admin Dashboard
- **Required authentication for all operations**
- Admin-only access check enforced on all endpoints
- Default admin users: `admin` and `demo`
- Admin users must be explicitly granted admin access in admin config
- Authentication via `POST /auth/login` (admin-specific endpoint)

## API Endpoint Differences

### Main Dashboard API (Port 8000)
- `GET /api/watchlist` - Get watchlist
- `GET /api/signal/{symbol}` - Get signal for symbol
- `POST /api/material` - Analyze material
- `GET /api/chart/{symbol}` - Get chart data
- `POST /api/risk/calculate` - Calculate risk
- `POST /api/strategy/optimize` - Optimize strategy
- `GET /api/news/{symbol}` - Get news
- `POST /api/correlation/analyze` - Analyze correlation
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Admin Dashboard API (Port 8000, /api/admin/*)
- `POST /api/admin/auth/login` - Admin login (superuser only)
- `GET /api/admin/config` - Get admin configuration
- `POST /api/admin/rate-limiting` - Toggle rate limiting
- `POST /api/admin/rate-limit/{endpoint}` - Update endpoint rate limit
- `POST /api/admin/maintenance` - Toggle maintenance mode
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/add-admin/{username}` - Add superuser
- `DELETE /api/admin/remove-admin/{username}` - Remove superuser
- `POST /api/admin/batch/predict` - Run batch prediction
- `GET /api/admin/batch/status` - Get batch status
- `GET /api/admin/batch/asset/{symbol}` - Get asset batch prediction

## Configuration Files

### Shared Configuration
- **`data/users.json`** - User accounts (shared by both apps)
- **`data/sessions.json`** - User sessions (shared by both apps)
- **`data/api_keys.json`** - API keys (shared by both apps)

### Main Dashboard Configuration
- **`data/signals.db`** - Signal history
- **`data/batch_predictions.json`** - Batch prediction results

### Admin Dashboard Configuration
- **`data/admin_config.json`** - Admin-specific configuration
  - Rate limiting settings
  - Maintenance mode
  - Admin user list
  - Allowed IPs

## Security Considerations

### Admin Access Control
1. **Admin List**: Admin users are explicitly listed in `data/admin_config.json`
2. **Check on Every Request**: Admin status is verified on every admin API call
3. **Separate Login**: Admin login is handled by separate endpoint on port 8000
4. **Security Logging**: All admin actions are logged to security log

### Network Security
1. **Firewall Rules**: Restrict admin port (8000) to specific IPs in production
2. **VPN Access**: Require VPN for admin access in production
3. **HTTPS**: Use HTTPS for both ports in production
4. **CORS**: Separate CORS configuration for admin port

### Rate Limiting
1. **Independent Limits**: Admin endpoints have separate rate limiting configuration
2. **Higher Limits**: Admin endpoints typically have higher rate limits
3. **Separate Tracking**: Rate limit violations tracked separately for admin

## Deployment Architecture

### Development
```
localhost:8000 -> Main Dashboard
localhost:8000/admin -> Admin Dashboard
```

### Production (Single Server)
```
example.com -> Main Dashboard (Nginx -> Port 8000)
example.com/admin -> Admin Dashboard (same server, different path)
```

### Production (Separate Servers)
```
Server 1 (public): Main Dashboard
Server 2 (private): Admin Dashboard (optional, for additional security)
```

## Troubleshooting

### Admin Dashboard Not Accessible
1. Check if admin server is running on port 8000
2. Verify firewall allows port 8000
3. Check admin user credentials
4. Verify user is in admin list in `data/admin_config.json`

### Authentication Issues
1. For main dashboard: Check `data/users.json`
2. For admin dashboard: Check both `data/users.json` and `data/admin_config.json`
3. Verify user is active and not disabled
4. Check JWT token expiration

### Batch Prediction Issues
1. Batch prediction runs on admin dashboard (port 8000)
2. Check admin dashboard for batch prediction controls
3. Verify `data/batch_predictions.json` exists and is writable
4. Check logs for prediction errors

## Future Enhancements

### Security
- Implement IP-based access control for admin port
- Add two-factor authentication for admin access
- Implement session timeout for admin sessions
- Add audit log for all admin actions

### Features
- Add real-time server metrics to admin dashboard
- Implement database management interface
- Add backup/restore functionality
- Create API key management UI

### Deployment
- Containerize each application separately
- Create Kubernetes manifests for each service
- Implement separate CI/CD pipelines
- Add monitoring and alerting for each service

## Conclusion

The complete separation of dashboard and admin applications provides:
- **Enhanced Security**: Isolated admin functions reduce attack surface
- **Better Operations**: Independent deployment and scaling
- **Clear Boundaries**: Separation of concerns between user and admin functionality
- **Flexibility**: Can deploy and maintain each application independently

This architecture follows security best practices by isolating administrative functions from the main user-facing application.