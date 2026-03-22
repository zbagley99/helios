"""Tests for Reddit scraper."""

import respx
from httpx import Response

from pulse.scrapers.reddit import REDDIT_URL, scrape_reddit

MOCK_REDDIT_RESPONSE = {
    "data": {
        "children": [
            {
                "data": {
                    "title": "Cool post",
                    "permalink": "/r/popular/comments/abc/cool_post/",
                    "subreddit": "popular",
                    "score": 1234,
                    "selftext": "Some text",
                }
            },
            {
                "data": {
                    "title": "Another post",
                    "permalink": "/r/news/comments/def/another_post/",
                    "subreddit": "news",
                    "score": 567,
                    "selftext": "",
                }
            },
        ]
    }
}


class TestRedditScraper:
    """Test Reddit scraper with mocked HTTP."""

    @respx.mock
    async def test_scrape_returns_items(self, mock_db):
        respx.get(REDDIT_URL).mock(return_value=Response(200, json=MOCK_REDDIT_RESPONSE))

        items = await scrape_reddit()
        assert len(items) == 2
        assert items[0].title == "Cool post"
        assert items[0].source == "reddit"
        assert items[0].score == 1234

    @respx.mock
    async def test_scrape_empty_description(self, mock_db):
        respx.get(REDDIT_URL).mock(return_value=Response(200, json=MOCK_REDDIT_RESPONSE))

        items = await scrape_reddit()
        assert items[1].description is None

    @respx.mock
    async def test_scrape_persists_to_db(self, mock_db):
        respx.get(REDDIT_URL).mock(return_value=Response(200, json=MOCK_REDDIT_RESPONSE))

        await scrape_reddit()
        from shared.db import get_collection

        coll = get_collection("reddit")
        count = await coll.count_documents({})
        assert count == 2
