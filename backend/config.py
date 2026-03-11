"""
Central configuration — loads .env file so every module can import from here.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Reddit
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv(
        "REDDIT_USER_AGENT", "StockSentimentAnalyzer/1.0"
    )

    # NewsAPI
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")

    # Flask
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    # Caching
    CACHE_TYPE: str = "SimpleCache"
    SENTIMENT_CACHE_TIMEOUT: int = 900   # 15 minutes
    PRICE_CACHE_TIMEOUT: int = 300       # 5 minutes

    # Scraping limits
    REDDIT_POST_LIMIT: int = 50
    NEWS_ARTICLE_LIMIT: int = 30

    # Sentiment thresholds
    VADER_POSITIVE_THRESHOLD: float = 0.05
    VADER_NEGATIVE_THRESHOLD: float = -0.05
    BULLISH_THRESHOLD: float = 0.05
    BEARISH_THRESHOLD: float = -0.05

    @property
    def reddit_configured(self) -> bool:
        return bool(self.REDDIT_CLIENT_ID and self.REDDIT_CLIENT_SECRET)

    @property
    def newsapi_configured(self) -> bool:
        return bool(self.NEWSAPI_KEY)


config = Config()
