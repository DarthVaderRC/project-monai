# Architecture — Cursor kit + project-monai

Panel-facing diagrams for **how the setup is wired**: monorepo plugins, thin
consumer, load path, contribution spine, and enforcement layers.

**Spoken frame:** *platform-core is the portable factory floor; pack-monai is the
MONAI jig; project-monai is the job on the bench.*

**View tip:** Cursor / GitHub render Mermaid live. For slides, paste a diagram into
[Mermaid Live Editor](https://mermaid.live) → Export PNG/SVG (theme already set
below for print contrast).

Related: [`DEMO.md`](DEMO.md) · [`productization/PRODUCTIZATION.md`](productization/PRODUCTIZATION.md)
· [`EVALUATION.md`](EVALUATION.md) · sibling [`cursor/README.md`](../../../cursor/README.md)

---

## Legend (all diagrams)

| Color | Role |
|---|---|
| Teal | **platform-core** (portable engine) |
| Sand | **pack-monai** (library content) |
| Sage | **project-monai** consumer / workspace |
| Amber | Gate / decision |
| Rose | Refuse / deny |
| Green | Pass / approve path |

---

## 1. High level — three pieces

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "ui-sans-serif, system-ui, sans-serif",
    "fontSize": "15px",
    "primaryTextColor": "#142033",
    "lineColor": "#5c6b7a",
    "tertiaryTextColor": "#142033"
  }
}}%%
flowchart TB
  subgraph SSOT["cursor monorepo — plugin SSOT"]
    direction LR
    PC["platform-core<br/><small>hooks · persona shells · spec-critic</small>"]
    PM["pack-monai<br/><small>rules · scaffold-* · refs SSOT</small>"]
  end

  subgraph HOST["Cursor IDE / Agent Desktop"]
    direction TB
    CZ["Customize<br/>enable both plugins"]
    AG["Agent session"]
    CZ --> AG
  end

  subgraph JOB["project-monai — thin consumer"]
    direction TB
    CFG["pack.config.json<br/>allowlists · TDD paths"]
    REF[".cursor/refs/<br/>materialized"]
    LIB["monai/ · tests/<br/>docs/cursor-kit/"]
    LED["usage/ledger.jsonl"]
  end

  PC -->|"hooks + shells + critic"| CZ
  PM -->|"rules + scaffold skills"| CZ
  CFG -.->|"CURSOR_PROJECT_DIR"| PC
  REF -->|"Read / @"| AG
  AG --> LIB
  AG --> LED

  classDef core fill:#cfe8ef,stroke:#1f5a6a,stroke-width:2px,color:#142033
  classDef pack fill:#ebe4d4,stroke:#6a5738,stroke-width:2px,color:#142033
  classDef host fill:#e8edf2,stroke:#3d4f63,stroke-width:2px,color:#142033
  classDef job fill:#d8e8de,stroke:#2f5c45,stroke-width:2px,color:#142033
  classDef meta fill:#f4f6f8,stroke:#8a96a3,stroke-width:1px,color:#142033
  class PC core
  class PM pack
  class CZ,AG host
  class CFG,REF,LIB,LED job
  class SSOT,HOST,JOB meta
  linkStyle default stroke:#5c6b7a,stroke-width:1.5px
```

| Piece | Owns | Does not own |
|---|---|---|
| **platform-core** | Boundary/ledger/nudge engine, persona skill shells, `spec-critic`, score/judge runners | MONAI paths, rule text |
| **pack-monai** | Rules `00–70`, `/scaffold-*`, refs **SSOT**, pack.config schema + example | Hook engine |
| **project-monai** | Library code, DEMO/EVAL, `pack.config` **instance**, materialized refs, ledger | Duplicate rules/skills as SSOT |

---

## 2. Plugin load path (what you enable)

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "ui-sans-serif, system-ui, sans-serif",
    "fontSize": "14px",
    "actorBkg": "#cfe8ef",
    "actorBorder": "#1f5a6a",
    "actorTextColor": "#142033",
    "signalColor": "#3d4f63",
    "signalTextColor": "#142033",
    "noteBkgColor": "#ebe4d4",
    "noteBorderColor": "#6a5738",
    "noteTextColor": "#142033",
    "activationBkgColor": "#d8e8de",
    "sequenceNumberColor": "#142033"
  }
}}%%
sequenceDiagram
  autonumber
  participant You
  participant Local as ~/.cursor/plugins/local
  participant UI as Customize
  participant WS as project-monai
  participant Agent as Agent chat

  You->>Local: Install platform-core + pack-monai
  You->>UI: Enable both (User-scoped OK)
  You->>WS: Open workspace
  Note over UI,WS: Optional: workspaceOpen → pluginPaths
  You->>Agent: New chat
  UI->>Agent: Inject rules · skills · hooks · spec-critic
  Agent->>WS: /init-pack (if refs missing)
  WS-->>Agent: .cursor/refs/ ready
```

