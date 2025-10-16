import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM articles WHERE embedding IS NOT NULL;")
emb = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM topics;")
tpc = cur.fetchone()[0]
cur.close(); conn.close()
print("Articoli con embedding:", emb)
print("Topic estratti:", tpc)