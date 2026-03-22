"""Google Trends scraper via RSS feed."""

import logging
import re
from xml.etree import ElementTree as ET  # noqa: S405

import httpx

from pulse.models import TrendItem
from shared.scrape import persist_batch

logger = logging.getLogger(__name__)

GOOGLE_TRENDS_URL = "https://trends.google.com/trending/rss?geo=US"

HT_NS = {"ht": "https://trends.google.com/trending/rss"}


def parse_trends_rss(xml_text: str) -> list[TrendItem]:
    """Parse Google Trends RSS XML into TrendItem list."""
    items: list[TrendItem] = []
    root = ET.fromstring(xml_text)  # noqa: S314
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        if title_el is None or not title_el.text:
            continue
        traffic_el = item.find("ht:approx_traffic", HT_NS)
        score = _parse_traffic(traffic_el.text) if traffic_el is not None and traffic_el.text else None
        items.append(
            TrendItem(
                title=title_el.text.strip(),
                url=link_el.text.strip() if link_el is not None and link_el.text else None,
                source="google",
                category="trending",
                score=score,
            )
        )
    return items


def _parse_traffic(traffic: str) -> float | None:
    """Parse traffic string like '500,000+' into a numeric value."""
    digits = re.sub(r"[^\d]", "", traffic)
    return float(digits) if digits else None


async def scrape_google_trends() -> list[TrendItem]:
    """Fetch trending topics from Google Trends RSS feed."""
    logger.info("scrape started")
    items: list[TrendItem] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, follow_redirects=True, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(GOOGLE_TRENDS_URL)
        resp.raise_for_status()
        items = parse_trends_rss(resp.text)

    if not items:
        logger.warning("no trends extracted from RSS feed")

    if items:
        await persist_batch("google", [item.model_dump(mode="json") for item in items], "url")
    logger.info("scrape finished — %d items", len(items))
    return items
