"""Pulse scraper registry — maps source names to scraper functions and intervals."""

from pulse.scrapers.google_trends import scrape_google_trends
from pulse.scrapers.hackernews import scrape_hackernews
from pulse.scrapers.mastodon import scrape_mastodon
from pulse.scrapers.news_rss import scrape_news_rss
from pulse.scrapers.reddit import scrape_reddit
from pulse.scrapers.wikipedia import scrape_wikipedia

SCRAPER_REGISTRY: dict[str, dict] = {
    "hackernews": {"func": scrape_hackernews, "interval_minutes": 60},
    "reddit": {"func": scrape_reddit, "interval_minutes": 30},
    "news": {"func": scrape_news_rss, "interval_minutes": 30},
    "wikipedia": {"func": scrape_wikipedia, "interval_minutes": 360},
    "mastodon": {"func": scrape_mastodon, "interval_minutes": 60},
    "google": {"func": scrape_google_trends, "interval_minutes": 120},
}
