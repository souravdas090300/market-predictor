"""FastAPI server. Run with:  uvicorn app.api:app --reload"""
from __future__ import annotations

import time
import os
import sys
from typing import Optional, List
from datetime import datetime, timezone
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse, Response, FileResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..core import config, data
from ..services import material
from ..models import predict
from ..security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_token, sanitize_symbol, sanitize_text, validate_url, get_security_headers,
    log_security_event, api_key_manager, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES,
    AuthenticationError
)
from ..auth import UserManager, user_manager
from ..admin import admin_manager
from ..services import charts
from ..services import risk
from ..services import strategy
from ..services import news
from ..services import correlation
from ..services import batch_prediction
from ..services import backtesting
from ..services import advanced_sentiment
from ..services import trading_automation

# Import new phase-based routes
from ..routes import phase1_5_router, phase6_10_router, phase11_18_router


# Initialize admin user on startup (production only)
def ensure_admin_on_startup():
    """Ensure admin user exists on application startup."""
    try:
        admin_user = user_manager.get_user_by_username("admin")
        if not admin_user:
            if config.ENV == "production":
                # In production, create admin with secure password from env
                admin_password = os.getenv("ADMIN_PASSWORD", "admin12345")
                admin_user = user_manager.create_user(
                    username="admin",
                    email="admin@marketpredictor.com",
                    password=admin_password
                )
                user_manager.set_superuser(admin_user["user_id"], True)
                log_security_event("ADMIN_USER_CREATED", {
                    "user_id": admin_user["user_id"],
                    "username": "admin",
                    "setup_method": "startup_script"
                })
            else:
                # In development, create with default password
                admin_user = user_manager.create_user(
                    username="admin",
                    email="admin@marketpredictor.com",
                    password="admin12345"
                )
                user_manager.set_superuser(admin_user["user_id"], True)
        else:
            # Ensure existing admin has superuser privileges
            if not user_manager.is_superuser(admin_user["user_id"]):
                user_manager.set_superuser(admin_user["user_id"], True)
    except Exception as e:
        # Don't fail startup if admin creation fails
        log_security_event("ADMIN_SETUP_ERROR", {
            "error": str(e)
        })


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    ensure_admin_on_startup()
    yield
    # Shutdown (cleanup if needed)
    pass


# Initialize security components
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Market Predictor", version="1.0.0", lifespan=lifespan)

# Security middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS configuration
origins = config.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include new phase-based routes
app.include_router(phase1_5_router)
app.include_router(phase6_10_router)
app.include_router(phase11_18_router)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for header, value in get_security_headers().items():
        response.headers[header] = value
    return response

# Cache
_cache: dict[str, tuple[float, dict]] = {}


