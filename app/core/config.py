"""Central settings. Edit the WATCHLIST to track the assets you care about."""
import os
import re
from pathlib import Path
import warnings
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import extended asset providers
from providers import crypto_extended_300
from providers import stocks_global_500
from providers import forex_global_100
from providers import commodities_global_50

# Environment
ENV = os.getenv("ENV", "development").lower()

# Security warnings for production
if ENV == "production":
    required_env_vars = ["SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        warnings.warn(
            f"SECURITY WARNING: Missing required environment variables for production: {missing_vars}. "
            "Set these before deploying to production!",
            RuntimeWarning
        )

# Base directory
ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Create data and logs directories
DATA = ROOT / "data"
LOGS = ROOT / "logs"
DATA.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

# Where every signal is logged so its real outcome can be checked later.
DB_PATH = ROOT / "data" / "signals.db"

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production" if ENV == "development" else None)
if SECRET_KEY is None and ENV == "production":
    raise ValueError("SECRET_KEY environment variable must be set in production")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Security Settings
ALLOW_PRIVATE_URLS = os.getenv("ALLOW_PRIVATE_URLS", "true" if ENV == "development" else "false").lower() == "true"
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"

# How many trading days ahead the model looks.
HORIZON_DAYS = 5

# Short-term prediction horizons (in hours)
SHORT_TERM_HORIZONS = {
    "1h": 1,      # 1 hour
    "2h": 2,      # 2 hours
    "3h": 3,      # 3 hours
    "4h": 4,      # 4 hours
    "5h": 5,      # 5 hours
    "6h": 6,      # 6 hours
    "8h": 8,      # 8 hours
    "12h": 12,    # 12 hours
    "24h": 24,    # 24 hours
    "7d": 168,    # 7 days
    "30d": 720    # 30 days
}

# Probability thresholds for turning P(up) into a label.
BULLISH_ABOVE = 0.55
BEARISH_BELOW = 0.45

# How strongly recent news tone can move the final probability.
# 0.10 means a fully positive news day shifts P(up) by at most +0.10.
SENTIMENT_WEIGHT = 0.10

# How strongly the user's own material can move the probability when combined with the auto signal.
# Material is one person's chosen text, so it gets a bit more weight than scraped headlines.
MATERIAL_WEIGHT = 0.15

# Material tone (-1..1) beyond this counts as bullish/bearish on its own.
MATERIAL_LEAN = 0.15

# Retrain a saved model when it is older than this many days.
MODEL_MAX_AGE_DAYS = 7

# Price history to download for training.
HISTORY_PERIOD = "5y"

# Cache API responses for this many seconds.
API_CACHE_SECONDS = int(os.getenv("API_CACHE_SECONDS", "60" if ENV == "development" else "300"))

# Live quote polling. Keep this modest — Yahoo rate-limits aggressive clients.
LIVE_QUOTE_CACHE_SECONDS = int(os.getenv("LIVE_QUOTE_CACHE_SECONDS", "15"))  # Increased from 8s to 15s
LIVE_STREAM_INTERVAL_SECONDS = float(os.getenv("LIVE_STREAM_INTERVAL_SECONDS", "20"))  # Increased from 12s to 20s

# Bulk limit
BULK_LIMIT = int(os.getenv("BULK_LIMIT", "100" if ENV == "development" else "50"))

# File upload limits
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "10_000_000" if ENV == "development" else "5_000_000"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if ENV == "development" else "INFO")
SECURITY_LOG_LEVEL = os.getenv("SECURITY_LOG_LEVEL", "DEBUG" if ENV == "development" else "INFO")

# CORS Settings
def get_cors_origins():
    """Get CORS origins from environment, handling Railway/Vercel URLs dynamically."""
    default_dev = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000"
    # Note: FastAPI CORSMiddleware doesn't support wildcard subdomains, so we use explicit domains
    default_prod = "https://market-predictor-eta.vercel.app"
    
    cors_env = os.getenv("CORS_ORIGINS", default_dev if ENV == "development" else default_prod)
    origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    
    # Ensure specific domains are included for production
    if ENV == "production":
        # Always include the explicit frontend domain
        if "https://market-predictor-eta.vercel.app" not in origins:
            origins.append("https://market-predictor-eta.vercel.app")
        
        # Allow localhost for development/testing from production
        origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ])
    
    return origins

CORS_ORIGINS = get_cors_origins()
ADMIN_CORS_ORIGINS = os.getenv("ADMIN_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000" if ENV == "development" else "https://market-predictor-eta.vercel.app").split(",")

# Feature Flags
ENABLE_DEBUG_MODE = os.getenv("ENABLE_DEBUG_MODE", "true" if ENV == "development" else "false").lower() == "true"
ENABLE_PROFILING = os.getenv("ENABLE_PROFILING", "false").lower() == "true"
ENABLE_TESTING_MODE = os.getenv("ENABLE_TESTING_MODE", "true" if ENV == "development" else "false").lower() == "true"

# Subscription Settings
# When false, all users have access to all features regardless of subscription status
# When true, only subscribed users can access premium features
SUBSCRIPTION_MODE_ENABLED = os.getenv("SUBSCRIPTION_MODE_ENABLED", "false").lower() == "true"

# Advanced features
HISTORY_KEEP_DAYS = 90

# URL fetching
FETCH_TIMEOUT = 10
FETCH_MAX_CHARS = 50000

CLASS_LABELS = {
    "stock": "Shares",
    "crypto": "Crypto",
    "forex": "Forex",
    "commodity": "Commodities",
    "other": "Other",
}

# What is worth pasting in "Your material", per market.
MATERIAL_HINTS = {
    "stock": [
        "Earnings release or guidance: revenue, profit and outlook",
        "Analyst upgrades, downgrades and price targets",
        "Market-wide news: interest rates, jobs and inflation data",
        "Company events: lawsuits, product launches, insider buying or selling",
    ],
    "crypto": [
        "ETF flows, regulation and exchange listing or delisting news",
        "Hacks, large wallet moves, staking or halving events",
        "Macro news that moves risk assets: rates, liquidity, dollar strength",
        "Your own notes, such as funding rates or a fear and greed reading",
    ],
    "forex": [
        "Central bank statements and rate decisions for both currencies",
        "Inflation, jobs and GDP releases (CPI, payrolls)",
        "Write it from the first currency's point of view: 'euro weakens after weak German data' for EUR/USD, because the tone reader can't tell which currency a sentence is about",
    ],
    "commodity": [
        "Supply reports: OPEC decisions, inventory data, mine output, weather",
        "Demand signals: China data, manufacturing, industrial use",
        "Dollar strength and interest-rate news, which move gold and oil",
        "Geopolitical events that affect supply routes or safe-haven demand",
    ],
    "other": [
        "News, reports or your own notes about this asset",
        "Anything about the wider economy that could move it",
    ],
}

