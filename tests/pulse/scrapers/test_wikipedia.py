"""Tests for Wikipedia scraper."""

import respx
from httpx import Response

from pulse.scrapers.wikipedia import scrape_wikipedia

MOCK_WIKI_RESPONSE = {
    "items": [
        {
            "articles": [
                {"article": "Main_Page", "views": 1000000},
                {"article": "Special:Search", "views": 500000},
                {"article": "Python_(programming_language)", "views": 50000},
                {"article": "OpenAI", "views": 40000},
            ]
        }
    ]
}


class TestWikipediaScraper:
    """Test Wikipedia scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(url__regex=r"wikimedia\.org.*").mock(return_value=Response(200, json=MOCK_WIKI_RESPONSE))

        items = await scrape_wikipedia()
        # Skips Main_Page and Special:Search
        assert len(items) == 2
        assert items[0].title == "Python (programming language)"
        assert items[0].source == "wikipedia"

    @respx.mock
    async def test_scrape_filters_special_pages(self, mock_db):
        respx.get(url__regex=r"wikimedia\.org.*").mock(return_value=Response(200, json=MOCK_WIKI_RESPONSE))

        items = await scrape_wikipedia()
        titles = [i.title for i in items]
        assert "Main Page" not in titles

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(url__regex=r"wikimedia\.org.*").mock(return_value=Response(200, json=MOCK_WIKI_RESPONSE))

        await scrape_wikipedia()
        from shared.db import get_collection

        coll = get_collection("wikipedia")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(url__regex=r"wikimedia\.org.*").mock(return_value=Response(200, json=MOCK_WIKI_RESPONSE))

        await scrape_wikipedia()
        from shared.db import get_collection

        coll = get_collection("wikipedia")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
