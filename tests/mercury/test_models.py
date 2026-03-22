"""Tests for Mercury models."""

from datetime import datetime

from mercury.models import CommodityItem


class TestCommodityItem:
    """Test CommodityItem model."""

    def test_minimal(self):
        item = CommodityItem(ticker="GC=F", name="Gold", category="metals")
        assert item.ticker == "GC=F"
        assert item.name == "Gold"
        assert item.category == "metals"
        assert item.price is None
        assert item.currency == "USD"
        assert isinstance(item.timestamp, datetime)
        assert isinstance(item.scraped_at, datetime)
        assert not item.batch_id
        assert item.status == "new"

    def test_full(self):
        item = CommodityItem(
            ticker="CL=F",
            name="Crude Oil WTI",
            category="energy",
            price=75.50,
            change=-1.25,
            pct_change=-1.63,
            currency="USD",
        )
        assert item.price == 75.50  # noqa: RUF069
        assert item.change == -1.25  # noqa: RUF069
        assert item.pct_change == -1.63  # noqa: RUF069

    def test_serialization(self):
        item = CommodityItem(ticker="GC=F", name="Gold", category="metals", price=2000.0)
        data = item.model_dump(mode="json")
        assert "ticker" in data
        assert "timestamp" in data
        assert "scraped_at" in data
        assert "batch_id" in data
        assert "status" in data
