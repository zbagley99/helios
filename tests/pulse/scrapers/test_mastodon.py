"""Tests for Mastodon scraper."""

import respx
from httpx import Response

from pulse.scrapers.mastodon import MASTODON_TRENDS_URL, scrape_mastodon

MOCK_MASTODON_RESPONSE = [
    {
        "content": "<p>This is a <strong>trending</strong> post</p>",
        "url": "https://mastodon.social/@user/12345",
        "reblogs_count": 10,
        "favourites_count": 50,
    },
    {
        "content": "<p>Another post with no HTML</p>",
        "url": "https://mastodon.social/@other/67890",
        "reblogs_count": 5,
        "favourites_count": 20,
    },
]


class TestMastodonScraper:
    """Test Mastodon scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(MASTODON_TRENDS_URL).mock(return_value=Response(200, json=MOCK_MASTODON_RESPONSE))

        items = await scrape_mastodon()
        assert len(items) == 2
        assert items[0].source == "mastodon"
        assert items[0].score == 60  # 10 + 50

    @respx.mock
    async def test_scrape_strips_html(self, mock_db):
        respx.get(MASTODON_TRENDS_URL).mock(return_value=Response(200, json=MOCK_MASTODON_RESPONSE))

        items = await scrape_mastodon()
        assert "<" not in items[0].description
        assert "trending" in items[0].description

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(MASTODON_TRENDS_URL).mock(return_value=Response(200, json=MOCK_MASTODON_RESPONSE))

        await scrape_mastodon()
        from shared.db import get_collection

        coll = get_collection("mastodon")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(MASTODON_TRENDS_URL).mock(return_value=Response(200, json=MOCK_MASTODON_RESPONSE))

        await scrape_mastodon()
        from shared.db import get_collection

        coll = get_collection("mastodon")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
