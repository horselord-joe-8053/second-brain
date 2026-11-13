#!/usr/bin/env bash
# Idempotent: sync Telegram/WhatsApp env → ~/.hermes/.env, merge platforms in config.yaml, gateway hints.
set -euo pipefail

HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERMES_AD/../../../.." && pwd)"
# shellcheck source=scripts/brain/adapters/hermes/hermes-env.sh
source "$HERMES_AD/hermes-env.sh"

echo "== setup-hermes-messaging =="

bash "$ROOT/scripts/brain/apply-stack-config.sh" >/dev/null

# shellcheck source=/dev/null
set -a
[[ -f "$HOME/.hermes/.env" ]] && source "$HOME/.hermes/.env"
[[ -f "$ROOT/.env" ]] && source "$ROOT/.env"
set +a

"$ROOT/scripts/py" "$HERMES_AD/merge-hermes-wiring.py"

has_tg=0
has_wa=0
[[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_ALLOWED_USERS:-}" ]] && has_tg=1
[[ "${WHATSAPP_ENABLED:-}" =~ ^([1tT][rR][uU][eE]|yes|1)$ ]] && [[ -n "${WHATSAPP_ALLOWED_USERS:-}" ]] && has_wa=1

if [[ "$has_tg" -eq 0 && "$has_wa" -eq 0 ]]; then
  echo "setup-hermes-messaging: no Telegram/WhatsApp secrets in .env or ~/.hermes/.env — skip gateway checks"
  echo "  Docs: runbook §16 · hermes gateway setup · Telegram QR in Desktop/dashboard"
  exit 0
fi

if command -v hermes >/dev/null 2>&1; then
  echo "--- hermes gateway status (summary) ---"
  hermes gateway status 2>/dev/null || echo "setup-hermes-messaging: gateway not running (start Desktop or: hermes gateway)"
fi

echo ""
echo "setup-hermes-messaging: OK"
echo "  Telegram: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram"
echo "  WhatsApp: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp"
