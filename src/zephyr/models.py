"""Zephyr data models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class WeatherCurrent(BaseModel):
    """Current weather conditions for a location."""

    location: str
    temperature_c: float | None = None
    temperature_f: float | None = None
    humidity: float | None = None
    wind_speed_mph: float | None = None
    wind_direction: float | None = None
    uv_index: float | None = None
    feels_like_f: float | None = None
    precipitation_in: float | None = None
    source: str = "open_meteo"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class WeatherForecast(BaseModel):
    """Daily weather forecast entry."""

    location: str
    date: str
    temp_high_f: float | None = None
    temp_low_f: float | None = None
    precipitation_prob: float | None = None
    wind_speed_mph: float | None = None
    weathercode: int | None = None
    source: str = "open_meteo"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class AirQuality(BaseModel):
    """Air quality data for a location."""

    location: str
    aqi: int | None = None
    pm25: float | None = None
    pm10: float | None = None
    source: str = "open_meteo"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class Earthquake(BaseModel):
    """A single earthquake event."""

    title: str
    magnitude: float
    location: str
    latitude: float
    longitude: float
    depth_km: float
    time: datetime
    url: str | None = None
    source: str = "usgs"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class SpaceWeatherAlert(BaseModel):
    """A space weather alert from NOAA SWPC."""

    issue_datetime: str
    message: str
    serial_number: str | None = None
    source: str = "swpc"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class KpIndex(BaseModel):
    """A Kp index forecast entry."""

    time_tag: str
    kp: float
    observed: str | None = None
    source: str = "swpc"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class Twilight(BaseModel):
    """Sunrise, sunset, and twilight times."""

    location: str
    date: str
    sunrise: str
    sunset: str
    civil_twilight_begin: str
    civil_twilight_end: str
    day_length: str | None = None
    source: str = "sunrise_sunset"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class Tide(BaseModel):
    """A single tidal prediction entry."""

    station: str
    time: str
    prediction_ft: float
    source: str = "noaa"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class Wildfire(BaseModel):
    """An active wildfire incident."""

    title: str
    location: str | None = None
    url: str | None = None
    published: str | None = None
    description: str | None = None
    source: str = "inciweb"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"


class ISSPosition(BaseModel):
    """International Space Station position and crew."""

    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    crew: list[str] = Field(default_factory=list)
    source: str = "open_notify"
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: str = ""
    status: str = "new"
