"""Tests for Yahoo Finance scraper."""

from unittest.mock import MagicMock, patch

from mercury.scrapers.yahoo_finance import _fetch_ticker_data, scrape_yahoo_finance


class TestFetchTickerData:
    """Test individual ticker fetching."""

    @patch("mercury.scrapers.yahoo_finance.yf.Ticker")
    def test_fetch_success(self, mock_ticker_cls):
        mock_info = MagicMock()
        mock_info.last_price = 2000.0
        mock_info.previous_close = 1990.0
        mock_info.currency = "USD"
        mock_ticker_cls.return_value.fast_info = mock_info

        result = _fetch_ticker_data("GC=F")
        assert result is not None
        assert result["price"] == 2000
        assert result["change"] == 10
        assert result["currency"] == "USD"

    @patch("mercury.scrapers.yahoo_finance.yf.Ticker")
    def test_fetch_no_price(self, mock_ticker_cls):
        mock_info = MagicMock()
        mock_info.last_price = None
        mock_ticker_cls.return_value.fast_info = mock_info

        result = _fetch_ticker_data("GC=F")
        assert result is None

    @patch("mercury.scrapers.yahoo_finance.yf.Ticker")
    def test_fetch_exception(self, mock_ticker_cls):
        mock_ticker_cls.side_effect = Exception("Network error")
        result = _fetch_ticker_data("GC=F")
        assert result is None


class TestScrapeYahooFinance:
    """Test full scraper with mocked yfinance."""

    @patch("mercury.scrapers.yahoo_finance._fetch_ticker_data")
    async def test_scrape_persists_data(self, mock_fetch, mock_db):
        mock_fetch.return_value = {
            "price": 2000.0,
            "change": 10.0,
            "pct_change": 0.5,
            "currency": "USD",
        }

        items = await scrape_yahoo_finance()
        assert len(items) > 0
        assert all(item.price == 2000.0 for item in items)  # noqa: RUF069

        from shared.db import get_collection

        coll = get_collection("commodities")
        count = await coll.count_documents({})
        assert count == len(items)

    @patch("mercury.scrapers.yahoo_finance._fetch_ticker_data")
    async def test_scrape_skips_failures(self, mock_fetch, mock_db):
        mock_fetch.return_value = None
        items = await scrape_yahoo_finance()
        assert len(items) == 0
