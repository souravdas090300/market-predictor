"""Separate admin API with complete isolation from main dashboard."""
from __future__ import annotations

import time
import os
import secrets
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .core import config
from .services import batch_prediction
from .security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_token, sanitize_symbol, sanitize_text, validate_url, get_security_headers,
    log_security_event, api_key_manager, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES,
    AuthenticationError
)
from .auth import UserManager, user_manager

# Admin-specific configuration
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", os.getenv("SECRET_KEY", secrets.token_urlsafe(32)))
ADMIN_ALGORITHM = "HS256"

# Admin limiter
admin_limiter = Limiter(key_func=get_remote_address)
admin_app = FastAPI(
    title="Market Predictor Admin",
    version="1.0.0",
    description="Administrative interface for Market Predictor"
)

# Security middleware
admin_app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS configuration for admin
admin_origins = os.getenv("ADMIN_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=admin_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
admin_app.state.limiter = admin_limiter
admin_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers
@admin_app.middleware("http")
async def add_admin_security_headers(request: Request, call_next):
    response = await call_next(request)
    for header, value in get_security_headers().items():
        response.headers[header] = value
    return response

# Security bearer scheme
security = HTTPBearer()

# Admin-only dependency
def admin_required(current_user: dict = Depends(get_current_active_user)):
    """Dependency to check if user is admin (superuser)."""
    from .auth import user_manager
    if not user_manager.is_superuser_by_username(current_user["username"]):
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user

# Mount static files
admin_app.mount("/", StaticFiles(directory=str(config.ROOT / "static" / "admin"), html=True), name="admin_static")


# Authentication endpoints for admin
class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


@admin_app.post("/auth/login")
@admin_limiter.limit("10/minute")
def admin_login(request: Request, body: LoginRequest):
    """Admin login endpoint."""
    # Authenticate user
    user_data = user_manager.authenticate_user(body.username, body.password)
    
    if not user_data:
        log_security_event("ADMIN_LOGIN_FAILED", {
            "username": body.username,
            "ip": request.client.host
        })
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is superuser
    if not user_manager.is_superuser_by_username(body.username):
        log_security_event("ADMIN_LOGIN_DENIED", {
            "username": body.username,
            "ip": request.client.host
        })
        raise HTTPException(status_code=403, detail="Superuser access required")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_data["username"]})
    refresh_token = create_refresh_token(data={"sub": user_data["username"]})
    
    # Log security event
    log_security_event("ADMIN_LOGIN_SUCCESS", {
        "username": body.username,
        "ip": request.client.host
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user_data["username"],
            "email": user_data["email"],
            "is_superuser": True
        }
    }


# Admin configuration endpoints
@admin_app.get("/config")
@admin_limiter.limit("30/minute")
def get_admin_config(request: Request, current_user: dict = Depends(admin_required)):
    """Get admin configuration."""
    try:
        from .admin import admin_manager
        return admin_manager.get_rate_limits()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting admin config: {str(e)}")


