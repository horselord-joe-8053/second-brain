# Corpus schema (v1)

- **Sources:** `raw/sources/<channel>/` — channel is one of `personal`, `uploads`, `drive`, `gmail`, `github`, `web`, `chat`.
- **Manifests:** optional envelope in `manifests/` (see `harness/second-brain/` for YAML shape).
- **Compiled wiki:** `wiki/` — maintained by Nashsu LLM Wiki; treat as compiler output.
- **Assets:** binaries under `raw/assets/` or channel folders; large files gitignored per `brain/.gitignore`.
