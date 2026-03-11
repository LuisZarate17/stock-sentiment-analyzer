"""
Stock price fetcher using yfinance.
Returns OHLCV data serialised for Plotly.
"""
from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)

VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y"}
VALID_INTERVALS = {"1d", "1wk", "1mo"}


def fetch_price_data(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
) -> dict[str, Any]:
    """
    Fetch OHLCV history for `ticker` and return a dict ready for Plotly.

    Raises ValueError if the ticker is invalid or yields no data.
    """
    period = period if period in VALID_PERIODS else "1mo"
    interval = interval if interval in VALID_INTERVALS else "1d"

    ticker_upper = ticker.upper()
    t = yf.Ticker(ticker_upper)
    df = t.history(period=period, interval=interval)

    if df.empty:
        raise ValueError(
            f"No price data found for ticker '{ticker_upper}'. "
            "Check that the symbol is valid."
        )

    # Serialise DatetimeIndex → ISO date strings
    dates = df.index.strftime("%Y-%m-%d").tolist()

    try:
        currency = t.fast_info["currency"] or "USD"
    except Exception:
        currency = "USD"

    return {
        "ticker": ticker_upper,
        "dates": dates,
        "open": [round(v, 4) for v in df["Open"].tolist()],
        "high": [round(v, 4) for v in df["High"].tolist()],
        "low": [round(v, 4) for v in df["Low"].tolist()],
        "close": [round(v, 4) for v in df["Close"].tolist()],
        "volume": [int(v) if v == v else 0 for v in df["Volume"].tolist()],
        "period": period,
        "interval": interval,
        "currency": currency,
    }
