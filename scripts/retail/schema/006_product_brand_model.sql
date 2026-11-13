-- Product identity for retrieval: brand + OEM model (not POS SKU).
-- Backfill existing rows via scripts/retail/ops/backfill_product_brand_model.py

ALTER TABLE service_queries ADD COLUMN IF NOT EXISTS brand TEXT NOT NULL DEFAULT '';

ALTER TABLE manual_chunks ADD COLUMN IF NOT EXISTS brand TEXT NOT NULL DEFAULT '';
ALTER TABLE manual_chunks ADD COLUMN IF NOT EXISTS oem_model TEXT NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS idx_service_queries_brand_model
  ON service_queries (brand, model);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_lane_brand_model
  ON manual_chunks (lane_id, brand, oem_model);
