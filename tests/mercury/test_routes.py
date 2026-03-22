"""Tests for Mercury routes."""

from datetime import UTC, datetime

from shared.db import get_collection


class TestCommoditiesRoutes:
    """Test commodity API endpoints."""

    async def test_summary_empty(self, mercury_client, mock_db):
        resp = await mercury_client.get("/commodities/summary")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_summary_with_data(self, mercury_client, mock_db):
        coll = get_collection("commodities")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2000, "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
            {
                "ticker": "SI=F", "name": "Silver", "category": "metals",
                "price": 25, "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
        ])
        resp = await mercury_client.get("/commodities/summary")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_category_filter(self, mercury_client, mock_db):
        coll = get_collection("commodities")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2000, "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
            {
                "ticker": "CL=F", "name": "Crude Oil", "category": "energy",
                "price": 75, "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
        ])
        resp = await mercury_client.get("/commodities/category/metals")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["category"] == "metals"

    async def test_category_not_found(self, mercury_client, mock_db):
        resp = await mercury_client.get("/commodities/category/invalid")
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] == "Category not found: invalid"

    async def test_ticker_found(self, mercury_client, mock_db):
        coll = get_collection("commodities")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_one({
            "ticker": "GC=F", "name": "Gold", "category": "metals",
            "price": 2000, "batch_id": batch_id, "scraped_at": now, "status": "new",
        })
        resp = await mercury_client.get("/commodities/ticker/GC=F")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ticker"] == "GC=F"

    async def test_ticker_not_in_registry(self, mercury_client, mock_db):
        resp = await mercury_client.get("/commodities/ticker/FAKE")
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] == "Ticker not found"

    async def test_ticker_not_in_db(self, mercury_client, mock_db):
        resp = await mercury_client.get("/commodities/ticker/GC=F")
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] == "Ticker not found"

    async def test_health(self, mercury_client):
        resp = await mercury_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "mercury"

    async def test_status_filter(self, mercury_client, mock_db):
        coll = get_collection("commodities")
        batch_id = datetime.now(tz=UTC).isoformat()
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2000, "batch_id": batch_id, "scraped_at": now, "status": "new",
            },
            {
                "ticker": "SI=F", "name": "Silver", "category": "metals",
                "price": 25, "batch_id": batch_id, "scraped_at": now, "status": "persisting",
            },
        ])
        resp = await mercury_client.get("/commodities/summary", params={"status": "new"})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "new"

    async def test_history_param(self, mercury_client, mock_db):
        coll = get_collection("commodities")
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2000, "batch_id": "2026-01-01T00:00:00", "scraped_at": now, "status": "new",
            },
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2010, "batch_id": "2026-01-02T00:00:00", "scraped_at": now, "status": "persisting",
            },
        ])
        # Without history — returns only latest batch
        resp = await mercury_client.get("/commodities/summary")
        assert len(resp.json()) == 1

        # With history — returns all
        resp = await mercury_client.get("/commodities/summary", params={"history": "true"})
        assert len(resp.json()) == 2

    async def test_ticker_history(self, mercury_client, mock_db):
        coll = get_collection("commodities")
        now = datetime.now(tz=UTC)
        await coll.insert_many([
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2000, "batch_id": "2026-01-01T00:00:00", "scraped_at": now, "status": "new",
            },
            {
                "ticker": "GC=F", "name": "Gold", "category": "metals",
                "price": 2010, "batch_id": "2026-01-02T00:00:00", "scraped_at": now, "status": "persisting",
            },
        ])
        resp = await mercury_client.get("/commodities/ticker/GC=F", params={"history": "true"})
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2
