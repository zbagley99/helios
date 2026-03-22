"""Base configuration for all Helios services."""

from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    """Shared settings inherited by each microservice."""

    mongo_uri: str = "mongodb://localhost:27017/"
    db_name: str = "helios"
    port: int = 8000
    debug: bool = False

    model_config = {"env_prefix": "", "extra": "ignore"}
