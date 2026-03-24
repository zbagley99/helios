"""NOAA SWPC Kp index forecast scraper."""

import logging

import httpx

from shared.scrape import persist_batch
from zephyr.models import KpIndex

logger = logging.getLogger(__name__)

KP_INDEX_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"


async def scrape_kp_index() -> list[KpIndex]:
    """Fetch Kp index forecast from NOAA SWPC."""
    logger.info("scrape started")
    items: list[KpIndex] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(KP_INDEX_URL)
        resp.raise_for_status()
        rows = resp.json()

        # First element is the header row; skip it
        items.extend(
            KpIndex(
                time_tag=row[0],
                kp=float(row[1]),
                observed=row[2] or None,
                source="swpc",
            )
            for row in rows[1:]
        )

    if items:
        await persist_batch("kp_index", [item.model_dump(mode="json") for item in items], "time_tag")
    logger.info("scrape finished — %d items", len(items))
    return items
