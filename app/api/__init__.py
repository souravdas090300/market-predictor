"""FastAPI server. Run with:  uvicorn app.api:app --reload"""
from __future__ import annotations

import time
import os
import sys
from typing import Optional, List
from datetime import datetime

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
from ..services import charts
from ..services import risk
from ..services import strategy
from ..services import news
from ..services import correlation
from ..services import batch_prediction
from ..admin import admin_manager

# Initialize security components
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Market Predictor", version="1.0.0")

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
        
        # Get live quotes for all symbols
        quotes = data.get_quotes(symbols)
        
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
                "quote": quote
            }
            assets_data.append(asset_data)
        
        return {
            "assets": assets_data,
            "total": len(assets_data),
            "timestamp": datetime.utcnow().isoformat()
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
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching asset data: {str(e)}")


# Admin endpoints
from ..admin import admin_manager

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
            "is_superuser": True
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
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_data["username"]})
    refresh_token = create_refresh_token(data={"sub": user_data["username"]})
    
    # Log security event
    log_security_event("USER_LOGIN", {
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "success": True
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user_data["username"],
            "email": user_data["email"],
            "roles": user_data["roles"]
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
        "created_at": datetime.utcnow().isoformat()
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
    return subscription


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
        "timestamp": datetime.utcnow().isoformat()
    }


# Health check and status endpoints
@app.get("/api/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "market-predictor-api"
    }


# Favicon endpoint to prevent 404/502 errors
@app.get("/favicon.ico")
async def favicon():
    """Return favicon to prevent browser errors."""
    favicon_path = config.ROOT / "static" / "market_predictor_favicon_32x32.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    # Return empty response if favicon doesn't exist
    return Response(status_code=204)


@app.get("/market_predictor_favicon_32x32.png")
async def favicon_png():
    """Return PNG favicon directly."""
    favicon_path = config.ROOT / "static" / "market_predictor_favicon_32x32.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    return Response(status_code=404)


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
            "api": {"status": "up", "response_time": 45, "last_check": datetime.utcnow().isoformat()},
            "database": {"status": "up", "response_time": 12, "last_check": datetime.utcnow().isoformat()},
            "cache": {"status": "up", "response_time": 3, "last_check": datetime.utcnow().isoformat()},
            "ml_model": {"status": "up", "response_time": 234, "last_check": datetime.utcnow().isoformat()},
            "data_feed": {"status": "up", "response_time": 89, "last_check": datetime.utcnow().isoformat()},
        }
        
        # Calculate overall status
        all_up = all(s["status"] == "up" for s in services.values())
        overall = "healthy" if all_up else "degraded"
        
        return {
            "overall": overall,
            "uptime": 99.95,  # In production, calculate actual uptime
            "last_check": datetime.utcnow().isoformat(),
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
            "timestamp": datetime.utcnow().isoformat()
        }


# Favicon endpoint to prevent 404/502 errors (must be before static mount)
@app.get("/favicon.ico")
async def favicon():
    """Return favicon to prevent browser errors."""
    favicon_path = config.ROOT / "static" / "market_predictor_favicon_32x32.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    # Return empty response if favicon doesn't exist
    return Response(status_code=204)


@app.get("/market_predictor_favicon_32x32.png")
async def favicon_png():
    """Return PNG favicon directly."""
    favicon_path = config.ROOT / "static" / "market_predictor_favicon_32x32.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    return Response(status_code=404)


# Static files last so they cannot shadow /api routes.
app.mount("/admin", StaticFiles(directory=str(config.ROOT / "static" / "admin"), html=True), name="admin")
app.mount("/", StaticFiles(directory=str(config.ROOT / "static"), html=True), name="static")
