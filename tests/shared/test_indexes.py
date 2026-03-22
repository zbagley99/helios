"""Tests for index creation helper."""

from shared.db import get_collection
from shared.indexes import ensure_indexes


class TestEnsureIndexes:
    """Test MongoDB index creation."""

    async def test_creates_indexes(self, mock_db):
        await ensure_indexes("test_col", 172800, ["url"])
        coll = get_collection("test_col")
        indexes = await coll.index_information()
        assert "ttl_scraped_at" in indexes
        assert "batch_id_desc" in indexes
        assert "batch_status" in indexes
        assert "natural_key" in indexes

    async def test_ttl_index_has_expire(self, mock_db):
        await ensure_indexes("test_col", 3600, ["url"])
        coll = get_collection("test_col")
        indexes = await coll.index_information()
        assert indexes["ttl_scraped_at"]["expireAfterSeconds"] == 3600

    async def test_idempotent(self, mock_db):
        await ensure_indexes("test_col", 3600, ["url"])
        await ensure_indexes("test_col", 3600, ["url"])
        coll = get_collection("test_col")
        indexes = await coll.index_information()
        assert "ttl_scraped_at" in indexes
