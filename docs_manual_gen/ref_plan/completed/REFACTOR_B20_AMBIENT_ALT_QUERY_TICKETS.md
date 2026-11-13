<h1 id="ref-b20-alt-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">REFACTOR — TYPE_B_B20 ambient alt query tickets (E08N / H10N)</h1>

**Status:** `new` · **Execute:** `aciubtdd` / **`qimpltdd`** on this file.

## Document outline

1. [Goal](#ref-b20b20-alt-goal hypothesis and scope.
2. [Decisions](#ref-b20-ab20-alt-decisionsligned choices.
3. [Phases](#ref-b20-alt-phasb20-alt-phasesn checklist.
4. [Quality bar](#ref-b20-alt-quality)b20-alt-qualityor exit.
5. [Exit](#ref-b20-alt-exit) — done b20-alt-exit<h2 id="ref-b20-alt-goal" style="cob20-alt-goalfont-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Add **BND-E08N-alt** and **BND-H10N-alt** to TYPE_B_B20 with customer wording tuned for **installation-site ambient** retrieval (unit 2), same gold as **BND-E08** / **BND-H10**. Run **D7 v3 PFDA** slice (2 rows), document in **§8.5** (do **not** replace §8.3).

**Parent baseline:** `b20-evo18-d7-v3-droptech-b20-evo18-d7-v3-droptech-full-20261029ref-b20-alt-decisions" style="color:#1565c0;font-size:1.2b20-alt-decisions50;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

| ID | Choice | Rationale |
|----|--------|-----------|
| D1 | Same `expected_ticket_ids`, `manual_anchor_question_id`, `answer` as parent rows | Judge target unchanged; query-only experiment |
| D2 | `BND-E08N-alt` easy; `BND-H10N-alt` hard | Mirrors parent difficulty |
| D3 | Run-id `b20-evo18-d7-v3-alt-query-20261029` | Distinct from droptechb20-evo18-d7-v3-alt-query-20261029rix row; §8.3 untouched | User requested separate section |

**last_aligned:** 2026-10-29 — user `qimpltdd` ambient alt tickets + §8.5.

---

<h2 id="ref-b20-alt-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4pb20-alt-phases5;padding-left:10px;margin-top:1.1em">3. Phases</h2>

### P1 — Fixture + contract tests

- [X] Add rows to `tests/retail_multi_profiles/data/retail-bundled-qa-b20.json`.
- [X] Extend `test_bundled_qa_suite.py` (count 23; alt gold parity test).
- [X] **Exit:** `./scripts/py -m pytest tests/retail_multi_profiles/test_bundled_qa_suite.py -q`

### P2 — Operator run (2-row slice)

- [X] Env: same as §7 reproduce + `RETAIL_D7=decompose`, `RETAIL_MANUAL_D2_CHUNK=page_heading`, `RETAIL_D2_PAGE_PACK=page_top5`, profile `MANUAL_B_RAW_PG_HYBRID`.
- [X] `./scripts/py tests/retail_multi_profiles/run_bundled_qa.py --question-ids BND-E08N-alt,BND-H10N-alt --run-id b20-evo18-d7-v3-alt-query-20261029`
- [X] **Exit:** JSONL under `ops/runs/retail-bundleb20-evo18-d7-v3-alt-query-2026102961029/` · **1/2 judge pass**

### P3 — Analysis artifact

- [X] Extend `_gen_d7_fb20-evo18-d7-v3-alt-query-20261029 (all listed ids, pass + fail).
- [X] Splice §8.5 into `TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`; add §8 table row.
- [X] **Exit:** `./scripts/py docs_manual_gen/artifacts/_gen_d7_fail_html.py b20-evo18-d7-v3-alt-query-20261029 --section alt --ids BND-E08N-alt,BND-H10N-alt`

### P4 — Plan close

- [X] Mark P1–P3 `[X]`; outcob20-evo18-d7-v3-alt-query-20261029merge); **BND-H10N-alt FAIL** (U1 repair-heavy merge drowns U2).

---

<h2 id="ref-b20-alt-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Quality bar</h2>b20-alt-quality mode | Test-first artifact | Red case | Green gate |
|-------|----------|---------------------|----------|------------|
| P1 | strict-TDD | `test_bundled_qa_suite.py` alt parity | Missing rows / wrong gold linkage | pytest suite |
| P2 | smoke-after-delete | — | — | JSONL 2 results |
| P3 | smoke-after-delete | — | — | §8.5 present in analysis md |

---

<h2 id="ref-b20-alt-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Exit</h2>

- TYPE_B_B20 JSON hb20-alt-exitids; tests green.
- Operator run recorded; §8.5 documents judge + manual merge vs parent hypothesis.
