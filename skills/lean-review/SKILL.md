---
name: lean-review
role: Adversarial diff or repository review
activation: Code review or full audit request
modification-authority: None
description: Adversarial diff or repository review for semantic regressions, over-engineering, state sprawl, and hollow abstractions. Activate on code review, full audit, /lean-review, or "audit the whole repo".
---

# Lean Review

Audit changes or repositories for semantic regressions, state explosions, and architectural bloat.

## Operating contract

- Start from the adversarial premise that the diff contains hidden edge-case failures, impossible states, or unnecessary indirection. Compare with specifications, invariants, and pre-change behavior.
- Read-only review: report actionable findings; do not perform arbitrary stylistic rewrites.
- Every finding MUST provide a concrete counterexample that a reader can evaluate as true or false without hidden context.
- Preserve safety controls, security, validation, error handling, accessibility, and domain invariants.

## Review vectors

Core:

1. **`[semantic]`**: Observable domain contract violation, temporal contract drift, or broken lifecycle / ownership / failure paths.
2. **`[state]`**: Data model permits contradictory or impossible states.
3. **`[indirection]`**: Premature or single-implementation abstraction (YAGNI).
4. **`[delete]`**: Dead code, orphaned types, unreachable branches, unused parameters.

Secondary (use only when clearly distinct from core):

- **`[effect]`**: Hidden I/O, unbounded resources, global mutable state, leaked transaction boundaries.
- **`[boundary]`**: Weakened validation, trust/partition leaks, non-atomic transitions, broken idempotency.
- **`[shrink]`**: Complex imperative logic replaceable by a clear stdlib/idiomatic primitive.
- **`[surgical]`**: Unrelated refactoring or scope creep.

Primary for code. For pure documentation or skill modules, map vectors onto the document's own claims, stated invariants, and reachable surface area.

## Nitpick gate

Discard formatting, naming, and stylistic preferences. Do not report an issue unless it demonstrates at least one of:

1. An executable failing input or state.
2. A race, leak, unbounded resource contention, or trust/partition boundary violation.
3. An observable contract or serialization break across temporal or version boundaries.
4. A measurable reduction in structural complexity or removal of unsupported surface area.

Do not recommend removing validation, error handling, security controls, accessibility mechanisms, or required business complexity. Reject speculative performance, scalability, or migration concerns without an executable, reproducible failure trigger.

## Workflow

Use `diff` by default; use `repo` for a repository-wide or named-module audit.

### `diff`

1. Identify the target diff (`git diff`, staged diff, commit range, or named files).
2. Trace changed lines through surrounding types, callers, state transitions, ownership, and boundaries.
3. Falsify observable behavior and failure paths against the review vectors.
4. Re-read the final diff after any formatter or external process changes. An inconclusive or timed-out diagnostic is not a clean result; rerun it with a sufficient wait budget before closing the review.

### `repo`

1. State the inspected repository or module boundary and excluded areas.
2. Trace exports, call paths, types, and boundaries using repository navigation tools.
3. Check duplicate helpers, custom stdlib replacements, speculative abstractions, and dead surfaces. Treat dynamic imports, runtime registration, generated entrypoints, and test-only reachability as uncertainty; report deletion candidates for confirmation.

## Output format

For each finding:

- **Priority**:
  - `[P1]`: Can produce incorrect observable behavior, crash, data loss, security issue, or hard invariant violation in a reachable scenario.
  - `[P2]`: Allows impossible/contradictory states or weakens a material contract, but does not by itself produce incorrect observable behavior.
  - `[P3]`: Structural cleanup with no contract or behavioral impact.
- **Location**: `path/to/file.ext:line`
- **Tag**: One tag from the taxonomy above
- **Issue**: Precise description of the defect
- **Evidence / Counterexample**: Concrete input, call trace, race, or code fact demonstrating failure
- **Minimal Action**: The smallest diff or replacement pattern (prefer GitHub ````suggestion` blocks for inline diffs)

Summary status:

- `Blocking`: `Yes ([P1] or [P2] findings present)` | `No (Clean or [P3] advisory only)`

If no issues exist for diff scope: `Diff is lean. No evidence-backed issues detected.`
If no issues exist for repo scope: `Repository is lean. No over-engineering detected.`
