<h1 id="pg-manual-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — unified Postgres embeddings for manual chunks (Lance A/B → cutover)</h1>

**Status:** **Complete (P1–P5)** on **`feature/evo-17-multi-embed-pg-only`** — Lane **B** manual raw RAG defaults to Postgres; **HG-PG-CUTOVER** closed 2026-10-26.  
**Execute:** **`aciubtdd`** / **`qimpltdd`** on **P5** checklist below; Lance A/B delivered on **evo-16**.  
**Branch target:** `feature/evo-17-multi-embed-pg-only` (cutover); implementation landed on **`feature/evo-16-multi-embed-unified-pg`** first.  
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
| **HG-PG-AB** | Phase **4** full M90 | Phase **3** retrieval tests green; PG ingest fresh on Lane **B** — **closed 2026-10-26** (see **U9**) |
| **HG-PG-CUTOVER** | Phase **5** Lance removal | **Approved 2026-10-26** — unify manual raw RAG to PG (Lane **B** first); execute P5 on **evo-17** |

Phase **2** ticket work on **evo-15** may continue in parallel; do **not** block on **HG-PG-CUTOVER**.

---

<h2 id="pg-manual-p0" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 0 — Align</h2>

- [X] Confirm **Lane B** only for first A/B (**R10**); C/D deferred (**U1**).
- [X] Embed model: **`text-embedding-3-small`** → **`manual_chunks.embedding vector(1536)`** (**U4**); tickets stay **768**.
- [X] Lexical default: in-process pool over PG rows (**U5**); PG `tsvector` / Tantivy deferred.
- [X] Promotion bar: operator sign-off (**U8**); reference metrics in analysis doc.

**Exit:** **Decisions** updated; **HG-PG-ALIGN** satisfied.

---

<h2 id="pg-manual-p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 1 — Schema</h2>

- [X] Add migration `scripts/retail/schema/005_manual_chunks.sql`:
  - `manual_chunks`: `chunk_id` PK, `lane_id`, `source_relpath`, `model_id`, `chunk_index`, `text`, `content_hash`, `embedding vector(N)`, `chunk_tsv tsvector`, `updated_at`.
  - Indexes: HNSW/IVFFlat on `embedding` (pgvector); GIN on `chunk_tsv`; `(lane_id, model_id)`.
- [X] Fingerprint file under lane (mirror Lance manifest); no separate manifest table.
- [X] **`pg_up_and_load.sh`** applies `005_manual_chunks.sql`; **`RETAIL_DATABASE_URL`** required.

**Exit:** Migration applies on dev PG; **`test_manual_chunks_schema.py`** green.

---

<h2 id="pg-manual-p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase 2 — Ingest</h2>

- [X] **`scripts/retail/retail_brain/manual_pg_ingest.py`**:
  - Reuse **`raw_chunking`** / **`iter_raw_source_files`** / manifest fingerprint from Lance path.
  - Batch embed via shared **`embed_texts_batch`** (same as Lance build).
  - **Upsert** by `chunk_id`; delete chunks whose files removed from manifest.
- [X] CLI: `python -m tests.retail_multi_profiles --ingest-manual-pg --lanes B`.
- [X] **neatlog:** `MANUAL_PG_INGEST` + `ingest_progress.jsonl` via `manual_pg_index_runner.py` / `--ingest-manual-pg`.
- [X] **`ensure_manual_pg_fresh(lane)`** in runner preflight (PG profiles).

**Exit:** Lane **B** — **208** `manual_chunks` operator ingest (2026-10-25); tests green.

---

<h2 id="pg-manual-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Phase 3 — Retrieval D3.PG-H</h2>

- [X] **`manual_pg_search.py`**: dense KNN + in-process lexical + **`reciprocal_rank_fusion`** + SKU filter.
- [X] **`ManualEvidenceRetriever`** `backend=lance|pg`; **`manual_d3_backend`** on resolved profile.
- [X] Parity tests: top-5 overlap vs Lance fixture (**`test_manual_pg_parity.py`**).
- [X] **`run_profiles`**: `MANUAL_B_RAW_PG_HYBRID`, `MANUAL_B_RAW_PG_HYBRID_RERANK`.

**Exit:** PG retrieval + parity pytest green; operator M90 profiles runnable.

---

<h2 id="pg-manual-p4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Phase 4 — A/B benchmark</h2>

