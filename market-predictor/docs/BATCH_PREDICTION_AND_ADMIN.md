# Batch Prediction and Admin Dashboard Documentation

## Overview

This document describes the batch prediction system and the completely separated admin dashboard for the Market Predictor application.

## Architecture: Complete Separation

### Two Separate Applications

The Market Predictor now consists of two completely separate applications:

1. **Main Dashboard** (Port 8000)
   - URL: `http://localhost:8000`
   - Purpose: User-facing market prediction dashboard
   - Access: Public with optional authentication
   - API: Standard prediction endpoints

2. **Admin Dashboard** (Port 8001)
   - URL: `http://localhost:8001`
   - Purpose: Administrative interface for system management
   - Access: Admin-only authentication required
   - API: Separate admin-specific endpoints
   - Frontend: `static/admin/index.html`

### Security Benefits of Separation

- **Isolation**: Admin functions completely isolated from main application
- **Separate Authentication**: Admin users authenticate separately on admin port
- **Different Rate Limits**: Admin endpoints have independent rate limiting
- **Independent Deployment**: Can be deployed on different servers
- **Security Monitoring**: Admin access can be monitored separately
- **Maintenance**: Admin dashboard can be maintained without affecting main app

## Features Implemented

### 1. Batch Prediction System

#### Purpose
Automatically predict all assets in the watchlist on a schedule (every 1 hour by default) and store results for 90 days.

#### Implementation
- **File**: `app/services/batch_prediction.py`
- **Service**: `BatchPredictionService`
- **Configuration**: Stored in `data/batch_predictions.json`

#### Key Features
- **Scheduled Predictions**: Automatically runs predictions for all assets at configurable intervals
- **1-Hour Refresh**: By default, predictions are refreshed every hour
- **90-Day History**: Maintains prediction history for 90 days
- **Caching**: Avoids redundant predictions if recent data exists
- **Error Handling**: Continues processing even if individual assets fail
- **Aggregate Metrics**: Provides summary statistics across all predictions

#### API Endpoints

##### POST /api/batch/predict
Run batch prediction for all assets.
- **Authentication**: Required
- **Parameters**: 
  - `force_refresh` (bool): Force refresh even if recent prediction exists
- **Response**:
  ```json
  {
    "timestamp": "2026-09-23T12:00:00",
    "total_assets": 13,
    "successful_predictions": 12,
    "failed_predictions": 1,
    "results": {
      "AAPL": {
        "timestamp": "2026-09-23T12:00:00",
        "symbol": "AAPL",
        "name": "Apple",
        "class": "stock",
        "signal": "bullish",
        "probability_up": 0.5836,
        "model_probability_up": 0.5521,
        "sentiment": {...},
        "indicators": {...},
        "candle_patterns": [...],
        "conviction": 0.167
      },
      ...
    }
  }
  ```

##### GET /api/batch/status
Get current batch prediction status and aggregate metrics.
- **Authentication**: Required
- **Response**:
  ```json
  {
    "total_assets": 13,
    "bullish_count": 8,
    "bearish_count": 3,
    "neutral_count": 2,
    "average_conviction": 0.452,
    "valid_predictions": 13,
    "timestamp": "2026-09-23T12:00:00"
  }
  ```

##### GET /api/batch/asset/{symbol}
Get batch prediction for a specific asset.
- **Authentication**: Required
- **Response**: Individual asset prediction data

#### Usage Example
```bash
# Run batch prediction
curl -X POST http://localhost:8000/api/batch/predict \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get batch status
curl http://localhost:8000/api/batch/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific asset prediction
curl http://localhost:8000/api/batch/asset/AAPL \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Scheduling
The batch prediction service includes a scheduling function that can be run as a background process:

```python
from app.services.batch_prediction import batch_service

# Schedule predictions every 1 hour
batch_service.schedule_predictions(interval_hours=1)
```

For production deployment, this should be run as a separate process or via a cron job.

### 2. Admin Dashboard

#### Purpose
Provide a separate administrative interface for managing system settings, rate limiting, and batch predictions.

#### Implementation
- **File**: `app/admin/__init__.py`
- **Service**: `AdminManager`
- **Frontend**: `static/admin.html`
- **Configuration**: Stored in `data/admin_config.json`

#### Key Features
- **Separate Access**: Admin-only endpoints protected by authentication
- **Rate Limiting Control**: Enable/disable rate limiting globally
- **Per-Endpoint Rate Limits**: Customize rate limits for each API endpoint
- **Maintenance Mode**: Enable/disable maintenance mode
- **User Management**: Add/remove admin users
- **System Statistics**: View system overview and batch prediction status
- **IP Whitelist**: Manage allowed IP addresses

#### Admin Access Control

Default admin users:
- `admin` (can be changed in admin config)
- `demo` (existing demo user also has admin access)

To check if a user is admin:
```python
from app.admin import admin_manager

