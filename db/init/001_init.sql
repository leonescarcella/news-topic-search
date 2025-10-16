CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS articles (
  id BIGSERIAL PRIMARY KEY,
  source TEXT,
  author TEXT,
  title TEXT,
  description TEXT,
  url TEXT UNIQUE,
  published_at TIMESTAMPTZ,
  content TEXT,
  raw_json JSONB,
  embedding VECTOR(384)
);

CREATE TABLE IF NOT EXISTS topics (
  id BIGSERIAL PRIMARY KEY,
  article_id BIGINT REFERENCES articles(id) ON DELETE CASCADE,
  keyphrase TEXT,
  score REAL
);

CREATE INDEX IF NOT EXISTS idx_articles_published ON articles (published_at);
CREATE INDEX IF NOT EXISTS idx_articles_embedding ON articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

ALTER TABLE articles ADD COLUMN IF NOT EXISTS tsv tsvector;
CREATE INDEX IF NOT EXISTS idx_articles_tsv ON articles USING GIN (tsv);
