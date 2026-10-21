<h1 id="legs-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail answer bundle — two legs</h1>

**Contract:** [`retail_answer.v1`](../../../scripts/retail/retail_brain/answer_bundle.py) always *can* run **two legs** for one customer query. Production CLI defaults to **both**; tests and operators can run **each leg alone** first, then **integration**.

<h2 id="legs-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Legs at a glance](#legs-glance) — ticket vs manual.
2. [Where code lives](#legs-code) — modules and CLI.
3. [Pytest order (CI)](#legs-pytest) — markers and runner script.
4. [Live tier](#legs-live) — Postgres, wiki, env.
5. [Ops scripts](#legs-ops) — not under `cursor_gen/` for repeat use.

---

<h2 id="legs-glance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Legs at a glance</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Leg</th><th>Finds</th><th>Typical backend (live)</th><th>CI tests</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Ticket</strong></td><td>Top-2 <strong>resolved</strong> past tickets + cosine / fused score</td><td>Postgres + pgvector + lexical (<code>RETAIL_DATABASE_URL</code>)</td><td><code>tests/retail/test_retail_answer_tickets.py</code> · marker <code>retail_ticket_leg</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>Manual</strong></td><td>Up to 3 manual excerpts with <code>doc_path</code> (wiki → compiled page → <code>.txt</code>, or <code>raw_txt</code> grep)</td><td>LLM Wiki HTTP + SKU-scoped <code>raw/sources/fridge-docs/**/*.txt</code></td><td><code>tests/test_retail_answer_manuals.py</code> · marker <code>retail_manual_leg</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>Both</strong></td><td>One JSON bundle + optional Markdown render</td><td><code>answer_ticket.py</code> (default both legs)</td><td><code>tests/retail/test_retail_answer_bundle.py</code>, <code>tests/retail/test_retail_answer_e2e.py</code> · marker <code>retail_answer_integration</code></td></tr>
</tbody>
</table>

**Leg isolation:** If one leg throws, the other still runs; `diagnostics.ticket_leg_ok` / `manual_leg_ok` and `notes` record failures. **Skip flags** (P17): `build_answer_bundle(..., skip_ticket_leg=, skip_manual_leg=)` and CLI `--skip-tickets` / `--skip-manual`.

---

<h2 id="legs-code" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Where code lives</h2>

| Piece | Path |
|-------|------|
| Orchestrator | `scripts/retail/retail_brain/answer_bundle.py` |
| Ticket leg | `scripts/retail/retail_brain/answer_tickets.py` |
| Manual leg | `scripts/retail/retail_brain/answer_manuals.py` + `txt_docs.py` |
| CLI | `scripts/retail/answer/answer_ticket.py` |

**Fast manual smoke (no 1k CSV embed):**

```bash
scripts/py scripts/retail/answer/answer_ticket.py \
  --query "RF28K9070SG ice maker not making ice" \
  --skip-tickets --brain-root brain/retail --md
```

**Ticket leg only (tiny CSV):** use `--tickets-csv` with one row and `--skip-manual`.

---

<h2 id="legs-pytest" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Pytest order (CI)</h2>

Recommended order: **ticket leg → manual leg → integration (bundle + E2E)**.

```bash
# From repo root — same steps as tests/support/retail/run_answer_ci_legs.sh
scripts/py -m pytest tests/test_retail_answer_tickets.py -q
scripts/py -m pytest tests/test_retail_answer_manuals.py -q
scripts/py -m pytest tests/test_retail_answer_bundle.py tests/test_retail_answer_e2e.py -q
```

Or by marker:

```bash
scripts/py -m pytest -m retail_ticket_leg -q
scripts/py -m pytest -m retail_manual_leg -q
scripts/py -m pytest -m retail_answer_integration -q
```

Full repo gate remains `./scripts/verify.sh`.

---

<h2 id="legs-live" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Live tier</h2>

1. Set **`RETAIL_DATABASE_URL`** in repo **`.env`** (see **`.env.example`** — not duplicated in scripts).
2. Optional: **`RETAIL_SIM_DATA_PROFILE=fru_us_1k`** for FRU 1k corpus paths.
3. Load Postgres: `bash scripts/retail/ops/pg_up_and_load.sh` (truncates + reloads profile CSV + embeds).
4. Run: `RUN_RETAIL_E2E=1 scripts/py -m pytest tests/test_retail_answer_live.py -s`

Needs **`GEMINI_API_KEY`**, loaded FRU DB, and LLM Wiki for wiki-sourced manual hits (otherwise contract still passes with more `raw_txt`).

---

<h2 id="legs-ops" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Ops scripts</h2>

| Repeat use | Location |
|------------|----------|
| Docker + Postgres load | [`scripts/retail/ops/`](../../../scripts/retail/ops/README.md) |
| One-off V1.1 A/B prep | [`cursor_gen/retail_v11_prep/`](../../../cursor_gen/retail_v11_prep/README.md) (thin wrappers for 00/03 → ops) |

**Why not move shell into `tests/`?** Pytest owns **assertions**; **operator bash** belongs next to `scripts/retail/` (compose, reload). This folder documents **how tests map to legs** and ships **`run_answer_ci_legs.sh`** only.
