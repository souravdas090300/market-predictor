"""Assets Library - Live Prices & Prediction Accuracy"""
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import asyncio
import json
from enum import Enum

from ..core import config, data
from ..models import predict
from ..core import accuracy


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class AssetCategory(str, Enum):
    CRYPTO = "crypto"
    STOCK = "stock"
    FOREX = "forex"
    COMMODITY = "commodity"


class AssetSort(str, Enum):
    POPULAR = "popular"
    GAINERS = "gainers"
    LOSERS = "losers"
    NEW = "new"
    VOLUME = "volume"
    MARKET_CAP = "market_cap"


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/v2/assets", tags=["assets"])


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class PriceUpdateManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, symbol: str, websocket: WebSocket):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)
        print(f"WebSocket connected for {symbol}. Total connections: {len(self.active_connections.get(symbol, []))}")
    
    def disconnect(self, symbol: str, websocket: WebSocket):
        if symbol in self.active_connections:
            self.active_connections[symbol].remove(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
    
    async def broadcast_price_update(self, symbol: str, price_data: dict):
        """Broadcast price update to all connected clients for this symbol"""
        if symbol in self.active_connections:
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json({
                        "type": "price_update",
                        "symbol": symbol,
                        "data": price_data
                    })
                except Exception as e:
                    print(f"Error sending price update: {e}")


price_manager = PriceUpdateManager()


# ============================================================================
# 1. GET ASSETS LIST WITH FILTERING
# ============================================================================

@router.get("/list")
def get_assets_list(
    category: Optional[AssetCategory] = Query(None),
    sort_by: AssetSort = Query(AssetSort.POPULAR),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get assets list with real-time prices and filtering
    
    Query: /api/v2/assets/list?category=crypto&sort_by=gainers&limit=20
    """
    
    # Get assets by category from watchlist
    watchlist = config.WATCHLIST
    
    if category:
        watchlist = [asset for asset in watchlist if asset["class"] == category.value]
    
    # Limit to first 50 assets to avoid timeout
    watchlist = watchlist[:50]
    
    # Get live quotes for assets (with error handling)
    symbols = [asset["symbol"] for asset in watchlist]
    quotes = {}
    
    try:
        quotes = data.get_quotes(symbols)
    except Exception as e:
        print(f"Error fetching quotes: {e}")
        quotes = {}
    
    results = []
    
    for asset in watchlist:
        symbol = asset["symbol"]
        quote = quotes.get(symbol)
        
        # Include asset even if quote is not available
        if not quote:
            # Get prediction accuracy for this asset
            accuracy_data = accuracy.get_prediction_accuracy(symbol, timeframe="7d")
            
            results.append({
                "symbol": symbol,
                "name": asset["name"],
                "icon": get_asset_icon(asset["class"]),
                "category": asset["class"],
                
                # Price data (zeros if not available)
                "current_price": 0,
                "change_24h": 0,
                "change_percent_24h": 0,
                "high_24h": 0,
                "low_24h": 0,
                "volume_24h": 0,
                
                # Market data
                "market_cap": None,
                "apy": get_apy_for_asset(symbol, asset["class"]),
                
                # Prediction accuracy
                "prediction_accuracy": {
                    "lstm": accuracy_data.get("lstm_accuracy", 0),
                    "arima": accuracy_data.get("arima_accuracy", 0),
                    "xgboost": accuracy_data.get("xgboost_accuracy", 0),
                    "prophet": accuracy_data.get("prophet_accuracy", 0),
                    "ensemble": accuracy_data.get("ensemble_accuracy", 0)
                },
                
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            continue
        
        # Get prediction accuracy for this asset
        accuracy_data = accuracy.get_prediction_accuracy(symbol, timeframe="7d")
        
        results.append({
            "symbol": symbol,
            "name": asset["name"],
            "icon": get_asset_icon(asset["class"]),
            "category": asset["class"],
            
            # Price data
            "current_price": quote.get("price", 0),
            "change_24h": quote.get("change", 0),
            "change_percent_24h": quote.get("change_pct", 0),
            "high_24h": quote.get("day_high", 0),
            "low_24h": quote.get("day_low", 0),
            "volume_24h": quote.get("volume", 0),
            
            # Market data
            "market_cap": quote.get("market_cap"),
            "apy": get_apy_for_asset(symbol, asset["class"]),
            
            # Prediction accuracy
            "prediction_accuracy": {
                "lstm": accuracy_data.get("lstm_accuracy", 0),
                "arima": accuracy_data.get("arima_accuracy", 0),
                "xgboost": accuracy_data.get("xgboost_accuracy", 0),
                "prophet": accuracy_data.get("prophet_accuracy", 0),
                "ensemble": accuracy_data.get("ensemble_accuracy", 0)
            },
            
            "updated_at": quote.get("as_of", datetime.now(timezone.utc).isoformat())
        })
    
    # Sort
    if sort_by == AssetSort.GAINERS:
        results.sort(key=lambda x: x["change_percent_24h"], reverse=True)
    elif sort_by == AssetSort.LOSERS:
        results.sort(key=lambda x: x["change_percent_24h"])
    elif sort_by == AssetSort.VOLUME:
        results.sort(key=lambda x: x["volume_24h"] or 0, reverse=True)
    elif sort_by == AssetSort.MARKET_CAP:
        results.sort(key=lambda x: x["market_cap"] or 0, reverse=True)
    elif sort_by == AssetSort.NEW:
        results.sort(key=lambda x: x["updated_at"], reverse=True)
    else:  # POPULAR - use a simple popularity metric based on change
        results.sort(key=lambda x: abs(x["change_percent_24h"]), reverse=True)
    
    return {
        "category": category.value if category else "all",
        "sort_by": sort_by.value,
        "count": len(results),
        "assets": results[:limit]
    }


# ============================================================================
# 2. GET SINGLE ASSET DETAIL
# ============================================================================

@router.get("/detail/{symbol:path}")
def get_asset_detail(symbol: str):
    """
    Get detailed info for single asset including price history
    
    Query: /api/v2/assets/detail/BTC-USD
    """
    
    symbol = symbol.upper()
    
    # Find asset in watchlist
    asset_info = None
    for asset in config.WATCHLIST:
        if asset["symbol"] == symbol:
            asset_info = asset
            break
    
    if not asset_info:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get live price
    quote = data.get_live_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail="Price data not found")
    
    # Get price history for charts
    try:
        price_history = data.get_prices(symbol, period="5d")
        
        # Convert to chart data format
        chart_data_24h = []
        chart_data_7d = []
        chart_data_30d = []
        
        # 24h data (hourly if available, otherwise use daily)
        if len(price_history) >= 24:
            chart_data_24h = [
                {
                    "timestamp": idx.isoformat(),
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"]
                }
                for idx, row in price_history.tail(24).iterrows()
            ]
        
        # 7d data
        if len(price_history) >= 7:
            chart_data_7d = [
                {
                    "timestamp": idx.isoformat(),
                    "close": row["close"]
                }
                for idx, row in price_history.tail(7).iterrows()
            ]
        
        # 30d data
        if len(price_history) >= 30:
            chart_data_30d = [
                {
                    "timestamp": idx.isoformat(),
                    "close": row["close"]
                }
                for idx, row in price_history.tail(30).iterrows()
            ]
    except Exception as e:
        print(f"Error fetching price history: {e}")
        chart_data_24h = []
        chart_data_7d = []
        chart_data_30d = []
    
    # Get prediction accuracy for different timeframes
    accuracy_24h = accuracy.get_prediction_accuracy(symbol, timeframe="24h")
    accuracy_7d = accuracy.get_prediction_accuracy(symbol, timeframe="7d")
    accuracy_30d = accuracy.get_prediction_accuracy(symbol, timeframe="30d")
    
    return {
        "asset": {
            "symbol": asset_info["symbol"],
            "name": asset_info["name"],
            "icon": get_asset_icon(asset_info["class"]),
            "category": asset_info["class"],
            "decimals": get_decimals_for_asset(asset_info["class"])
        },
        
        "price": {
            "current": quote.get("price", 0),
            "bid": quote.get("price", 0) * 0.999,  # Simulated bid
            "ask": quote.get("price", 0) * 1.001,  # Simulated ask
            "spread": ((quote.get("price", 0) * 1.001 - quote.get("price", 0) * 0.999) / (quote.get("price", 0) * 0.999) * 100) if quote.get("price", 0) > 0 else 0
        },
        
        "change": {
            "change_24h_dollars": quote.get("change", 0),
            "change_24h_percent": quote.get("change_pct", 0),
            "high_24h": quote.get("day_high", 0),
            "low_24h": quote.get("day_low", 0)
        },
        
        "market": {
            "market_cap": quote.get("market_cap"),
            "volume_24h": quote.get("volume", 0),
            "circulating_supply": None,
            "apy": get_apy_for_asset(symbol, asset_info["class"])
        },
        
        "chart_data": {
            "interval_24h": chart_data_24h,
            "interval_7d": chart_data_7d,
            "interval_30d": chart_data_30d
        },
        
        "predictions": {
            "timeframe_24h": {
                "lstm_accuracy": accuracy_24h.get("lstm_accuracy", 0),
                "arima_accuracy": accuracy_24h.get("arima_accuracy", 0),
                "xgboost_accuracy": accuracy_24h.get("xgboost_accuracy", 0),
                "prophet_accuracy": accuracy_24h.get("prophet_accuracy", 0),
                "ensemble_accuracy": accuracy_24h.get("ensemble_accuracy", 0),
                "predictions_tested": accuracy_24h.get("predictions_tested", 0)
            },
            "timeframe_7d": {
                "lstm_accuracy": accuracy_7d.get("lstm_accuracy", 0),
                "arima_accuracy": accuracy_7d.get("arima_accuracy", 0),
                "xgboost_accuracy": accuracy_7d.get("xgboost_accuracy", 0),
                "prophet_accuracy": accuracy_7d.get("prophet_accuracy", 0),
                "ensemble_accuracy": accuracy_7d.get("ensemble_accuracy", 0),
                "predictions_tested": accuracy_7d.get("predictions_tested", 0)
            },
            "timeframe_30d": {
                "lstm_accuracy": accuracy_30d.get("lstm_accuracy", 0),
                "arima_accuracy": accuracy_30d.get("arima_accuracy", 0),
                "xgboost_accuracy": accuracy_30d.get("xgboost_accuracy", 0),
                "prophet_accuracy": accuracy_30d.get("prophet_accuracy", 0),
                "ensemble_accuracy": accuracy_30d.get("ensemble_accuracy", 0),
                "predictions_tested": accuracy_30d.get("predictions_tested", 0)
            }
        },
        
        "updated_at": quote.get("as_of", datetime.now(timezone.utc).isoformat())
    }


# ============================================================================
# 3. GET PRICE HISTORY FOR CHARTS
# ============================================================================

@router.get("/price-history/{symbol:path}")
def get_price_history(
    symbol: str,
    timeframe: str = Query("24h")  # 24h, 7d, 30d, 1y, all
):
    """
    Get price history for charting
    
    Query: /api/v2/assets/price-history/BTC-USD?timeframe=7d
    """
    
    symbol = symbol.upper()
    
    # Determine interval and days
    if timeframe == "24h":
        days = 1
    elif timeframe == "7d":
        days = 7
    elif timeframe == "30d":
        days = 30
    elif timeframe == "1y":
        days = 365
    else:  # all
        days = 3650
    
    try:
        price_history = data.get_prices(symbol, period=f"{days}d")
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "interval": "1d",
            "data": [
                {
                    "timestamp": idx.isoformat(),
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"]
                }
                for idx, row in price_history.iterrows()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Price history not found: {str(e)}")


# ============================================================================
# 4. WEBSOCKET - LIVE PRICE UPDATES
# ============================================================================

@router.websocket("/ws/price/{symbol:path}")
async def websocket_price_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket for live price updates
    
    ws://localhost:8000/api/v2/assets/ws/price/BTC-USD
    """
    
    symbol = symbol.upper()
    await price_manager.connect(symbol, websocket)
    
    try:
        while True:
            # Get current price
            quote = data.get_live_quote(symbol)
            
            if quote:
                await websocket.send_json({
                    "type": "price_update",
                    "symbol": symbol,
                    "current_price": quote.get("price", 0),
                    "bid": quote.get("price", 0) * 0.999,
                    "ask": quote.get("price", 0) * 1.001,
                    "change_24h": quote.get("change", 0),
                    "change_percent_24h": quote.get("change_pct", 0),
                    "volume_24h": quote.get("volume", 0),
                    "timestamp": quote.get("as_of", datetime.now(timezone.utc).isoformat())
                })
            
            # Update every 5 seconds
            await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        price_manager.disconnect(symbol, websocket)
    except Exception as e:
        print(f"WebSocket error for {symbol}: {e}")
        price_manager.disconnect(symbol, websocket)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_asset_icon(asset_class: str) -> str:
    """Get icon for asset class"""
    icons = {
        "crypto": "₿",
        "stock": "📈",
        "forex": "💱",
        "commodity": "🪙"
    }
    return icons.get(asset_class, "📊")


def get_decimals_for_asset(asset_class: str) -> int:
    """Get decimal places for asset class"""
    decimals = {
        "crypto": 2,
        "stock": 2,
        "forex": 4,
        "commodity": 2
    }
    return decimals.get(asset_class, 2)


def get_apy_for_asset(symbol: str, asset_class: str) -> Optional[float]:
    """Get APY for asset (for staking/earning assets)"""
    # This is a placeholder - implement with your earning assets data
    # For now, return None for most assets
    return None