@admin_app.post("/rate-limiting")
@admin_limiter.limit("10/minute")
def toggle_rate_limiting(request: Request, enabled: bool, current_user: dict = Depends(admin_required)):
    """Enable or disable rate limiting."""
    try:
        from .admin import admin_manager
        result = admin_manager.enable_rate_limiting(enabled)
        log_security_event("RATE_LIMITING_TOGGLED", {
            "enabled": enabled,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling rate limiting: {str(e)}")


@admin_app.post("/rate-limit/{endpoint}")
@admin_limiter.limit("10/minute")
def update_rate_limit(request: Request, endpoint: str, limit: str, current_user: dict = Depends(admin_required)):
    """Update rate limit for a specific endpoint."""
    try:
        from .admin import admin_manager
        result = admin_manager.update_rate_limit(endpoint, limit)
        log_security_event("RATE_LIMIT_UPDATED", {
            "endpoint": endpoint,
            "new_limit": limit,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rate limit: {str(e)}")


@admin_app.post("/maintenance")
@admin_limiter.limit("10/minute")
def toggle_maintenance(request: Request, enabled: bool, current_user: dict = Depends(admin_required)):
    """Enable or disable maintenance mode."""
    try:
        from .admin import admin_manager
        result = admin_manager.set_maintenance_mode(enabled)
        log_security_event("MAINTENANCE_TOGGLED", {
            "enabled": enabled,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling maintenance mode: {str(e)}")


@admin_app.get("/stats")
@admin_limiter.limit("30/minute")
def get_system_stats(request: Request, current_user: dict = Depends(admin_required)):
    """Get system statistics."""
    try:
        from .admin import admin_manager
        stats = admin_manager.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")


@admin_app.post("/add-admin/{username}")
@admin_limiter.limit("10/minute")
def add_admin_user(request: Request, username: str, current_user: dict = Depends(admin_required)):
    """Add a user to admin list (set as superuser)."""
    try:
        # Find user by username
        user_id = None
        for uid, user in user_manager.users.items():
            if user["username"].lower() == username.lower():
                user_id = uid
                break
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Set as superuser
        user_manager.set_superuser(user_id, True)
        
        log_security_event("SUPERUSER_GRANTED", {
            "new_superuser": username,
            "admin": current_user["username"]
        })
        
        return {
            "message": f"User {username} granted superuser privileges",
            "username": username,
            "is_superuser": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding superuser: {str(e)}")


@admin_app.delete("/remove-admin/{username}")
@admin_limiter.limit("10/minute")
def remove_admin_user(request: Request, username: str, current_user: dict = Depends(admin_required)):
    """Remove a user from admin list (revoke superuser)."""
    try:
        # Find user by username
        user_id = None
        for uid, user in user_manager.users.items():
            if user["username"].lower() == username.lower():
                user_id = uid
                break
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Revoke superuser
        user_manager.set_superuser(user_id, False)
        
        log_security_event("SUPERUSER_REVOKED", {
            "removed_superuser": username,
            "admin": current_user["username"]
        })
        
        return {
            "message": f"Superuser privileges revoked for {username}",
            "username": username,
            "is_superuser": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing superuser: {str(e)}")


# Batch prediction endpoints
@admin_app.post("/batch/predict")
@admin_limiter.limit("10/minute")
def run_batch_prediction(request: Request, force_refresh: bool = False, current_user: dict = Depends(admin_required)):
    """Run batch prediction for all assets."""
    try:
        result = batch_prediction.run_batch_prediction(force_refresh=force_refresh)
        log_security_event("BATCH_PREDICTION_RUN", {
            "force_refresh": force_refresh,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running batch prediction: {str(e)}")


@admin_app.get("/batch/status")
@admin_limiter.limit("30/minute")
def get_batch_status(request: Request, current_user: dict = Depends(admin_required)):
    """Get batch prediction status."""
    try:
        status = batch_prediction.get_batch_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting batch status: {str(e)}")


@admin_app.get("/batch/asset/{symbol:path}")
@admin_limiter.limit("30/minute")
def get_asset_batch_prediction(request: Request, symbol: str, current_user: dict = Depends(admin_required)):
    """Get batch prediction for a specific asset."""
    try:
        prediction = batch_prediction.get_asset_prediction(symbol)
        if prediction:
            return prediction
        else:
            raise HTTPException(status_code=404, detail="No batch prediction found for this symbol")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting asset prediction: {str(e)}")


@admin_app.get("/users")
@admin_limiter.limit("30/minute")
def list_all_users(request: Request, current_user: dict = Depends(admin_required)):
    """List all users (admin-only)."""
    try:
        users = user_manager.list_users()
        return {
            "users": users,
            "total": len(users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")


@admin_app.put("/user/{username}/subscription")
@admin_limiter.limit("10/minute")
def update_user_subscription_admin(request: Request, username: str, plan: str, duration_days: int = 30, current_user: dict = Depends(admin_required)):
    """Update user subscription (admin-only)."""
    try:
        # Find user by username
        user_id = None
        for uid, user in user_manager.users.items():
            if user["username"].lower() == username.lower():
                user_id = uid
                break
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update subscription
        subscription = user_manager.update_subscription(user_id, plan, duration_days)
        
        log_security_event("SUBSCRIPTION_UPDATED_ADMIN", {
            "target_user": username,
            "new_plan": plan,
            "duration_days": duration_days,
            "admin": current_user["username"]
        })
        
        return {
            "message": f"Subscription updated for {username}",
            "subscription": subscription
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating subscription: {str(e)}")


@admin_app.put("/user/{username}/enable")
@admin_limiter.limit("10/minute")
def enable_user_account(request: Request, username: str, current_user: dict = Depends(admin_required)):
    """Enable a user account (admin-only)."""
    try:
        # Find user by username
        user_id = None
        for uid, user in user_manager.users.items():
            if user["username"].lower() == username.lower():
                user_id = uid
                break
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Enable user
        user_manager.enable_user(user_id)
        
        log_security_event("USER_ENABLED_ADMIN", {
            "target_user": username,
            "admin": current_user["username"]
        })
        
        return {
            "message": f"User {username} has been enabled",
            "username": username,
            "is_active": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enabling user: {str(e)}")


@admin_app.put("/user/{username}/disable")
@admin_limiter.limit("10/minute")
def disable_user_account(request: Request, username: str, current_user: dict = Depends(admin_required)):
    """Disable a user account (admin-only)."""
    try:
        # Find user by username
        user_id = None
        for uid, user in user_manager.users.items():
            if user["username"].lower() == username.lower():
                user_id = uid
                break
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Disable user
        user_manager.disable_user(user_id)
        
        log_security_event("USER_DISABLED_ADMIN", {
            "target_user": username,
            "admin": current_user["username"]
        })
        
        return {
            "message": f"User {username} has been disabled",
            "username": username,
            "is_active": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disabling user: {str(e)}")


# Health check endpoint
@admin_app.get("/health")
def health_check():
    """Health check endpoint for admin service."""
    return {
        "status": "healthy",
        "service": "market-predictor-admin",
        "timestamp": datetime.utcnow().isoformat()
    }