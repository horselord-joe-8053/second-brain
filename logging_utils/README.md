<h1 id="logging-utils-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">logging_utils</h1>

**Purpose:** Domain-specific logging helpers when **`utils/neat_logger`** is not a natural fit, but operators still need the **same story-shaped logs** (milestones, heartbeats, flush, checkpoint files).

**Default:** Prefer **`utils/neat_logger`** (Python) or **`utils/neat_logger_ts`** — see **`utils/neat_logger/HOWTO_USE_NEAT_LOGGER.md`**.

**Create modules here when you need:**

- JSONL checkpoint writers paired with neat_logger progress lines
- Resume keys `(run_id, lane, question_id)` without bloating the runner
- Wrappers that must not add `sys.path` hacks in test packages

**Bar:** **`.cursor/rules/neatlog-operator-logging-bar.mdc`** (`neatlog`).

**Layout (add as needed):**

```text
logging_utils/
  README.md           ← this file
  run_progress.py     ← example: JSONL append + neat_logger step lines
```

No code until a refactor plan phase calls for it — avoid empty abstractions.