if admin_manager.is_admin_user(username):
    # User has admin access
```

#### API Endpoints

##### GET /api/admin/config
Get admin configuration including rate limits.
- **Authentication**: Admin required
- **Response**:
  ```json
  {
    "rate_limiting_enabled": true,
    "rate_limits": {
      "watchlist": "100/minute",
      "signal": "60/minute",
      "material": "30/minute",
      ...
    },
    "updated_at": "2026-09-23T12:00:00"
  }
  ```

##### POST /api/admin/rate-limiting
Enable or disable rate limiting globally.
- **Authentication**: Admin required
- **Parameters**: `enabled` (bool)
- **Response**:
  ```json
  {
    "message": "Rate limiting enabled",
    "rate_limiting_enabled": true,
    "updated_at": "2026-09-23T12:00:00"
  }
  ```

##### POST /api/admin/rate-limit/{endpoint}
Update rate limit for a specific endpoint.
- **Authentication**: Admin required
- **Parameters**: 
  - `endpoint` (path): API endpoint name
  - `limit` (string): New rate limit (e.g., "100/minute")
- **Response**:
  ```json
  {
    "message": "Rate limit updated for watchlist",
    "endpoint": "watchlist",
    "new_limit": "200/minute",
    "updated_at": "2026-09-23T12:00:00"
  }
  ```

##### POST /api/admin/maintenance
Enable or disable maintenance mode.
- **Authentication**: Admin required
- **Parameters**: `enabled` (bool)
- **Response**:
  ```json
  {
    "message": "Maintenance mode enabled",
    "maintenance_mode": true,
    "updated_at": "2026-09-23T12:00:00"
  }
  ```

##### GET /api/admin/stats
Get system statistics and batch prediction status.
- **Authentication**: Admin required
- **Response**:
  ```json
  {
    "config": {
      "rate_limiting_enabled": true,
      "maintenance_mode": false,
      "total_admin_users": 2,
      "total_allowed_ips": 0
    },
    "batch_predictions": {
      "total_assets": 13,
      "bullish_count": 8,
      "bearish_count": 3,
      "neutral_count": 2,
      "average_conviction": 0.452
    },
    "system_info": {
      "python_version": "3.12.8",
      "watchlist_size": 13,
      "root_path": "/path/to/project"
    },
    "timestamp": "2026-09-23T12:00:00"
  }
  ```

##### POST /api/admin/add-admin/{username}
Add a user to admin list.
- **Authentication**: Admin required
- **Response**:
  ```json
  {
    "message": "User john added to admin list",
    "admin_users": ["admin", "demo", "john"]
  }
  ```

##### DELETE /api/admin/remove-admin/{username}
Remove a user from admin list.
- **Authentication**: Admin required
- **Response**:
  ```json
  {
    "message": "User john removed from admin list",
    "admin_users": ["admin", "demo"]
  }
  ```

#### Admin Dashboard UI

Access the admin dashboard at: `http://localhost:8000/admin.html`

##### Features
1. **Overview Tab**
   - System statistics
   - Batch prediction status
   - Rate limiting status
   - Maintenance mode status
   - Admin user count

2. **Rate Limiting Tab**
   - Toggle rate limiting on/off
   - Toggle maintenance mode
   - Per-endpoint rate limit configuration
   - Update individual endpoint limits

3. **Batch Predictions Tab**
   - Run batch prediction manually
   - View batch prediction results
   - Refresh status
   - Detailed results table

4. **Users Tab**
   - Add admin users
   - Remove admin users
   - View current admin list

#### UI Navigation
- **Overview**: System statistics and status
- **Rate Limiting**: Configure rate limits
- **Batch Predictions**: Manage batch predictions
- **Users**: Manage admin users
- **Back to Main App**: Return to main dashboard

