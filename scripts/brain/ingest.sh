#!/usr/bin/env bash
# Optional helper: copy file into <active brain-profile>/raw/sources/<channel>/ (BRAIN_PROFILE, default retail).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=scripts/brain/brain-profile-env.sh
source "$ROOT/scripts/brain/brain-profile-env.sh"
CHANNEL="${1:?usage: [BRAIN_PROFILE=personal|retail] ingest.sh <channel> <file>}"
FILE="${2:?usage: [BRAIN_PROFILE=personal|retail] ingest.sh <channel> <file>}"
DEST="$BRAIN_ROOT/raw/sources/$CHANNEL/$(basename "$FILE")"
mkdir -p "$(dirname "$DEST")"
cp -f "$FILE" "$DEST"
echo "ingest.sh: [$BRAIN_PROFILE] copied → $DEST (trigger Nashsu Source Watch / rescan)"
