#!/usr/bin/env bash
# check-changelog.sh — consumer entrypoint.
# Prefer pack-monai SSOT when available; else run embedded body (CI-safe).
# Keep embedded body in sync with pack-monai/scripts/check-changelog.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export CURSOR_PROJECT_DIR="${CURSOR_PROJECT_DIR:-$ROOT}"

_resolve_pack() {
  local d
  if [[ -n "${CURSOR_ONBOARDING_PACK:-}" && -f "${CURSOR_ONBOARDING_PACK}/scripts/check-changelog.sh" ]]; then
    echo "${CURSOR_ONBOARDING_PACK}"
    return
  fi
  for d in \
    "$ROOT/.ci/cursor-platform/plugins/pack-monai" \
    "$ROOT/../cursor/plugins/pack-monai" \
    "$HOME/.cursor/plugins/local/pack-monai"
  do
    if [[ -f "$d/scripts/check-changelog.sh" ]]; then
      echo "$d"
      return
    fi
  done
  echo ""
}

PACK="$(_resolve_pack)"
if [[ -n "$PACK" ]]; then
  exec bash "$PACK/scripts/check-changelog.sh" "$@"
fi

echo "check-changelog: pack-monai unavailable — running consumer-embedded copy" >&2

# --- embedded fallback ---
cd "$ROOT"

CHANGELOG="CHANGELOG.md"
if [[ ! -f "$CHANGELOG" ]]; then
  echo "ERROR: missing $CHANGELOG"
  exit 1
fi
if [[ "$#" -eq 0 ]]; then
  echo "usage: check-changelog.sh <SymbolName> [SymbolName ...]"
  exit 1
fi

unreleased="$(awk '
  /^## \[Unreleased\]/ {inblk=1; next}
  /^## \[/ && inblk {inblk=0}
  inblk {print}
' "$CHANGELOG")"

if [[ -z "$unreleased" ]]; then
  echo "ERROR: no '## [Unreleased]' section with content in $CHANGELOG"
  exit 1
fi

missing=0
for name in "$@"; do
  if grep -qF "$name" <<< "$unreleased"; then
    echo "OK   $name documented under [Unreleased]"
  else
    echo "MISS $name not found under [Unreleased]"
    missing=$((missing + 1))
  fi
done

if [[ "$missing" -gt 0 ]]; then
  cat <<EOF
check-changelog: $missing symbol(s) undocumented.
Add a bullet under '## [Unreleased]' -> '### Added' in $CHANGELOG, e.g.:
  * \`RobustScaleIntensity\` / \`RobustScaleIntensityd\`: robust median/IQR intensity scaling.
EOF
  exit 1
fi
echo "check-changelog: all documented."
exit 0
