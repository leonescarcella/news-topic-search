"use client";
import { useState } from "react";

type Result = {
  id: number;
  title?: string;
  url?: string;
  published_at?: string;
  score?: number;
};

export default function Home() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);
  const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const doSearch = async () => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error(e);
      alert("Errore durante la ricerca");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">News Topics Search</h1>
      <div className="flex gap-2">
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="Es. AI, climate, economy…"
          value={q}
          onChange={e => setQ(e.target.value)}
          onKeyDown={e => e.key === "Enter" ? doSearch() : null}
        />
        <button className="border rounded px-4" onClick={doSearch}>
          {loading ? "..." : "Cerca"}
        </button>
      </div>
      <ul className="mt-6 space-y-3">
        {results.map((r) => (
          <li key={r.id} className="border rounded p-3">
            <a href={r.url ?? "#"} target="_blank" className="font-medium underline">
              {r.title ?? "Senza titolo"}
            </a>
            <div className="text-sm opacity-70">
              {r.published_at ? new Date(r.published_at).toLocaleString() : "Data n/d"} — score: {r.score?.toFixed?.(3) ?? "n/d"}
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
