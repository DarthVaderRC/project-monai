#!/usr/bin/env bash
# sync-check.sh — consumer entrypoint.
#
# Prefer platform-core SSOT when available (local plugins / CI checkout).
# Otherwise run the embedded inventory below so pure-consumer CI still works
# (existence checks; refs drift skipped without pack SSOT).
#
# Keep the embedded body in sync with:
#   cursor/plugins/platform-core/scripts/sync-check.sh
#
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
if [[ -n "$CORE" ]]; then
  exec bash "$CORE/scripts/sync-check.sh" "$@"
fi

echo "sync-check: platform-core unavailable — running consumer-embedded inventory (drift skipped)" >&2

# --- embedded fallback (mirrors platform-core/scripts/sync-check.sh) ---
cd "$ROOT"
missing=0
checked=0
drift=0

echo "sync-check: root=$ROOT"

REF_INVENTORY=(
  transforms-array-dict.md
  testing.md
  contributing-checklist.md
  deprecations.md
  losses.md
  metrics.md
  networks.md
)

resolve_pack_refs() {
  if [[ -n "${CURSOR_ONBOARDING_PACK_REFS:-}" && -d "${CURSOR_ONBOARDING_PACK_REFS}" ]]; then
    echo "${CURSOR_ONBOARDING_PACK_REFS}"
    return
  fi
  if [[ -n "${CURSOR_ONBOARDING_PACK:-}" && -d "${CURSOR_ONBOARDING_PACK}/refs" ]]; then
    echo "${CURSOR_ONBOARDING_PACK}/refs"
    return
  fi
  local d
  for d in \
    "$ROOT/.ci/cursor-platform/plugins"/pack-*/refs \
    "$HOME/.cursor/plugins/local"/pack-*/refs \
    "$ROOT/../cursor/plugins"/pack-*/refs
  do
    if [[ -d "$d" ]]; then
      echo "$d"
      return
    fi
  done
  echo ""
}

resolve_pack_rules() {
  if [[ -n "${CURSOR_ONBOARDING_PACK_RULES:-}" && -d "${CURSOR_ONBOARDING_PACK_RULES}" ]]; then
    echo "${CURSOR_ONBOARDING_PACK_RULES}"
    return
  fi
  if [[ -n "${CURSOR_ONBOARDING_PACK:-}" && -d "${CURSOR_ONBOARDING_PACK}/rules" ]]; then
    echo "${CURSOR_ONBOARDING_PACK}/rules"
    return
  fi
  local d
  for d in \
    "$ROOT/.ci/cursor-platform/plugins"/pack-*/rules \
    "$HOME/.cursor/plugins/local"/pack-*/rules \
    "$ROOT/../cursor/plugins"/pack-*/rules
  do
    if [[ -d "$d" ]]; then
      echo "$d"
      return
    fi
  done
  if [[ -d "$ROOT/.cursor/rules" ]]; then
    echo "$ROOT/.cursor/rules"
    return
  fi
  echo ""
}

RULES_DIR="$(resolve_pack_rules)"
if [[ -n "$RULES_DIR" ]]; then
  echo "sync-check: rules_dir=$RULES_DIR"
  while IFS= read -r line; do
    while [[ "$line" =~ \`([^\`]+)\` ]]; do
      token="${BASH_REMATCH[1]}"
      line="${line#*\`${token}\`}"
      if [[ "$token" == *" "* ]] && [[ "$token" != *"/"* ]]; then
        continue
      fi
      path="${token%% (*}"
      path="${path%%)}"
      path="${path%/}"

      if [[ "$path" == ".cursor/refs" ]]; then
        path=".cursor/refs"
      fi
      if [[ "$path" == ".github/workflows" || "$path" == ".github/workflows/" ]]; then
        path=".github/workflows"
      fi

      checked=$((checked + 1))
      if [[ -e "$ROOT/$path" ]]; then
        echo "OK   $path"
      else
        echo "MISS $path"
        missing=$((missing + 1))
      fi
    done
  done < <(grep -h "Source of truth:" "$RULES_DIR"/*.mdc 2>/dev/null || true)
else
  echo "sync-check: rules_dir=(unavailable — skip Source-of-truth cross-check)"
fi

for req in \
  AGENTS.md \
  .cursor/pack.config.json \
  .cursor/boundary-profile \
  .cursor/refs \
  .cursor/usage \
  docs/cursor-kit/README.md \
  docs/cursor-kit/DEMO.md \
  docs/cursor-kit/EVALUATION.md \
  docs/cursor-kit/ARCHITECTURE.md \
  docs/cursor-kit/scripts/sync-check.sh \
  docs/cursor-kit/scripts/check-deprecations.sh \
  docs/cursor-kit/scripts/check-changelog.sh \
  docs/cursor-kit/scripts/ledger-report.py \
  docs/cursor-kit/scripts/ledger-dashboard.py \
  docs/cursor-kit/scripts/ledger-dashboard-plain.py \
  docs/cursor-kit/scripts/score_tdd_gate.py \
  docs/cursor-kit/scripts/score_trajectory.py \
  docs/cursor-kit/scripts/score_process.py \
  docs/cursor-kit/scripts/score_rubric.py \
  docs/cursor-kit/scripts/llm_judge.py \
  docs/cursor-kit/productization/manifest.json \
  docs/cursor-kit/productization/PRODUCTIZATION.md \
  .github/workflows/cursor-kit-sync.yml
do
  checked=$((checked + 1))
  if [[ -e "$ROOT/$req" ]]; then
    echo "OK   $req"
  else
    echo "MISS $req"
    missing=$((missing + 1))
  fi
done

echo "sync-check: refs existence under .cursor/refs/"
for name in "${REF_INVENTORY[@]}"; do
  checked=$((checked + 1))
  if [[ -f "$ROOT/.cursor/refs/$name" ]]; then
    echo "OK   .cursor/refs/$name"
  else
    echo "MISS .cursor/refs/$name"
    missing=$((missing + 1))
  fi
done

PACK_REFS="$(resolve_pack_refs)"
if [[ -n "$PACK_REFS" ]]; then
  echo "sync-check: pack_refs_ssot=$PACK_REFS (drift check on)"
  for name in "${REF_INVENTORY[@]}"; do
    checked=$((checked + 1))
    ssot="$PACK_REFS/$name"
    copy="$ROOT/.cursor/refs/$name"
    if [[ ! -f "$ssot" ]]; then
      echo "MISS pack-ssot $ssot"
      missing=$((missing + 1))
      continue
    fi
    if [[ ! -f "$copy" ]]; then
      echo "MISS $copy"
      missing=$((missing + 1))
      continue
    fi
    if cmp -s "$ssot" "$copy"; then
      echo "OK   drift-match $name"
    else
      echo "DRIFT .cursor/refs/$name != pack SSOT"
      drift=$((drift + 1))
    fi
  done
else
  echo "sync-check: pack_refs_ssot=(unavailable — skip drift; set CURSOR_ONBOARDING_PACK_REFS to enable)"
fi

echo "sync-check: checked=$checked missing=$missing drift=$drift"
if [[ "$missing" -gt 0 || "$drift" -gt 0 ]]; then
  exit 1
fi
exit 0
