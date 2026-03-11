# Technical Reflection: Stock Sentiment Analyzer

## Activity Description

The goal was to build a full-stack web application that analyzes public sentiment around a stock ticker and displays it alongside a price chart. The expectation was to scrape real-time text data, run sentiment analysis with at least one NLP model, and present results through a clean React frontend. I built a Flask REST API that fetches news headlines via Google News RSS, scores them with VADER or FinBERT, and returns aggregated bullish/bearish/neutral verdicts — paired with a 30-day candlestick chart powered by yfinance and Plotly.

---

## Technical Decisions

The primary news source is Google News RSS via feedparser — no API key required, no daily cap. NewsAPI was added as an optional supplement for users with a key. For sentiment, I chose VADER as the default because it runs in milliseconds with no GPU and handles informal text punctuation well. FinBERT (ProsusAI/finbert) is the optional alternative — a BERT model fine-tuned on the Financial PhraseBank dataset that handles negation and context far better but requires ~440 MB and 5–10 seconds per inference on CPU. For price data I used yfinance, which is free and convenient for an MVP despite being an unofficial scraper. On the frontend, Vite + React with Tailwind handles the UI, and Plotly renders the interactive candlestick chart.

---

## Contributions

This was an individual project. I was solely responsible for all parts: designing the API architecture, writing the Flask routes and services, integrating the sentiment models, building the React frontend, and debugging issues end-to-end — including resolving a Flask-Caching circular import bug, fixing yfinance compatibility after a major version jump (0.2.38 → 1.2.0), and hardening error handling across all routes so backend exceptions return clean JSON instead of HTML 500 pages.

---

## Quality Assessment

The app works end-to-end and handles real tickers reliably. The caching layer (15 min for sentiment, 5 min for price) keeps it responsive on repeated queries. That said, I would do a few things differently. I would set up the Reddit data source from the start rather than removing it late — the API policy change was a blocker I didn't anticipate. I would also add an integration test suite early so regressions like the cache KeyError or the yfinance `.get()` crash would be caught before runtime. Finally, the sentiment signal itself is limited — news-only coverage without social data misses a lot of retail-driven momentum, so for a v2 I would prioritize a proper social data source alongside the news pipeline.