- [X] Full **D6.M90** Lane **B**: `a2-pg-hybrid-b-v1` vs `a2-hybrid-rrf-b-v2`; `a2-pg-hybrid-rerank-b-v1` vs `a2-hybrid-rerank-b-v2`.
- [X] **latency_ms.retrieval** mean/p50/p95 logged; per-question tables in analysis doc.
- [X] **`TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`**: overlap, latency, flip cases, §2.1–2.2 answer-pipeline read for **U8**.
- [X] Ticket ladder unchanged (out of scope).

**Recorded results (Lane B, 60 answerable):**

| Arm | Lance pass | PG pass | Top‑5 Jaccard (PG vs Lance) | Mean retrieval (PG/Lance) |
|-----|------------|---------|-----------------------------|---------------------------|
| Hybrid | 34/60 | **35/60** | **1.00** all rows | ~463 / ~405 ms (~1.14× means) |
| Rerank | **37/60** | 36/60 | **1.00** sets; rank‑1 same ~83% | ~2178 / ~1968 ms (~1.11× means) |

Pass deltas are **answer/judge** on shared top‑5 sets (see analysis §2.2), not missing-chunk drift.

**Phase 4 exit (reference metrics for analysis doc — per **U8**, not automated hard gates):**

| Metric | Reference target (log in analysis) |
|--------|-----------------------------------|
| Answerable pass (60) | PG vs Lance headline; note **−1** as informal guide |
| Mean retrieval latency | PG vs Lance ratio (informal **1.25×** guide) |
| Retrieval-only top-5 overlap (fixture) | Jaccard on chunk ids (informal **0.80** guide) |

**HG-PG-AB** / **HG-PG-CUTOVER:** operator sign-off after reviewing artifact; waivers documented in **Decisions** if needed.

**Exit:** Analysis doc complete; **HG-PG-AB** closed (**U9**, 2026-10-26).

---

<h2 id="pg-manual-p5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Phase 5 — Cutover and Lance removal (evo-17)</h2>

**Operator intent:** Manual raw RAG **unifies on Postgres** for Lane **B**; Lance build/search **removed from default path** (not required for new work). C/D lanes may stay Lance until a follow-up or same pattern.

- [X] Set **`default_run_profile`** to **`MANUAL_B_RAW_PG_HYBRID_RERANK`**; Lane B profiles use **`manual_d3_backend: pg`**.
- [X] Lance gated for Lane B default (env **`RETAIL_MANUAL_D3_BACKEND=lance`**); C/D still use **`--index-raw`**.
- [X] Update **`RAW_RAG.md`**, **`RUN_PROFILES.md`**.
- [X] **`smoke-after-delete`:** `./scripts/verify.sh` green (2026-10-26).

**Exit:** Lane **B** operational path is PG-only; Lance retained for C/D and explicit legacy compare. **HG-PG-CUTOVER** closed.

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
| **U4** | **`manual_chunks.embedding vector(1536)`** — independent of ticket **`vector(768)`**; no ticket re-embed in this plan. Manual embed model stays **`text-embedding-3-small`** at native/default dims unless run-config sets **`dimensions`**. |
| **U5** | **Lexical default (P3):** in-process **BM25-ish pool** over PG-loaded chunk rows (**`raw_lexical`** parity with Lance hybrid). PG **`tsvector`** / Tantivy remain optional **Phase 4** compare arms, not P3 blocker. |
| **U6** | **Parallel track:** May **`qimpltdd`** this plan on **evo-16** while **evo-15** finishes Phase **2** P2.6. |
| **U7** | **Phase 4 M90 profiles:** two PG runs — **`MANUAL_B_RAW_PG_HYBRID`** + **`MANUAL_B_RAW_PG_HYBRID_RERANK`** vs Lance **`MANUAL_B_RAW_HYBRID_RERANK`** baseline (same D5 stack on rerank profile). |
| **U8** | **Promotion bar:** **operator sign-off** at **HG-PG-AB** / **HG-PG-CUTOVER** after **`TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`** logs pass rates, latency, and retrieval overlap — **no fixed numeric hard gate** in automation (Phase 4 exit table = **reference targets** for the doc, not CI fail). |
| **U9** | **2026-10-26 cutover approval:** Operator accepts **PG-only** manual D3 for Lane **B** — top‑5 retrieval parity **1.00**, latency within informal **1.25×** guide, hybrid **+1** / rerank **−1** acceptable vs Lance. **HG-PG-AB** closed; **HG-PG-CUTOVER** authorized — implement **P5** on **`feature/evo-17-multi-embed-pg-only`**. |

