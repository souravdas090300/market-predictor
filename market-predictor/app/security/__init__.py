"""Security module for authentication, authorization, and security utilities."""
import os
import secrets
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import redis
from functools import wraps
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param

from ..core import config

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing - using argon2 instead of bcrypt to avoid 72-byte limit issues
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Redis for rate limiting and session storage (optional, falls back to memory)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    USE_REDIS = True
except:
    redis_client = None
    USE_REDIS = False
    # Fallback to in-memory storage
    _memory_store: Dict[str, Any] = {}

# Security bearer scheme
bearer_scheme = HTTPBearer()


class SecurityError(Exception):
    """Base security exception."""
    pass


class AuthenticationError(SecurityError):
    """Authentication failed."""
    pass


class AuthorizationError(SecurityError):
    """Authorization failed."""
    pass


class RateLimitError(SecurityError):
    """Rate limit exceeded."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(16)  # Unique identifier for refresh token
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
    """Get the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    try:
        payload = decode_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
            
    except AuthenticationError:
        raise credentials_exception
    
    return {"username": username, **payload}


def get_current_active_user(current_user: Dict[str, Any]) -> Dict[str, Any]:
    """Get the current active user."""
    if current_user.get("disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Rate limiting
class RateLimiter:
    """Rate limiter using Redis or in-memory storage."""
    
    def __init__(self):
        self.requests = {}
        self.window = 60  # 1 minute window
        self.max_requests = 100  # Max requests per minute
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        
        if USE_REDIS:
            # Use Redis for distributed rate limiting
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(f"rate_limit:{key}", 0, now - self.window)
            pipe.zcard(f"rate_limit:{key}")
            pipe.zadd(f"rate_limit:{key}", {str(now): now})
            pipe.expire(f"rate_limit:{key}", self.window + 1)
            results = pipe.execute()
            count = results[1]
            return count < self.max_requests
        else:
            # Fallback to in-memory storage
            if key not in self.requests:
                self.requests[key] = []
            
            # Clean old requests
            self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < self.window]
            
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for a key."""
        if USE_REDIS:
            count = redis_client.zcard(f"rate_limit:{key}")
            return max(0, self.max_requests - count)
        else:
            now = time.time()
            if key not in self.requests:
                return self.max_requests
            self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < self.window]
            return max(0, self.max_requests - len(self.requests[key]))


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_decorator(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting endpoints."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get client identifier (IP or user)
            # This is a simplified version - in production you'd get this from request headers
            client_id = "default"  # In production, use request.client.host or user ID
            
            rate_limiter.max_requests = max_requests
            rate_limiter.window = window
            
            if not rate_limiter.is_allowed(client_id):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + window)
                    }
                )
            
            remaining = rate_limiter.get_remaining(client_id)
            
            # Continue with the function
            result = await func(*args, **kwargs)
            
            # Add rate limit headers to response
            if hasattr(result, 'headers'):
                result.headers["X-RateLimit-Limit"] = str(max_requests)
                result.headers["X-RateLimit-Remaining"] = str(remaining)
                result.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
            
            return result
        return wrapper
    return decorator


# API Key management
class APIKeyManager:
    """Manage API keys for external access."""
    
    def __init__(self):
        self.api_keys = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from storage."""
        # In production, load from database or secure storage
        api_keys_file = config.ROOT / "data" / "api_keys.json"
        if api_keys_file.exists():
            import json
            try:
                with open(api_keys_file) as f:
                    self.api_keys = json.load(f)
            except:
                self.api_keys = {}
    
    def _save_api_keys(self):
        """Save API keys to storage."""
        api_keys_file = config.ROOT / "data"
        api_keys_file.mkdir(exist_ok=True)
        api_keys_file = api_keys_file / "api_keys.json"
        
        import json
        with open(api_keys_file, 'w') as f:
            json.dump(self.api_keys, f, indent=2)
    
    def generate_api_key(self, user_id: str, name: str, scopes: list = None) -> str:
        """Generate a new API key."""
        if scopes is None:
            scopes = ["read", "write"]
        
        api_key = f"mp_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        key_data = {
            "key_hash": key_hash,
            "user_id": user_id,
            "name": name,
            "scopes": scopes,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "is_active": True
        }
        
        # Store by hash instead of raw key for security
        self.api_keys[key_hash] = key_data
        self._save_api_keys()
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return its data."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in self.api_keys and self.api_keys[key_hash]["is_active"]:
            # Update last used
            self.api_keys[key_hash]["last_used"] = datetime.utcnow().isoformat()
            self._save_api_keys()
            return self.api_keys[key_hash]
        
        return None
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            self.api_keys[key_hash]["is_active"] = False
            self._save_api_keys()
            return True
        return False
    
    def list_user_api_keys(self, user_id: str) -> list:
        """List all API keys for a user."""
        return [
            {
                "name": data["name"],
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "is_active": data["is_active"],
                "scopes": data["scopes"]
            }
            for key_hash, data in self.api_keys.items()
            if data["user_id"] == user_id
        ]


