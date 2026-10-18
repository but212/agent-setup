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

`spec-drive` coordinates the requirement lifecycle: `lean-design` owns structural modeling, `lean-mode` owns production code changes, and `.plans/YYYY-MM-DD/[task-name].md` (or an agent plan artifact) tracks execution state.

1. **Crisp over Bloat:** Express concrete observable behavior, invariants, and input/output contracts; omit speculative requirements and decoration.
2. **Lean over Patchwork:** Eliminate impossible states before implementing logic; write only the code needed to satisfy contracts.
3. **Execution SSOT:** Track execution through `.plans/YYYY-MM-DD/[task-name].md` or an agent plan artifact. Synchronize permanent domain rules and architecture into repository documentation.
4. **Authority Separation:** Permanent specifications govern domain rules and public contracts; plan files track execution progress and verification history.
5. **Approval Boundary:** Planning ends in review. Produce only a `planned` plan or analysis before explicit approval; do not modify production code, tests, or execute checklist items without explicit approval.
6. **Composed Activation:** When `/crisp` is active with `/spec-drive`, `spec-drive` coordinates the task while `crisp` controls response prose density.

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
- **Invariants Matrix:** Allowed states, valid transitions, and prohibited states.
- **Contracts Table:**

| ID | Behavior / Scenario | Condition / Input | Expected Result / Error | Invariant | Test path/name | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| `C-01` | ... | ... | ... | ... | ... | ... |

Classify material claims as `Confirmed`, `Assumption`, or `Open decision`. Flag breaking changes to public APIs, schemas, or security for explicit approval.

### Phase 2: Lean Structural Design (lean-design)

Delegate data models and type boundaries to `lean-design`:

- Make invalid states unrepresentable using explicit types/enums.
- Identify failure boundaries before happy paths.
- Remove redundant abstractions and speculative extension points.

### Phase 3: Surgical TDD Implementation

Execute implementation in small vertical slices mapped 1:1 to the Contracts Table in dependency order:

1. **Red:** Write smallest deterministic test exercising contract `C-NN`. Prove it fails as expected.
2. **Green:** Write minimal surgical code to make test pass (`lean-mode`). Touch only scoped files.
3. **Verify:** Run repository-native command proving slice passes without regressions.
4. **Refactor:** Remove concrete duplication or simplify structure exposed after Green (or `None`).

### Phase 4: Review, Living Spec Sync & Finish

- Run full repository test suite.
- Synchronize permanent documentation (`AGENTS.md`, architecture specs) with any changed contracts.
- Mark plan complete only when every item and acceptance criterion is verified.

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

## Acceptance criteria
- [ ] `C-01` - [Observable requirement]

## Checklist
- [ ] `C-01` **[Step name]** - `[target paths]`; verify: `[command or result]`

## Contracts
| ID | Behavior | Condition or Input | Expected Result | Invariant | Test path/name | Verification |
| --- | --- | --- | --- | --- | --- | --- |

## TDD Slices
### 1. [Slice name]
- Red: `[test path]` - `[test name and expected failure]`
- Green: `[source path]` - `[smallest required change]`
- Verify: `[command]`
- Refactor: `[concrete change]` or `None`
```
