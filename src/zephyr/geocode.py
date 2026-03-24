"""Geocode city names via the Open-Meteo geocoding API."""

import logging

import httpx

from zephyr.config import ZephyrSettings

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def geocode(city: str) -> tuple[float, float, str]:
    """
    Resolve a city name to (latitude, longitude, display_name).

    Uses the free Open-Meteo geocoding API (no key required).
    Returns the top result by population.

    Raises:
        ValueError: If no results are found for the given city name.

    """
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=2),
        timeout=10,
    ) as client:
        resp = await client.get(GEOCODE_URL, params={"name": city, "count": 1, "language": "en", "format": "json"})
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results")
    if not results:
        msg = f"No geocoding results for city: {city!r}"
        raise ValueError(msg)

    hit = results[0]
    lat = hit["latitude"]
    lon = hit["longitude"]
    name = hit.get("name", city)
    admin = hit.get("admin1", "")
    country = hit.get("country_code", "")
    display = f"{name}, {admin}" if admin else name
    if country:
        display = f"{display}, {country}"

    logger.info("Geocoded %r → %s (%.4f, %.4f)", city, display, lat, lon)
    return lat, lon, display


# ---------------------------------------------------------------------------
# Cached coordinates for scrapers
# ---------------------------------------------------------------------------

_coords: tuple[float, float, str] | None = None


async def get_coords() -> tuple[float, float, str]:
    """Return cached (lat, lon, display_name) for the configured location."""
    global _coords  # noqa: PLW0603
    if _coords is None:
        _coords = await geocode(ZephyrSettings().location_name)
    return _coords
