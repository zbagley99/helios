"""Air quality scraper via Open-Meteo."""

import logging

import httpx

from shared.scrape import persist_batch
from zephyr.geocode import get_coords
from zephyr.models import AirQuality

logger = logging.getLogger(__name__)

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


async def scrape_air_quality() -> list[AirQuality]:
    """Fetch current air quality data from Open-Meteo."""
    logger.info("scrape started")
    lat, lng, display = await get_coords()
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "pm10,pm2_5,us_aqi",
    }
    items: list[AirQuality] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(AIR_QUALITY_URL, params=params)
        resp.raise_for_status()
        cur = resp.json()["current"]

        items.append(
            AirQuality(
                location=display,
                aqi=cur.get("us_aqi"),
                pm25=cur.get("pm2_5"),
                pm10=cur.get("pm10"),
            )
        )

    if items:
        await persist_batch("air_quality", [i.model_dump(mode="json") for i in items], "location")
    logger.info("scrape finished — %d items", len(items))
    return items
