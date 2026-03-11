import { useState } from "react";

export default function SearchBar({ onSearch, loading }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = value.trim().toUpperCase();
    if (trimmed) onSearch(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value.toUpperCase())}
        placeholder="Enter ticker…  e.g. TSLA"
        maxLength={5}
        className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3
                   text-white placeholder-gray-500 text-lg font-mono tracking-widest
                   focus:outline-none focus:ring-2 focus:ring-indigo-500"
        disabled={loading}
        spellCheck={false}
        autoComplete="off"
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50
                   disabled:cursor-not-allowed text-white font-semibold
                   px-6 py-3 rounded-xl transition-colors"
      >
        {loading ? "…" : "Analyze"}
      </button>
    </form>
  );
}
