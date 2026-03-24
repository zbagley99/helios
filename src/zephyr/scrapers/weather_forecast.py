"""Daily weather forecast scraper via Open-Meteo."""

import logging

import httpx

from shared.scrape import persist_batch
from zephyr.geocode import get_coords
from zephyr.models import WeatherForecast

logger = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def scrape_weather_forecast() -> list[WeatherForecast]:
    """Fetch daily weather forecast from Open-Meteo."""
    logger.info("scrape started")
    lat, lng, display = await get_coords()
    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": (
            "temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
            "wind_speed_10m_max,weathercode"
        ),
        "timezone": "auto",
    }
    items: list[WeatherForecast] = []
    transport = httpx.AsyncHTTPTransport(retries=2)
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "Helios/0.1"}, transport=transport
    ) as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        daily = resp.json()["daily"]

        dates = daily["time"]
        highs_c = daily["temperature_2m_max"]
        lows_c = daily["temperature_2m_min"]
        precip_probs = daily["precipitation_probability_max"]
        winds_kmh = daily["wind_speed_10m_max"]
        codes = daily["weathercode"]

        for i, date in enumerate(dates):
            high_c = highs_c[i]
            low_c = lows_c[i]
            wind_kmh = winds_kmh[i]
            items.append(
                WeatherForecast(
                    location=display,
                    date=date,
                    temp_high_f=round(high_c * 9 / 5 + 32, 1) if high_c is not None else None,
                    temp_low_f=round(low_c * 9 / 5 + 32, 1) if low_c is not None else None,
                    precipitation_prob=precip_probs[i],
                    wind_speed_mph=round(wind_kmh * 0.621371, 1) if wind_kmh is not None else None,
                    weathercode=codes[i],
                )
            )

    if items:
        await persist_batch("weather_forecast", [i.model_dump(mode="json") for i in items], "date")
    logger.info("scrape finished — %d items", len(items))
    return items
