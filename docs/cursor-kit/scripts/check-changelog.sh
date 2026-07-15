#!/usr/bin/env bash
# check-changelog.sh — ensure a user-facing change is documented for the next release.
#
# "Fit the path to production" includes the deploy step: a new public transform
# must appear under CHANGELOG.md's "## [Unreleased]" section so it ships in the
# next tagged release (release.yml) and weekly preview (weekly-preview.yml).
#
# Usage: check-changelog.sh <SymbolName> [SymbolName ...]
# Exit 0 = all names documented under [Unreleased]; exit 1 = missing.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
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

# Isolate the [Unreleased] block (from that header to the next '## [' header).
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
