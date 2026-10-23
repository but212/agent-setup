---
name: spec-drive
role: Coordinates contract-centered SDD and plan tracking
activation: "`/spec-drive`, contract-sensitive change, planning request"
modification-authority: Plan file and contract coordination
description: >
  Spec-Driven Development (SDD) orchestrator bridging crisp specification
  density with lean structural design, surgical TDD vertical slices, and plan
  tracking (.plans/YYYY-MM-DD/[task-name].md or agent plan artifacts).
---

# Spec-Driven Development (spec-drive)

Drive complex or contract-sensitive changes through high-density specifications, structural invariant enforcement, surgical TDD slices, and file-backed execution tracking.

## Operating Contract

`spec-drive` coordinates the requirement lifecycle through role adapters: Structural Designer (default: `lean-design`) owns structural modeling, Implementation Engine (default: `lean-mode`) owns production code changes, Review Gate (default: `lean-review`) audits changes, and `.plans/YYYY-MM-DD/[task-name].md` (or an agent plan artifact) tracks execution state.

1. **Crisp over Bloat:** Express concrete observable behavior, invariants, and input/output contracts; omit speculative requirements and decoration.
2. **Lean over Patchwork:** Eliminate impossible states before implementing logic; write only the code needed to satisfy contracts.
3. **Execution SSOT:** Track execution through `.plans/YYYY-MM-DD/[task-name].md` or an agent plan artifact. Synchronize permanent domain rules and architecture into permanent specifications.
4. **Authority Separation:** Permanent specifications govern domain rules and public contracts; plan files track execution progress and verification history.
5. **Approval Boundary:** Planning ends in review. Produce only a `planned` plan or analysis before explicit approval; do not modify production code, tests, or execute checklist items without explicit approval.

## Plan Tracking Lifecycle

When planning is requested or non-trivial execution begins:

1. **Search & Reuse:** Search `.plans/` across all date folders or active agent artifacts. Reuse an existing `planned`, `in-progress`, or `blocked` plan for the task. Never silently resume a `complete` or `cancelled` plan without asking.
2. **Path & Artifact Convention:** Create `.plans/YYYY-MM-DD/[task-name].md` using the plan creation date in ISO format and a lowercase kebab-case task name, or use an agent plan artifact when supported and preferred.
3. **State Transitions:**
   - `planned -> in-progress | cancelled`
   - `in-progress -> blocked | complete | cancelled`
   - `blocked -> in-progress | cancelled`
4. **Completion Rule:** Check checklist items only after verification passes. Do not mark the plan complete while criteria, checklist items, or blockers remain unresolved.

## The 4-Phase SDD Pipeline

### Phase 1: Crisp Specification

Establish clear boundaries and observable contracts before implementation:

- **Scope:** Concise goal, explicit In-Scope vs Out-of-Scope boundaries.
- **Contracts Table:**

| ID | Behavior / Scenario | Condition / Input | Expected Result / Error | Invariant | Test path/name | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| `C-01` | ... | ... | ... | ... | ... | ... |

Classify material claims as `Confirmed`, `Assumption`, or `Open decision`. Flag breaking changes to public APIs, schemas, or security for explicit approval.

### Phase 2: Structural Design Quality Gate (default: `lean-design`)

Delegate structural modeling to the Structural Designer role (default: `lean-design`) when states, types, schemas, or API boundaries change. If no structural model changes, record `None: <reason>` in the plan's Invariants section.
The Structural Design Quality Gate ensures:

- Makes invalid states unrepresentable using explicit types/enums.
- Identifies failure boundaries before happy paths.
- Assigns persistent `I-NN` IDs to explicit invariants and references their enforcement location.
- Contracts Table `Invariant` column references these `I-NN` IDs.

### Phase 3: Surgical TDD Implementation (default: `lean-mode`)

Execute implementation in small vertical slices mapped 1:1 to the Contracts Table in dependency order using the Implementation Engine role (default: `lean-mode`):

1. **Red:** Write smallest deterministic test exercising contract `C-NN`. Prove it fails as expected.
2. **Green:** Write minimal surgical code to make test pass (`lean-mode`). Touch only scoped files.
3. **Refactor:** Remove concrete duplication or simplify structure exposed after Green (or `None`).
4. **Verify:** Run repository-native command proving slice passes without regressions.

### Phase 4: Review Quality Gate, Living Spec Sync & Finish (default: `lean-review`)

- Enforce the Review Quality Gate: run Review Gate (default: `lean-review`) diff against the changes.
- If `Blocking: Yes` (P1 or P2 findings exist): add a surgical fix slice to the plan, apply the minimal fix via Implementation Engine (`lean-mode`), and re-run Review Gate (`lean-review`) diff until `Blocking: No`.
- If P3 findings exist: record them under Decisions and deviations as non-blocking notes.
- Run full repository test suite.
- Synchronize permanent specifications (architecture specs, `context.md`, ADRs) with any changed contracts.
- Mark plan complete only when `Blocking: No`, all checklist slices are checked, and verification passes.

## Plan File Format

When creating a plan file, use this structure:

```markdown
# Plan: [Task name]

- Status: `planned`
- Updated: [YYYY-MM-DD]
- Owner: [agent or user]

## Goal
[One concise outcome]

## Scope
- In: [explicit boundaries]
- Out: [explicit exclusions]

## Evidence and assumptions
- Confirmed: [paths, existing behavior, commands]
- Assumption: [unverified fact], or `None`

## Contracts
| ID | Behavior | Condition or Input | Expected Result | Invariant | Test path/name | Verification |
| --- | --- | --- | --- | --- | --- | --- |

## Invariants
[Invariants defined by lean-design with I-NN IDs and code locations, or None: <reason>]

## TDD slices and checklist
- [ ] 1. [Slice name] (`C-01`)
  - Red: `[test path]` - `[test name and expected failure]`
  - Green: `[source path]` - `[smallest required change]`
  - Refactor: `[concrete change]` or `None`
  - Verify: `[command]`

## Decisions and deviations
- [Date]: [Context and decision or deviation note]
```
