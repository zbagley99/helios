"""Tests for Pulse models."""

from datetime import datetime

from pulse.models import TrendItem


class TestTrendItem:
    """Test TrendItem model."""

    def test_minimal(self):
        item = TrendItem(title="Test", source="hackernews")
        assert item.title == "Test"
        assert item.source == "hackernews"
        assert item.category == "general"
        assert item.url is None
        assert item.score is None
        assert isinstance(item.timestamp, datetime)

    def test_full(self):
        item = TrendItem(
            title="Big Story",
            url="https://example.com",
            source="reddit",
            category="tech",
            score=42.0,
            description="A big story",
        )
        assert item.url == "https://example.com"
        assert item.score == 42
        assert item.description == "A big story"

    def test_serialization(self):
        item = TrendItem(title="Test", source="hackernews")
        data = item.model_dump(mode="json")
        assert "title" in data
        assert "timestamp" in data
