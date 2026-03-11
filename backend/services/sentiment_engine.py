"""
Sentiment analysis engine.

Models:
  - VADER  (default): fast, lexicon-based, great for social media text.
  - FinBERT (optional): ProsusAI/finbert — finance-tuned BERT; ~440 MB on first use.

Both models return normalised per-item scores and an aggregated summary.
"""
from __future__ import annotations

import logging
import math
from typing import Any

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from config import config

logger = logging.getLogger(__name__)

# Download VADER lexicon on first use (cached after that)
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

_vader: SentimentIntensityAnalyzer | None = None
_finbert_pipeline: Any = None  # lazy-loaded


# ───────────────────────────── helpers ──────────────────────────────────────

def _get_vader() -> SentimentIntensityAnalyzer:
    global _vader
    if _vader is None:
        _vader = SentimentIntensityAnalyzer()
    return _vader


def _get_finbert():
    global _finbert_pipeline
    if _finbert_pipeline is None:
        try:
            from transformers import pipeline as hf_pipeline

            logger.info("Loading FinBERT model (first time may take a while)...")
            _finbert_pipeline = hf_pipeline(
                "text-classification",
                model="ProsusAI/finbert",
                truncation=True,
                max_length=512,
            )
            logger.info("FinBERT loaded.")
        except Exception as exc:
            logger.error("Failed to load FinBERT: %s — falling back to VADER.", exc)
            _finbert_pipeline = None
    return _finbert_pipeline


def _classify(compound: float) -> str:
    if compound >= config.VADER_POSITIVE_THRESHOLD:
        return "positive"
    if compound <= config.VADER_NEGATIVE_THRESHOLD:
        return "negative"
    return "neutral"


def _overall_label(avg_compound: float) -> str:
    if avg_compound >= config.BULLISH_THRESHOLD:
        return "bullish"
    if avg_compound <= config.BEARISH_THRESHOLD:
        return "bearish"
    return "neutral"


# ───────────────────────────── VADER scoring ────────────────────────────────

def _score_vader(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sia = _get_vader()
    scored = []
    for item in items:
        text = (item.get("title") or "") + " " + (item.get("text") or "")
        scores = sia.polarity_scores(text.strip())
        compound = scores["compound"]

        scored.append(
            {
                **item,
                "sentiment": _classify(compound),
                "score": round(compound, 4),
                "model": "vader",
            }
        )
    return scored


# ───────────────────────────── FinBERT scoring ──────────────────────────────

_FINBERT_LABEL_MAP = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}


def _score_finbert(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pipe = _get_finbert()
    if pipe is None:
        # Graceful fallback to VADER
        logger.warning("FinBERT unavailable; falling back to VADER.")
        results = _score_vader(items)
        for r in results:
            r["model"] = "finbert_fallback_vader"
        return results

    scored = []
    for item in items:
        text = (item.get("title") or "") + " " + (item.get("text") or "")
        text = text.strip()[:1000]  # guard against very long strings pre-tokenization

        try:
            prediction = pipe(text)[0]  # {"label": "positive", "score": 0.97}
            label = prediction["label"].lower()
            confidence = prediction["score"]
            # Map to compound-like float: +1/-1/0 scaled by confidence
            polarity = _FINBERT_LABEL_MAP.get(label, 0.0)
            compound = round(polarity * confidence, 4)
        except Exception as exc:
            logger.warning("FinBERT inference error: %s — using VADER fallback.", exc)
            sia = _get_vader()
            compound = sia.polarity_scores(text)["compound"]
            label = _classify(compound)

        scored.append(
            {
                **item,
                "sentiment": _classify(compound),
                "score": round(compound, 4),
                "model": "finbert",
            }
        )
    return scored


# ───────────────────────────── aggregation ──────────────────────────────────

def _upvote_weight(upvotes: int) -> float:
    """Log-scale weight so highly upvoted posts carry more signal."""
    return math.log(max(upvotes, 1) + 1)


def _aggregate(scored_items: list[dict[str, Any]]) -> dict[str, Any]:
    if not scored_items:
        return {
            "overall": "neutral",
            "score": 0.0,
            "breakdown": {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "total": 0,
                "pct_positive": 0.0,
                "pct_negative": 0.0,
                "pct_neutral": 0.0,
            },
        }

    # Weighted average compound score (Reddit: weighted by upvotes; news: weight 1)
    weighted_sum = 0.0
    total_weight = 0.0
    counts = {"positive": 0, "negative": 0, "neutral": 0}

    for item in scored_items:
        weight = (
            _upvote_weight(item.get("upvotes", 0))
            if item.get("type") == "reddit"
            else 1.0
        )
        weighted_sum += item["score"] * weight
        total_weight += weight
        counts[item["sentiment"]] += 1

    avg_compound = weighted_sum / total_weight if total_weight else 0.0
    total = len(scored_items)

    return {
        "overall": _overall_label(avg_compound),
        "score": round(avg_compound, 4),
        "breakdown": {
            "positive": counts["positive"],
            "negative": counts["negative"],
            "neutral": counts["neutral"],
            "total": total,
            "pct_positive": round(counts["positive"] / total * 100, 1),
            "pct_negative": round(counts["negative"] / total * 100, 1),
            "pct_neutral": round(counts["neutral"] / total * 100, 1),
        },
    }


def _top_sources(scored: list[dict[str, Any]], n: int = 5) -> list[dict[str, Any]]:
    """
    Return the `n` most extreme items from reddit and `n` from news,
    sorted by absolute score descending.
    """
    reddit = [x for x in scored if x.get("type") == "reddit"]
    news = [x for x in scored if x.get("type") == "news"]

    def _key(item: dict) -> float:
        return abs(item["score"])

    top_reddit = sorted(reddit, key=_key, reverse=True)[:n]
    top_news = sorted(news, key=_key, reverse=True)[:n]

    # Merge and strip large internal fields before returning
    output = []
    for item in top_reddit + top_news:
        output.append(
            {
                "type": item.get("type"),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "date": item.get("date", ""),
                "sentiment": item.get("sentiment"),
                "score": item.get("score"),
                "source": item.get("source") or item.get("subreddit") or "",
                "upvotes": item.get("upvotes"),
            }
        )
    return output


# ───────────────────────────── public API ───────────────────────────────────

def analyze(
    items: list[dict[str, Any]],
    model: str = "vader",
) -> dict[str, Any]:
    """
    Score all items with the chosen model and return aggregated results.

    Args:
        items:  Combined list of reddit + news dicts from scrapers.
        model:  "vader" or "finbert"

    Returns:
        {overall, score, breakdown, sources, model}
    """
    if not items:
        agg = _aggregate([])
        return {**agg, "sources": [], "model": model}

    if model == "finbert":
        scored = _score_finbert(items)
    else:
        scored = _score_vader(items)

    agg = _aggregate(scored)
    sources = _top_sources(scored)

    return {**agg, "sources": sources, "model": scored[0].get("model", model)}
