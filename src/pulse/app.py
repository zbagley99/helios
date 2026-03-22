"""Pulse FastAPI application."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pulse.config import PulseSettings
from pulse.routes.trends import router as trends_router
from pulse.scrapers import SCRAPER_REGISTRY
from shared.db import close_db, init_db
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.indexes import ensure_indexes
from shared.scheduler import create_scheduler, register_job

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

settings = PulseSettings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage database and scheduler lifecycle."""
    init_db(settings.mongo_uri, settings.db_name)
    ttl_seconds = settings.ttl_hours * 3600
    for name in SCRAPER_REGISTRY:
        await ensure_indexes(name, ttl_seconds, ["url"])
    scheduler = create_scheduler()
    for name, entry in SCRAPER_REGISTRY.items():
        register_job(scheduler, entry["func"], entry["interval_minutes"], f"pulse_{name}")
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        close_db()


app = FastAPI(title="Pulse", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)
app.include_router(create_health_router("pulse", list(SCRAPER_REGISTRY.keys())))
app.include_router(trends_router)
