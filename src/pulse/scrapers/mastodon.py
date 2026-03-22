"""Mastodon trending scraper via public API."""

import logging
import re

import httpx

from pulse.models import TrendItem
from shared.db import get_collection

logger = logging.getLogger(__name__)

MASTODON_TRENDS_URL = "https://mastodon.social/api/v1/trends/statuses"
MAX_ITEMS = 20


async def scrape_mastodon() -> list[TrendItem]:
    """Fetch trending statuses from mastodon.social."""
    logger.info("scrape started")
    items: list[TrendItem] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(timeout=15, transport=transport) as client:
        resp = await client.get(MASTODON_TRENDS_URL, params={"limit": MAX_ITEMS})
        resp.raise_for_status()
        statuses = resp.json()

        for status in statuses:
            content = status.get("content", "")
            clean = re.sub(r"<[^>]+>", "", content)[:200]
            items.append(
                TrendItem(
                    title=clean[:100] or "Untitled",
                    url=status.get("url"),
                    source="mastodon",
                    category="social",
                    score=status.get("reblogs_count", 0) + status.get("favourites_count", 0),
                    description=clean or None,
                )
            )

    if items:
        staging = get_collection("mastodon_staging")
        await staging.delete_many({})
        await staging.insert_many([item.model_dump(mode="json") for item in items])
        await staging.rename("mastodon", dropTarget=True)
    logger.info("scrape finished — %d items", len(items))
    return items