#### Usage Example
```bash
# Access admin dashboard
open http://localhost:8000/admin.html

# Login with admin credentials
# Username: admin or demo
# Password: demo12345 (for demo user)

# Or use API directly
curl http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Security Considerations

### Admin Access
- Admin endpoints require authentication AND admin role
- Admin users are managed separately from regular users
- Admin list is stored in `data/admin_config.json`
- Default admin users: `admin` and `demo`

### Rate Limiting Control
- Rate limiting can be completely disabled (not recommended in production)
- Individual endpoint limits can be adjusted
- Changes take effect immediately
- All rate limit changes are logged

### Maintenance Mode
- When enabled, the system can show maintenance messages
- Future enhancement: Block non-admin requests during maintenance
- Currently informational only

## Deployment

### Starting Both Applications

#### Start Main Dashboard (Port 8000)
```bash
uvicorn app.api:app --reload --port 8000
```

#### Start Admin Dashboard (Port 8001)
```bash
python scripts/run_admin.py
```

Or with uvicorn directly:
```bash
uvicorn app.admin_api:admin_app --reload --port 8001
```

### Access URLs

- **Main Dashboard**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8001

### Authentication

#### Main Dashboard
- Optional authentication for regular users
- Demo user: `demo` / `demo12345`
- Public access to prediction endpoints

#### Admin Dashboard
- **Required authentication for all operations**
- Admin-only access check
- Default admin users: `admin` and `demo`
- Admin users must be explicitly granted admin access

## Deployment Considerations

### Batch Prediction Scheduling
For production deployment, you have several options:

#### Option 1: Background Process
```bash
# Run as background process
python -c "from app.services.batch_prediction import batch_service; batch_service.schedule_predictions()"
```

#### Option 2: Cron Job
```bash
# Add to crontab
0 * * * * cd /path/to/project && python -c "from app.services.batch_prediction import batch_service; batch_service.predict_all_assets(force_refresh=True)"
```

#### Option 3: Systemd Service
Create a systemd service file for automatic scheduling.

### Admin Dashboard Access
- Restrict admin dashboard access via firewall rules
- Use reverse proxy (nginx) to add additional authentication layer
- Consider IP whitelisting for admin access
- Log all admin actions

### Rate Limiting Configuration
- Start with conservative limits in production
- Monitor rate limit violations
- Adjust limits based on actual usage patterns
- Never disable rate limiting in production unless absolutely necessary

## Testing

### Batch Prediction Tests
```bash
# Test batch prediction endpoint
curl -X POST http://localhost:8000/api/batch/predict \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test batch status endpoint
curl http://localhost:8000/api/batch/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Admin Dashboard Tests
```bash
# First, login to get admin token
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# Test admin config endpoint
curl http://localhost:8001/config \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Test rate limiting toggle
curl -X POST "http://localhost:8001/rate-limiting?enabled=false" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Test admin stats
curl http://localhost:8001/stats \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Configuration Files

### Batch Predictions
- **Location**: `data/batch_predictions.json`
- **Format**: JSON with symbol keys and prediction data
- **Retention**: 90 days (configurable)

### Admin Configuration
- **Location**: `data/admin_config.json`
- **Format**: JSON with system settings
- **Key Settings**:
  - `rate_limiting_enabled`: Global rate limiting toggle
  - `rate_limits`: Per-endpoint rate limits
  - `maintenance_mode`: Maintenance mode toggle
  - `admin_users`: List of admin usernames
  - `allowed_ips`: IP whitelist (future enhancement)

## Integration with Existing Features

### Security Integration
- Admin endpoints use existing JWT authentication
- Admin check added to user authentication flow
- Security logging for all admin actions
- Rate limiting applies to admin endpoints (with higher limits)

### API Integration
- Batch prediction uses existing prediction service
- Admin configuration stored alongside other data files
- Reuses existing rate limiting infrastructure
- Integrates with existing user management

### Frontend Integration
- Admin dashboard is separate from main dashboard
- Uses same authentication tokens
- Professional design system consistent with main app
- Responsive design for mobile access

## Troubleshooting

### Batch Prediction Issues
- **Problem**: Batch prediction fails for some assets
- **Solution**: Check logs for specific error messages, verify data sources are accessible
- **Problem**: Predictions not refreshing
- **Solution**: Check scheduling process is running, verify force_refresh parameter

### Admin Dashboard Issues
- **Problem**: Cannot access admin endpoints
- **Solution**: Verify user is in admin list, check JWT token is valid
- **Problem**: Rate limiting changes not taking effect
- **Solution**: Restart server, check admin config file permissions

### Rate Limiting Issues
- **Problem**: Rate limiting disabled but still being applied
- **Solution**: Check if middleware is properly reading admin config
- **Problem**: Individual endpoint limits not working
- **Solution**: Verify endpoint name matches configuration key

## Future Enhancements

### Batch Prediction
- Add historical prediction analysis
- Implement prediction accuracy tracking
- Add email/SMS alerts for significant signal changes
- Create prediction comparison dashboard

### Admin Dashboard
- Add real-time server metrics (CPU, memory, disk)
- Implement log viewer
- Add database management interface
- Create backup/restore functionality
- Add API key management UI

### Rate Limiting
- Add rate limit analytics dashboard
- Implement IP-based rate limiting
- Add user-specific rate limits
- Create rate limit violation alerts

## Conclusion

The batch prediction system and admin dashboard provide powerful administrative capabilities for the Market Predictor application. The batch prediction system ensures all assets are regularly analyzed and predictions are stored for historical analysis. The admin dashboard gives administrators control over system settings, rate limiting, and user management through a professional, separate interface.

Both features are production-ready and integrate seamlessly with the existing security and API infrastructure.