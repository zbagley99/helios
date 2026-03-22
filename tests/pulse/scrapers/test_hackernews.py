"""Tests for Hacker News scraper."""

import respx
from httpx import Response

from pulse.scrapers.hackernews import HN_ITEM_URL, HN_TOP_URL, scrape_hackernews


class TestHackerNewsScraper:
    """Test HN scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(HN_TOP_URL).mock(return_value=Response(200, json=[1, 2]))
        respx.get(HN_ITEM_URL.format(1)).mock(
            return_value=Response(200, json={"type": "story", "title": "Story 1", "url": "https://a.com", "score": 10})
        )
        respx.get(HN_ITEM_URL.format(2)).mock(
            return_value=Response(200, json={"type": "story", "title": "Story 2", "url": "https://b.com", "score": 5})
        )

        items = await scrape_hackernews()
        assert len(items) == 2
        assert items[0].title == "Story 1"
        assert items[0].source == "hackernews"

    @respx.mock
    async def test_scrape_skips_non_stories(self, mock_db):
        respx.get(HN_TOP_URL).mock(return_value=Response(200, json=[1]))
        respx.get(HN_ITEM_URL.format(1)).mock(
            return_value=Response(200, json={"type": "comment", "text": "hi"})
        )

        items = await scrape_hackernews()
        assert len(items) == 0

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(HN_TOP_URL).mock(return_value=Response(200, json=[1]))
        respx.get(HN_ITEM_URL.format(1)).mock(
            return_value=Response(200, json={"type": "story", "title": "Saved", "url": "https://c.com", "score": 1})
        )

        await scrape_hackernews()
        from shared.db import get_collection

        coll = get_collection("hackernews")
        count = await coll.count_documents({})
        assert count == 1
