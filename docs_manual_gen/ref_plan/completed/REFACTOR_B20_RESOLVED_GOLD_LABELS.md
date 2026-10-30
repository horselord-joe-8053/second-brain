<h1 id="b20-gold-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — B20 resolved retrieval gold (align labels with ticket leg)</h1>

**Plan role:** **minor** (child).  
**Parent (only):** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) — **M4** bundled Q&amp;A.  
**Related:** [`REFACTOR_BUNDLED_MANUAL_TICKET_QA.md`](./REFACTOR_BUNDLED_MANUAL_TICKET_QA.md), [`REFACTOR_EVO18_MULTI_VARIOUS_NEW_COMBOS.md`](./REFACTOR_EVO18_MULTI_VARIOUS_NEW_COMBOS.md) (**D7 v3** operator row).  
**Branch context:** `feature/evo-18-multi-various-new-combos`.  
**Status:** **completed** — **`qimpltdd`** 2026-10-28.  
**Execute with:** **`aciubtdd`** on this path (TDD chain 2).

**Problem:** Six B20 rows label **`expected_ticket_ids`** that are **`open`** in `service_queries` while **`ticket_leg`** searches **`status = resolved` only** — strict top-2 metrics are impossible on those rows (e.g. **BND-H10** / `T-0042-100010`).

**Goal:** Retrieval gold ∈ resolved pool (same as T100 generator); optional **`provenance_ticket_ids`** preserves narrative source row; re-run **EVO18-D7 v3** B20 only; refresh §8 metrics.

<h2 id="b20-gold-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Decisions](#b20-gold-decisions) — label mapping and scope.
2. [Phase P1 — Contract tests](#b20-gold-p1) — CSV + optional PG gate.
3. [Phase P2 — Fixture + loader](#b20-gold-p2) — B20 JSON + types.
4. [Phase P3 — Operator + analysis](#b20-gold-p3) — D7 v3 rerun only.
5. [TDD bar](#b20-gold-tdd) — strict vs smoke.
6. [Quality bar](#b20-gold-quality) — cdcm, neatlog.
7. [Execution checklist](#b20-gold-checklist).

---

<h2 id="b20-gold-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decisions</h2>

| ID | Decision |
|----|----------|
| **G1** | **`expected_ticket_ids[0]`** = **resolved** ticket id searchable under mode C (same `resolution_text` as provenance row). |
| **G2** | **`provenance_ticket_ids`** (optional, parallel tuple) = original open id used when authoring gold **answer** text — logged in JSONL metadata only. |
| **G3** | **Do not** widen search to `open` tickets. |
| **G4** | Operator rerun: **full B20** + **customer six** under **EVO18-D7 v3** env only (`RETAIL_D7=decompose`, D2-PACK-PAGE stack). Run-id suffix **`b20-evo18-d7-v3-goldfix-YYYYMMDD`**. |
| **G5** | T100 unchanged (already `_resolved` pool). |

**Label mapping (locked):**

| Row | Provenance (open) | New retrieval gold (resolved) |
|-----|-------------------|----------------------------------|
| BND-E07, BND-H07 | `T-0042-100002` | `T-0042-100018` |
| BND-E08, BND-H08 | `T-0042-100004` | `T-0042-100026` |
| BND-E10, BND-H10 | `T-0042-100010` | `T-0042-100132` |

---

<h2 id="b20-gold-p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase P1 — Contract tests</h2>

- [X] Add `tests/retail_multi_profiles/lib/bundled_gold_contract.py` — load ticket id → status from sim **`service_queries.csv`**; **`assert_expected_tickets_resolved`**.
- [X] Extend `tests/retail_multi_profiles/test_bundled_qa_suite.py` — every **`expected_ticket_ids`** entry has **`status=resolved`** in corpus CSV; provenance ids may be any status.
- [X] Red: test fails on current fixture; green after P2.

---

<h2 id="b20-gold-p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase P2 — Fixture + loader</h2>

- [X] Update `retail-bundled-qa-b20.json` — six rows per **G1**; add **`provenance_ticket_ids`**; extend **`grounding_policy`** sentence on resolved retrieval gold.
- [X] Extend `load_bundled_suite.py` — optional **`provenance_ticket_ids`** on **`BundledQuestion`**.
- [X] `bundled_runner.py` — embed **`provenance_ticket_ids`** in results row when present (inline comment: narrative vs retrieval label).

---

<h2 id="b20-gold-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase P3 — Operator + analysis</h2>

- [X] Run **`b20-evo18-d7-v3-goldfix-20261028`** (full 20) + **`b20-evo18-d7-v3-goldfix-six-20261028`** with EVO18 D7 v3 env.
- [X] Update **`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`** §8 row (goldfix run-id, judge, strict top-2, six); note label fix in §8.3 intro.
- [X] Regenerate §8.3 HTML via **`_gen_d7_fail_html.py`** when failure set changes. (Failure set unchanged — same 4 ids; §8 table + intro updated.)
- [X] Tick **REFACTOR_EVO18** plan note: B20 gold aligned (**G1**).

---

<h2 id="b20-gold-tdd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. TDD bar</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Phase</th><th>TDD mode</th><th>Test-first artifact</th><th>Green gate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">P1</td><td style="background:#e8f5e9">strict-TDD</td><td><code>test_bundled_qa_suite.py</code> resolved-gold assert</td><td><code>pytest tests/retail_multi_profiles/test_bundled_qa_suite.py</code></td></tr>
<tr><td style="background:#e3f2fd">P2</td><td style="background:#e8f5e9">strict-TDD</td><td>fixture + loader types</td><td>same pytest + <code>./scripts/verify.sh</code></td></tr>
<tr><td style="background:#e3f2fd">P3</td><td style="background:#fff8e1">smoke-after-delete</td><td>—</td><td>operator JSONL + analysis doc updated</td></tr>
</tbody>
</table>

---

<h2 id="b20-gold-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Quality bar</h2>

- **cdcm:** file header + doc line on new module and extended dataclass fields.
- **neatlog:** B20 goldfix run under `logs/ops/retail-bundled-qa-*`.
- **onlyref boundary:** no change to **`pg_search`** resolved filter.

---

<h2 id="b20-gold-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Execution checklist</h2>

- [X] P1 contract tests
- [X] P2 fixture + harness metadata
- [X] P3 operator + TEST_ANALYSIS
- [X] `./scripts/verify.sh` green
