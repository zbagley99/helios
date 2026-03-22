"""Shared response models for all Helios services."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str


class SourceHealth(BaseModel):
    """Health status for a single data source."""

    source: str
    status: str
    last_updated: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    service: str
    status: str
    sources: list[SourceHealth] = []
