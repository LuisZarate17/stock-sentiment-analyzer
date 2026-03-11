const MODELS = [
  {
    id: "vader",
    label: "VADER",
    desc: "Fast · lexicon-based",
  },
  {
    id: "finbert",
    label: "FinBERT",
    desc: "Accurate · finance-tuned BERT",
  },
];

export default function ModelToggle({ value, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-500 text-xs mr-1">Model:</span>
      {MODELS.map((m) => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          title={m.desc}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
            ${
              value === m.id
                ? "bg-indigo-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
