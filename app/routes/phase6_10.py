"""
Phase 6-10: Assets Library, Technical Indicators, Admin Features
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel, Field

router = APIRouter()

# Pydantic models for request bodies
class AssetComparisonRequest(BaseModel):
    symbols: list = Field(..., min_length=2, max_length=10)

class PerformanceComparisonRequest(BaseModel):
    symbols: list = Field(..., min_length=2, max_length=10)
    period: str = "1m"

class CustomIndicatorRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    indicator_type: str = Field(..., min_length=1, max_length=50)
    params: dict

class AdminSettingsRequest(BaseModel):
    settings: dict

class RateLimitUpdateRequest(BaseModel):
    limits: dict

# ============================================================================
# PHASE 6: ASSETS LIBRARY
# ============================================================================

@router.get("/api/assets")
def get_assets(category: str = None, search: str = None, skip: int = 0, limit: int = 50):
    """Get list of available assets"""
    from ..core import config
    
    # Get assets from config
    all_assets = []
    for idx, asset in enumerate(config.WATCHLIST):
        all_assets.append({
            "id": idx + 1,
            "symbol": asset["symbol"],
            "name": asset["name"],
            "category": asset["class"],
            "exchange": "various" if asset["class"] in ["crypto", "forex"] else "NASDAQ/NYSE"
        })
    
    if category:
        all_assets = [a for a in all_assets if a["category"] == category]
    if search:
        all_assets = [a for a in all_assets if search.lower() in a["symbol"].lower()]
    
    return {
        "assets": all_assets[skip:skip+limit],
        "total": len(all_assets)
    }

@router.get("/api/assets/all")
def get_all_assets():
    """Get all available assets without pagination"""
    from ..core import config
    
    all_assets = []
    for idx, asset in enumerate(config.WATCHLIST):
        all_assets.append({
            "id": idx + 1,
            "symbol": asset["symbol"],
            "name": asset["name"],
            "category": asset["class"],
            "query": asset["query"]
        })
    
    return {
        "assets": all_assets,
        "total": len(all_assets),
        "categories": {
            "stock": len([a for a in all_assets if a["category"] == "stock"]),
            "crypto": len([a for a in all_assets if a["category"] == "crypto"]),
            "forex": len([a for a in all_assets if a["category"] == "forex"]),
            "commodity": len([a for a in all_assets if a["category"] == "commodity"])
        }
    }

@router.get("/api/assets/search")
def search_assets(q: str = None, category: str = None, limit: int = 100):
    """Search assets by symbol or name"""
    from ..core import config
    
    all_assets = []
    for idx, asset in enumerate(config.WATCHLIST):
        all_assets.append({
            "id": idx + 1,
            "symbol": asset["symbol"],
            "name": asset["name"],
            "category": asset["class"],
            "query": asset["query"]
        })
    
    # Filter by search query
    if q:
        q_lower = q.lower()
        all_assets = [a for a in all_assets if q_lower in a["symbol"].lower() or q_lower in a["name"].lower()]
    
    # Filter by category
    if category and category != "all":
        all_assets = [a for a in all_assets if a["category"] == category]
    
    # Limit results
    all_assets = all_assets[:limit]
    
    return {
        "assets": all_assets,
        "total": len(all_assets),
        "query": q,
        "category": category
    }

@router.get("/api/assets/{symbol}")
def get_asset_details(symbol: str):
    """Get asset details"""
    return {
        "symbol": symbol,
        "name": f"{symbol} Details",
        "current_price": 150.00,
        "change_24h": 2.45,
        "change_percent_24h": 1.65,
        "volume_24h": 1000000,
        "market_cap": 2400000000,
        "pe_ratio": 28.5,
        "description": f"Detailed information about {symbol}"
    }

@router.get("/api/assets/{symbol}/price-history")
def get_price_history(symbol: str, days: int = 30):
    """Get historical prices"""
    return {
        "symbol": symbol,
        "period": f"last_{days}_days",
        "prices": [
            {
                "date": f"2024-01-{i:02d}",
                "open": 150 - i*0.5,
                "high": 152 - i*0.5,
                "low": 148 - i*0.5,
                "close": 151 - i*0.5,
                "volume": 1000000 + i*10000
            }
            for i in range(1, days + 1)
        ]
    }

# ============================================================================
# PHASE 7: TECHNICAL INDICATORS
# ============================================================================

@router.get("/api/technical-indicators/{symbol}")
def get_technical_indicators(symbol: str):
    """Get technical indicators"""
    return {
        "symbol": symbol,
        "indicators": {
            "sma_20": 149.50,
            "sma_50": 148.20,
            "ema_12": 151.30,
            "ema_26": 148.90,
            "rsi_14": 65.45,
            "macd": {"line": 2.40, "signal": 2.10, "histogram": 0.30},
            "bollinger_bands": {"upper": 155.20, "middle": 151.00, "lower": 146.80},
            "atr": 2.35,
            "adx": 28.5
        }
    }

@router.get("/api/technical-indicators/{symbol}/signals")
def get_indicator_signals(symbol: str):
    """Get buy/sell signals from indicators"""
    return {
        "symbol": symbol,
        "signals": {
            "moving_average_cross": "buy",
            "rsi_oversold": False,
            "rsi_overbought": True,
            "macd_cross": "sell",
            "bollinger_bands": "at_middle"
        },
        "overall_signal": "sell",
        "confidence": 0.78
    }

@router.post("/api/technical-indicators/calculate")
def calculate_custom_indicator(request: CustomIndicatorRequest):
    """Calculate custom indicator"""
    return {
        "symbol": request.symbol,
        "indicator": request.indicator_type,
        "params": request.params,
        "values": [100 + i for i in range(30)]
    }

# ============================================================================
# PHASE 8: EARNINGS CALENDAR
# ============================================================================

@router.get("/api/earnings-calendar")
def get_earnings_calendar(month: str = None):
    """Get earnings calendar"""
    return {
        "earnings": [
            {
                "symbol": "AAPL",
                "date": "2024-02-01",
                "time": "16:00 EST",
                "estimated_eps": 2.15,
                "previous_eps": 1.98,
                "surprise": "+8.6%"
            },
            {
                "symbol": "MSFT",
                "date": "2024-02-08",
                "time": "17:30 EST",
                "estimated_eps": 3.45,
                "previous_eps": 3.12,
                "surprise": "+10.6%"
            }
        ]
    }

@router.get("/api/earnings-calendar/{symbol}")
def get_symbol_earnings(symbol: str):
    """Get earnings history for symbol"""
    return {
        "symbol": symbol,
        "earnings_history": [
            {
                "date": "2023-11-01",
                "eps": 2.15,
                "revenue": "114.6B",
                "surprise": "+8.6%"
            }
        ]
    }

# ============================================================================
# PHASE 9: ASSET COMPARISON
# ============================================================================

@router.post("/api/asset-comparison")
def compare_assets(request: AssetComparisonRequest):
    """Compare multiple assets"""
    comparison = {}
    for symbol in request.symbols:
        comparison[symbol] = {
            "price": 150.00,
            "change_24h": 2.45,
            "volume": 1000000,
            "market_cap": 2400000000,
            "pe_ratio": 28.5 if symbol != "BTC" else None
        }
    return {"comparison": comparison}

@router.post("/api/asset-comparison/performance")
def compare_performance(request: PerformanceComparisonRequest):
    """Compare performance over period"""
    return {
        "period": request.period,
        "performance": {
            symbol: {"return": 0.05 + i*0.02, "volatility": 0.15 + i*0.02}
            for i, symbol in enumerate(request.symbols)
        }
    }

# ============================================================================
# PHASE 10: ADMIN DASHBOARD
# ============================================================================

@router.get("/api/admin/dashboard")
def get_admin_dashboard():
    """Get admin dashboard data"""
    return {
        "stats": {
            "total_users": 2547,
            "monthly_revenue": 48500,
            "uptime": 0.9942,
            "active_sessions": 1249
        },
        "recent_activity": [
            {"timestamp": "2024-01-02 14:30", "action": "User registered", "details": "john@example.com"},
            {"timestamp": "2024-01-02 13:15", "action": "Payment processed", "details": "$99.00"}
        ]
    }

@router.get("/api/admin/users")
def get_admin_users(skip: int = 0, limit: int = 50):
    """Get list of users"""
    return {
        "users": [
            {"id": 1, "username": "john_trader", "email": "john@example.com", "status": "active", "joined": "2024-01-15"},
            {"id": 2, "username": "sarah_invest", "email": "sarah@example.com", "status": "active", "joined": "2024-02-20"}
        ],
        "total": 2547
    }

@router.post("/api/admin/users/{user_id}/ban")
def ban_user(user_id: int):
    """Ban a user"""
    return {"success": True, "user_id": user_id, "status": "banned"}

@router.get("/api/admin/subscriptions")
def get_admin_subscriptions():
    """Get subscription statistics"""
    return {
        "stats": {
            "free": 1247,
            "professional": 847,
            "enterprise": 53,
            "churned": 142
        }
    }

@router.get("/api/admin/analytics")
def get_admin_analytics():
    """Get platform analytics"""
    return {
        "daily_active_users": 500,
        "daily_signals_generated": 15000,
        "avg_session_duration": 23.5,
        "bounce_rate": 0.15
    }

@router.get("/api/admin/audit-logs")
def get_audit_logs(skip: int = 0, limit: int = 50):
    """Get audit logs"""
    return {
        "logs": [
            {
                "timestamp": "2024-01-02 10:30",
                "action": "USER_BANNED",
                "admin": "admin",
                "details": "Banned user: spam_account"
            }
        ]
    }

@router.put("/api/admin/settings")
def update_admin_settings(request: AdminSettingsRequest):
    """Update admin settings"""
    return {"success": True, "settings": request.settings}

# ============================================================================
# PHASE 10: RATE LIMITING
# ============================================================================

@router.get("/api/admin/rate-limits")
def get_all_rate_limits():
    """Get rate limits for all users"""
    return {
        "rate_limits": [
            {"plan": "free", "requests_per_minute": 10, "daily_limit": 500},
            {"plan": "professional", "requests_per_minute": 100, "daily_limit": 50000},
            {"plan": "enterprise", "requests_per_minute": "unlimited", "daily_limit": "unlimited"}
        ]
    }

@router.put("/api/admin/rate-limits/{plan}")
def update_rate_limits(plan: str, request: RateLimitUpdateRequest):
    """Update rate limits for a plan"""
    return {"success": True, "plan": plan, "limits": request.limits}