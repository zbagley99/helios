"""International Space Station position and crew scraper."""

import logging
from datetime import UTC, datetime

import httpx

from shared.scrape import persist_batch
from zephyr.models import ISSPosition

logger = logging.getLogger(__name__)

ISS_POSITION_URL = "http://api.open-notify.org/iss-now.json"
ISS_CREW_URL = "http://api.open-notify.org/astros.json"


async def scrape_iss() -> list[ISSPosition]:
    """Fetch current ISS position and crew manifest."""
    logger.info("scrape started")
    items: list[ISSPosition] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        pos_resp = await client.get(ISS_POSITION_URL)
        pos_resp.raise_for_status()
        pos_data = pos_resp.json()

        crew_resp = await client.get(ISS_CREW_URL)
        crew_resp.raise_for_status()
        crew_data = crew_resp.json()

        iss_pos = pos_data.get("iss_position", {})
        crew = [
            p["name"]
            for p in crew_data.get("people", [])
            if p.get("craft") == "ISS"
        ]

        items.append(
            ISSPosition(
                latitude=float(iss_pos.get("latitude", 0)),
                longitude=float(iss_pos.get("longitude", 0)),
                timestamp=datetime.fromtimestamp(pos_data.get("timestamp", 0), tz=UTC),
                crew=crew,
            )
        )

    if items:
        await persist_batch("iss", [i.model_dump(mode="json") for i in items], "source")
    logger.info("scrape finished — %d items", len(items))
    return items
