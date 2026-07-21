#!/usr/bin/env bash
# check-deprecations.sh — consumer entrypoint.
# Prefer pack-monai SSOT when available; else run embedded body (CI-safe).
# Keep embedded body in sync with pack-monai/scripts/check-deprecations.sh
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
if [[ -n "$PACK" ]]; then
  exec bash "$PACK/scripts/check-deprecations.sh" "$@"
fi

echo "check-deprecations: pack-monai unavailable — running consumer-embedded copy" >&2

# --- embedded fallback ---
cd "$ROOT"

RULES_DOC=".cursor/refs/deprecations.md"
if [[ ! -f "$RULES_DOC" ]]; then
  echo "ERROR: missing $RULES_DOC"
  exit 1
fi

files=()
if [[ "$#" -gt 0 ]]; then
  files=("$@")
else
  while IFS= read -r f; do
    [[ -n "$f" ]] && files+=("$f")
  done < <(git status --porcelain 2>/dev/null \
             | sed 's/^...//' \
             | grep -E '^(monai/(transforms|losses|metrics|networks/blocks)/|tests/(transforms|losses|metrics|networks/blocks)/).*\.py$' || true)
fi

if [[ "${#files[@]}" -eq 0 ]]; then
  echo "check-deprecations: no kit-scoped source/test files to scan (clean)."
  exit 0
fi

rules="$(awk '/<!-- deprecations:start -->/{f=1;next} /<!-- deprecations:end -->/{f=0} f' "$RULES_DOC" \
          | grep -E '\|' || true)"
if [[ -z "$rules" ]]; then
  echo "ERROR: no rules found in $RULES_DOC (deprecations:start/end block)"
  exit 1
fi

found=0
while IFS= read -r rule; do
  [[ -z "$rule" ]] && continue
  pattern="$(echo "$rule" | sed -E 's/[[:space:]]*\|.*$//' | sed -E 's/^[[:space:]]+//;s/[[:space:]]+$//')"
  reason="$(echo "$rule" | sed -E 's/^[^|]*\|[[:space:]]*//')"
  [[ -z "$pattern" ]] && continue
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    if matches="$(grep -nE "$pattern" "$f" 2>/dev/null)"; then
      while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        echo "DEPRECATED  $f:$hit"
        echo "            -> $reason"
        found=$((found + 1))
      done <<< "$matches"
    fi
  done
done <<< "$rules"

if [[ "$found" -gt 0 ]]; then
  echo "check-deprecations: $found deprecated API usage(s) found."
  exit 1
fi
echo "check-deprecations: clean (${#files[@]} file(s) scanned)."
exit 0
