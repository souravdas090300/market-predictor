"""Central settings. Edit the WATCHLIST to track the assets you care about."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Where every signal is logged so its real outcome can be checked later.
DB_PATH = ROOT / "data" / "signals.db"

# Reading links: private, local and reserved addresses are blocked. Only tests switch this on.
ALLOW_PRIVATE_URLS = False

# How many trading days ahead the model looks.
HORIZON_DAYS = 5

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
API_CACHE_SECONDS = 300

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

WATCHLIST = [
    # Shares
    {"symbol": "AAPL", "name": "Apple", "class": "stock", "query": "Apple AAPL stock"},
    {"symbol": "MSFT", "name": "Microsoft", "class": "stock", "query": "Microsoft MSFT stock"},
    {"symbol": "NVDA", "name": "Nvidia", "class": "stock", "query": "Nvidia NVDA stock"},
    {"symbol": "^GSPC", "name": "S&P 500", "class": "stock", "query": "S&P 500 stock market"},
    # Crypto
    {"symbol": "BTC-USD", "name": "Bitcoin", "class": "crypto", "query": "Bitcoin price"},
    {"symbol": "ETH-USD", "name": "Ethereum", "class": "crypto", "query": "Ethereum price"},
    # Forex
    {"symbol": "EURUSD=X", "name": "EUR/USD", "class": "forex", "query": "EUR USD euro dollar forex"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "class": "forex", "query": "GBP USD pound dollar forex"},
    # Commodities (front-month futures)
    {"symbol": "GC=F", "name": "Gold", "class": "commodity", "query": "gold price"},
    {"symbol": "SI=F", "name": "Silver", "class": "commodity", "query": "silver price"},
    {"symbol": "CL=F", "name": "WTI crude oil", "class": "commodity", "query": "crude oil price"},
    {"symbol": "NG=F", "name": "Natural gas", "class": "commodity", "query": "natural gas price"},
    {"symbol": "HG=F", "name": "Copper", "class": "commodity", "query": "copper price"},
]

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

# Advanced features
DB_PATH = ROOT / "signals.db"
HISTORY_KEEP_DAYS = 90
BULK_LIMIT = 50  # Max symbols in one /bulk request

# URL fetching
FETCH_TIMEOUT = 10
FETCH_MAX_CHARS = 50000
# PDF and CSV
MAX_UPLOAD_BYTES = 5_000_000
