"""Tests for NOAA SWPC Kp index forecast scraper."""

import pytest
import respx
from httpx import Response

from zephyr.scrapers.kp_index import KP_INDEX_URL, scrape_kp_index

MOCK_KP_RESPONSE = [
    ["time_tag", "kp", "observed", "noaa_scale"],
    ["2026-03-23 00:00:00", "2.33", "observed", ""],
    ["2026-03-23 03:00:00", "1.67", "predicted", ""],
]


class TestKpIndexScraper:
    """Test Kp index scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(KP_INDEX_URL).mock(return_value=Response(200, json=MOCK_KP_RESPONSE))

        items = await scrape_kp_index()
        assert len(items) == 2
        assert items[0].kp == pytest.approx(2.33)
        assert items[0].source == "swpc"

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(KP_INDEX_URL).mock(return_value=Response(200, json=MOCK_KP_RESPONSE))

        await scrape_kp_index()
        from shared.db import get_collection

        coll = get_collection("kp_index")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(KP_INDEX_URL).mock(return_value=Response(200, json=MOCK_KP_RESPONSE))

        await scrape_kp_index()
        from shared.db import get_collection

        coll = get_collection("kp_index")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
