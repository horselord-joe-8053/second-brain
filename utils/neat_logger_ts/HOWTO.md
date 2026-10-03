<h1 id="howto-neat-logger-ts" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Using <code>neat_logger_ts</code></h1>

TypeScript sibling of `utils/neat_logger` (Python). Phase A: own yaml; Phase B: merge under `utils/neat_logger/ts/`.

## Document outline

1. [Purpose](#purpose) — PW / Playwright logging.
2. [Line format](#format) — `[TS]` tag.
3. [Roles](#roles) — `frontendMonitor`.
4. [Watch progress](#watch) — tail monitor file.

---

<h2 id="purpose" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Purpose</h2>

Playwright helpers import `@floor35/neat-logger-ts`. Key PW lines (`[PWLAD_PROGRESS]`, `[PWLAD_FAIL]`) also append to **`logs/monitor/monitor_frontend_progress.log`** while **`console.log`** still feeds **`ubs-run-*.log`**.

Backend/ops Python logging is unchanged (`api.log`).

---

<h2 id="format" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Line format</h2>

Monitor file (plain):

```text
[2026-08-25 20:15:01.234 GMT-3] [TS] [INFO] [PWLAD_PROGRESS] try=1 || ladder_id=… || 5/53_paragraphs_completed
```

Phase B will add **`[PY]`** to Python neat_logger lines the same way.

---

<h2 id="roles" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Roles</h2>

```typescript
import { NeatLoggerFactory } from "@floor35/neat-logger-ts/factory";

NeatLoggerFactory.frontendMonitor().info("[PWLAD_PROGRESS] …");
```

Config: `utils/neat_logger_ts/neat_logger_fallback_config.yaml` → `roles.frontend_monitor`.

Env: `REPO_ROOT`, `NEAT_LOGGER_TS_LOG_ROOT`, `NEAT_LOGGER_TS_LOG_FILE_NAME`.

---

<h2 id="watch" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Watch progress</h2>

```bash
tail -f logs/monitor/monitor_frontend_progress.log
```

Run pwlad on the **same host** as the log file (or shared mount).
