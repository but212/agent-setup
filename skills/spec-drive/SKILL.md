---
name: spec-drive
description: >
  Spec-Driven Development (SDD) orchestrator bridging crisp specification density
  with lean structural design, surgical TDD vertical slices, and living spec synchronization.
  Activate with /spec-drive.
---

# Spec-Driven Development (spec-drive)

Drive complex or contract-sensitive changes through high-density specifications, structural invariant enforcement, and surgical TDD slices. Use a reduced path for simple, local changes.

## Operating Contract

`spec-drive` defines the requirement boundary and coordinates delegation: `lean-design` owns structure, `tdd-plan` owns test slices, and `lean-mode` owns production edits.

1. **Crisp over Bloat:** Express concrete observable behavior, invariants, and input/output contracts; omit speculative requirements and decoration.
2. **Lean over Patchwork:** Eliminate impossible states before implementing logic; write only the code needed to satisfy contracts.
3. **Bounded Generalization:** Extract `condition -> guarantee` laws only from multiple cases or explicit domain evidence. State scope, preconditions, exceptions, and counterexamples; reject one-case restatements and unsupported abstractions. Promote laws to shared rules only with cross-boundary recurrence or clear reuse evidence.
4. **Evidence-Gated Pipeline:** Follow the 4 phases. Stop for review on breaking changes, major architectural trade-offs, genuine ambiguity, or before implementation without explicit approval.
5. **Living Spec Sync:** Keep execution contracts in `.plans/YYYY-MM-DD/<task-name>.md` when `mark-plan` is active; synchronize permanent domain and architecture docs in the same change.
6. **Authority Separation:** Permanent specifications govern domain rules, public contracts, and architecture; plans track execution scope and verification only.
7. **Composed Activation:** When `/crisp` is active with `/spec-drive`, `spec-drive` coordinates the task and `crisp` controls response prose only; it does not grant edit permission.

## The 4-Phase SDD Pipeline

Apply all four phases when the change affects domain rules, state transitions, public contracts, persistence, security, or a material architectural decision. For simple local changes, record only the relevant contract, verification, and documentation impact.

### Phase 1: Crisp Specification

Establish clear boundaries and observable contracts before modifying code:

- **Intent & Scope:** Single-paragraph summary of requirement. Explicit In-Scope vs Out-of-Scope boundaries.
- **Generalization Pass:** Group contracts and scenarios into cases, extract bounded law candidates from their shared relations, state each law's scope, preconditions, exceptions, and counterexamples, then link accepted laws to invariants, contracts, and tests. Reject candidates that merely restate one case or add speculative scope. If no law applies, record `None` and continue.
- **Invariants Matrix:** Allowed states, valid state transitions, and prohibited/impossible states.
- **Contracts Table:**

  | ID | Behavior / Scenario | Condition / Input | Expected Result / Error |
  | --- | --- | --- | --- |
  | `C-01` | ... | ... | ... |

For each contract, record linked invariants, test path and name, implementation boundary, and permanent specification path when applicable. For non-executable contracts, record the verification method.

*Rules:* If requirements contain ambiguity, stop and resolve with the user before writing implementation. Classify material claims as `Confirmed`, `Assumption`, or `Open decision`.

Treat changes to public inputs/outputs, error meaning, state transitions, persistence schemas, authentication, or authorization as breaking changes. Require explicit approval and compatibility, migration, and rollback decisions before implementation.

### Phase 2: Lean Structural Design (lean-design)

Delegate this phase to `lean-design`; do not duplicate its structural review in the specification.

Use accepted laws as inputs to design data models and state representations that make invalid states unrepresentable:

- Model transitions as explicit states, enums, or constrained types (avoid primitive obsession and loose booleans).
- Identify failure boundaries (nulls, boundary violations, data constraints, unhandled exceptions) before happy paths.
- Remove redundant abstractions, unused parameters, and speculative extension points.