# Create deduplicated watchlist to avoid data fetching issues
# Start with existing manually curated assets
_RAW_WATCHLIST = [
    # Major Stocks (removed delisted TWTR, BRK.B, SQ - kept active stocks)
    {"symbol": "AAPL", "name": "Apple", "class": "stock", "query": "Apple AAPL stock"},
    {"symbol": "MSFT", "name": "Microsoft", "class": "stock", "query": "Microsoft MSFT stock"},
    {"symbol": "NVDA", "name": "Nvidia", "class": "stock", "query": "Nvidia NVDA stock"},
    {"symbol": "GOOGL", "name": "Alphabet", "class": "stock", "query": "Alphabet GOOGL stock"},
    {"symbol": "AMZN", "name": "Amazon", "class": "stock", "query": "Amazon AMZN stock"},
    {"symbol": "META", "name": "Meta", "class": "stock", "query": "Meta META stock"},
    {"symbol": "TSLA", "name": "Tesla", "class": "stock", "query": "Tesla TSLA stock"},
    {"symbol": "JPM", "name": "JPMorgan Chase", "class": "stock", "query": "JPMorgan JPM stock"},
    {"symbol": "V", "name": "Visa", "class": "stock", "query": "Visa V stock"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "class": "stock", "query": "Johnson & Johnson JNJ stock"},
    {"symbol": "WMT", "name": "Walmart", "class": "stock", "query": "Walmart WMT stock"},
    {"symbol": "PG", "name": "Procter & Gamble", "class": "stock", "query": "Procter & Gamble PG stock"},
    {"symbol": "XOM", "name": "Exxon Mobil", "class": "stock", "query": "Exxon Mobil XOM stock"},
    {"symbol": "CVX", "name": "Chevron", "class": "stock", "query": "Chevron CVX stock"},
    {"symbol": "KO", "name": "Coca-Cola", "class": "stock", "query": "Coca-Cola KO stock"},
    {"symbol": "PEP", "name": "PepsiCo", "class": "stock", "query": "PepsiCo PEP stock"},
    {"symbol": "MRK", "name": "Merck", "class": "stock", "query": "Merck MRK stock"},
    {"symbol": "ABBV", "name": "AbbVie", "class": "stock", "query": "AbbVie ABBV stock"},
    {"symbol": "AVGO", "name": "Broadcom", "class": "stock", "query": "Broadcom AVGO stock"},
    {"symbol": "COST", "name": "Costco", "class": "stock", "query": "Costco COST stock"},
    {"symbol": "CSCO", "name": "Cisco", "class": "stock", "query": "Cisco CSCO stock"},
    {"symbol": "ADBE", "name": "Adobe", "class": "stock", "query": "Adobe ADBE stock"},
    {"symbol": "CRM", "name": "Salesforce", "class": "stock", "query": "Salesforce CRM stock"},
    {"symbol": "NFLX", "name": "Netflix", "class": "stock", "query": "Netflix NFLX stock"},
    {"symbol": "AMD", "name": "AMD", "class": "stock", "query": "AMD stock"},
    {"symbol": "INTC", "name": "Intel", "class": "stock", "query": "Intel INTC stock"},
    {"symbol": "PYPL", "name": "PayPal", "class": "stock", "query": "PayPal PYPL stock"},
    {"symbol": "DIS", "name": "Disney", "class": "stock", "query": "Disney DIS stock"},
    {"symbol": "NKE", "name": "Nike", "class": "stock", "query": "Nike NKE stock"},
    {"symbol": "ABT", "name": "Abbott Laboratories", "class": "stock", "query": "Abbott Laboratories ABT stock"},
    {"symbol": "T", "name": "AT&T", "class": "stock", "query": "AT&T T stock"},
    {"symbol": "IBM", "name": "IBM", "class": "stock", "query": "IBM stock"},
    {"symbol": "ORCL", "name": "Oracle", "class": "stock", "query": "Oracle ORCL stock"},
    {"symbol": "ACN", "name": "Accenture", "class": "stock", "query": "Accenture ACN stock"},
    {"symbol": "QCOM", "name": "Qualcomm", "class": "stock", "query": "Qualcomm QCOM stock"},
    {"symbol": "TXN", "name": "Texas Instruments", "class": "stock", "query": "Texas Instruments TXN stock"},
    {"symbol": "SHOP", "name": "Shopify", "class": "stock", "query": "Shopify SHOP stock"},
    {"symbol": "SPOT", "name": "Spotify", "class": "stock", "query": "Spotify SPOT stock"},
    {"symbol": "UBER", "name": "Uber", "class": "stock", "query": "Uber UBER stock"},
    {"symbol": "LYFT", "name": "Lyft", "class": "stock", "query": "Lyft LYFT stock"},
    {"symbol": "SNAP", "name": "Snap", "class": "stock", "query": "Snap SNAP stock"},
    {"symbol": "COIN", "name": "Coinbase", "class": "stock", "query": "Coinbase COIN stock"},
    {"symbol": "ROKU", "name": "Roku", "class": "stock", "query": "Roku ROKU stock"},
    {"symbol": "ZM", "name": "Zoom", "class": "stock", "query": "Zoom ZM stock"},
    {"symbol": "DOCU", "name": "DocuSign", "class": "stock", "query": "DocuSign DOCU stock"},
    {"symbol": "SNOW", "name": "Snowflake", "class": "stock", "query": "Snowflake SNOW stock"},
    {"symbol": "PLTR", "name": "Palantir", "class": "stock", "query": "Palantir PLTR stock"},
    {"symbol": "U", "name": "Unity", "class": "stock", "query": "Unity U stock"},
    {"symbol": "RBLX", "name": "Roblox", "class": "stock", "query": "Roblox RBLX stock"},
    {"symbol": "AFRM", "name": "Affirm", "class": "stock", "query": "Affirm AFRM stock"},
    {"symbol": "UPST", "name": "Upstart", "class": "stock", "query": "Upstart UPST stock"},
    {"symbol": "HOOD", "name": "Robinhood", "class": "stock", "query": "Robinhood HOOD stock"},
    {"symbol": "GME", "name": "GameStop", "class": "stock", "query": "GameStop GME stock"},
    {"symbol": "AMC", "name": "AMC Entertainment", "class": "stock", "query": "AMC Entertainment AMC stock"},
    
    # Major Indices
    {"symbol": "^GSPC", "name": "S&P 500", "class": "stock", "query": "S&P 500 stock market"},
    {"symbol": "^DJI", "name": "Dow Jones", "class": "stock", "query": "Dow Jones Industrial Average"},
    {"symbol": "^IXIC", "name": "NASDAQ", "class": "stock", "query": "NASDAQ Composite Index"},
    {"symbol": "^RUT", "name": "Russell 2000", "class": "stock", "query": "Russell 2000 Index"},
    {"symbol": "^VIX", "name": "VIX", "class": "stock", "query": "CBOE Volatility Index"},
    
    # NOTE: Cryptocurrencies are now fetched dynamically from CoinGecko API
    # Use data.get_top_cryptos_watchlist() to get top 300+ cryptos
    # Below are the top 20 major cryptos as examples/fallback (removed delisted symbols)
    {"symbol": "BTC-USD", "name": "Bitcoin", "class": "crypto", "query": "Bitcoin price"},
    {"symbol": "ETH-USD", "name": "Ethereum", "class": "crypto", "query": "Ethereum price"},
    {"symbol": "BNB-USD", "name": "Binance Coin", "class": "crypto", "query": "Binance Coin price"},
    {"symbol": "XRP-USD", "name": "Ripple", "class": "crypto", "query": "Ripple XRP price"},
    {"symbol": "SOL-USD", "name": "Solana", "class": "crypto", "query": "Solana SOL price"},
    {"symbol": "ADA-USD", "name": "Cardano", "class": "crypto", "query": "Cardano ADA price"},
    {"symbol": "DOGE-USD", "name": "Dogecoin", "class": "crypto", "query": "Dogecoin DOGE price"},
    {"symbol": "DOT-USD", "name": "Polkadot", "class": "crypto", "query": "Polkadot DOT price"},
    {"symbol": "AVAX-USD", "name": "Avalanche", "class": "crypto", "query": "Avalanche AVAX price"},
    {"symbol": "LINK-USD", "name": "Chainlink", "class": "crypto", "query": "Chainlink LINK price"},
    {"symbol": "UNI-USD", "name": "Uniswap", "class": "crypto", "query": "Uniswap UNI price"},
    {"symbol": "ATOM-USD", "name": "Cosmos", "class": "crypto", "query": "Cosmos ATOM price"},
    {"symbol": "LTC-USD", "name": "Litecoin", "class": "crypto", "query": "Litecoin LTC price"},
    {"symbol": "XLM-USD", "name": "Stellar", "class": "crypto", "query": "Stellar XLM price"},
    {"symbol": "ALGO-USD", "name": "Algorand", "class": "crypto", "query": "Algorand ALGO price"},
    {"symbol": "VET-USD", "name": "VeChain", "class": "crypto", "query": "VeChain VET price"},
    {"symbol": "FIL-USD", "name": "Filecoin", "class": "crypto", "query": "Filecoin FIL price"},
    {"symbol": "TRX-USD", "name": "TRON", "class": "crypto", "query": "TRON TRX price"},
    {"symbol": "XMR-USD", "name": "Monero", "class": "crypto", "query": "Monero XMR price"},
    {"symbol": "ETC-USD", "name": "Ethereum Classic", "class": "crypto", "query": "Ethereum Classic ETC price"},
    {"symbol": "XTZ-USD", "name": "Tezos", "class": "crypto", "query": "Tezos XTZ price"},
    {"symbol": "NEAR-USD", "name": "NEAR Protocol", "class": "crypto", "query": "NEAR Protocol NEAR price"},
    {"symbol": "AAVE-USD", "name": "Aave", "class": "crypto", "query": "Aave AAVE price"},
    {"symbol": "MKR-USD", "name": "Maker", "class": "crypto", "query": "Maker MKR price"},
    {"symbol": "SHIB-USD", "name": "Shiba Inu", "class": "crypto", "query": "Shiba Inu SHIB price"},
    {"symbol": "ARB-USD", "name": "Arbitrum", "class": "crypto", "query": "Arbitrum ARB price"},
    {"symbol": "OP-USD", "name": "Optimism", "class": "crypto", "query": "Optimism OP price"},
    {"symbol": "LDO-USD", "name": "Lido DAO", "class": "crypto", "query": "Lido DAO LDO price"},
    {"symbol": "APT-USD", "name": "Aptos", "class": "crypto", "query": "Aptos APT price"},
    {"symbol": "SUI-USD", "name": "Sui", "class": "crypto", "query": "Sui SUI price"},
    {"symbol": "SEI-USD", "name": "Sei", "class": "crypto", "query": "Sei SEI price"},
    {"symbol": "TIA-USD", "name": "Celestia", "class": "crypto", "query": "Celestia TIA price"},
    {"symbol": "BONK-USD", "name": "Bonk", "class": "crypto", "query": "Bonk BONK price"},
    {"symbol": "WIF-USD", "name": "dogwifhat", "class": "crypto", "query": "dogwifhat WIF price"},
    {"symbol": "PEPE-USD", "name": "Pepe", "class": "crypto", "query": "Pepe PEPE price"},
    {"symbol": "FLOKI-USD", "name": "Floki", "class": "crypto", "query": "Floki FLOKI price"},
    {"symbol": "PENDLE-USD", "name": "Pendle", "class": "crypto", "query": "Pendle PENDLE price"},
    {"symbol": "GRT-USD", "name": "The Graph", "class": "crypto", "query": "The Graph GRT price"},
    {"symbol": "BAND-USD", "name": "Band Protocol", "class": "crypto", "query": "Band Protocol BAND price"},
    {"symbol": "REN-USD", "name": "Ren", "class": "crypto", "query": "Ren REN price"},
    {"symbol": "NMR-USD", "name": "Numeraire", "class": "crypto", "query": "Numeraire NMR price"},
    {"symbol": "KNC-USD", "name": "Kyber Network", "class": "crypto", "query": "Kyber Network KNC price"},
    {"symbol": "BNT-USD", "name": "Bancor", "class": "crypto", "query": "Bancor BNT price"},
    {"symbol": "RAI-USD", "name": "Reflexer", "class": "crypto", "query": "Reflexer RAI price"},
    {"symbol": "TRU-USD", "name": "TrueFi", "class": "crypto", "query": "TrueFi TRU price"},
    {"symbol": "RPL-USD", "name": "Rocket Pool", "class": "crypto", "query": "Rocket Pool RPL price"},
    {"symbol": "GNO-USD", "name": "Gnosis", "class": "crypto", "query": "Gnosis GNO price"},
    {"symbol": "JOE-USD", "name": "JOE", "class": "crypto", "query": "JOE price"},
    {"symbol": "INDEX-USD", "name": "Index Coop", "class": "crypto", "query": "Index Coop INDEX price"},
    {"symbol": "DPI-USD", "name": "DeFi Pulse Index", "class": "crypto", "query": "DeFi Pulse Index DPI price"},
    {"symbol": "DATA-USD", "name": "Streamr", "class": "crypto", "query": "Streamr DATA price"},
    {"symbol": "CELR-USD", "name": "Celer Network", "class": "crypto", "query": "Celer Network CELR price"},
    {"symbol": "ROSE-USD", "name": "Oasis Network", "class": "crypto", "query": "Oasis Network ROSE price"},
    {"symbol": "MINA-USD", "name": "Mina", "class": "crypto", "query": "Mina MINA price"},
    {"symbol": "IDEX-USD", "name": "IDEX", "class": "crypto", "query": "IDEX price"},
    {"symbol": "CKB-USD", "name": "Nervos Network", "class": "crypto", "query": "Nervos Network CKB price"},
    {"symbol": "KMD-USD", "name": "Komodo", "class": "crypto", "query": "Komodo KMD price"},
    {"symbol": "ZEN-USD", "name": "Horizen", "class": "crypto", "query": "Horizen ZEN price"},
    {"symbol": "SC-USD", "name": "Siacooin", "class": "crypto", "query": "Siacooin SC price"},
    {"symbol": "STORJ-USD", "name": "Storj", "class": "crypto", "query": "Storj STORJ price"},
    {"symbol": "AR-USD", "name": "Arweave", "class": "crypto", "query": "Arweave AR price"},
    {"symbol": "MASS-USD", "name": "Massnet", "class": "crypto", "query": "Massnet MASS price"},
    {"symbol": "IPFS-USD", "name": "Filecoin", "class": "crypto", "query": "Filecoin IPFS price"},
    {"symbol": "BTT-USD", "name": "BitTorrent", "class": "crypto", "query": "BitTorrent BTT price"},
    {"symbol": "JST-USD", "name": "Just", "class": "crypto", "query": "Just JST price"},
    {"symbol": "WIN-USD", "name": "WinToken", "class": "crypto", "query": "WinToken WIN price"},
    {"symbol": "SAFE-USD", "name": "SafePal", "class": "crypto", "query": "SafePal SAFE price"},
    {"symbol": "RVN-USD", "name": "Ravencoin", "class": "crypto", "query": "Ravencoin RVN price"},
    {"symbol": "XVG-USD", "name": "Verge", "class": "crypto", "query": "Verge XVG price"},
    {"symbol": "XZC-USD", "name": "Zcoin", "class": "crypto", "query": "Zcoin XZC price"},
    {"symbol": "BTCP-USD", "name": "Bitcoin Private", "class": "crypto", "query": "Bitcoin Private BTCP price"},
    {"symbol": "ZCL-USD", "name": "Zclassic", "class": "crypto", "query": "Zclassic ZCL price"},
    {"symbol": "ETHW-USD", "name": "EthereumPoW", "class": "crypto", "query": "EthereumPoW ETHW price"},
    {"symbol": "ETP-USD", "name": "Metaverse ETP", "class": "crypto", "query": "Metaverse ETP ETP price"},
    {"symbol": "BCHA-USD", "name": "Bitcoin Cash ABC", "class": "crypto", "query": "Bitcoin Cash ABC BCHA price"},
    {"symbol": "XEC-USD", "name": "eCash", "class": "crypto", "query": "eCash XEC price"},
    {"symbol": "XCP-USD", "name": "Counterparty", "class": "crypto", "query": "Counterparty XCP price"},
    {"symbol": "NMC-USD", "name": "Namecoin", "class": "crypto", "query": "Namecoin NMC price"},
    {"symbol": "PPC-USD", "name": "Peercoin", "class": "crypto", "query": "Peercoin PPC price"},
    {"symbol": "XRP-USD", "name": "XRP", "class": "crypto", "query": "XRP price"},
    {"symbol": "XLM-USD", "name": "Stellar", "class": "crypto", "query": "Stellar XLM price"},
    {"symbol": "XMR-USD", "name": "Monero", "class": "crypto", "query": "Monero XMR price"},
    {"symbol": "DASH-USD", "name": "Dash", "class": "crypto", "query": "Dash DASH price"},
    {"symbol": "ZEC-USD", "name": "Zcash", "class": "crypto", "query": "Zcash ZEC price"},
    {"symbol": "BTC-USD", "name": "Bitcoin", "class": "crypto", "query": "Bitcoin price"},
    {"symbol": "ETH-USD", "name": "Ethereum", "class": "crypto", "query": "Ethereum price"},
    {"symbol": "BNB-USD", "name": "Binance Coin", "class": "crypto", "query": "Binance Coin BNB price"},
    {"symbol": "SOL-USD", "name": "Solana", "class": "crypto", "query": "Solana SOL price"},
    {"symbol": "XRP-USD", "name": "XRP", "class": "crypto", "query": "XRP price"},
    {"symbol": "ADA-USD", "name": "Cardano", "class": "crypto", "query": "Cardano ADA price"},
    {"symbol": "DOGE-USD", "name": "Dogecoin", "class": "crypto", "query": "Dogecoin DOGE price"},
    {"symbol": "DOT-USD", "name": "Polkadot", "class": "crypto", "query": "Polkadot DOT price"},
    {"symbol": "MATIC-USD", "name": "Polygon", "class": "crypto", "query": "Polygon MATIC price"},
    {"symbol": "SHIB-USD", "name": "Shiba Inu", "class": "crypto", "query": "Shiba Inu SHIB price"},
    {"symbol": "LTC-USD", "name": "Litecoin", "class": "crypto", "query": "Litecoin LTC price"},
    {"symbol": "AVAX-USD", "name": "Avalanche", "class": "crypto", "query": "Avalanche AVAX price"},
    {"symbol": "TRX-USD", "name": "TRON", "class": "crypto", "query": "TRON TRX price"},
    {"symbol": "LINK-USD", "name": "Chainlink", "class": "crypto", "query": "Chainlink LINK price"},
    {"symbol": "ATOM-USD", "name": "Cosmos", "class": "crypto", "query": "Cosmos ATOM price"},
    {"symbol": "UNI-USD", "name": "Uniswap", "class": "crypto", "query": "Uniswap UNI price"},
    {"symbol": "XLM-USD", "name": "Stellar", "class": "crypto", "query": "Stellar XLM price"},
    {"symbol": "BCH-USD", "name": "Bitcoin Cash", "class": "crypto", "query": "Bitcoin Cash BCH price"},
    {"symbol": "ALGO-USD", "name": "Algorand", "class": "crypto", "query": "Algorand ALGO price"},
    {"symbol": "VET-USD", "name": "VeChain", "class": "crypto", "query": "VeChain VET price"},
    {"symbol": "FIL-USD", "name": "Filecoin", "class": "crypto", "query": "Filecoin FIL price"},
    {"symbol": "ICP-USD", "name": "Internet Computer", "class": "crypto", "query": "Internet Computer ICP price"},
    {"symbol": "NEAR-USD", "name": "NEAR Protocol", "class": "crypto", "query": "NEAR Protocol NEAR price"},
    {"symbol": "AAVE-USD", "name": "Aave", "class": "crypto", "query": "Aave AAVE price"},
    {"symbol": "MKR-USD", "name": "Maker", "class": "crypto", "query": "Maker MKR price"},
    {"symbol": "COMP-USD", "name": "Compound", "class": "crypto", "query": "Compound COMP price"},
    {"symbol": "YFI-USD", "name": "yearn.finance", "class": "crypto", "query": "yearn.finance YFI price"},
    {"symbol": "SUSHI-USD", "name": "SushiSwap", "class": "crypto", "query": "SushiSwap SUSHI price"},
    {"symbol": "CRV-USD", "name": "Curve DAO", "class": "crypto", "query": "Curve DAO CRV price"},
    {"symbol": "1INCH-USD", "name": "1inch", "class": "crypto", "query": "1inch 1INCH price"},
    {"symbol": "SNX-USD", "name": "Synthetix", "class": "crypto", "query": "Synthetix SNX price"},
    {"symbol": "LDO-USD", "name": "Lido DAO", "class": "crypto", "query": "Lido DAO LDO price"},
    {"symbol": "STX-USD", "name": "Stacks", "class": "crypto", "query": "Stacks STX price"},
    {"symbol": "OP-USD", "name": "Optimism", "class": "crypto", "query": "Optimism OP price"},
    {"symbol": "ARB-USD", "name": "Arbitrum", "class": "crypto", "query": "Arbitrum ARB price"},
    {"symbol": "APT-USD", "name": "Aptos", "class": "crypto", "query": "Aptos APT price"},
    {"symbol": "SUI-USD", "name": "Sui", "class": "crypto", "query": "Sui SUI price"},
    {"symbol": "SEI-USD", "name": "Sei", "class": "crypto", "query": "Sei SEI price"},
    {"symbol": "TIA-USD", "name": "Celestia", "class": "crypto", "query": "Celestia TIA price"},
    {"symbol": "QNT-USD", "name": "Quant", "class": "crypto", "query": "Quant QNT price"},
    {"symbol": "HBAR-USD", "name": "Hedera Hashgraph", "class": "crypto", "query": "Hedera Hashgraph HBAR price"},
    {"symbol": "NEO-USD", "name": "NEO", "class": "crypto", "query": "NEO price"},
    {"symbol": "XEM-USD", "name": "NEM", "class": "crypto", "query": "NEM XEM price"},
    {"symbol": "XDC-USD", "name": "XDC Network", "class": "crypto", "query": "XDC Network XDC price"},
    {"symbol": "FLOW-USD", "name": "Flow", "class": "crypto", "query": "Flow FLOW price"},
    {"symbol": "HNT-USD", "name": "Helium", "class": "crypto", "query": "Helium HNT price"},
    {"symbol": "IOTA-USD", "name": "IOTA", "class": "crypto", "query": "IOTA price"},
    {"symbol": "EOS-USD", "name": "EOS", "class": "crypto", "query": "EOS price"},
    {"symbol": "XTZ-USD", "name": "Tezos", "class": "crypto", "query": "Tezos XTZ price"},
    {"symbol": "ALGO-USD", "name": "Algorand", "class": "crypto", "query": "Algorand ALGO price"},
    {"symbol": "ZIL-USD", "name": "Zilliqa", "class": "crypto", "query": "Zilliqa ZIL price"},
    {"symbol": "ONT-USD", "name": "Ontology", "class": "crypto", "query": "Ontology ONT price"},
    {"symbol": "QTUM-USD", "name": "Qtum", "class": "crypto", "query": "Qtum QTUM price"},
    {"symbol": "KAVA-USD", "name": "Kava", "class": "crypto", "query": "Kava KAVA price"},
    {"symbol": "CELO-USD", "name": "Celo", "class": "crypto", "query": "Celo CELO price"},
    {"symbol": "MINA-USD", "name": "Mina", "class": "crypto", "query": "Mina MINA price"},
    {"symbol": "ROSE-USD", "name": "Oasis Network", "class": "crypto", "query": "Oasis Network ROSE price"},
    {"symbol": "SCRT-USD", "name": "Secret", "class": "crypto", "query": "Secret SCRT price"},
    {"symbol": "BLZ-USD", "name": "Bluzelle", "class": "crypto", "query": "Bluzelle BLZ price"},
    {"symbol": "NKN-USD", "name": "NKN", "class": "crypto", "query": "NKN price"},
    {"symbol": "PHX-USD", "name": "Phoenix", "class": "crypto", "query": "Phoenix PHX price"},
    {"symbol": "AKRO-USD", "name": "Akropolis", "class": "crypto", "query": "Akropolis AKRO price"},
    {"symbol": "BAND-USD", "name": "Band Protocol", "class": "crypto", "query": "Band Protocol BAND price"},
    {"symbol": "LRC-USD", "name": "Loopring", "class": "crypto", "query": "Loopring LRC price"},
    {"symbol": "IMX-USD", "name": "Immutable X", "class": "crypto", "query": "Immutable X IMX price"},
    {"symbol": "GALA-USD", "name": "Gala", "class": "crypto", "query": "Gala GALA price"},
    {"symbol": "SAND-USD", "name": "The Sandbox", "class": "crypto", "query": "The Sandbox SAND price"},
    {"symbol": "MANA-USD", "name": "Decentraland", "class": "crypto", "query": "Decentraland MANA price"},
    {"symbol": "AXS-USD", "name": "Axie Infinity", "class": "crypto", "query": "Axie Infinity AXS price"},
    {"symbol": "ENJ-USD", "name": "Enjin Coin", "class": "crypto", "query": "Enjin Coin ENJ price"},
    {"symbol": "CHZ-USD", "name": "Chiliz", "class": "crypto", "query": "Chiliz CHZ price"},
    {"symbol": "HIVE-USD", "name": "Hive", "class": "crypto", "query": "Hive HIVE price"},
    {"symbol": "STEEM-USD", "name": "Steem", "class": "crypto", "query": "Steem STEEM price"},
    {"symbol": "WAX-USD", "name": "WAX", "class": "crypto", "query": "WAX WAX price"},
    {"symbol": "EOS-USD", "name": "EOS", "class": "crypto", "query": "EOS price"},
    {"symbol": "TRX-USD", "name": "TRON", "class": "crypto", "query": "TRON TRX price"},
    {"symbol": "ONT-USD", "name": "Ontology", "class": "crypto", "query": "Ontology ONT price"},
    {"symbol": "XLM-USD", "name": "Stellar", "class": "crypto", "query": "Stellar XLM price"},
    {"symbol": "XRP-USD", "name": "XRP", "class": "crypto", "query": "XRP price"},
    {"symbol": "XMR-USD", "name": "Monero", "class": "crypto", "query": "Monero XMR price"},
    {"symbol": "DASH-USD", "name": "Dash", "class": "crypto", "query": "Dash DASH price"},
    {"symbol": "ZEC-USD", "name": "Zcash", "class": "crypto", "query": "Zcash ZEC price"},
    {"symbol": "ETC-USD", "name": "Ethereum Classic", "class": "crypto", "query": "Ethereum Classic ETC price"},
    {"symbol": "BCH-USD", "name": "Bitcoin Cash", "class": "crypto", "query": "Bitcoin Cash BCH price"},
    {"symbol": "LTC-USD", "name": "Litecoin", "class": "crypto", "query": "Litecoin LTC price"},
    {"symbol": "DOGE-USD", "name": "Dogecoin", "class": "crypto", "query": "Dogecoin DOGE price"},
    {"symbol": "SHIB-USD", "name": "Shiba Inu", "class": "crypto", "query": "Shiba Inu SHIB price"},
    {"symbol": "PEPE-USD", "name": "Pepe", "class": "crypto", "query": "Pepe PEPE price"},
    {"symbol": "FLOKI-USD", "name": "Floki", "class": "crypto", "query": "Floki FLOKI price"},
    {"symbol": "BONK-USD", "name": "Bonk", "class": "crypto", "query": "Bonk BONK price"},
    {"symbol": "WIF-USD", "name": "dogwifhat", "class": "crypto", "query": "dogwifhat WIF price"},
    {"symbol": "ORDI-USD", "name": "Ordinals", "class": "crypto", "query": "Ordinals ORDI price"},
    {"symbol": "SATS-USD", "name": "1000SATS", "class": "crypto", "query": "1000SATS SATS price"},
    {"symbol": "TIA-USD", "name": "Celestia", "class": "crypto", "query": "Celestia TIA price"},
    {"symbol": "SEI-USD", "name": "Sei", "class": "crypto", "query": "Sei SEI price"},
    {"symbol": "SUI-USD", "name": "Sui", "class": "crypto", "query": "Sui SUI price"},
    {"symbol": "APT-USD", "name": "Aptos", "class": "crypto", "query": "Aptos APT price"},
    {"symbol": "OP-USD", "name": "Optimism", "class": "crypto", "query": "Optimism OP price"},
    {"symbol": "ARB-USD", "name": "Arbitrum", "class": "crypto", "query": "Arbitrum ARB price"},
    {"symbol": "LDO-USD", "name": "Lido DAO", "class": "crypto", "query": "Lido DAO LDO price"},
    {"symbol": "GMX-USD", "name": "GMX", "class": "crypto", "query": "GMX price"},
    {"symbol": "FXS-USD", "name": "Frax Share", "class": "crypto", "query": "Frax Share FXS price"},
    {"symbol": "CRV-USD", "name": "Curve DAO", "class": "crypto", "query": "Curve DAO CRV price"},
    {"symbol": "CVX-USD", "name": "Convex Finance", "class": "crypto", "query": "Convex Finance CVX price"},
    {"symbol": "BAL-USD", "name": "Balancer", "class": "crypto", "query": "Balancer BAL price"},
    {"symbol": "UNI-USD", "name": "Uniswap", "class": "crypto", "query": "Uniswap UNI price"},
    {"symbol": "SUSHI-USD", "name": "SushiSwap", "class": "crypto", "query": "SushiSwap SUSHI price"},
    {"symbol": "1INCH-USD", "name": "1inch", "class": "crypto", "query": "1inch 1INCH price"},
    {"symbol": "AAVE-USD", "name": "Aave", "class": "crypto", "query": "Aave AAVE price"},
    {"symbol": "COMP-USD", "name": "Compound", "class": "crypto", "query": "Compound COMP price"},
    {"symbol": "YFI-USD", "name": "yearn.finance", "class": "crypto", "query": "yearn.finance YFI price"},
    {"symbol": "MKR-USD", "name": "Maker", "class": "crypto", "query": "Maker MKR price"},
    {"symbol": "SNX-USD", "name": "Synthetix", "class": "crypto", "query": "Synthetix SNX price"},
    {"symbol": "PERP-USD", "name": "Perpetual Protocol", "class": "crypto", "query": "Perpetual Protocol PERP price"},
    {"symbol": "UMA-USD", "name": "UMA", "class": "crypto", "query": "UMA price"},
    {"symbol": "GRT-USD", "name": "The Graph", "class": "crypto", "query": "The Graph GRT price"},
    {"symbol": "BAND-USD", "name": "Band Protocol", "class": "crypto", "query": "Band Protocol BAND price"},
    {"symbol": "LINK-USD", "name": "Chainlink", "class": "crypto", "query": "Chainlink LINK price"},
    {"symbol": "UMA-USD", "name": "UMA", "class": "crypto", "query": "UMA price"},
    {"symbol": "REN-USD", "name": "Ren", "class": "crypto", "query": "Ren REN price"},
    {"symbol": "NMR-USD", "name": "Numeraire", "class": "crypto", "query": "Numeraire NMR price"},
    {"symbol": "REP-USD", "name": "Augur", "class": "crypto", "query": "Augur REP price"},
    {"symbol": "KNC-USD", "name": "Kyber Network", "class": "crypto", "query": "Kyber Network KNC price"},
    {"symbol": "BNT-USD", "name": "Bancor", "class": "crypto", "query": "Bancor BNT price"},
    {"symbol": "MLN-USD", "name": "Enzyme", "class": "crypto", "query": "Enzyme MLN price"},
    {"symbol": "RAI-USD", "name": "Reflexer", "class": "crypto", "query": "Reflexer RAI price"},
    {"symbol": "FEI-USD", "name": "Fei USD", "class": "crypto", "query": "Fei USD FEI price"},
    {"symbol": "TRU-USD", "name": "TrueFi", "class": "crypto", "query": "TrueFi TRU price"},
    {"symbol": "RPL-USD", "name": "Rocket Pool", "class": "crypto", "query": "Rocket Pool RPL price"},
    {"symbol": "FX-USD", "name": "Function X", "class": "crypto", "query": "Function X FX price"},
    {"symbol": "MASK-USD", "name": "Mask Network", "class": "crypto", "query": "Mask Network MASK price"},
    {"symbol": "RAD-USD", "name": "Radicle", "class": "crypto", "query": "Radicle RAD price"},
    {"symbol": "GNO-USD", "name": "Gnosis", "class": "crypto", "query": "Gnosis GNO price"},
    {"symbol": "DXM-USD", "name": "DXdao", "class": "crypto", "query": "DXdao DXM price"},
    {"symbol": "LDO-USD", "name": "Lido DAO", "class": "crypto", "query": "Lido DAO LDO price"},
    {"symbol": "PENDLE-USD", "name": "Pendle", "class": "crypto", "query": "Pendle PENDLE price"},
    {"symbol": "JOE-USD", "name": "JOE", "class": "crypto", "query": "JOE price"},
    {"symbol": "TRAC-USD", "name": "OriginTrail", "class": "crypto", "query": "OriginTrail TRAC price"},
    {"symbol": "BTRST-USD", "name": "BarnBridge", "class": "crypto", "query": "BarnBridge BTRST price"},
    {"symbol": "INDEX-USD", "name": "Index Coop", "class": "crypto", "query": "Index Coop INDEX price"},
    {"symbol": "DPI-USD", "name": "DeFi Pulse Index", "class": "crypto", "query": "DeFi Pulse Index DPI price"},
    {"symbol": "MVI-USD", "name": "Metaverse Index", "class": "crypto", "query": "Metaverse Index MVI price"},
    {"symbol": "DATA-USD", "name": "Streamr", "class": "crypto", "query": "Streamr DATA price"},
    {"symbol": "CELR-USD", "name": "Celer Network", "class": "crypto", "query": "Celer Network CELR price"},
    {"symbol": "NYM-USD", "name": "Nym", "class": "crypto", "query": "Nym NYM price"},
    {"symbol": "ROSE-USD", "name": "Oasis Network", "class": "crypto", "query": "Oasis Network ROSE price"},
    {"symbol": "MINA-USD", "name": "Mina", "class": "crypto", "query": "Mina MINA price"},
    {"symbol": "APT-USD", "name": "Aptos", "class": "crypto", "query": "Aptos APT price"},
    {"symbol": "SUI-USD", "name": "Sui", "class": "crypto", "query": "Sui SUI price"},
    {"symbol": "NEON-USD", "name": "Neon", "class": "crypto", "query": "Neon NEON price"},
    {"symbol": "ALEPH-USD", "name": "Aleph.im", "class": "crypto", "query": "Aleph.im ALEPH price"},
    {"symbol": "IDEX-USD", "name": "IDEX", "class": "crypto", "query": "IDEX price"},
    {"symbol": "LAT-USD", "name": "PlatON", "class": "crypto", "query": "PlatON LAT price"},
    {"symbol": "CKB-USD", "name": "Nervos Network", "class": "crypto", "query": "Nervos Network CKB price"},
    {"symbol": "GRS-USD", "name": "Groestlcoin", "class": "crypto", "query": "Groestlcoin GRS price"},
    {"symbol": "XRP-USD", "name": "XRP", "class": "crypto", "query": "XRP price"},
    {"symbol": "XLM-USD", "name": "Stellar", "class": "crypto", "query": "Stellar XLM price"},
    {"symbol": "XMR-USD", "name": "Monero", "class": "crypto", "query": "Monero XMR price"},
    {"symbol": "DASH-USD", "name": "Dash", "class": "crypto", "query": "Dash DASH price"},
    {"symbol": "ZEC-USD", "name": "Zcash", "class": "crypto", "query": "Zcash ZEC price"},
    {"symbol": "BTG-USD", "name": "Bitcoin Gold", "class": "crypto", "query": "Bitcoin Gold BTG price"},
    {"symbol": "BTG-USD", "name": "Bitcoin Gold", "class": "crypto", "query": "Bitcoin Gold BTG price"},
    {"symbol": "KMD-USD", "name": "Komodo", "class": "crypto", "query": "Komodo KMD price"},
    {"symbol": "ZEN-USD", "name": "Horizen", "class": "crypto", "query": "Horizen ZEN price"},
    {"symbol": "ARRR-USD", "name": "Pirate Chain", "class": "crypto", "query": "Pirate Chain ARRR price"},
    {"symbol": "SC-USD", "name": "Siacooin", "class": "crypto", "query": "Siacooin SC price"},
    {"symbol": "STORJ-USD", "name": "Storj", "class": "crypto", "query": "Storj STORJ price"},
    {"symbol": "FIL-USD", "name": "Filecoin", "class": "crypto", "query": "Filecoin FIL price"},
    {"symbol": "AR-USD", "name": "Arweave", "class": "crypto", "query": "Arweave AR price"},
    {"symbol": "MASS-USD", "name": "Massnet", "class": "crypto", "query": "Massnet MASS price"},
    {"symbol": "IPFS-USD", "name": "Filecoin", "class": "crypto", "query": "Filecoin IPFS price"},
    {"symbol": "BTT-USD", "name": "BitTorrent", "class": "crypto", "query": "BitTorrent BTT price"},
    {"symbol": "JST-USD", "name": "Just", "class": "crypto", "query": "Just JST price"},
    {"symbol": "WIN-USD", "name": "WinToken", "class": "crypto", "query": "WinToken WIN price"},
    {"symbol": "SAFE-USD", "name": "SafePal", "class": "crypto", "query": "SafePal SAFE price"},
    {"symbol": "RVN-USD", "name": "Ravencoin", "class": "crypto", "query": "Ravencoin RVN price"},
    {"symbol": "XVG-USD", "name": "Verge", "class": "crypto", "query": "Verge XVG price"},
    {"symbol": "XZC-USD", "name": "Zcoin", "class": "crypto", "query": "Zcoin XZC price"},
    {"symbol": "BTCP-USD", "name": "Bitcoin Private", "class": "crypto", "query": "Bitcoin Private BTCP price"},
    {"symbol": "ZCL-USD", "name": "Zclassic", "class": "crypto", "query": "Zclassic ZCL price"},
    {"symbol": "ETC-USD", "name": "Ethereum Classic", "class": "crypto", "query": "Ethereum Classic ETC price"},
    {"symbol": "ETHW-USD", "name": "EthereumPoW", "class": "crypto", "query": "EthereumPoW ETHW price"},
    {"symbol": "ETP-USD", "name": "Metaverse ETP", "class": "crypto", "query": "Metaverse ETP ETP price"},
    {"symbol": "BCHA-USD", "name": "Bitcoin Cash ABC", "class": "crypto", "query": "Bitcoin Cash ABC BCHA price"},
    {"symbol": "XEC-USD", "name": "eCash", "class": "crypto", "query": "eCash XEC price"},
    {"symbol": "BTG-USD", "name": "Bitcoin Gold", "class": "crypto", "query": "Bitcoin Gold BTG price"},
    {"symbol": "ZEN-USD", "name": "Horizen", "class": "crypto", "query": "Horizen ZEN price"},
    {"symbol": "XCP-USD", "name": "Counterparty", "class": "crypto", "query": "Counterparty XCP price"},
    {"symbol": "NMC-USD", "name": "Namecoin", "class": "crypto", "query": "Namecoin NMC price"},
    {"symbol": "PPC-USD", "name": "Peercoin", "class": "crypto", "query": "Peercoin PPC price"},
    
    # Forex Major Pairs
    {"symbol": "EURUSD=X", "name": "EUR/USD", "class": "forex", "query": "EUR USD euro dollar forex"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "class": "forex", "query": "GBP USD pound dollar forex"},
    {"symbol": "USDJPY=X", "name": "USD/JPY", "class": "forex", "query": "USD JPY dollar yen forex"},
    {"symbol": "USDCHF=X", "name": "USD/CHF", "class": "forex", "query": "USD CHF dollar swiss franc forex"},
    {"symbol": "USDCAD=X", "name": "USD/CAD", "class": "forex", "query": "USD CAD dollar canadian dollar forex"},
    {"symbol": "AUDUSD=X", "name": "AUD/USD", "class": "forex", "query": "AUD USD australian dollar forex"},
    {"symbol": "NZDUSD=X", "name": "NZD/USD", "class": "forex", "query": "NZD USD new zealand dollar forex"},
    {"symbol": "EURGBP=X", "name": "EUR/GBP", "class": "forex", "query": "EUR GBP euro pound forex"},
    {"symbol": "EURJPY=X", "name": "EUR/JPY", "class": "forex", "query": "EUR JPY euro yen forex"},
    {"symbol": "EURCHF=X", "name": "EUR/CHF", "class": "forex", "query": "EUR CHF euro swiss franc forex"},
    {"symbol": "EURAUD=X", "name": "EUR/AUD", "class": "forex", "query": "EUR AUD euro australian dollar forex"},
    {"symbol": "EURCAD=X", "name": "EUR/CAD", "class": "forex", "query": "EUR CAD euro canadian dollar forex"},
    {"symbol": "GBPJPY=X", "name": "GBP/JPY", "class": "forex", "query": "GBP JPY pound yen forex"},
    {"symbol": "GBPCHF=X", "name": "GBP/CHF", "class": "forex", "query": "GBP CHF pound swiss franc forex"},
    {"symbol": "GBPAUD=X", "name": "GBP/AUD", "class": "forex", "query": "GBP AUD pound australian dollar forex"},
    {"symbol": "GBPCAD=X", "name": "GBP/CAD", "class": "forex", "query": "GBP CAD pound canadian dollar forex"},
    {"symbol": "CHFJPY=X", "name": "CHF/JPY", "class": "forex", "query": "CHF JPY swiss franc yen forex"},
    {"symbol": "CADJPY=X", "name": "CAD/JPY", "class": "forex", "query": "CAD JPY canadian dollar yen forex"},
    {"symbol": "AUDJPY=X", "name": "AUD/JPY", "class": "forex", "query": "AUD JPY australian dollar yen forex"},
    {"symbol": "NZDJPY=X", "name": "NZD/JPY", "class": "forex", "query": "NZD JPY new zealand dollar yen forex"},
    {"symbol": "AUDCHF=X", "name": "AUD/CHF", "class": "forex", "query": "AUD CHF australian dollar swiss franc forex"},
    {"symbol": "NZDCHF=X", "name": "NZD/CHF", "class": "forex", "query": "NZD CHF new zealand dollar swiss franc forex"},
    {"symbol": "AUDCAD=X", "name": "AUD/CAD", "class": "forex", "query": "AUD CAD australian dollar canadian dollar forex"},
    {"symbol": "NZDCAD=X", "name": "NZD/CAD", "class": "forex", "query": "NZD CAD new zealand dollar canadian dollar forex"},
    {"symbol": "EURNZD=X", "name": "EUR/NZD", "class": "forex", "query": "EUR NZD euro new zealand dollar forex"},
    {"symbol": "GBPNZD=X", "name": "GBP/NZD", "class": "forex", "query": "GBP NZD pound new zealand dollar forex"},
    {"symbol": "EURSEK=X", "name": "EUR/SEK", "class": "forex", "query": "EUR SEK euro swedish krona forex"},
    {"symbol": "EURNOK=X", "name": "EUR/NOK", "class": "forex", "query": "EUR NOK euro norwegian krone forex"},
    {"symbol": "EURDKK=X", "name": "EUR/DKK", "class": "forex", "query": "EUR DKK euro danish krone forex"},
    {"symbol": "EURMXN=X", "name": "EUR/MXN", "class": "forex", "query": "EUR MXN euro mexican peso forex"},
    {"symbol": "EURSGD=X", "name": "EUR/SGD", "class": "forex", "query": "EUR SGD euro singapore dollar forex"},
    {"symbol": "EURHKD=X", "name": "EUR/HKD", "class": "forex", "query": "EUR HKD euro hong kong dollar forex"},
    {"symbol": "EURCNY=X", "name": "EUR/CNY", "class": "forex", "query": "EUR CNY euro chinese yuan forex"},
    {"symbol": "EURINR=X", "name": "EUR/INR", "class": "forex", "query": "EUR INR euro indian rupee forex"},
    {"symbol": "EURTRY=X", "name": "EUR/TRY", "class": "forex", "query": "EUR TRY euro turkish lira forex"},
    {"symbol": "EURZAR=X", "name": "EUR/ZAR", "class": "forex", "query": "EUR ZAR euro south african rand forex"},
    {"symbol": "EURRUB=X", "name": "EUR/RUB", "class": "forex", "query": "EUR RUB euro russian ruble forex"},
    {"symbol": "USDRUB=X", "name": "USD/RUB", "class": "forex", "query": "USD RUB dollar russian ruble forex"},
    {"symbol": "USDTRY=X", "name": "USD/TRY", "class": "forex", "query": "USD TRY dollar turkish lira forex"},
    {"symbol": "USDZAR=X", "name": "USD/ZAR", "class": "forex", "query": "USD ZAR dollar south african rand forex"},
    {"symbol": "USDMXN=X", "name": "USD/MXN", "class": "forex", "query": "USD MXN dollar mexican peso forex"},
    {"symbol": "USDBRL=X", "name": "USD/BRL", "class": "forex", "query": "USD BRL dollar brazilian real forex"},
    {"symbol": "USDCLP=X", "name": "USD/CLP", "class": "forex", "query": "USD CLP dollar chilean peso forex"},
    {"symbol": "USDCOP=X", "name": "USD/COP", "class": "forex", "query": "USD COP dollar colombian peso forex"},
    {"symbol": "USDPEN=X", "name": "USD/PEN", "class": "forex", "query": "USD PEN dollar peruvian sol forex"},
    {"symbol": "USDCNY=X", "name": "USD/CNY", "class": "forex", "query": "USD CNY dollar chinese yuan forex"},
    {"symbol": "USDHKD=X", "name": "USD/HKD", "class": "forex", "query": "USD HKD dollar hong kong dollar forex"},
    {"symbol": "USDSGD=X", "name": "USD/SGD", "class": "forex", "query": "USD SGD dollar singapore dollar forex"},
    {"symbol": "USDINR=X", "name": "USD/INR", "class": "forex", "query": "USD INR dollar indian rupee forex"},
    {"symbol": "USDKRW=X", "name": "USD/KRW", "class": "forex", "query": "USD KRW dollar south korean won forex"},
    {"symbol": "USDIDR=X", "name": "USD/IDR", "class": "forex", "query": "USD IDR dollar indonesian rupiah forex"},
    {"symbol": "USDPHP=X", "name": "USD/PHP", "class": "forex", "query": "USD PHP dollar philippine peso forex"},
    {"symbol": "USDTHB=X", "name": "USD/THB", "class": "forex", "query": "USD THB dollar thai baht forex"},
    {"symbol": "USDMYR=X", "name": "USD/MYR", "class": "forex", "query": "USD MYR dollar malaysian ringgit forex"},
    {"symbol": "USDVND=X", "name": "USD/VND", "class": "forex", "query": "USD VND dollar vietnamese dong forex"},
    
    # Commodities (front-month futures) - removed LB=F, ME=F, RR=F, RS=F (unavailable)
    {"symbol": "GC=F", "name": "Gold", "class": "commodity", "query": "gold price"},
    {"symbol": "SI=F", "name": "Silver", "class": "commodity", "query": "silver price"},
    {"symbol": "CL=F", "name": "WTI crude oil", "class": "commodity", "query": "crude oil price"},
    {"symbol": "BZ=F", "name": "Brent crude oil", "class": "commodity", "query": "brent oil price"},
    {"symbol": "NG=F", "name": "Natural gas", "class": "commodity", "query": "natural gas price"},
    {"symbol": "HG=F", "name": "Copper", "class": "commodity", "query": "copper price"},
    {"symbol": "PL=F", "name": "Platinum", "class": "commodity", "query": "platinum price"},
    {"symbol": "PA=F", "name": "Palladium", "class": "commodity", "query": "palladium price"},
    {"symbol": "ZC=F", "name": "Corn", "class": "commodity", "query": "corn futures price"},
    {"symbol": "ZW=F", "name": "Wheat", "class": "commodity", "query": "wheat futures price"},
    {"symbol": "ZS=F", "name": "Soybeans", "class": "commodity", "query": "soybeans futures price"},
    {"symbol": "ZM=F", "name": "Soybean Meal", "class": "commodity", "query": "soybean meal futures price"},
    {"symbol": "ZL=F", "name": "Soybean Oil", "class": "commodity", "query": "soybean oil futures price"},
    {"symbol": "SB=F", "name": "Sugar", "class": "commodity", "query": "sugar futures price"},
    {"symbol": "KC=F", "name": "Coffee", "class": "commodity", "query": "coffee futures price"},
    {"symbol": "CC=F", "name": "Cocoa", "class": "commodity", "query": "cocoa futures price"},
    {"symbol": "CT=F", "name": "Cotton", "class": "commodity", "query": "cotton futures price"},
    {"symbol": "RB=F", "name": "Gasoline", "class": "commodity", "query": "gasoline futures price"},
    {"symbol": "HO=F", "name": "Heating Oil", "class": "commodity", "query": "heating oil futures price"},
    {"symbol": "HE=F", "name": "Lean Hogs", "class": "commodity", "query": "lean hogs futures price"},
    {"symbol": "LE=F", "name": "Live Cattle", "class": "commodity", "query": "live cattle futures price"},
    {"symbol": "GF=F", "name": "Feeder Cattle", "class": "commodity", "query": "feeder cattle futures price"},
    {"symbol": "OJ=F", "name": "Orange Juice", "class": "commodity", "query": "orange juice futures price"},

    # ============================================================================
    # EXTENDED ASSETS - Load from provider modules
    # ============================================================================

    # Extended Crypto (300+ from crypto_extended_300.py)
    # Note: We format these to match watchlist structure
] + [
    {
        "symbol": f"{crypto['symbol']}-USD",
        "name": crypto["name"],
        "class": "crypto",
        "query": f"{crypto['name']} {crypto['symbol']} price",
        "coingecko_id": crypto.get("coingecko_id")
    }
    for crypto in crypto_extended_300.TOP_300_CRYPTO
    if crypto["symbol"] not in ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "DOT", "AVAX", "LINK"]  # Avoid duplicates
] + [
    # Extended Stocks (500+ from stocks_global_500.py)
    {
        "symbol": stock["symbol"],
        "name": stock["name"],
        "class": "stock",
        "query": f"{stock['name']} {stock['symbol']} stock"
    }
    for stock in stocks_global_500.GLOBAL_STOCKS_500
    if stock["symbol"] not in ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "JNJ", "WMT", "PG", "XOM", "CVX", "KO", "PEP", "MRK", "ABBV", "AVGO", "COST", "CSCO", "ADBE", "CRM", "NFLX", "AMD", "INTC", "PYPL", "DIS", "NKE", "ABT", "T", "IBM", "ORCL", "ACN", "QCOM", "TXN", "SHOP", "SPOT", "UBER", "LYFT", "SNAP", "COIN", "ROKU", "ZM", "DOCU", "SNOW", "PLTR", "U", "RBLX", "AFRM", "UPST", "HOOD", "GME", "AMC"]  # Avoid duplicates
] + [
    # Extended Forex (100+ from forex_global_100.py)
    {
        "symbol": pair["symbol"],
        "name": pair["name"],
        "class": "forex",
        "query": f"{pair['name']} forex"
    }
    for pair in forex_global_100.FOREX_PAIRS_100
    if pair["symbol"] not in ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X", "AUDUSD=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "EURCHF=X", "EURAUD=X", "EURCAD=X", "GBPJPY=X", "GBPCHF=X", "GBPAUD=X", "GBPCAD=X", "CHFJPY=X", "CADJPY=X", "AUDJPY=X", "NZDJPY=X", "AUDCHF=X", "NZDCHF=X", "AUDCAD=X", "NZDCAD=X", "EURNZD=X", "EURSEK=X", "EURNOK=X", "EURDKK=X", "EURMXN=X", "EURSGD=X", "EURHKD=X", "EURCNY=X", "EURINR=X", "EURTRY=X", "EURZAR=X", "EURRUB=X", "USDRUB=X", "USDTRY=X", "USDZAR=X", "USDMXN=X", "USDBRL=X", "USDCLP=X", "USDCOP=X", "USDPEN=X", "USDCNY=X", "USDHKD=X", "USDSGD=X", "USDINR=X", "USDKRW=X", "USDIDR=X", "USDPHP=X", "USDTHB=X", "USDMYR=X", "USDVND=X"]  # Avoid duplicates
] + [
    # Extended Commodities (50+ from commodities_global_50.py)
    {
        "symbol": commodity["symbol"],
        "name": commodity["name"],
        "class": "commodity",
        "query": f"{commodity['name']} price"
    }
    for commodity in commodities_global_50.COMMODITIES_50
    if commodity["symbol"] not in ["GC=F", "SI=F", "CL=F", "BZ=F", "NG=F", "HG=F", "PL=F", "PA=F", "ZC=F", "ZW=F", "ZS=F", "ZM=F", "ZL=F", "SB=F", "KC=F", "CC=F", "CT=F", "RB=F", "HO=F", "HE=F", "LE=F", "GF=F", "OJ=F"]  # Avoid duplicates
]

