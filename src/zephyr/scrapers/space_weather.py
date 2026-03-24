"""NOAA SWPC space weather alerts scraper."""

import logging

import httpx

from shared.scrape import persist_batch
from zephyr.models import SpaceWeatherAlert

logger = logging.getLogger(__name__)

SWPC_ALERTS_URL = "https://services.swpc.noaa.gov/products/alerts.json"
MAX_ALERTS = 20


async def scrape_space_weather() -> list[SpaceWeatherAlert]:
    """Fetch recent space weather alerts from NOAA SWPC."""
    logger.info("scrape started")
    items: list[SpaceWeatherAlert] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(SWPC_ALERTS_URL)
        resp.raise_for_status()
        alerts = resp.json()

        items.extend(
            SpaceWeatherAlert(
                issue_datetime=alert.get("issue_datetime", ""),
                message=alert.get("message", ""),
                serial_number=alert.get("serial_number"),
                source="swpc",
            )
            for alert in alerts[-MAX_ALERTS:]
        )

    if items:
        await persist_batch("space_weather", [item.model_dump(mode="json") for item in items], "issue_datetime")
    logger.info("scrape finished — %d items", len(items))
    return items