# Global API key manager
api_key_manager = APIKeyManager()


# Input validation and sanitization
import re
from urllib.parse import urlparse

def sanitize_symbol(symbol: str) -> str:
    """Sanitize and validate stock/crypto symbol."""
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Validate format (basic validation)
    if not re.match(r'^[A-Z0-9\-\.=]+$', symbol):
        raise ValueError("Invalid symbol format")
    
    # Length check
    if len(symbol) > 20:
        raise ValueError("Symbol too long")
    
    return symbol


def validate_url(url: str) -> bool:
    """Validate and sanitize URL."""
    try:
        result = urlparse(url)
        
        # Check for private/internal addresses
        if not config.ALLOW_PRIVATE_URLS:
            hostname = result.hostname or ""
            if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
                return False
            if hostname.startswith('192.168.') or hostname.startswith('10.'):
                return False
            if hostname.startswith('172.'):
                parts = hostname.split('.')
                if len(parts) == 4 and 16 <= int(parts[1]) <= 31:
                    return False
        
        # Only allow HTTP/HTTPS
        if result.scheme not in ['http', 'https']:
            return False
        
        return True
    except:
        return False


def sanitize_text(text: str, max_length: int = 20000) -> str:
    """Sanitize user-provided text."""
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove potentially dangerous characters (basic sanitization)
    # This is a basic implementation - in production use proper sanitization libraries
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text


# Security headers
def get_security_headers() -> Dict[str, str]:
    """Get security headers for HTTP responses."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }


# Session management
class SessionManager:
    """Manage user sessions."""
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        self.sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        # Check if expired
        try:
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                del self.sessions[session_id]
                return None
        except:
            del self.sessions[session_id]
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if datetime.fromisoformat(session["expires_at"]) < now
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)


# Global session manager
session_manager = SessionManager()


# Security logging
import logging
from logging.handlers import RotatingFileHandler

def setup_security_logging():
    """Set up security logging."""
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    
    # Create logs directory
    logs_dir = config.ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        logs_dir / "security.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    security_logger.addHandler(file_handler)
    security_logger.addHandler(console_handler)
    
    return security_logger


security_logger = setup_security_logging()


def log_security_event(event_type: str, details: Dict[str, Any], user_id: str = None):
    """Log a security event."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "details": details
    }
    
    security_logger.info(f"Security Event: {event_type} - {log_data}")


# Export all functions for easier importing
__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'decode_token',
    'get_current_user',
    'get_current_active_user',
    'sanitize_symbol',
    'validate_url',
    'sanitize_text',
    'get_security_headers',
    'log_security_event',
    'api_key_manager',
    'bearer_scheme',
    'SecurityError',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError',
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    'REFRESH_TOKEN_EXPIRE_DAYS',
    'ALGORITHM',
    'SECRET_KEY'
]