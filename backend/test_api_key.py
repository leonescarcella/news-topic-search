import os, requests
from dotenv import load_dotenv

# Carica variabili da backend/.env
load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")

print("API_KEY letta:", (API_KEY[:6] + "...") if API_KEY else "❌ nessuna chiave trovata")

url = "https://newsapi.ai/api/v1/article/getArticles"
params = {
    "apiKey": API_KEY,
    "resultType": "articles",
    "articlesCount": 10,
    "keyword": "news",   # keyword semplice per avere risultati
    "lang": "eng"
}

try:
    r = requests.get(url, params=params, timeout=30)
    print("HTTP status:", r.status_code)
    j = r.json()
    arts = (j.get("articles") or {}).get("results") or []
    print("Articoli trovati:", len(arts))
    if arts:
        print("Primo titolo:", arts[0].get("title", "—")[:120])
except Exception as e:
    print("Errore:", e)
