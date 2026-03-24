"""Tests for NOAA SWPC space weather alerts scraper."""

import respx
from httpx import Response

from zephyr.scrapers.space_weather import SWPC_ALERTS_URL, scrape_space_weather

MOCK_ALERTS_RESPONSE = [
    {
        "product_id": "1",
        "issue_datetime": "2026-03-23 12:00:00.000",
        "message": "Space Weather Alert",
        "serial_number": "1234",
    }
]


class TestSpaceWeatherScraper:
    """Test space weather scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(SWPC_ALERTS_URL).mock(return_value=Response(200, json=MOCK_ALERTS_RESPONSE))

        items = await scrape_space_weather()
        assert len(items) == 1
        assert items[0].message == "Space Weather Alert"
        assert items[0].source == "swpc"

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(SWPC_ALERTS_URL).mock(return_value=Response(200, json=MOCK_ALERTS_RESPONSE))

        await scrape_space_weather()
        from shared.db import get_collection

        coll = get_collection("space_weather")
        count = await coll.count_documents({})
        assert count == 1

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(SWPC_ALERTS_URL).mock(return_value=Response(200, json=MOCK_ALERTS_RESPONSE))

        await scrape_space_weather()
        from shared.db import get_collection

        coll = get_collection("space_weather")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
