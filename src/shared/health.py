"""Health route factory for Helios services."""

from fastapi import APIRouter

from shared.models import HealthResponse, SourceHealth


def create_health_router(service_name: str, sources: list[str]) -> APIRouter:
    """Create a health check router for a service."""
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            service=service_name,
            status="ok",
            sources=[SourceHealth(source=s, status="ok") for s in sources],
        )

    return router
