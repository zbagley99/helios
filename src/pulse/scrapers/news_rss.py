"""News RSS scraper for major outlets."""

import asyncio
import itertools
import logging
from xml.etree import ElementTree as ET  # noqa: S405

import httpx

from pulse.models import TrendItem
from shared.scrape import persist_batch

logger = logging.getLogger(__name__)

RSS_FEEDS: dict[str, str] = {
    "ap": "https://rsshub.app/apnews/topics/apf-topnews",
    "reuters": "https://rsshub.app/reuters/world",
    "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    "npr": "https://feeds.npr.org/1001/rss.xml",
}


def parse_rss(xml_text: str, feed_name: str) -> list[TrendItem]:
    """Parse RSS XML into TrendItem list."""
    items: list[TrendItem] = []
    root = ET.fromstring(xml_text)  # noqa: S314
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")
        if title_el is None or not title_el.text:
            continue
        items.append(
            TrendItem(
                title=title_el.text.strip(),
                url=link_el.text.strip() if link_el is not None and link_el.text else None,
                source="news",
                category=feed_name,
                description=desc_el.text.strip()[:200] if desc_el is not None and desc_el.text else None,
            )
        )
    return items


async def scrape_news_rss() -> list[TrendItem]:
    """Fetch and parse all configured RSS feeds."""
    logger.info("scrape started")
    all_items: list[TrendItem] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport) as client:

        async def fetch_feed(feed_name: str, url: str) -> list[TrendItem]:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return parse_rss(resp.text, feed_name)
            except httpx.HTTPError:
                logger.warning("failed to fetch feed %s", feed_name, exc_info=True)
                return []

        results = await asyncio.gather(*itertools.starmap(fetch_feed, RSS_FEEDS.items()))
        for feed_items in results:
            all_items.extend(feed_items)

    if all_items:
        await persist_batch("news", [item.model_dump(mode="json") for item in all_items], "url")
    logger.info("scrape finished — %d items", len(all_items))
    return all_items
