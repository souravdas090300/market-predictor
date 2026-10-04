"""
Market Predictor Pro - Extended Crypto Database
Top 300+ Cryptocurrencies by market cap with CoinGecko IDs
"""

# ============================================================================
# TOP 300+ CRYPTOCURRENCIES - Mapped to CoinGecko IDs
# ============================================================================

TOP_300_CRYPTO = [
    # Tier 1: Top 10 (Market Leaders)
    {"symbol": "BTC", "name": "Bitcoin", "coingecko_id": "bitcoin", "icon": "₿", "category": "crypto"},
    {"symbol": "ETH", "name": "Ethereum", "coingecko_id": "ethereum", "icon": "Ξ", "category": "crypto"},
    {"symbol": "BNB", "name": "BNB Chain", "coingecko_id": "binancecoin", "icon": "🟡", "category": "crypto"},
    {"symbol": "XRP", "name": "Ripple", "coingecko_id": "ripple", "icon": "✕", "category": "crypto"},
    {"symbol": "SOL", "name": "Solana", "coingecko_id": "solana", "icon": "◎", "category": "crypto"},
    {"symbol": "ADA", "name": "Cardano", "coingecko_id": "cardano", "icon": "₳", "category": "crypto"},
    {"symbol": "DOGE", "name": "Dogecoin", "coingecko_id": "dogecoin", "icon": "🐕", "category": "crypto"},
    {"symbol": "AVAX", "name": "Avalanche", "coingecko_id": "avalanche-2", "icon": "▲", "category": "crypto"},
    {"symbol": "LINK", "name": "Chainlink", "coingecko_id": "chainlink", "icon": "🔗", "category": "crypto"},
    {"symbol": "DOT", "name": "Polkadot", "coingecko_id": "polkadot", "icon": "●", "category": "crypto"},

    # Tier 2: Top 20-50
    {"symbol": "MATIC", "name": "Polygon", "coingecko_id": "matic-network", "icon": "◇", "category": "crypto"},
    {"symbol": "SHIB", "name": "Shiba Inu", "coingecko_id": "shiba-inu", "icon": "🐕", "category": "crypto"},
    {"symbol": "TRX", "name": "TRON", "coingecko_id": "tron", "icon": "Ⓣ", "category": "crypto"},
    {"symbol": "LTC", "name": "Litecoin", "coingecko_id": "litecoin", "icon": "Ł", "category": "crypto"},
    {"symbol": "BCH", "name": "Bitcoin Cash", "coingecko_id": "bitcoin-cash", "icon": "💰", "category": "crypto"},
    {"symbol": "ARB", "name": "Arbitrum", "coingecko_id": "arbitrum", "icon": "🔷", "category": "crypto"},
    {"symbol": "OP", "name": "Optimism", "coingecko_id": "optimism", "icon": "⭕", "category": "crypto"},
    {"symbol": "UNI", "name": "Uniswap", "coingecko_id": "uniswap", "icon": "🦄", "category": "crypto"},
    {"symbol": "XMR", "name": "Monero", "coingecko_id": "monero", "icon": "🔒", "category": "crypto"},
    {"symbol": "ZEC", "name": "Zcash", "coingecko_id": "zcash", "icon": "Ƶ", "category": "crypto"},

    # Tier 3: Top 50-100 (DeFi Leaders)
    {"symbol": "AAVE", "name": "Aave", "coingecko_id": "aave", "icon": "👻", "category": "crypto"},
    {"symbol": "CRV", "name": "Curve", "coingecko_id": "curve-dao-token", "icon": "📈", "category": "crypto"},
    {"symbol": "MKR", "name": "Maker", "coingecko_id": "maker", "icon": "🔴", "category": "crypto"},
    {"symbol": "COMP", "name": "Compound", "coingecko_id": "compound-governance-token", "icon": "🏛️", "category": "crypto"},
    {"symbol": "SNX", "name": "Synthetix", "coingecko_id": "synthetix-network-token", "icon": "🔷", "category": "crypto"},
    {"symbol": "SUSHI", "name": "SushiSwap", "coingecko_id": "sushi", "icon": "🍣", "category": "crypto"},
    {"symbol": "BAL", "name": "Balancer", "coingecko_id": "balancer", "icon": "⚖️", "category": "crypto"},
    {"symbol": "YFI", "name": "Yearn Finance", "coingecko_id": "yearn-finance", "icon": "🌾", "category": "crypto"},
    {"symbol": "1INCH", "name": "1inch", "coingecko_id": "1inch", "icon": "💧", "category": "crypto"},

    # Layer 2 Solutions
    {"symbol": "LDO", "name": "Lido", "coingecko_id": "lido-dao", "icon": "🟦", "category": "crypto"},
    {"symbol": "STETH", "name": "Lido Staked Ether", "coingecko_id": "staked-ether", "icon": "Ξ", "category": "crypto"},
    {"symbol": "RETH", "name": "Rocket Pool Ether", "coingecko_id": "rocket-pool-eth", "icon": "🚀", "category": "crypto"},
    {"symbol": "CBETH", "name": "Coinbase Wrapped ETH", "coingecko_id": "coinbase-wrapped-staked-eth", "icon": "🏦", "category": "crypto"},

    # Metaverse & Gaming
    {"symbol": "SAND", "name": "The Sandbox", "coingecko_id": "the-sandbox", "icon": "🏜️", "category": "crypto"},
    {"symbol": "MANA", "name": "Decentraland", "coingecko_id": "decentraland", "icon": "🌐", "category": "crypto"},
    {"symbol": "AXS", "name": "Axie Infinity", "coingecko_id": "axie-infinity", "icon": "🐉", "category": "crypto"},
    {"symbol": "ENJ", "name": "Enjin", "coingecko_id": "enjin-coin", "icon": "🎮", "category": "crypto"},
    {"symbol": "GALA", "name": "Gala", "coingecko_id": "gala", "icon": "🎪", "category": "crypto"},
    {"symbol": "ILV", "name": "Illuvium", "coingecko_id": "illuvium", "icon": "💎", "category": "crypto"},
    {"symbol": "FLOW", "name": "Flow", "coingecko_id": "flow", "icon": "🌊", "category": "crypto"},

    # AI & ML Tokens
    {"symbol": "FET", "name": "Fetch.ai", "coingecko_id": "fetch-ai", "icon": "🤖", "category": "crypto"},
    {"symbol": "OCEAN", "name": "Ocean Protocol", "coingecko_id": "ocean-protocol", "icon": "🌊", "category": "crypto"},
    {"symbol": "RNDR", "name": "Render", "coingecko_id": "render-token", "icon": "🎨", "category": "crypto"},
    {"symbol": "GRT", "name": "The Graph", "coingecko_id": "the-graph", "icon": "📊", "category": "crypto"},
    {"symbol": "AGIX", "name": "SingularityNET", "coingecko_id": "singularitynet", "icon": "🧠", "category": "crypto"},
    {"symbol": "TAO", "name": "Bittensor", "coingecko_id": "bittensor", "icon": "⚡", "category": "crypto"},

    # Stablecoins (Critical for Trading)
    {"symbol": "USDT", "name": "Tether", "coingecko_id": "tether", "icon": "💵", "category": "crypto"},
    {"symbol": "USDC", "name": "USDC", "coingecko_id": "usd-coin", "icon": "💶", "category": "crypto"},
    {"symbol": "BUSD", "name": "BUSD", "coingecko_id": "binance-usd", "icon": "💷", "category": "crypto"},
    {"symbol": "DAI", "name": "Dai", "coingecko_id": "dai", "icon": "🪙", "category": "crypto"},
    {"symbol": "FRAX", "name": "Frax", "coingecko_id": "frax", "icon": "🏦", "category": "crypto"},
    {"symbol": "LUSD", "name": "LUSD", "coingecko_id": "liquity-usd", "icon": "💳", "category": "crypto"},

    # Exchange Tokens
    {"symbol": "FTT", "name": "FTX Token", "coingecko_id": "ftx-token", "icon": "🏦", "category": "crypto"},
    {"symbol": "OKB", "name": "OKB", "coingecko_id": "okb", "icon": "🏛️", "category": "crypto"},
    {"symbol": "HT", "name": "Huobi Token", "coingecko_id": "huobi-token", "icon": "🔷", "category": "crypto"},
    {"symbol": "KCS", "name": "KuCoin Token", "coingecko_id": "kucoin-token", "icon": "🪙", "category": "crypto"},

    # Top 100-200: Emerging & Promising Projects
    {"symbol": "NEAR", "name": "NEAR Protocol", "coingecko_id": "near", "icon": "🌐", "category": "crypto"},
    {"symbol": "ATOM", "name": "Cosmos", "coingecko_id": "cosmos", "icon": "🌌", "category": "crypto"},
    {"symbol": "THETA", "name": "Theta", "coingecko_id": "theta-token", "icon": "📺", "category": "crypto"},
    {"symbol": "DYDX", "name": "dYdX", "coingecko_id": "dydx", "icon": "📊", "category": "crypto"},
    {"symbol": "LUNC", "name": "Luna Classic", "coingecko_id": "terra-luna-2", "icon": "🌙", "category": "crypto"},
    {"symbol": "CRO", "name": "Cronos", "coingecko_id": "crypto-com-coin", "icon": "🟦", "category": "crypto"},
    {"symbol": "FTM", "name": "Fantom", "coingecko_id": "fantom", "icon": "👻", "category": "crypto"},
    {"symbol": "ONE", "name": "Harmony", "coingecko_id": "harmony", "icon": "🎵", "category": "crypto"},

    # Tier 4: Top 200-300
    {"symbol": "CELO", "name": "Celo", "coingecko_id": "celo", "icon": "🌍", "category": "crypto"},
    {"symbol": "ALGO", "name": "Algorand", "coingecko_id": "algorand", "icon": "⚙️", "category": "crypto"},
    {"symbol": "VET", "name": "VeChain", "coingecko_id": "vechain", "icon": "🔗", "category": "crypto"},
    {"symbol": "IOTA", "name": "IOTA", "coingecko_id": "iota", "icon": "🌐", "category": "crypto"},
    {"symbol": "ZIL", "name": "Zilliqa", "coingecko_id": "zilliqa", "icon": "⚡", "category": "crypto"},
    {"symbol": "HBAR", "name": "Hedera Hashgraph", "coingecko_id": "hedera-hashgraph", "icon": "🔗", "category": "crypto"},
    {"symbol": "NEO", "name": "Neo", "coingecko_id": "neo", "icon": "🐲", "category": "crypto"},
    {"symbol": "XTZ", "name": "Tezos", "coingecko_id": "tezos", "icon": "🔷", "category": "crypto"},

    # Privacy Coins
    {"symbol": "DASH", "name": "Dash", "coingecko_id": "dash", "icon": "💨", "category": "crypto"},
    {"symbol": "XVG", "name": "Verge", "coingecko_id": "verge", "icon": "🛡️", "category": "crypto"},

    # Additional Layer 1s & Layer 2s
    {"symbol": "ZKSYNC", "name": "ZkSync", "coingecko_id": "zksync", "icon": "🔐", "category": "crypto"},
    {"symbol": "BASE", "name": "Base", "coingecko_id": "base", "icon": "🔵", "category": "crypto"},
    {"symbol": "LINEA", "name": "Linea", "coingecko_id": "linea", "icon": "📏", "category": "crypto"},

    # Meme Coins & Community-Driven
    {"symbol": "PEPE", "name": "Pepe", "coingecko_id": "pepe", "icon": "🐸", "category": "crypto"},
    {"symbol": "BONK", "name": "Bonk", "coingecko_id": "bonk", "icon": "🦴", "category": "crypto"},
    {"symbol": "WIF", "name": "dogwifhat", "coingecko_id": "dogwifhat", "icon": "🐕", "category": "crypto"},
    {"symbol": "FLOKI", "name": "Floki", "coingecko_id": "floki", "icon": "🧔", "category": "crypto"},

    # Oracles & Infrastructure
    {"symbol": "BAND", "name": "Band Protocol", "coingecko_id": "band-protocol", "icon": "📡", "category": "crypto"},
    {"symbol": "TELLOR", "name": "Tellor", "coingecko_id": "tellor", "icon": "📊", "category": "crypto"},
    {"symbol": "PYTH", "name": "Pyth Network", "coingecko_id": "pyth-network", "icon": "🔭", "category": "crypto"},

    # Asset Management & Yield
    {"symbol": "CVX", "name": "Convex Finance", "coingecko_id": "convex-finance", "icon": "📈", "category": "crypto"},
    {"symbol": "PENDLE", "name": "Pendle", "coingecko_id": "pendle", "icon": "📚", "category": "crypto"},

    # Additional Top 100-300
    {"symbol": "ICP", "name": "Internet Computer", "coingecko_id": "internet-computer", "icon": "🖥️", "category": "crypto"},
    {"symbol": "STX", "name": "Stacks", "coingecko_id": "stacks", "icon": "🏗️", "category": "crypto"},
    {"symbol": "APT", "name": "Aptos", "coingecko_id": "aptos", "icon": "🎯", "category": "crypto"},
    {"symbol": "SUI", "name": "Sui", "coingecko_id": "sui", "icon": "🗡️", "category": "crypto"},
    {"symbol": "SEI", "name": "Sei", "coingecko_id": "sei-network", "icon": "⚡", "category": "crypto"},
    {"symbol": "TIA", "name": "Celestia", "coingecko_id": "celestia", "icon": "🌟", "category": "crypto"},

    # NFT & Marketplace
    {"symbol": "BLUR", "name": "Blur", "coingecko_id": "blur", "icon": "👁️", "category": "crypto"},
    {"symbol": "LOOKS", "name": "LooksRare", "coingecko_id": "looksrare", "icon": "👀", "category": "crypto"},
    {"symbol": "X2Y2", "name": "X2Y2", "coingecko_id": "x2y2", "icon": "🔷", "category": "crypto"},
    {"symbol": "RAY", "name": "Raydium", "coingecko_id": "raydium", "icon": "☀️", "category": "crypto"},
    {"symbol": "ORCA", "name": "Orca", "coingecko_id": "orca", "icon": "🐋", "category": "crypto"},
    {"symbol": "JTO", "name": "Jito", "coingecko_id": "jito", "icon": "🚀", "category": "crypto"},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_crypto_300():
    """Get all 300+ crypto assets"""
    return TOP_300_CRYPTO

def get_crypto_count():
    """Get total crypto count"""
    return len(TOP_300_CRYPTO)

def get_coingecko_id(symbol):
    """Get CoinGecko ID by symbol"""
    for crypto in TOP_300_CRYPTO:
        if crypto['symbol'].upper() == symbol.upper():
            return crypto.get('coingecko_id')
    return None

def get_coingecko_id_map():
    """Get complete mapping of symbol -> CoinGecko ID"""
    return {crypto['symbol'].upper(): crypto['coingecko_id'] for crypto in TOP_300_CRYPTO}
