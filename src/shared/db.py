"""Async MongoDB client via Motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def init_db(mongo_uri: str, db_name: str) -> None:
    """Initialize the Motor client and select the database."""
    global _client, _db  # noqa: PLW0603
    _client = AsyncIOMotorClient(mongo_uri)
    _db = _client[db_name]


def close_db() -> None:
    """Close the Motor client connection."""
    global _client, _db  # noqa: PLW0603
    if _client is not None:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    """Return the current database instance."""
    if _db is None:
        msg = "Database not initialized. Call init_db() first."
        raise RuntimeError(msg)
    return _db


def get_collection(name: str) -> AsyncIOMotorCollection:
    """Return a collection from the current database."""
    return get_db()[name]
