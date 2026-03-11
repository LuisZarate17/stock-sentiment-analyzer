import Plot from "react-plotly.js";

export default function SentimentBreakdown({ data }) {
  const bd = data?.breakdown;
  if (!bd) return null;

  const positive = bd.pct_positive ?? 0;
  const neutral = bd.pct_neutral ?? 0;
  const negative = bd.pct_negative ?? 0;

  // Donut chart
  const plotData = [
    {
      type: "pie",
      hole: 0.65,
      values: [positive, neutral, negative],
      labels: ["Positive", "Neutral", "Negative"],
      marker: {
        colors: ["#22c55e", "#6b7280", "#ef4444"],
      },
      textinfo: "label+percent",
      textposition: "outside",
      hovertemplate: "%{label}: %{value:.1f}%<extra></extra>",
    },
  ];

  const layout = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: { color: "#d1d5db", size: 13 },
    margin: { t: 20, b: 20, l: 20, r: 20 },
    showlegend: false,
    annotations: [
      {
        text: `${bd.total}<br>items`,
        x: 0.5,
        y: 0.5,
        font: { size: 15, color: "#e5e7eb" },
        showarrow: false,
      },
    ],
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <h2 className="text-gray-300 font-semibold mb-4 text-sm uppercase tracking-wide">
        Sentiment Breakdown
      </h2>

      <div className="flex items-center gap-6">
        <Plot
          data={plotData}
          layout={layout}
          config={{ displayModeBar: false, responsive: true }}
          useResizeHandler
          style={{ width: "100%", maxWidth: 260, height: 220 }}
        />

        {/* Bar legend */}
        <div className="flex-1 space-y-3 text-sm">
          {[
            { label: "Positive", pct: positive, count: bd.positive, color: "bg-green-500" },
            { label: "Neutral", pct: neutral, count: bd.neutral, color: "bg-gray-500" },
            { label: "Negative", pct: negative, count: bd.negative, color: "bg-red-500" },
          ].map(({ label, pct, count, color }) => (
            <div key={label}>
              <div className="flex justify-between text-gray-400 mb-1">
                <span>{label}</span>
                <span className="font-mono">
                  {count}{" "}
                  <span className="text-gray-600">({pct.toFixed(1)}%)</span>
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`${color} h-2 rounded-full transition-all`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
