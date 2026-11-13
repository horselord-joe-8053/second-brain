<h1 id="ref-xenc-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">REFACTOR — manual rerank probe (cross-encoder vs listwise)</h1>

**Status:** `completed` · Executed with **`qimpltdd`** (chain 2: **`aciubtdd`** / **`implreftdd`**) on 2026-10-30.

**Repo plan home:** `docs_manual_gen/ref_plan/new/` (this repo’s redirect from `cursor_gen/refactor_plans/`).

## Document outline

1. [Goal](#ref-xenc-goal) — two arms, one baseline.
2. [Evidence](#ref-xenc-evidence) — why both arms see 20.
3. [Decisions](#ref-xenc-decisions) — locks for qimpltdd.
4. [Phases](#ref-xenc-phases) — checklist.
5. [Quality bar](#ref-xenc-quality) — TDD per phase.
6. [Metrics](#ref-xenc-metrics) — what each step records.
7. [Exit](#ref-xenc-exit) — done when.
8. [Deferred](#ref-xenc-deferred) — out of this probe.

---

<h2 id="ref-xenc-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Two new bundled rows, same customer question and gold as **BND-H10N-alt**. Each row reranks the manual leg a different way. **BND-H10N-alt** stays the baseline (hybrid top 5, no manual rerank) and is not edited.

Both arms, per decomposed manual subquery (D7 unit):

1. Hybrid candidate list of **20**.
2. Rerank that list.
3. Keep **top 2 per subquery** (D9; the first probe kept 5) and append those lists in subquery order. Manual answer text budget is **10000** characters. Do not fuse those lists back down to one global top 5.

| Row id | Rerank |
|--------|--------|
| **BND-H10N-alt-rr-xenc** | Local cross-encoder. Question and one chunk scored as a pair. |
| **BND-H10N-alt-rr-llm** | Existing listwise chat call (`llm_listwise`), shown the 20 chunks in one prompt. |

Ticket leg stays mode C plus PFDA listwise. This probe does not change ticket retrieval.

Shared scorer home: `scripts/retail/retail_brain/rerank.py` (`cross_encoder_rerank` beside `listwise_rerank`). Switch: `scripts/retail/retail_brain/rerank_registry.py` `build_rank_fn`. Call site: `tests/retail_multi_profiles/lib/bundled_runner.py`, only when the row’s fixture field is set.

---

<h2 id="ref-xenc-evidence" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Evidence</h2>

Query (unit 2 of **BND-H10N-alt**), model filter Samsung **RF28K9070SG**, embedding `text-embedding-3-small`, stack `page_heading` + `page_top5` + Tantivy. Gold chunk `53d849bffff6d4707598cf57df1aa251` (`user-guide.md`, heading `## PDF page 27`):

| Leg | Rank of gold chunk |
|-----|---------------------|
| Keyword (top 20) | 7, still present after `page_top5` |
| Vector (top 20) | 20, dropped by `page_top5` |
| Fused hybrid, `top_k=20` | **12** |
| Fused hybrid, `top_k=5` (production) | absent |

Baseline fail: `ops/runs/retail-bundled-qa/b20-evo18-d7-v3-alt-query-20261029/` row **BND-H10N-alt**. Judge FAIL. Page 27 not in unit-2 top 5 and not in the merged manual list.

Bundled manuals do not call listwise today. Profile `MANUAL_B_RAW_PG_HYBRID` has D5 rerank off. When D5 is on, `evidence/retriever.py` calls `listwise_rerank` only after hybrid already cut to `top_k` (5). Ticket PFDA already uses `llm_listwise` on the ticket pool. `cross_encoder` is named in config and `assert_rerank_preflight` raises.

---

<h2 id="ref-xenc-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Decisions</h2>

**Grill:** skipped. The user named both ids, both methods, the baseline row, the section 8 matrix, and step metrics in one message.

**last_aligned:** 2026-10-30.

| ID | Choice |
|----|--------|
| D1 | New ids **`BND-H10N-alt-rr-xenc`** and **`BND-H10N-alt-rr-llm`**. Same `question`, `answer`, `expected_ticket_ids` (`T-0042-100132`), `manual_anchor_question_id` (`samsung_RF28K9070SG-E01`), model, and `difficulty: hard` as **BND-H10N-alt**. Question text equals **BND-H10N-alt**, not **BND-H10**. |
| D2 | Dispatch is a fixture field **`manual_rerank`**: `cross_encoder` or `llm_listwise`. Absent on every other row, including **BND-H10N-alt**. No global env that would rerank the whole TYPE_B_B20 suite. Profile `MANUAL_B_RAW_PG_HYBRID` stays rerank-off. |
| D3 | Both arms use the same pool: hybrid **`top_k=20`** per manual unit, rerank, keep **5 per unit**, union into the answer packet (dedupe by `chunk_id`, unit order). Do not call `merge_manual_chunk_rows(..., top_k=5)` when the field is set. |
| D4 | Cross-encoder model **`cross-encoder/ms-marco-MiniLM-L-6-v2`**, in the `./scripts/py` process, CPU. No new Docker service. `scripts/retail/docker-compose.yml` stays Postgres only. |
| D5 | Listwise arm calls the existing `build_rank_fn("llm_listwise")` path (default chat model `gpt-4o-mini`). Snippet cap stays **500** characters so the arm is the current call, shown 20 rows. |
| D6 | Unit tests inject a fake scorer / fake `rank_fn`. They must not download weights or call the chat API. |
| D7 | Baseline numbers come from the existing **BND-H10N-alt** JSONL plus the fused rank **12** already measured. Do not re-run **BND-H10N-alt**. |
| D8 | Success is the comparison record, not a required judge pass. Each arm records whether gold entered unit-2 top 5 and the answer packet. |
| D9 | Follow-up 2026-10-30. D3’s keep-5 packet crowded subquery 2 out of the 8000-character copy. Probe rows now keep **2** reranked chunks per subquery, append them in subquery order, and use a **10000**-character manual budget. Other TYPE_B_B20 rows stay at 5 and 8000. |

---

<h2 id="ref-xenc-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phases</h2>

### 4.1 Phase P1 — fixture

- [X] Add both rows to `tests/retail_multi_profiles/data/retail-bundled-qa-b20.json` (copy of **BND-H10N-alt** plus `manual_rerank`).
- [X] Extend `tests/retail_multi_profiles/test_bundled_qa_suite.py`: count **26**, **12 easy / 14 hard**; parent-gold parity vs **BND-H10**; both new questions **equal** **BND-H10N-alt**’s question; `manual_rerank` values as in D2.
- [X] **Exit:** `./scripts/py -m pytest tests/retail_multi_profiles/test_bundled_qa_suite.py -q`

### 4.2 Phase P2 — rerank on the manual subquery pool

Touch `scripts/retail/retail_brain/rerank.py`, `scripts/retail/retail_brain/rerank_registry.py`, `tests/retail_multi_profiles/lib/bundled_runner.py`. `assert_rerank_preflight` in `tests/retail_multi_profiles/lib/resolved_run_profile.py` must allow `cross_encoder` when this probe loads the model id in D4. Default TYPE_B_B20 profiles still do not select that backend.

- [X] `cross_encoder_rerank(query, candidates, score_fn)` in `rerank.py`. Registry `build_rank_fn("cross_encoder")` loads **`cross-encoder/ms-marco-MiniLM-L-6-v2`** only for a real operator call.
- [X] When `manual_rerank` is set: per D7 manual unit, hybrid **`top_k=20`**, rerank with that row’s backend, keep **2** (D9). Append per-unit tops into the answer packet with a **10000**-character budget. Skip `merge_manual_chunk_rows(..., top_k=5)`.
- [X] When `manual_rerank` is absent: today’s retrieve-5 and `merge_manual_chunk_rows` path, unchanged.
- [X] Trace on each manual unit (both arms): `rerank_backend`, `rerank_model`, `candidate_count`, `rerank_ms`, `pre_rerank_chunk_ids` (the 20), `post_rerank_chunk_ids` (the 5). Row keeps existing `manual_retrieval_ms`, `answer_ms`, `judge_ms`.
- [X] **cdcm:** one doc line on each new function. File header on `rerank.py` already states listwise; extend it to name the cross-encoder helper.
- [X] **Exit:** pytest on the new test module (see Quality bar). No network, no weight download.

### 4.3 Phase P3 — operator slice

- [X] If `sentence_transformers` is missing from `./scripts/py`, install it there before the run. Expect a PyTorch download (hundreds of MB) and about 1 GB RAM while the MiniLM weights are loaded. First cross-encoder call downloads about 80 MB of weights.
- [X] Same env as the droptech full run: `set -a && source .env && set +a`, `PYTHONPATH=$PWD/scripts/retail:$PWD`, `RETAIL_D7=decompose`, `RETAIL_MANUAL_D2_CHUNK=page_heading`, `RETAIL_D2_PAGE_PACK=page_top5`, `RETAIL_LEXICAL_BACKEND=tantivy`, `RETAIL_SIM_DATA_PROFILE=fru_us_1k`, profile `MANUAL_B_RAW_PG_HYBRID`. No extra rerank env. The fixture field selects the arm.
- [X] `./scripts/py tests/retail_multi_profiles/run_bundled_qa.py --question-ids BND-H10N-alt-rr-xenc,BND-H10N-alt-rr-llm --run-id b20-manual-rr-compare-YYb20-manual-rr-compare-YYYYMMDDPG_HYBRID`
- [X] **neatlog:** one progress line per row with backend, `rerank_ms`, and candidate count. `NEAT_LOGGER_DEBUG` may dump the id lists; the JSONL trace is the record that analysis reads.
- [X] **Exit:** JSONL under `ops/runs/retail-bundled-qa/b20-manual-rr-compare-YYYYMMDD/`. Both rows b20-manual-rr-compare-YYYYMMDDnalysis

- [X] Add two rows to the section 8 profile matrix in `docs_manual_gen/artifacts/TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md` (`#bnd-evo18`). Profile cells are exactly **`BND-H10N-alt-rr-xenc`** and **`BND-H10N-alt-rr-llm`**. Do not replace existing rows, including the **BND-H10N-alt** alt-query row.
- [X] Add **section 8.7** after section 8.6. One comparison table of **BND-H10N-alt**, **BND-H10N-alt-rr-xenc**, and **BND-H10N-alt-rr-llm** using the metric rows in section 6 below. Update the document outline with `8.7`.
- [X] Do not replace section 8.3 or section 8.5.
- [X] **Exit:** matrix has both ids; section 8.7 names the run id, judge result, gold-chunk result, and the step timings.

---

<h2 id="ref-xenc-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Quality bar</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Phase</th><th>TDD mode</th><th>Test-first artifact</th><th>Red case</th><th>Green gate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">P1 fixture</td><td style="background:#e8f5e9">strict-TDD</td><td><code>test_bundled_qa_suite.py</code> count 26 and question-equality for the two new ids</td><td style="background:#fff3e0">Count is still 24, so the new assertion fails before the JSON rows exist</td><td><code>pytest tests/retail_multi_profiles/test_bundled_qa_suite.py -q</code></td></tr>
<tr><td style="background:#e3f2fd">P2 rerank</td><td style="background:#e8f5e9">strict-TDD</td><td>New module <code>tests/retail/test_manual_rerank_probe.py</code>: fake cross-encoder promotes the id at position 12 into the top 5; fake listwise <code>rank_fn</code> does the same; a row with no <code>manual_rerank</code> still merges with <code>top_k=5</code></td><td style="background:#fff3e0">Those tests fail while <code>cross_encoder_rerank</code> and the fixture branch are absent</td><td><code>pytest tests/retail/test_manual_rerank_probe.py -q</code></td></tr>
<tr><td style="background:#e3f2fd">P3 operator</td><td style="background:#fff8e1">smoke-after-delete</td><td>JSONL for both question ids</td><td style="background:#fff8e1">No red-first test; the run is the smoke</td><td>Both rows in <code>results.jsonl</code> with <code>pre_rerank_chunk_ids</code> and <code>rerank_ms</code></td></tr>
<tr><td style="background:#e3f2fd">P4 analysis</td><td style="background:#fff8e1">smoke-after-delete</td><td>Section 8 matrix plus section 8.7</td><td style="background:#fff8e1">Docs only</td><td>Both ids appear in the section 8 table and in section 8.7</td></tr>
</tbody>
</table>

Comments: **cdcm** one-liners on new callables. No comment-only sweep of unrelated rerank helpers.

---

<h2 id="ref-xenc-metrics" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Metrics</h2>

Section 8.7 rows. Baseline column is **BND-H10N-alt** from `b20-evo18-d7-v3-alt-query-20261029` (no rerank, so rerank cells b20-evo18-d7-v3-alt-query-20261029ookup: `53d849bffff6d4707598cf57df1aa251`.

| Step | What to write |
|------|----------------|
| Unit-2 candidate depth | 5 on the baseline, 20 on both arms |
| Unit-2 gold fused rank before the keep-5 cut | 12 on the baseline (absent from the 5). Arms: index in `pre_rerank_chunk_ids`, or absent |
| Rerank model | blank / `cross-encoder/ms-marco-MiniLM-L-6-v2` / `gpt-4o-mini` (or the resolved chat model if the env overrides it) |
| Unit-2 rerank ms | `rerank_ms` on that unit. Also the other unit’s `rerank_ms` |
| Unit-2 gold rank after rerank | Index in `post_rerank_chunk_ids`, or absent |
| Gold in unit-2 top 5 | yes / no |
| Gold chunk id in the text passed to the answer model | yes / no |
| `50` and `110` in `manual_leg_context` | yes / no |
| Judge | pass / fail |
| Timing | `manual_retrieval_ms` / `answer_ms` / `judge_ms`, plus sum of per-unit `rerank_ms` |
| Ticket top-2 | ids actually returned (expected label `T-0042-100132` may still be absent) |

Record the same gold-in-top-5 fact for unit 1 so a hum/level chunk is not mistaken for the page-27 hit.

---

<h2 id="ref-xenc-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Exit</h2>

Both probe rows exist. Default **BND-H10N-alt** behavior is unchanged. One operator run has both arms. Section 8 names **BND-H10N-alt-rr-xenc** and **BND-H10N-alt-rr-llm**. Section 8.7 compares them with **BND-H10N-alt** on gold survival and the timings above.

---

<h2 id="ref-xenc-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Deferred</h2>

| Item | Why deferred |
|------|----------------|
| Full TYPE_B_B20 rerun with either reranker | Two-row probe first |
| Docker sidecar for the cross-encoder | Same CPU job as in-process; compose stays Postgres |
| Larger reranker (`BAAI/bge-reranker-base`) | Only if MiniLM leaves page 27 outside unit-2 top 5 |
| Turning either backend on for TYPE_A_M90 or ticket D5 | Different pools; tickets already use listwise |
| Raising the listwise snippet cap above 500 | This arm measures the current call |
| Frequent-Q&A cache | Separate later dimension |
| Re-embed with a contextual prefix | Index change, not this probe |
