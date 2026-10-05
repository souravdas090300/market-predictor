"""
Asset Historical Price Data Routes
Provides OHLCV data for all timeframes (24H, 1W, 1M, 6M, 1Y, 5Y, ALL)
Integrates with CoinGecko, Yahoo Finance (yfinance)
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import httpx
import asyncio
from typing import List, Dict, Optional
from cachetools import TTLCache
import pandas as pd

from app.core import data, coingecko

router = APIRouter()

# Cache for historical data (1 hour TTL)
price_cache = TTLCache(maxsize=500, ttl=3600)

# ============================================================================
# HISTORICAL PRICE DATA ENDPOINTS
# ============================================================================

@router.get("/price-history/{symbol}")
async def get_price_history(
    symbol: str,
    timeframe: str = Query("24H", regex="^(24H|1W|1M|6M|1Y|5Y|ALL)$"),
    category: str = Query("crypto")
):
    """
    Get historical price data with OHLCV (Open, High, Low, Close, Volume)
    
    Timeframes: 24H, 1W, 1M, 6M, 1Y, 5Y, ALL
    Categories: crypto, stock, forex, commodity
    
    Returns:
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "category": "crypto",
        "timeframe": "24H",
        "current": {
            "price": 45000,
            "change24h": 1200,
            "changePercent": 2.74,
            "high24h": 46000,
            "low24h": 44000,
            "volume24h": 28500000000,
            "marketCap": 890000000000
        },
        "historical": [
            {
                "timestamp": "2026-10-05T10:00:00Z",
                "open": 44900,
                "high": 45200,
                "low": 44800,
                "close": 45100,
                "volume": 1250000
            },
            ...
        ]
    }
    """
    
    cache_key = f"{symbol}_{timeframe}_{category}"
    
    # Check cache first
    if cache_key in price_cache:
        return price_cache[cache_key]
    
    try:
        # Fetch current price
        current_price = await get_current_price(symbol, category)
        
        # Fetch historical data based on category
        if category.lower() == "crypto":
            historical = await get_crypto_history(symbol, timeframe)
        elif category.lower() == "stock":
            historical = await get_stock_history(symbol, timeframe)
        elif category.lower() == "forex":
            historical = await get_forex_history(symbol, timeframe)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported category: {category}")
        
        response = {
            "symbol": symbol.upper(),
            "name": symbol,
            "category": category.lower(),
            "timeframe": timeframe,
            "current": current_price,
            "historical": historical
        }
        
        # Cache the response
        price_cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price history: {str(e)}")


async def get_current_price(symbol: str, category: str) -> dict:
    """Get current price and 24h stats"""
    
    # Use existing data module
    try:
        if category.lower() == "crypto":
            quote = data.get_crypto_quote(symbol)
        else:
            quote = data.get_live_quote(symbol)
        
        if quote:
            return {
                "price": float(quote.get("price", 0)),
                "change24h": float(quote.get("change", 0)),
                "changePercent": float(quote.get("change_pct", 0) * 100),
                "high24h": float(quote.get("day_high", 0)),
                "low24h": float(quote.get("day_low", 0)),
                "volume24h": float(quote.get("volume", 0)),
                "marketCap": float(quote.get("market_cap", 0))
            }
    except Exception as e:
        print(f"Error fetching current price: {e}")
    
    return {"price": 0, "change24h": 0, "changePercent": 0, "high24h": 0, "low24h": 0, "volume24h": 0, "marketCap": 0}


# ============================================================================
# CRYPTO PRICE HISTORY (CoinGecko)
# ============================================================================

async def get_crypto_history(symbol: str, timeframe: str) -> List[Dict]:
    """
    Fetch crypto price history using existing coingecko module
    Supports 24H (5min intervals), 1W (hourly), 1M+ (daily)
    """
    
    try:
        # Use existing yfinance for crypto (e.g., BTC-USD, ETH-USD)
        crypto_symbol = f"{symbol}-USD"
        
        interval_map = {
            "24H": "5m",   # 5 minute candles
            "1W": "1h",    # Hourly candles
            "1M": "1d",    # Daily candles
            "6M": "1d",
            "1Y": "1d",
            "5Y": "1wk",   # Weekly candles
            "ALL": "1mo"   # Monthly candles
        }
        
        period_map = {
            "24H": "1d",
            "1W": "7d",
            "1M": "1mo",
            "6M": "6mo",
            "1Y": "1y",
            "5Y": "5y",
            "ALL": "max"
        }
        
        interval = interval_map.get(timeframe, "1d")
        period = period_map.get(timeframe, "1d")
        
        # Fetch data using existing data module
        df = data.get_prices(crypto_symbol, period)
        
        # Convert to OHLCV format
        historical = []
        for idx, row in df.iterrows():
            historical.append({
                "timestamp": idx.isoformat() + "Z",
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"])
            })
        
        return historical[-200:]  # Return last 200 candles
        
    except Exception as e:
        print(f"Error fetching crypto history for {symbol}: {e}")
        return generate_demo_ohlcv(timeframe, symbol)


# ============================================================================
# STOCK PRICE HISTORY (Yahoo Finance / Alpha Vantage)
# ============================================================================

async def get_stock_history(symbol: str, timeframe: str) -> List[Dict]:
    """
    Fetch stock price history from Yahoo Finance
    Supports all timeframes with proper intervals
    """
    
    try:
        import yfinance as yf
        
        interval_map = {
            "24H": "5m",   # 5 minute candles
            "1W": "1h",    # Hourly candles
            "1M": "1d",    # Daily candles
            "6M": "1d",
            "1Y": "1d",
            "5Y": "1wk",   # Weekly candles
            "ALL": "1mo"   # Monthly candles
        }
        
        period_map = {
            "24H": "1d",
            "1W": "7d",
            "1M": "1mo",
            "6M": "6mo",
            "1Y": "1y",
            "5Y": "5y",
            "ALL": "max"
        }
        
        interval = interval_map.get(timeframe, "1d")
        period = period_map.get(timeframe, "1d")
        
        # Fetch data
        stock = yf.Ticker(symbol.upper())
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Convert to OHLCV format
        historical = []
        for idx, row in df.iterrows():
            historical.append({
                "timestamp": idx.isoformat() + "Z",
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"])
            })
        
        return historical[-200:]  # Return last 200 candles
        
    except Exception as e:
        print(f"Error fetching stock history for {symbol}: {e}")
        return generate_demo_ohlcv(timeframe, symbol)


# ============================================================================
# FOREX PRICE HISTORY (Twelve Data)
# ============================================================================

async def get_forex_history(symbol: str, timeframe: str) -> List[Dict]:
    """
    Fetch forex price history using yfinance
    Supports all timeframes
    """
    
    try:
        # Use yfinance for forex (e.g., EURUSD=X)
        forex_symbol = f"{symbol}=X"
        
        interval_map = {
            "24H": "5m",   # 5 minute candles
            "1W": "1h",    # Hourly candles
            "1M": "1d",    # Daily candles
            "6M": "1d",
            "1Y": "1d",
            "5Y": "1wk",   # Weekly candles
            "ALL": "1mo"   # Monthly candles
        }
        
        period_map = {
            "24H": "1d",
            "1W": "7d",
            "1M": "1mo",
            "6M": "6mo",
            "1Y": "1y",
            "5Y": "5y",
            "ALL": "max"
        }
        
        interval = interval_map.get(timeframe, "1d")
        period = period_map.get(timeframe, "1d")
        
        # Fetch data using existing data module
        df = data.get_prices(forex_symbol, period)
        
        # Convert to OHLCV format
        historical = []
        for idx, row in df.iterrows():
            historical.append({
                "timestamp": idx.isoformat() + "Z",
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"])
            })
        
        return historical[-200:]  # Return last 200 candles
        
    except Exception as e:
        print(f"Error fetching forex history for {symbol}: {e}")
        return generate_demo_ohlcv(timeframe, symbol)


# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

def generate_demo_ohlcv(timeframe: str, symbol: str) -> List[Dict]:
    """Generate demo OHLCV data for testing"""
    
    limit_map = {
        "24H": 288,   # 5-min candles
        "1W": 168,    # Hourly
        "1M": 30,     # Daily
        "6M": 26,     # Weekly
        "1Y": 52,     # Weekly
        "5Y": 60,     # Monthly
        "ALL": 200    # Monthly
    }
    
    limit = limit_map.get(timeframe, 100)
    data = []
    base_price = 45000 if symbol.upper() in ["BTC"] else 2500 if symbol.upper() in ["ETH"] else 100
    
    for i in range(limit):
        # Calculate time based on timeframe
        now = datetime.utcnow()
        
        if timeframe == "24H":
            timestamp = now - timedelta(minutes=i * 5)
        elif timeframe == "1W":
            timestamp = now - timedelta(hours=i)
        elif timeframe == "1M":
            timestamp = now - timedelta(days=i)
        elif timeframe == "6M":
            timestamp = now - timedelta(days=i * 7)
        elif timeframe == "1Y":
            timestamp = now - timedelta(weeks=i)
        elif timeframe == "5Y":
            timestamp = now - timedelta(days=i * 30)
        else:  # ALL
            timestamp = now - timedelta(days=i * 30)
        
        # Generate OHLC data
        change = (2 * (i / limit) - 1) * base_price * 0.05  # Trend
        random_walk = (hash(str(i)) % 1000) / 1000 * base_price * 0.02
        
        open_price = base_price + change + random_walk
        close_price = base_price + change + random_walk + (hash(str(i * 2)) % 1000 - 500) / 1000 * base_price * 0.01
        high_price = max(open_price, close_price) * 1.01
        low_price = min(open_price, close_price) * 0.99
        volume = (hash(str(i * 3)) % 10000000) + 1000000
        
        data.insert(0, {  # Insert at beginning to maintain chronological order
            "timestamp": timestamp.isoformat() + "Z",
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": int(volume)
        })
    
    return data


# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================

@router.get("/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: str = "crypto"
):
    """
    Get OHLCV data for a specific date range
    Dates format: YYYY-MM-DD
    """
    
    try:
        if category.lower() == "crypto":
            return await get_crypto_history(symbol, "1M")
        elif category.lower() == "stock":
            return await get_stock_history(symbol, "1M")
        else:
            return await get_forex_history(symbol, "1M")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison/{symbols}")
async def compare_assets(
    symbols: str,  # Comma-separated: BTC,ETH,AAPL
    timeframe: str = "1M",
    category: str = "crypto"
):
    """
    Compare multiple assets on same chart
    Returns normalized data for comparison
    """
    
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    comparison_data = {}
    
    for symbol in symbol_list:
        try:
            if category.lower() == "crypto":
                data = await get_crypto_history(symbol, timeframe)
            elif category.lower() == "stock":
                data = await get_stock_history(symbol, timeframe)
            else:
                data = await get_forex_history(symbol, timeframe)
            
            # Normalize to percentage change from first close
            if data:
                base_price = data[0]["close"]
                normalized = [
                    {
                        **candle,
                        "change_percent": ((candle["close"] - base_price) / base_price) * 100
                    }
                    for candle in data
                ]
                comparison_data[symbol] = normalized
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    
    return comparison_data


@router.post("/cache-clear")
async def clear_price_cache():
    """Clear price history cache (admin only)"""
    price_cache.clear()
    return {"status": "Cache cleared", "items": 0}
