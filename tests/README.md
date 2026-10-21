<h1 id="tests-readme-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Second Brain — tests layout</h1>

<h2 id="tests-readme-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Top level](#tests-top) — brain, fabrication, repo smoke.
2. [Retail unit and integration](#tests-retail) — ticket/manual answer, corpus, lexical.
3. [Retail multi-profile lane benchmark](#tests-rmp) — A–D ingest lane QA harness.
4. [Support](#tests-support) — shared scripts and docs.
5. [Running](#tests-run) — verify and focused pytest.

---

<h2 id="tests-top" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Top level</h2>

| Path | Role |
|------|------|
| `tests/conftest.py` | Shared pytest config, retail embed stub, seed fixture |
| `tests/test_brain_*.py` | Brain stack, MCP, Hermes wiring |
| `tests/test_fabrication_*.py` | Fabrication kit smoke |
| `tests/fixtures/` | Cross-cutting fixtures |

---

<h2 id="tests-retail" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Retail</h2>

All **`test_retail_*.py`** live under **`tests/retail/`** (Fridges R Us service brain: tickets, manuals, corpus, lexical, sim data).

Leg docs: `tests/support/retail/RETAIL_ANSWER_LEGS.md`.

---

<h2 id="tests-rmp" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Retail multi-profile lane benchmark</h2>

**`tests/retail_multi_profiles/`** — centralized code + docs for the **A–D retail ingest lane** manual QA benchmark (see plan `docs_manual_gen/ref_plan/new/REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md`).

---

<h2 id="tests-support" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Support</h2>

| Path | Role |
|------|------|
| `tests/support/repo_root.py` | `REPO_ROOT` for nested test packages |
| `tests/support/retail/` | Answer-leg CI shell helper |

---

<h2 id="tests-run" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Running</h2>

```bash
./scripts/verify.sh
scripts/py -m pytest -q tests/retail
scripts/py -m pytest -q tests/retail_multi_profiles
```

Nested retail tests use `Path(__file__).resolve().parents[2]` or `from tests.support.repo_root import REPO_ROOT` when importing repo-relative paths.
