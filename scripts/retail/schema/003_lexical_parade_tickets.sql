-- ParadeDB sidecar (port 5434): keyword index table for RETAIL_LEXICAL_BACKEND=parade_db.
-- Apply with psql against RETAIL_PARADEDB_URL, not retail_pg on 5433.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_search;

CREATE TABLE IF NOT EXISTS lexical_tickets (
    id SERIAL PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    search_text TEXT NOT NULL,
    model TEXT
);

-- BM25 index for @@@ queries (ParadeDB extension). Safe to re-run: drop if you change key_field.
DROP INDEX IF EXISTS lexical_tickets_search_idx;
CREATE INDEX lexical_tickets_search_idx ON lexical_tickets
USING bm25 (id, search_text)
WITH (key_field = 'id');
