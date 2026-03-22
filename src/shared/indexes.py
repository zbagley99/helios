"""MongoDB index helpers for TTL and query optimization."""

import logging

from pymongo import DESCENDING
from pymongo.errors import OperationFailure

from shared.db import get_collection, get_db

logger = logging.getLogger(__name__)


async def ensure_indexes(collection_name: str, ttl_seconds: int, natural_key_fields: list[str]) -> None:
    """Create TTL, batch, and natural-key indexes for a collection."""
    coll = get_collection(collection_name)

    # TTL index on scraped_at (collMod fallback if TTL value changed)
    try:
        await coll.create_index("scraped_at", expireAfterSeconds=ttl_seconds, name="ttl_scraped_at")
    except OperationFailure:
        await get_db().command({
            "collMod": collection_name,
            "index": {"keyPattern": {"scraped_at": 1}, "expireAfterSeconds": ttl_seconds},
        })
        logger.info("updated TTL on %s to %ds", collection_name, ttl_seconds)

    # Descending index on batch_id for latest-batch lookups
    await coll.create_index([("batch_id", DESCENDING)], name="batch_id_desc")

    # Compound index on (batch_id, status) for filtered queries
    await coll.create_index([("batch_id", DESCENDING), ("status", 1)], name="batch_status")

    # Index on natural key fields for change detection lookups
    if natural_key_fields:
        try:
            await coll.create_index([(f, 1) for f in natural_key_fields], name="natural_key")
        except OperationFailure:
            await coll.drop_index("natural_key")
            await coll.create_index([(f, 1) for f in natural_key_fields], name="natural_key")
            logger.info("recreated natural_key index on %s", collection_name)
