# Technical Reflection: Stock Sentiment Analyzer

## Overview

Building a stock sentiment analyzer required integrating four distinct data pipelines — Reddit, news, sentiment models, and financial price data — into a cohesive API. Each component presented its own trade-offs in accuracy, reliability, and latency. This reflection examines those decisions.

---

## Data Sources: Why Reddit and RSS?

Reddit's r/wallstreetbets and r/stocks were chosen as primary social sources because they represent two ends of the retail investor spectrum: high-energy meme-driven trading (WSB) and more measured discussion (r/stocks). Together, they provide breadth. PRAW, the official Python Reddit wrapper, handles OAuth automatically and respects rate limits, making it robust for production use.

One significant limitation is that Reddit data is inherently noisy. WSB is saturated with hyperbole, irony, and community-specific vocabulary ("tendies," "to the moon," "bag holder"). A post saying "TSLA will moon 🚀🚀🚀" may register as neutral or only mildly positive under VADER due to the absence of those terms from its lexicon, while a FinBERT model trained on formal financial language may underperform on such slang altogether.

Google News RSS was selected as the primary news source because it requires no API key, has no daily request cap, and returns results from hundreds of publishers. NewsAPI was added as an optional supplement for users who register a key, providing structured metadata and more reliable article counts. The limitation of both is recency — free-tier NewsAPI caps articles at one month old, and Google News RSS typically returns only the past week.

---

## Sentiment Model Choice: VADER vs. FinBERT

VADER (Valence Aware Dictionary and sEntiment Reasoner) was made the default for several reasons. It runs in milliseconds per text, requires no GPU, handles punctuation effects (capitalization, exclamation marks, ellipses), and was explicitly tuned for social media text — which aligns closely with Reddit posts. Its compound score provides a single normalised float that maps cleanly to bullish/bearish/neutral categories.

FinBERT (ProsusAI/finbert) is the optional high-precision alternative. It is a BERT-base model fine-tuned on the Financial PhraseBank dataset — a corpus of financial news sentences annotated by domain experts. It handles context and negation far better than a lexicon-based approach. "Analysts are not optimistic about Q3 earnings" would score near zero in VADER but strongly negative in FinBERT. The trade-off is a ~440 MB model size, 5–10 second inference time per text on CPU, and the fact that it performs better on formal financial prose than informal Reddit posts.

In practice, for Reddit-heavy searches VADER often produces comparable or better results. For news-heavy or earnings-focused searches, FinBERT provides more trustworthy sentiment signals.

---

## Aggregation and Upvote Weighting

A key design decision was weighting Reddit posts by upvote count using a logarithmic scale: `log(upvotes + 1)`. A post with 10,000 upvotes carries substantially more community signal than one with 2 upvotes, but without a cap the distribution would be dominated by viral posts. The log transform keeps the scale manageable. News articles receive a flat weight of 1.0 since no engagement metric is available.

The overall verdict threshold (bullish: >+0.05, bearish: <-0.05) was chosen conservatively to avoid false signals on weakly opinionated text pools.

---

## Price Data and yfinance

yfinance is an unofficial Yahoo Finance scraper. It is convenient and free but carries risks: Yahoo can change its API contract without notice, rate limiting occurs during high-traffic periods, and there is no SLA. For a production system, a paid data provider (Polygon.io, Alpaca, IEX Cloud) would be preferable. For this local-use MVP, yfinance is a pragmatic choice.

---

## Accuracy Limitations

The system has several known accuracy limitations. First, the correlation between social sentiment and price movement is weak and noisy — this tool analyzes *current* community mood, not future price direction. Second, sentiment alone cannot account for short-squeeze dynamics, earnings surprises, or macro events that dominate short-term price action. Third, both models struggle with sarcasm: "Oh yeah NVDA going to zero for sure haha" would likely score as negative. Finally, the dataset is limited to English-language sources and biased toward U.S. markets.

This analyzer is best used as a supplementary signal alongside fundamental analysis, not as a standalone trading tool.

---

## Future Improvements

Potential enhancements include fine-tuning a transformer model on WSB-specific labeled data, adding temporal trend analysis (sentiment over time), integrating options flow data, deduplicating near-duplicate headlines across sources, and adding real-time streaming via WebSockets.
