#!/usr/bin/env bash
# Thin wrapper — canonical script: pack-monai/scripts/check-deprecations.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export CURSOR_PROJECT_DIR="${CURSOR_PROJECT_DIR:-$ROOT}"
PACK="${CURSOR_ONBOARDING_PACK:-}"
if [[ -z "$PACK" ]]; then
  if [[ -d "$ROOT/../cursor/plugins/pack-monai" ]]; then
    PACK="$(cd "$ROOT/../cursor/plugins/pack-monai" && pwd)"
  elif [[ -d "$HOME/.cursor/plugins/local/pack-monai" ]]; then
    PACK="$HOME/.cursor/plugins/local/pack-monai"
  else
    echo "ERROR: pack-monai not found; set CURSOR_ONBOARDING_PACK or fetch plugins (see PRODUCTIZATION.md CI note)" >&2
    exit 1
  fi
fi
exec bash "$PACK/scripts/check-deprecations.sh" "$@"
