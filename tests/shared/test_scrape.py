"""Tests for persist_batch change detection."""

from shared.db import get_collection
from shared.scrape import persist_batch


class TestPersistBatch:
    """Test batch persistence with change detection."""

    async def test_first_batch_all_new(self, mock_db):
        items = [
            {"url": "https://a.com", "title": "A"},
            {"url": "https://b.com", "title": "B"},
        ]
        docs = await persist_batch("test_col", items, "url")
        assert len(docs) == 2
        assert all(d["status"] == "new" for d in docs)
        assert all("batch_id" in d for d in docs)
        assert all("scraped_at" in d for d in docs)

    async def test_second_batch_persisting_new_dropped(self, mock_db):
        # First batch: A, B
        await persist_batch("test_col", [
            {"url": "https://a.com", "title": "A"},
            {"url": "https://b.com", "title": "B"},
        ], "url")

        # Second batch: A (persisting), C (new), B dropped
        docs = await persist_batch("test_col", [
            {"url": "https://a.com", "title": "A updated"},
            {"url": "https://c.com", "title": "C"},
        ], "url")

        status_map = {d["url"]: d["status"] for d in docs}
        assert status_map["https://a.com"] == "persisting"
        assert status_map["https://c.com"] == "new"
        assert status_map["https://b.com"] == "dropped"

    async def test_empty_items_returns_empty(self, mock_db):
        docs = await persist_batch("test_col", [], "url")
        assert docs == []

    async def test_docs_stored_in_collection(self, mock_db):
        await persist_batch("test_col", [{"url": "https://x.com", "title": "X"}], "url")
        coll = get_collection("test_col")
        count = await coll.count_documents({})
        assert count == 1

    async def test_batch_ids_are_unique_across_batches(self, mock_db):
        await persist_batch("test_col", [{"url": "https://a.com", "title": "A"}], "url")
        await persist_batch("test_col", [{"url": "https://a.com", "title": "A"}], "url")
        coll = get_collection("test_col")
        batch_ids = set()
        async for doc in coll.find({}, {"batch_id": 1}):
            batch_ids.add(doc["batch_id"])
        assert len(batch_ids) == 2
