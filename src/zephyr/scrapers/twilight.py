"""Sunrise, sunset, and twilight times via sunrise-sunset.org."""

import logging
from datetime import UTC, datetime

import httpx

from shared.scrape import persist_batch
from zephyr.geocode import get_coords
from zephyr.models import Twilight

logger = logging.getLogger(__name__)

SUNRISE_SUNSET_URL = "https://api.sunrise-sunset.org/json"


async def scrape_twilight() -> list[Twilight]:
    """Fetch sunrise/sunset and twilight times for the configured location."""
    logger.info("scrape started")
    lat, lng, display = await get_coords()
    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    items: list[Twilight] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(
            SUNRISE_SUNSET_URL, params={"lat": lat, "lng": lng, "formatted": 0}
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "OK":
            r = data["results"]
            day_secs = r.get("day_length", 0)
            hours, remainder = divmod(int(day_secs), 3600)
            minutes, seconds = divmod(remainder, 60)
            day_length = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            items.append(
                Twilight(
                    location=display,
                    date=today,
                    sunrise=r["sunrise"],
                    sunset=r["sunset"],
                    civil_twilight_begin=r["civil_twilight_begin"],
                    civil_twilight_end=r["civil_twilight_end"],
                    day_length=day_length,
                )
            )

    if items:
        await persist_batch("twilight", [i.model_dump(mode="json") for i in items], "date")
    logger.info("scrape finished — %d items", len(items))
    return items
