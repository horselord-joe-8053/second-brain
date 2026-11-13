-- Manual raw RAG chunks in Postgres (dense + optional tsvector for future A/B).
-- Embed dim 1536 (OpenAI text-embedding-3-small default); tickets stay vector(768).

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS manual_chunks (
  chunk_id TEXT PRIMARY KEY,
  lane_id TEXT NOT NULL,
  source_relpath TEXT NOT NULL,
  model_id TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  embedding vector(1536),
  chunk_tsv tsvector,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_lane_model
  ON manual_chunks (lane_id, model_id);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_tsv
  ON manual_chunks USING GIN (chunk_tsv);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_embedding
  ON manual_chunks USING hnsw (embedding vector_cosine_ops);
