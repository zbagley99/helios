"""Mercury-specific test fixtures."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from mercury.routes.commodities import router as commodities_router
from shared.health import create_health_router


@pytest.fixture
def mercury_app():
    """Create a Mercury FastAPI app without lifespan for testing."""
    app = FastAPI()
    app.include_router(create_health_router("mercury", ["yahoo_finance"]))
    app.include_router(commodities_router)
    return app


@pytest.fixture
async def mercury_client(mercury_app, mock_db):
    """Async HTTP client for Mercury routes."""
    async with AsyncClient(transport=ASGITransport(app=mercury_app), base_url="http://test") as client:
        yield client
