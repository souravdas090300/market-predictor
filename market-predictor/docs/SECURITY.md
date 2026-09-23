# Security Documentation

## Overview

This document describes the security features implemented in the Market Predictor application and how to use them.

## Security Features

### 1. Authentication & Authorization

#### JWT Token-Based Authentication
- **Access Tokens**: 30-minute expiration
- **Refresh Tokens**: 7-day expiration
- **Secure Storage**: Tokens are signed with HS256 algorithm
- **Demo Account**: `demo` / `demo123` for testing

#### User Management
- User registration with email validation
- Password hashing with bcrypt
- Account activation/deactivation
- User preferences management

### 2. Rate Limiting

#### Endpoint-Specific Limits
- **Public endpoints**: 100 requests/minute
- **Signal endpoints**: 60 requests/minute
- **Material analysis**: 30 requests/minute
- **Bulk operations**: 10 requests/minute
- **Authentication**: 10 requests/minute (login), 5 requests/minute (register)

#### Implementation
- Redis-based distributed rate limiting (with memory fallback)
- Per-client identification
- Configurable time windows and request limits

### 3. API Key Management

#### API Key Features
- Secure API key generation
- Scope-based access control (read, write)
- API key revocation
- Usage tracking (last used timestamp)
- User-specific key management

#### Scopes
- `read`: Access to read-only endpoints
- `write`: Access to write operations
- Custom scopes can be added as needed

### 4. Input Validation & Sanitization

#### Symbol Validation
- Format validation (alphanumeric, hyphens, periods)
- Length limits (max 20 characters)
- Case normalization (uppercase)

#### URL Validation
- Protocol validation (HTTP/HTTPS only)
- Private network blocking (localhost, 192.168.x.x, etc.)
- Comprehensive URL parsing

#### Text Sanitization
- Length limits (max 20,000 characters)
- Removal of control characters
- Basic XSS prevention

#### File Upload Security
- File size limits (5MB max)
- File type validation (PDF, CSV only)
- Content scanning capabilities

### 5. Security Headers

#### Implemented Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS enforcement)
- `Content-Security-Policy` (CSP headers)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` (restricts sensitive APIs)

### 6. CORS Configuration

#### CORS Settings
- Configurable allowed origins via environment variables
- Credentials support for cross-origin requests
- All methods and headers allowed for trusted origins

### 7. Session Management

#### Session Features
- Secure session ID generation
- Session expiration (24 hours)
- Session cleanup and rotation
- Activity tracking

### 8. Security Logging

#### Logged Events
- User registration
- Login attempts (success/failure)
- API key creation/revocation
- User account changes
- Failed authentication attempts
- Security violations

#### Log Storage
- Rotating log files (10MB max, 5 backups)
- Structured logging format
- Separate security log file

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Security Configuration
SECRET_KEY=your-secret-key-here-generate-with-python-secrets
REDIS_URL=redis://localhost:6379/0

# Security Settings
ALLOW_PRIVATE_URLS=false
ENABLE_RATE_LIMITING=true
ENABLE_AUTHENTICATION=true

# API Settings
API_CACHE_SECONDS=300
BULK_LIMIT=50

# File Upload Limits
MAX_UPLOAD_BYTES=5000000

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_LEVEL=INFO

# CORS Settings
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Generating Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## API Usage

### Authentication

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123"}'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

#### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your_refresh_token"}'
```

### Protected Endpoints

#### Using JWT Token
```bash
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer your_access_token"
```

#### Using API Key
```bash
curl -X GET http://localhost:8000/api/signal/AAPL \
  -H "X-API-Key: your_api_key"
```

### API Key Management

#### Create API Key
```bash
curl -X POST http://localhost:8000/api/auth/api-key \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"name":"Trading Bot","scopes":["read","write"]}'
```

#### List API Keys
```bash
curl -X GET http://localhost:8000/api/auth/api-keys \
  -H "Authorization: Bearer your_access_token"
```

#### Revoke API Key
```bash
curl -X DELETE http://localhost:5000/api/auth/api-key/key_id \
  -H "Authorization: Bearer your_access_token"
```

## Security Best Practices

### For Developers

1. **Never commit secrets**: Use environment variables
2. **Rotate keys regularly**: Change JWT secret periodically
3. **Monitor logs**: Review security logs regularly
4. **Use HTTPS**: Always use HTTPS in production
5. **Keep dependencies updated**: Regular security updates
6. **Limit API key scopes**: Grant minimum required permissions
7. **Monitor rate limits**: Watch for abuse patterns

### For Users

1. **Use strong passwords**: Minimum 8 characters, mixed case, numbers, symbols
2. **Enable 2FA**: When available
3. **Protect API keys**: Never share or commit them
4. **Use HTTPS**: Always use secure connections
5. **Report issues**: Report security vulnerabilities immediately
6. **Regular password changes**: Update passwords periodically
7. **Review permissions**: Regularly audit API key permissions

## Security Testing

### Running Security Tests

```bash
# Install security testing tools
pip install bandit safety

# Run security checks
bandit -r app/
safety check

# Run security tests
pytest tests/test_security.py
```

### Manual Security Testing

1. **Authentication Testing**
   - Test with invalid credentials
   - Test token expiration
   - Test refresh token flow

2. **Rate Limiting Testing**
   - Test endpoint limits
   - Test distributed rate limiting
   - Test rate limit headers

3. **Input Validation Testing**
   - Test malicious input
   - Test oversized payloads
   - Test malformed requests

4. **Authorization Testing**
   - Test unauthorized access
   - Test role-based access
   - Test API key permissions

## Deployment Security

### Production Checklist

- [ ] Set strong SECRET_KEY in environment variables
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure Redis for distributed rate limiting
- [ ] Set up proper CORS origins
- [ ] Enable security logging and monitoring
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable security alerts
- [ ] Review and update dependencies regularly
- [ ] Conduct security audits

### Docker Security

```dockerfile
# Dockerfile example
FROM python:3.12-slim

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Security configurations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/watchlist || exit 1

# Run as non-root
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring and Alerts

### Security Metrics to Monitor

1. **Failed login attempts**
2. **Rate limit violations**
3. **Unusual API usage patterns**
4. **Token refresh frequency**
5. **Failed API key usage**
6. **Input validation failures**
7. **File upload attempts**

### Alert Configuration

Set up alerts for:
- Brute force attack detection
- Anomaly detection in API usage
- Security log file size
- Failed authentication spikes
- Rate limit exhaustion

## Compliance

### Data Protection

- **Data at Rest**: All passwords are hashed with bcrypt
- **Data in Transit**: HTTPS encryption
- **Data Retention**: Configurable data retention policies
- **Data Access**: Role-based access control

### Audit Trail

- All authentication events logged
- API key creation/revocation tracked
- User account changes recorded
- Security violations documented

## Incident Response

### Security Incident Response Plan

1. **Identification**: Monitor security logs for anomalies
2. **Containment**: Revoke compromised credentials
3. **Eradication**: Fix security vulnerabilities
4. **Recovery**: Restore from clean backups
5. **Lessons Learned**: Update security practices

## Support

For security issues or questions:
- Email: security@marketpredictor.com
- Documentation: See SECURITY.md
- Issues: Report via GitHub issues with "security" tag

## Version History

- **v1.0.0** (2026-09-22): Initial security implementation
  - JWT authentication
  - Rate limiting
  - API key management
  - Input validation
  - Security headers
  - Security logging