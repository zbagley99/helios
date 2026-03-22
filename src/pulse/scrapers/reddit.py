"""Reddit scraper via public JSON API."""

import logging

import httpx

from pulse.models import TrendItem
from shared.db import get_collection

logger = logging.getLogger(__name__)

REDDIT_URL = "https://www.reddit.com/r/popular/hot.json"
MAX_ITEMS = 30
USER_AGENT = "Helios/0.1 (trends aggregator)"


async def scrape_reddit() -> list[TrendItem]:
    """Fetch hot posts from r/popular."""
    logger.info("scrape started")
    items: list[TrendItem] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}, transport=transport) as client:
        resp = await client.get(REDDIT_URL, params={"limit": MAX_ITEMS})
        resp.raise_for_status()
        posts = resp.json().get("data", {}).get("children", [])

        for post in posts:
            d = post.get("data", {})
            items.append(
                TrendItem(
                    title=d.get("title", ""),
                    url=f"https://reddit.com{d.get('permalink', '')}",
                    source="reddit",
                    category=d.get("subreddit", "general"),
                    score=d.get("score", 0),
                    description=d.get("selftext", "")[:200] or None,
                )
            )

    if items:
        staging = get_collection("reddit_staging")
        await staging.delete_many({})
        await staging.insert_many([item.model_dump(mode="json") for item in items])
        await staging.rename("reddit", dropTarget=True)
    logger.info("scrape finished — %d items", len(items))
    return items
