"""
Market Predictor Pro - Global Forex Database
100+ Currency Pairs from Around the World
"""

# ============================================================================
# 100+ GLOBAL FOREX PAIRS - Major, Minor, and Exotic Pairs
# ============================================================================

FOREX_PAIRS_100 = [
    # ============================================================================
    # MAJOR PAIRS (Most traded - with USD)
    # ============================================================================
    {"symbol": "EURUSD=X", "name": "EUR/USD", "base_currency": "EUR", "quote_currency": "USD", "category": "major"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "base_currency": "GBP", "quote_currency": "USD", "category": "major"},
    {"symbol": "USDJPY=X", "name": "USD/JPY", "base_currency": "USD", "quote_currency": "JPY", "category": "major"},
    {"symbol": "USDCHF=X", "name": "USD/CHF", "base_currency": "USD", "quote_currency": "CHF", "category": "major"},
    {"symbol": "USDCAD=X", "name": "USD/CAD", "base_currency": "USD", "quote_currency": "CAD", "category": "major"},
    {"symbol": "AUDUSD=X", "name": "AUD/USD", "base_currency": "AUD", "quote_currency": "USD", "category": "major"},
    {"symbol": "NZDUSD=X", "name": "NZD/USD", "base_currency": "NZD", "quote_currency": "USD", "category": "major"},

    # ============================================================================
    # MINOR PAIRS (Cross pairs - without USD)
    # ============================================================================
    {"symbol": "EURGBP=X", "name": "EUR/GBP", "base_currency": "EUR", "quote_currency": "GBP", "category": "minor"},
    {"symbol": "EURJPY=X", "name": "EUR/JPY", "base_currency": "EUR", "quote_currency": "JPY", "category": "minor"},
    {"symbol": "EURCHF=X", "name": "EUR/CHF", "base_currency": "EUR", "quote_currency": "CHF", "category": "minor"},
    {"symbol": "EURAUD=X", "name": "EUR/AUD", "base_currency": "EUR", "quote_currency": "AUD", "category": "minor"},
    {"symbol": "EURCAD=X", "name": "EUR/CAD", "base_currency": "EUR", "quote_currency": "CAD", "category": "minor"},
    {"symbol": "EURNZD=X", "name": "EUR/NZD", "base_currency": "EUR", "quote_currency": "NZD", "category": "minor"},
    {"symbol": "GBPJPY=X", "name": "GBP/JPY", "base_currency": "GBP", "quote_currency": "JPY", "category": "minor"},
    {"symbol": "GBPCHF=X", "name": "GBP/CHF", "base_currency": "GBP", "quote_currency": "CHF", "category": "minor"},
    {"symbol": "GBPAUD=X", "name": "GBP/AUD", "base_currency": "GBP", "quote_currency": "AUD", "category": "minor"},
    {"symbol": "GBPCAD=X", "name": "GBP/CAD", "base_currency": "GBP", "quote_currency": "CAD", "category": "minor"},
    {"symbol": "GBPNZD=X", "name": "GBP/NZD", "base_currency": "GBP", "quote_currency": "NZD", "category": "minor"},
    {"symbol": "CHFJPY=X", "name": "CHF/JPY", "base_currency": "CHF", "quote_currency": "JPY", "category": "minor"},
    {"symbol": "CADJPY=X", "name": "CAD/JPY", "base_currency": "CAD", "quote_currency": "JPY", "category": "minor"},
    {"symbol": "AUDJPY=X", "name": "AUD/JPY", "base_currency": "AUD", "quote_currency": "JPY", "category": "minor"},
    {"symbol": "NZDJPY=X", "name": "NZD/JPY", "base_currency": "NZD", "quote_currency": "JPY", "category": "minor"},
    {"symbol": "AUDCHF=X", "name": "AUD/CHF", "base_currency": "AUD", "quote_currency": "CHF", "category": "minor"},
    {"symbol": "NZDCHF=X", "name": "NZD/CHF", "base_currency": "NZD", "quote_currency": "CHF", "category": "minor"},
    {"symbol": "AUDCAD=X", "name": "AUD/CAD", "base_currency": "AUD", "quote_currency": "CAD", "category": "minor"},
    {"symbol": "NZDCAD=X", "name": "NZD/CAD", "base_currency": "NZD", "quote_currency": "CAD", "category": "minor"},
    {"symbol": "AUDNZD=X", "name": "AUD/NZD", "base_currency": "AUD", "quote_currency": "NZD", "category": "minor"},
    {"symbol": "CADCHF=X", "name": "CAD/CHF", "base_currency": "CAD", "quote_currency": "CHF", "category": "minor"},

    # ============================================================================
    # ASIAN CURRENCIES (USD crosses)
    # ============================================================================
    {"symbol": "USDCNY=X", "name": "USD/CNY", "base_currency": "USD", "quote_currency": "CNY", "category": "asian"},
    {"symbol": "USDHKD=X", "name": "USD/HKD", "base_currency": "USD", "quote_currency": "HKD", "category": "asian"},
    {"symbol": "USDSGD=X", "name": "USD/SGD", "base_currency": "USD", "quote_currency": "SGD", "category": "asian"},
    {"symbol": "USDINR=X", "name": "USD/INR", "base_currency": "USD", "quote_currency": "INR", "category": "asian"},
    {"symbol": "USDKRW=X", "name": "USD/KRW", "base_currency": "USD", "quote_currency": "KRW", "category": "asian"},
    {"symbol": "USDIDR=X", "name": "USD/IDR", "base_currency": "USD", "quote_currency": "IDR", "category": "asian"},
    {"symbol": "USDMYR=X", "name": "USD/MYR", "base_currency": "USD", "quote_currency": "MYR", "category": "asian"},
    {"symbol": "USDPHP=X", "name": "USD/PHP", "base_currency": "USD", "quote_currency": "PHP", "category": "asian"},
    {"symbol": "USDTHB=X", "name": "USD/THB", "base_currency": "USD", "quote_currency": "THB", "category": "asian"},
    {"symbol": "USDVND=X", "name": "USD/VND", "base_currency": "USD", "quote_currency": "VND", "category": "asian"},
    {"symbol": "USDTWD=X", "name": "USD/TWD", "base_currency": "USD", "quote_currency": "TWD", "category": "asian"},
    {"symbol": "USDBND=X", "name": "USD/BND", "base_currency": "USD", "quote_currency": "BND", "category": "asian"},
    {"symbol": "USDLKR=X", "name": "USD/LKR", "base_currency": "USD", "quote_currency": "LKR", "category": "asian"},
    {"symbol": "USDPKR=X", "name": "USD/PKR", "base_currency": "USD", "quote_currency": "PKR", "category": "asian"},
    {"symbol": "USDBDT=X", "name": "USD/BDT", "base_currency": "USD", "quote_currency": "BDT", "category": "asian"},
    {"symbol": "USDNPR=X", "name": "USD/NPR", "base_currency": "USD", "quote_currency": "NPR", "category": "asian"},
    {"symbol": "USDLAK=X", "name": "USD/LAK", "base_currency": "USD", "quote_currency": "LAK", "category": "asian"},
    {"symbol": "USDKHR=X", "name": "USD/KHR", "base_currency": "USD", "quote_currency": "KHR", "category": "asian"},
    {"symbol": "USDKYAT=X", "name": "USD/MMK", "base_currency": "USD", "quote_currency": "MMK", "category": "asian"},
    {"symbol": "USDMNT=X", "name": "USD/MNT", "base_currency": "USD", "quote_currency": "MNT", "category": "asian"},
    {"symbol": "USDKZT=X", "name": "USD/KZT", "base_currency": "USD", "quote_currency": "KZT", "category": "asian"},
    {"symbol": "USDUZS=X", "name": "USD/UZS", "base_currency": "USD", "quote_currency": "UZS", "category": "asian"},
    {"symbol": "USDGEL=X", "name": "USD/GEL", "base_currency": "USD", "quote_currency": "GEL", "category": "asian"},
    {"symbol": "USDAZN=X", "name": "USD/AZN", "base_currency": "USD", "quote_currency": "AZN", "category": "asian"},
    {"symbol": "USDAMD=X", "name": "USD/AMD", "base_currency": "USD", "quote_currency": "AMD", "category": "asian"},
    {"symbol": "USDKGS=X", "name": "USD/KGS", "base_currency": "USD", "quote_currency": "KGS", "category": "asian"},
    {"symbol": "USDTJS=X", "name": "USD/TJS", "base_currency": "USD", "quote_currency": "TJS", "category": "asian"},

    # ============================================================================
    # EUROPEAN CURRENCIES (USD crosses)
    # ============================================================================
    {"symbol": "EURUSD=X", "name": "EUR/USD", "base_currency": "EUR", "quote_currency": "USD", "category": "european"},
    {"symbol": "USDCHF=X", "name": "USD/CHF", "base_currency": "USD", "quote_currency": "CHF", "category": "european"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "base_currency": "GBP", "quote_currency": "USD", "category": "european"},
    {"symbol": "USDNOK=X", "name": "USD/NOK", "base_currency": "USD", "quote_currency": "NOK", "category": "european"},
    {"symbol": "USDSEK=X", "name": "USD/SEK", "base_currency": "USD", "quote_currency": "SEK", "category": "european"},
    {"symbol": "USDDKK=X", "name": "USD/DKK", "base_currency": "USD", "quote_currency": "DKK", "category": "european"},
    {"symbol": "USDPLN=X", "name": "USD/PLN", "base_currency": "USD", "quote_currency": "PLN", "category": "european"},
    {"symbol": "USDCZK=X", "name": "USD/CZK", "base_currency": "USD", "quote_currency": "CZK", "category": "european"},
    {"symbol": "USDHUF=X", "name": "USD/HUF", "base_currency": "USD", "quote_currency": "HUF", "category": "european"},
    {"symbol": "USDRON=X", "name": "USD/RON", "base_currency": "USD", "quote_currency": "RON", "category": "european"},
    {"symbol": "USDBGN=X", "name": "USD/BGN", "base_currency": "USD", "quote_currency": "BGN", "category": "european"},
    {"symbol": "USDHRK=X", "name": "USD/HRK", "base_currency": "USD", "quote_currency": "HRK", "category": "european"},
    {"symbol": "USDRSD=X", "name": "USD/RSD", "base_currency": "USD", "quote_currency": "RSD", "category": "european"},
    {"symbol": "USDBAM=X", "name": "USD/BAM", "base_currency": "USD", "quote_currency": "BAM", "category": "european"},
    {"symbol": "USDMKD=X", "name": "USD/MKD", "base_currency": "USD", "quote_currency": "MKD", "category": "european"},
    {"symbol": "USDALL=X", "name": "USD/ALL", "base_currency": "USD", "quote_currency": "ALL", "category": "european"},
    {"symbol": "USDEUR=X", "name": "USD/EUR", "base_currency": "USD", "quote_currency": "EUR", "category": "european"},
    {"symbol": "USDGBP=X", "name": "USD/GBP", "base_currency": "USD", "quote_currency": "GBP", "category": "european"},
    {"symbol": "USDCHE=X", "name": "USD/CHE", "base_currency": "USD", "quote_currency": "CHE", "category": "european"},
    {"symbol": "USDCHW=X", "name": "USD/CHW", "base_currency": "USD", "quote_currency": "CHW", "category": "european"},

    # ============================================================================
    # MIDDLE EASTERN CURRENCIES (USD crosses)
    # ============================================================================
    {"symbol": "USDAED=X", "name": "USD/AED", "base_currency": "USD", "quote_currency": "AED", "category": "middle_east"},
    {"symbol": "USDSAR=X", "name": "USD/SAR", "base_currency": "USD", "quote_currency": "SAR", "category": "middle_east"},
    {"symbol": "USDQAR=X", "name": "USD/QAR", "base_currency": "USD", "quote_currency": "QAR", "category": "middle_east"},
    {"symbol": "USDKWD=X", "name": "USD/KWD", "base_currency": "USD", "quote_currency": "KWD", "category": "middle_east"},
    {"symbol": "USDBHD=X", "name": "USD/BHD", "base_currency": "USD", "quote_currency": "BHD", "category": "middle_east"},
    {"symbol": "USDOMR=X", "name": "USD/OMR", "base_currency": "USD", "quote_currency": "OMR", "category": "middle_east"},
    {"symbol": "USDJOD=X", "name": "USD/JOD", "base_currency": "USD", "quote_currency": "JOD", "category": "middle_east"},
    {"symbol": "USDLBP=X", "name": "USD/LBP", "base_currency": "USD", "quote_currency": "LBP", "category": "middle_east"},
    {"symbol": "USDEGP=X", "name": "USD/EGP", "base_currency": "USD", "quote_currency": "EGP", "category": "middle_east"},
    {"symbol": "USDTND=X", "name": "USD/TND", "base_currency": "USD", "quote_currency": "TND", "category": "middle_east"},
    {"symbol": "USDMAD=X", "name": "USD/MAD", "base_currency": "USD", "quote_currency": "MAD", "category": "middle_east"},
    {"symbol": "USDDZD=X", "name": "USD/DZD", "base_currency": "USD", "quote_currency": "DZD", "category": "middle_east"},
    {"symbol": "USDLYD=X", "name": "USD/LYD", "base_currency": "USD", "quote_currency": "LYD", "category": "middle_east"},
    {"symbol": "USDILS=X", "name": "USD/ILS", "base_currency": "USD", "quote_currency": "ILS", "category": "middle_east"},
    {"symbol": "USDTRY=X", "name": "USD/TRY", "base_currency": "USD", "quote_currency": "TRY", "category": "middle_east"},
    {"symbol": "USDIRR=X", "name": "USD/IRR", "base_currency": "USD", "quote_currency": "IRR", "category": "middle_east"},
    {"symbol": "USDIQD=X", "name": "USD/IQD", "base_currency": "USD", "quote_currency": "IQD", "category": "middle_east"},
    {"symbol": "USDSYP=X", "name": "USD/SYP", "base_currency": "USD", "quote_currency": "SYP", "category": "middle_east"},
    {"symbol": "USDYER=X", "name": "USD/YER", "base_currency": "USD", "quote_currency": "YER", "category": "middle_east"},

    # ============================================================================
    # AFRICAN CURRENCIES (USD crosses)
    # ============================================================================
    {"symbol": "USDZAR=X", "name": "USD/ZAR", "base_currency": "USD", "quote_currency": "ZAR", "category": "african"},
    {"symbol": "USDNGN=X", "name": "USD/NGN", "base_currency": "USD", "quote_currency": "NGN", "category": "african"},
    {"symbol": "USDKES=X", "name": "USD/KES", "base_currency": "USD", "quote_currency": "KES", "category": "african"},
    {"symbol": "USDEGP=X", "name": "USD/EGP", "base_currency": "USD", "quote_currency": "EGP", "category": "african"},
    {"symbol": "USDMAD=X", "name": "USD/MAD", "base_currency": "USD", "quote_currency": "MAD", "category": "african"},
    {"symbol": "USDTND=X", "name": "USD/TND", "base_currency": "USD", "quote_currency": "TND", "category": "african"},
    {"symbol": "USDDZD=X", "name": "USD/DZD", "base_currency": "USD", "quote_currency": "DZD", "category": "african"},
    {"symbol": "USDGHS=X", "name": "USD/GHS", "base_currency": "USD", "quote_currency": "GHS", "category": "african"},
    {"symbol": "USDTZS=X", "name": "USD/TZS", "base_currency": "USD", "quote_currency": "TZS", "category": "african"},
    {"symbol": "USDUGX=X", "name": "USD/UGX", "base_currency": "USD", "quote_currency": "UGX", "category": "african"},
    {"symbol": "USDBWP=X", "name": "USD/BWP", "base_currency": "USD", "quote_currency": "BWP", "category": "african"},
    {"symbol": "USDZMW=X", "name": "USD/ZMW", "base_currency": "USD", "quote_currency": "ZMW", "category": "african"},
    {"symbol": "USDMZN=X", "name": "USD/MZN", "base_currency": "USD", "quote_currency": "MZN", "category": "african"},
    {"symbol": "USDXOF=X", "name": "USD/XOF", "base_currency": "USD", "quote_currency": "XOF", "category": "african"},
    {"symbol": "USDXAF=X", "name": "USD/XAF", "base_currency": "USD", "quote_currency": "XAF", "category": "african"},
    {"symbol": "USDXCD=X", "name": "USD/XCD", "base_currency": "USD", "quote_currency": "XCD", "category": "african"},
    {"symbol": "USDBIF=X", "name": "USD/BIF", "base_currency": "USD", "quote_currency": "BIF", "category": "african"},
    {"symbol": "USDRWF=X", "name": "USD/RWF", "base_currency": "USD", "quote_currency": "RWF", "category": "african"},
    {"symbol": "USDSOS=X", "name": "USD/SOS", "base_currency": "USD", "quote_currency": "SOS", "category": "african"},
    {"symbol": "USDETH=X", "name": "USD/ETH", "base_currency": "USD", "quote_currency": "ETH", "category": "african"},
    {"symbol": "USDSLL=X", "name": "USD/SLL", "base_currency": "USD", "quote_currency": "SLL", "category": "african"},
    {"symbol": "USDLRD=X", "name": "USD/LRD", "base_currency": "USD", "quote_currency": "LRD", "category": "african"},
    {"symbol": "USDGMD=X", "name": "USD/GMD", "base_currency": "USD", "quote_currency": "GMD", "category": "african"},
    {"symbol": "USDCVE=X", "name": "USD/CVE", "base_currency": "USD", "quote_currency": "CVE", "category": "african"},
    {"symbol": "USDSTN=X", "name": "USD/STN", "base_currency": "USD", "quote_currency": "STN", "category": "african"},
    {"symbol": "USDCDF=X", "name": "USD/CDF", "base_currency": "USD", "quote_currency": "CDF", "category": "african"},
    {"symbol": "USDKES=X", "name": "USD/KES", "base_currency": "USD", "quote_currency": "KES", "category": "african"},
    {"symbol": "USDLKR=X", "name": "USD/LKR", "base_currency": "USD", "quote_currency": "LKR", "category": "african"},

    # ============================================================================
    # AMERICAS CURRENCIES (USD crosses - excluding major)
    # ============================================================================
    {"symbol": "USDMXN=X", "name": "USD/MXN", "base_currency": "USD", "quote_currency": "MXN", "category": "americas"},
    {"symbol": "USDBRL=X", "name": "USD/BRL", "base_currency": "USD", "quote_currency": "BRL", "category": "americas"},
    {"symbol": "USDARS=X", "name": "USD/ARS", "base_currency": "USD", "quote_currency": "ARS", "category": "americas"},
    {"symbol": "USDCLP=X", "name": "USD/CLP", "base_currency": "USD", "quote_currency": "CLP", "category": "americas"},
    {"symbol": "USDCOP=X", "name": "USD/COP", "base_currency": "USD", "quote_currency": "COP", "category": "americas"},
    {"symbol": "USDPEN=X", "name": "USD/PEN", "base_currency": "USD", "quote_currency": "PEN", "category": "americas"},
    {"symbol": "USDVES=X", "name": "USD/VES", "base_currency": "USD", "quote_currency": "VES", "category": "americas"},
    {"symbol": "USDCOP=X", "name": "USD/COP", "base_currency": "USD", "quote_currency": "COP", "category": "americas"},
    {"symbol": "USDCRC=X", "name": "USD/CRC", "base_currency": "USD", "quote_currency": "CRC", "category": "americas"},
    {"symbol": "USDDOP=X", "name": "USD/DOP", "base_currency": "USD", "quote_currency": "DOP", "category": "americas"},
    {"symbol": "USDGTQ=X", "name": "USD/GTQ", "base_currency": "USD", "quote_currency": "GTQ", "category": "americas"},
    {"symbol": "USDHNL=X", "name": "USD/HNL", "base_currency": "USD", "quote_currency": "HNL", "category": "americas"},
    {"symbol": "USDNIO=X", "name": "USD/NIO", "base_currency": "USD", "quote_currency": "NIO", "category": "americas"},
    {"symbol": "USDPAB=X", "name": "USD/PAB", "base_currency": "USD", "quote_currency": "PAB", "category": "americas"},
    {"symbol": "USDPYG=X", "name": "USD/PYG", "base_currency": "USD", "quote_currency": "PYG", "category": "americas"},
    {"symbol": "USDSVC=X", "name": "USD/SVC", "base_currency": "USD", "quote_currency": "SVC", "category": "americas"},
    {"symbol": "USDUYU=X", "name": "USD/UYU", "base_currency": "USD", "quote_currency": "UYU", "category": "americas"},
    {"symbol": "USDXCD=X", "name": "USD/XCD", "base_currency": "USD", "quote_currency": "XCD", "category": "americas"},
    {"symbol": "USDBBD=X", "name": "USD/BBD", "base_currency": "USD", "quote_currency": "BBD", "category": "americas"},
    {"symbol": "USDBSD=X", "name": "USD/BSD", "base_currency": "USD", "quote_currency": "BSD", "category": "americas"},
    {"symbol": "USDBZD=X", "name": "USD/BZD", "base_currency": "USD", "quote_currency": "BZD", "category": "americas"},
    {"symbol": "USDCAD=X", "name": "USD/CAD", "base_currency": "USD", "quote_currency": "CAD", "category": "americas"},
    {"symbol": "USDJMD=X", "name": "USD/JMD", "base_currency": "USD", "quote_currency": "JMD", "category": "americas"},
    {"symbol": "USDHTG=X", "name": "USD/HTG", "base_currency": "USD", "quote_currency": "HTG", "category": "americas"},
    {"symbol": "USDXAF=X", "name": "USD/XAF", "base_currency": "USD", "quote_currency": "XAF", "category": "americas"},
    {"symbol": "USDTTD=X", "name": "USD/TTD", "base_currency": "USD", "quote_currency": "TTD", "category": "americas"},

    # ============================================================================
    # OCEANIA CURRENCIES (USD crosses - excluding major)
    # ============================================================================
    {"symbol": "AUDUSD=X", "name": "AUD/USD", "base_currency": "AUD", "quote_currency": "USD", "category": "oceania"},
    {"symbol": "NZDUSD=X", "name": "NZD/USD", "base_currency": "NZD", "quote_currency": "USD", "category": "oceania"},
    {"symbol": "USDFJD=X", "name": "USD/FJD", "base_currency": "USD", "quote_currency": "FJD", "category": "oceania"},
    {"symbol": "USDPGK=X", "name": "USD/PGK", "base_currency": "USD", "quote_currency": "PGK", "category": "oceania"},
    {"symbol": "USDSBD=X", "name": "USD/SBD", "base_currency": "USD", "quote_currency": "SBD", "category": "oceania"},
    {"symbol": "USDVUV=X", "name": "USD/VUV", "base_currency": "USD", "quote_currency": "VUV", "category": "oceania"},
    {"symbol": "USDWST=X", "name": "USD/WST", "base_currency": "USD", "quote_currency": "WST", "category": "oceania"},
    {"symbol": "USDTOP=X", "name": "USD/TOP", "base_currency": "USD", "quote_currency": "TOP", "category": "oceania"},
    {"symbol": "USDKID=X", "name": "USD/KID", "base_currency": "USD", "quote_currency": "KID", "category": "oceania"},
    {"symbol": "USDMUR=X", "name": "USD/MUR", "base_currency": "USD", "quote_currency": "MUR", "category": "oceania"},
    {"symbol": "USDSCR=X", "name": "USD/SCR", "base_currency": "USD", "quote_currency": "SCR", "category": "oceania"},

    # ============================================================================
    # GOLD & SILVER (Precious Metals as Forex Pairs)
    # ============================================================================
    {"symbol": "XAUUSD=X", "name": "Gold/USD", "base_currency": "XAU", "quote_currency": "USD", "category": "precious_metal"},
    {"symbol": "XAGUSD=X", "name": "Silver/USD", "base_currency": "XAG", "quote_currency": "USD", "category": "precious_metal"},
    {"symbol": "XPTUSD=X", "name": "Platinum/USD", "base_currency": "XPT", "quote_currency": "USD", "category": "precious_metal"},
    {"symbol": "XPDUSD=X", "name": "Palladium/USD", "base_currency": "XPD", "quote_currency": "USD", "category": "precious_metal"},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_forex_100():
    """Get all 100+ forex pairs"""
    return FOREX_PAIRS_100

def get_forex_count():
    """Get total forex count"""
    return len(FOREX_PAIRS_100)

def get_forex_by_category(category: str):
    """Get forex pairs by category"""
    return [pair for pair in FOREX_PAIRS_100 if pair["category"] == category]

def get_forex_by_base_currency(currency: str):
    """Get forex pairs by base currency"""
    return [pair for pair in FOREX_PAIRS_100 if pair["base_currency"] == currency]

def get_forex_by_quote_currency(currency: str):
    """Get forex pairs by quote currency"""
    return [pair for pair in FOREX_PAIRS_100 if pair["quote_currency"] == currency]

def get_major_pairs():
    """Get major forex pairs only"""
    return [pair for pair in FOREX_PAIRS_100 if pair["category"] == "major"]

def get_minor_pairs():
    """Get minor forex pairs only"""
    return [pair for pair in FOREX_PAIRS_100 if pair["category"] == "minor"]

def get_exotic_pairs():
    """Get exotic forex pairs (non-major, non-minor)"""
    return [pair for pair in FOREX_PAIRS_100 if pair["category"] not in ["major", "minor"]]
