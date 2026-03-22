"""Mercury commodities API routes."""

from fastapi import APIRouter, Query

from mercury.tickers import CATEGORIES, TICKERS
from shared.db import get_collection
from shared.models import ErrorResponse

router = APIRouter()


async def _get_latest_batch(query_filter: dict | None = None) -> list[dict]:
    """Return documents from the latest batch, optionally filtered."""
    coll = get_collection("commodities")
    latest = await coll.find_one(
        {"status": {"$ne": "dropped"}},
        {"batch_id": 1},
        sort=[("batch_id", -1)],
    )
    if not latest:
        return []
    query: dict = {"batch_id": latest["batch_id"]}
    if query_filter:
        query.update(query_filter)
    cursor = coll.find(query, {"_id": 0})
    return await cursor.to_list(length=200)


@router.get("/commodities/summary")
async def get_summary(
    status: str | None = Query(default=None, description="Filter by status: new, persisting, dropped"),
    history: str | None = Query(default=None, description="Set to 'true' to return all docs within TTL window"),
) -> list[dict]:
    """Return all cached commodity data."""
    want_history = history and history.lower() == "true"
    coll = get_collection("commodities")
    if want_history:
        query: dict = {}
        if status:
            query["status"] = status
        cursor = coll.find(query, {"_id": 0})
        return await cursor.to_list(length=200)
    extra: dict = {}
    if status:
        extra["status"] = status
    return await _get_latest_batch(extra or None)


@router.get("/commodities/category/{category}", responses={404: {"model": ErrorResponse}})
async def get_by_category(
    category: str,
    status: str | None = Query(default=None, description="Filter by status: new, persisting, dropped"),
    history: str | None = Query(default=None, description="Set to 'true' to return all docs within TTL window"),
) -> list[dict] | ErrorResponse:
    """Return commodities filtered by category."""
    if category not in CATEGORIES:
        return ErrorResponse(error=f"Category not found: {category}")
    want_history = history and history.lower() == "true"
    coll = get_collection("commodities")
    if want_history:
        query: dict = {"category": category}
        if status:
            query["status"] = status
        cursor = coll.find(query, {"_id": 0})
        return await cursor.to_list(length=200)
    extra: dict = {"category": category}
    if status:
        extra["status"] = status
    return await _get_latest_batch(extra)


@router.get("/commodities/ticker/{symbol}", responses={404: {"model": ErrorResponse}})
async def get_by_ticker(
    symbol: str,
    status: str | None = Query(default=None, description="Filter by status: new, persisting, dropped"),
    history: str | None = Query(default=None, description="Set to 'true' to return all docs within TTL window"),
) -> dict | list[dict] | ErrorResponse:
    """Return data for a specific ticker."""
    if symbol not in TICKERS:
        return ErrorResponse(error="Ticker not found")
    want_history = history and history.lower() == "true"
    coll = get_collection("commodities")
    if want_history:
        query: dict = {"ticker": symbol}
        if status:
            query["status"] = status
        cursor = coll.find(query, {"_id": 0})
        return await cursor.to_list(length=200)
    docs = await _get_latest_batch({"ticker": symbol})
    if not docs:
        return ErrorResponse(error="Ticker not found")
    return docs[0]
