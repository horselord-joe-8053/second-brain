#!/usr/bin/env bash
# Seed backend/.env and frontend/.env from bootstrap templates (no secrets).

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
KIT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$REPO_ROOT/backend" "$REPO_ROOT/frontend"

if [[ ! -f "$REPO_ROOT/backend/.env" ]]; then
  cp "$KIT/templates/backend.env.template" "$REPO_ROOT/backend/.env"
  echo "seed-dev-env: wrote backend/.env (includes LLM_* placeholders)."
else
  echo "seed-dev-env: backend/.env already exists; skipped."
fi

if [[ ! -f "$REPO_ROOT/frontend/.env" ]]; then
  cp "$KIT/templates/frontend.env.template" "$REPO_ROOT/frontend/.env"
  echo "seed-dev-env: wrote frontend/.env"
else
  echo "seed-dev-env: frontend/.env already exists; skipped."
fi

cp "$KIT/templates/backend.env.template" "$REPO_ROOT/.env.example" 2>/dev/null || true
cp "$KIT/templates/frontend.env.template" "$REPO_ROOT/frontend/.env.example" 2>/dev/null || true

echo "seed-dev-env: done."
echo "seed-dev-env: HUMAN — set LLM_API_KEY in backend/.env (OpenAI or compatible) for server-side AI."
