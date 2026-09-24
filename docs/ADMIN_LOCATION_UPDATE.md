# Admin Dashboard Location Update

## Change Summary

The admin dashboard has been moved from a separate port (8001) to a path on the main application:

**Before:**
- Main Dashboard: http://localhost:8000
- Admin Dashboard: http://localhost:8001 (separate server)

**After:**
- Main Dashboard: http://localhost:8000
- Admin Dashboard: http://localhost:8000/admin (same server, different path)

## Benefits

1. **Simplified Deployment**: Only one server to run
2. **Unified Authentication**: Uses same JWT tokens as main app
3. **Easier Configuration**: Single CORS, rate limiting, and security setup
4. **Resource Efficiency**: One server process instead of two
5. **Simpler URLs**: No need to remember multiple ports

## How to Run

```bash
# Start the application (serves both dashboards)
uvicorn app.api:app --reload --port 8000
```

## Access URLs

- **Main Dashboard**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **Admin API**: http://localhost:8000/api/admin/*

## API Changes

Admin endpoints are now under `/api/admin/*`:

- `POST /api/admin/auth/login` - Admin login
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

## Authentication

- **Main Dashboard**: User authentication required
- **Admin Dashboard**: Superuser authentication required
- **Shared Tokens**: Both use the same JWT authentication system
- **Admin Check**: `/api/admin/*` endpoints verify `is_superuser` flag

## Superuser Management

Create superuser using the setup script:

```bash
python scripts/setup_superuser.py
```

Default credentials:
- **Username**: `admin`
- **Password**: `admin123`

## Frontend Changes

The admin frontend (`static/admin/index.html`) has been updated to:
- Call `/api/admin/*` endpoints instead of separate port API
- Use shared authentication tokens with main app
- Redirect to `/index.html` instead of `http://localhost:8000`

## Notes

- The separate `app/admin_api.py` file still exists but is no longer used
- `scripts/run_admin.py` is no longer needed
- All admin functionality is now integrated into the main API at `/api/admin/*`
- The admin static files remain at `static/admin/` and are mounted at `/admin`
