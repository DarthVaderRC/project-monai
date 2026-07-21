#!/usr/bin/env bash
# Thin wrapper — canonical script: pack-monai/scripts/check-deprecations.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export CURSOR_PROJECT_DIR="${CURSOR_PROJECT_DIR:-$ROOT}"

_resolve_pack() {
  local d
  if [[ -n "${CURSOR_ONBOARDING_PACK:-}" && -f "${CURSOR_ONBOARDING_PACK}/scripts/check-deprecations.sh" ]]; then
    echo "${CURSOR_ONBOARDING_PACK}"
    return
  fi
  for d in \
    "$ROOT/.ci/cursor-platform/plugins/pack-monai" \
    "$ROOT/../cursor/plugins/pack-monai" \
    "$HOME/.cursor/plugins/local/pack-monai"
  do
    if [[ -f "$d/scripts/check-deprecations.sh" ]]; then
      echo "$d"
      return
    fi
  done
  echo ""
}

PACK="$(_resolve_pack)"
if [[ -z "$PACK" ]]; then
  cat >&2 <<'EOF'
ERROR: pack-monai not found.

Set CURSOR_ONBOARDING_PACK, or place plugins at one of:
  .ci/cursor-platform/plugins/pack-monai
  ../cursor/plugins/pack-monai
  ~/.cursor/plugins/local/pack-monai

CI: ensure the cursor-play checkout step succeeded.
See docs/cursor-kit/productization/PRODUCTIZATION.md
EOF
  exit 1
fi
exec bash "$PACK/scripts/check-deprecations.sh" "$@"
