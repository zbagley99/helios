"""Zephyr weather routes — current conditions, forecast, and air quality."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query

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


@router.get("/weather/current")
async def get_current_weather() -> list[dict]:
    """Return current weather conditions."""
    return await _get_latest_batch("weather_current")


@router.get("/weather/forecast")
async def get_weather_forecast(
    days: int = Query(default=7, ge=1, le=14, description="Number of forecast days"),
) -> list[dict]:
    """Return daily weather forecast, filtered to requested number of days."""
    docs = await _get_latest_batch("weather_forecast")
    if not docs:
        return []
    cutoff = (datetime.now(tz=UTC) + timedelta(days=days)).strftime("%Y-%m-%d")
    return [d for d in docs if d.get("date", "") <= cutoff]


@router.get("/weather/air")
async def get_air_quality() -> list[dict]:
    """Return current air quality data."""
    return await _get_latest_batch("air_quality")
