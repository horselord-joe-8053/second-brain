-- FRU service brain: join key to future sales analytics (nullable on phone-era rows).
ALTER TABLE service_queries ADD COLUMN IF NOT EXISTS customer_id TEXT;
