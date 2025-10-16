from fastapi.responses import HTMLResponse
import os, psycopg2
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="News Topics Search API", version="0.1.0")

# CORS libero per test locale (puoi restringere in produzione)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Modello per embedding query (lo stesso dell'enrich)
emb_model = SentenceTransformer("all-MiniLM-L6-v2")

class SearchResponse(BaseModel):
    id: int
    title: str | None
    url: str | None
    published_at: str | None
    score: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/count")
def count():
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM articles;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM articles WHERE embedding IS NOT NULL;")
    with_emb = cur.fetchone()[0]
    cur.close(); conn.close()
    return {"articles": total, "with_embedding": with_emb}

@app.get("/search", response_model=list[SearchResponse])
def search(q: str = Query(..., min_length=2), limit: int = 20):
    # 1) embedding della query
    vec = emb_model.encode([q])[0].tolist()
    # 2) query su Postgres (pgvector) ordinata per distanza coseno
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("""
        SELECT id, title, url, published_at, 1 - (embedding <=> %s::vector) AS score
        FROM articles
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (vec, vec, limit))
    rows = cur.fetchall()
    cur.close(); conn.close()
    # 3) risposta
    return [
        {
            "id": r[0],
            "title": r[1],
            "url": r[2],
            "published_at": r[3].isoformat() if r[3] else None,
            "score": float(r[4]),
        }
        for r in rows
    ]
@app.get("/")
def root():
    return {
        "message": "News Topics Search API",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "count": "/count",
            "search": "/search?q=ai"
        }
    }
@app.get("/demo", response_class=HTMLResponse)
def demo():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>News Topics Search — Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; }
    input, button { font-size: 16px; padding: 8px; }
    li { margin: 8px 0; }
  </style>
</head>
<body>
  <h1>Demo ricerca articoli per topic</h1>
  <p>Scrivi un argomento (es. <em>ai</em>, <em>climate</em>, <em>economy</em>) e premi Cerca.</p>
  <div>
    <input id="q" placeholder="es. ai, climate, economy..." />
    <button onclick="doSearch()">Cerca</button>
  </div>
  <ul id="results"></ul>

<script>
async function doSearch() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  const ul = document.getElementById('results');
  ul.innerHTML = '';
  data.forEach(item => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = item.url || '#';
    a.target = '_blank';
    a.textContent = item.title || '(senza titolo)';
    const small = document.createElement('div');
    small.style.opacity = 0.7;
    small.style.fontSize = '14px';
    small.textContent = (item.published_at || 'data n/d') + ' — score: ' + (item.score?.toFixed?.(3) || 'n/d');
    li.appendChild(a);
    li.appendChild(small);
    ul.appendChild(li);
  });
}
</script>
</body>
</html>
"""
