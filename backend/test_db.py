import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    print("✅ Connessione al database riuscita!")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM articles;")
    print("Numero articoli:", cur.fetchone()[0])
    cur.close()
    conn.close()
except Exception as e:
    print("❌ Errore nella connessione:", e)
