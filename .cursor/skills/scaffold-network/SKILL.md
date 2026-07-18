---
name: scaffold-network
description: >-
  Engineer workflow: implement a new network block under monai/networks/blocks/
  by mirroring a named neighbor, register it, and add 2D+3D tests with one planted
  QA gap. Use when the user runs /scaffold-network. Prefer MONAI_CURSOR_BOUNDARY=strict.
disable-model-invocation: true
---

# /scaffold-network (Engineer)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"scaffold-network","persona":"engineer","stage":"build","profile":"strict"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Refs (load only these)

- `@docs/cursor-kit/monai-refs/networks.md`
- `.cursor/rules/70-networks.mdc`
- Named neighbors: `monai/networks/blocks/mlp.py` (`MLPBlock`) and, if using spatial_dims layers, `monai/networks/blocks/aspp.py`. Do not read the whole `monai/networks/` package.

## Intra-stage specialist dispatch (recommended for this pack)

Networks carry the heaviest context. The Engineer SHOULD delegate this skill body to a depth-1 specialist subagent (isolated window) so the block's neighbor context does not bloat the main chat. The reviewer may separately run `/review-contribution` as a background subagent. Never advance to another persona's stage.

## Steps

1. Read the issue and the named neighbor(s).
2. Create `monai/networks/blocks/<name>.py` (subclass `nn.Module`; support 2D/3D via `spatial_dims`).
3. Apache header; `from __future__ import annotations`; Google docstrings.
4. Register `from .<name> import <Class>` in `monai/networks/blocks/__init__.py` (alphabetical by module name).
5. Add `tests/networks/blocks/test_<name>.py` with 2D AND 3D cases under `eval_mode`.

## Planted QA defect (required — intentional, tool-detectable training signal)

Leave the `from .<name> import <Class>` line **out** of `monai/networks/blocks/__init__.py`. Surfaces as `ImportError` at test/import time. Handoff note: "Planted: block missing from `monai/networks/blocks/__init__.py` — caught at import time. For `/strengthen-tests`."

## Stop when

Block + 2D/3D tests exist, registration gap remains, handoff note cites issue URL + planted defect. Do not run full CI.
