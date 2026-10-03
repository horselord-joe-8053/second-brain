#!/usr/bin/env bash
# Apply a capability module into the target repo (idempotent where possible).

set -euo pipefail

REPO_ROOT="${1:-}"
MODULE="${2:-}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
CORE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$CORE/.." && pwd)"
MOD_ROOT="$KIT/modules/$MODULE"

if [[ -z "$MODULE" ]]; then
  echo "apply-module: missing module name" >&2
  exit 1
fi

echo "== apply-module: $MODULE -> $REPO_ROOT =="

case "$MODULE" in
  webapp)
    mkdir -p "$REPO_ROOT/docs/specs" "$REPO_ROOT/docs/mocks" "$REPO_ROOT/docs/templates"
    cp "$MOD_ROOT/harness/docs/WEBAPP-TDD.md" "$REPO_ROOT/docs/"
    cp "$MOD_ROOT/harness/docs/specs/ui-factory-convention.md" "$REPO_ROOT/docs/specs/"
    cp "$MOD_ROOT/docs/specs/homepage-ui-decision.md" "$REPO_ROOT/docs/specs/"
    cp "$MOD_ROOT/harness/docs/templates/"*.md "$REPO_ROOT/docs/templates/"
    cp "$MOD_ROOT/harness/docs/mocks/README.md" "$REPO_ROOT/docs/mocks/"
    mkdir -p "$REPO_ROOT/.agents/skills/ui-choose-look" "$REPO_ROOT/.agents/skills/implement-feature"
    cp "$MOD_ROOT/dot-agents-skills/ui-choose-look/SKILL.md" "$REPO_ROOT/.agents/skills/ui-choose-look/"
    cp "$MOD_ROOT/dot-agents-skills/implement-feature/SKILL.md" "$REPO_ROOT/.agents/skills/implement-feature/"
    echo "apply-module: webapp factory docs, templates, ui-choose-look, implement-feature (web)"
    ;;
  webapp-utils|kit-utils)
    bash "$CORE/scripts/seed-utils.sh" "$REPO_ROOT"
    ;;
  logging-neat)
    echo "apply-module: logging-neat — agent must follow $MOD_ROOT/MODULE.md (requires kit-utils)"
    ;;
  ui-choose)
    bash "$0" "$REPO_ROOT" webapp
    echo "apply-module: ui-choose — run ui-choose-look skill per spec; see modules/webapp/MODULE.md § UI-CHOOSE"
    ;;
  desktop-install)
    echo "apply-module: desktop-install — agent must follow $MOD_ROOT/MODULE.md"
    bash "$MOD_ROOT/scripts/detect-host-os.sh" || true
    ;;
  second-brain)
    mkdir -p "$REPO_ROOT/scripts"
    if [[ ! -x "$REPO_ROOT/scripts/verify-local.sh" ]]; then
      cp "$MOD_ROOT/templates/verify-local.sh" "$REPO_ROOT/scripts/verify-local.sh"
      chmod +x "$REPO_ROOT/scripts/verify-local.sh"
      echo "apply-module: installed scripts/verify-local.sh"
    fi
    echo "apply-module: second-brain — follow $MOD_ROOT/MODULE.md"
    ;;
  *)
    if [[ -d "$MOD_ROOT" ]] && [[ -f "$MOD_ROOT/MODULE.md" ]]; then
      echo "apply-module: loaded $MOD_ROOT/MODULE.md (agent-driven)"
    else
      echo "apply-module: no handler for $MODULE" >&2
      exit 1
    fi
    ;;
esac

echo "apply-module: done ($MODULE)"
