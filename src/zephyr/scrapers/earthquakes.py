"""USGS earthquake feed scraper."""

import logging
from datetime import UTC, datetime

import httpx

from shared.scrape import persist_batch
from zephyr.models import Earthquake

logger = logging.getLogger(__name__)

USGS_EARTHQUAKE_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"


async def scrape_earthquakes() -> list[Earthquake]:
    """Fetch recent M2.5+ earthquakes from USGS GeoJSON feed."""
    logger.info("scrape started")
    items: list[Earthquake] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(USGS_EARTHQUAKE_URL)
        resp.raise_for_status()
        features = resp.json().get("features", [])

        for f in features:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [0, 0, 0])
            items.append(
                Earthquake(
                    title=props.get("title", ""),
                    magnitude=props.get("mag", 0.0),
                    location=props.get("place", ""),
                    latitude=coords[1],
                    longitude=coords[0],
                    depth_km=coords[2],
                    time=datetime.fromtimestamp(props.get("time", 0) / 1000, tz=UTC),
                    url=props.get("url"),
                    source="usgs",
                )
            )

    if items:
        await persist_batch("earthquakes", [item.model_dump(mode="json") for item in items], "url")
    logger.info("scrape finished — %d items", len(items))
    return items
