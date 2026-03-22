"""Mercury FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mercury.config import MercurySettings
from mercury.routes.commodities import router as commodities_router
from mercury.scrapers.yahoo_finance import scrape_yahoo_finance
from shared.db import close_db, init_db
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.indexes import ensure_indexes
from shared.scheduler import create_scheduler, register_job

settings = MercurySettings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage database and scheduler lifecycle."""
    init_db(settings.mongo_uri, settings.db_name)
    await ensure_indexes("commodities", settings.ttl_hours * 3600, ["ticker"])
    scheduler = create_scheduler()
    register_job(scheduler, scrape_yahoo_finance, interval_minutes=5, job_id="mercury_yahoo")
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        close_db()


app = FastAPI(title="Mercury", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)
app.include_router(create_health_router("mercury", ["yahoo_finance"]))
app.include_router(commodities_router)
