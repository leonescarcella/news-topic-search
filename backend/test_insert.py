import os, psycopg2
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Conta prima
cur.execute("SELECT COUNT(*) FROM articles;")
before = cur.fetchone()[0]

# Inseriamo un articolo finto
cur.execute("""
INSERT INTO articles (source, author, title, description, url, published_at, content, raw_json)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT (url) DO NOTHING
""", (
    "TestSource", "Me", "Titolo di test", "Descrizione di test",
    "https://example.com/finto-articolo",  # <- url unico
    datetime.utcnow(), "Contenuto di test", '{}'
))

conn.commit()

# Conta dopo
cur.execute("SELECT COUNT(*) FROM articles;")
after = cur.fetchone()[0]
cur.close(); conn.close()

print(f"Prima: {before}, Dopo: {after}, Inseriti: {after - before}")
