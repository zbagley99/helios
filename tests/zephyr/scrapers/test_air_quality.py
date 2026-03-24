"""Tests for air quality scraper."""

from unittest.mock import AsyncMock, patch

import respx
from httpx import Response

from zephyr.scrapers.air_quality import AIR_QUALITY_URL, scrape_air_quality

MOCK_COORDS = (38.8951, -77.0364, "Washington, District of Columbia, US")

MOCK_AIR_QUALITY_RESPONSE = {
    "current": {
        "pm10": 15.2,
        "pm2_5": 8.3,
        "us_aqi": 42,
    }
}


class TestAirQualityScraper:
    """Test air quality scraper with mocked HTTP."""

    @respx.mock
    @patch("zephyr.scrapers.air_quality.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_returns_items(self, mock_geo, mock_db):
        respx.get(url__startswith=AIR_QUALITY_URL).mock(return_value=Response(200, json=MOCK_AIR_QUALITY_RESPONSE))

        items = await scrape_air_quality()
        assert len(items) == 1
        assert items[0].location == "Washington, District of Columbia, US"
        assert items[0].aqi == 42
        assert items[0].source == "open_meteo"

    @respx.mock
    @patch("zephyr.scrapers.air_quality.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_persists_to_db(self, mock_geo, mock_db):
        respx.get(url__startswith=AIR_QUALITY_URL).mock(return_value=Response(200, json=MOCK_AIR_QUALITY_RESPONSE))

        await scrape_air_quality()
        from shared.db import get_collection

        coll = get_collection("air_quality")
        count = await coll.count_documents({})
        assert count == 1

    @respx.mock
    @patch("zephyr.scrapers.air_quality.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_sets_batch_fields(self, mock_geo, mock_db):
        respx.get(url__startswith=AIR_QUALITY_URL).mock(return_value=Response(200, json=MOCK_AIR_QUALITY_RESPONSE))

        await scrape_air_quality()
        from shared.db import get_collection

        coll = get_collection("air_quality")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
