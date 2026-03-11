import { useState } from "react";
import SearchBar from "./components/SearchBar";
import ModelToggle from "./components/ModelToggle";
import SentimentCard from "./components/SentimentCard";
import SentimentBreakdown from "./components/SentimentBreakdown";
import PriceChart from "./components/PriceChart";
import SourcesList from "./components/SourcesList";
import { fetchSentiment, fetchPrice } from "./api/client";

export default function App() {
  const [ticker, setTicker] = useState("");
  const [model, setModel] = useState("vader");
  const [period, setPeriod] = useState("1mo");

  const [sentiment, setSentiment] = useState(null);
  const [price, setPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSearch(newTicker) {
    const t = newTicker.trim().toUpperCase();
    if (!t) return;

    setTicker(t);
    setLoading(true);
    setError(null);
    setSentiment(null);
    setPrice(null);

    try {
      const [sentimentData, priceData] = await Promise.all([
        fetchSentiment(t, model),
        fetchPrice(t, period),
      ]);
      setSentiment(sentimentData);
      setPrice(priceData);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // Re-fetch only sentiment when model changes (price stays the same)
  async function handleModelChange(newModel) {
    setModel(newModel);
    if (!ticker) return;

    setLoading(true);
    setError(null);
    try {
      const sentimentData = await fetchSentiment(ticker, newModel);
      setSentiment(sentimentData);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  // Re-fetch only price when period changes
  async function handlePeriodChange(newPeriod) {
    setPeriod(newPeriod);
    if (!ticker) return;

    try {
      const priceData = await fetchPrice(ticker, newPeriod);
      setPrice(priceData);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    }
  }

  const hasData = sentiment && price;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📈</span>
            <h1 className="text-xl font-bold text-white">
              Stock Sentiment Analyzer
            </h1>
          </div>
          <ModelToggle value={model} onChange={handleModelChange} />
        </div>
      </header>

      {/* Search */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="max-w-xl mx-auto text-center mb-8">
          <p className="text-gray-400 mb-4 text-sm">
            Enter a stock ticker to analyze Reddit &amp; news sentiment alongside
            a price chart.
          </p>
          <SearchBar onSearch={handleSearch} loading={loading} />
        </div>

        {/* Error state */}
        {error && (
          <div className="max-w-xl mx-auto bg-red-900/40 border border-red-700 rounded-xl p-4 text-center text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Loading spinner */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="ml-4 text-gray-400">
              Fetching data for {ticker}…
            </span>
          </div>
        )}

        {/* Results */}
        {hasData && !loading && (
          <div className="space-y-6">
            {/* Top row: Sentiment card + breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SentimentCard data={sentiment} />
              <SentimentBreakdown data={sentiment} />
            </div>

            {/* Price chart */}
            <PriceChart
              data={price}
              period={period}
              onPeriodChange={handlePeriodChange}
            />

            {/* Sources */}
            <SourcesList sources={sentiment.sources} />
          </div>
        )}

        {/* Empty state */}
        {!hasData && !loading && !error && (
          <div className="text-center py-24 text-gray-600">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-lg">Search for a ticker to get started</p>
            <p className="text-sm mt-2">
              e.g. TSLA, NVDA, AAPL, MSFT, GME
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
