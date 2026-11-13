# Retail brain profile (`brain/retail`)

- **Raw sources:** `raw/sources/fridge-docs/<sku>/*.txt` — full manual text for LLM Wiki ingest (no PDFs here).
- **Archive:** `archive/fridge-docs/<sku>/*.pdf` — human reference + operator rebuild input; not Source Watch. Multilingual extracts: **`*.mul.txt`** (full PDF text); **`raw/…/*.txt`** English-only via per-manual markers in [`scripts/retail/manuals/multilingual_trim.py`](../../scripts/retail/manuals/multilingual_trim.py) (not auto-detect).
- **Wiki compile gap:** see [`docs_manual_gen/artifacts/RETAIL_LLM_WIKI_TXT_COMPILE.md`](../../docs_manual_gen/artifacts/RETAIL_LLM_WIKI_TXT_COMPILE.md) and **HG-TXT-3**.
- **Optional index:** `archive/pdf_page_index.jsonl` — page rows when `WRITE_PAGE_INDEX=1` on `scripts/retail/manuals/build_pdf_txt_and_page_idx.py` (Phase 2 page citation).
- **Answer bundle:** manual leg cites `raw_origin.doc_path` (+ optional `archive_pdf_path`); pages deferred.