# Deduplicate watchlist to avoid duplicate API calls and display issues
seen_symbols = set()
WATCHLIST = []
for asset in _RAW_WATCHLIST:
    if asset["symbol"] not in seen_symbols:
        seen_symbols.add(asset["symbol"])
        WATCHLIST.append(asset)

_BY_SYMBOL = {a["symbol"].upper(): a for a in WATCHLIST}


def infer_class(symbol: str) -> str:
    s = symbol.upper()
    if s.endswith("=F"):
        return "commodity"
    if s.endswith("=X"):
        return "forex"
    if re.search(r"-(USD|USDT|EUR|GBP|BTC|ETH)$", s):
        return "crypto"
    return "stock"


def asset_info(symbol: str) -> dict:
    """Watchlist info for a symbol, or a sensible guess for one the user typed in."""
    known = _BY_SYMBOL.get(symbol.upper())
    if known:
        return known
    cls = infer_class(symbol)
    s = symbol.upper()
    if cls == "forex":
        pair = s.replace("=X", "")
        query = f"{pair[:3]} {pair[3:6]} forex"
    elif cls == "crypto":
        query = f"{s.split('-')[0]} crypto price"
    elif cls == "commodity":
        query = f"{s.replace('=F', '')} futures price"
    else:
        query = f"{s} stock"
    return {"symbol": symbol, "name": symbol, "class": cls, "query": query}
