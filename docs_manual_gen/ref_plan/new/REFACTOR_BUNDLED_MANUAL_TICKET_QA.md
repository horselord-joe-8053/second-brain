<h1 id="bnd-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — bundled manual + ticket Q&amp;A (fixed-k concat)</h1>

**Plan role:** **minor** (child).  
**Parent (only):** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) — Phase **4** prelude **B0** (see main plan [§0 minor **M4**](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md#gpt-hierarchy)).  
**Prerequisites (not parents):** main **P2.6** ticket metrics; minor **M3** PG manual cutover [`completed`](../completed/REFACTOR_UNIFIED_PG_MANUAL_EMBEDDINGS.md).  
**Status:** **implemented** — P1–P3 code + unit tests; operator full B20 **`b20-full-20261026`** (**2026-10-26**).  
**Analysis:** [`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`](../../artifacts/TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md).  
**Next:** Improve manual recall (PG hybrid tuning) or ticket top-2 before merged-packet rerank experiments.  
**Child plan:** [`REFACTOR_B20_RESOLVED_GOLD_LABELS.md`](../completed/REFACTOR_B20_RESOLVED_GOLD_LABELS.md) — align B20 **`expected_ticket_ids`** with resolved-only ticket search.

<h2 id="bnd-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Locked policy](#bnd-policy) — 5 manuals + 2 tickets, no per-leg LLM rerank.
2. [Evidence](#bnd-evidence) — ticket-leg restest and gold fixture.
3. [Phase 1 — Config comments](#bnd-p1) — name the two k values.
4. [Phase 2 — Context concat](#bnd-p2) — one prompt from both legs.
5. [Phase 3 — Judged B20 harness](#bnd-p3) — same judge style as M90.
6. [Quality bar and TDD](#bnd-quality) — red/green per phase.
7. [Decisions](#bnd-decisions) — letters locked this turn.
8. [Execution checklist](#bnd-checklist) — `[ ]` / `[X]`.
9. [Deferred](#bnd-deferred) — later rerank profiles.
10. [Related](#bnd-related).

---

<h2 id="bnd-policy" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Locked policy</h2>

Bundled answers use **two legs**, then **concatenate** a fixed number of hits into one answer prompt. There is **no** single fused index and **no** listwise LLM rerank on either leg for the regression profile.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Knob</th><th>Value</th><th>Why</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>k_manuals</strong></td><td style="background:#e8f5e9"><strong>5</strong></td><td>Same as M90 <code>search_top_k</code> in <code>config/brain-stack.example.yaml</code> / harness merge.</td></tr>
<tr><td style="background:#e3f2fd"><strong>k_tickets</strong></td><td style="background:#e8f5e9"><strong>2</strong></td><td>Already the default of <code>build_answer_bundle</code> in <code>scripts/retail/retail_brain/answer_bundle.py</code>. Keeping 2 avoids a second ticket-k experiment.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Assembly</strong></td><td>Fixed-k concat (approach A)</td><td>Debuggable. Sections stay labeled (tickets vs manuals).</td></tr>
<tr><td style="background:#e3f2fd"><strong>Per-leg LLM rerank</strong></td><td style="background:#fff3e0">Off for the bundled regression profile</td><td>M90 rerank passes moved 36 → 34 → 35 with large latency. RRF-only manual profile is the stable anchor.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Ticket search score</strong></td><td>Primary <strong>recall@1</strong></td><td>Matches the ABC ladder. recall@3 is optional later; with k_tickets=2 it is not the promotion metric.</td></tr>
</tbody>
</table>

`build_answer_bundle` today returns **evidence JSON** (`retail_answer.v1`), not a generated answer. Phase 2 adds the **answer string** on top of that JSON. Deterministic merge already means stable JSON bytes, not “the model concatenated prose.”

---

<h2 id="bnd-evidence" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Evidence</h2>

<h3 id="bnd-t100" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 Ticket leg restest (2026-10-26)</h3>

Profile **`fru_us_1k`** (100 eval rows, Postgres + Tantivy). Reports written under `/tmp/fru-abc-restest/` (committed profile reports were **not** overwritten). `check_abc_ladder.py` exited **OK**.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Mode</th><th>recall@1</th><th>paraphrase</th><th>hybrid_stress</th><th>code_in_query</th><th>Lexical leg nonempty</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">A <code>vector_only</code></td><td>0.25 (25%)</td><td>0.26</td><td>0.30</td><td>0.15</td><td>n/a</td></tr>
<tr><td style="background:#e3f2fd">B <code>rrf_normal</code></td><td>0.44 (44%)</td><td>0.56</td><td>0.43</td><td>0.15</td><td>100/100</td></tr>
<tr><td style="background:#e8f5e9">C <code>rrf_term_boosted</code></td><td><strong>0.54 (54%)</strong></td><td>0.56</td><td>0.43</td><td>0.65</td><td>100/100</td></tr>
</tbody>
</table>

Default env without `RETAIL_TICKET_SEARCH_MODE` is **`vector_only`** (25%). The published benchmark score to quote is **mode C, 54% recall@1** (gold ticket id is rank 1). This matches [`ABOUT_SEARCH_RRF_FRU.md`](../../artifacts/ABOUT_SEARCH_RRF_FRU.md).

<h3 id="bnd-gold" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.2 Bundled gold (authored with this plan)</h3>

[`tests/retail_multi_profiles/data/retail-bundled-qa-b20.json`](../../../tests/retail_multi_profiles/data/retail-bundled-qa-b20.json) — **20** rows, **10 easy** + **10 hard**. Each gold sentence pairs one real `resolution_text` from `fru_us_1000_100/service_queries.csv` with one manual fact copied in spirit from `retail-manual-qa-test-suite.json` (`manual_anchor_question_id`). `expected_ticket_ids` is the retrieval label. Several hard rows reuse the same ticket as an easy row on purpose: retrieval target stays fixed; wording gets harder.

---

<h2 id="bnd-p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase 1 — Config comments</h2>

Put **`k_tickets: 2`** and **`k_manuals: 5`** (bundle) next to existing **`search_top_k: 5`** (M90 manual-only) in `config/brain-stack.example.yaml`, with comments that the three numbers are **not** one knob:

- `search_top_k` — manual-only harness (M90).
- `k_manuals` — manual hits copied into a bundled answer.
- `k_tickets` — ticket hits copied into a bundled answer.

Expose `--k-tickets` on `scripts/retail/answer/answer_ticket.py` (today only `--k-manuals` exists; tickets stay at the function default 2).

---

<h2 id="bnd-p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2 — Context concat</h2>

Build one prompt: labeled **past tickets** (top 2: id, customer text, resolution) then **manual excerpts** (top 5 chunks, same char caps as M90). One `answer_from_context` call. Manual leg for this profile is **Postgres hybrid RRF** (`MANUAL_B_RAW_PG_HYBRID` behavior, D5 rerank off). Ticket leg is **mode C** `rrf_term_boosted` unless the operator sets `RETAIL_TICKET_SEARCH_MODE`.

Do **not** listwise-rerank inside a leg in this phase.

---

<h2 id="bnd-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 3 — Judged B20 harness</h2>

Score the 20 rows the way M90 scores answerable items: temperature 0 answer model + Gemini judge vs `answer` text (`tests/retail_multi_profiles/lib/scoring.py`). Also log whether `expected_ticket_ids[0]` appears in the two ticket hits (hit-in-packet). Persist `ops/runs/retail-bundled-qa/<run_id>/results.jsonl` with neatlog progress (see neatlog rule). Smoke = 2 question ids; full = all 20.

---

<h2 id="bnd-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Quality bar and TDD</h2>

Comments: file header plus one doc line per new function (**cdcm**). Operator runs: neatlog channel, JSONL checkpoint, heartbeat on LLM steps.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Phase</th><th>TDD mode</th><th>Test-first artifact</th><th>Red case</th><th>Green gate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">1 Config</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail_multi_profiles/test_run_config.py</code> asserts bundle k defaults 5 and 2 and that comments exist in the example yaml keys</td><td>Merged config lacks <code>k_tickets</code> / <code>k_manuals</code></td><td><code>./scripts/py -m pytest tests/retail_multi_profiles/test_run_config.py</code></td></tr>
<tr><td style="background:#e3f2fd">2 Concat</td><td style="background:#e8f5e9">strict-TDD</td><td>New <code>tests/retail/test_bundle_context.py</code>: fixture hits → prompt contains both ticket id and manual chunk text, truncated at caps, tickets section before manuals</td><td>Concat helper missing or drops a leg</td><td>That pytest file</td></tr>
<tr><td style="background:#e3f2fd">3 Harness</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail_multi_profiles/test_bundled_qa_suite.py</code> loads B20: 20 rows, 10/10 difficulty, every <code>expected_ticket_ids</code> exists in the FRU CSV for that model</td><td>Suite drifts (count, missing ticket, model mismatch)</td><td>Suite pytest, then operator smoke (2 ids) and full 20 with <code>OPENAI_API_KEY</code> + <code>GEMINI_API_KEY</code></td></tr>
</tbody>
</table>

---

<h2 id="bnd-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Decisions</h2>

| ID | Choice |
|----|--------|
| **B1** | Bundle context = **5 manual hits + 2 ticket hits**. |
| **B2** | Assembly = **fixed-k concat**. No cross-leg score fusion in v1. |
| **B3** | Bundled regression profile **does not** use per-leg LLM listwise rerank. |
| **B4** | Ticket headline metric stays **recall@1**. Mode C restest **2026-10-26 = 0.54**. |
| **B5** | D6 bundled gold = prose answer **plus** `expected_ticket_ids` **plus** `manual_anchor_question_id`. File: B20 JSON above. |
| **B6** | Heterogeneous legs stay (manuals vs tickets). Homogeneous one-index chunking is out of scope (war story 12). |
| **B7** | Alignment **2026-10-27**: rewrite the six failed B20 prompts as natural customer questions that require both historical-ticket and manual knowledge, without revealing either answer. Labels, anchors, and gold may change when coherence requires it. Run the six changed rows first, then full B20 if the targeted run is healthy. |
| **B8** | Targeted gate **`b20-natural-six-20261027`**: **0/6** judge, **0/6** labeled ticket in top-2, **6/6** manual legs non-empty. Per B7, do **not** run the full 20 yet; fix ticket retrieval/manual top-5 coverage before replacing the 14/20 pre-rewrite baseline. |
| **B9** | Customer-language correction: remove “past/similar service cases” and “user guide says” from incoming questions. Superseding gate **`b20-customer-six-20261027`** remains **0/6** judge, **0/6** labeled ticket in top-2, **6/6** manual legs non-empty; full-20 rerun remains gated. |

---

<h2 id="bnd-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Execution checklist</h2>

- [X] Author 20 bundled gold rows (easy/hard) grounded in FRU resolutions + M90 manual anchors.
- [X] P1.1 Document `k_tickets` / `k_manuals` beside `search_top_k` with comments.
- [X] P1.2 `--k-tickets` on `answer_ticket.py` (default **2**); `--k-manuals` default **5** for bundled CLI path.
- [X] P2.1 Concat helper + unit test (`retail_brain.bundle_context`, `tests/retail/test_bundle_context.py`).
- [X] P2.2 Wire helper to PG manual hybrid (RRF, rerank off) and ticket mode C (`bundled_runner.py`).
- [X] P3.1 Suite loader test for B20 (`test_bundled_qa_suite.py`).
- [X] P3.2 Operator full 20 → [`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`](../../artifacts/TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md).

**P1.2 note for the implementer:** `answer_ticket.py` currently defaults `--k-manuals` to **3**. Locked bundle policy is **5**. Prefer a named config default of 5 for the bundled command and leave a comment if any caller still wants 3.

---

<h2 id="bnd-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Deferred</h2>

| Item | When |
|------|------|
| Run profile: rerank **only inside a leg** | After a deterministic reranker exists (not LLM listwise without a seed). |
| Run profile: rerank **only on the merged packet** | After B20 baseline exists, so A/B has a control. |
| Run profile: rerank **both** levels | Only as an explicit third profile, never the default. |
| Drop Tantivy for in-process lexical on 1000 tickets | Separate A/B; do not fold into this plan. See war story 11. |
| recall@3 as a co-primary ticket KPI | Not while k_tickets stays 2. |

---

<h2 id="bnd-related" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Related</h2>

- [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) — **main plan**; this file is minor **M4** ([§0](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md#gpt-hierarchy)).
- `scripts/retail/retail_brain/answer_bundle.py` — evidence JSON.
- `scripts/retail/answer/answer_ticket.py` — CLI.
- `tests/retail_multi_profiles/lib/scoring.py` — M90 judge.
- `scripts/retail/eval/eval_ticket_search.py` — ticket recall@1.
- War stories **11** and **12** in `war_stories/WAR_STORIES.md`.
