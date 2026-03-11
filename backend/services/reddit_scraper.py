"""
Reddit scraper using PRAW.
Searches r/wallstreetbets and r/stocks for posts mentioning the given ticker.
Falls back gracefully if credentials are missing.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import praw
from praw.exceptions import PRAWException

from config import config

logger = logging.getLogger(__name__)

# Subreddits to search (combined multireddit string)
SUBREDDITS = "wallstreetbets+stocks+investing+options"


def _build_reddit_client() -> praw.Reddit | None:
    if not config.reddit_configured:
        logger.warning("Reddit credentials not set — skipping Reddit scraping.")
        return None
    return praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )


def _iso_from_utc(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")


def fetch_reddit_posts(ticker: str) -> list[dict[str, Any]]:
    """
    Search multiple subreddits for posts mentioning `ticker`.
    Returns a list of post dicts with keys:
        type, title, text, url, date, upvotes
    """
    reddit = _build_reddit_client()
    if reddit is None:
        return []

    results: list[dict[str, Any]] = []
    try:
        subreddit = reddit.subreddit(SUBREDDITS)
        # Search for the ticker symbol; sort by new for freshness
        for submission in subreddit.search(
            ticker.upper(),
            sort="new",
            time_filter="week",
            limit=config.REDDIT_POST_LIMIT,
        ):
            # Only include posts where the ticker appears in title or body
            ticker_upper = ticker.upper()
            text_combined = (submission.title + " " + submission.selftext).upper()
            if ticker_upper not in text_combined:
                continue

            results.append(
                {
                    "type": "reddit",
                    "title": submission.title,
                    "text": submission.selftext[:500] if submission.selftext else "",
                    "url": f"https://reddit.com{submission.permalink}",
                    "date": _iso_from_utc(submission.created_utc),
                    "upvotes": max(submission.score, 0),
                    "subreddit": str(submission.subreddit),
                }
            )
    except Exception as exc:
        logger.error("Reddit scraping error for %s: %s", ticker, exc)

    logger.info("Fetched %d Reddit posts for %s", len(results), ticker)
    return results
