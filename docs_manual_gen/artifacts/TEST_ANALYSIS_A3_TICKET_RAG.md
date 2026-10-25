<h1 id="a3-analysis-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">TEST_ANALYSIS — A3 Ticket RAG (D6.T100)</h1>

**Status:** Phase **2** engineering **in progress** on branch **`feature/evo-15-multi-run-profile-phase-2`**. Operator **T100** + ladder promotion pending live Postgres run (**P2.6**).

<h2 id="a3-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Scope](#a3-scope) — eval contract and baseline.
2. [Evidence paths](#a3-paths) — CLI `--evidence-path` modes.
3. [Exit criteria (HG-P2)](#a3-exit) — recall@1 vs mode C.
4. [Next](#a3-next) — operator commands.

---

<h2 id="a3-scope" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Scope</h2>

| Item | Value |
|------|--------|
| **D6** | **T100** — `scripts/retail/eval/ticket_retrieval.jsonl` |
| **D3 baseline** | Mode **C** `rrf_term_boosted` (~0.54 recall@1 overall — see [`ABOUT_SEARCH_RRF_FRU.md`](./ABOUT_SEARCH_RRF_FRU.md)) |
| **Do not regress** | `python scripts/retail/eval/check_abc_ladder.py` |

---

<h2 id="a3-paths" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Evidence paths (P2.5)</h2>

| `--evidence-path` | Stack |
|-------------------|--------|
| `baseline` | `search_ticket_hits_pg` only |
| `retriever` | `TicketEvidenceRetriever` |
| `retriever_rerank` | retriever + listwise **D5.R** |
| `agentic` | retriever + applicability verifier + **one** sub-search (**R4**) |

Output: `ops/runs/fru-ticket-evidence/<run_id>/evidence_rows.jsonl`.

---

<h2 id="a3-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Exit criteria (HG-P2)</h2>

Per plan §11.6: **paraphrase** stratum recall@1 **≥ +0.05** vs mode **C**, or overall **≥ +0.03** with no stratum drop **> 0.02**. Fill metrics here after operator **T100** run.

---

<h2 id="a3-next" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Next</h2>

```bash
# Full Postgres eval (existing)
python scripts/retail/eval/eval_ticket_search.py --postgres

# Evidence path smoke (requires RETAIL_DATABASE_URL)
python scripts/retail/eval/eval_ticket_search.py --evidence-path retriever --evidence-run-id p2-smoke

# ABC ladder gate
python scripts/retail/eval/check_abc_ladder.py
```
