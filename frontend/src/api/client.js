/**
 * API client — thin wrappers around fetch() using the /api proxy.
 */

const BASE = "/api";

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      msg = data.error || msg;
    } catch (_) {
      // backend returned non-JSON (e.g. HTML error page)
    }
    throw new Error(msg);
  }
  return res.json();
}

/**
 * Fetch sentiment analysis for a ticker.
 * @param {string} ticker  e.g. "TSLA"
 * @param {string} model   "vader" | "finbert"
 */
export function fetchSentiment(ticker, model = "vader") {
  return fetchJSON(
    `${BASE}/sentiment/${encodeURIComponent(ticker)}?model=${model}`
  );
}

/**
 * Fetch OHLCV price data for a ticker.
 * @param {string} ticker  e.g. "TSLA"
 * @param {string} period  "1mo" | "3mo" | "6mo" | "1y"
 */
export function fetchPrice(ticker, period = "1mo") {
  return fetchJSON(
    `${BASE}/price/${encodeURIComponent(ticker)}?period=${period}`
  );
}