class MaterialIn(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    text: str = Field(max_length=20000)
    combine: bool = True
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        return sanitize_symbol(v)
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        return sanitize_text(v)


def _auto_signal(symbol: str, news: bool = True, refresh: bool = False) -> dict:
    sanitized_symbol = sanitize_symbol(symbol)
    key = f"{sanitized_symbol}|{news}"
    hit = _cache.get(key)
    if hit and not refresh and time.time() - hit[0] < config.API_CACHE_SECONDS:
        return hit[1]
    try:
        result = predict.get_signal(sanitized_symbol, use_news=news, retrain=refresh)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  # network errors, yfinance hiccups, etc.
        raise HTTPException(status_code=502, detail=f"Could not analyse {sanitized_symbol}: {e}")
    _cache[key] = (time.time(), result)
    return result


@app.get("/api/watchlist")
@limiter.limit("100/minute")
def watchlist(request: Request):
    return config.WATCHLIST


@app.get("/api/classes")
@limiter.limit("100/minute")
def classes(request: Request):
    return [{"key": k, "label": v, "hints": config.MATERIAL_HINTS.get(k, [])}
            for k, v in config.CLASS_LABELS.items()]


@app.get("/api/signal/{symbol:path}")
@limiter.limit("60/minute")
def signal(request: Request, symbol: str, news: bool = True, refresh: bool = False):
    """Automatic mode: prices, candlesticks, ML model and recent news."""
    sanitized_symbol = sanitize_symbol(symbol)
    return _auto_signal(sanitized_symbol, news, refresh)


@app.post("/api/material")
@limiter.limit("30/minute")
def read_material(request: Request, body: MaterialIn):
    """Material mode: read the user's own text, alone or combined with the automatic signal."""
    asset_class = config.asset_info(body.symbol)["class"]
    try:
        analysis = material.analyze(body.text, asset_class)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    auto = combined = None
    if body.combine:
        auto = _auto_signal(sanitize_symbol(body.symbol))
        combined = predict.combine(auto, analysis)
    return {
        "symbol": body.symbol,
        "asset_class": asset_class,
        "material": analysis,
        "auto": {"signal": auto["signal"], "probability_up": auto["probability_up"]} if auto else None,
        "combined": combined,
    }


@app.get("/api/quote/{symbol:path}")
@limiter.limit("120/minute")
def quote(request: Request, symbol: str):
    """Latest traded price. Independent of the daily prediction model."""
    q = data.get_live_quote(sanitize_symbol(symbol))
    if not q:
        raise HTTPException(status_code=502, detail=f"No live quote for {symbol}")
    return q


@app.get("/api/quotes")
@limiter.limit("60/minute")
def quotes(request: Request, symbols: str):
    """Live quotes for a comma-separated watchlist."""
    syms = [sanitize_symbol(s) for s in symbols.split(",") if s.strip()][:20]
    return data.get_quotes(syms)


@app.get("/api/live/quotes")
@limiter.limit("20/minute")
async def live_quotes_stream(request: Request, symbols: str):
    """Server-sent live quotes. Polls Yahoo on an interval; does not retrain."""
    import asyncio
    import json

    syms = [sanitize_symbol(s) for s in symbols.split(",") if s.strip()][:20]

    async def events():
        while True:
            if await request.is_disconnected():
                break
            payload = data.get_quotes(syms)
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(config.LIVE_STREAM_INTERVAL_SECONDS)

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/api/assets/all")
@limiter.limit("30/minute")
def get_all_assets(request: Request):
    """Get comprehensive data for all assets in the watchlist."""
    try:
        watchlist = config.WATCHLIST
        symbols = [asset["symbol"] for asset in watchlist]
        
        # Get live quotes for all symbols with error handling
        try:
            quotes = data.get_quotes(symbols)
        except Exception as e:
            print(f"Error fetching quotes: {e}")
            quotes = {symbol: None for symbol in symbols}
        
        # Combine watchlist info with live quotes
        assets_data = []
        for asset in watchlist:
            symbol = asset["symbol"]
            quote = quotes.get(symbol)
            
            asset_data = {
                "symbol": symbol,
                "name": asset["name"],
                "class": asset["class"],
                "query": asset.get("query", ""),
                "quote": quote,
                # Add fields that frontend might expect
                "price": quote.get("price", 0) if quote else 0,
                "change_pct": quote.get("change_pct", 0) if quote else 0,
                "volume": quote.get("volume", 0) if quote else 0,
                "high_24h": quote.get("high_24h", 0) if quote else 0,
                "low_24h": quote.get("low_24h", 0) if quote else 0,
                "market_cap": quote.get("market_cap") if quote else None,
                "last_update": quote.get("timestamp", datetime.now(timezone.utc).isoformat()) if quote else datetime.now(timezone.utc).isoformat()
            }
            assets_data.append(asset_data)
        
        return {
            "assets": assets_data,
            "total": len(assets_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching asset data: {str(e)}")


@app.get("/api/assets/by-class")
@limiter.limit("30/minute")
def get_assets_by_class(request: Request, asset_class: str):
    """Get assets filtered by class (stock, crypto, forex, commodity)."""
    try:
        if asset_class not in config.CLASS_LABELS:
            raise HTTPException(status_code=400, detail=f"Invalid asset class. Must be one of: {list(config.CLASS_LABELS.keys())}")
        
        watchlist = config.WATCHLIST
        filtered_assets = [asset for asset in watchlist if asset["class"] == asset_class]
        symbols = [asset["symbol"] for asset in filtered_assets]
        
        # Get live quotes for filtered symbols
        quotes = data.get_quotes(symbols)
        
        # Combine asset info with live quotes
        assets_data = []
        for asset in filtered_assets:
            symbol = asset["symbol"]
            quote = quotes.get(symbol)
            
            asset_data = {
                "symbol": symbol,
                "name": asset["name"],
                "class": asset["class"],
                "query": asset.get("query", ""),
                "quote": quote
            }
            assets_data.append(asset_data)
        
        return {
            "assets": assets_data,
            "class": asset_class,
            "class_label": config.CLASS_LABELS[asset_class],
            "total": len(assets_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching asset data: {str(e)}")


# Admin endpoints


# Admin-only dependency
def admin_required(current_user: dict = Depends(get_current_active_user)):
    """Dependency to check if user is admin (superuser)."""
    if not user_manager.is_superuser_by_username(current_user["username"]):
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user


# Admin authentication
class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class SubscriptionModeRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable subscription mode")


@app.post("/api/admin/auth/login")
@limiter.limit("10/minute")
def admin_login(request: Request, body: AdminLoginRequest):
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
            "is_superuser": True,
            "roles": user_data.get("roles", ["admin"])
        }
    }


# Admin configuration endpoints
@app.get("/api/admin/config")
@limiter.limit("30/minute")
def get_admin_config(request: Request, current_user: dict = Depends(admin_required)):
    """Get admin configuration."""
    try:
        return admin_manager.get_rate_limits()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting admin config: {str(e)}")


@app.post("/api/admin/rate-limiting")
@limiter.limit("10/minute")
def toggle_rate_limiting(request: Request, enabled: bool, current_user: dict = Depends(admin_required)):
    """Enable or disable rate limiting."""
    try:
        result = admin_manager.enable_rate_limiting(enabled)
        log_security_event("RATE_LIMITING_TOGGLED", {
            "enabled": enabled,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling rate limiting: {str(e)}")


@app.post("/api/admin/rate-limit/{endpoint}")
@limiter.limit("10/minute")
def update_rate_limit(request: Request, endpoint: str, limit: str, current_user: dict = Depends(admin_required)):
    """Update rate limit for a specific endpoint."""
    try:
        result = admin_manager.update_rate_limit(endpoint, limit)
        log_security_event("RATE_LIMIT_UPDATED", {
            "endpoint": endpoint,
            "new_limit": limit,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rate limit: {str(e)}")


@app.post("/api/admin/maintenance")
@limiter.limit("10/minute")
def toggle_maintenance(request: Request, enabled: bool, current_user: dict = Depends(admin_required)):
    """Enable or disable maintenance mode."""
    try:
        result = admin_manager.set_maintenance_mode(enabled)
        log_security_event("MAINTENANCE_TOGGLED", {
            "enabled": enabled,
            "admin": current_user["username"]
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling maintenance mode: {str(e)}")


@app.get("/api/admin/subscription-mode")
@limiter.limit("30/minute")
def get_subscription_mode(request: Request, current_user: dict = Depends(admin_required)):
    """Get subscription mode status (admin-only)."""
    try:
        return {
            "subscription_mode_enabled": config.SUBSCRIPTION_MODE_ENABLED
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting subscription mode: {str(e)}")


@app.post("/api/admin/subscription-mode")
@limiter.limit("10/minute")
def toggle_subscription_mode(request: Request, body: SubscriptionModeRequest, current_user: dict = Depends(admin_required)):
    """Enable or disable subscription mode (admin-only)."""
    try:
        # Update the environment variable in the config
        config.SUBSCRIPTION_MODE_ENABLED = body.enabled
        
        log_security_event("SUBSCRIPTION_MODE_TOGGLED", {
            "enabled": body.enabled,
            "admin": current_user["username"]
        })
        
        return {
            "message": f"Subscription mode {'enabled' if body.enabled else 'disabled'}",
            "subscription_mode_enabled": body.enabled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling subscription mode: {str(e)}")


@app.get("/api/admin/stats")
@limiter.limit("30/minute")
def get_system_stats(request: Request, current_user: dict = Depends(admin_required)):
    """Get system statistics."""
    try:
        stats = admin_manager.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")


@app.post("/api/admin/add-admin/{username}")
@limiter.limit("10/minute")
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


# Temporary setup endpoint for initial admin setup (remove after first use)
class SetupAdminRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)

@app.post("/api/setup-initial-admin")
@limiter.limit("5/hour")
def setup_initial_admin(request: Request, body: SetupAdminRequest):
    """Setup initial admin user - for one-time use only."""
    try:
        # Authenticate the user
        user_data = user_manager.authenticate_user(body.username, body.password)
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if there are any existing superusers
        existing_superusers = [u for u in user_manager.users.values() if u.get("is_superuser", False)]
        
        if existing_superusers:
            raise HTTPException(status_code=403, detail="Admin already exists - use regular admin promotion")
        
        # Set as superuser
        user_manager.set_superuser(user_data["user_id"], True)
        
        log_security_event("INITIAL_ADMIN_SETUP", {
            "username": body.username,
            "ip": request.client.host
        })
        
        return {
            "message": f"Initial admin '{body.username}' setup successfully",
            "username": body.username,
            "is_superuser": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up initial admin: {str(e)}")


@app.delete("/api/admin/remove-admin/{username}")
@limiter.limit("10/minute")
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


@app.get("/api/admin/users")
@limiter.limit("30/minute")
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


@app.put("/api/admin/user/{username}/subscription")
@limiter.limit("10/minute")
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


@app.put("/api/admin/user/{username}/enable")
@limiter.limit("10/minute")
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


@app.put("/api/admin/user/{username}/disable")
@limiter.limit("10/minute")
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


# Phase 10: Asset Predictions endpoints
@app.get("/api/predictions/assets")
@limiter.limit("30/minute")
def get_assets_list(request: Request):
    """Get list of all assets with current prices and changes."""
    try:
        watchlist = config.WATCHLIST
        symbols = [asset["symbol"] for asset in watchlist]
        
        # Get live quotes for all symbols with error handling
        try:
            quotes = data.get_quotes(symbols)
        except Exception as e:
            print(f"Error fetching quotes for assets list: {e}")
            quotes = {symbol: None for symbol in symbols}
        
        # Combine watchlist info with live quotes
        assets_data = []
        for asset in watchlist:
            symbol = asset["symbol"]
            quote = quotes.get(symbol)
            
            if quote:
                assets_data.append({
                    "symbol": symbol,
                    "name": asset["name"],
                    "class": asset["class"],
                    "price": quote.get("price", 0),
                    "change_pct": quote.get("change_pct", 0),
                    "volume": quote.get("volume", 0),
                    "high_24h": quote.get("high_24h", 0),
                    "low_24h": quote.get("low_24h", 0),
                    "market_cap": quote.get("market_cap"),
                    "last_update": quote.get("timestamp", datetime.now(timezone.utc).isoformat())
                })
            else:
                # Include asset even if quote is not available
                assets_data.append({
                    "symbol": symbol,
                    "name": asset["name"],
                    "class": asset["class"],
                    "price": 0,
                    "change_pct": 0,
                    "volume": 0,
                    "high_24h": 0,
                    "low_24h": 0,
                    "market_cap": None,
                    "last_update": datetime.now(timezone.utc).isoformat()
                })
        
        return {
            "assets": assets_data,
            "total": len(assets_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assets list: {str(e)}")


@app.get("/api/predictions/assets/{symbol:path}")
@limiter.limit("30/minute")
def get_asset_details(request: Request, symbol: str):
    """Get detailed information for a specific asset."""
    try:
        sanitized_symbol = sanitize_symbol(symbol)
        
        # Find asset in watchlist
        asset_info = None
        for asset in config.WATCHLIST:
            if asset["symbol"] == sanitized_symbol:
                asset_info = asset
                break
        
        if not asset_info:
            raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")
        
        # Get live quote
        quote = data.get_live_quote(sanitized_symbol)
        
        if not quote:
            raise HTTPException(status_code=502, detail=f"No live quote for {symbol}")
        
        return {
            "symbol": asset_info["symbol"],
            "name": asset_info["name"],
            "class": asset_info["class"],
            "price": quote.get("price", 0),
            "change_pct": quote.get("change_pct", 0),
            "volume": quote.get("volume", 0),
            "high_24h": quote.get("high_24h", 0),
            "low_24h": quote.get("low_24h", 0),
            "market_cap": quote.get("market_cap"),
            "last_update": quote.get("timestamp", datetime.now(timezone.utc).isoformat())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching asset details: {str(e)}")


@app.get("/api/predictions/{symbol}")
@limiter.limit("30/minute")
def get_asset_predictions(request: Request, symbol: str, timeframe: str = "1d"):
    """Get AI price predictions for a specific asset."""
    try:
        # Sanitize symbol
        sanitized_symbol = symbol.strip().upper()
        
        # Validate timeframe
        valid_timeframes = ["1h", "2h", "3h", "4h", "5h", "6h", "8h", "12h", "1d", "1w", "1m", "3m"]
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe. Must be one of: {valid_timeframes}")
        
        # Check if symbol exists in watchlist
        if sanitized_symbol not in config._BY_SYMBOL:
            raise HTTPException(status_code=404, detail=f"Symbol {sanitized_symbol} not found in watchlist")
        
        # Get current signal data with error handling
        try:
            signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        except HTTPException:
            raise
        except Exception as e:
            # Fallback to basic prediction if signal generation fails
            signal_data = {
                "signal": "neutral",
                "probability_up": 0.5,
                "conviction": 0.0,
                "candles": []
            }
        
        # Get current price with fallback
        quote = data.get_live_quote(sanitized_symbol)
        if quote and quote.get("price"):
            current_price = quote.get("price", 0)
        elif signal_data.get("candles") and len(signal_data["candles"]) > 0:
            current_price = signal_data["candles"][-1].get("c", 0)
        else:
            # Use a default price if everything fails
            current_price = 0
        
        # Handle case where we don't have a valid price
        if current_price <= 0:
            # Try to get a fallback price from watchlist or use a reasonable default
            asset_info = config.asset_info(sanitized_symbol)
            # For crypto, use a reasonable default based on the asset
            if asset_info["class"] == "crypto":
                current_price = 1000.0 if "BTC" in sanitized_symbol else 100.0
            else:
                current_price = 100.0
        
        # Generate prediction based on signal and timeframe
        # This is a simplified prediction logic - in production, use your ML model
        timeframe_multiplier = {
            "1h": 0.001,
            "2h": 0.002,
            "3h": 0.0025,
            "4h": 0.003,
            "5h": 0.0035,
            "6h": 0.004,
            "8h": 0.005,
            "12h": 0.007,
            "1d": 0.01,
            "1w": 0.03,
            "1m": 0.08,
            "3m": 0.15
        }.get(timeframe, 0.01)
        
        # Use signal probability to determine trend
        probability_up = signal_data.get("probability_up", 0.5)
        signal_bias = (probability_up - 0.5) * 2  # -1 to 1
        
        predicted_change = signal_bias * timeframe_multiplier
        predicted_price = current_price * (1 + predicted_change)
        
        confidence = int(75 + abs(signal_bias) * 20)  # 75-95% confidence based on signal strength
        trend = "bullish" if predicted_change > 0.005 else "bearish" if predicted_change < -0.005 else "neutral"
        
        confidence_range = current_price * timeframe_multiplier * 0.5
        
        return {
            "symbol": sanitized_symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "predicted_change_pct": predicted_change * 100,
            "confidence": confidence,
            "confidence_interval": {
                "low": predicted_price - confidence_range,
                "high": predicted_price + confidence_range
            },
            "expected_high": predicted_price + confidence_range * 0.7,
            "expected_low": predicted_price - confidence_range * 0.7,
            "expected_average": predicted_price,
            "trend": trend,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signal_data": {
                "signal": signal_data.get("signal"),
                "probability_up": signal_data.get("probability_up"),
                "conviction": signal_data.get("conviction")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        error_detail = f"Error generating prediction for {symbol}: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")


@app.get("/api/predictions/assets/{symbol:path}/historical")
@limiter.limit("30/minute")
def get_asset_historical(request: Request, symbol: str, timeframe: str = "1d", days: int = 30):
    """Get historical price data for a specific asset."""
    try:
        sanitized_symbol = sanitize_symbol(symbol)
        
        # Validate timeframe
        valid_timeframes = ["1h", "4h", "1d", "1w", "1m"]
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe. Must be one of: {valid_timeframes}")
        
        # Validate days
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
        
        # Get signal data which includes candlestick data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get("candles", [])
        
        # Process candlestick data into historical format
        historical_data = []
        for candle in candles[-days:]:  # Get last N days of data
            historical_data.append({
                "timestamp": candle.get("t", ""),
                "price": candle.get("c", 0),
                "volume": candle.get("v", 0),
                "open": candle.get("o", 0),
                "high": candle.get("h", 0),
                "low": candle.get("l", 0)
            })
        
        return {
            "symbol": sanitized_symbol,
            "timeframe": timeframe,
            "data": historical_data,
            "total": len(historical_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


@app.get("/api/predictions/compare")
@limiter.limit("20/minute")
def compare_assets(request: Request, symbols: str):
    """Compare predictions for multiple assets."""
    try:
        symbol_list = [sanitize_symbol(s) for s in symbols.split(",") if s.strip()][:10]  # Max 10 assets
        
        comparison_data = []
        for symbol in symbol_list:
            try:
                # Get asset details
                quote = data.get_live_quote(symbol)
                if not quote:
                    continue
                
                # Get predictions for all timeframes
                predictions = []
                for timeframe in ["1h", "4h", "1d", "1w", "1m", "3m"]:
                    try:
                        pred_response = get_asset_predictions(request, symbol, timeframe)
                        predictions.append({
                            "timeframe": timeframe,
                            "predicted_price": pred_response["predicted_price"],
                            "change_pct": pred_response["predicted_change_pct"]
                        })
                    except (KeyError, HTTPException, Exception):
                        continue
                
                # Find asset name
                asset_name = symbol
                for asset in config.WATCHLIST:
                    if asset["symbol"] == symbol:
                        asset_name = asset["name"]
                        break
                
                comparison_data.append({
                    "symbol": symbol,
                    "name": asset_name,
                    "current_price": quote.get("price", 0),
                    "predictions": predictions
                })
            except (KeyError, ValueError, Exception):
                continue
        
        return {
            "comparison": comparison_data,
            "total": len(comparison_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing assets: {str(e)}")


# Batch prediction endpoints (admin-only)
@app.post("/api/admin/batch/predict")
@limiter.limit("10/minute")
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


@app.get("/api/admin/batch/status")
@limiter.limit("30/minute")
def get_batch_status(request: Request, current_user: dict = Depends(admin_required)):
    """Get batch prediction status."""
    try:
        status = batch_prediction.get_batch_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting batch status: {str(e)}")


@app.get("/api/admin/batch/asset/{symbol:path}")
@limiter.limit("30/minute")
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


class MaterialWithSource(MaterialIn):
    source: str = "text"  # text, url, pdf, csv


@app.post("/api/material-from-url")
@limiter.limit("20/minute")
def material_from_url(request: Request, body: MaterialIn):
    """Fetch a URL and read it as material."""
    symbol = body.symbol
    url = body.text
    
    # Validate URL
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid or blocked URL")
    
    asset_class = config.asset_info(symbol)["class"]
    try:
        from ..core import fetcher
        result = fetcher.fetch_url(url)
        text = result["text"]
        analysis = material.analyze(text, asset_class)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    auto = combined = None
    if body.combine:
        auto = _auto_signal(sanitize_symbol(symbol))
        combined = predict.combine(auto, analysis)
    return {
        "symbol": symbol,
        "asset_class": asset_class,
        "source": "url",
        "material": analysis,
        "auto": {"signal": auto["signal"], "probability_up": auto["probability_up"]} if auto else None,
        "combined": combined,
    }


@app.post("/api/material-from-file")
@limiter.limit("10/minute")
def material_from_file(request: Request, symbol: str, file_bytes: bytes, file_type: str, combine: bool = True):
    """Upload PDF or CSV as material."""
    # Validate file size
    if len(file_bytes) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {config.MAX_UPLOAD_BYTES} bytes")
    
    asset_class = config.asset_info(symbol)["class"]
    try:
        from ..core import fetcher
        if file_type == "pdf":
            result = fetcher.extract_pdf(file_bytes)
        elif file_type == "csv":
            result = fetcher.extract_csv(file_bytes)
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        text = result["text"]
        analysis = material.analyze(text, asset_class)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    auto = combined = None
    if combine:
        auto = _auto_signal(sanitize_symbol(symbol))
        combined = predict.combine(auto, analysis)
    return {
        "symbol": symbol,
        "asset_class": asset_class,
        "source": file_type,
        "material": analysis,
        "auto": {"signal": auto["signal"], "probability_up": auto["probability_up"]} if auto else None,
        "combined": combined,
    }


@app.get("/api/signal/{symbol}/history")
@limiter.limit("60/minute")
def signal_history(request: Request, symbol: str, days: int = 90):
    """Signal history and metrics for a symbol."""
    from ..services import history as hist
    from ..services import metrics as metrics_mod
    entries = hist.get_history(symbol, days)
    return {"symbol": symbol, "entries": entries, "metrics": metrics_mod.metrics_from_history(symbol, days)}


@app.post("/api/bulk")
@limiter.limit("10/minute")
def bulk_signals(request: Request, symbols: list[str]):
    """Analyse up to 50 symbols in one request."""
    if len(symbols) > config.BULK_LIMIT:
        raise HTTPException(status_code=422, detail=f"Max {config.BULK_LIMIT} symbols at once")
    results = []
    for s in symbols:
        try:
            sanitized_symbol = sanitize_symbol(s)
            results.append(_auto_signal(sanitized_symbol, news=True))
        except HTTPException:
            results.append({"symbol": s, "error": "Could not fetch"})
    return results


@app.get("/api/export/{symbol}")
@limiter.limit("30/minute")
def export_signals(request: Request, symbol: str, format: str = "csv"):
    """Export signal history as CSV or JSON."""
    from ..services import history as hist
    entries = hist.get_history(symbol, days=config.HISTORY_KEEP_DAYS)
    if format == "csv":
        import csv
        from io import StringIO
        out = StringIO()
        if entries:
            w = csv.DictWriter(out, fieldnames=entries[0].keys())
            w.writeheader()
            w.writerows(entries)
        return {"data": out.getvalue(), "filename": f"{symbol}_signals.csv"}
    return {"data": entries, "filename": f"{symbol}_signals.json"}


@app.get("/api/portfolio")
@limiter.limit("30/minute")
def portfolio_metrics(request: Request, symbols: list[str]):
    """Aggregate metrics across a portfolio."""
    from ..services import metrics
    return metrics.portfolio_metrics(symbols)


@app.get("/api/chart/{symbol:path}")
@limiter.limit("60/minute")
def get_chart_data(request: Request, symbol: str, indicators: str = "ma,bollinger"):
    """Get enhanced chart data with technical indicators."""
    try:
        signal_data = _auto_signal(symbol, news=True, refresh=False)
        
        # Convert candles to DataFrame
        candles = signal_data.get('candles', [])
        if not candles:
            raise HTTPException(status_code=404, detail="No candle data available")
        
        import pandas as pd
        df = pd.DataFrame(candles)
        df.index = pd.to_datetime(df['d'])
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'})
        
        # Get patterns
        patterns = signal_data.get('candle_patterns', [])
        
        # Generate chart data
        chart_data = charts.generate_chart_data(symbol, df, patterns)
        
        return chart_data
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


class RiskRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    account_balance: float = Field(default=100000, gt=0)
    max_risk_percent: float = Field(default=2.0, ge=0.1, le=10.0)


@app.post("/api/risk/calculate")
@limiter.limit("30/minute")
def calculate_risk(request: Request, body: RiskRequest):
    """Calculate risk metrics for a trading position."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        risk_analysis = risk.calculate_position_risk(
            symbol=sanitized_symbol,
            entry_price=body.entry_price,
            stop_loss=body.stop_loss,
            take_profit=body.take_profit,
            account_balance=body.account_balance,
            max_risk_percent=body.max_risk_percent
        )
        return risk_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating risk: {str(e)}")


class StrategyRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_type: str = Field(default="momentum")
    lookback_min: int = Field(default=5, ge=1, le=50)
    lookback_max: int = Field(default=20, ge=1, le=100)
    holding_min: int = Field(default=1, ge=1, le=30)
    holding_max: int = Field(default=10, ge=1, le=60)


@app.post("/api/strategy/optimize")
@limiter.limit("20/minute")
def optimize_strategy(request: Request, body: StrategyRequest):
    """Optimize trading strategy parameters."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        import pandas as pd
        df = pd.DataFrame(candles)
        df.index = pd.to_datetime(df['d'])
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'})
        
        # Optimize strategy
        result = strategy.optimize_strategy_for_symbol(
            symbol=sanitized_symbol,
            data=df,
            strategy_type=body.strategy_type
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing strategy: {str(e)}")


class BacktestRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_type: str = Field(default="momentum")
    initial_capital: float = Field(default=100000, gt=0)
    commission: float = Field(default=0.001, ge=0, le=0.1)
    monte_carlo_iterations: int = Field(default=1000, ge=100, le=10000)
    run_stress_tests: bool = Field(default=True)
    run_monte_carlo: bool = Field(default=True)


class BacktestParameterOptimizationRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_type: str = Field(default="momentum")
    param_ranges: dict = Field(default={
        "lookback_period": [5, 10, 15, 20],
        "threshold": [0.01, 0.02, 0.03, 0.05]
    })
    initial_capital: float = Field(default=100000, gt=0)


class WalkForwardRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_type: str = Field(default="momentum")
    window_size: int = Field(default=100, ge=50, le=500)
    step_size: int = Field(default=20, ge=10, le=100)
    initial_capital: float = Field(default=100000, gt=0)


@app.post("/api/backtest/run")
@limiter.limit("10/minute")
async def run_backtest(request: Request, body: BacktestRequest):
    """Run comprehensive backtest with analysis."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        import pandas as pd
        df = pd.DataFrame(candles)
        df.index = pd.to_datetime(df['d'])
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'})
        df['timestamp'] = df.index
        
        # Select strategy
        if body.strategy_type == "momentum":
            strategy = backtesting.SimpleMomentumStrategy()
        elif body.strategy_type == "mean_reversion":
            strategy = backtesting.MeanReversionStrategy()
        else:
            strategy = backtesting.SimpleMomentumStrategy()
        
        # Run main backtest
        engine = backtesting.BacktestingEngine()
        main_metrics = await engine.run_backtest(
            df, strategy, body.initial_capital, body.commission
        )
        
        result = {
            'symbol': sanitized_symbol,
            'strategy_type': body.strategy_type,
            'main_metrics': {
                'total_return': main_metrics.total_return,
                'total_return_percent': main_metrics.total_return_percent,
                'sharpe_ratio': main_metrics.sharpe_ratio,
                'sortino_ratio': main_metrics.sortino_ratio,
                'max_drawdown': main_metrics.max_drawdown,
                'win_rate': main_metrics.win_rate,
                'profit_factor': main_metrics.profit_factor,
                'total_trades': main_metrics.total_trades,
                'avg_return': main_metrics.avg_return,
                'recovery_factor': main_metrics.recovery_factor,
                'equity_history': main_metrics.equity_history,
                'trades': [
                    {
                        'entry_date': t.entry_date.isoformat() if hasattr(t.entry_date, 'isoformat') else str(t.entry_date),
                        'exit_date': t.exit_date.isoformat() if hasattr(t.exit_date, 'isoformat') else str(t.exit_date),
                        'entry_price': t.entry_price,
                        'exit_price': t.exit_price,
                        'quantity': t.quantity,
                        'pnl': t.pnl,
                        'pnl_percent': t.pnl_percent,
                        'trade_type': t.trade_type
                    }
                    for t in main_metrics.trades
                ]
            }
        }
        
        # Run Monte Carlo simulation if requested
        if body.run_monte_carlo:
            monte_carlo_results = engine.monte_carlo_simulation(
                iterations=body.monte_carlo_iterations,
                initial_capital=body.initial_capital
            )
            result['monte_carlo'] = monte_carlo_results
        
        # Run stress tests if requested
        if body.run_stress_tests:
            stress_results = engine.stress_test(df, strategy, body.initial_capital)
            result['stress_tests'] = stress_results
        
        result['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running backtest: {str(e)}")


@app.post("/api/backtest/optimize")
@limiter.limit("5/minute")
async def optimize_backtest_parameters(request: Request, body: BacktestParameterOptimizationRequest):
    """Optimize strategy parameters using grid search."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        import pandas as pd
        df = pd.DataFrame(candles)
        df.index = pd.to_datetime(df['d'])
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'})
        df['timestamp'] = df.index
        
        # Select strategy
        if body.strategy_type == "momentum":
            strategy = backtesting.SimpleMomentumStrategy()
        elif body.strategy_type == "mean_reversion":
            strategy = backtesting.MeanReversionStrategy()
        else:
            strategy = backtesting.SimpleMomentumStrategy()
        
        # Run parameter optimization
        engine = backtesting.BacktestingEngine()
        optimization_results = await engine.optimize_parameters(
            df, strategy, body.param_ranges, body.initial_capital
        )
        
        return {
            'symbol': sanitized_symbol,
            'strategy_type': body.strategy_type,
            'optimization_results': optimization_results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing parameters: {str(e)}")


@app.post("/api/backtest/walk-forward")
@limiter.limit("5/minute")
async def run_walk_forward_analysis(request: Request, body: WalkForwardRequest):
    """Run walk-forward analysis for robust strategy testing."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        import pandas as pd
        df = pd.DataFrame(candles)
        df.index = pd.to_datetime(df['d'])
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'})
        df['timestamp'] = df.index
        
        # Select strategy
        if body.strategy_type == "momentum":
            strategy = backtesting.SimpleMomentumStrategy()
        elif body.strategy_type == "mean_reversion":
            strategy = backtesting.MeanReversionStrategy()
        else:
            strategy = backtesting.SimpleMomentumStrategy()
        
        # Run walk-forward analysis
        engine = backtesting.BacktestingEngine()
        walk_forward_results = await engine.walk_forward_analysis(
            df, strategy, body.window_size, body.step_size, body.initial_capital
        )
        
        return {
            'symbol': sanitized_symbol,
            'strategy_type': body.strategy_type,
            'walk_forward': walk_forward_results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running walk-forward analysis: {str(e)}")


class NewsRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    asset_class: str = Field(default="stock")
    max_articles: int = Field(default=20, ge=1, le=50)


@app.get("/api/news/{symbol:path}")
@limiter.limit("30/minute")
def get_news(request: Request, symbol: str, asset_class: str = "stock", max_articles: int = 20):
    """Get news with sentiment analysis for a symbol."""
    try:
        sanitized_symbol = sanitize_symbol(symbol)
        news_data = news.get_news_with_sentiment(sanitized_symbol, asset_class)
        return news_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")


class AdvancedSentimentRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    asset_class: str = Field(default="stock")
    include_social: bool = Field(default=True)
    include_fear_greed: bool = Field(default=True)


class SocialMediaSentimentRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    platform: str = Field(default="twitter")


class EarningsSentimentRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    transcript_text: str = Field(min_length=10, max_length=50000)


@app.post("/api/sentiment/advanced")
@limiter.limit("20/minute")
async def get_advanced_sentiment(request: Request, body: AdvancedSentimentRequest):
    """Get comprehensive sentiment analysis including news, social media, and fear/greed index."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        result = await advanced_sentiment.get_comprehensive_sentiment(
            symbol=sanitized_symbol,
            asset_class=body.asset_class,
            include_social=body.include_social,
            include_fear_greed=body.include_fear_greed
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")


@app.post("/api/sentiment/news")
@limiter.limit("30/minute")
async def get_news_sentiment(request: Request, body: AdvancedSentimentRequest):
    """Get detailed news sentiment analysis."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
        result = await analyzer.analyze_news_sentiment(
            symbol=sanitized_symbol,
            asset_class=body.asset_class
        )
        
        return {
            'symbol': result.symbol,
            'overall_sentiment': result.overall_sentiment,
            'sentiment_label': result.sentiment_label,
            'strength': result.strength,
            'bullish_count': result.bullish_count,
            'bearish_count': result.bearish_count,
            'neutral_count': result.neutral_count,
            'total_articles': result.total_articles,
            'impact_score': result.impact_score,
            'articles': [
                {
                    'headline': a.headline,
                    'source': a.source,
                    'sentiment': a.sentiment,
                    'relevance_score': a.relevance_score,
                    'published_at': a.published_at.isoformat() if hasattr(a.published_at, 'isoformat') else str(a.published_at)
                }
                for a in result.articles
            ],
            'timestamp': result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing news sentiment: {str(e)}")


@app.post("/api/sentiment/social")
@limiter.limit("20/minute")
async def get_social_sentiment(request: Request, body: SocialMediaSentimentRequest):
    """Get social media sentiment analysis."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
        result = await analyzer.analyze_social_media_sentiment(
            symbol=sanitized_symbol,
            platform=body.platform
        )
        
        return {
            'symbol': result.symbol,
            'platform': result.platform,
            'overall_sentiment': result.overall_sentiment,
            'sentiment_label': result.sentiment_label,
            'total_posts': result.total_posts,
            'bullish_count': result.bullish_count,
            'bearish_count': result.bearish_count,
            'total_engagement': result.total_engagement,
            'avg_engagement': result.avg_engagement,
            'top_posts': result.top_posts,
            'sentiment_trend': result.sentiment_trend,
            'virality': result.virality,
            'timestamp': result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing social sentiment: {str(e)}")


@app.get("/api/sentiment/fear-greed")
@limiter.limit("10/minute")
async def get_fear_greed_index(request: Request):
    """Get current Fear & Greed index with historical data."""
    try:
        analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
        result = await analyzer.calculate_fear_greed_index()
        
        return {
            'index': result.index,
            'classification': result.classification,
            'components': result.components,
            'history': result.history,
            'timestamp': result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating fear/greed index: {str(e)}")


@app.post("/api/sentiment/earnings")
@limiter.limit("10/minute")
async def get_earnings_sentiment(request: Request, body: EarningsSentimentRequest):
    """Analyze sentiment from earnings call transcripts."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        analyzer = advanced_sentiment.AdvancedSentimentAnalyzer()
        result = await analyzer.analyze_earnings_sentiment(
            symbol=sanitized_symbol,
            transcript_text=body.transcript_text
        )
        
        return {
            'symbol': result.symbol,
            'overall_sentiment': result.overall_sentiment,
            'sentiment_label': result.sentiment_label,
            'key_points': result.key_points,
            'confidence': result.confidence,
            'timestamp': result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing earnings sentiment: {str(e)}")


# ============================================================================
# PHASES 11-18: ADVANCED API ROUTES
# Backtesting, Trading Automation, Portfolio, ML, Social, Broker, Risk
# ============================================================================

# Request Models for Phase 11-18

class BacktestRunRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_name: str = Field(default="momentum")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = Field(default=100000, gt=0)
    commission: float = Field(default=0.001, ge=0, le=0.1)


class MonteCarloRequest(BaseModel):
    iterations: int = Field(default=1000, ge=100, le=10000)


class WalkForwardRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_name: str = Field(default="momentum")
    window_size: int = Field(default=100, ge=50, le=500)
    step_size: int = Field(default=20, ge=10, le=100)


class ParameterOptimizationRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    strategy_name: str = Field(default="momentum")
    param_ranges: Dict[str, List[float]]


class CreateAlertRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    alert_type: str = Field(default="price")
    price: float = Field(gt=0)
    condition: str = Field(default="above")
    notification_method: str = Field(default="email")


class ExecuteOrderRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(default="buy")
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    order_type: str = Field(default="market")


class LimitOrderRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(default="buy")
    quantity: float = Field(gt=0)
    limit_price: float = Field(gt=0)
    stop_price: Optional[float] = Field(default=None)


class PortfolioAnalyzeRequest(BaseModel):
    holdings: List[Dict[str, Any]]


class PortfolioRebalanceRequest(BaseModel):
    holdings: List[Dict[str, Any]]
    target_allocation: Dict[str, float]


class EfficientFrontierRequest(BaseModel):
    holdings: List[Dict[str, Any]]
    returns: List[float]
    covariance: List[List[float]]


class TaxLossHarvestingRequest(BaseModel):
    holdings: List[Dict[str, Any]]


class MLPredictionRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    timeframe: str = Field(default="1d")


class AnomalyDetectionRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)


class PatternRecognitionRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)


class PublishStrategyRequest(BaseModel):
    author: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    rules: Dict[str, Any]
    performance: Dict[str, Any]


class FollowStrategyRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=50)
    strategy_id: str = Field(min_length=1, max_length=50)
    allocation: float = Field(gt=0, le=1)


class RateStrategyRequest(BaseModel):
    strategy_id: str = Field(min_length=1, max_length=50)
    rating: float = Field(ge=1, le=5)
    review: str = Field(min_length=10, max_length=500)


class BrokerConnectRequest(BaseModel):
    broker_name: str = Field(default="alpaca")
    api_key: str = Field(min_length=10, max_length=100)
    api_secret: Optional[str] = Field(default=None)
    account_id: Optional[str] = Field(default=None)


class BrokerOrderRequest(BaseModel):
    broker_name: str = Field(default="alpaca")
    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(default="buy")
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    order_type: str = Field(default="limit")


class BrokerSyncRequest(BaseModel):
    broker_name: str = Field(default="alpaca")


class RiskLimitsRequest(BaseModel):
    max_position_size: float = Field(default=0.1, gt=0, le=1)
    max_daily_loss: float = Field(default=-0.05, ge=-1, le=0)
    max_drawdown: float = Field(default=-0.20, ge=-1, le=0)
    max_correlation: float = Field(default=0.8, gt=0, le=1)
    max_leverage: float = Field(default=2.0, gt=0, le=10)
    stop_loss_percent: float = Field(default=0.05, gt=0, le=1)


class VaRRequest(BaseModel):
    holdings: List[Dict[str, Any]]
    confidence: float = Field(default=0.95, ge=0.9, le=0.99)


class CVaRRequest(BaseModel):
    holdings: List[Dict[str, Any]]
    confidence: float = Field(default=0.95, ge=0.9, le=0.99)


class StressTestRequest(BaseModel):
    holdings: List[Dict[str, Any]]


class RiskMonitorRequest(BaseModel):
    holdings: List[Dict[str, Any]]
    market_prices: Dict[str, float]
    daily_pnl: float


class PositionCheckRequest(BaseModel):
    holdings: List[Dict[str, Any]]


# ============================================================================
# PHASE 11: BACKTESTING ROUTES
# ============================================================================

@app.post("/api/v2/backtest/run")
@limiter.limit("10/minute")
async def run_backtest_v2(request: Request, body: BacktestRunRequest):
    """Run backtest with given strategy."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(candles)
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
        
        # Convert to list of dicts
        historical_data = [
            {
                'timestamp': row['d'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row.get('volume', 0)
            }
            for _, row in df.iterrows()
        ]
        
        # Create strategy based on name
        if body.strategy_name == "momentum":
            strategy = backtesting.SimpleMomentumStrategy(lookback=10, threshold=0.02)
        elif body.strategy_name == "mean_reversion":
            strategy = backtesting.MeanReversionStrategy(lookback=20, threshold=0.02)
        else:
            strategy = backtesting.SimpleMomentumStrategy()
        
        # Run backtest
        engine = backtesting.BacktestingEngine()
        results = await engine.run_backtest(
            historical_data,
            strategy,
            initial_capital=body.initial_capital,
            commission=body.commission
        )
        
        return {
            "success": True,
            "results": {
                "total_return": results.total_return,
                "total_return_percent": results.total_return_percent,
                "sharpe_ratio": results.sharpe_ratio,
                "sortino_ratio": results.sortino_ratio,
                "max_drawdown": results.max_drawdown,
                "win_rate": results.win_rate,
                "profit_factor": results.profit_factor,
                "trades": results.trades,
                "avg_return": results.avg_return,
                "recovery_factor": results.recovery_factor
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running backtest: {str(e)}")


@app.post("/api/v2/backtest/monte-carlo")
@limiter.limit("5/minute")
def monte_carlo_simulation(request: Request, body: MonteCarloRequest):
    """Run Monte Carlo simulation."""
    try:
        engine = backtesting.BacktestingEngine()
        # Create sample trades for simulation
        engine.trades = [
            backtesting.Trade(
                entry_date=datetime.now(tz.utc) - timedelta(days=i),
                exit_date=datetime.now(tz.utc) - timedelta(days=i-1),
                entry_price=100 + random.uniform(-5, 5),
                exit_price=100 + random.uniform(-5, 5),
                quantity=10,
                pnl=random.uniform(-100, 100),
                pnl_percent=random.uniform(-10, 10),
                type="LONG"
            )
            for i in range(50)
        ]
        
        results = engine.monte_carlo_simulation(iterations=body.iterations)
        
        return {
            "success": True,
            "results": {
                "avg_final_equity": results.avg_final_equity,
                "avg_max_drawdown": results.avg_max_drawdown,
                "avg_return": results.avg_return,
                "worst_case": results.worst_case,
                "best_case": results.best_case,
                "simulations": results.simulations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Monte Carlo: {str(e)}")


@app.post("/api/v2/backtest/walk-forward")
@limiter.limit("5/minute")
async def walk_forward_analysis(request: Request, body: WalkForwardRequest):
    """Run walk-forward analysis."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(candles)
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
        
        historical_data = [
            {
                'timestamp': row['d'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row.get('volume', 0)
            }
            for _, row in df.iterrows()
        ]
        
        # Create strategy
        strategy = backtesting.SimpleMomentumStrategy()
        
        # Run walk-forward
        engine = backtesting.BacktestingEngine()
        results = await engine.walk_forward_analysis(
            historical_data,
            strategy,
            window_size=body.window_size,
            step_size=body.step_size
        )
        
        return {
            "success": True,
            "results": {
                "periods": results.periods,
                "avg_sharpe_ratio": results.avg_sharpe_ratio,
                "avg_return": results.avg_return,
                "consistency": results.consistency
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running walk-forward: {str(e)}")


@app.post("/api/v2/backtest/optimize")
@limiter.limit("5/minute")
async def optimize_parameters(request: Request, body: ParameterOptimizationRequest):
    """Optimize strategy parameters."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Get historical data
        signal_data = _auto_signal(sanitized_symbol, news=True, refresh=False)
        candles = signal_data.get('candles', [])
        
        if not candles:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(candles)
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
        
        historical_data = [
            {
                'timestamp': row['d'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row.get('volume', 0)
            }
            for _, row in df.iterrows()
        ]
        
        # Create strategy
        strategy = backtesting.SimpleMomentumStrategy()
        
        # Optimize parameters
        engine = backtesting.BacktestingEngine()
        results = await engine.optimize_parameters(
            historical_data,
            strategy,
            body.param_ranges
        )
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing parameters: {str(e)}")


# ============================================================================
# PHASE 12: SENTIMENT ANALYSIS ROUTES (v2)
# ============================================================================

@app.get("/api/v2/sentiment/news/{symbol}")
@limiter.limit("20/minute")
async def get_news_sentiment_v2(request: Request, symbol: str):
    """Get news sentiment for symbol."""
    try:
        sanitized_symbol = sanitize_symbol(symbol)
        sentiment = await advanced_sentiment.get_news_sentiment(sanitized_symbol)
        return {"success": True, "sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting news sentiment: {str(e)}")


@app.get("/api/v2/sentiment/social/{symbol}/{platform}")
@limiter.limit("20/minute")
async def get_social_sentiment_v2(request: Request, symbol: str, platform: str):
    """Get social media sentiment."""
    try:
        sanitized_symbol = sanitize_symbol(symbol)
        sentiment = await advanced_sentiment.get_social_sentiment(sanitized_symbol, platform)
        return {"success": True, "sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting social sentiment: {str(e)}")


@app.get("/api/v2/sentiment/fear-greed")
@limiter.limit("10/minute")
async def get_fear_greed_v2(request: Request):
    """Get fear and greed index."""
    try:
        index = await advanced_sentiment.get_fear_greed_index()
        return {"success": True, "index": index}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fear/greed index: {str(e)}")


@app.post("/api/v2/sentiment/earnings")
@limiter.limit("10/minute")
async def analyze_earnings_v2(request: Request, body: dict):
    """Analyze earnings transcript sentiment."""
    try:
        symbol = sanitize_symbol(body.get("symbol", ""))
        transcript = body.get("transcript", "")
        sentiment = await advanced_sentiment.analyze_earnings_sentiment(symbol, transcript)
        return {"success": True, "sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing earnings: {str(e)}")


# ============================================================================
# PHASE 13: ALERTS & AUTOMATION ROUTES
# ============================================================================

@app.post("/api/v2/alerts")
@limiter.limit("20/minute")
async def create_alert_v2(request: Request, body: CreateAlertRequest):
    """Create price/sentiment alert."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        alert = await trading_automation.trade_executor.create_alert(
            symbol=sanitized_symbol,
            alert_type=body.alert_type,
            price=body.price,
            condition=body.condition,
            notification_method=body.notification_method
        )
        return {
            "success": True,
            "alert": {
                "id": alert.id,
                "symbol": alert.symbol,
                "type": alert.type,
                "price": alert.price,
                "condition": alert.condition,
                "status": alert.status,
                "created_at": alert.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")


@app.post("/api/v2/orders/market")
@limiter.limit("30/minute")
async def execute_market_order_v2(request: Request, body: ExecuteOrderRequest):
    """Execute market order."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        result = await trading_automation.trade_executor.execute_market_order(
            symbol=sanitized_symbol,
            side=body.side,
            quantity=body.quantity,
            price=body.price
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing order: {str(e)}")


@app.post("/api/v2/orders/limit")
@limiter.limit("20/minute")
async def execute_limit_order_v2(request: Request, body: LimitOrderRequest):
    """Execute limit order."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        order = await trading_automation.trade_executor.execute_limit_order(
            symbol=sanitized_symbol,
            side=body.side,
            quantity=body.quantity,
            limit_price=body.limit_price,
            stop_price=body.stop_price
        )
        return {
            "success": True,
            "order": {
                "id": order.id,
                "symbol": order.symbol,
                "side": order.side,
                "type": order.type,
                "quantity": order.quantity,
                "limit_price": order.limit_price,
                "stop_price": order.stop_price,
                "status": order.status,
                "created_at": order.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing limit order: {str(e)}")


@app.delete("/api/v2/orders/{order_id}")
@limiter.limit("20/minute")
async def cancel_order_v2(request: Request, order_id: str):
    """Cancel order."""
    try:
        result = await trading_automation.trade_executor.cancel_order(order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling order: {str(e)}")


@app.get("/api/v2/execution-history")
@limiter.limit("30/minute")
def get_execution_history_v2(request: Request, symbol: Optional[str] = None, days: int = 30):
    """Get execution history."""
    try:
        sanitized_symbol = sanitize_symbol(symbol) if symbol else None
        history = trading_automation.trade_executor.get_execution_history(
            symbol=sanitized_symbol,
            days=days
        )
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


# ============================================================================
# PHASE 14: PORTFOLIO OPTIMIZATION ROUTES
# ============================================================================

@app.post("/api/v2/portfolio/analyze")
@limiter.limit("20/minute")
def analyze_portfolio_v2(request: Request, body: PortfolioAnalyzeRequest):
    """Analyze portfolio risk."""
    try:
        # Convert to Holding objects
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"],
                beta=h.get("beta", 1.0),
                hedged=h.get("hedged", False)
            )
            for h in body.holdings
        ]
        
        # Mock historical data
        historical_data = []
        for holding in holdings:
            for i in range(50):
                historical_data.append({
                    "symbol": holding.symbol,
                    "close": holding.current_price * (1 + random.uniform(-0.02, 0.02)),
                    "timestamp": (datetime.now(tz.utc) - timedelta(days=i)).isoformat()
                })
        
        risk_metrics = trading_automation.portfolio_optimizer.calculate_portfolio_risk(
            holdings, historical_data
        )
        
        return {
            "success": True,
            "risk_metrics": {
                "total_value": risk_metrics.total_value,
                "portfolio_volatility": risk_metrics.portfolio_volatility,
                "diversification_ratio": risk_metrics.diversification_ratio,
                "var95": risk_metrics.var95,
                "var99": risk_metrics.var99,
                "cvar95": risk_metrics.cvar95,
                "beta": risk_metrics.beta,
                "hedge_ratio": risk_metrics.hedge_ratio,
                "risk_assessment": risk_metrics.risk_assessment,
                "recommendations": risk_metrics.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")


@app.post("/api/v2/portfolio/rebalance")
@limiter.limit("10/minute")
def rebalance_portfolio_v2(request: Request, body: PortfolioRebalanceRequest):
    """Get rebalancing recommendations."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        rebalancing = trading_automation.portfolio_optimizer.rebalance_portfolio(
            holdings, body.target_allocation
        )
        return {"success": True, "rebalancing": rebalancing}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebalancing portfolio: {str(e)}")


@app.post("/api/v2/portfolio/efficient-frontier")
@limiter.limit("5/minute")
def efficient_frontier_v2(request: Request, body: EfficientFrontierRequest):
    """Calculate efficient frontier."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        import numpy as np
        covariance_array = np.array(body.covariance)
        frontier = trading_automation.portfolio_optimizer.calculate_efficient_frontier(
            holdings, body.returns, covariance_array
        )
        return {"success": True, "frontier": frontier}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating efficient frontier: {str(e)}")


@app.post("/api/v2/portfolio/tax-loss-harvesting")
@limiter.limit("10/minute")
def tax_loss_harvesting_v2(request: Request, body: TaxLossHarvestingRequest):
    """Get tax loss harvesting opportunities."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        opportunities = trading_automation.portfolio_optimizer.calculate_tax_loss_harvesting(holdings)
        return {"success": True, "opportunities": opportunities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating tax-loss harvesting: {str(e)}")


# ============================================================================
# PHASE 15: ML PREDICTIONS ROUTES
# ============================================================================

@app.post("/api/v2/predictions/ensemble")
@limiter.limit("15/minute")
async def ensemble_prediction_v2(request: Request, body: MLPredictionRequest):
    """Get ensemble ML prediction."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Mock historical data
        data = []
        for i in range(100):
            data.append({
                "close": 100 + random.uniform(-10, 10),
                "volume": random.randint(1000, 10000),
                "timestamp": (datetime.now(tz.utc) - timedelta(days=i)).isoformat()
            })
        
        prediction = await trading_automation.ml_prediction_engine.get_ensemble_prediction(
            sanitized_symbol, data, body.timeframe
        )
        
        return {
            "success": True,
            "prediction": {
                "ensemble_prediction": prediction.ensemble_prediction,
                "confidence": prediction.confidence,
                "model_predictions": {
                    model: {
                        "model": pred.model,
                        "price": pred.price,
                        "confidence": pred.confidence,
                        "reasoning": pred.reasoning
                    }
                    for model, pred in prediction.model_predictions.items()
                },
                "timestamp": prediction.timestamp.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ML prediction: {str(e)}")


@app.post("/api/v2/predictions/anomalies")
@limiter.limit("10/minute")
def detect_anomalies_v2(request: Request, body: AnomalyDetectionRequest):
    """Detect anomalies in price data."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Mock historical data
        data = []
        for i in range(100):
            data.append({
                "close": 100 + random.uniform(-10, 10),
                "timestamp": (datetime.now(tz.utc) - timedelta(days=i)).isoformat()
            })
        
        anomalies = trading_automation.ml_prediction_engine.detect_anomalies(data)
        
        return {
            "success": True,
            "anomalies": [
                {
                    "date": a.date,
                    "price": a.price,
                    "z_score": a.z_score,
                    "daily_return": a.daily_return,
                    "severity": a.severity
                }
                for a in anomalies
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")


@app.post("/api/v2/predictions/patterns")
@limiter.limit("10/minute")
def recognize_patterns_v2(request: Request, body: PatternRecognitionRequest):
    """Recognize chart patterns."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        
        # Mock historical data
        data = []
        for i in range(100):
            data.append({
                "close": 100 + random.uniform(-10, 10),
                "timestamp": (datetime.now(tz.utc) - timedelta(days=i)).isoformat()
            })
        
        patterns = trading_automation.ml_prediction_engine.recognize_patterns(data)
        
        return {
            "success": True,
            "patterns": [
                {
                    "pattern": p.pattern,
                    "bullish": p.bullish,
                    "confidence": p.confidence
                }
                for p in patterns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recognizing patterns: {str(e)}")


# ============================================================================
# PHASE 16: SOCIAL TRADING ROUTES
# ============================================================================

@app.post("/api/v2/social/strategies")
@limiter.limit("5/minute")
def publish_strategy_v2(request: Request, body: PublishStrategyRequest):
    """Publish strategy."""
    try:
        strategy = trading_automation.social_trading_platform.publish_strategy(
            author=body.author,
            name=body.name,
            description=body.description,
            rules=body.rules,
            performance=body.performance
        )
        
        return {
            "success": True,
            "strategy": {
                "id": strategy.id,
                "author": strategy.author,
                "name": strategy.name,
                "description": strategy.description,
                "followers": strategy.followers,
                "rating": strategy.rating,
                "created_at": strategy.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing strategy: {str(e)}")


@app.post("/api/v2/social/follow")
@limiter.limit("10/minute")
async def follow_strategy_v2(request: Request, body: FollowStrategyRequest):
    """Follow/copy strategy."""
    try:
        result = await trading_automation.social_trading_platform.follow_strategy(
            body.user_id, body.strategy_id, body.allocation
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error following strategy: {str(e)}")


@app.get("/api/v2/social/leaderboard")
@limiter.limit("30/minute")
def get_leaderboard_v2(request: Request):
    """Get strategy leaderboard."""
    try:
        leaderboard = trading_automation.social_trading_platform.generate_leaderboard()
        return {"success": True, "leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting leaderboard: {str(e)}")


@app.post("/api/v2/social/rate")
@limiter.limit("10/minute")
def rate_strategy_v2(request: Request, body: RateStrategyRequest):
    """Rate strategy."""
    try:
        result = trading_automation.social_trading_platform.rate_strategy(
            body.strategy_id, body.rating, body.review
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rating strategy: {str(e)}")


# ============================================================================
# PHASE 17: BROKER INTEGRATION ROUTES
# ============================================================================

@app.post("/api/v2/brokers/connect")
@limiter.limit("5/minute")
async def connect_broker_v2(request: Request, body: BrokerConnectRequest):
    """Connect to broker."""
    try:
        if body.broker_name.lower() == "alpaca":
            broker = await trading_automation.broker_integration.connect_alpaca(
                body.api_key, body.api_secret or ""
            )
        elif body.broker_name.lower() == "interactive brokers" or body.broker_name.lower() == "ib":
            broker = await trading_automation.broker_integration.connect_ib(
                body.account_id or "", body.api_key
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported broker")
        
        return {
            "success": True,
            "broker": {
                "name": broker.name,
                "connected": broker.connected,
                "assets": broker.assets,
                "features": broker.features
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to broker: {str(e)}")


@app.post("/api/v2/brokers/orders")
@limiter.limit("20/minute")
async def place_broker_order_v2(request: Request, body: BrokerOrderRequest):
    """Place order with broker."""
    try:
        sanitized_symbol = sanitize_symbol(body.symbol)
        result = await trading_automation.broker_integration.place_order(
            broker_name=body.broker_name,
            symbol=sanitized_symbol,
            side=body.side,
            quantity=body.quantity,
            price=body.price,
            order_type=body.order_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error placing broker order: {str(e)}")


@app.post("/api/v2/brokers/sync")
@limiter.limit("10/minute")
async def sync_broker_v2(request: Request, body: BrokerSyncRequest):
    """Sync broker account."""
    try:
        account = await trading_automation.broker_integration.sync_broker_account(body.broker_name)
        return {
            "success": True,
            "account": {
                "account_id": account.account_id,
                "broker": account.broker,
                "equity": round(account.equity, 2),
                "cash": round(account.cash, 2),
                "buying_power": round(account.buying_power, 2),
                "portfolio": account.portfolio,
                "synced_at": account.synced_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing broker account: {str(e)}")


@app.get("/api/v2/brokers/positions/{broker_name}")
@limiter.limit("10/minute")
def get_broker_positions_v2(request: Request, broker_name: str):
    """Get broker account positions."""
    try:
        positions = trading_automation.broker_integration.get_positions(broker_name)
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting positions: {str(e)}")


# ============================================================================
# PHASE 18: RISK MANAGEMENT ROUTES
# ============================================================================

@app.post("/api/v2/risk/limits")
@limiter.limit("10/minute")
def set_risk_limits_v2(request: Request, body: RiskLimitsRequest):
    """Set risk limits."""
    try:
        limits = trading_automation.risk_management.set_risk_limits(body.model_dump())
        return {
            "success": True,
            "limits": {
                "max_position_size": limits.max_position_size,
                "max_daily_loss": limits.max_daily_loss,
                "max_drawdown": limits.max_drawdown,
                "max_correlation": limits.max_correlation,
                "max_leverage": limits.max_leverage,
                "stop_loss_percent": limits.stop_loss_percent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting risk limits: {str(e)}")


@app.post("/api/v2/risk/var")
@limiter.limit("20/minute")
def calculate_var_v2(request: Request, body: VaRRequest):
    """Calculate Value at Risk."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        # Mock returns
        returns = [random.uniform(-0.05, 0.05) for _ in range(100)]
        
        var_result = trading_automation.risk_management.calculate_var(holdings, returns, body.confidence)
        
        return {
            "success": True,
            "var": {
                "confidence": var_result.confidence,
                "var_percent": var_result.var_percent,
                "var_amount": var_result.var_amount,
                "interpretation": var_result.interpretation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating VaR: {str(e)}")


@app.post("/api/v2/risk/cvar")
@limiter.limit("20/minute")
def calculate_cvar_v2(request: Request, body: CVaRRequest):
    """Calculate Conditional Value at Risk."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        # Mock returns
        returns = [random.uniform(-0.05, 0.05) for _ in range(100)]
        
        cvar_result = trading_automation.risk_management.calculate_cvar(holdings, returns, body.confidence)
        
        return {
            "success": True,
            "cvar": {
                "confidence": cvar_result.confidence,
                "cvar_percent": cvar_result.cvar_percent,
                "cvar_amount": cvar_result.cvar_amount,
                "worse_than_var": cvar_result.worse_than_var
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CVaR: {str(e)}")


@app.post("/api/v2/risk/stress-test")
@limiter.limit("10/minute")
def stress_test_v2(request: Request, body: StressTestRequest):
    """Run stress test scenarios."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        results = trading_automation.risk_management.stress_test_scenarios(holdings)
        
        return {
            "success": True,
            "scenarios": [
                {
                    "scenario": r.scenario,
                    "market_change": r.market_change,
                    "portfolio_value": r.portfolio_value,
                    "loss": r.loss,
                    "loss_percent": r.loss_percent
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running stress test: {str(e)}")


@app.post("/api/v2/risk/monitor")
@limiter.limit("30/minute")
def risk_monitor_v2(request: Request, body: RiskMonitorRequest):
    """Real-time risk monitoring."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        status = trading_automation.risk_management.monitor_real_time(
            holdings, body.market_prices, body.daily_pnl
        )
        
        return {
            "success": True,
            "status": {
                "risk_status": status["status"],
                "alerts": [
                    {
                        "type": alert.type,
                        "message": alert.message,
                        "action": alert.action
                    }
                    for alert in status["alerts"]
                ],
                "timestamp": status["timestamp"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error monitoring risk: {str(e)}")


@app.post("/api/v2/risk/position-check")
@limiter.limit("20/minute")
def position_check_v2(request: Request, body: PositionCheckRequest):
    """Check position sizing violations."""
    try:
        holdings = [
            trading_automation.Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                value=h["value"],
                purchase_price=h.get("purchase_price", h["current_price"]),
                current_price=h["current_price"]
            )
            for h in body.holdings
        ]
        
        violations = trading_automation.risk_management.check_position_sizing(holdings)
        return {"success": True, "violations": violations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking positions: {str(e)}")


class CorrelationRequest(BaseModel):
    symbols: List[str] = Field(min_length=2, max_length=20)


@app.post("/api/correlation/analyze")
@limiter.limit("20/minute")
def analyze_correlation(request: Request, body: CorrelationRequest):
    """Analyze correlations between multiple assets."""
    try:
        # Sanitize all symbols
        sanitized_symbols = [sanitize_symbol(s) for s in body.symbols]
        
        # Fetch data for all symbols
        data = {}
        for symbol in sanitized_symbols:
            try:
                signal_data = _auto_signal(symbol, news=True, refresh=False)
                candles = signal_data.get('candles', [])
                if candles:
                    import pandas as pd
                    df = pd.DataFrame(candles)
                    df.index = pd.to_datetime(df['d'])
                    df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close'})
                    data[symbol] = df
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                continue
        
        if len(data) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 assets with valid data")
        
        # Generate correlation data
        correlation_data = correlation.generate_correlation_data(sanitized_symbols, data)
        
        return correlation_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing correlation: {str(e)}")


# Security endpoints
class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=100)


class APIKeyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    scopes: list = Field(default=["read", "write"])


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)


class UpdateSubscriptionRequest(BaseModel):
    plan: str = Field(..., description="Subscription plan: free, basic, pro, enterprise")
    duration_days: int = Field(default=30, ge=1, le=365)


class OAuthCallbackRequest(BaseModel):
    provider: str = Field(..., description="OAuth provider: google, github, etc.")
    code: str = Field(..., description="OAuth authorization code")
    redirect_uri: str = Field(..., description="OAuth redirect URI")


@app.post("/api/auth/register")
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest):
    """Register a new user account."""
    try:
        user_data = user_manager.create_user(
            username=body.username,
            email=body.email,
            password=body.password
        )
        
        # Small delay to ensure data is persisted
        import time
        time.sleep(0.1)
        
        return {
            "message": "User registered successfully",
            "username": user_data["username"],
            "user_id": user_data["user_id"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest):
    """Authenticate user and return tokens."""
    # Authenticate user
    user_data = user_manager.authenticate_user(body.username, body.password)
    
    if not user_data:
        log_security_event("LOGIN_FAILED", {
            "username": body.username,
            "success": False
        })
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    if not user_data.get("is_active") or user_data.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Prevent admin users from using regular login - they must use admin login
    if user_manager.is_superuser_by_username(body.username):
        log_security_event("ADMIN_USER_REGULAR_LOGIN_ATTEMPT", {
            "username": body.username,
            "ip": request.client.host
        })
        raise HTTPException(
            status_code=403,
            detail="Admin users must use /api/admin/auth/login endpoint"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_data["username"]})
    refresh_token = create_refresh_token(data={"sub": user_data["username"]})
    
    # Log security event
    log_security_event("USER_LOGIN", {
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "success": True
    })
    
    # Determine primary role for frontend compatibility
    primary_role = "user"
    if user_data.get("is_superuser", False):
        primary_role = "superuser"
    elif "admin" in user_data.get("roles", []):
        primary_role = "admin"
    else:
        primary_role = user_data.get("roles", ["user"])[0] if user_data.get("roles") else "user"
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user_data["user_id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "role": primary_role,  # CRITICAL: Single role field for frontend
            "is_superuser": user_data.get("is_superuser", False),
            "roles": user_data.get("roles", ["user"])
        }
    }


@app.post("/api/auth/refresh")
@limiter.limit("20/minute")
def refresh_token(request: Request, refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new access token
        access_token = create_access_token(data={"sub": username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@app.post("/api/auth/api-key")
@limiter.limit("10/minute")
def create_api_key(request: Request, body: APIKeyRequest, current_user: dict = Depends(get_current_active_user)):
    """Create a new API key for the user."""
    username = current_user["username"]
    
    api_key = api_key_manager.generate_api_key(
        user_id=username,
        name=body.name,
        scopes=body.scopes
    )
    
    # Log security event
    log_security_event("API_KEY_CREATED", {
        "username": username,
        "key_name": body.name,
        "scopes": body.scopes
    })
    
    return {
        "api_key": api_key,
        "name": body.name,
        "scopes": body.scopes,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/auth/api-keys")
@limiter.limit("30/minute")
def list_api_keys(request: Request, current_user: dict = Depends(get_current_active_user)):
    """List all API keys for the current user."""
    username = current_user["username"]
    api_keys = api_key_manager.list_user_api_keys(username)
    
    return {
        "api_keys": api_keys,
        "count": len(api_keys)
    }


@app.delete("/api/auth/api-key/{key_id}")
@limiter.limit("20/minute")
def revoke_api_key(request: Request, key_id: str, current_user: dict = Depends(get_current_active_user)):
    """Revoke an API key."""
    username = current_user["username"]
    
    # In production, verify key belongs to user
    success = api_key_manager.revoke_api_key(key_id)
    
    if success:
        # Log security event
        log_security_event("API_KEY_REVOKED", {
            "username": username,
            "key_id": key_id
        })
        return {"message": "API key revoked successfully"}
    else:
        raise HTTPException(status_code=404, detail="API key not found")


@app.post("/api/auth/setup-admin")
@limiter.limit("1/hour")
def setup_admin_user(request: Request):
    """Setup admin user for production (one-time setup)."""
    try:
        # Check if admin already exists
        existing_admin = user_manager.get_user_by_username("admin")
        if existing_admin:
            return {
                "message": "Admin user already exists",
                "username": "admin",
                "email": existing_admin["email"]
            }
        
        # SECURITY: Don't allow creating admin via API in production
        # Admin should be created via environment variables or CLI
        if config.ENV == "production":
            raise HTTPException(
                status_code=403,
                detail="Admin creation via API is disabled in production. Use environment variables or CLI."
            )
        
        # Create admin user (development only)
        admin_data = user_manager.create_user(
            username="admin",
            email="admin@marketpredictor.local",
            password="admin123"
        )
        
        # Set as superuser
        user_manager.set_superuser(admin_data["user_id"], True)
        
        log_security_event("ADMIN_USER_CREATED", {
            "user_id": admin_data["user_id"],
            "username": "admin",
            "setup_method": "api_endpoint"
        })
        
        return {
            "message": "Admin user created successfully",
            "username": "admin",
            "email": "admin@marketpredictor.local",
            "user_id": admin_data["user_id"],
            "roles": admin_data["roles"],
            "is_superuser": admin_data["is_superuser"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admin user: {str(e)}")


@app.post("/api/auth/setup-demo")
@limiter.limit("1/hour")
def setup_demo_user(request: Request):
    """Setup demo user for testing (one-time setup)."""
    try:
        # Check if demo already exists
        existing_demo = user_manager.get_user_by_username("demo")
        if existing_demo:
            return {
                "message": "Demo user already exists",
                "username": "demo",
                "email": existing_demo["email"]
            }
        
        # SECURITY: Don't allow creating demo user via API in production
        if config.ENV == "production":
            raise HTTPException(
                status_code=403,
                detail="Demo user creation via API is disabled in production."
            )
        
        # Create demo user (development only)
        demo_data = user_manager.create_user(
            username="demo",
            email="demo@marketpredictor.local",
            password="demo12345"
        )
        
        log_security_event("DEMO_USER_CREATED", {
            "user_id": demo_data["user_id"],
            "username": "demo",
            "setup_method": "api_endpoint"
        })
        
        return {
            "message": "Demo user created successfully",
            "username": "demo",
            "email": "demo@marketpredictor.local",
            "user_id": demo_data["user_id"],
            "roles": demo_data["roles"],
            "is_superuser": demo_data["is_superuser"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating demo user: {str(e)}")


@app.get("/api/auth/me")
@limiter.limit("60/minute")
def get_current_user_info(request: Request, current_user: dict = Depends(get_current_active_user)):
    """Get current user information."""
    # Get full user data
    user = None
    for u in user_manager.users.values():
        if u["username"] == current_user["username"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription status
    subscription_status = user_manager.get_subscription_status(user["user_id"])
    
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "email_verified": user.get("email_verified", False),
        "created_at": user["created_at"],
        "last_login": user.get("last_login"),
        "is_superuser": user.get("is_superuser", False),
        "roles": user.get("roles", []),
        "preferences": user.get("preferences", {}),
        "profile": user.get("profile", {}),
        "subscription": subscription_status,
        "oauth_providers": list(user.get("oauth_providers", {}).keys()),
        "token_type": "access",
        "expires": current_user.get("exp")
    }


@app.put("/api/user/profile")
@limiter.limit("20/minute")
def update_user_profile(request: Request, body: UpdateProfileRequest, current_user: dict = Depends(get_current_active_user)):
    """Update user profile."""
    # Get user
    user = None
    for u in user_manager.users.values():
        if u["username"] == current_user["username"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update profile
    profile_data = {
        "first_name": body.first_name,
        "last_name": body.last_name,
        "bio": body.bio,
        "location": body.location,
        "website": body.website
    }
    
    success = user_manager.update_profile(user["user_id"], profile_data)
    
    if success:
        return {"message": "Profile updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update profile")


@app.get("/api/user/subscription")
@limiter.limit("30/minute")
def get_user_subscription(request: Request, current_user: dict = Depends(get_current_active_user)):
    """Get user subscription status."""
    # Get user
    user = None
    for u in user_manager.users.values():
        if u["username"] == current_user["username"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription = user_manager.get_subscription_status(user["user_id"])
    
    # Add subscription mode status to response
    subscription["subscription_mode_enabled"] = config.SUBSCRIPTION_MODE_ENABLED
    
    return subscription


@app.get("/api/user/features")
@limiter.limit("30/minute")
def get_user_features(request: Request, current_user: dict = Depends(get_current_active_user)):
    """Get user's available features based on subscription."""
    try:
        # Get user
        user = None
        for u in user_manager.users.values():
            if u["username"] == current_user["username"]:
                user = u
                break
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's subscription plan
        subscription = user_manager.get_subscription_status(user["user_id"])
        plan_str = subscription.get("plan", "free")
        
        try:
            from ..auth import SubscriptionPlan
            plan = SubscriptionPlan(plan_str)
        except ValueError:
            plan = SubscriptionPlan.FREE
        
        # Get effective plan (considering subscription mode)
        from ..admin.feature_limits import get_user_effective_plan, feature_limits_manager
        effective_plan = get_user_effective_plan(plan)
        
        # Get available features
        available_features = feature_limits_manager.get_available_features(effective_plan)
        user_limits = feature_limits_manager.get_user_limits(effective_plan)
        
        return {
            "subscription_mode_enabled": config.SUBSCRIPTION_MODE_ENABLED,
            "current_plan": plan_str,
            "effective_plan": effective_plan.value,
            "available_features": available_features,
            "limits": user_limits,
            "has_full_access": not config.SUBSCRIPTION_MODE_ENABLED
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user features: {str(e)}")


# Helper function for checking user feature access
def check_user_feature_access(feature: str, current_user: dict) -> bool:
    """Check if current user has access to a specific feature."""
    try:
        # If subscription mode is disabled, everyone has access
        if not config.SUBSCRIPTION_MODE_ENABLED:
            return True
        
        # Get user
        user = None
        for u in user_manager.users.values():
            if u["username"] == current_user["username"]:
                user = u
                break
        
        if not user:
            return False
        
        # Get user's subscription plan
        subscription = user_manager.get_subscription_status(user["user_id"])
        plan_str = subscription.get("plan", "free")
        
        try:
            from ..auth import SubscriptionPlan
            from ..admin.feature_limits import FeatureType, check_feature_access
            plan = SubscriptionPlan(plan_str)
            feature_type = FeatureType(feature)
            return check_feature_access(feature_type, plan)
        except (ValueError, KeyError):
            return False
    except Exception:
        return False


@app.put("/api/user/subscription")
@limiter.limit("10/minute")
def update_user_subscription(request: Request, body: UpdateSubscriptionRequest, current_user: dict = Depends(get_current_active_user)):
    """Update user subscription."""
    # Get user
    user = None
    for u in user_manager.users.values():
        if u["username"] == current_user["username"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate plan
    valid_plans = ["free", "basic", "pro", "enterprise"]
    if body.plan not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}")
    
    # Update subscription
    subscription = user_manager.update_subscription(user["user_id"], body.plan, body.duration_days)
    
    return {
        "message": "Subscription updated successfully",
        "subscription": subscription
    }


@app.post("/api/auth/oauth/callback")
@limiter.limit("10/minute")
def oauth_callback(request: Request, body: OAuthCallbackRequest):
    """Handle OAuth callback (placeholder for Google sign-up)."""
    # TODO: Implement actual OAuth flow with Google
    # This is a placeholder that simulates the OAuth flow
    
    # For now, return an error indicating not implemented
    raise HTTPException(
        status_code=501,
        detail="OAuth not yet implemented. Please use email/password registration."
    )


@app.get("/api/auth/oauth/google")
@limiter.limit("20/minute")
def google_oauth_redirect(request: Request):
    """Redirect to Google OAuth (placeholder)."""
    # TODO: Implement actual Google OAuth redirect
    raise HTTPException(
        status_code=501,
        detail="Google OAuth not yet implemented. Please use email/password registration."
    )


# Protected endpoint example
@app.get("/api/protected")
@limiter.limit("60/minute")
def protected_route(request: Request, current_user: dict = Depends(get_current_active_user)):
    """Example protected endpoint requiring authentication."""
    return {
        "message": "This is a protected endpoint",
        "user": current_user["username"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Health check and status endpoints
@app.get("/api/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "market-predictor-api"
    }





@app.get("/api/status")
@limiter.limit("30/minute")
def system_status(request: Request):
    """Comprehensive system status endpoint."""
    import psutil
    import time
    
    try:
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get service health (simulated - in production, check actual services)
        services = {
            "api": {"status": "up", "response_time": 45, "last_check": datetime.now(timezone.utc).isoformat()},
            "database": {"status": "up", "response_time": 12, "last_check": datetime.now(timezone.utc).isoformat()},
            "cache": {"status": "up", "response_time": 3, "last_check": datetime.now(timezone.utc).isoformat()},
            "ml_model": {"status": "up", "response_time": 234, "last_check": datetime.now(timezone.utc).isoformat()},
            "data_feed": {"status": "up", "response_time": 89, "last_check": datetime.now(timezone.utc).isoformat()},
        }
        
        # Calculate overall status
        all_up = all(s["status"] == "up" for s in services.values())
        overall = "healthy" if all_up else "degraded"
        
        return {
            "overall": overall,
            "uptime": 99.95,  # In production, calculate actual uptime
            "last_check": datetime.now(timezone.utc).isoformat(),
            "services": services,
            "metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "network_in": 1024,  # Simulated - use psutil.net_io_counters() in production
                "network_out": 512,
                "active_connections": 127,  # Track actual connections in production
                "requests_per_minute": 1450,  # Track actual requests in production
                "error_rate": 0.02,  # Track actual error rate in production
            },
            "incidents": [],  # Populate from incident tracking system
            "system_info": {
                "version": "1.0.0",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
            }
        }
    except Exception as e:
        return {
            "overall": "degraded",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Landing page route (main user-facing page)
@app.get("/")
async def landing_page():
    """Serve the landing page."""
    landing_path = config.ROOT / "static" / "landing.html"
    if landing_path.exists():
        return FileResponse(landing_path, media_type="text/html")
    return Response(status_code=404, content="Landing page not found")


# User dashboard route
@app.get("/dashboard")
async def dashboard_page():
    """Serve the user dashboard page."""
    dashboard_path = config.ROOT / "static" / "index.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    return Response(status_code=404, content="Dashboard page not found")


@app.get("/app")
async def app_page():
    """Serve the user dashboard page (alternate route)."""
    dashboard_path = config.ROOT / "static" / "index.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    return Response(status_code=404, content="Dashboard page not found")


@app.get("/assets")
async def assets_page():
    """Serve the assets page."""
    assets_path = config.ROOT / "static" / "assets.html"
    if assets_path.exists():
        return FileResponse(assets_path, media_type="text/html")
    return Response(status_code=404, content="Assets page not found")


@app.get("/profile")
async def profile_page():
    """Serve the profile page."""
    profile_path = config.ROOT / "static" / "profile.html"
    if profile_path.exists():
        return FileResponse(profile_path, media_type="text/html")
    return Response(status_code=404, content="Profile page not found")


# Admin page route (must be before static mount)
@app.get("/admin")
async def admin_page():
    """Serve the admin dashboard page."""
    admin_path = config.ROOT / "static" / "admin" / "index.html"
    if admin_path.exists():
        return FileResponse(admin_path, media_type="text/html")
    return Response(status_code=404, content="Admin page not found")


@app.get("/admin/")
async def admin_page_trailing():
    """Serve the admin dashboard page with trailing slash."""
    admin_path = config.ROOT / "static" / "admin" / "index.html"
    if admin_path.exists():
        return FileResponse(admin_path, media_type="text/html")
    return Response(status_code=404, content="Admin page not found")


@app.get("/auth/login")
async def login_page():
    """Serve the login page."""
    login_path = config.ROOT / "static" / "login.html"
    if login_path.exists():
        return FileResponse(login_path, media_type="text/html")
    return Response(status_code=404, content="Login page not found")


# Favicon endpoint to prevent 404/502 errors (must be before static mount)
@app.get("/favicon.ico")
async def favicon():
    """Return favicon to prevent browser errors."""
    favicon_path = config.ROOT / "static" / "market_predictor_favicon_32x32.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    # Return empty response if favicon doesn't exist
    return Response(status_code=204)


@app.get("/static/market_predictor_favicon_32x32.png")
async def favicon_png():
    """Return PNG favicon directly."""
    favicon_path = config.ROOT / "static" / "market_predictor_favicon_32x32.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    return Response(status_code=404)


# Static files (serves CSS, JS, images, etc. from /static/ path)
# Note: /admin, /, /dashboard are handled by specific routes above
app.mount("/static", StaticFiles(directory=str(config.ROOT / "static"), html=True), name="static")
