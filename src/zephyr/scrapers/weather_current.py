"""Current weather scraper via Open-Meteo."""

import logging

import httpx

from shared.scrape import persist_batch
from zephyr.geocode import get_coords
from zephyr.models import WeatherCurrent

logger = logging.getLogger(__name__)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


async def scrape_weather_current() -> list[WeatherCurrent]:
    """Fetch current weather conditions from Open-Meteo."""
    logger.info("scrape started")
    lat, lng, display = await get_coords()
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,wind_speed_10m,wind_direction_10m,uv_index"
        ),
    }
    items: list[WeatherCurrent] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(WEATHER_URL, params=params)
        resp.raise_for_status()
        cur = resp.json()["current"]

        temp_c = cur.get("temperature_2m")
        temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None
        feels_c = cur.get("apparent_temperature")
        feels_f = round(feels_c * 9 / 5 + 32, 1) if feels_c is not None else None
        wind_kmh = cur.get("wind_speed_10m")
        wind_mph = round(wind_kmh * 0.621371, 1) if wind_kmh is not None else None
        precip_mm = cur.get("precipitation")
        precip_in = round(precip_mm * 0.0393701, 2) if precip_mm is not None else None

        items.append(
            WeatherCurrent(
                location=display,
                temperature_c=temp_c,
                temperature_f=temp_f,
                humidity=cur.get("relative_humidity_2m"),
                wind_speed_mph=wind_mph,
                wind_direction=cur.get("wind_direction_10m"),
                uv_index=cur.get("uv_index"),
                feels_like_f=feels_f,
                precipitation_in=precip_in,
            )
        )

    if items:
        await persist_batch("weather_current", [i.model_dump(mode="json") for i in items], "location")
    logger.info("scrape finished — %d items", len(items))
    return items
