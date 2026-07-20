#!/usr/bin/env bash
# sync-check.sh — smoke alarm for Cursor kit path drift
#
# Purpose: confirm every file the kit points at still exists on disk. Rules and
# skills tell agents to read paths like CONTRIBUTING.md or monai-refs/*.md; if
# someone renames or deletes those files, agents get bad guidance silently.
# sync-check catches that before merge.
#
# What it checks (two passes):
#   1. Rules cross-check — parse "Source of truth:" lines in .cursor/rules/*.mdc
#      and verify each backtick path exists.
#   2. Kit inventory — verify a fixed list of hooks, skills, docs, scripts, and
#      CI workflow files exist (see REQUIRED KIT ARTIFACTS below).
#
# What it does NOT do:
#   - Run tests or lint
#   - Validate file contents or that agents followed the rules
#   - Prove conventions are correct — only that linked paths are present
#
# Exit codes: 0 = all paths found; 1 = one or more MISS
#
# When it runs:
#   - Manually: bash docs/cursor-kit/scripts/sync-check.sh
#   - CI: .github/workflows/cursor-kit-sync.yml on kit-related path changes
#
# Significance (panel / ownership): versioned kit + CODEOWNERS + this gate means
# the platform team owns maintainability — drift fails CI instead of teaching
# wrong norms. See docs/cursor-kit/README.md § Sync check and DEMO.md.
#
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

# REQUIRED KIT ARTIFACTS — fixed inventory (pass 2)
for req in \
  AGENTS.md \
  .cursor/hooks.json \
  .cursor/boundary-profile \
  .cursor/hooks/policy.py \
  .cursor/hooks/ledger_append.py \
  .cursor/hooks/session_start.py \
  .cursor/hooks/boundary_read.py \
  .cursor/hooks/boundary_shell.py \
  .cursor/hooks/nudge_style_test.py \
  .cursor/hooks/post_edit_nudge.py \
  .cursor/hooks/prompt_coach.py \
  .cursor/hooks/subagent_audit.py \
  docs/cursor-kit/README.md \
  docs/cursor-kit/DEMO.md \
  docs/cursor-kit/EVALUATION.md \
  docs/cursor-kit/monai-refs/transforms-array-dict.md \
  docs/cursor-kit/monai-refs/testing.md \
  docs/cursor-kit/monai-refs/contributing-checklist.md \
  docs/cursor-kit/monai-refs/deprecations.md \
  docs/cursor-kit/scripts/sync-check.sh \
  docs/cursor-kit/scripts/check-deprecations.sh \
  docs/cursor-kit/scripts/check-changelog.sh \
  docs/cursor-kit/scripts/ledger-report.py \
  docs/cursor-kit/scripts/ledger-dashboard.py \
  docs/cursor-kit/scripts/ledger-dashboard-plain.py \
  docs/cursor-kit/productization/manifest.json \
  docs/cursor-kit/productization/PRODUCTIZATION.md \
  .cursor/agents/spec-critic.md \
  .cursor/skills/triage-issues/SKILL.md \
  .cursor/skills/plan-feature/SKILL.md \
  .cursor/skills/critique-spec/SKILL.md \
  .cursor/skills/scaffold-transform/SKILL.md \
  docs/cursor-kit/scripts/score_tdd_gate.py \
  .cursor/skills/strengthen-tests/SKILL.md \
  .cursor/skills/prep-for-ci/SKILL.md \
  .cursor/skills/review-contribution/SKILL.md \
  .cursor/rules/50-losses.mdc \
  .cursor/rules/60-metrics.mdc \
  .cursor/rules/70-networks.mdc \
  docs/cursor-kit/monai-refs/losses.md \
  docs/cursor-kit/monai-refs/metrics.md \
  docs/cursor-kit/monai-refs/networks.md \
  .cursor/skills/scaffold-loss/SKILL.md \
  .cursor/skills/scaffold-metric/SKILL.md \
  .cursor/skills/scaffold-network/SKILL.md \
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
