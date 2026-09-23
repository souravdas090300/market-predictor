# Environment Configuration Guide

## Overview

The Market Predictor application now supports separate environment configurations for development and production deployments.

## Environment Files

### `.env.dev` - Development Environment
Used for local development with relaxed security settings and debugging enabled.

**Key Settings:**
- `ENV=development`
- `SECRET_KEY=dev-secret-key-for-local-development-only`
- `ALLOW_PRIVATE_URLS=true` - Allows fetching from private networks
- `ENABLE_DEBUG_MODE=true` - Enables debug features
- `ENABLE_TESTING_MODE=true` - Enables testing features
- `LOG_LEVEL=DEBUG` - Verbose logging
- `API_CACHE_SECONDS=60` - Shorter cache for development
- `BULK_LIMIT=100` - Higher bulk limit for testing
- `MAX_UPLOAD_BYTES=10000000` - Larger upload limit
- `CORS_ORIGINS` - Allows localhost and local development servers

### `.env.prod` - Production Environment
Used for production deployment with strict security settings.

**Key Settings:**
- `ENV=production`
- `SECRET_KEY=CHANGE_THIS_TO_A_STRONG_RANDOM_SECRET_KEY_IN_PRODUCTION` - Must be changed!
- `ALLOW_PRIVATE_URLS=false` - Blocks private network URLs
- `ENABLE_DEBUG_MODE=false` - Disables debug features
- `ENABLE_TESTING_MODE=false` - Disables testing features
- `LOG_LEVEL=INFO` - Standard logging
- `API_CACHE_SECONDS=300` - Longer cache for performance
- `BULK_LIMIT=50` - Lower bulk limit for production
- `MAX_UPLOAD_BYTES=5000000` - Standard upload limit
- `CORS_ORIGINS` - Restricted to production domains only

### `.env.example` - Template
Template file showing all available configuration options.

## Usage

### Development Mode

**Option 1: Using the development script**
```bash
python scripts/run_dev.py
```

**Option 2: Using uvicorn directly with environment variable**
```bash
export ENV=development
uvicorn app.api:app --reload --port 8000
```

**Option 3: Loading environment file manually**
```bash
python scripts/load_env.py development
uvicorn app.api:app --reload --port 8000
```

### Production Mode

**Option 1: Using the production script**
```bash
python scripts/run_prod.py
```

**Option 2: Using uvicorn directly with environment variable**
```bash
export ENV=production
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option 3: Loading environment file manually**
```bash
python scripts/load_env.py production
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration Differences

| Setting | Development | Production |
|---------|------------|------------|
| `ENV` | `development` | `production` |
| `SECRET_KEY` | Dev key (safe for local) | Must be strong random key |
| `ALLOW_PRIVATE_URLS` | `true` | `false` |
| `ENABLE_DEBUG_MODE` | `true` | `false` |
| `ENABLE_TESTING_MODE` | `true` | `false` |
| `LOG_LEVEL` | `DEBUG` | `INFO` |
| `SECURITY_LOG_LEVEL` | `DEBUG` | `INFO` |
| `API_CACHE_SECONDS` | `60` | `300` |
| `BULK_LIMIT` | `100` | `50` |
| `MAX_UPLOAD_BYTES` | `10,000,000` | `5,000,000` |
| `CORS_ORIGINS` | localhost,127.0.0.1 | production domains |
| Workers | 1 (reload enabled) | 4 (no reload) |

## Production Setup Checklist

Before deploying to production:

1. **Generate Strong Secret Key**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Copy the output and set it as `SECRET_KEY` in `.env.prod`

