<h1 id="pg-manual-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — unified Postgres embeddings for manual chunks (Lance A/B → cutover)</h1>

**Status:** **new** — plan-only (**onlyref** / **onlyreftdd**); no implementation on this file until **`qimpltdd`** / **`aciubtdd`**.  
**Execute:** **`qimpltdd docs_manual_gen/ref_plan/new/REFACTOR_UNIFIED_PG_MANUAL_EMBEDDINGS.md`** after **Decisions** aligned.  
**Branch target:** `feature/evo-16-multi-embed-unified-pg` (isolated from Phase 2 ticket work on **evo-15**).  
**Parent context:** [`REFACTOR_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_FURTHER_ENHANCEMENT_GPT.md) Phase **1** (Lance D3.R-H today); does **not** replace Phase **2** A3 ticket adapters.

**Problem:** Manual raw RAG stores **chunk text + vectors** in **Lance** under `brain/<lane>/.retail-raw-rag/`; tickets store **embeddings in Postgres** (`service_queries.query_embedding`). Ops wants **one always-on PG** stack and optional **shared embed pipeline**, with **A/B** against Lance before removal.

**Non-goals (this plan):** Unifying **ticket** hybrid search logic (already PG); COS; outcome-memory loop; replacing **LLM Wiki** track.

<h2 id="pg-manual-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Current Lance sync (baseline)](#pg-manual-lance-sync) — when rebuild runs.
2. [Target architecture](#pg-manual-target) — PG manual chunks + parity with tickets.
3. [Human gates](#pg-manual-gates) — promotion vs Lance.
4. [Phase 0 — Align](#pg-manual-p0) — decisions + embed dimension.
5. [Phase 1 — Schema](#pg-manual-p1) — `manual_chunks` + migrations.
6. [Phase 2 — Ingest](#pg-manual-p2) — file → chunk → embed → PG.
7. [Phase 3 — Retrieval D3.PG-H](#pg-manual-p3) — vector + lexical + RRF.
8. [Phase 4 — A/B benchmark](#pg-manual-p4) — M90 + latency vs Lance.
9. [Phase 5 — Cutover and Lance removal](#pg-manual-p5) — default profile + delete path.
10. [TDD bar](#pg-manual-tdd) — strict-TDD / smoke-after-delete per phase.
11. [Decisions](#pg-manual-decisions) — pre-fill + align before code.
12. [Execution checklist](#pg-manual-checklist) — `[ ]` / `[X]` ledger.
13. [Related](#pg-manual-related).

---

<h2 id="pg-manual-lance-sync" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Current Lance sync (baseline)</h2>

Manual index freshness today (`tests/retail_multi_profiles/lib/raw_rag_index.py`):

- **When:** Before each **raw_rag** harness run (`ensure_index_fresh` in runner); or **`--index-raw`** / **`--force-reindex`**.
- **How:** Re-scan lane raw glob → **manifest** (path, **SHA-256**, mtime, size) → **fingerprint** compared to `index_meta.json` + **chunk policy** + **embed model id**.
- **On drift:** Full **re-chunk → re-embed → replace Lance table** (not incremental per file).

**PG ingest must mirror:** same manifest/fingerprint semantics; stale → rebuild lane rows (full or upsert-by-`chunk_id` — see Phase 2).

---

<h2 id="pg-manual-target" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Target architecture</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Corpus</th><th>Dense store</th><th>Lexical (A/B)</th><th>Hybrid fuse</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Tickets (unchanged D3)</strong></td><td><code>service_queries.query_embedding</code></td><td>Tantivy / existing</td><td><code>pg_search</code> + <code>rrf.py</code></td></tr>
<tr><td style="background:#e8f5e9"><strong>Manuals (new D3.PG-H)</strong></td><td><code>manual_chunks.embedding</code></td><td>PG <code>tsvector</code> **or** sidecar Tantivy (A/B)</td><td>Same <code>rrf.py</code> weights as Lance hybrid</td></tr>
<tr><td style="background:#fff3e0"><strong>Lance (legacy until P5)</strong></td><td><code>.retail-raw-rag/lancedb</code></td><td>In-memory over Lance rows</td><td><code>raw_hybrid_search.py</code></td></tr>
</tbody>
</table>

**Shared:** embed batch helper, **RRF** math, **D5** stack (`rerank_registry`), **EvidencePackage** shape. **Not shared:** D3 candidate generation implementation until cutover.

**Run profile (Phase 4+):** add e.g. **`MANUAL_B_RAW_PG_HYBRID`** vs existing **`MANUAL_B_RAW_HYBRID`** (Lance) for fair **D6.M90** compare (fix D5 + D2.B; sweep D3 only).

---

<h2 id="pg-manual-gates" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Human gates</h2>

| Gate | Starts | Condition |
|------|--------|-----------|
| **HG-PG-ALIGN** | Phase **1** schema | **Decisions** embed dimension + lexical arm chosen (section 11) |
| **HG-PG-AB** | Phase **4** full M90 | Phase **3** retrieval tests green; PG ingest fresh on Lane **B** |
| **HG-PG-CUTOVER** | Phase **5** Lance removal | Phase **4** exit met (section 4 exit table) + operator sign-off |

Phase **2** ticket work on **evo-15** may continue in parallel; do **not** block on **HG-PG-CUTOVER**.

---

<h2 id="pg-manual-p0" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 0 — Align</h2>

- [ ] Confirm **Lane B** only for first A/B (**R10**); C/D deferred.
- [ ] Record **embed model** for manuals (today: `text-embedding-3-small` in run-config) vs tickets (**768-dim** in `001_retail.sql` — **dimension mismatch** must be resolved: separate columns, re-embed tickets, or manual-only table with native dims).
- [ ] Pick **lexical A/B arms** for Phase 4: (A) PG `tsvector`, (B) existing in-process BM25 over chunk pool, (C) optional Tantivy manual index.
- [ ] Define **promotion bar** (section 8 exit) in **Decisions**.

**Exit:** **Decisions** updated; **HG-PG-ALIGN** satisfied.

---

<h2 id="pg-manual-p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 1 — Schema</h2>

- [ ] Add migration `scripts/retail/schema/005_manual_chunks.sql` (name tentative):
  - `manual_chunks`: `chunk_id` PK, `lane_id`, `source_relpath`, `model_id`, `chunk_index`, `text`, `content_hash`, `embedding vector(N)`, `chunk_tsv tsvector`, `updated_at`.
  - Indexes: HNSW/IVFFlat on `embedding` (pgvector); GIN on `chunk_tsv`; `(lane_id, model_id)`.
- [ ] Optional `manual_ingest_manifest` table or reuse JSON fingerprint file under `ops/` (mirror Lance manifest).
- [ ] Document **`RETAIL_DATABASE_URL`** requirement for manual PG path (same as tickets).

**Exit:** Migration applies on dev PG; unit test loads empty table.

---

<h2 id="pg-manual-p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase 2 — Ingest</h2>

- [ ] **`scripts/retail/retail_brain/manual_pg_ingest.py`** (or under `tests/retail_multi_profiles/lib/` if harness-coupled):
  - Reuse **`raw_chunking`** / **`iter_raw_source_files`** / manifest fingerprint from Lance path.
  - Batch embed via shared **`embed_texts_batch`** (same as Lance build).
  - **Upsert** by `chunk_id`; delete chunks whose files removed from manifest.
- [ ] CLI: `python -m tests.retail_multi_profiles --ingest-manual-pg --lanes B` (or sibling retail CLI).
- [ ] **neatlog:** `MANUAL_PG_INGEST` + `ingest_progress.jsonl` per **§17.6** pattern in parent plan.
- [ ] **`ensure_manual_pg_fresh(lane)`** — same trigger points as `ensure_index_fresh` (runner preflight).

**Exit:** Lane **B** ingested; row count ≈ Lance chunk count on fixture corpus; fingerprint stale triggers rebuild.

---

<h2 id="pg-manual-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Phase 3 — Retrieval D3.PG-H</h2>

- [ ] **`manual_pg_search.py`**: dense KNN on `manual_chunks`; lexical leg per Phase 0 choice; fuse with **`reciprocal_rank_fusion`** + SKU filter (**reuse `sku_scope`**).
- [ ] **`ManualPgEvidenceRetriever`** or extend **`ManualEvidenceRetriever`** with `backend=lance|pg` flag — runner/profile selects backend.
- [ ] Parity **retrieval-only** tests: same query → top-5 **chunk_id** overlap ≥ **X%** vs Lance on **frozen fixture index** (not full LLM judge).
- [ ] Wire **`run_profiles`**: `MANUAL_B_RAW_PG_HYBRID` (D5.0), optional `MANUAL_B_RAW_PG_HYBRID_RERANK` (D5.R+V+A).

**Exit:** `pytest` PG retrieval + parity module green; smoke harness row with `--profile MANUAL_B_RAW_PG_HYBRID`.

---

<h2 id="pg-manual-p4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Phase 4 — A/B benchmark</h2>

- [ ] Full **D6.M90** Lane **B**: Lance **`MANUAL_B_RAW_HYBRID_RERANK`** (baseline) vs PG profile(s).
- [ ] Log **latency_ms** retrieval mean/p95 (same as **R14** style).
- [ ] **`TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`** (new artifact): headline pass rates + lexical arm notes.
- [ ] **`check_abc_ladder.py`** unchanged (ticket regression).

**Phase 4 exit (promotion bar — default proposal):**

| Metric | Accept PG cutover |
|--------|-------------------|
| Answerable pass (60) | PG ≥ Lance **−1** (same judge suite) |
| Mean retrieval latency | PG ≤ Lance × **1.25** |
| Retrieval-only top-5 overlap (fixture) | ≥ **0.80** Jaccard on chunk ids |

Waivers require row in **Decisions** + **HG-PG-AB** note.

**Exit:** Analysis doc complete; **HG-PG-AB** human review for cutover.

---

<h2 id="pg-manual-p5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Phase 5 — Cutover and Lance removal</h2>

- [ ] Set **`default_run_profile`** or document PG as default only if **HG-PG-CUTOVER** signed.
- [ ] Remove **`lancedb`** dependency from default verify path; delete or gate **`raw_rag_index`** Lance build behind feature flag until final deletion.
- [ ] Update **`RAW_RAG.md`**, **`RUN_PROFILES.md`**, parent plan **Deferred** row.
- [ ] **`smoke-after-delete`:** no imports of `lancedb` in harness default; `./scripts/verify.sh` green.

**Exit:** Lance code path removed; PG ingest + search sole manual D3; **HG-PG-CUTOVER** closed.

---

<h2 id="pg-manual-tdd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. TDD bar</h2>

| Phase | TDD mode | Test-first artifact | Red case | Green gate |
|-------|----------|---------------------|----------|------------|
| **P1** schema | strict-TDD | `tests/retail/test_manual_chunks_schema.py` | migration missing table | pytest schema test |
| **P2** ingest | strict-TDD | `tests/retail/test_manual_pg_ingest.py` | fingerprint change → row count updates | ingest tests + manifest fixture |
| **P3** retrieval | strict-TDD | `tests/retail/test_manual_pg_search.py` + extend `test_raw_hybrid_search.py` parity | PG top-K empty while Lance hits | pytest retrieval + parity |
| **P4** operator | smoke-after-delete | analysis doc + existing M90 harness | N/A | smoke PG profile + optional full M90 |
| **P5** Lance removal | smoke-after-delete | `./scripts/verify.sh` | import lancedb in default path | full verify green |

---

<h2 id="pg-manual-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Decisions</h2>

| ID | Decision |
|----|----------|
| **U1** | **Scope:** Lane **B** first; ticket D3 unchanged; shared **embed job code** only. |
| **U2** | **Sync semantics:** Match Lance — manifest fingerprint + full-lane rebuild on drift (incremental upsert OK if idempotent by `chunk_id`). |
| **U3** | **A/B required** before Lance removal; promotion bar = Phase **4** exit table unless revised at **HG-PG-AB**. |
| **U4** | **Embed dimension:** **OPEN — align Phase 0.** Tickets use **768**; OpenAI manual embed may be **1536**. Options: (a) `manual_chunks.embedding vector(1536)` independent of tickets; (b) re-embed all tickets to 1536; (c) dual models documented — **pick one before P1**. |
| **U5** | **Lexical default for PG hybrid:** **OPEN — align Phase 0** (PG tsvector vs scan pool vs Tantivy manual). |
| **U6** | **Parallel track:** May **`qimpltdd`** this plan on **evo-16** while **evo-15** finishes Phase **2** P2.6. |

**last_aligned:** _pending Phase 0 grill_

---

<h2 id="pg-manual-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. Execution checklist</h2>

**Phase 0 — Align**

- [ ] P0.1 Decisions **U4**, **U5** closed
- [ ] P0.2 Promotion bar confirmed

**Phase 1 — Schema**

- [ ] P1.1 Migration `005_manual_chunks.sql`
- [ ] P1.2 Schema tests

**Phase 2 — Ingest**

- [ ] P2.1 Ingest module + manifest parity
- [ ] P2.2 CLI + neatlog
- [ ] P2.3 `ensure_manual_pg_fresh` in runner

**Phase 3 — Retrieval**

- [ ] P3.1 `manual_pg_search` + RRF
- [ ] P3.2 Profiles + retriever backend flag
- [ ] P3.3 Parity tests vs Lance

**Phase 4 — A/B**

- [ ] P4.1 Full M90 PG vs Lance runs
- [ ] P4.2 `TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`
- [ ] P4.3 **HG-PG-AB** sign-off

**Phase 5 — Cutover**

- [ ] P5.1 Default profile / docs
- [ ] P5.2 Lance removal
- [ ] P5.3 **HG-PG-CUTOVER**

---

<h2 id="pg-manual-related" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. Related</h2>

| Link | Role |
|------|------|
| [`REFACTOR_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_FURTHER_ENHANCEMENT_GPT.md) | Parent phases; Phase **1** Lance baseline |
| [`TEST_ANALYSIS_A2_MANUAL_RAG.md`](../../artifacts/TEST_ANALYSIS_A2_MANUAL_RAG.md) | Lance M90 promotion numbers |
| [`REALIGNMENT_DIMENSIONS.md`](../../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md) | D3 / D4 vocabulary |
| `tests/retail_multi_profiles/lib/raw_rag_index.py` | Lance freshness reference |
| `scripts/retail/schema/001_retail.sql` | Ticket pgvector schema |
| [`RUN_PROFILES.md`](../../../tests/retail_multi_profiles/docs/RUN_PROFILES.md) | Profile SSOT |

**Execution boundary:** Plan authored per **onlyref**; implement with **`aciubtdd`** on this path (**onlyreftdd** chain).
