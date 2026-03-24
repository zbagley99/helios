"""Tests for twilight scraper."""

from unittest.mock import AsyncMock, patch

import respx
from httpx import Response

from zephyr.scrapers.twilight import SUNRISE_SUNSET_URL, scrape_twilight

MOCK_COORDS = (38.8951, -77.0364, "Washington, District of Columbia, US")

MOCK_TWILIGHT_RESPONSE = {
    "results": {
        "sunrise": "2026-03-23T11:30:00+00:00",
        "sunset": "2026-03-23T23:45:00+00:00",
        "civil_twilight_begin": "2026-03-23T11:00:00+00:00",
        "civil_twilight_end": "2026-03-24T00:15:00+00:00",
        "day_length": 44100,
    },
    "status": "OK",
}


class TestTwilightScraper:
    """Test twilight scraper with mocked HTTP."""

    @respx.mock
    @patch("zephyr.scrapers.twilight.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_returns_items(self, mock_geo, mock_db):
        respx.get(SUNRISE_SUNSET_URL).mock(return_value=Response(200, json=MOCK_TWILIGHT_RESPONSE))

        items = await scrape_twilight()
        assert len(items) == 1
        assert items[0].location == "Washington, District of Columbia, US"
        assert items[0].sunrise == "2026-03-23T11:30:00+00:00"
        assert items[0].source == "sunrise_sunset"

    @respx.mock
    @patch("zephyr.scrapers.twilight.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_persists_to_db(self, mock_geo, mock_db):
        respx.get(SUNRISE_SUNSET_URL).mock(return_value=Response(200, json=MOCK_TWILIGHT_RESPONSE))

        await scrape_twilight()
        from shared.db import get_collection

        coll = get_collection("twilight")
        count = await coll.count_documents({})
        assert count == 1

    @respx.mock
    @patch("zephyr.scrapers.twilight.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_sets_batch_fields(self, mock_geo, mock_db):
        respx.get(SUNRISE_SUNSET_URL).mock(return_value=Response(200, json=MOCK_TWILIGHT_RESPONSE))

        await scrape_twilight()
        from shared.db import get_collection

        coll = get_collection("twilight")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
