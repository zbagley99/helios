"""Tests for USGS earthquake scraper."""

import pytest
import respx
from httpx import Response

from zephyr.scrapers.earthquakes import USGS_EARTHQUAKE_URL, scrape_earthquakes

MOCK_EARTHQUAKE_RESPONSE = {
    "features": [
        {
            "properties": {
                "title": "M 3.5 - 10km NW of Test",
                "mag": 3.5,
                "place": "10km NW of Test",
                "time": 1711152000000,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/test1",
            },
            "geometry": {"coordinates": [-122.5, 45.5, 10.2]},
        },
        {
            "properties": {
                "title": "M 4.0 - 20km SE of Other",
                "mag": 4.0,
                "place": "20km SE of Other",
                "time": 1711153000000,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/test2",
            },
            "geometry": {"coordinates": [-120.0, 40.0, 5.0]},
        },
    ]
}


class TestEarthquakeScraper:
    """Test earthquake scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(USGS_EARTHQUAKE_URL).mock(return_value=Response(200, json=MOCK_EARTHQUAKE_RESPONSE))

        items = await scrape_earthquakes()
        assert len(items) == 2
        assert items[0].title == "M 3.5 - 10km NW of Test"
        assert items[0].magnitude == pytest.approx(3.5)
        assert items[0].source == "usgs"

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(USGS_EARTHQUAKE_URL).mock(return_value=Response(200, json=MOCK_EARTHQUAKE_RESPONSE))

        await scrape_earthquakes()
        from shared.db import get_collection

        coll = get_collection("earthquakes")
        count = await coll.count_documents({})
        assert count == 2

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(USGS_EARTHQUAKE_URL).mock(return_value=Response(200, json=MOCK_EARTHQUAKE_RESPONSE))

        await scrape_earthquakes()
        from shared.db import get_collection

        coll = get_collection("earthquakes")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
