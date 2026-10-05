"""
Complete Database Models with LivePrice table
Fixes the $0.0000 issue by properly storing and retrieving live prices
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# ============================================================================
# ASSET MASTER TABLE (All assets - crypto, stocks, forex, commodities)
# ============================================================================

class AssetMaster(Base):
    __tablename__ = "assets_master"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True)
    category = Column(String(50), index=True)  # crypto, stock, forex, commodity
    
    # Asset identifiers for APIs
    coingecko_id = Column(String(255), unique=True, nullable=True)  # For CoinGecko API
    yahoo_symbol = Column(String(50), unique=True, nullable=True)   # For Yahoo Finance
    twelvedata_symbol = Column(String(50), nullable=True)           # For Twelve Data
    
    icon = Column(String(255), nullable=True)  # Icon URL
    decimals = Column(Integer, default=2)
    market_cap = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_category', 'symbol', 'category'),
        Index('idx_category', 'category'),
    )


# ============================================================================
# LIVE PRICES TABLE (Current/latest prices - this was missing!)
# ============================================================================

class LivePrice(Base):
    __tablename__ = "live_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    name = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)
    
    # Price data
    current_price = Column(Float, default=0.0)
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    
    # 24h statistics
    change_24h = Column(Float, default=0.0)
    change_percent_24h = Column(Float, default=0.0)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    
    # Market data
    market_cap = Column(Float, nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    
    # Source and timestamp
    source = Column(String(50), default="coingecko")  # coingecko, yfinance, twelvedata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_updated', 'symbol', 'updated_at'),
        Index('idx_category', 'category'),
    )


# ============================================================================
# PRICE HISTORY TABLE (Historical OHLCV data)
# ============================================================================

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    
    # OHLCV
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    # Interval (5m, 1h, 1d, 1w, 1mo)
    interval = Column(String(10), index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_symbol_interval', 'symbol', 'interval'),
    )


# ============================================================================
# WATCHLIST TABLE
# ============================================================================

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String(50), index=True)
    category = Column(String(50))
    
    added_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_symbol', 'user_id', 'symbol'),
    )


# ============================================================================
# PORTFOLIO TABLE
# ============================================================================

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String(50), index=True)
    quantity = Column(Float)
    average_cost = Column(Float)
    purchase_date = Column(DateTime)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# PREDICTIONS TABLE
# ============================================================================

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True)
    timeframe = Column(String(10))  # 30m, 1h, 4h, 1d, 7d, 30d
    
    prediction = Column(String(20))  # BULLISH, BEARISH, HOLD
    confidence = Column(Float)
    
    lstm_pred = Column(String(20), nullable=True)
    lstm_conf = Column(Float, nullable=True)
    
    arima_pred = Column(String(20), nullable=True)
    arima_conf = Column(Float, nullable=True)
    
    xgb_pred = Column(String(20), nullable=True)
    xgb_conf = Column(Float, nullable=True)
    
    prophet_pred = Column(String(20), nullable=True)
    prophet_conf = Column(Float, nullable=True)
    
    model_agreement = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
    )


# ============================================================================
# ALERTS TABLE
# ============================================================================

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String(50), index=True)
    alert_type = Column(String(50))  # price, change, prediction
    
    trigger_price = Column(Float, nullable=True)
    trigger_percent = Column(Float, nullable=True)
    
    triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# SIGNALS TABLE
# ============================================================================

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True)
    signal_type = Column(String(50))  # BUY, SELL, HOLD
    confidence = Column(Float)
    timeframe = Column(String(10))
    
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_created', 'symbol', 'created_at'),
    )


# ============================================================================
# Create Tables Function
# ============================================================================

def create_tables(engine):
    """Create all tables in database"""
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("All tables created successfully")


def drop_tables(engine):
    """Drop all tables (WARNING: This deletes all data!)"""
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")
