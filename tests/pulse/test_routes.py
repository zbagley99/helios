"""Tests for Pulse routes."""

from shared.db import get_collection


class TestTrendsRoute:
    """Test GET /trends endpoints."""

    async def test_get_trends_empty(self, pulse_client, mock_db):
        resp = await pulse_client.get("/trends")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_trends_with_data(self, pulse_client, mock_db):
        coll = get_collection("hackernews")
        await coll.insert_many([
            {"title": "Story 1", "source": "hackernews", "url": "https://a.com", "category": "tech"},
            {"title": "Story 2", "source": "hackernews", "url": "https://b.com", "category": "tech"},
        ])
        resp = await pulse_client.get("/trends")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_get_trends_by_source(self, pulse_client, mock_db):
        coll = get_collection("reddit")
        await coll.insert_one({"title": "Reddit Post", "source": "reddit", "url": "https://r.com", "category": "fun"})
        resp = await pulse_client.get("/trends/source/reddit")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["source"] == "reddit"

    async def test_get_trends_unknown_source(self, pulse_client, mock_db):
        resp = await pulse_client.get("/trends/source/twitter")
        assert resp.status_code == 404
        data = resp.json()
        assert data["error"] == "Unknown source: twitter"

    async def test_health(self, pulse_client):
        resp = await pulse_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "pulse"
