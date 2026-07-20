#!/usr/bin/env bash
# Thin wrapper — canonical script: platform-core/scripts/sync-check.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export CURSOR_PROJECT_DIR="${CURSOR_PROJECT_DIR:-$ROOT}"
CORE="${CURSOR_PLATFORM_CORE:-}"
if [[ -z "$CORE" ]]; then
  if [[ -d "$ROOT/../cursor/plugins/platform-core" ]]; then
    CORE="$(cd "$ROOT/../cursor/plugins/platform-core" && pwd)"
  elif [[ -d "$HOME/.cursor/plugins/local/platform-core" ]]; then
    CORE="$HOME/.cursor/plugins/local/platform-core"
  else
    echo "ERROR: platform-core not found; set CURSOR_PLATFORM_CORE or fetch plugins (see PRODUCTIZATION.md CI note)" >&2
    exit 1
  fi
fi
exec bash "$CORE/scripts/sync-check.sh" "$@"
