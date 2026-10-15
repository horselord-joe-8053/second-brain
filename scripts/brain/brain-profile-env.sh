#!/usr/bin/env bash
# Source me: exports BRAIN_PROFILE, BRAIN_ROOT, SECOND_BRAIN_WIKI_VAULT for the active brain-profile.
# Resolution (brain_stack.py): env BRAIN_PROFILE -> config active_brain_profile -> retail.
#   source "$ROOT/scripts/brain/brain-profile-env.sh"
_bp_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
_bp_out="$("$_bp_root/scripts/py" "$_bp_root/scripts/brain/brain_stack.py" profile-env)" || {
  echo "brain-profile-env: could not resolve brain profile" >&2
  return 1 2>/dev/null || exit 1
}
eval "$_bp_out"
unset _bp_root _bp_out