2. **Update CORS Origins**
   Set `CORS_ORIGINS` to your actual production domains:
   ```
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Configure Redis** (if using)
   Update `REDIS_URL` to your production Redis instance

4. **Set Up SSL/HTTPS**
   Configure your web server (Nginx, Apache) with SSL certificates

5. **Configure Firewall**
   Restrict access to port 8000 if needed

6. **Remove Demo Accounts**
   Disable or remove the demo account before production

7. **Set Up Monitoring**
   Configure logging and monitoring for production

## Environment-Specific Behavior

### Development Mode
- Detailed debug logging
- Error stack traces shown in responses
- Auto-reload on code changes
- Allows private network URLs
- Higher rate limits
- Longer cache timeouts for testing
- Debug features enabled

### Production Mode
- Standard logging (no debug)
- Generic error messages (no stack traces)
- No auto-reload
- Blocks private network URLs
- Stricter rate limits
- Optimized cache settings
- Multiple workers for performance
- Debug features disabled

## File Structure

```
market-predictor/
├── .env                    # Current active environment (gitignored)
├── .env.dev               # Development configuration (gitignored)
├── .env.prod              # Production configuration (gitignored)
├── .env.example           # Configuration template (committed)
├── app/
│   └── core/
│       └── config.py      # Loads environment variables
└── scripts/
    ├── load_env.py        # Environment loader utility
    ├── run_dev.py         # Development runner
    └── run_prod.py        # Production runner
```

## Git Configuration

Add to `.gitignore`:
```
.env
.env.dev
.env.prod
```

Commit `.env.example` to provide template for other developers.

## Testing

### Test Development Configuration
```bash
python scripts/run_dev.py
# Check that debug mode is enabled
# Check that localhost CORS is allowed
# Check that private URLs are allowed
```

### Test Production Configuration
```bash
python scripts/run_prod.py
# Check that debug mode is disabled
# Check that CORS is restricted
# Check that private URLs are blocked
```

## Troubleshooting

### Environment Not Loading
```bash
# Check current environment
python -c "import os; print(os.getenv('ENV', 'not set'))"

# Manually load environment
python scripts/load_env.py development
```

### CORS Issues in Production
- Update `CORS_ORIGINS` in `.env.prod` to include your domain
- Ensure HTTPS is configured (CORS doesn't work well with mixed content)

### Rate Limiting Too Strict
- Adjust `BULK_LIMIT` in `.env.prod`
- Modify rate limiting settings in admin dashboard

### Secret Key Warning
- Generate a new secret key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Update `SECRET_KEY` in `.env.prod`
- Restart the application

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong secret keys** in production
3. **Restrict CORS origins** to your actual domains
4. **Disable debug mode** in production
5. **Use HTTPS** in production
6. **Regularly rotate secret keys**
7. **Monitor security logs** for suspicious activity
8. **Keep dependencies updated**
9. **Use firewall rules** to restrict access
10. **Implement backup and recovery** procedures

## Docker Deployment (Optional)

If using Docker, you can pass environment variables:

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "scripts/run_prod.py"]
```

```bash
# Run with environment file
docker run -p 8000:8000 --env-file .env.prod market-predictor
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment name | `development` |
| `SECRET_KEY` | JWT signing key | auto-generated |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ALLOW_PRIVATE_URLS` | Allow private network URLs | `false` (prod) / `true` (dev) |
| `ENABLE_RATE_LIMITING` | Enable rate limiting | `true` |
| `ENABLE_AUTHENTICATION` | Enable authentication | `true` |
| `API_CACHE_SECONDS` | API cache duration | `60` (dev) / `300` (prod) |
| `BULK_LIMIT` | Max bulk items | `100` (dev) / `50` (prod) |
| `MAX_UPLOAD_BYTES` | Max upload size | `10M` (dev) / `5M` (prod) |
| `LOG_LEVEL` | Application log level | `DEBUG` (dev) / `INFO` (prod) |
| `SECURITY_LOG_LEVEL` | Security log level | `DEBUG` (dev) / `INFO` (prod) |
| `CORS_ORIGINS` | Allowed CORS origins | localhost (dev) / domain (prod) |
| `ADMIN_CORS_ORIGINS` | Admin CORS origins | localhost (dev) / domain (prod) |
| `ENABLE_DEBUG_MODE` | Enable debug features | `true` (dev) / `false` (prod) |
| `ENABLE_PROFILING` | Enable profiling | `false` |
| `ENABLE_TESTING_MODE` | Enable testing mode | `true` (dev) / `false` (prod) |
