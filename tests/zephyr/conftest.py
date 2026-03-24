"""Zephyr-specific test fixtures."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from shared.health import create_health_router
from zephyr.routes.earthquakes import router as earthquakes_router
from zephyr.routes.iss import router as iss_router
from zephyr.routes.space import router as space_router
from zephyr.routes.tides import router as tides_router
from zephyr.routes.twilight import router as twilight_router
from zephyr.routes.weather import router as weather_router
from zephyr.routes.wildfires import router as wildfires_router


@pytest.fixture
def zephyr_app():
    """Create a Zephyr FastAPI app without lifespan for testing."""
    app = FastAPI()
    app.include_router(create_health_router("zephyr", ["weather_current", "earthquakes"]))
    app.include_router(weather_router)
    app.include_router(earthquakes_router)
    app.include_router(space_router)
    app.include_router(twilight_router)
    app.include_router(tides_router)
    app.include_router(wildfires_router)
    app.include_router(iss_router)
    return app


@pytest.fixture
async def zephyr_client(zephyr_app, mock_db):
    """Async HTTP client for Zephyr routes."""
    async with AsyncClient(transport=ASGITransport(app=zephyr_app), base_url="http://test") as client:
        yield client
