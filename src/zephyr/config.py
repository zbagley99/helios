"""Zephyr service configuration."""

from shared.config import BaseServiceSettings


class ZephyrSettings(BaseServiceSettings):
    """Settings for the Zephyr weather service."""

    db_name: str = "zephyr"
    port: int = 5555
    location_name: str = "Washington"
    tide_station_id: str = "8594900"
