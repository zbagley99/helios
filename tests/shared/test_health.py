"""Tests for shared.models and shared.health."""

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from shared.health import create_health_router
from shared.models import ErrorResponse, HealthResponse, SourceHealth


class TestModels:
    """Test shared Pydantic models."""

    def test_error_response(self):
        resp = ErrorResponse(error="Not found")
        assert resp.error == "Not found"

    def test_source_health(self):
        sh = SourceHealth(source="hackernews", status="ok")
        assert sh.source == "hackernews"
        assert sh.last_updated is None

    def test_health_response(self):
        hr = HealthResponse(
            service="pulse",
            status="ok",
            sources=[SourceHealth(source="reddit", status="ok")],
        )
        assert hr.service == "pulse"
        assert len(hr.sources) == 1


class TestHealthRouter:
    """Test health route factory."""

    async def test_health_endpoint(self):
        app = FastAPI()
        app.include_router(create_health_router("pulse", ["hackernews", "reddit"]))
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "pulse"
        assert data["status"] == "ok"
        assert len(data["sources"]) == 2

    async def test_health_no_sources(self):
        app = FastAPI()
        app.include_router(create_health_router("mercury", []))
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["sources"] == []
