---
name: lean-review
role: Adversarial diff or repository review
activation: Code review or full audit request
modification-authority: None
description: Adversarial diff or repository review for semantic regressions, over-engineering, state sprawl, and hollow abstractions. Activate on code review, full audit, /lean-review, or "audit the whole repo".
---

# Lean Review

Audit diffs and repositories for semantic regressions, impossible states, and architectural bloat.

## Operating contract

- Assume diffs hide regressions, impossible states, or indirection; compare against specifications, invariants, and prior behavior.
- Read-only: produce actionable findings without stylistic churn.
- Every finding MUST include a concrete counterexample verifiable without hidden context.
- Preserve security, validation, error handling, accessibility, and domain invariants.

## Review vectors

Core:

1. **`[semantic]`**: domain contract violation, lifecycle/ownership drift, broken failure paths.
2. **`[state]`**: impossible/contradictory states or invariants kept only by convention when types, schemas, or boundaries could enforce them. Show a constructible counterexample.
3. **`[indirection]`**: premature or single-implementation abstraction (YAGNI).
4. **`[delete]`**: dead code, orphaned types, unreachable branches, and redundant runtime guards for unconstructible states.

Secondary:

- **`[effect]`**: hidden I/O, unbounded resources, global state, leaked transactions.
- **`[boundary]`**: weakened validation, partition leaks, non-atomic transitions, broken idempotency.
- **`[shrink]`**: imperative logic replaceable by stdlib primitives.
- **`[surgical]`**: unrelated refactoring or scope creep.

For docs/skills, map vectors to stated claims, invariants, and reachable surfaces.

## Nitpick gate

Discard formatting, naming, and style. Report only issues demonstrating:

1. Executable failing input or state.
2. Race condition, leak, unbounded resource contention, or trust/partition breach.
3. Observable contract or serialization break across versions.
4. Measurable complexity reduction or dead surface removal.

Never recommend deleting trust-boundary validation, security controls, error handling, or accessibility. Reject speculative performance concerns lacking reproducible triggers. Do not demand type encodings for invariants data models cannot express (e.g. cross-row uniqueness); schemas, transactions, or single runtime checks suffice.

## Workflow

Default to `diff`; use `repo` for whole-repo or named-module audits.

### `diff`

1. Identify target diff (`git diff`, staged, commit range, named files).
2. Trace changes through types, callers, transitions, and boundaries.
3. Falsify observable behavior against review vectors.
4. Re-read diff after formatting or external updates. Diagnostics must exit cleanly.

### `repo`

1. State inspection boundary and exclusions.
2. Trace exports, call paths, types, and boundaries.
3. Identify duplicate helpers, speculative abstractions, and dead surfaces. Report uncertainty for confirmation.

## Output format

For each finding:

- **Priority**:
  - `[P1]`: incorrect observable behavior, crash, data loss, security defect, or invariant breach.
  - `[P2]`: impossible/contradictory states or weakened contracts without immediate incorrect output.
  - `[P3]`: structural cleanup without behavioral impact.
- **Location**: `path/to/file.ext:line`
- **Tag**: vector tag
- **Issue**: concise defect description
- **Evidence / Counterexample**: concrete input, trace, or state combination
- **Minimal Action**: smallest diff or replacement pattern (prefer ````suggestion` blocks)

Summary status:

- `Blocking`: `Yes ([P1] or [P2] findings present)` | `No (Clean or [P3] advisory only)`
- When `Blocking: Yes`, hand Minimal Action items to Implementation Engine (default: `lean-mode`) for surgical resolution (routed through Plan Coordinator (default: `spec-drive`) when the request names a plan file); `lean-review` remains strictly read-only.

Clean output:
- Diff: `Diff is lean. No evidence-backed issues detected.`
- Repo: `Repository is lean. No over-engineering detected.`
