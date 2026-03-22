"""Ticker-to-metadata mapping for Mercury commodities."""

TICKERS: dict[str, dict[str, str]] = {
    # Precious metals
    "GC=F": {"name": "Gold", "category": "metals"},
    "SI=F": {"name": "Silver", "category": "metals"},
    "PL=F": {"name": "Platinum", "category": "metals"},
    "PA=F": {"name": "Palladium", "category": "metals"},
    # Energy
    "CL=F": {"name": "Crude Oil WTI", "category": "energy"},
    "BZ=F": {"name": "Brent Crude", "category": "energy"},
    "NG=F": {"name": "Natural Gas", "category": "energy"},
    "RB=F": {"name": "Gasoline", "category": "energy"},
    # Grains
    "ZC=F": {"name": "Corn", "category": "grains"},
    "ZW=F": {"name": "Wheat", "category": "grains"},
    "ZS=F": {"name": "Soybeans", "category": "grains"},
    # Softs
    "KC=F": {"name": "Coffee", "category": "softs"},
    "SB=F": {"name": "Sugar", "category": "softs"},
    "CC=F": {"name": "Cocoa", "category": "softs"},
    # Livestock
    "LE=F": {"name": "Live Cattle", "category": "livestock"},
    "HE=F": {"name": "Lean Hogs", "category": "livestock"},
    "GF=F": {"name": "Feeder Cattle", "category": "livestock"},
    # Industrial metals
    "HG=F": {"name": "Copper", "category": "industrial_metals"},
    "ALI=F": {"name": "Aluminum", "category": "industrial_metals"},
    # Indices
    "^GSPC": {"name": "S&P 500", "category": "indices"},
    "^DJI": {"name": "Dow Jones", "category": "indices"},
    "^IXIC": {"name": "NASDAQ", "category": "indices"},
    # Crypto
    "BTC-USD": {"name": "Bitcoin", "category": "crypto"},
    "ETH-USD": {"name": "Ethereum", "category": "crypto"},
}

CATEGORIES: set[str] = {meta["category"] for meta in TICKERS.values()}
