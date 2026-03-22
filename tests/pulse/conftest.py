"""Pulse-specific test fixtures."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from pulse.routes.trends import router as trends_router
from shared.health import create_health_router


@pytest.fixture
def pulse_app():
    """Create a Pulse FastAPI app without lifespan for testing."""
    app = FastAPI()
    app.include_router(create_health_router("pulse", ["hackernews", "reddit"]))
    app.include_router(trends_router)
    return app


@pytest.fixture
async def pulse_client(pulse_app, mock_db):
    """Async HTTP client for Pulse routes."""
    async with AsyncClient(transport=ASGITransport(app=pulse_app), base_url="http://test") as client:
        yield client
