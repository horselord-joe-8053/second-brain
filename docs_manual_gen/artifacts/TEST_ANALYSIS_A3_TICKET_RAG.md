<h1 id="a3-analysis-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">TEST_ANALYSIS — A3 Ticket RAG (D6.T100)</h1>

**Status:** Phase **2** operator **P2.6** complete (**2026-10-26**). Reports: `ops/runs/fru-ticket-abc-p26-20261026/`. **`check_abc_ladder.py`** **OK**.

<h2 id="a3-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Scope](#a3-scope) — eval contract and baseline.
2. [P2.6 ABC results](#a3-p26) — T100 Postgres ladder.
3. [Evidence paths](#a3-paths) — CLI `--evidence-path` modes.
4. [Exit criteria (HG-P2)](#a3-exit) — recall@1 vs mode C.
5. [Next](#a3-next) — rerank/agentic promotion.

---

<h2 id="a3-scope" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Scope</h2>

| Item | Value |
|------|--------|
| **D6** | **T100** — `scripts/retail/eval/ticket_retrieval.jsonl` (100 eval rows) |
| **D3 baseline** | Mode **C** `rrf_term_boosted` |
| **Lexical** | `RETAIL_LEXICAL_BACKEND=tantivy` |
| **Profile** | `RETAIL_SIM_DATA_PROFILE=fru_us_1k` |
| **Gate** | `python scripts/retail/eval/check_abc_ladder.py` |

---

<h2 id="a3-p26" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. P2.6 ABC results (2026-10-26)</h2>

Operator command (each mode):

```bash
set -a && source .env && set +a
export PYTHONPATH="$PWD/scripts/retail" RETAIL_LEXICAL_BACKEND=tantivy RETAIL_SIM_DATA_PROFILE=fru_us_1k
RETAIL_TICKET_SEARCH_MODE=<mode> ./scripts/py scripts/retail/eval/eval_ticket_search.py --postgres --report ops/runs/fru-ticket-abc-p26-20261026/<mode>.json
```

Reports copied to ladder filenames (`pg_baseline_v1.json`, `pg_ab_v1_1_normal.json`, `pg_ab_v1_2_term_boosted.json`) for `check_abc_ladder.py`.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Mode</th><th>recall@1</th><th>paraphrase</th><th>hybrid_stress</th><th>code_in_query</th><th>Lexical leg nonempty</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">A <code>vector_only</code></td><td>0.25</td><td>0.26</td><td>0.30</td><td>0.15</td><td>n/a</td></tr>
<tr><td style="background:#e3f2fd">B <code>rrf_normal</code></td><td>0.44</td><td>0.56</td><td>0.43</td><td>0.15</td><td>100/100</td></tr>
<tr><td style="background:#e8f5e9">C <code>rrf_term_boosted</code></td><td><strong>0.54</strong></td><td>0.56</td><td>0.43</td><td>0.65</td><td>100/100</td></tr>
</tbody>
</table>

**Ladder check:** strict **A &lt; B &lt; C** on overall recall@1; **hybrid_stress** and **code_in_query** stratum rules satisfied.

**Bundled ticket leg default:** production and B20 harness set `RETAIL_TICKET_SEARCH_MODE=rrf_term_boosted` (mode **C**).

---

<h2 id="a3-paths" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Evidence paths (P2.5)</h2>

| `--evidence-path` | Stack |
|-------------------|--------|
| `baseline` | `search_ticket_hits_pg` only |
| `retriever` | `TicketEvidenceRetriever` |
| `retriever_rerank` | retriever + listwise **D5.R** |
| `agentic` | retriever + applicability verifier + **one** sub-search (**R4**) |

Output: `ops/runs/fru-ticket-evidence/<run_id>/evidence_rows.jsonl`.

---

<h2 id="a3-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Exit criteria (HG-P2)</h2>

Plan §11.6 promotion requires **evidence-path** uplift vs mode **C** baseline (paraphrase **≥ +0.05** or overall **≥ +0.03** with stratum guardrails). **ABC ladder alone does not close HG-P2** — rerank/agentic T100 compare still open.

| Check | P2.6 status |
|-------|-------------|
| T100 ABC on Postgres | <span style="background:#c8e6c9;padding:2px 4px">done</span> |
| `check_abc_ladder.py` | <span style="background:#c8e6c9;padding:2px 4px">green</span> |
| Evidence-path promotion vs C | <span style="background:#fff9c4;padding:2px 4px">not run this session</span> |

---

<h2 id="a3-next" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Next</h2>

```bash
python scripts/retail/eval/eval_ticket_search.py --evidence-path retriever --evidence-run-id p2-promotion
python scripts/retail/eval/check_abc_ladder.py --reports-dir ops/runs/fru-ticket-abc-p26-20261026
```

**Related:** [`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`](./TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md) (B20 uses mode **C** ticket leg).
