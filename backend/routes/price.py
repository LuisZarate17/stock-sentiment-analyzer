"""
Price route — returns OHLCV data for Plotly candlestick chart.
GET /api/price/<ticker>?period=1mo&interval=1d
"""
from __future__ import annotations

import logging
import re

from flask import Blueprint, jsonify, request

from extensions import cache
from config import config
from services.price_fetcher import fetch_price_data

logger = logging.getLogger(__name__)
price_bp = Blueprint("price", __name__)

_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")


@price_bp.get("/price/<string:ticker>")
def get_price(ticker: str):
    ticker = ticker.upper().strip()

    if not _TICKER_RE.match(ticker):
        return jsonify({"error": "Invalid ticker symbol."}), 400

    period = request.args.get("period", "1mo")
    interval = request.args.get("interval", "1d")

    cache_key = f"price:{ticker}:{period}:{interval}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    try:
        data = fetch_price_data(ticker, period=period, interval=interval)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.exception("Unexpected error fetching price for %s", ticker)
        return jsonify({"error": "Failed to fetch price data. Please try again."}), 500

    cache.set(cache_key, data, timeout=config.PRICE_CACHE_TIMEOUT)
    return jsonify(data)
