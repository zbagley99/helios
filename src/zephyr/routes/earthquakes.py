"""Zephyr earthquake routes."""

from fastapi import APIRouter

from shared.db import get_collection

router = APIRouter()


async def _get_latest_batch(collection: str) -> list[dict]:
    """Return documents from the latest batch for a collection."""
    coll = get_collection(collection)
    latest = await coll.find_one(
        {"status": {"$ne": "dropped"}},
        {"batch_id": 1},
        sort=[("batch_id", -1)],
    )
    if not latest:
        return []
    cursor = coll.find({"batch_id": latest["batch_id"]}, {"_id": 0}).sort("magnitude", -1)
    return await cursor.to_list(length=100)


@router.get("/earthquakes")
async def get_earthquakes() -> list[dict]:
    """Return recent earthquakes sorted by magnitude."""
    return await _get_latest_batch("earthquakes")