**last_aligned:** 2026-10-26 — **U9** operator PG-only approval; **evo-17** owns P5.

### Decisions (Phase 0 grill)

| MC | Choice | Rationale |
|----|--------|-----------|
| **U4** | **A** | Smallest blast radius; manuals and tickets stay separate vector columns/dims. |
| **U5** | **B** | Matches current Lance hybrid lexical behavior before experimenting with PG-native search. |
| **P4 scope** | **Two profiles** | Fair compare to Lance hybrid vs hybrid+rerank without lexical sweep cost up front. |
| **P0.2 bar** | **Operator** | Human reads analysis artifact; avoids false CI blocks while still logging default reference metrics. |

### Decisions (cutover — 2026-10-26)

| MC | Choice | Rationale |
|----|--------|-----------|
| **U9 / HG-PG-AB** | **Approve PG A/B** | Analysis shows top‑5 Jaccard **1.00**, latency within guide; pass deltas explained as ordering/LLM/judge on shared evidence. |
| **HG-PG-CUTOVER** | **Approve PG-only (Lane B)** | Unify manual raw RAG on Postgres; **P5** on **evo-17** removes Lance from default path. |

---

<h2 id="pg-manual-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. Execution checklist</h2>

**Phase 0 — Align**

- [X] P0.1 Decisions **U4**, **U5**, **U7**, **U8** closed (2026-10-25 grill)
- [X] P0.2 Promotion bar confirmed (**U8** operator sign-off)

**Phase 1 — Schema**

- [X] P1.1 Migration `005_manual_chunks.sql`
- [X] P1.2 Schema tests

**Phase 2 — Ingest**

- [X] P2.1 Ingest module + manifest parity
- [X] P2.2 CLI (`--ingest-manual-pg`) + neatlog (**P5**)
- [X] P2.3 `ensure_manual_pg_fresh` in runner

**Phase 3 — Retrieval**

- [X] P3.1 `manual_pg_search` + RRF
- [X] P3.2 Profiles + retriever backend flag
- [X] P3.3 Parity tests vs Lance

**Phase 4 — A/B**

- [X] P4.1 Full M90 PG vs Lance runs (2026-10-25: `a2-pg-hybrid-b-v1`, `a2-pg-hybrid-rerank-b-v1`)
- [X] P4.2 `TEST_ANALYSIS_A2_MANUAL_RAG_PG.md` (overlap, latency tickets, flip tables, §2.1–2.2)
- [X] P4.3 **HG-PG-AB** sign-off (**U9**, 2026-10-26)

**Phase 5 — Cutover (evo-17)**

- [X] P5.1 Default profile **`MANUAL_B_RAW_PG_HYBRID_RERANK`**; Lane B **`MANUAL_B_RAW_HYBRID*`** → **`manual_d3_backend: pg`**; docs updated
- [X] P5.2 Lane B default harness uses PG preflight (Lance only via **`RETAIL_MANUAL_D3_BACKEND=lance`** or `--index-raw` on C/D)
- [X] P5.3 **HG-PG-CUTOVER** closed — `./scripts/verify.sh` green (2026-10-26)

---

<h2 id="pg-manual-related" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. Related</h2>

| Link | Role |
|------|------|
| [`REFACTOR_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_FURTHER_ENHANCEMENT_GPT.md) | Parent phases; Phase **1** Lance baseline |
| [`TEST_ANALYSIS_A2_MANUAL_RAG.md`](../../artifacts/TEST_ANALYSIS_A2_MANUAL_RAG.md) | Lance M90 promotion numbers |
| [`TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`](../../artifacts/TEST_ANALYSIS_A2_MANUAL_RAG_PG.md) | PG vs Lance A/B + **U8** / **U9** sign-off read |
| [`_build_pg_vs_lance_flip_tables.py`](../../artifacts/_build_pg_vs_lance_flip_tables.py) | Regenerate PG analysis artifact |
| [`REALIGNMENT_DIMENSIONS.md`](../../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md) | D3 / D4 vocabulary |
| `tests/retail_multi_profiles/lib/raw_rag_index.py` | Lance freshness reference |
| `scripts/retail/schema/001_retail.sql` | Ticket pgvector schema |
| [`RUN_PROFILES.md`](../../../tests/retail_multi_profiles/docs/RUN_PROFILES.md) | Profile SSOT |

**Execution boundary:** Plan authored per **onlyref**; implement with **`aciubtdd`** on this path (**onlyreftdd** chain).
