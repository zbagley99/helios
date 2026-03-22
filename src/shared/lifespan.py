"""FastAPI lifespan context manager for database and scheduler lifecycle."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from shared.db import close_db, init_db
from shared.scheduler import create_scheduler


def create_lifespan(
    mongo_uri: str,
    db_name: str,
    register_jobs: Callable[[AsyncIOScheduler], None] | None = None,
) -> Callable[[FastAPI], AsyncIterator[None]]:
    """Build a lifespan context manager with db and optional scheduler."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:  # noqa: RUF029
        init_db(mongo_uri, db_name)
        scheduler = create_scheduler()
        if register_jobs is not None:
            register_jobs(scheduler)
        scheduler.start()
        try:
            yield
        finally:
            scheduler.shutdown(wait=False)
            close_db()

    return lifespan
