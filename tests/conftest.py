"""Shared test fixtures for all Helios services."""

from unittest.mock import patch

import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
def mock_db():
    """Provide a mongomock-motor client and patch shared.db globals."""
    client = AsyncMongoMockClient()
    with (
        patch("shared.db._client", client),
        patch("shared.db._db", client["test_db"]),
    ):
        yield client["test_db"]
