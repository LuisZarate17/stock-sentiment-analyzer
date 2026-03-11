import Plot from "react-plotly.js";

const PERIODS = [
  { value: "5d", label: "5D" },
  { value: "1mo", label: "1M" },
  { value: "3mo", label: "3M" },
  { value: "6mo", label: "6M" },
  { value: "1y", label: "1Y" },
];

export default function PriceChart({ data, period, onPeriodChange }) {
  if (!data) return null;

  const { ticker, dates, open, high, low, close, volume, currency } = data;

  // Candlestick trace
  const candlestick = {
    type: "candlestick",
    x: dates,
    open,
    high,
    low,
    close,
    name: ticker,
    increasing: { line: { color: "#22c55e" }, fillcolor: "#16a34a" },
    decreasing: { line: { color: "#ef4444" }, fillcolor: "#dc2626" },
    yaxis: "y",
    hovertemplate:
      "<b>%{x}</b><br>" +
      "Open: %{open:.2f}<br>" +
      "High: %{high:.2f}<br>" +
      "Low: %{low:.2f}<br>" +
      "Close: %{close:.2f}<extra></extra>",
  };

  // Volume bar trace
  const volumeBars = {
    type: "bar",
    x: dates,
    y: volume,
    name: "Volume",
    yaxis: "y2",
    marker: {
      color: close.map((c, i) =>
        c >= open[i] ? "rgba(34,197,94,0.4)" : "rgba(239,68,68,0.4)"
      ),
    },
    hovertemplate: "Vol: %{y:,}<extra></extra>",
  };

  const layout = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "#111827",
    font: { color: "#9ca3af", size: 11 },
    xaxis: {
      rangeslider: { visible: false },
      gridcolor: "#1f2937",
      linecolor: "#374151",
      tickfont: { color: "#6b7280" },
      type: "date",
    },
    yaxis: {
      domain: [0.25, 1.0],
      gridcolor: "#1f2937",
      linecolor: "#374151",
      tickfont: { color: "#6b7280" },
      tickprefix: currency === "USD" ? "$" : "",
      side: "right",
    },
    yaxis2: {
      domain: [0, 0.2],
      gridcolor: "#1f2937",
      linecolor: "#374151",
      tickfont: { color: "#6b7280" },
      showticklabels: false,
    },
    margin: { t: 20, b: 30, l: 10, r: 60 },
    showlegend: false,
    hovermode: "x unified",
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      {/* Header + period selector */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-gray-300 font-semibold text-sm uppercase tracking-wide">
          {ticker} — Price Chart
        </h2>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => onPeriodChange(p.value)}
              className={`px-3 py-1 text-xs rounded-lg font-medium transition-colors
                ${
                  period === p.value
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <Plot
        data={[candlestick, volumeBars]}
        layout={layout}
        config={{ displayModeBar: false, responsive: true }}
        useResizeHandler
        style={{ width: "100%", height: 400 }}
      />
    </div>
  );
}
