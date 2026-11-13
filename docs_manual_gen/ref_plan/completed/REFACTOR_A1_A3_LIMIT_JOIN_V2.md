<h1 id="lj2-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Limit-join v2 — A1 vs A3 accuracy demo</h1>

**Status:** Complete (`limit-join-v2-20261112`). **Construct:** one model per question, guide plus compiled news limit. **Gold:** ≤75 words. **Answers:** ≤150 words on both arms. **Eval-only:** no ranking, top-k, or prompt changes outside the word cap.

<h2 id="lj2-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#lj2-goal) — show when A1 wins limit-join questions.
2. [Decisions](#lj2-decisions) — word caps and fairness.
3. [Phases](#lj2-phases) — suite, harness, run, report.
4. [Exit](#lj2-exit) — artifacts and checkboxes.

<h2 id="lj2-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

<p>Extend the L01–L10 limit-join smoke with <strong>ten new</strong> staff questions. Each row joins a live user guide with a compiled news summary that states what cannot be promised. Compare A1 (compiled wiki) and A3 (manual hybrid RAG) with the same judge and independent providers.</p>

<h2 id="lj2-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

<table>
<thead><tr style="background:#1565c0;color:white"><th>Id</th><th>Decision</th></tr></thead>
<tbody>
<tr><td style="background:#e3f2fd">J2-D1</td><td>Gold answers ≤75 words; one critical criterion per row.</td></tr>
<tr><td style="background:#e3f2fd">J2-D2</td><td>Both arms get the same 150-word generation cap via suite metadata.</td></tr>
<tr><td style="background:#e3f2fd">J2-D3</td><td>One model per question; no catalog id strings; no triple-model briefing row.</td></tr>
<tr><td style="background:#e3f2fd">J2-D4</td><td>Report format: headline plus one matrix table; full text in ops JSONL only.</td></tr>
</tbody>
</table>

<h2 id="lj2-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phases</h2>

<h3 id="lj2-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">3.1 P1 — Suite and tests</h3>

- [X] `tests/retail_multi_profiles/data/retail-limit-join-v2.json` with V01–V10.
- [X] `tests/retail_multi_profiles/test_limit_join_v2.py` green.

<h3 id="lj2-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">3.2 P2 — Harness word cap</h3>

- [X] `answer_from_context` honors `answer_max_words` in insight mode.
- [X] `run_cos_insight_qa.py` passes suite `answer_max_words` into the benchmark.

<h3 id="lj2-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">3.3 P3 — Live run</h3>

- [X] Wiki health 200; Postgres lane B includes news files.
- [X] `run_cos_insight_qa --full --arm both --suite retail-limit-join-v2.json --run-id limit-join-v2-20261112`.

<h3 id="lj2-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">3.4 P4 — Report</h3>

- [X] `docs_manual_gen/artifacts/TEST_ANALYSIS_A1_A3_LIMIT_JOINS_V2.md` with matrix table.

<h2 id="lj2-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Exit</h2>

<p>Suite locked before scores. Results under <code>ops/runs/retail-cos-insight/limit-join-v2-20261112/</code>. v1 analysis remains at <code>TEST_ANALYSIS_A1_A3_LIMIT_JOINS.md</code>.</p>
