"""Pulse data models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TrendItem(BaseModel):
    """A single trending item from any source."""

    title: str
    url: str | None = None
    source: str
    category: str = "general"
    score: float | None = None
    description: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"
