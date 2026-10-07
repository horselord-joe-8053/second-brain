<h1 id="mod-logging-neat" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Module: logging-neat</h1>

**When:** Web stack ticket or spec `<!-- module: logging-neat -->`. Requires **`kit-utils`** (or **`webapp-utils`**) first.

1. Read `utils/neat_logger/HOWTO_USE_NEAT_LOGGER.md` and `utils/neat_logger_ts/HOWTO.md`.
2. Backend: `from utils.neat_logger import logger`; ensure `PYTHONPATH` includes repo root (`verify.sh` / `dev.sh` do).
3. Frontend: `"@floor35/neat-logger-ts": "file:../utils/neat_logger_ts"` in `package.json`.
4. Add **`logs/`** to `.gitignore`.

Do not apply to pure docs/shell/desktop-only phases.
