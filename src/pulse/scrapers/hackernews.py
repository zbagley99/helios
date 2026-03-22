"""Hacker News scraper via Firebase API."""

import asyncio
import logging

import httpx

from pulse.models import TrendItem
from shared.db import get_collection

logger = logging.getLogger(__name__)

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
MAX_ITEMS = 30


async def scrape_hackernews() -> list[TrendItem]:
    """Fetch top stories from Hacker News."""
    logger.info("scrape started")
    items: list[TrendItem] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(timeout=15, transport=transport) as client:
        resp = await client.get(HN_TOP_URL)
        resp.raise_for_status()
        story_ids = resp.json()[:MAX_ITEMS]

        async def fetch_item(story_id: int) -> TrendItem | None:
            try:
                detail = await client.get(HN_ITEM_URL.format(story_id))
                if detail.status_code != 200:
                    logger.warning("failed to fetch item %s: HTTP %s", story_id, detail.status_code)
                    return None
                data = detail.json()
                if not data or data.get("type") != "story":
                    return None
                return TrendItem(
                    title=data.get("title", ""),
                    url=data.get("url"),
                    source="hackernews",
                    category="tech",
                    score=data.get("score", 0),
                    description=None,
                )
            except httpx.HTTPError:
                logger.warning("error fetching item %s", story_id, exc_info=True)
                return None

        results = await asyncio.gather(*[fetch_item(sid) for sid in story_ids])
        items = [r for r in results if r is not None]

    if items:
        staging = get_collection("hackernews_staging")
        await staging.delete_many({})
        await staging.insert_many([item.model_dump(mode="json") for item in items])
        await staging.rename("hackernews", dropTarget=True)
    logger.info("scrape finished — %d items", len(items))
    return items
