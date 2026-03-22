"""APScheduler helpers for periodic scraping jobs."""

from collections.abc import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def create_scheduler() -> AsyncIOScheduler:
    """Create an async scheduler instance."""
    return AsyncIOScheduler()


def register_job(scheduler: AsyncIOScheduler, func: Callable, interval_minutes: int, job_id: str) -> None:
    """Register an interval job on the scheduler."""
    scheduler.add_job(func, "interval", minutes=interval_minutes, id=job_id, replace_existing=True)
