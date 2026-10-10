CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS retail_sales (
  id SERIAL PRIMARY KEY,
  store_id TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  model TEXT NOT NULL,
  units INTEGER NOT NULL,
  revenue NUMERIC NOT NULL,
  sale_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS service_queries (
  ticket_id TEXT PRIMARY KEY,
  item_number TEXT NOT NULL,
  store_id TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  model TEXT NOT NULL,
  status TEXT NOT NULL,
  customer_query_text TEXT NOT NULL,
  resolution_text TEXT,
  opened_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ,
  query_embedding vector(768),
  query_tsv tsvector
);

CREATE INDEX IF NOT EXISTS idx_service_queries_status ON service_queries (status);
CREATE INDEX IF NOT EXISTS idx_service_queries_model ON service_queries (model);
CREATE INDEX IF NOT EXISTS idx_service_queries_tsv ON service_queries USING GIN (query_tsv);