**v1 reality:** manual Customize enable is the reliable path. `workspaceOpen → pluginPaths` is a bonus after reload.

**Talk track:** *Plugins are User-scoped in the spike; the agent session on project-monai still receives pack rules when both plugins are on.*

---

## 3. Split-by-reader (why config is not “in the pack plugin”)

Cursor has **no** cross-plugin filesystem for hooks. Readers differ:

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "ui-sans-serif, system-ui, sans-serif",
    "fontSize": "15px",
    "primaryTextColor": "#142033",
    "lineColor": "#5c6b7a"
  }
}}%%
flowchart LR
  subgraph INJ["Cursor injects"]
    direction TB
    R["Rules *.mdc"]
    S["Skills / agents"]
    H["Core hooks"]
  end

  subgraph DISK["Consumer disk<br/>hooks can read"]
    direction TB
    CFG["pack.config.json"]
    REF[".cursor/refs/"]
    BP["boundary-profile"]
  end

  Agent["Agent<br/>LLM context"]
  Hooks["Hook process<br/>policy.py …"]

  R ==> Agent
  S ==> Agent
  REF -->|"Read / @"| Agent
  CFG ==>|"CURSOR_PROJECT_DIR"| Hooks
  BP --> Hooks
  H ==> Hooks

  classDef inj fill:#ebe4d4,stroke:#6a5738,stroke-width:2px,color:#142033
  classDef disk fill:#d8e8de,stroke:#2f5c45,stroke-width:2px,color:#142033
  classDef run fill:#cfe8ef,stroke:#1f5a6a,stroke-width:2px,color:#142033
  classDef box fill:#f4f6f8,stroke:#8a96a3,stroke-width:1px,color:#142033
  class R,S,H inj
  class CFG,REF,BP disk
  class Agent,Hooks run
  class INJ,DISK box
```

| Content | How it reaches the agent / hooks |
|---|---|
| Rules + skills | Cursor **injects** |
| Refs | Pack SSOT → `/init-pack` → `.cursor/refs/` → agent reads |
| Allowlists, coach, nudge, TDD paths | `pack.config.json` → hooks via `CURSOR_PROJECT_DIR` |

---

## 4. Contribution spine (workflow)

Seven `/` skills on the live path (plus Layer T tests between plan and critique):

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "ui-sans-serif, system-ui, sans-serif",
    "fontSize": "14px",
    "primaryTextColor": "#142033",
    "lineColor": "#5c6b7a"
  }
}}%%
flowchart TD
  T["1 · /triage-issues"]
  P["2 · /plan-feature → SPEC.md"]
  R["3 · Layer T red tests"]
  C["4 · /critique-spec → Approve"]
  G{"5 · score_tdd_gate?"}
  STOP["Scaffold refuses"]
  ST["6 · strict + deny probe"]
  SC["7 · /scaffold-transform"]
  QA["8 · /strengthen-tests"]
  CI["9 · /prep-for-ci"]
  RV["10 · /review-contribution"]
  PR["Ready for fork PR"]

  T --> P --> R --> C --> G
  G -->|fail| STOP
  G -->|pass| ST --> SC --> QA --> CI --> RV --> PR

  classDef step fill:#cfe8ef,stroke:#1f5a6a,stroke-width:2px,color:#142033
  classDef gate fill:#f3dfc4,stroke:#9a6b2f,stroke-width:2px,color:#142033
  classDef bad fill:#f0d4d4,stroke:#8b3a3a,stroke-width:2px,color:#142033
  classDef good fill:#cfe8d8,stroke:#2d6a4f,stroke-width:2px,color:#142033
  class T,P,R,C,ST,SC,QA,CI,RV step
  class G gate
  class STOP bad
  class PR good
```

