"""InciWeb wildfire incidents RSS scraper."""

import logging
from xml.etree import ElementTree as ET  # noqa: S405

import httpx

from shared.scrape import persist_batch
from zephyr.models import Wildfire

logger = logging.getLogger(__name__)

INCIWEB_RSS_URL = "https://inciweb.wildfire.gov/incidents/rss.xml"


async def scrape_wildfires() -> list[Wildfire]:
    """Fetch active wildfire incidents from InciWeb RSS feed."""
    logger.info("scrape started")
    items: list[Wildfire] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(INCIWEB_RSS_URL)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)  # noqa: S314

        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            desc_el = item.find("description")

            if title_el is None or not title_el.text:
                continue

            description = desc_el.text.strip() if desc_el is not None and desc_el.text else None

            items.append(
                Wildfire(
                    title=title_el.text.strip(),
                    location=None,
                    url=link_el.text.strip() if link_el is not None and link_el.text else None,
                    published=pub_el.text.strip() if pub_el is not None and pub_el.text else None,
                    description=description[:500] if description else None,
                )
            )

    if items:
        await persist_batch("wildfires", [i.model_dump(mode="json") for i in items], "url")
    logger.info("scrape finished — %d items", len(items))
    return items
