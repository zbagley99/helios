"""Yahoo Finance scraper via yfinance."""

from datetime import UTC, datetime

import yfinance as yf

from mercury.models import CommodityItem
from mercury.tickers import TICKERS
from shared.db import get_collection


def _fetch_ticker_data(symbol: str) -> dict | None:
    """Fetch current data for a single ticker."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = getattr(info, "last_price", None)
        prev_close = getattr(info, "previous_close", None)
        if price is None:
            return None
        change = round(price - prev_close, 4) if prev_close else None
        pct_change = round((change / prev_close) * 100, 4) if prev_close and change is not None else None
        return {
            "price": round(price, 4),
            "change": change,
            "pct_change": pct_change,
            "currency": getattr(info, "currency", "USD") or "USD",
        }
    except Exception:
        return None


async def scrape_yahoo_finance() -> list[CommodityItem]:
    """Fetch commodity data for all configured tickers."""
    items: list[CommodityItem] = []
    now = datetime.now(tz=UTC)

    for symbol, meta in TICKERS.items():
        data = _fetch_ticker_data(symbol)
        if data is None:
            continue
        items.append(
            CommodityItem(
                ticker=symbol,
                name=meta["name"],
                category=meta["category"],
                price=data["price"],
                change=data["change"],
                pct_change=data["pct_change"],
                currency=data["currency"],
                timestamp=now,
            )
        )

    coll = get_collection("commodities")
    if items:
        await coll.delete_many({})
        await coll.insert_many([item.model_dump(mode="json") for item in items])
    return items
