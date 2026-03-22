"""Pulse trends API routes."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from pulse.scrapers import SCRAPER_REGISTRY
from shared.db import get_collection

router = APIRouter()

SOURCES = list(SCRAPER_REGISTRY.keys())


async def _get_latest_batch(source: str, status_filter: str | None = None) -> list[dict]:
    """Return documents from the latest batch for a source."""
    coll = get_collection(source)
    latest = await coll.find_one(
        {"status": {"$ne": "dropped"}} if not status_filter else {},
        {"batch_id": 1},
        sort=[("batch_id", -1)],
    )
    if not latest:
        return []
    query: dict = {"batch_id": latest["batch_id"]}
    if status_filter:
        query["status"] = status_filter
    cursor = coll.find(query, {"_id": 0})
    return await cursor.to_list(length=100)


@router.get("/trends")
async def get_trends(
    status: str | None = Query(default=None, description="Filter by status: new, persisting, dropped"),
    history: str | None = Query(default=None, description="Set to 'true' to return all docs within TTL window"),
) -> list[dict]:
    """Return all cached trends across all sources."""
    want_history = history and history.lower() == "true"
    all_trends: list[dict] = []
    for source in SOURCES:
        if want_history:
            coll = get_collection(source)
            query: dict = {}
            if status:
                query["status"] = status
            cursor = coll.find(query, {"_id": 0})
            docs = await cursor.to_list(length=100)
        else:
            docs = await _get_latest_batch(source, status)
        all_trends.extend(docs)
    return all_trends


@router.get("/trends/source/{source}", responses={404: {"description": "Unknown source"}})
async def get_trends_by_source(
    source: str,
    status: str | None = Query(default=None, description="Filter by status: new, persisting, dropped"),
    history: str | None = Query(default=None, description="Set to 'true' to return all docs within TTL window"),
) -> list[dict]:
    """Return cached trends for a specific source."""
    if source not in SOURCES:
        return JSONResponse(status_code=404, content={"error": f"Unknown source: {source}"})
    want_history = history and history.lower() == "true"
    if want_history:
        coll = get_collection(source)
        query: dict = {}
        if status:
            query["status"] = status
        cursor = coll.find(query, {"_id": 0})
        return await cursor.to_list(length=100)
    return await _get_latest_batch(source, status)
