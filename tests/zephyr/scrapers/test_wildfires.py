"""Tests for wildfires scraper."""

import respx
from httpx import Response

from zephyr.scrapers.wildfires import INCIWEB_RSS_URL, scrape_wildfires

RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<item>
<title>Test Fire</title>
<link>https://inciweb.wildfire.gov/incident/123</link>
<pubDate>Mon, 23 Mar 2026 00:00:00 GMT</pubDate>
<description>A wildfire in Oregon</description>
</item>
<item>
<title>Another Fire</title>
<link>https://inciweb.wildfire.gov/incident/456</link>
<pubDate>Mon, 23 Mar 2026 12:00:00 GMT</pubDate>
<description>A wildfire in California</description>
</item>
</channel>
</rss>"""


class TestWildfiresScraper:
    """Test wildfires scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(INCIWEB_RSS_URL).mock(return_value=Response(200, text=RSS_XML))

        items = await scrape_wildfires()
        assert len(items) == 2
        assert items[0].title == "Test Fire"
        assert items[1].title == "Another Fire"
        assert items[0].source == "inciweb"

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(INCIWEB_RSS_URL).mock(return_value=Response(200, text=RSS_XML))

        await scrape_wildfires()
        from shared.db import get_collection

        coll = get_collection("wildfires")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(INCIWEB_RSS_URL).mock(return_value=Response(200, text=RSS_XML))

        await scrape_wildfires()
        from shared.db import get_collection

        coll = get_collection("wildfires")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
