"""Tests for tides scraper."""

import pytest
import respx
from httpx import Response

from zephyr.scrapers.tides import NOAA_TIDES_URL, scrape_tides

MOCK_TIDES_RESPONSE = {
    "predictions": [
        {"t": "2026-03-23 06:12", "v": "4.5", "type": "H"},
        {"t": "2026-03-23 12:30", "v": "0.3", "type": "L"},
    ]
}


class TestTidesScraper:
    """Test tides scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(NOAA_TIDES_URL).mock(return_value=Response(200, json=MOCK_TIDES_RESPONSE))

        items = await scrape_tides()
        assert len(items) == 2
        assert items[0].prediction_ft == pytest.approx(4.5)
        assert items[1].prediction_ft == pytest.approx(0.3)
        assert items[0].source == "noaa"

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(NOAA_TIDES_URL).mock(return_value=Response(200, json=MOCK_TIDES_RESPONSE))

        await scrape_tides()
        from shared.db import get_collection

        coll = get_collection("tides")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(NOAA_TIDES_URL).mock(return_value=Response(200, json=MOCK_TIDES_RESPONSE))

        await scrape_tides()
        from shared.db import get_collection

        coll = get_collection("tides")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
