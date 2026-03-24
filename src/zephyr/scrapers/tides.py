"""NOAA CO-OPS tidal predictions scraper."""

import logging
from datetime import UTC, datetime, timedelta

import httpx

from shared.scrape import persist_batch
from zephyr.config import ZephyrSettings
from zephyr.models import Tide

logger = logging.getLogger(__name__)

settings = ZephyrSettings()

NOAA_TIDES_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"


async def scrape_tides() -> list[Tide]:
    """Fetch high/low tide predictions from NOAA CO-OPS."""
    logger.info("scrape started")
    now = datetime.now(tz=UTC)
    begin = now.strftime("%Y%m%d")
    end = (now + timedelta(days=1)).strftime("%Y%m%d")
    params = {
        "station": settings.tide_station_id,
        "product": "predictions",
        "interval": "hilo",
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "units": "english",
        "format": "json",
        "begin_date": begin,
        "end_date": end,
    }
    items: list[Tide] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(NOAA_TIDES_URL, params=params)
        resp.raise_for_status()
        predictions = resp.json().get("predictions", [])

        items.extend(
            Tide(
                station=settings.tide_station_id,
                time=p["t"],
                prediction_ft=float(p["v"]),
            )
            for p in predictions
        )

    if items:
        await persist_batch("tides", [i.model_dump(mode="json") for i in items], "time")
    logger.info("scrape finished — %d items", len(items))
    return items
