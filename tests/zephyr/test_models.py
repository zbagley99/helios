"""Tests for Zephyr models."""

from datetime import UTC, datetime

import pytest

from zephyr.models import (
    AirQuality,
    Earthquake,
    ISSPosition,
    KpIndex,
    SpaceWeatherAlert,
    Tide,
    Twilight,
    WeatherCurrent,
    WeatherForecast,
    Wildfire,
)


class TestWeatherCurrent:
    """Test WeatherCurrent model."""

    def test_minimal(self):
        item = WeatherCurrent(location="Washington, DC, US")
        assert item.location == "Washington, DC, US"
        assert item.source == "open_meteo"
        assert item.status == "new"
        assert isinstance(item.scraped_at, datetime)

    def test_full(self):
        item = WeatherCurrent(
            location="Washington, DC, US",
            temperature_c=20.0,
            temperature_f=68.0,
            humidity=50.0,
            wind_speed_mph=10.0,
            wind_direction=180.0,
            uv_index=5.0,
            feels_like_f=66.0,
            precipitation_in=0.0,
        )
        assert item.temperature_f == pytest.approx(68.0)

    def test_serialization(self):
        item = WeatherCurrent(location="Test")
        data = item.model_dump(mode="json")
        assert "scraped_at" in data
        assert "batch_id" in data


class TestWeatherForecast:
    """Test WeatherForecast model."""

    def test_minimal(self):
        item = WeatherForecast(location="Test", date="2026-03-23")
        assert item.date == "2026-03-23"
        assert item.source == "open_meteo"

    def test_full(self):
        item = WeatherForecast(
            location="Test",
            date="2026-03-23",
            temp_high_f=70.0,
            temp_low_f=50.0,
            precipitation_prob=30.0,
            wind_speed_mph=15.0,
            weathercode=3,
        )
        assert item.temp_high_f == pytest.approx(70.0)


class TestAirQuality:
    """Test AirQuality model."""

    def test_minimal(self):
        item = AirQuality(location="Test")
        assert item.source == "open_meteo"

    def test_full(self):
        item = AirQuality(location="Test", aqi=42, pm25=8.3, pm10=15.2)
        assert item.aqi == 42


class TestEarthquake:
    """Test Earthquake model."""

    def test_minimal(self):
        item = Earthquake(
            title="M 3.5",
            magnitude=3.5,
            location="10km NW of Test",
            latitude=45.5,
            longitude=-122.6,
            depth_km=10.0,
            time=datetime(2026, 3, 23, tzinfo=UTC),
        )
        assert item.source == "usgs"
        assert item.magnitude == pytest.approx(3.5)

    def test_serialization(self):
        item = Earthquake(
            title="M 3.5",
            magnitude=3.5,
            location="Test",
            latitude=0.0,
            longitude=0.0,
            depth_km=0.0,
            time=datetime(2026, 1, 1, tzinfo=UTC),
        )
        data = item.model_dump(mode="json")
        assert "time" in data


class TestSpaceWeatherAlert:
    """Test SpaceWeatherAlert model."""

    def test_minimal(self):
        item = SpaceWeatherAlert(issue_datetime="2026-03-23 12:00:00.000", message="Alert")
        assert item.source == "swpc"

    def test_serialization(self):
        item = SpaceWeatherAlert(issue_datetime="2026-03-23", message="Test")
        data = item.model_dump(mode="json")
        assert "issue_datetime" in data


class TestKpIndex:
    """Test KpIndex model."""

    def test_minimal(self):
        item = KpIndex(time_tag="2026-03-23 00:00:00", kp=2.33)
        assert item.source == "swpc"
        assert item.kp == pytest.approx(2.33)


class TestTwilight:
    """Test Twilight model."""

    def test_minimal(self):
        item = Twilight(
            location="Test",
            date="2026-03-23",
            sunrise="06:30",
            sunset="18:45",
            civil_twilight_begin="06:00",
            civil_twilight_end="19:15",
        )
        assert item.source == "sunrise_sunset"


class TestTide:
    """Test Tide model."""

    def test_minimal(self):
        item = Tide(station="8594900", time="2026-03-23 06:00", prediction_ft=3.5)
        assert item.source == "noaa"


class TestWildfire:
    """Test Wildfire model."""

    def test_minimal(self):
        item = Wildfire(title="Test Fire")
        assert item.source == "inciweb"
        assert item.location is None

    def test_full(self):
        item = Wildfire(
            title="Test Fire",
            location="Oregon",
            url="https://inciweb.wildfire.gov/incident/123",
            published="Mon, 23 Mar 2026 00:00:00 GMT",
            description="A fire",
        )
        assert item.url is not None


class TestISSPosition:
    """Test ISSPosition model."""

    def test_minimal(self):
        item = ISSPosition(latitude=45.5, longitude=-122.6)
        assert item.source == "open_notify"
        assert item.crew == []

    def test_full(self):
        item = ISSPosition(latitude=45.5, longitude=-122.6, crew=["Alice", "Bob"])
        assert len(item.crew) == 2
