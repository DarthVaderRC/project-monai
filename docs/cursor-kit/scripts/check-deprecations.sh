#!/usr/bin/env bash
# check-deprecations.sh — flag deprecated / removed APIs in touched transform files.
#
# Requirement #2 ("catch deprecated APIs early") made concrete. Rules are curated
# in docs/cursor-kit/monai-refs/deprecations.md between the machine-readable
# markers, so the platform team owns them (sync-check + CODEOWNERS) instead of
# hard-coding patterns here.
#
# Usage:
#   check-deprecations.sh [file ...]     # scan specific files
#   check-deprecations.sh                # scan changed transforms/tests files
#
# Exit 0 = clean, exit 1 = deprecated API found (suitable for CI and QA skill).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

RULES_DOC="docs/cursor-kit/monai-refs/deprecations.md"
if [[ ! -f "$RULES_DOC" ]]; then
  echo "ERROR: missing $RULES_DOC"
  exit 1
fi

# Collect target files: explicit args, else changed kit-scoped python files
# (transforms + Phase 1 loss/metric/network packs and their tests).
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

# Extract "regex | reason" rules between the machine-readable markers.
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
