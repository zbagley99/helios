"""Mercury service configuration."""

from shared.config import BaseServiceSettings


class MercurySettings(BaseServiceSettings):
    """Settings for the Mercury commodities service."""

    db_name: str = "mercury"
    port: int = 5602
