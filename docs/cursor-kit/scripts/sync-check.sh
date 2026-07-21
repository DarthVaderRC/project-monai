#!/usr/bin/env bash
# Thin wrapper — canonical script: platform-core/scripts/sync-check.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export CURSOR_PROJECT_DIR="${CURSOR_PROJECT_DIR:-$ROOT}"

_resolve_core() {
  local d
  if [[ -n "${CURSOR_PLATFORM_CORE:-}" && -f "${CURSOR_PLATFORM_CORE}/scripts/sync-check.sh" ]]; then
    echo "${CURSOR_PLATFORM_CORE}"
    return
  fi
  for d in \
    "$ROOT/.ci/cursor-platform/plugins/platform-core" \
    "$ROOT/../cursor/plugins/platform-core" \
    "$HOME/.cursor/plugins/local/platform-core"
  do
    if [[ -f "$d/scripts/sync-check.sh" ]]; then
      echo "$d"
      return
    fi
  done
  echo ""
}

CORE="$(_resolve_core)"
if [[ -z "$CORE" ]]; then
  cat >&2 <<'EOF'
ERROR: platform-core not found.

Set CURSOR_PLATFORM_CORE, or place plugins at one of:
  .ci/cursor-platform/plugins/platform-core
  ../cursor/plugins/platform-core
  ~/.cursor/plugins/local/platform-core

CI: ensure the cursor-play checkout step succeeded and
CURSOR_PLATFORM_READ_TOKEN can read DarthVaderRC/cursor-play.
See docs/cursor-kit/productization/PRODUCTIZATION.md
EOF
  exit 1
fi
exec bash "$CORE/scripts/sync-check.sh" "$@"
