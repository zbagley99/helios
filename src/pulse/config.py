"""Pulse service configuration."""

from shared.config import BaseServiceSettings


class PulseSettings(BaseServiceSettings):
    """Settings for the Pulse trends service."""

    db_name: str = "pulse"
    port: int = 5603
