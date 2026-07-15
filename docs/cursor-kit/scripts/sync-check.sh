#!/usr/bin/env bash
# Verify Cursor kit "Source of truth" paths still exist.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

RULES_DIR=".cursor/rules"
missing=0
checked=0

echo "sync-check: root=$ROOT"

if [[ ! -d "$RULES_DIR" ]]; then
  echo "ERROR: missing $RULES_DIR"
  exit 1
fi

# Extract backtick paths from Source of truth lines in rules.
while IFS= read -r line; do
  # Collect `path` tokens; skip section titles in parentheses by taking only path-like tokens
  while [[ "$line" =~ \`([^\`]+)\` ]]; do
    token="${BASH_REMATCH[1]}"
    line="${line#*\`${token}\`}"
    # Skip prose fragments that are not filesystem paths
    if [[ "$token" == *" "* ]] && [[ "$token" != *"/"* ]]; then
      continue
    fi
    # Strip parenthetical notes: "CONTRIBUTING.md (Unit testing)" → CONTRIBUTING.md
    path="${token%% (*}"
    path="${path%%)}"
    path="${path%/}"

    # Directories referenced without trailing files
    if [[ "$path" == "docs/cursor-kit/monai-refs" ]]; then
      path="docs/cursor-kit/monai-refs"
    fi
    if [[ "$path" == ".github/workflows" || "$path" == ".github/workflows/" ]]; then
      path=".github/workflows"
    fi

    checked=$((checked + 1))
    if [[ -e "$path" ]]; then
      echo "OK   $path"
    else
      echo "MISS $path"
      missing=$((missing + 1))
    fi
  done
done < <(grep -h "Source of truth:" "$RULES_DIR"/*.mdc || true)

# Required kit artifacts
for req in \
  AGENTS.md \
  .cursor/hooks.json \
  .cursor/boundary-profile \
  docs/cursor-kit/README.md \
  docs/cursor-kit/DEMO.md \
  docs/cursor-kit/monai-refs/transforms-array-dict.md \
  docs/cursor-kit/monai-refs/testing.md \
  docs/cursor-kit/monai-refs/contributing-checklist.md \
  .cursor/skills/triage-issues/SKILL.md \
  .cursor/skills/plan-feature/SKILL.md \
  .cursor/skills/scaffold-transform/SKILL.md \
  .cursor/skills/strengthen-tests/SKILL.md \
  .cursor/skills/prep-for-ci/SKILL.md \
  .cursor/skills/review/SKILL.md \
  .github/workflows/cursor-kit-sync.yml
do
  checked=$((checked + 1))
  if [[ -e "$req" ]]; then
    echo "OK   $req"
  else
    echo "MISS $req"
    missing=$((missing + 1))
  fi
done

echo "sync-check: checked=$checked missing=$missing"
if [[ "$missing" -gt 0 ]]; then
  exit 1
fi
exit 0
