"""Tests for news RSS scraper."""

import respx
from httpx import Response

from pulse.scrapers.news_rss import RSS_FEEDS, parse_rss, scrape_news_rss

MOCK_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Breaking News</title>
      <link>https://example.com/story1</link>
      <description>Something happened</description>
    </item>
    <item>
      <title>Another Story</title>
      <link>https://example.com/story2</link>
    </item>
  </channel>
</rss>"""


class TestParseRss:
    """Test RSS XML parsing."""

    def test_parse_items(self):
        items = parse_rss(MOCK_RSS, "ap")
        assert len(items) == 2
        assert items[0].title == "Breaking News"
        assert items[0].url == "https://example.com/story1"
        assert items[0].source == "news"
        assert items[0].category == "ap"

    def test_parse_no_description(self):
        items = parse_rss(MOCK_RSS, "bbc")
        assert items[1].description is None


class TestNewsRssScraper:
    """Test full RSS scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_all_feeds(self, mock_db):
        for url in RSS_FEEDS.values():
            respx.get(url).mock(return_value=Response(200, text=MOCK_RSS))

        items = await scrape_news_rss()
        assert len(items) == 8  # 2 items * 4 feeds

    @respx.mock
    async def test_scrape_handles_feed_error(self, mock_db):
        urls = list(RSS_FEEDS.values())
        respx.get(urls[0]).mock(return_value=Response(200, text=MOCK_RSS))
        for url in urls[1:]:
            respx.get(url).mock(return_value=Response(500))

        items = await scrape_news_rss()
        assert len(items) == 2  # Only first feed succeeded
