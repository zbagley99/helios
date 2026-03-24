"""Zephyr FastAPI application."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.db import close_db, init_db
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.indexes import ensure_indexes
from shared.scheduler import create_scheduler, register_job
from shared.scrape import get_next_run_time
from zephyr.config import ZephyrSettings
from zephyr.routes.earthquakes import router as earthquakes_router
from zephyr.routes.iss import router as iss_router
from zephyr.routes.space import router as space_router
from zephyr.routes.tides import router as tides_router
from zephyr.routes.twilight import router as twilight_router
from zephyr.routes.weather import router as weather_router
from zephyr.routes.wildfires import router as wildfires_router
from zephyr.scrapers import NATURAL_KEYS, SCRAPER_REGISTRY

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

settings = ZephyrSettings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage database and scheduler lifecycle."""
    init_db(settings.mongo_uri, settings.db_name)
    ttl_seconds = settings.ttl_hours * 3600
    for name in SCRAPER_REGISTRY:
        await ensure_indexes(name, ttl_seconds, [NATURAL_KEYS[name]])
    scheduler = create_scheduler()
    for name, entry in SCRAPER_REGISTRY.items():
        nrt = await get_next_run_time(name, entry["interval_minutes"])
        register_job(scheduler, entry["func"], entry["interval_minutes"], f"zephyr_{name}", next_run_time=nrt)
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        close_db()


app = FastAPI(title="Zephyr", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)
app.include_router(create_health_router("zephyr", list(SCRAPER_REGISTRY.keys())))
app.include_router(weather_router)
app.include_router(earthquakes_router)
app.include_router(space_router)
app.include_router(twilight_router)
app.include_router(tides_router)
app.include_router(wildfires_router)
app.include_router(iss_router)
