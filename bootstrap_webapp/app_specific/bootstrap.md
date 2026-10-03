<h1 id="app-specific-bootstrap" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Phase 2: Personal Dashboard (kit only)</h1>

**Not copied to the app repo.** Agent: after phase 1 STOP, run **Part B** using this file.

<h3 id="kit-meta" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Kit meta</h3>

```text
feature_id: dashboard-v1
spec_file: dashboard-v1.md
env_append: none
done_display_name: Personal Dashboard
```

<h2 id="mission" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Mission</h2>

Ship a **one-page personal dashboard** showing **10 AI-related headlines**, sourced from configured RSS feeds with **AI curation** when `LLM_API_KEY` is set (else deterministic RSS rules). **`./scripts/verify.sh` green**.

<h2 id="tickets" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Ticket slices (`/to-tickets`)</h2>

1. **News API** (deterministic baseline) → (2) **Dashboard UI** → blocked by 1 — (3) **UI-CHOOSE** → blocked by 2 — (4) **UI implement** → blocked by 3 — (5) **AI curation** (`docs/specs/dashboard-v1-ai-curation.md`) → blocked by 1.

<h2 id="glossary" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Glossary / AGENTS</h2>

**Region quota:** 6 US / 1 UK / 3 CN. **AI curation:** server-side LLM ranks latest AI stories from RSS candidates. **`AGENTS.md`:** **`docs/WEBAPP-TDD.md`**; specs under **`docs/specs/`**.

<h2 id="ui-notes" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">UI mock notes</h2>

See **`docs/specs/dashboard-v1-ui-decision.md`**. Show **Curated: AI** vs **RSS rules** in status when API returns `curated_by`.
