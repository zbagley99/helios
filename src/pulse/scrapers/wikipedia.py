"""Wikipedia most-viewed pages scraper via Wikimedia REST API."""

import logging
from datetime import UTC, datetime, timedelta

import httpx

from pulse.models import TrendItem
from shared.db import get_collection

logger = logging.getLogger(__name__)

WIKI_API = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date}"
MAX_ITEMS = 30


async def scrape_wikipedia() -> list[TrendItem]:
    """Fetch yesterday's most-viewed Wikipedia articles."""
    logger.info("scrape started")
    yesterday = datetime.now(tz=UTC) - timedelta(days=1)
    date_str = yesterday.strftime("%Y/%m/%d")
    items: list[TrendItem] = []

    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport) as client:
        resp = await client.get(WIKI_API.format(date=date_str))
        resp.raise_for_status()
        articles = resp.json().get("items", [{}])[0].get("articles", [])

        for article in articles[:MAX_ITEMS]:
            title = article.get("article", "").replace("_", " ")
            if title.startswith("Special:") or title == "Main Page":
                continue
            items.append(
                TrendItem(
                    title=title,
                    url=f"https://en.wikipedia.org/wiki/{article.get('article', '')}",
                    source="wikipedia",
                    category="reference",
                    score=article.get("views", 0),
                )
            )

    if items:
        staging = get_collection("wikipedia_staging")
        await staging.delete_many({})
        await staging.insert_many([item.model_dump(mode="json") for item in items])
        await staging.rename("wikipedia", dropTarget=True)
    logger.info("scrape finished — %d items", len(items))
    return items
