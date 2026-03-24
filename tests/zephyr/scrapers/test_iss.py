"""Tests for ISS scraper."""

import pytest
import respx
from httpx import Response

from zephyr.scrapers.iss import ISS_CREW_URL, ISS_POSITION_URL, scrape_iss

MOCK_POSITION_RESPONSE = {
    "iss_position": {"latitude": "45.5", "longitude": "-122.6"},
    "timestamp": 1711152000,
    "message": "success",
}

MOCK_CREW_RESPONSE = {
    "people": [
        {"craft": "ISS", "name": "Alice"},
        {"craft": "ISS", "name": "Bob"},
        {"craft": "Tiangong", "name": "Charlie"},
    ],
    "number": 3,
    "message": "success",
}


class TestISSScraper:
    """Test ISS scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(ISS_POSITION_URL).mock(return_value=Response(200, json=MOCK_POSITION_RESPONSE))
        respx.get(ISS_CREW_URL).mock(return_value=Response(200, json=MOCK_CREW_RESPONSE))

        items = await scrape_iss()
        assert len(items) == 1
        assert items[0].latitude == pytest.approx(45.5)
        assert items[0].longitude == pytest.approx(-122.6)
        assert items[0].source == "open_notify"
        assert items[0].crew == ["Alice", "Bob"]
        assert "Charlie" not in items[0].crew

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(ISS_POSITION_URL).mock(return_value=Response(200, json=MOCK_POSITION_RESPONSE))
        respx.get(ISS_CREW_URL).mock(return_value=Response(200, json=MOCK_CREW_RESPONSE))

        await scrape_iss()
        from shared.db import get_collection

        coll = get_collection("iss")
        count = await coll.count_documents({})
        assert count == 1

    @respx.mock
    async def test_scrape_sets_batch_fields(self, mock_db):
        respx.get(ISS_POSITION_URL).mock(return_value=Response(200, json=MOCK_POSITION_RESPONSE))
        respx.get(ISS_CREW_URL).mock(return_value=Response(200, json=MOCK_CREW_RESPONSE))

        await scrape_iss()
        from shared.db import get_collection

        coll = get_collection("iss")
        doc = await coll.find_one({})
        assert doc["status"] == "new"
        assert doc["batch_id"]
        assert "scraped_at" in doc
