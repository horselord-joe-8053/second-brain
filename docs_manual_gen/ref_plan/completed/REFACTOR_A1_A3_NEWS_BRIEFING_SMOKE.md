<h1 id="news-smoke-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — five-question news briefing smoke</h1>

**Plan role:** evaluation-only smoke after the W20 briefing run. Search ranking stays unchanged.<br>
**Status:** complete. Smoke run `news-n5-smoke-20261112`. Mean confidence A1 0.90 and A3 0.90. Mean graded score A1 66.8 and A3 49.0. A3 was faster.<br>
**last_aligned:** 2026-11-12 — use the three news source summaries; widen Lane B so A2 and A3 can read the same news files; report confidence, not a binary pass.<br>
**Execute:** completed at `docs_manual_gen/ref_plan/completed/REFACTOR_A1_A3_NEWS_BRIEFING_SMOKE.md`.

<h2 id="news-smoke-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#news-smoke-goal) — what five questions can show.
2. [Evidence](#news-smoke-evidence) — where the path is set, and where the facts live.
3. [Decisions](#news-smoke-decisions) — grill answers.
4. [Questions](#news-smoke-questions) — the five frozen prompts and gold points.
5. [Phases](#news-smoke-phases) — index first, then smoke.
 5.1 [P0 — Freeze the five questions](#news-smoke-p0) — fixture and confidence contract.
 5.2 [P1 — Include the news files in Lane B](#news-smoke-p1) — one glob for A2 and A3.
 5.3 [P2 — Reindex and smoke](#news-smoke-p2) — confidence, hits, and cost.
6. [Boundary](#news-smoke-boundary) — what stays unchanged.
7. [TDD bar](#news-smoke-tdd) — red case and green gate per phase.
8. [Deferred](#news-smoke-deferred) — follow-ups that are out of this smoke.

---

<h2 id="news-smoke-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Show whether A1 (compiled wiki search) can answer five news-briefing questions with higher correctness confidence, and with less context or latency, than A3 (chunk search over the manuals) once both arms can read the same three news files.

The useful facts are in the three wiki source summaries, not in the one-paragraph concept pages. This smoke therefore uses those summaries as the gold source and records whether search actually opens them.

---

<h2 id="news-smoke-evidence" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Evidence</h2>

A2 and A3 do not have separate corpus paths. Both read Lane B. The path is set in one place:

`config/retail-ingest-lanes.yaml` → lane `B` → `raw_glob: raw/sources/fridge-docs_md/**/*.md`

`tests/retail_multi_profiles/lib/lanes.py` loads that glob. `tests/retail_multi_profiles/lib/raw_corpus.py` expands it. Lane C and Lane D keep their own globs and are not part of this smoke.

`brain/retail-md/raw/sources/` currently contains only `fridge-docs_md/` and `fridge-news_md/`. The news folder has three markdown files. They are absent from the Lane B glob, so A3 cannot retrieve them today.

The dates, scores, and “not a successor” limits are in:

- `wiki/sources/13-fridge-newsmd--16-gegne27jymfsnews--1j33fyx.md`
- `wiki/sources/13-fridge-newsmd--24-kitchenaidkrff507hpsnews--1f4ab6n.md`
- `wiki/sources/13-fridge-newsmd--22-samsungrf28k9070sgnews--1vtdbi6.md`

The matching concept pages, such as `wiki/concepts/product-lifecycle-management.md`, are one-paragraph paraphrases. They are not the gold source for this smoke.

---

<h2 id="news-smoke-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Decisions</h2>

| ID | Decision |
|----|----------|
| **N-D1** | Gold comes from the three news source summaries. Record whether each arm’s top hits include the matching news page. |
| **N-D2** | Widen Lane B from `fridge-docs_md` to `raw/sources/**/*.md`, reindex, and only then run A3. A2 uses the same Lane B glob, so the same correction covers A2. |
| **N-D3** | The smoke result is correctness confidence from 0 to 1, plus the existing 0–100 score as context. Binary pass is not the headline. |
| **N-D4** | Do not change search ranking, top-k, query splitting, or the answer prompt. |
| **N-D5** | Keep the historical Type B 16/20 result untouched. This smoke does not rerun it. |

---

<h2 id="news-smoke-questions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Questions</h2>

P0 copies these five into a frozen fixture. Gold text must stay within the facts below.

| ID | Question | Required gold point | News summary |
|----|----------|---------------------|--------------|
| **N01** | What should support staff say about GE GNE27JYMFS now that its product page says it is no longer manufactured? | Discontinuation is not a recall, and it does not prove that parts or service are unavailable. | GE summary, section 1 |
| **N02** | How should staff use the RTINGS review when an owner says produce is drying out in a GNE27JYMFS? | The review rates everyday use 7.4/10 and attributes drying to a dry compartment and crispers. Drying is not automatic proof of a cooling failure. | GE summary, section 2 |
| **N03** | Can staff tell a GNE27JYMFS owner that the new GE Profile Kitchen Assistant features can be added to that model? | No. Scan-to-List, the inventory camera, and the new display belong to the announced Profile model, not to GNE27JYMFS. | GE summary, section 3 |
| **N04** | Does KitchenAid KRFF507HPS have Intelligent Auto Fill? | No. Intelligent Auto Fill is a newer hands-free dispenser. KRFF507HPS has a through-the-door dispenser and no announced upgrade to Auto Fill. | KitchenAid summary, sections 1 and 3 |
| **N05** | What should staff say when an RF28K9070SG owner expects the new Samsung AI refrigerator software? | The announced AI software update covers selected newer Family Hub models and excludes RF28K9070SG. Review scores also differ by retailer. | Samsung summary, sections 1 and 2 |

---

<h2 id="news-smoke-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phases</h2>

<h3 id="news-smoke-p0" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.1 P0 — Freeze the five questions</h3>

- [X] Add `tests/retail_multi_profiles/data/retail-news-briefing-n5.json` with the five rows, gold answers, and one critical criterion per required gold point.
- [X] Mark the suite as a smoke fixture. Do not reuse the W20 20-row pass threshold as the headline.
- [X] Store the expected A1 hit prefix `wiki/sources/13-fridge-newsmd--` and the expected A3 hit prefix `raw/sources/fridge-news_md/`.

**P0 exit:** the fixture loads, has exactly five ids `N01`–`N05`, and rejects a row whose gold contradicts the required point.

<h3 id="news-smoke-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.2 P1 — Include the news files in Lane B</h3>

- [X] Change lane B `raw_glob` to `raw/sources/**/*.md`.
- [X] Keep lanes C and D unchanged.
- [X] Prove the loader returns the three `fridge-news_md` files and the existing `fridge-docs_md` manuals.
- [X] Reindex Lane B only after that test is green. Do not start the A1/A3 smoke before the news rows are in the index.

**P1 exit:** a targeted test fails while the glob is still `fridge-docs_md/**/*.md`, and passes after the widened glob. The reindex log lists the three news files.

<h3 id="news-smoke-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.3 P2 — Reindex and smoke</h3>

- [X] Run A1 and A3 on the five questions with the same answer model.
- [X] Judge with a different provider from the answer model. Record `correctness_confidence` as the primary result.
- [X] For each row, record top-hit paths, whether the expected news page appeared, context size, retrieval time, and total time.
- [X] Update `docs_manual_gen/artifacts/TEST_ANALYSIS_A1_LLM_WIKI.md` with a five-row section. State the result as confidence and efficiency. Do not convert it into a pass-rate claim.

**P2 exit:** `ops/runs/retail-cos-insight/news-n5-smoke-<date>/results.jsonl` has 10 rows, and the analysis section can be regenerated from that file.

Suggested commands, after P1 is green:

```bash
PYTHONPATH="$PWD/scripts/retail:$PWD" python3.12 -m tests.retail_multi_profiles.lib.manual_pg_index --lane B
PYTHONPATH="$PWD/scripts/retail:$PWD" python3.12 tests/retail_multi_profiles/run_cos_insight_qa.py \
  --full --arm both \
  --suite tests/retail_multi_profiles/data/retail-news-briefing-n5.json \
  --run-id news-n5-smoke-20261112
```

The index command must be the repo’s existing Lane B reindex entrypoint. If that module path differs, use the existing reindex CLI and name it in the run log. Do not invent a second indexer.

---

<h2 id="news-smoke-boundary" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Boundary</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Layer</th><th>This plan may change</th><th>This plan leaves alone</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Corpus scope</td><td style="background:#e8f5e9">Lane B glob, so news markdown is indexed</td><td>Wiki compilation, concept pages, and lanes C and D</td></tr>
<tr><td style="background:#e3f2fd">Search</td><td>Nothing</td><td>Ranking, top-k, aliases, and query splitting</td></tr>
<tr><td style="background:#e3f2fd">Score</td><td style="background:#e8f5e9">Report confidence first</td><td>The old W20 pass threshold and the Type B 16/20 result</td></tr>
</tbody>
</table>

---

<h2 id="news-smoke-tdd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. TDD bar</h2>

| Phase | TDD mode | Test-first artifact and red case | Green gate |
|-------|----------|----------------------------------|------------|
| **P0** | **strict-TDD** | `tests/retail_multi_profiles/test_news_briefing_smoke.py`: a four-row fixture or a missing N03 gold point fails | `python3.12 -m pytest -q tests/retail_multi_profiles/test_news_briefing_smoke.py` |
| **P1** | **strict-TDD** | Same test file: Lane B loader omits `fridge-news_md` under the old glob | Loader test includes all three news files and the existing manuals |
| **P2** | **strict-TDD** | Report fixture fails when confidence, hit path, or latency is missing | Targeted tests, then the live five-question smoke after reindex |

Execution:

- [X] P0 freeze the five-question fixture and confidence contract.
- [X] P1 widen Lane B and prove the news files are eligible.
- [X] P1 reindex Lane B and confirm the three news files are present.
- [X] P2 run A1 and A3, then update the analysis with confidence and efficiency.
- [X] Leave search ranking and the Type B result unchanged.

Exwar: P0 and P1 are a fixture and a glob change, so no new story. P2 repeats story 16 in `war_stories/WAR_STORIES.md`: judge confidence is a review signal. On N05, A3 confidence was 0.95 while correctness was 0.

Comments and logging:

- Every new or edited function needs one doc line.
- The reindex and smoke commands use the existing operator logger, with a JSONL progress line per question.
- Heartbeat any step that can run longer than about 20 seconds.

---

<h2 id="news-smoke-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Deferred</h2>

| Item | Why it waits |
|------|----------------|
| Ranking compiled pages ahead of `wiki/sources` | The useful news currently lives in the source summaries. Hiding those pages would remove the gold. |
| Rewriting concept pages into real briefs | That is a compilation change, not this smoke. |
| A 20-question promotion run | Only after this five-question smoke shows a confidence and efficiency difference. |
