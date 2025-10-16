import os, time, requests
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
DB_URL = os.getenv("DATABASE_URL")

def get_news(page=1):
    url = "https://newsapi.ai/api/v1/article/getArticles"
    params = {
        "apiKey": API_KEY,
        "resultType": "articles",
        "articlesPage": page,
        "articlesCount": 100,
        "lang": "eng",
        "sourceLocationUri": "http://en.wikipedia.org/wiki/World"
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def save_article(cur, art):
    url = art.get("url")
    if not url:
        return
    cur.execute("SELECT id FROM articles WHERE url=%s", (url,))
    if cur.fetchone():
        return
    title = art.get("title")
    description = (art.get("body") or "")[:500]
    author = art.get("authors", [{}])[0].get("name") if art.get("authors") else None
    source = art.get("source", {}).get("title")
    content = art.get("body")
    pub = art.get("dateTimePub")
    published_at = datetime.fromisoformat(pub.replace("Z","+00:00")) if pub else None
    cur.execute("""
        INSERT INTO articles (source, author, title, description, url, published_at, content, raw_json)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (url) DO NOTHING
    """, (source, author, title, description, url, published_at, content, Json(art)))

def main():
    if not API_KEY:
        raise RuntimeError("NEWSAPI_KEY mancante nel .env")
    conn = psycopg2.connect(DB_URL); conn.autocommit = False
    cur = conn.cursor()
    page = 1
    while True:
        data = get_news(page)
        arts = data.get("articles", {}).get("results", [])
        if not arts:
            break
        for a in arts:
            save_article(cur, a)
        conn.commit()
        page += 1
        time.sleep(1)
    cur.close(); conn.close()

if __name__ == "__main__":
    main()
