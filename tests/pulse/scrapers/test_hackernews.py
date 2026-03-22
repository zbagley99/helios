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

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(HN_TOP_URL).mock(return_value=Response(200, json=[1]))
        respx.get(HN_ITEM_URL.format(1)).mock(
            return_value=Response(200, json={"type": "story", "title": "Story", "url": "https://a.com", "score": 5})
        )

        await scrape_hackernews()
        from shared.db import get_collection

        coll = get_collection("hackernews")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc

    @respx.mock
    async def test_scrape_change_detection(self, mock_db):
        """Second scrape marks persisting items and detects dropped ones."""
        respx.get(HN_TOP_URL).mock(return_value=Response(200, json=[1, 2]))
        respx.get(HN_ITEM_URL.format(1)).mock(
            return_value=Response(200, json={"type": "story", "title": "A", "url": "https://a.com", "score": 1})
        )
        respx.get(HN_ITEM_URL.format(2)).mock(
            return_value=Response(200, json={"type": "story", "title": "B", "url": "https://b.com", "score": 2})
        )
        await scrape_hackernews()

        # Second scrape: only story 1 remains, story 2 dropped, story 3 new
        respx.get(HN_TOP_URL).mock(return_value=Response(200, json=[1, 3]))
        respx.get(HN_ITEM_URL.format(3)).mock(
            return_value=Response(200, json={"type": "story", "title": "C", "url": "https://c.com", "score": 3})
        )
        await scrape_hackernews()

        from shared.db import get_collection

        coll = get_collection("hackernews")
        # Get latest batch docs
        latest = await coll.find_one({}, sort=[("batch_id", -1)])
        batch_id = latest["batch_id"]
        docs = await coll.find({"batch_id": batch_id}).to_list(length=100)
        status_map = {d["url"]: d["status"] for d in docs}
        assert status_map["https://a.com"] == "persisting"
        assert status_map["https://c.com"] == "new"
        assert status_map["https://b.com"] == "dropped"
