"""Tests for Google Trends scraper."""

import respx
from httpx import Response

from pulse.scrapers.google_trends import GOOGLE_TRENDS_URL, parse_trends_page, scrape_google_trends

MOCK_HTML_WITH_CLASSES = """
<html>
<body>
<div class="trending-item">Climate Change</div>
<div class="trending-item">AI Regulation</div>
<div class="trending-item">Space Launch</div>
</body>
</html>
"""

MOCK_HTML_EMPTY = """
<html><body><div>Nothing here</div></body></html>
"""


class TestParseTrendsPage:
    """Test HTML parsing logic."""

    def test_parse_with_classes(self):
        items = parse_trends_page(MOCK_HTML_WITH_CLASSES)
        assert len(items) == 3
        assert items[0].title == "Climate Change"
        assert items[0].source == "google"

    def test_parse_empty_page(self):
        items = parse_trends_page(MOCK_HTML_EMPTY)
        assert len(items) == 0


class TestGoogleTrendsScraper:
    """Test full scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(GOOGLE_TRENDS_URL).mock(return_value=Response(200, text=MOCK_HTML_WITH_CLASSES))

        items = await scrape_google_trends()
        assert len(items) == 3

    @respx.mock
    async def test_scrape_empty_page(self, mock_db):
        respx.get(GOOGLE_TRENDS_URL).mock(return_value=Response(200, text=MOCK_HTML_EMPTY))

        items = await scrape_google_trends()
        assert len(items) == 0
