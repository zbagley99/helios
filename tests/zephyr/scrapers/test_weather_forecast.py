"""Tests for weather forecast scraper."""

from unittest.mock import AsyncMock, patch

import respx
from httpx import Response

from zephyr.scrapers.weather_forecast import FORECAST_URL, scrape_weather_forecast

MOCK_COORDS = (38.8951, -77.0364, "Washington, District of Columbia, US")

MOCK_FORECAST_RESPONSE = {
    "daily": {
        "time": ["2026-03-23", "2026-03-24"],
        "temperature_2m_max": [15.0, 18.0],
        "temperature_2m_min": [5.0, 8.0],
        "precipitation_probability_max": [20, 40],
        "wind_speed_10m_max": [20.0, 15.0],
        "weathercode": [3, 1],
    }
}


class TestWeatherForecastScraper:
    """Test weather forecast scraper with mocked HTTP."""

    @respx.mock
    @patch("zephyr.scrapers.weather_forecast.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_returns_items(self, mock_geo, mock_db):
        respx.get(url__startswith=FORECAST_URL).mock(return_value=Response(200, json=MOCK_FORECAST_RESPONSE))

        items = await scrape_weather_forecast()
        assert len(items) == 2
        assert items[0].location == "Washington, District of Columbia, US"
        assert items[0].date == "2026-03-23"
        assert items[0].source == "open_meteo"

    @respx.mock
    @patch("zephyr.scrapers.weather_forecast.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_persists_to_db(self, mock_geo, mock_db):
        respx.get(url__startswith=FORECAST_URL).mock(return_value=Response(200, json=MOCK_FORECAST_RESPONSE))

        await scrape_weather_forecast()
        from shared.db import get_collection

        coll = get_collection("weather_forecast")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    @patch("zephyr.scrapers.weather_forecast.get_coords", new_callable=AsyncMock, return_value=MOCK_COORDS)
    async def test_scrape_sets_batch_fields(self, mock_geo, mock_db):
        respx.get(url__startswith=FORECAST_URL).mock(return_value=Response(200, json=MOCK_FORECAST_RESPONSE))

        await scrape_weather_forecast()
        from shared.db import get_collection

        coll = get_collection("weather_forecast")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
