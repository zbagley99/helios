"""Tests for Pulse routes."""

from datetime import UTC, datetime

from shared.db import get_collection


class TestTrendsRoute:
    """Test GET /trends endpoints."""

    async def test_get_trends_empty(self, pulse_client, mock_db):
        resp = await pulse_client.get("/trends")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_trends_with_data(self, pulse_client, mock_db):
        coll = get_collection("hackernews")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "title": "Story 1", "source": "hackernews", "url": "https://a.com",
                "category": "tech", "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
            {
                "title": "Story 2", "source": "hackernews", "url": "https://b.com",
                "category": "tech", "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
        ])
        resp = await pulse_client.get("/trends")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_get_trends_by_source(self, pulse_client, mock_db):
        coll = get_collection("reddit")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_one({
            "title": "Reddit Post", "source": "reddit", "url": "https://r.com",
            "category": "fun", "batch_id": batch_id, "scraped_at": now, "status": "new",
        })
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

    async def test_status_filter(self, pulse_client, mock_db):
        coll = get_collection("hackernews")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "title": "New", "source": "hackernews", "url": "https://new.com",
                "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
            {
                "title": "Old", "source": "hackernews", "url": "https://old.com",
                "batch_id": batch_id, "scraped_at": now, "status": "persisting",
            },
        ])
        resp = await pulse_client.get("/trends", params={"status": "new"})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "new"

    async def test_history_param(self, pulse_client, mock_db):
        coll = get_collection("hackernews")
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "title": "Batch1", "source": "hackernews", "url": "https://a.com",
                "batch_id": "2026-01-01T00:00:00", "scraped_at": now, "status": "new",
            },
            {
                "title": "Batch2", "source": "hackernews", "url": "https://a.com",
                "batch_id": "2026-01-02T00:00:00", "scraped_at": now, "status": "persisting",
            },
        ])
        # Without history — returns only latest batch
        resp = await pulse_client.get("/trends")
        assert len(resp.json()) == 1
        assert resp.json()[0]["batch_id"] == "2026-01-02T00:00:00"

        # With history — returns all
        resp = await pulse_client.get("/trends", params={"history": "true"})
        assert len(resp.json()) == 2
