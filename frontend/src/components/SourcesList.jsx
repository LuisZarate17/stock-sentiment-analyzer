import { useState } from "react";

const TABS = ["All", "Reddit", "News"];

const SENTIMENT_BADGE = {
  positive: "bg-green-700/60 text-green-300 border border-green-700",
  negative: "bg-red-700/60 text-red-300 border border-red-700",
  neutral: "bg-gray-700/60 text-gray-300 border border-gray-700",
};

const SOURCE_ICONS = {
  reddit: "🔴",
  news: "📰",
};

export default function SourcesList({ sources }) {
  const [activeTab, setActiveTab] = useState("All");

  if (!sources?.length) return null;

  const filtered = sources.filter((s) => {
    if (activeTab === "All") return true;
    if (activeTab === "Reddit") return s.type === "reddit";
    if (activeTab === "News") return s.type === "news";
    return true;
  });

  // Sort by absolute score descending
  const sorted = [...filtered].sort(
    (a, b) => Math.abs(b.score) - Math.abs(a.score)
  );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      {/* Header + tabs */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h2 className="text-gray-300 font-semibold text-sm uppercase tracking-wide">
          Posts &amp; Headlines
        </h2>
        <div className="flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1 text-xs rounded-lg font-medium transition-colors
                ${
                  activeTab === tab
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      <ul className="space-y-3">
        {sorted.map((item, idx) => (
          <li
            key={idx}
            className="flex items-start gap-3 bg-gray-800/60 rounded-xl p-4 hover:bg-gray-800 transition-colors"
          >
            {/* Source icon */}
            <span className="text-lg mt-0.5 shrink-0">
              {SOURCE_ICONS[item.type] ?? "📄"}
            </span>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-gray-200 hover:text-indigo-400 font-medium line-clamp-2 transition-colors"
              >
                {item.title || "(no title)"}
              </a>
              <div className="flex items-center gap-2 mt-2 flex-wrap text-xs text-gray-500">
                {item.source && (
                  <span className="bg-gray-700 px-2 py-0.5 rounded">
                    {item.source}
                  </span>
                )}
                {item.date && <span>{item.date}</span>}
                {item.type === "reddit" && item.upvotes != null && (
                  <span>▲ {item.upvotes.toLocaleString()}</span>
                )}
              </div>
            </div>

            {/* Sentiment badge + score */}
            <div className="shrink-0 text-right">
              <span
                className={`text-xs font-semibold px-2 py-1 rounded-full ${
                  SENTIMENT_BADGE[item.sentiment] ?? SENTIMENT_BADGE.neutral
                }`}
              >
                {item.sentiment}
              </span>
              <p className="text-xs text-gray-500 font-mono mt-1">
                {item.score >= 0 ? "+" : ""}
                {item.score?.toFixed(3)}
              </p>
            </div>
          </li>
        ))}
      </ul>

      {sorted.length === 0 && (
        <p className="text-gray-600 text-sm text-center py-6">
          No {activeTab.toLowerCase()} sources available.
        </p>
      )}
    </div>
  );
}
