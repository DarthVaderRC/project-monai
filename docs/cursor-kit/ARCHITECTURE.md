# Architecture — Cursor kit + project-monai

Panel-facing diagrams for **how the setup is wired**: monorepo plugins, thin
consumer, load path, contribution spine, and enforcement layers.

**Spoken frame:** *platform-core is the portable factory floor; pack-monai is the
MONAI jig; project-monai is the job on the bench.*

Related: [`DEMO.md`](DEMO.md) (runbook), [`productization/PRODUCTIZATION.md`](productization/PRODUCTIZATION.md)
(seam), [`EVALUATION.md`](EVALUATION.md) (measurement), sibling
[`cursor/README.md`](../../../cursor/README.md).

---

## 1. High level — three pieces

```mermaid
flowchart LR
  subgraph monorepo ["cursor monorepo (SSOT)"]
    PC[platform-core plugin]
    PM[pack-monai plugin]
  end
  subgraph cursorApp ["Cursor IDE / Agent Desktop"]
    CZ[Customize: enable plugins]
    AG[Agent session]
  end
  subgraph consumer ["project-monai (thin consumer)"]
    CFG[".cursor/pack.config.json"]
    BP[".cursor/boundary-profile"]
    REF[".cursor/refs/ (materialized)"]
    LED[".cursor/usage/ledger.jsonl"]
    LIB[monai/ + tests/ + docs/cursor-kit/]
  end
  PC -->|hooks + persona shells + spec-critic| CZ
  PM -->|rules + scaffold-* skills| CZ
  CZ --> AG
  CFG -->|CURSOR_PROJECT_DIR| PC
  REF -->|on-demand @ / read| AG
  AG --> LIB
  AG --> LED
  BP -->|strict / everyday| PC
```

| Piece | Owns | Does not own |
|---|---|---|
| **platform-core** | Boundary/ledger/nudge engine, `/triage` `/plan` `/critique-spec` `/strengthen` `/prep-for-ci` `/review` shells, `spec-critic`, score/judge runners | MONAI paths, rule text |
| **pack-monai** | Rules `00–70`, `/scaffold-*`, refs **SSOT**, pack.config schema + example | Hook engine |
| **project-monai** | Library code, DEMO/EVAL, `pack.config` **instance**, materialized refs, ledger | Duplicate rules/skills as SSOT |

---

## 2. Plugin load path (what you enable)

```mermaid
sequenceDiagram
  participant Dev as You
  participant Disk as ~/.cursor/plugins/local/
  participant UI as Customize
  participant WS as project-monai workspace
  participant Hook as workspaceOpen (optional)
  participant Agent as Agent chat

  Dev->>Disk: cp platform-core + pack-monai
  Dev->>UI: Enable both plugins (User-scoped OK)
  Dev->>WS: Open folder / Agent Desktop workspace
  opt Upgrade path
    WS->>Hook: workspaceOpen
    Hook->>UI: pluginPaths from pack.config "pack"
  end
  Dev->>Agent: New chat
  UI->>Agent: Inject rules + skills + hooks + spec-critic
  Agent->>WS: /init-pack if refs missing
  WS->>WS: Materialize pack refs → .cursor/refs/
```

**v1 reality:** manual enable in Customize is the reliable path. `workspaceOpen → pluginPaths` exists in core as a bonus after reload.

**Talk track:** *Plugins are User-scoped in the spike; the workspace still gets pack rules because the agent session is on project-monai with both plugins on.*

---

## 3. Split-by-reader (why config is not “in the pack plugin”)

Cursor has **no** cross-plugin filesystem for hooks. So readers differ:

```mermaid
flowchart TB
  subgraph injected ["Injected by Cursor when plugin enabled"]
    R[pack rules *.mdc]
    S[skills / agents]
    H[platform-core hooks]
  end
  subgraph ondisk ["On disk in consumer - hooks can read"]
    CFG[".cursor/pack.config.json"]
    REF[".cursor/refs/*.md"]
    BP[boundary-profile]
  end
  Agent[Agent LLM context]
  HookEng[Hook process policy.py etc]

  R --> Agent
  S --> Agent
  REF -->|agent Read / @ attach| Agent
  CFG -->|CURSOR_PROJECT_DIR| HookEng
  BP --> HookEng
  H --> HookEng
```

