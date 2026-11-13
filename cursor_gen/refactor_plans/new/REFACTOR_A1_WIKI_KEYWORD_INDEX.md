<h1 id="a1-kw-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — save a wiki keyword index at page write</h1>

**Plan role:** parked efficiency work. Do not start it during the current A1 versus A3 accuracy test.<br>
**Status:** plan only. Every implementable item is `[ ]`.<br>
**Execute later:** `implref cursor_gen/refactor_plans/new/REFACTOR_A1_WIKI_KEYWORD_INDEX.md`.<br>
**last_aligned:** 2026-11-12 — record why Tantivy exists, and keep this work off the accuracy route.

<h2 id="a1-kw-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#a1-kw-goal) — what later work may speed up.
2. [Background](#a1-kw-background) — why and when Tantivy was added.
3. [Evidence](#a1-kw-evidence) — what the measurements actually showed.
4. [Decisions](#a1-kw-decisions) — parked scope.
5. [Phases](#a1-kw-phases) — index, returned text, embedding wait.
 5.1 [P1 — Write the keyword index when a page is saved](#a1-kw-p1) — stop the live file walk.
 5.2 [P2 — Return page text with the hit](#a1-kw-p2) — stop the second download.
 5.3 [P3 — Bound the query embedding wait](#a1-kw-p3) — one question vector, not 282 page vectors.
 5.4 [P4 — Remeasure search time only](#a1-kw-p4) — do not retune the accuracy suite.
6. [Quality bar](#a1-kw-quality) — tests, comments, logging.
7. [Deferred](#a1-kw-deferred) — accuracy test and the model filter.

---

<h2 id="a1-kw-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Give A1 (compiled wiki search) a saved keyword index, written when a wiki page is saved, so a question does not open all 282 markdown files under `brain/retail-md/wiki/`.

This plan does not change ranking weights, top-k, or the A1 versus A3 accuracy comparison.

---

<h2 id="a1-kw-background" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Background</h2>

Nashsu’s wiki search, current `search.rs` on `nashsu/llm_wiki`, still walks every `wiki/**/*.md` file at question time. The keyword score counts query words that appear in the file and multiplies title hits by 5. Page embeddings are written at ingest. The question embedding is the only new vector at search time. The keyword leg has no saved index. Upstream has no Tantivy and no BM25.

This repo added Tantivy for a different corpus:

| Date | Commit | What it indexed |
|------|--------|-----------------|
| 2026-10-14 | `0f28596` | Ticket text. `RETAIL_LEXICAL_BACKEND` defaults to `tantivy`. |
| 2026-10-28 | `68a2401` | Manual chunks. `ManualTantivyLexicalIndex` in `scripts/retail/retail_brain/lexical_search/manual_tantivy_index.py`. |

War stories 4, 6, and 11 in `war_stories/WAR_STORIES.md` record the ticket and manual path. Story 6 lists four engines (Tantivy, bm25x, ParadeDB, OpenSearch) and the Tantivy default. Story 11 records the in-process overlap scorer giving about 66% of one Samsung chunk’s score to “the”, “a”, and “and”, with the expected chunk ranked 48th of 59. Story 4 records an empty ticket keyword leg and rejects scanning every row for word overlap. A past chat, [Nu LLM Wiki management](9621e855-c855-4c84-aa62-2342caeeaef4), showed Nashsu’s overlap plus title bonus ranking a door-reversal concept first on a door-alarm question.

Tantivy was not substituted into Nashsu’s `search.rs`. A1 still uses that scan.

---

<h2 id="a1-kw-evidence" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Evidence</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Measurement</th><th>What changed</th><th>Result</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Ticket ladder</td><td>Vector only, then vector plus Tantivy, then a code boost</td><td style="background:#e8f5e9">recall@1 0.25, then 0.44, then 0.54</td></tr>
<tr><td style="background:#e3f2fd">Manual judge, same questions</td><td>`b20-brand-model-20261027` overlap, then `b20-evo18-t0-20261028` Tantivy plus SQL model filter</td><td style="background:#fff3e0">14/20 down to 11/20. Manual median 456 ms down to 272 ms.</td></tr>
<tr><td style="background:#e3f2fd">News smoke `news-n5-smoke-20261112`</td><td>A1 file scan versus A3 Tantivy hybrid. Filter was off because the questions used bare model codes.</td><td style="background:#fff3e0">Search 5.6 s versus 1.1 s. Graded score 66.8 versus 49.0. Matching news page 5/5 versus 3/5.</td></tr>
</tbody>
</table>

The wiki folder count on 2026-11-12 is 282 markdown files: 139 concepts, 116 sources, 24 entities, 3 at the wiki root. A1’s keyword walk includes `wiki/sources/`.

The current A3 model filter reads the question for exactly one catalog id (`ge_GNE27JYMFS`, `kitchenaid_KRFF507HPS`, or `samsung_RF28K9070SG`). One id limits both Tantivy and the Postgres vector query to that brand and model. Zero ids, two ids, or a bare code such as `RF28K9070SG` leave the filter off. The older filter loaded 200 chunks first and discarded mismatches afterward.

---

<h2 id="a1-kw-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Decisions</h2>

| ID | Decision |
|----|----------|
| **K-D1** | Park this plan. The live route is A1 versus A3 accuracy, not search speed. |
| **K-D2** | A later keyword index is a new wiki-page index written at save time. Do not reuse A3’s manual-chunk index. |
| **K-D3** | Tantivy is the preferred library because the wiki app is Rust and this repo already operates Tantivy. Confirm the crate choice in P1 before coding. |
| **K-D4** | Do not change RRF weights, top-k, or the answer prompt in this plan. |

---

<h2 id="a1-kw-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phases</h2>

<h3 id="a1-kw-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.1 P1 — Write the keyword index when a page is saved</h3>

- [ ] Add a wiki-page keyword index in the LLM wiki app, updated when a page is created or edited, and removed when a page is deleted.
- [ ] Point the keyword half of `search.rs` at that index. Remove the per-question walk of `wiki/**/*.md` from the hot path.
- [ ] Keep the stored page vectors. Do not re-embed unchanged pages at question time.

**P1 exit:** a test shows a question does not read all 282 files, and an edited page is searchable after save without a full vault scan.

<h3 id="a1-kw-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.2 P2 — Return page text with the hit</h3>

- [ ] The search API already accepts `includeContent`. The Python client in `scripts/retail/retail_brain/answer_manuals.py` sends only `query` and `topK`, then calls `read` once per hit.
- [ ] Return the kept prefix with the hit and stop the extra page downloads on the A1 answer path.

**P2 exit:** one search response supplies the context text for the top hits. Retrieval time no longer includes five separate file reads.

<h3 id="a1-kw-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.3 P3 — Bound the query embedding wait</h3>

- [ ] The query embedding timeout in `search.rs` is 8 seconds (`SEARCH_EMBEDDING_TIMEOUT_SECS`). A failure already drops the vector leg and continues with keywords.
- [ ] Fail that call faster, or cache the question embedding, without embedding the 282 pages again.

**P3 exit:** a failed embedding does not consume the full 8 seconds, and keyword results still return.

<h3 id="a1-kw-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.4 P4 — Remeasure search time only</h3>

- [ ] Rerun the five news questions, or a smaller smoke, and record search time, write time, and whether the same news page is still in the top 5.
- [ ] Do not treat a faster search as an accuracy promotion.

**P4 exit:** a short note in `docs_manual_gen/artifacts/TEST_ANALYSIS_A1_LLM_WIKI.md` with before and after search times.

---

<h2 id="a1-kw-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Quality bar</h2>

- Tests first on the index update and on the search path. A deleted page must disappear from the keyword hits.
- Every new function needs one doc line. File headers on new modules. A short comment where the keyword leg stops walking the vault.
- Operator logs use the existing neat logger, a JSONL progress line per ingest or reindex, and a heartbeat if a rebuild can run longer than about 20 seconds.
- Long run, when P4 is executed: smoke on two questions, then the five-question news smoke. Commands belong in the run log, not a second indexer.

---

<h2 id="a1-kw-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Deferred</h2>

| Item | Why it waits |
|------|----------------|
| A1 versus A3 accuracy suite | Separate route. Speed work must not change it. |
| Forcing A3’s model filter off for multi-model questions | A Type C question can name more than one model. Exactly one catalog id narrows A3 and makes the comparison unfair. Bare model codes already leave the filter off. Do not “fix” that inside this efficiency plan. |
| Rewriting concept pages | The non-source pages are one-paragraph paraphrases. They are not this plan. |
