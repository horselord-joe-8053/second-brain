# Corpus schema — retail brain-profile (v1)

- **Sources:** `raw/sources/fridge-docs/<sku>/{user-guide.pdf,repair-guide.pdf}` — SKU folders: `samsung_RF28K9070SG`, `ge_GNE27JYMFS`, `kitchenaid_KRFF507HPS`. PDFs are committed (see `brain/.gitignore`).
- **Manifests:** `manifests/pdf_page_index.jsonl` — one row per PDF page (`pdf_path`, `sku`, `guide`, `page`, `text`), built by `scripts/retail/manuals/build_pdf_page_index.py`; used to cite manual evidence by page.
- **Compiled wiki:** `wiki/` — maintained by Nashsu LLM Wiki (compiler output). Source pages keep frontmatter `sources: ["fridge-docs/<sku>/<guide>.pdf"]`, which maps a wiki excerpt back to its raw PDF.
- **Tickets:** not stored here. Historical tickets live in Postgres `service_queries` (corpus `fru_us_1k`, `scripts/retail/sim_data/profiles/fru_us_1000_100/`).