| Content | How it reaches the agent / hooks |
|---|---|
| Rules + skills | Cursor **injects** |
| Refs | Pack SSOT → `/init-pack` → consumer `.cursor/refs/` → agent reads |
| Allowlists, coach, nudge globs, TDD paths | Consumer `pack.config.json` → hooks via `CURSOR_PROJECT_DIR` |

---

## 4. Contribution spine (workflow)

Seven `/` skills on the live path (plus Layer T tests between plan and critique):

```mermaid
flowchart TD
  T["/triage-issues"] --> P["/plan-feature → SPEC.md"]
  P --> R[Layer T red tests]
  R --> C["/critique-spec → SPEC-REVIEW"]
  C --> G{"score_tdd_gate OK?"}
  G -->|no| STOP[Scaffold refuses]
  G -->|yes| ST[strict + deny probe]
  ST --> SC["/scaffold-transform"]
  SC --> QA["/strengthen-tests"]
  QA --> CI["everyday → /prep-for-ci"]
  CI --> RV["/review-contribution"]
  RV --> PR[Ready for fork PR]
```

**Topology (say once):** each persona owns a stage; handoff is **artifacts** (issue, SPEC, diff, verdict) — not a god-command. Subagents stay **intra-stage** (e.g. background review). Proposed follow-on: [ADR-0001 thin orchestrator](../../../cursor/docs/superpowers/specs/2026-07-21-thin-orchestrator-adr.md).

---

## 5. Low level — Layer T hard gate

```mermaid
flowchart LR
  subgraph artifacts ["Work artifacts"]
    SPEC["docs/cursor-kit/work/n/SPEC.md"]
    TEST["tests/... Layer T red"]
    REV["SPEC-REVIEW.md Verdict: Approve"]
  end
  subgraph gate ["score_tdd_gate.py"]
    CHK[Required sections + marker + verdict + ledger source=critique-spec]
  end
  subgraph scaffold ["/scaffold-*"]
    RUN[Run gate first]
    IMPL[Write monai/** + planted gaps]
  end
  SPEC --> CHK
  TEST --> CHK
  REV --> CHK
  Critic[spec-critic agent model pin] --> REV
  RUN --> CHK
  CHK -->|exit 0| IMPL
  CHK -->|exit ≠ 0| Refuse[Stop — no prod edits]
```

Only **enforceable** model pin in v1: `spec-critic` agent frontmatter (`cursor-grok-4.5-high-fast`). Skills do not honor `model:`.

---

## 6. Low level — guardrails stack

```mermaid
flowchart TB
  subgraph hard ["Hard — can deny"]
    AL[pack.config allowlists strict / everyday]
    SH[beforeShellExecution / beforeReadFile]
  end
  subgraph soft ["Soft — prompt / nudge"]
    RU[Rules 00–70]
    CO[prompt coach e.g. soft-clip]
    NU[post-edit nudges]
  end
  subgraph gates ["Gates / eval"]
    T[Layer T score_tdd_gate]
    A[Layer A process]
    C[Layer C trajectory]
    D[Layer D judge additive]
    E[Layer E model_id cost only]
  end
  Agent --> soft
  Agent --> hard
  Agent --> gates
```

Hooks ≠ OS sandbox. Strict = contribution boundary; everyday = org boundary.

---

## 7. Where files live (cheat sheet)

```text
cursor/
  plugins/platform-core/   hooks, persona skills, spec-critic, score_trajectory, llm_judge
  plugins/pack-monai/      rules, scaffold-*, refs SSOT, pack.config schema/example
project-monai/
  .cursor/pack.config.json boundary-profile refs/ usage/
  docs/cursor-kit/         DEMO EVAL ARCHITECTURE scripts/ (wrappers + A/B scorers)
  monai/ tests/            library under contribution
```

Consumer `docs/cursor-kit/scripts/*` are mostly **thin wrappers** → `platform-core` (or pack scripts for deprecations/changelog).
