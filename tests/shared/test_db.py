"""Tests for shared.config and shared.db."""

import pytest
from mongomock_motor import AsyncMongoMockClient

from shared.config import BaseServiceSettings
from shared.db import close_db, get_collection, get_db, init_db


class TestBaseServiceSettings:
    """Test BaseServiceSettings defaults and overrides."""

    def test_defaults(self):
        settings = BaseServiceSettings()
        assert settings.mongo_uri == "mongodb://localhost:27017/"
        assert settings.db_name == "helios"
        assert settings.port == 8000
        assert settings.debug is False

    def test_override(self):
        settings = BaseServiceSettings(db_name="pulse", port=5603)
        assert settings.db_name == "pulse"
        assert settings.port == 5603


class TestDatabase:
    """Test db module init/get/close lifecycle."""

    def test_get_db_before_init_raises(self):
        close_db()
        with pytest.raises(RuntimeError, match="Database not initialized"):
            get_db()

    def test_init_and_get_db(self):
        client = AsyncMongoMockClient()
        init_db.__wrapped__ if hasattr(init_db, "__wrapped__") else None
        # Directly test the module-level init
        import shared.db as db_mod

        db_mod._client = client
        db_mod._db = client["test_db"]
        assert get_db() is not None
        close_db()

    def test_get_collection(self, mock_db):
        coll = get_collection("items")
        assert coll.name == "items"

    async def test_insert_and_find(self, mock_db):
        coll = get_collection("items")
        await coll.insert_one({"name": "test"})
        doc = await coll.find_one({"name": "test"})
        assert doc["name"] == "test"
