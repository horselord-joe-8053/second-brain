# {{APP_NAME}} — Security and privacy

- LLM and third-party API keys **server-side only** (`backend/.env`); never in frontend bundle or git.
- Frontend talks only to this app's API origin (CORS aligned in dev).
- Do not log full user source text, secrets, or API keys. Backend logs use `utils/neat_logger`; frontend logs use `utils/neat_logger_ts`. Dev-only verbose logging requires explicit spec/ADR.
- Browser `localStorage` for user data only with approved spec and documented key/version.
