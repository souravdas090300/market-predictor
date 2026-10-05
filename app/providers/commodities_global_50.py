"""
Market Predictor Pro - Global Commodities Database
23 Major Commodities Available on Yahoo Finance
"""

# ============================================================================
# 23 GLOBAL COMMODITIES - Available on Yahoo Finance
# ============================================================================

COMMODITIES_50 = [
    # ============================================================================
    # PRECIOUS METALS
    # ============================================================================
    {"symbol": "GC=F", "name": "Gold", "category": "precious_metals", "exchange": "COMEX", "unit": "troy oz", "contract": "futures"},
    {"symbol": "SI=F", "name": "Silver", "category": "precious_metals", "exchange": "COMEX", "unit": "troy oz", "contract": "futures"},
    {"symbol": "PL=F", "name": "Platinum", "category": "precious_metals", "exchange": "NYMEX", "unit": "troy oz", "contract": "futures"},
    {"symbol": "PA=F", "name": "Palladium", "category": "precious_metals", "exchange": "NYMEX", "unit": "troy oz", "contract": "futures"},

    # ============================================================================
    # BASE METALS
    # ============================================================================
    {"symbol": "HG=F", "name": "Copper", "category": "base_metals", "exchange": "COMEX", "unit": "lbs", "contract": "futures"},

    # ============================================================================
    # ENERGY - CRUDE OIL
    # ============================================================================
    {"symbol": "CL=F", "name": "WTI Crude Oil", "category": "energy_crude", "exchange": "NYMEX", "unit": "barrels", "contract": "futures"},
    {"symbol": "BZ=F", "name": "Brent Crude Oil", "category": "energy_crude", "exchange": "ICE", "unit": "barrels", "contract": "futures"},

    # ============================================================================
    # ENERGY - REFINED PRODUCTS
    # ============================================================================
    {"symbol": "RB=F", "name": "RBOB Gasoline", "category": "energy_refined", "exchange": "NYMEX", "unit": "gallons", "contract": "futures"},
    {"symbol": "HO=F", "name": "Heating Oil", "category": "energy_refined", "exchange": "NYMEX", "unit": "gallons", "contract": "futures"},

    # ============================================================================
    # ENERGY - NATURAL GAS
    # ============================================================================
    {"symbol": "NG=F", "name": "Natural Gas", "category": "energy_gas", "exchange": "NYMEX", "unit": "MMBtu", "contract": "futures"},

    # ============================================================================
    # AGRICULTURE - GRAINS
    # ============================================================================
    {"symbol": "ZC=F", "name": "Corn", "category": "agriculture_grains", "exchange": "CBOT", "unit": "bushels", "contract": "futures"},
    {"symbol": "ZW=F", "name": "Wheat", "category": "agriculture_grains", "exchange": "CBOT", "unit": "bushels", "contract": "futures"},
    {"symbol": "ZS=F", "name": "Soybeans", "category": "agriculture_grains", "exchange": "CBOT", "unit": "bushels", "contract": "futures"},
    {"symbol": "ZR=F", "name": "Rough Rice", "category": "agriculture_grains", "exchange": "CBOT", "unit": "cwt", "contract": "futures"},
    {"symbol": "ZM=F", "name": "Soybean Meal", "category": "agriculture_grains", "exchange": "CBOT", "unit": "tons", "contract": "futures"},
    {"symbol": "ZL=F", "name": "Soybean Oil", "category": "agriculture_grains", "exchange": "CBOT", "unit": "lbs", "contract": "futures"},

    # ============================================================================
    # AGRICULTURE - SOFT COMMODITIES
    # ============================================================================
    {"symbol": "SB=F", "name": "Sugar", "category": "agriculture_softs", "exchange": "ICE", "unit": "lbs", "contract": "futures"},
    {"symbol": "KC=F", "name": "Coffee", "category": "agriculture_softs", "exchange": "ICE", "unit": "lbs", "contract": "futures"},
    {"symbol": "CC=F", "name": "Cocoa", "category": "agriculture_softs", "exchange": "ICE", "unit": "metric tons", "contract": "futures"},
    {"symbol": "CT=F", "name": "Cotton", "category": "agriculture_softs", "exchange": "ICE", "unit": "lbs", "contract": "futures"},
    {"symbol": "OJ=F", "name": "Orange Juice", "category": "agriculture_softs", "exchange": "ICE", "unit": "lbs", "contract": "futures"},

    # ============================================================================
    # LIVESTOCK
    # ============================================================================
    {"symbol": "LE=F", "name": "Live Cattle", "category": "livestock", "exchange": "CME", "unit": "lbs", "contract": "futures"},
    {"symbol": "GF=F", "name": "Feeder Cattle", "category": "livestock", "exchange": "CME", "unit": "lbs", "contract": "futures"},
    {"symbol": "HE=F", "name": "Lean Hogs", "category": "livestock", "exchange": "CME", "unit": "lbs", "contract": "futures"},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_commodities_50():
    """Get all 50+ commodities"""
    return COMMODITIES_50

def get_commodity_count():
    """Get total commodity count"""
    return len(COMMODITIES_50)

def get_commodities_by_category(category: str):
    """Get commodities by category"""
    return [commodity for commodity in COMMODITIES_50 if commodity["category"] == category]

def get_precious_metals():
    """Get precious metals only"""
    return [commodity for commodity in COMMODITIES_50 if commodity["category"] == "precious_metals"]

def get_base_metals():
    """Get base metals only"""
    return [commodity for commodity in COMMODITIES_50 if commodity["category"] == "base_metals"]

def get_energy_commodities():
    """Get all energy commodities"""
    energy_categories = ["energy_crude", "energy_refined", "energy_gas", "energy_coal", "energy_uranium"]
    return [commodity for commodity in COMMODITIES_50 if commodity["category"] in energy_categories]

def get_agriculture_commodities():
    """Get all agriculture commodities"""
    agriculture_categories = ["agriculture_grains", "agriculture_softs"]
    return [commodity for commodity in COMMODITIES_50 if commodity["category"] in agriculture_categories]

def get_livestock():
    """Get livestock commodities only"""
    return [commodity for commodity in COMMODITIES_50 if commodity["category"] == "livestock"]

def get_commodities_by_exchange(exchange: str):
    """Get commodities by exchange"""
    return [commodity for commodity in COMMODITIES_50 if commodity["exchange"] == exchange]
