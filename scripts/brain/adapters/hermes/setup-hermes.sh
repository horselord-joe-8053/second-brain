#!/usr/bin/env bash
# Idempotent Hermes CLI install (official installer) + `hermes doctor`.
# See docs_manual_gen/SECOND_BRAIN_RUNBOOK.md §10.
set -euo pipefail

HERMES_INSTALL_URL="${HERMES_INSTALL_URL:-https://hermes-agent.nousresearch.com/install.sh}"

hermes_on_path() {
  command -v hermes >/dev/null 2>&1
}

ensure_hermes_path() {
  if hermes_on_path; then
    return 0
  fi
  # Common install locations (install.sh may not update non-interactive PATH).
  local candidate
  for candidate in \
    "${HOME}/.local/bin/hermes" \
    "${HOME}/.hermes/bin/hermes" \
    "${HOME}/.hermes/hermes-agent/hermes" \
    "/usr/local/bin/hermes"; do
    if [[ -x "$candidate" ]]; then
      export PATH="$(dirname "$candidate"):${PATH}"
      return 0
    fi
  done
  return 1
}

run_official_install() {
  echo "== hermes: installing via official script =="
  echo "    ${HERMES_INSTALL_URL}"
  curl -fsSL "${HERMES_INSTALL_URL}" | bash
}

if ! ensure_hermes_path; then
  run_official_install
  if ! ensure_hermes_path; then
    echo "hermes: install finished but binary not on PATH."
    echo "Open a new shell, or: export PATH=\"\${HOME}/.local/bin:\${HOME}/.hermes/hermes-agent:\${PATH}\""
    echo "Then re-run: ./scripts/brain/setup-hermes.sh"
    exit 1
  fi
else
  echo "== hermes: found $(command -v hermes) — verifying with doctor =="
fi

echo "hermes: $(command -v hermes)"
hermes --version 2>/dev/null || true
echo "--- hermes doctor ---"
doctor_rc=0
hermes doctor || doctor_rc=$?
if [[ "$doctor_rc" -ne 0 ]]; then
  if hermes --version >/dev/null 2>&1; then
    echo "hermes doctor: exit ${doctor_rc} (often optional: API keys, npm audit) — CLI OK; skipping full reinstall."
    echo "  Run 'hermes setup' for model keys; 'hermes doctor --fix' for auto-fixes when desired."
  else
    echo "hermes doctor failed and CLI broken — re-running official installer to repair partial install"
    run_official_install
    ensure_hermes_path || true
    echo "--- hermes doctor (retry) ---"
    hermes doctor || true
  fi
fi

if ! hermes --version >/dev/null 2>&1; then
  echo "hermes: CLI not runnable after setup"
  exit 1
fi
echo "setup-hermes.sh: OK ($(command -v hermes))"
