<h1 id="rrf-strip-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: retail hybrid RRF with FTS normalize + realistic deterministic seed</h1>

**Status:** **completed** (branch `feature/rrf-strip-fluff`) — Phase 5 deterministic narrative shipped  
**Parent plan:** [`REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](./REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md)  
**Execution:** **`qimpltdd`** / [`implreftdd`](../.cursor/rules/tdd/implreftdd-resumimpl-refactor-plan-followthrough.mdc)

## Document outline

1. [Problem](#1-problem)
2. [Design](#2-design)
3. [Phase 1 — text_normalize](#3-phase-1)
4. [Phase 2 — PG index + embed](#4-phase-2)
5. [Phase 3 — seed + eval (v1)](#5-phase-3)
6. [Phase 4 — tests + operator](#6-phase-4)
7. [Phase 5 — deterministic narrative seed (no ID prose)](#7-phase-5)
8. [Quality bar](#8-quality-bar)
9. [Deferred](#9-deferred)

---

<h2 id="1-problem" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Problem</h2>

Hybrid RRF was wired but (a) lexical leg was empty pre-normalize, then (b) post-shakedown **hybrid lift was inflated** by **store/case-ref tokens** in prose and eval queries copying structured IDs — not live CRM behavior.

---

<h2 id="2-design" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Design</h2>

| Layer | Choice |
|-------|--------|
| Search | Dense + normalized FTS + RRF (unchanged) |
| Seed prose | **No** `store_id`, `ticket_id`, `item_number`, or case ref in `customer_query_text` |
| Uniqueness | **`seed_narrative.py`**: 10-issue pool + seeded RNG detail slots (when/symptom/name) — **fully deterministic**, CI-safe |
| Eval queries | **`eval_query_template`** — short caller wording; **no** operational IDs |
| LLM batch enrich | **Out of scope** — determinism required for test suite |

---

<h2 id="3-phase-1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase 1 — text_normalize</h2>

**TDD mode:** strict-TDD · **Done**

- [X] `text_normalize.py`, tests, hybrid + PG wiring (see prior completion).

---

<h2 id="4-phase-2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2 — PG index + embed</h2>

**TDD mode:** strict-TDD · **Done**

- [X] `search_text`, `websearch_to_tsquery`, embed path, schema `002`.

---

<h2 id="5-phase-3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 3 — seed + eval (v1)</h2>

**Superseded by Phase 5** — store-in-prose approach reverted.

- [X] ~~store in prose for uniqueness~~ (removed in Phase 5)

---

<h2 id="6-phase-4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase 4 — tests + operator</h2>

- [X] Hybrid lexical tests, war story #4
- [X] Operator re-embed + A/B (prior cabinet; re-run after Phase 5 regen)

---

<h2 id="7-phase-5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Phase 5 — deterministic narrative seed (no ID prose)</h2>

**TDD mode:** strict-TDD

- [X] `retail_brain/seed_narrative.py` — `narrative_parts`, stored + eval formatters, `Random(seed:index)`.
- [X] `market.py` — **10** issues per market; `eval_query_template`.
- [X] `seed.py` — prose via narrative only; IDs remain CSV columns.
- [X] `eval_gen.py` — paraphrase from `(ticket_id, manifest seed)` not full-body copy.
- [X] Tests: `test_retail_seed_narrative.py`, ID-free assertions in `test_retail_seed_eval.py`.
- [X] Regenerate `seed/generated/*`, `eval/ticket_retrieval.jsonl`.
- [X] Update `docs/specs/samsung-retail-synthetic-data.md` anti-leakage + uniqueness bullets.
- [X] **Exit:** `./scripts/verify.sh` green.

---

<h2 id="8-quality-bar" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Quality bar</h2>

- Regenerated fixtures committed; pytest never calls Gemini for seed.
- Operator may re-run `03`/`04` after merge for honest hybrid metrics on new corpus.

---

<h2 id="9-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Deferred</h2>

| Item | Notes |
|------|-------|
| Cross-encoder rerank | V3 eval |
| Optional offline LLM gold (`llm_author_gold.py`) | `acceptable_ticket_ids` only — not ticket bodies |
| D6 hybrid default `1` | After scale A/B on Phase 5 corpus |
