"""Mercury data models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class CommodityItem(BaseModel):
    """A single commodity/market data point."""

    ticker: str
    name: str
    category: str
    price: float | None = None
    change: float | None = None
    pct_change: float | None = None
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.now)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"
