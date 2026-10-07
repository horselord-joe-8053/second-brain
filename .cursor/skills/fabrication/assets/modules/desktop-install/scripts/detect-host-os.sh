#!/usr/bin/env bash
# Print normalized host OS for desktop-install MODULE.md instructions.

set -euo pipefail

case "$(uname -s)" in
  Darwin) echo "HOST_OS=darwin" ;;
  Linux) echo "HOST_OS=linux" ;;
  MINGW*|MSYS*|CYGWIN*) echo "HOST_OS=windows" ;;
  *) echo "HOST_OS=unknown" ;;
esac

if command -v sw_vers >/dev/null 2>&1; then
  sw_vers -productVersion | awk '{print "HOST_OS_VERSION="$0}'
fi