### Phase 3: Surgical TDD Implementation (tdd-plan & lean-mode)

Delegate test slicing to `tdd-plan` and production changes to `lean-mode`; `spec-drive` tracks contract coverage but does not implement either.

Execute implementation in small, vertical slices mapped 1:1 to the Contracts Table in dependency order. For each accepted law, include a representative case and a boundary or failure case in the verification plan:

1. **Red:** Write smallest deterministic test exercising contract `C-NN`. Prove it fails with expected failure.
2. **Green:** Write minimal surgical code to make test pass (`lean-mode`). Touch only scoped files.
3. **Verify:** Run repository-native test runner proving slice passes without regressions.
4. **Refactor:** Remove duplication or polish structure exposed after Green (or `None`).

### Phase 4: Quality Gate & Spec Synchronization

Before declaring done, enforce repository quality boundaries:

1. **Contract Coverage:** Every defined contract that is executable and in scope has a passing automated test; document non-executable contracts and their verification method.
2. **Law Coverage:** Every accepted law is linked to an invariant or contract and has executable verification where practical. Do not promote a law to `context.md` or a shared rule without repeated cross-boundary evidence or explicit domain justification.
3. **Code Quality:** Pass all repository-native formatting, linting, and static analysis checks.
4. **Spec Synchronization:**
   - Check if changes alter domain models, API contracts, business rules, or platform invariants.
   - Classify material claims as `Confirmed`, `Assumption`, or `Open decision`.
   - Update repository specification documents (e.g., `docs/spec/`, architecture decision records, or contract references) in the same change.
   - Compare the skills catalog with actual `skills/*/SKILL.md` names, activation rules, and modification boundaries.
   - Run any repository-native catalog or policy validator and record its exact result.

## Output Format

When invoking `spec-drive`, present the task progress systematically:

```markdown
# Spec: [Feature / Task Name]

## 1. Intent & Boundaries
- In-Scope: ...
- Out-of-Scope: ...
- Assumptions: ...

## 2. General Laws
| ID | Law | Scope / Preconditions | Limits / Counterexample | Linked Contracts |
|---|---|---|---|---|
| `L-01` | ... | ... | ... | `C-01` |

## 3. Invariants & State Rules
- Valid States: ...
- Forbidden States: ...

## 4. Contracts Table
| ID | Behavior | Condition / Input | Expected Output / Error | Invariant | Test path/name | Implementation boundary | Permanent spec |
|---|---|---|---|---|---|---|---|
| C-01 | ... | ... | ... | ... | ... | ... | ... |

## 5. TDD Slices
- Slice 1 (C-01): Red (`[test path]`) -> Green (`[src path]`) -> Verify (`[cmd]`)
...

## 6. Quality & Spec Sync Check
- [ ] Contract tests passing
- [ ] Accepted laws linked to invariants or contracts and covered by representative plus boundary/failure tests
- [ ] Linter & static analysis passing
- [ ] Repository specs synchronized (or confirmed unchanged)
```

## Stabilization handoff

When the repository defines a candidate/stable policy, remain `candidate` until catalog parity, routing coverage, safety review, documentation consistency, and repository-native validation all pass. Record unresolved breaking-change decisions, blockers, and open questions instead of promoting the status optimistically.

## Plan handoff

When `mark-plan` is active, use its `.plans/YYYY-MM-DD/<task-name>.md` as the execution SSOT. Put the SDD contracts, laws, invariants, and TDD slices in the plan or link them from the plan; do not create a competing plan artifact.

## Controls & Revert

- **Scope:** Contract orchestration and synchronization decisions; do not directly edit production code or tests.
- **Approval:** Analysis and planning are read-only until explicit execution approval. Breaking changes also require compatibility, migration, and rollback decisions.
- **Activate:** `/spec-drive`, `/sdd`, or when asked for spec-driven development.
- **Deactivate:** `stop spec-drive` or return to normal mode.
