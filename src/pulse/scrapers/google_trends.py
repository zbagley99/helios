"""Google Trends scraper via trending page."""

import json
import logging
import re

import httpx
from bs4 import BeautifulSoup

from pulse.models import TrendItem
from shared.scrape import persist_batch

logger = logging.getLogger(__name__)

GOOGLE_TRENDS_URL = "https://trends.google.com/trending?geo=US"
MAX_ITEMS = 20


def parse_trends_page(html: str) -> list[TrendItem]:
    """Extract trending topics from the Google Trends page HTML."""
    items: list[TrendItem] = []

    # Try to find embedded JSON data first
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "trendingSearches" in script.string:
            matches = re.findall(r'\{[^{}]*"title"[^{}]*\}', script.string)
            for match in matches[:MAX_ITEMS]:
                try:
                    data = json.loads(match)
                    items.append(
                        TrendItem(
                            title=data.get("title", {}).get("query", data.get("query", "")),
                            url=f"https://trends.google.com{data.get('url', '')}",
                            source="google",
                            category="trending",
                            score=None,
                        )
                    )
                except (json.JSONDecodeError, AttributeError):
                    logger.warning("failed to parse trend JSON match: %s", match[:80])
                    continue

    # Fallback: parse visible trending items from HTML
    if not items:
        for el in soup.select("[class*='trending'], [class*='trend-item'], .mZ3RIc"):
            text = el.get_text(strip=True)
            if text and len(text) > 1:
                items.append(
                    TrendItem(
                        title=text[:100],
                        source="google",
                        category="trending",
                    )
                )
                if len(items) >= MAX_ITEMS:
                    break

    return items


async def scrape_google_trends() -> list[TrendItem]:
    """Fetch trending topics from Google Trends."""
    logger.info("scrape started")
    items: list[TrendItem] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
    }
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(timeout=15, headers=headers, follow_redirects=True, transport=transport) as client:
        resp = await client.get(GOOGLE_TRENDS_URL)
        resp.raise_for_status()
        items = parse_trends_page(resp.text)

    if not items:
        logger.warning("no trends extracted from page — parser may need updating")

    if items:
        await persist_batch("google", [item.model_dump(mode="json") for item in items], "title")
    logger.info("scrape finished — %d items", len(items))
    return items
