-- Idempotent add for existing retail PG volumes (fresh installs use 001_retail.sql).
ALTER TABLE service_queries ADD COLUMN IF NOT EXISTS search_text TEXT;
