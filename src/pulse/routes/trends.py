"""Pulse trends API routes."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pulse.scrapers import SCRAPER_REGISTRY
from shared.db import get_collection

router = APIRouter()

SOURCES = list(SCRAPER_REGISTRY.keys())


@router.get("/trends")
async def get_trends() -> list[dict]:
    """Return all cached trends across all sources."""
    all_trends: list[dict] = []
    for source in SOURCES:
        coll = get_collection(source)
        cursor = coll.find({}, {"_id": 0})
        docs = await cursor.to_list(length=100)
        all_trends.extend(docs)
    return all_trends


@router.get("/trends/source/{source}", responses={404: {"description": "Unknown source"}})
async def get_trends_by_source(source: str) -> list[dict]:
    """Return cached trends for a specific source."""
    if source not in SOURCES:
        return JSONResponse(status_code=404, content={"error": f"Unknown source: {source}"})
    coll = get_collection(source)
    cursor = coll.find({}, {"_id": 0})
    return await cursor.to_list(length=100)
