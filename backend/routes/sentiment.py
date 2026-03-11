"""
Sentiment route — orchestrates scraping + analysis.
GET /api/sentiment/<ticker>?model=vader|finbert
"""
from __future__ import annotations

import logging
import re

from flask import Blueprint, jsonify, request

from app import cache
from config import config
from services.news_scraper import fetch_news
from services.reddit_scraper import fetch_reddit_posts
from services.sentiment_engine import analyze

logger = logging.getLogger(__name__)
sentiment_bp = Blueprint("sentiment", __name__)

_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")


@sentiment_bp.get("/sentiment/<string:ticker>")
def get_sentiment(ticker: str):
    ticker = ticker.upper().strip()

    if not _TICKER_RE.match(ticker):
        return jsonify({"error": "Invalid ticker symbol."}), 400

    model = request.args.get("model", "vader").lower()
    if model not in ("vader", "finbert"):
        model = "vader"

    cache_key = f"sentiment:{ticker}:{model}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    # Fetch data from both sources concurrently using threads
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        fut_reddit = executor.submit(fetch_reddit_posts, ticker)
        fut_news = executor.submit(fetch_news, ticker)
        reddit_posts = fut_reddit.result()
        news_articles = fut_news.result()

    all_items = reddit_posts + news_articles

    if not all_items:
        return (
            jsonify(
                {
                    "error": (
                        f"No data found for '{ticker}'. "
                        "Check your Reddit/News API credentials and try again."
                    )
                }
            ),
            404,
        )

    result = analyze(all_items, model=model)
    result["ticker"] = ticker
    result["reddit_count"] = len(reddit_posts)
    result["news_count"] = len(news_articles)

    cache.set(cache_key, result, timeout=config.SENTIMENT_CACHE_TIMEOUT)
    return jsonify(result)
