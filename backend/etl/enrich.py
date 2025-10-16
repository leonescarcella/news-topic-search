import os, re, psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def clean_text(t):
    if not t: return ""
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def main():
    kw = KeyBERT()
    emb = SentenceTransformer("all-MiniLM-L6-v2")
    conn = psycopg2.connect(DB_URL); conn.autocommit = False
    cur = conn.cursor()
    cur.execute("""
      SELECT id, COALESCE(title,'')||' '||COALESCE(description,'')||' '||COALESCE(content,'') AS text
      FROM articles WHERE embedding IS NULL LIMIT 300
    """)
    for aid, raw in cur.fetchall():
        text = clean_text(raw)
        if not text: continue
        keyphrases = kw.extract_keywords(text, keyphrase_ngram_range=(1,3), stop_words="english", top_n=10)
        vec = emb.encode([text])[0].tolist()
        cur.execute("UPDATE articles SET embedding=%s::vector, tsv=to_tsvector('simple', %s) WHERE id=%s",
                    (vec, text[:50000], aid))
        if keyphrases:
            execute_values(cur,
                "INSERT INTO topics (article_id, keyphrase, score) VALUES %s",
                [(aid, kp, float(score)) for kp, score in keyphrases]
            )
    conn.commit(); cur.close(); conn.close()

if __name__ == "__main__":
    main()
