# Stock Sentiment Analyzer

A full-stack web app that scrapes Reddit posts (r/wallstreetbets, r/stocks) and news headlines, runs sentiment analysis, and displays whether overall market sentiment is **bullish**, **bearish**, or **neutral** — alongside an interactive price chart.

![screenshot placeholder](docs/screenshots/dashboard.png)

---

## Features

- **Search by ticker** — Enter any stock symbol (e.g. TSLA, NVDA, AAPL)
- **Dual sentiment models** — Toggle between VADER (fast) and FinBERT (accurate)
- **Breakdown chart** — % positive / negative / neutral with a donut + bar chart
- **Candlestick price chart** — 30-day OHLCV data with volume subplot via Plotly
- **Source list** — Top Reddit posts and news headlines that drove the score, tabbed and sortable
- **Smart caching** — Sentiment cached 15 min, price cached 5 min to avoid API throttling

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask 3, Flask-CORS, Flask-Caching |
| Reddit | PRAW 7 (r/wallstreetbets, r/stocks, r/investing, r/options) |
| News | feedparser (Google News RSS) + NewsAPI (optional) |
| Sentiment | NLTK VADER · HuggingFace FinBERT (ProsusAI/finbert) |
| Price data | yfinance |
| Frontend | React 18 + Vite 5 |
| Charts | Plotly.js (via react-plotly.js) |
| Styling | Tailwind CSS 3 |

---

## Prerequisites

- **Python 3.11+** — [python.org](https://python.org)
- **Node.js 18+** — [nodejs.org](https://nodejs.org)
- **Reddit API credentials** — free, read-only app (instructions below)
- **NewsAPI key** *(optional)* — [newsapi.org/register](https://newsapi.org/register)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/stock-sentiment-analyzer.git
cd stock-sentiment-analyzer
```

### 2. Configure environment variables

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and fill in your credentials:

```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=StockSentimentAnalyzer/1.0 by YourRedditUsername
NEWSAPI_KEY=your_newsapi_key        # optional
FLASK_SECRET_KEY=any-random-string
```

#### Getting Reddit credentials

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **"create another app"** at the bottom
3. Choose **"script"** type
4. Set redirect URI to `http://localhost:8080`
5. Copy the **client ID** (under the app name) and **client secret**

### 3. Install backend dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Optional: FinBERT support (~440 MB)

The FinBERT model toggle requires PyTorch and HuggingFace Transformers. Install the lightweight CPU-only build:

```bash
# CPU-only PyTorch (saves ~1.5 GB vs the default GPU build)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install Transformers
pip install -r requirements-finbert.txt
```

> The model weights (~440 MB) are downloaded automatically from HuggingFace on first use and cached at `~/.cache/huggingface/`. Subsequent runs use the local cache.

### 4. Install frontend dependencies

```bash
cd ../frontend
npm install
```

---

## Running the App

Open **two terminals**:

**Terminal 1 — Flask backend**
```bash
cd backend
# Activate venv if not already active
python app.py
```
Flask starts on [http://localhost:5000](http://localhost:5000)

**Terminal 2 — React frontend**
```bash
cd frontend
npm run dev
```
Vite starts on [http://localhost:5173](http://localhost:5173)

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## API Reference

### `GET /api/sentiment/<ticker>`

| Parameter | Type  | Default | Description |
| `model`   | query | `vader` | `vader` or `finbert` |

**Example:** `GET /api/sentiment/TSLA?model=vader`

```json
{
  "ticker": "TSLA",
  "overall": "bullish",
  "score": 0.342,
  "model": "vader",
  "breakdown": {
    "positive": 45, "negative": 12, "neutral": 23,
    "total": 80,
    "pct_positive": 56.2, "pct_negative": 15.0, "pct_neutral": 28.8
  },
  "sources": [
    {
      "type": "reddit",
      "title": "TSLA's FSD v13 is a game changer",
      "url": "https://reddit.com/...",
      "date": "2026-03-09",
      "sentiment": "positive",
      "score": 0.871,
      "source": "wallstreetbets",
      "upvotes": 4210
    }
  ],
  "reddit_count": 45,
  "news_count": 35
}
```

**Errors:**
- `400` — Invalid ticker format
- `404` — No data found for ticker

---

### `GET /api/price/<ticker>`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `period` | query | `1mo` | `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y` |
| `interval` | query | `1d` | `1d`, `1wk`, `1mo` |

**Example:** `GET /api/price/TSLA?period=3mo`

```json
{
  "ticker": "TSLA",
  "dates": ["2025-12-10", "2025-12-11", "..."],
  "open": [350.2, 355.1, "..."],
  "high": [362.0, 358.4, "..."],
  "low":  [348.5, 350.2, "..."],
  "close": [355.8, 352.1, "..."],
  "volume": [48200000, 39100000, "..."],
  "period": "3mo",
  "interval": "1d",
  "currency": "USD"
}
```

---

## Project Structure

```
stock-sentiment-analyzer/
├── backend/
│   ├── app.py                    # Flask entry point + factory
│   ├── config.py                 # Environment config
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── sentiment.py          # GET /api/sentiment/<ticker>
│   │   └── price.py              # GET /api/price/<ticker>
│   └── services/
│       ├── reddit_scraper.py     # PRAW scraping
│       ├── news_scraper.py       # RSS + NewsAPI
│       ├── sentiment_engine.py   # VADER + FinBERT scoring
│       └── price_fetcher.py      # yfinance data
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Root component + state
│   │   ├── api/client.js         # fetch() wrappers
│   │   └── components/
│   │       ├── SearchBar.jsx
│   │       ├── ModelToggle.jsx
│   │       ├── SentimentCard.jsx
│   │       ├── SentimentBreakdown.jsx
│   │       ├── PriceChart.jsx
│   │       └── SourcesList.jsx
│   ├── vite.config.js
│   └── package.json
├── docs/
│   ├── reflection.md
│   └── screenshots/
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No data found for ticker` | Check Reddit credentials in `.env`; try a well-known ticker like AAPL |
| `PRAW 401 Unauthorized` | Double-check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` |
| FinBERT very slow | Expected on CPU — ~5-10s per item. First run also downloads 440 MB. Use VADER for faster results. |
| News articles empty | Google News RSS may be rate-limited. Wait 30s and retry. |
| `Port 5000 already in use` | Change Flask port: `python app.py --port 5001` and update `vite.config.js` proxy target |

---

## License

MIT
