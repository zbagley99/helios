"""Batch persistence with change detection."""

from datetime import UTC, datetime

from shared.db import get_collection


async def persist_batch(collection_name: str, items: list[dict], natural_key: str) -> list[dict]:
    """Persist a scrape batch with change-detection status."""
    if not items:
        return []

    now = datetime.now(tz=UTC)
    batch_id = now.isoformat()
    coll = get_collection(collection_name)

    # Find the previous batch's natural keys (most recent batch where status != "dropped")
    prev_cursor = coll.find(
        {"status": {"$ne": "dropped"}},
        {"batch_id": 1},
    ).sort("batch_id", -1).limit(1)
    prev_doc = await prev_cursor.to_list(length=1)

    prev_keys: set[str] = set()
    prev_batch_id: str | None = None
    if prev_doc:
        prev_batch_id = prev_doc[0]["batch_id"]
        key_cursor = coll.find(
            {"batch_id": prev_batch_id, "status": {"$ne": "dropped"}},
            {natural_key: 1},
        )
        prev_keys = {doc[natural_key] async for doc in key_cursor}

    # Classify current items
    current_keys: set[str] = set()
    for item in items:
        item["scraped_at"] = now
        item["batch_id"] = batch_id
        key_val = item.get(natural_key, "")
        current_keys.add(key_val)
        item["status"] = "persisting" if key_val in prev_keys else "new"

    # Create dropped docs for keys absent from current batch
    dropped_keys = prev_keys - current_keys
    dropped_docs: list[dict] = []
    if dropped_keys and prev_batch_id:
        async for doc in coll.find({"batch_id": prev_batch_id, natural_key: {"$in": list(dropped_keys)}}):
            doc.pop("_id", None)
            doc["scraped_at"] = now
            doc["batch_id"] = batch_id
            doc["status"] = "dropped"
            dropped_docs.append(doc)

    all_docs = items + dropped_docs
    if all_docs:
        await coll.insert_many(all_docs)

    return all_docs
