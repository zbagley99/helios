"""Tests for current weather scraper."""

from unittest.mock import AsyncMock, patch

import pytest
import respx
from httpx import Response

from zephyr.scrapers.weather_current import WEATHER_URL, scrape_weather_current

MOCK_COORDS = (38.8951, -77.0364, "Washington, District of Columbia, US")

MOCK_WEATHER_RESPONSE = {
    "current": {
        "temperature_2m": 20.0,
        "relative_humidity_2m": 65,
        "apparent_temperature": 18.0,
        "precipitation": 0.0,
        "wind_speed_10m": 15.0,
        "wind_direction_10m": 225,
        "uv_index": 3.5,
    }
}


class TestWeatherCurrentScraper:
    """Test current weather scraper with mocked HTTP."""

    @respx.mock
    @patch("zephyr.scrapers.weather_current.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_returns_items(self, mock_geo, mock_db):
        respx.get(url__startswith=WEATHER_URL).mock(return_value=Response(200, json=MOCK_WEATHER_RESPONSE))

        items = await scrape_weather_current()
        assert len(items) == 1
        assert items[0].location == "Washington, District of Columbia, US"
        assert items[0].temperature_c == pytest.approx(20.0)
        assert items[0].source == "open_meteo"

    @respx.mock
    @patch("zephyr.scrapers.weather_current.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_persists_to_db(self, mock_geo, mock_db):
        respx.get(url__startswith=WEATHER_URL).mock(return_value=Response(200, json=MOCK_WEATHER_RESPONSE))

        await scrape_weather_current()
        from shared.db import get_collection

        coll = get_collection("weather_current")
        count = await coll.count_documents({})
        assert count == 1

    @respx.mock
    @patch("zephyr.scrapers.weather_current.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_sets_batch_fields(self, mock_geo, mock_db):
        respx.get(url__startswith=WEATHER_URL).mock(return_value=Response(200, json=MOCK_WEATHER_RESPONSE))

        await scrape_weather_current()
        from shared.db import get_collection

        coll = get_collection("weather_current")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