**Topology (say once):** each persona owns a stage; handoff is **artifacts** — not a god-command. Subagents stay **intra-stage**. Follow-on: [ADR-0001 thin orchestrator](../../../cursor/docs/superpowers/specs/2026-07-21-thin-orchestrator-adr.md).

---

## 5. Low level — Layer T hard gate

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "ui-sans-serif, system-ui, sans-serif",
    "fontSize": "14px",
    "primaryTextColor": "#142033",
    "lineColor": "#5c6b7a"
  }
}}%%
flowchart TB
  Critic["spec-critic agent<br/><i>model pin enforced</i>"]

  subgraph ART["Required artifacts"]
    direction LR
    SPEC["SPEC.md"]
    TEST["Layer T red tests"]
    REV["SPEC-REVIEW<br/>Verdict: Approve"]
  end

  Critic --> REV
  SPEC --> GATE
  TEST --> GATE
  REV --> GATE

  GATE{"score_tdd_gate.py"}
  GATE -->|exit 0| IMPL["/scaffold-*<br/>impl + planted gaps"]
  GATE -->|exit ≠ 0| NO["Refuse — no monai/** edits"]

  classDef art fill:#d8e8de,stroke:#2f5c45,stroke-width:2px,color:#142033
  classDef pin fill:#ebe4d4,stroke:#6a5738,stroke-width:2px,color:#142033
  classDef gate fill:#f3dfc4,stroke:#9a6b2f,stroke-width:2px,color:#142033
  classDef ok fill:#cfe8d8,stroke:#2d6a4f,stroke-width:2px,color:#142033
  classDef bad fill:#f0d4d4,stroke:#8b3a3a,stroke-width:2px,color:#142033
  class SPEC,TEST,REV art
  class Critic pin
  class GATE gate
  class IMPL ok
  class NO bad
```

Only **enforceable** model pin in v1: `spec-critic` (`cursor-grok-4.5-high-fast`). Skills do not honor `model:`.

---

## 6. Low level — guardrails stack

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "ui-sans-serif, system-ui, sans-serif",
    "fontSize": "14px",
    "primaryTextColor": "#142033",
    "lineColor": "#5c6b7a"
  }
}}%%
flowchart TB
  Agent(["Agent actions"])

  Agent --> HARD
  Agent --> SOFT
  Agent --> EVAL

  subgraph HARD["Hard — can deny"]
    direction LR
    AL["Allowlists<br/>strict / everyday"]
    SH["beforeReadFile<br/>beforeShellExecution"]
  end

  subgraph SOFT["Soft — can ignore"]
    direction LR
    RU["Rules 00–70"]
    CO["Prompt coach"]
    NU["Post-edit nudges"]
  end

  subgraph EVAL["Gates / eval"]
    direction LR
    LT["T · tdd_gate"]
    LA["A · process"]
    LC["C · trajectory"]
    LD["D · judge +"]
    LE["E · model_id $"]
  end

  classDef agent fill:#e8edf2,stroke:#3d4f63,stroke-width:2px,color:#142033
  classDef hard fill:#f0d4d4,stroke:#8b3a3a,stroke-width:2px,color:#142033
  classDef soft fill:#ebe4d4,stroke:#6a5738,stroke-width:2px,color:#142033
  classDef eval fill:#cfe8ef,stroke:#1f5a6a,stroke-width:2px,color:#142033
  class Agent agent
  class AL,SH hard
  class RU,CO,NU soft
  class LT,LA,LC,LD,LE eval
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
  docs/cursor-kit/         DEMO EVAL ARCHITECTURE scripts/
  monai/ tests/            library under contribution
```

Consumer `docs/cursor-kit/scripts/*` are mostly **thin wrappers** → `platform-core` (or pack scripts for deprecations/changelog).
