"""APScheduler helpers for periodic scraping jobs."""

from collections.abc import Callable
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def create_scheduler() -> AsyncIOScheduler:
    """Create an async scheduler instance."""
    return AsyncIOScheduler()


def register_job(
    scheduler: AsyncIOScheduler,
    func: Callable,
    interval_minutes: int,
    job_id: str,
    next_run_time: datetime | None = None,
) -> None:
    """Register an interval job on the scheduler."""
    kwargs: dict = {
        "minutes": interval_minutes,
        "id": job_id,
        "replace_existing": True,
    }
    if next_run_time is not None:
        kwargs["next_run_time"] = next_run_time
    scheduler.add_job(func, "interval", **kwargs)
