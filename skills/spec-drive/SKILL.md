---
name: spec-drive
role: Coordinates contract-centered SDD and plan tracking
activation: "`/spec-drive`, contract-sensitive change, planning request"
modification-authority: Plan file and contract coordination
description: Spec-Driven Development (SDD) orchestrator bridging crisp specification density with lean structural design, surgical TDD vertical slices, and plan tracking (.plans/YYYY-MM-DD/[task-name].md or agent plan artifacts).
---

# Spec-Driven Development (spec-drive)

Drive contract-sensitive changes via high-density specifications, structural invariants, surgical TDD slices, and execution tracking.

## Operating Contract

`spec-drive` coordinates the requirement lifecycle through role adapters: Structural Designer (default: `lean-design`) owns structural modeling, Implementation Engine (default: `lean-mode`) owns production code changes, Review Gate (default: `lean-review`) audits changes, and `.plans/YYYY-MM-DD/[task-name].md` (or an agent plan artifact) tracks execution state.

### Role Registry

This table is the single source of role bindings. Other skills reference these roles by name and default only.

| Role | Default skill | Owns | Input | Output |
| --- | --- | --- | --- | --- |
| Plan Coordinator | `spec-drive` (this skill) | `.plans/` file, lifecycle, checklist | Decision Summary (`challenge`), Blocking status (`lean-review`) | Plan file |
| Structural Designer | `lean-design` | `I-NN` invariants, Handoff Contract | Contracts Table | Handoff Contract |
| Implementation Engine | `lean-mode` | Code and test changes | Plan slice or Handoff Contract | Verification Record (`lean-mode`) |
| Review Gate | `lean-review` | Findings, `Blocking` status | Diff or named files | Findings with `Blocking` |

1. **Crisp over Bloat:** Observable behavior, invariants, and I/O contracts over speculative decoration.
2. **Lean over Patchwork:** Eliminate impossible states before implementing code.
3. **Execution SSOT:** Track execution in `.plans/YYYY-MM-DD/[task-name].md` or an agent plan artifact; sync domain rules into permanent specifications.
4. **Authority Separation:** Permanent specifications govern domain rules and contracts; plan files track execution progress and verification history.
5. **Approval Boundary:** Planning ends in review. Produce only a `planned` plan or analysis before explicit approval; do not modify production code, tests, or execute checklist items without approval.

## Plan Tracking Lifecycle

1. **Search & Reuse:** Search `.plans/` across date folders or active agent artifacts; reuse `planned`, `in-progress`, or `blocked` plans. Never silently resume `complete` or `cancelled` plans.
2. **Convention:** Create `.plans/YYYY-MM-DD/[task-name].md` (ISO date, lowercase kebab-case name) or an agent plan artifact.
3. **State Transitions:**
   - `planned -> in-progress | cancelled`
   - `in-progress -> blocked | complete | cancelled`
   - `blocked -> in-progress | cancelled`
4. **Completion:** Mark complete only when all criteria, checklist items, and verification pass without unresolved blockers.

## The 4-Phase SDD Pipeline

### Phase 1: Crisp Specification

Establish boundaries and observable contracts:

- **Scope:** Concise goal, explicit In-Scope and Out-of-Scope boundaries.
- **Contracts Table:**

| ID | Behavior / Scenario | Condition / Input | Expected Result / Error | Invariant | Test path/name | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| `C-01` | ... | ... | ... | ... | ... | ... |

Classify claims as `Confirmed`, `Assumption`, or `Open decision`. Flag breaking API, schema, or security changes for explicit approval.

### Phase 2: Structural Design Quality Gate (default: `lean-design`)

Delegate structural modeling to Structural Designer (default: `lean-design`) when states, types, schemas, or API boundaries change (or record `None: <reason>`).
The Structural Design Quality Gate ensures:

- Invalid states are unrepresentable via explicit types/enums.
- Failure boundaries are identified before happy paths.
- Persistent `I-NN` invariant IDs with enforcement locations are assigned and referenced in the Contracts Table.

### Phase 3: Surgical TDD Implementation (default: `lean-mode`)

Implement vertical slices mapped 1:1 to the Contracts Table in dependency order via Implementation Engine (default: `lean-mode`):

1. **Red:** Write smallest deterministic test exercising contract `C-NN`; prove it fails as expected.
2. **Green:** Write minimal surgical code to pass the test (`lean-mode`) in scoped files.
3. **Refactor:** Remove concrete duplication or simplify structure exposed after Green (or `None`).
4. **Verify:** Run repository-native command proving the slice passes without regressions. Report it as a Verification Record (`lean-mode` format); check the item only on `Result: pass`.

### Phase 4: Review Quality Gate, Living Spec Sync & Finish (default: `lean-review`)

- Enforce Review Quality Gate: run Review Gate (default: `lean-review`) diff against changes.
- If `Blocking: Yes` (P1/P2 findings): add a fix slice, apply minimal fix via Implementation Engine (`lean-mode`), and re-run Review Gate (`lean-review`) until `Blocking: No`.
- If P3 findings exist: record under Decisions and deviations as non-blocking notes.
- Run full test suite, synchronize permanent specifications (`context.md`, ADRs), and mark plan complete only when `Blocking: No` and all checklist items pass.

## Plan File Format

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
