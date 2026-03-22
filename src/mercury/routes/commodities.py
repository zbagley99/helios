"""Mercury commodities API routes."""

from fastapi import APIRouter

from mercury.tickers import CATEGORIES, TICKERS
from shared.db import get_collection
from shared.models import ErrorResponse

router = APIRouter()


@router.get("/commodities/summary")
async def get_summary() -> list[dict]:
    """Return all cached commodity data."""
    coll = get_collection("commodities")
    cursor = coll.find({}, {"_id": 0})
    return await cursor.to_list(length=200)


@router.get("/commodities/category/{category}", responses={404: {"model": ErrorResponse}})
async def get_by_category(category: str) -> list[dict] | ErrorResponse:
    """Return commodities filtered by category."""
    if category not in CATEGORIES:
        return ErrorResponse(error=f"Category not found: {category}")
    coll = get_collection("commodities")
    cursor = coll.find({"category": category}, {"_id": 0})
    return await cursor.to_list(length=200)


@router.get("/commodities/ticker/{symbol}", responses={404: {"model": ErrorResponse}})
async def get_by_ticker(symbol: str) -> dict | ErrorResponse:
    """Return data for a specific ticker."""
    if symbol not in TICKERS:
        return ErrorResponse(error="Ticker not found")
    coll = get_collection("commodities")
    doc = await coll.find_one({"ticker": symbol}, {"_id": 0})
    if doc is None:
        return ErrorResponse(error="Ticker not found")
    return doc
