const LABEL_CONFIG = {
  bullish: {
    bg: "bg-green-900/40",
    border: "border-green-700",
    text: "text-green-400",
    badge: "bg-green-600",
    icon: "🐂",
  },
  bearish: {
    bg: "bg-red-900/40",
    border: "border-red-700",
    text: "text-red-400",
    badge: "bg-red-600",
    icon: "🐻",
  },
  neutral: {
    bg: "bg-gray-800/60",
    border: "border-gray-700",
    text: "text-gray-300",
    badge: "bg-gray-600",
    icon: "⚖️",
  },
};

export default function SentimentCard({ data }) {
  const overall = data?.overall ?? "neutral";
  const cfg = LABEL_CONFIG[overall] ?? LABEL_CONFIG.neutral;
  const score = data?.score ?? 0;
  const ticker = data?.ticker ?? "";
  const model = data?.model ?? "";
  const redditCount = data?.reddit_count ?? 0;
  const newsCount = data?.news_count ?? 0;

  return (
    <div
      className={`rounded-2xl border p-6 ${cfg.bg} ${cfg.border} flex flex-col gap-4`}
    >
      {/* Ticker + overall label */}
      <div className="flex items-center justify-between">
        <span className="text-3xl font-black font-mono tracking-widest text-white">
          {ticker}
        </span>
        <span
          className={`${cfg.badge} text-white text-sm font-bold px-4 py-1.5 rounded-full uppercase tracking-wide`}
        >
          {cfg.icon} {overall}
        </span>
      </div>

      {/* Composite score */}
      <div>
        <p className="text-gray-400 text-xs mb-1">Composite Sentiment Score</p>
        <div className="flex items-end gap-2">
          <span className={`text-5xl font-black ${cfg.text}`}>
            {score >= 0 ? "+" : ""}
            {score.toFixed(3)}
          </span>
          <span className="text-gray-500 text-sm mb-1">/ ±1.0</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2 mt-2 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              overall === "bullish"
                ? "bg-green-500"
                : overall === "bearish"
                ? "bg-red-500"
                : "bg-gray-400"
            }`}
            style={{ width: `${Math.min(Math.abs(score) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Meta */}
      <div className="flex gap-4 text-xs text-gray-500 flex-wrap">
        <span>
          📊 {data?.breakdown?.total ?? 0} items analyzed
        </span>
        <span>🔴 Reddit: {redditCount}</span>
        <span>📰 News: {newsCount}</span>
        <span className="ml-auto bg-gray-800 px-2 py-1 rounded-md font-mono">
          {model.toUpperCase()}
        </span>
      </div>
    </div>
  );
}
