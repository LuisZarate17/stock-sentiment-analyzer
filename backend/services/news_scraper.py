"""
News scraper.
Primary source:  Google News RSS via feedparser (no key required)
Secondary source: NewsAPI (used when NEWSAPI_KEY is set in .env)
"""
from __future__ import annotations

import logging
import time
from typing import Any
from urllib.parse import quote_plus

import feedparser
import requests

from config import config

logger = logging.getLogger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/everything"
GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en-US&gl=US&ceid=US:en"
)


def _fetch_rss(ticker: str) -> list[dict[str, Any]]:
    query = quote_plus(f"{ticker} stock")
    url = GOOGLE_NEWS_RSS.format(query=query)
    try:
        feed = feedparser.parse(url)
    except Exception as exc:  # feedparser rarely raises, but guard anyway
        logger.error("feedparser error: %s", exc)
        return []

    results: list[dict[str, Any]] = []
    for entry in feed.entries[: config.NEWS_ARTICLE_LIMIT]:
        published = ""
        if hasattr(entry, "published"):
            # Convert time tuple to ISO string
            try:
                t = entry.published_parsed
                published = (
                    f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
                    if t
                    else ""
                )
            except Exception:
                published = ""

        results.append(
            {
                "type": "news",
                "title": entry.get("title", ""),
                "text": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "date": published,
                "source": entry.get("source", {}).get("title", "Google News"),
            }
        )

    # Small polite delay to avoid hammering Google RSS
    time.sleep(0.5)
    logger.info("Fetched %d RSS articles for %s", len(results), ticker)
    return results


def _fetch_newsapi(ticker: str) -> list[dict[str, Any]]:
    if not config.newsapi_configured:
        return []

    params = {
        "q": f"{ticker} stock",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": config.NEWS_ARTICLE_LIMIT,
        "apiKey": config.NEWSAPI_KEY,
    }
    try:
        resp = requests.get(NEWSAPI_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error("NewsAPI request failed: %s", exc)
        return []

    results: list[dict[str, Any]] = []
    for article in data.get("articles", []):
        published = (article.get("publishedAt") or "")[:10]  # keep YYYY-MM-DD
        results.append(
            {
                "type": "news",
                "title": article.get("title") or "",
                "text": article.get("description") or "",
                "url": article.get("url") or "",
                "date": published,
                "source": (article.get("source") or {}).get("name", "NewsAPI"),
            }
        )

    logger.info("Fetched %d NewsAPI articles for %s", len(results), ticker)
    return results


def fetch_news(ticker: str) -> list[dict[str, Any]]:
    """
    Combine RSS and NewsAPI results, deduplicated by title.
    """
    rss_articles = _fetch_rss(ticker)
    newsapi_articles = _fetch_newsapi(ticker)

    # Deduplicate by normalised title
    seen: set[str] = set()
    combined: list[dict[str, Any]] = []
    for article in rss_articles + newsapi_articles:
        key = article["title"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            combined.append(article)

    return combined
