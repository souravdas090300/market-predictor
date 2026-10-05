"""
Background tasks for real-time price updates
Pre-fetches data every 5 seconds to avoid slow API calls on page load
Uses database storage for persistence
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict
import threading

logger = logging.getLogger(__name__)

# In-memory price cache (global for fast access) - kept for instant responses
_price_cache: Dict[str, dict] = {}
_cache_lock = threading.Lock()
_last_update = None

# Top assets to update (expanded for comprehensive coverage)
TOP_CRYPTO = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD", 
    "ADA-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "LINK-USD",
    "MATIC-USD", "SHIB-USD", "TRX-USD", "LTC-USD", "BCH-USD",
    "ATOM-USD", "NEAR-USD", "UNI-USD", "AAVE-USD", "COMP-USD",
    "MKR-USD", "SUSHI-USD", "CRV-USD", "YFI-USD", "SNX-USD",
    "OP-USD", "ARB-USD", "LDO-USD", "FTM-USD", "CELO-USD",
    "ALGO-USD", "VET-USD", "ZIL-USD", "NEO-USD", "HBAR-USD",
    "IOTA-USD", "ONE-USD", "QTUM-USD", "ONT-USD", "ICX-USD",
    "IOST-USD", "SC-USD", "LUNC-USD", "CRO-USD", "KAVA-USD",
    "MINA-USD", "AXS-USD", "GLM-USD", "RNDR-USD", "GRT-USD",
    "FET-USD", "OCEAN-USD", "BAT-USD", "CVC-USD", "ENJ-USD",
    "MANA-USD", "SAND-USD", "GALA-USD", "ILV-USD", "FLOW-USD",
    "NEO-USD", "XEM-USD", "DASH-USD", "ZEC-USD", "KSM-USD",
    "USDT-USD", "USDC-USD", "BUSD-USD", "DAI-USD", "FRAX-USD"
]

TOP_STOCKS = [
    # Technology Giants
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    # Financial Services
    "JPM", "V", "BAC", "WFC", "C", "GS", "MS", "BLK",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "ABT", "T",
    # Consumer Goods
    "PG", "KO", "PEP", "PM", "MO", "KMB", "GIS", "KHC",
    # Energy
    "XOM", "CVX", "COP", "SHEL", "MPC", "PSX", "OXY", "EOG",
    # Industrials
    "CAT", "DE", "GE", "HON", "MMM", "UPS", "RTX", "BA",
    # Retail
    "WMT", "COST", "HD", "TGT", "LOW", "KR", "TJX", "M",
    # Telecom
    "VZ", "T", "TMUS", "CMCSA", "CHTR", "DISH", "OMC",
    # Semiconductors
    "AMD", "INTC", "QCOM", "TXN", "ADI", "MRVL", "MU", "NVDA",
    # Software
    "ADBE", "CRM", "ORCL", "IBM", "INTU", "SNOW", "NOW", "VMW",
    # Media
    "DIS", "NFLX", "CMCSA", "NKE", "SBUX", "FOXA", "ROKU",
    # Insurance
    "ALL", "PGR", "TRV", "CB", "MET", "AIG", "HIG", "LNC",
    # Real Estate
    "PLD", "AMT", "EQIX", "PSA", "VTR", "SPG", "AVB", "EQR",
    # Industrial Conglomerates
    "MMM", "GE", "HON", "CAT", "DE", "EMR", "ITW", "ETN",
    # Aerospace & Defense
    "BA", "LMT", "RTX", "NOC", "GD", "TDG", "TXT", "HEI",
    # Automobiles
    "TSLA", "F", "GM", "STLA", "HMC", "TM", "RACE", "LCID",
    # Utilities
    "NEE", "DUK", "SO", "D", "ED", "AEP", "XEL", "ETR",
    # Materials
    "SHW", "FCX", "NUE", "VAL", "NEM", "CLF", "RIO", "BHP",
    # Gold & Precious Metals
    "GOLD", "BARRICK", "NEM", "FCX", "AEM", "WPM", "KLAC",
    # Chemicals
    "DOW", "DD", "APD", "CTVA", "EMN", "FMC", "HUN", "PPG",
    # Agriculture
    "ADM", "BG", "CAG", "MO", "ADM", "TSN", "BG", "CF",
    # Banks
    "JPM", "BAC", "WFC", "C", "GS", "MS", "PNC", "USB",
    # Dividend Aristocrats
    "KO", "PG", "JNJ", "MMM", "CAT", "XOM", "CVX", "CSCO",
    # Growth Stocks
    "NVDA", "AMD", "TSLA", "META", "AMZN", "GOOGL", "MSFT", "AAPL",
    # Value Stocks
    "BRK.B", "JPM", "V", "PG", "KO", "PEP", "WMT", "MCD",
    # ETFs
    "SPY", "QQQ", "IWM", "VTI", "VOO", "GLD", "SLV", "TLT"
]

TOP_FOREX = [
    # Major Pairs
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X",
    "AUDUSD=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X",
    # Cross Pairs
    "EURCHF=X", "EURCAD=X", "EURAUD=X", "EURGBP=X", "EURJPY=X",
    "GBPCHF=X", "GBPAUD=X", "GBPJPY=X", "GBPCHF=X", "GBPCAD=X",
    "AUDCHF=X", "AUDJPY=X", "AUDCAD=X", "AUDNZD=X", "EURNZD=X",
    "CADCHF=X", "CADJPY=X", "CHFJPY=X", "NZDJPY=X", "NZDCHF=X",
    # Emerging Markets
    "USDTRY=X", "USDMXN=X", "USDZAR=X", "USDRUB=X", "USDINR=X",
    "USDCNY=X", "USDKRW=X", "USDSGD=X", "USDHKD=X", "USDTWD=X",
    "USDTHB=X", "USDPHP=X", "USDAED=X", "USDSAR=X", "USDBRL=X",
    # Commodity Currencies
    "USDCAD=X", "USDAUD=X", "USDNZD=X", "USDNOK=X", "USDSEK=X",
    # Safe Haven
    "USDCHF=X", "USDJPY=X", "XAUUSD=X", "XAGUSD=X"
]

TOP_COMMODITIES = [
    # Gold & Precious Metals
    "GC=F", "GLD", "IAU", "SLV", "PPLT", "PALL", "PLG",
    # Energy
    "CL=F", "NG=F", "RB=F", "HO=F", "XLE", "XOM", "CVX",
    # Agriculture
    "ZC=F", "ZW=F", "ZS=F", "ZC=F", "KE=F", "RR=F", "SB=F",
    "LE=F", "HE=F", "GF=F", "KC=F", "CC=F", "CT=F", "OJ=F",
    # Industrial Metals
    "HG=F", "SI=F", "AL=F", "ZN=F", "CU=F", "LE=F", "NI=F",
    # Livestock
    "LE=F", "HE=F", "GF=F", "KC=F", "ZC=F", "SB=F", "ZM=F",
    # Soft Commodities
    "KC=F", "SB=F", "CC=F", "CT=F", "ZC=F", "ZW=F", "ZO=F",
    # Indices
    "ES=F", "NQ=F", "YM=F", "RTY=F", "ZB=F", "ZN=F", "CL=F",
    "GC=F", "SI=F"
]


def get_cached_price(symbol: str) -> dict | None:
    """Get price from in-memory cache"""
    with _cache_lock:
        return _price_cache.get(symbol.upper())


def get_all_cached_prices() -> Dict[str, dict]:
    """Get all cached prices"""
    with _cache_lock:
        return _price_cache.copy()


def update_price_cache(quotes: Dict[str, dict]):
    """Update price cache with new quotes"""
    with _cache_lock:
        for symbol, quote in quotes.items():
            if quote:
                _price_cache[symbol.upper()] = quote
        global _last_update
        _last_update = datetime.now(timezone.utc)


async def background_price_update_task():
    """
    Background task to update prices every 5 seconds
    Pre-fetches data to avoid slow API calls on page load
    PARALLELIZED - Updates crypto, stocks, and forex simultaneously
    Stores prices in database for persistence
    
    Usage in main.py:
        @app.on_event("startup")
        async def startup():
            asyncio.create_task(background_price_update_task())
    """
    from app.core import data
    from app.database import SessionLocal
    from app.providers.live_price_fetcher import (
        CoinGeckoLivePriceFetcher,
        YahooFinanceLivePriceFetcher,
        update_live_prices_in_db
    )
    
    logger.info("Starting background price update task...")
    
    async def update_crypto():
        """Update crypto prices in parallel using thread pool"""
        logger.info("Updating crypto prices...")
        crypto_quotes = {}
        tasks = []

        for symbol in TOP_CRYPTO:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_crypto_quote(sym) if data.get_crypto_quote(sym) else None)
            )
            tasks.append(task)

        # Run all crypto fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    crypto_quotes[sym] = quote

        update_price_cache(crypto_quotes)
        logger.info(f"Updated {len(crypto_quotes)} crypto prices")

        # Also update database with live prices from CoinGecko for better data
        try:
            db_session = SessionLocal()
            # Use the CoinGecko fetcher for better data quality
            coingecko_prices = await CoinGeckoLivePriceFetcher.fetch_multiple(
                [s.replace("-USD", "") for s in TOP_CRYPTO[:15]]  # Top 15 for CoinGecko
            )
            # Convert to format expected by database
            db_prices = {}
            for symbol, price_data in coingecko_prices.items():
                db_prices[f"{symbol}-USD"] = {
                    "current_price": price_data.get("current_price"),
                    "change_24h": price_data.get("change_24h"),
                    "change_percent_24h": price_data.get("change_24h"),  # CoinGecko returns absolute change
                    "high_24h": price_data.get("high_24h"),
                    "low_24h": price_data.get("low_24h"),
                    "volume_24h": price_data.get("volume_24h"),
                    "market_cap": price_data.get("market_cap"),
                    "source": "coingecko"
                }
            if db_prices:
                await update_live_prices_in_db(db_session, db_prices)
                db_session.close()
                logger.info(f"Updated {len(db_prices)} crypto prices in database")
        except Exception as e:
            logger.error(f"Error updating crypto prices in database: {e}")

        return crypto_quotes
    
    async def update_stocks():
        """Update stock prices in parallel using thread pool"""
        logger.info("Updating stock prices...")
        stock_quotes = {}
        tasks = []

        for symbol in TOP_STOCKS:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_live_quote(sym) if data.get_live_quote(sym) else None)
            )
            tasks.append(task)

        # Run all stock fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    stock_quotes[sym] = quote

        update_price_cache(stock_quotes)
        logger.info(f"Updated {len(stock_quotes)} stock prices")

        # Update database with live prices from Yahoo Finance
        try:
            db_session = SessionLocal()
            # Use Yahoo Finance fetcher for top stocks
            yahoo_prices = YahooFinanceLivePriceFetcher.fetch_multiple(TOP_STOCKS[:20])
            if yahoo_prices:
                await update_live_prices_in_db(db_session, yahoo_prices)
                db_session.close()
                logger.info(f"Updated {len(yahoo_prices)} stock prices in database")
        except Exception as e:
            logger.error(f"Error updating stock prices in database: {e}")

        return stock_quotes
    
    async def update_forex():
        """Update forex prices in parallel using thread pool"""
        logger.info("Updating forex prices...")
        forex_quotes = {}
        tasks = []
        
        for symbol in TOP_FOREX:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_live_quote(sym) if data.get_live_quote(sym) else None)
            )
            tasks.append(task)
        
        # Run all forex fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    forex_quotes[sym] = quote
        
        update_price_cache(forex_quotes)
        logger.info(f"Updated {len(forex_quotes)} forex prices")
        return forex_quotes
    
    async def update_commodities():
        """Update commodity prices in parallel using thread pool"""
        logger.info("Updating commodity prices...")
        commodity_quotes = {}
        tasks = []
        
        for symbol in TOP_COMMODITIES:
            # Run synchronous fetch in thread pool
            task = asyncio.to_thread(
                lambda sym=symbol: (sym, data.get_live_quote(sym) if data.get_live_quote(sym) else None)
            )
            tasks.append(task)
        
        # Run all commodity fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                sym, quote = result
                if quote:
                    commodity_quotes[sym] = quote
        
        update_price_cache(commodity_quotes)
        logger.info(f"Updated {len(commodity_quotes)} commodity prices")
        return commodity_quotes
    
    while True:
        try:
            # PARALLELIZE ALL UPDATES - Run crypto, stocks, forex, and commodities simultaneously
            await asyncio.gather(
                update_crypto(),
                update_stocks(),
                update_forex(),
                update_commodities()
            )
            
            logger.info(f"Total cached prices: {len(_price_cache)}")
            
            await asyncio.sleep(10)  # Update every 10 seconds for larger lists
        
        except Exception as e:
            logger.error(f"Background task error: {e}")
            await asyncio.sleep(5)


def get_cache_status() -> dict:
    """Get cache statistics"""
    with _cache_lock:
        return {
            "total_cached": len(_price_cache),
            "last_update": _last_update.isoformat() if _last_update else None,
            "crypto_count": len([s for s in _price_cache if s.endswith("-USD")]),
            "stock_count": len([s for s in _price_cache if not s.endswith("-USD") and not s.endswith("=X")]),
            "forex_count": len([s for s in _price_cache if s.endswith("=X")])
        }
