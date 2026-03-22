"""Tests for Google Trends scraper."""

import respx
from httpx import Response

from pulse.scrapers.google_trends import GOOGLE_TRENDS_URL, parse_trends_rss, scrape_google_trends

MOCK_RSS = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:ht="https://trends.google.com/trending/rss" version="2.0">
  <channel>
    <title>Trending Searches</title>
    <item>
      <title>Climate Change</title>
      <link>https://trends.google.com/trends/explore?q=Climate+Change</link>
      <ht:approx_traffic>500,000+</ht:approx_traffic>
    </item>
    <item>
      <title>AI Regulation</title>
      <link>https://trends.google.com/trends/explore?q=AI+Regulation</link>
      <ht:approx_traffic>200,000+</ht:approx_traffic>
    </item>
    <item>
      <title>Space Launch</title>
      <link>https://trends.google.com/trends/explore?q=Space+Launch</link>
      <ht:approx_traffic>50,000+</ht:approx_traffic>
    </item>
  </channel>
</rss>
"""

MOCK_RSS_EMPTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:ht="https://trends.google.com/trending/rss" version="2.0">
  <channel>
    <title>Trending Searches</title>
  </channel>
</rss>
"""


class TestParseTrendsRss:
    """Test RSS parsing logic."""

    def test_parse_rss_items(self):
        items = parse_trends_rss(MOCK_RSS)
        assert len(items) == 3
        assert items[0].title == "Climate Change"
        assert items[0].source == "google"
        assert items[0].category == "trending"
        assert items[0].url == "https://trends.google.com/trends/explore?q=Climate+Change"
        assert items[0].score == 500000

    def test_parse_traffic_values(self):
        items = parse_trends_rss(MOCK_RSS)
        assert items[1].score == 200000
        assert items[2].score == 50000

    def test_parse_empty_rss(self):
        items = parse_trends_rss(MOCK_RSS_EMPTY)
        assert len(items) == 0


class TestGoogleTrendsScraper:
    """Test full scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(GOOGLE_TRENDS_URL).mock(return_value=Response(200, text=MOCK_RSS))

        items = await scrape_google_trends()
        assert len(items) == 3

    @respx.mock
    async def test_scrape_empty_feed(self, mock_db):
        respx.get(GOOGLE_TRENDS_URL).mock(return_value=Response(200, text=MOCK_RSS_EMPTY))

        items = await scrape_google_trends()
        assert len(items) == 0
