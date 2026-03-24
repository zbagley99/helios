"""Zephyr scraper registry — maps collection names to scraper functions, intervals, and natural keys."""

from zephyr.scrapers.air_quality import scrape_air_quality
from zephyr.scrapers.earthquakes import scrape_earthquakes
from zephyr.scrapers.iss import scrape_iss
from zephyr.scrapers.kp_index import scrape_kp_index
from zephyr.scrapers.space_weather import scrape_space_weather
from zephyr.scrapers.tides import scrape_tides
from zephyr.scrapers.twilight import scrape_twilight
from zephyr.scrapers.weather_current import scrape_weather_current
from zephyr.scrapers.weather_forecast import scrape_weather_forecast
from zephyr.scrapers.wildfires import scrape_wildfires

SCRAPER_REGISTRY: dict[str, dict] = {
    "weather_current": {"func": scrape_weather_current, "interval_minutes": 15},
    "weather_forecast": {"func": scrape_weather_forecast, "interval_minutes": 60},
    "air_quality": {"func": scrape_air_quality, "interval_minutes": 30},
    "earthquakes": {"func": scrape_earthquakes, "interval_minutes": 15},
    "space_weather": {"func": scrape_space_weather, "interval_minutes": 60},
    "kp_index": {"func": scrape_kp_index, "interval_minutes": 30},
    "twilight": {"func": scrape_twilight, "interval_minutes": 720},
    "tides": {"func": scrape_tides, "interval_minutes": 360},
    "wildfires": {"func": scrape_wildfires, "interval_minutes": 30},
    "iss": {"func": scrape_iss, "interval_minutes": 5},
}

NATURAL_KEYS: dict[str, str] = {
    "weather_current": "location",
    "weather_forecast": "date",
    "air_quality": "location",
    "earthquakes": "url",
    "space_weather": "issue_datetime",
    "kp_index": "time_tag",
    "twilight": "date",
    "tides": "time",
    "wildfires": "url",
    "iss": "source",
}
