"""Zephyr space weather and Kp index routes."""

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
    cursor = coll.find({"batch_id": latest["batch_id"]}, {"_id": 0})
    return await cursor.to_list(length=100)


@router.get("/space-weather/summary")
async def get_space_weather_summary() -> list[dict]:
    """Return recent space weather alerts."""
    return await _get_latest_batch("space_weather")


@router.get("/kp/current")
async def get_kp_current() -> list[dict]:
    """Return Kp index forecast data."""
    return await _get_latest_batch("kp_index")
