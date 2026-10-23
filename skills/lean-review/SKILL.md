---
name: lean-review
role: Adversarial diff or repository review
activation: Code review or full audit request
modification-authority: None
description: Adversarial diff or repository review for semantic regressions, over-engineering, state sprawl, and hollow abstractions. Activate on code review, full audit, /lean-review, or "audit the whole repo".
---

# Lean Review

Audit changes or repositories for semantic regressions, state explosions, architectural bloat.

## Operating contract

- Assume the diff hides edge-case failures, impossible states, or unnecessary indirection. Compare against specifications, invariants, pre-change behavior.
- Read-only: report actionable findings; no stylistic rewrites.
- Every finding MUST include a concrete counterexample a reader can judge true or false without hidden context.
- Preserve safety controls, security, validation, error handling, accessibility, domain invariants.

## Review vectors

Core:

1. **`[semantic]`**: observable domain contract violation, temporal contract drift, broken lifecycle / ownership / failure paths.
2. **`[state]`**: data model permits a contradictory or impossible state, or an invariant lives only by convention (caller order, comments, docs) though a type, schema, or boundary parse could carry it. Counterexample must show a value or sequence the code can actually construct.
3. **`[indirection]`**: premature or single-implementation abstraction (YAGNI).
4. **`[delete]`**: dead code, orphaned types, unreachable branches, unused parameters, and runtime guards for violations a type, schema, or boundary parse already makes impossible on every reaching path.

Secondary (only when clearly distinct from core):

- **`[effect]`**: hidden I/O, unbounded resources, global mutable state, leaked transaction boundaries.
- **`[boundary]`**: weakened validation, trust/partition leaks, non-atomic transitions, broken idempotency.
- **`[shrink]`**: complex imperative logic replaceable by a clear stdlib/idiomatic primitive.
- **`[surgical]`**: unrelated refactoring or scope creep.

Primary for code. For pure documentation or skill modules, map vectors onto the document's own claims, stated invariants, reachable surface area.

## Nitpick gate

Discard formatting, naming, style. Report an issue only if it shows at least one of:

1. An executable failing input or state.
2. A race, leak, unbounded resource contention, or trust/partition violation.
3. An observable contract or serialization break across temporal or version boundaries.
4. A measurable reduction in structural complexity or removal of unsupported surface area.

Do not recommend removing validation, error handling, security controls, accessibility mechanisms, or required business complexity. Validation at a trust boundary is never a `[delete]` candidate. Reject speculative performance, scalability, or migration concerns without an executable, reproducible failure trigger.

Do not demand a type-level encoding for invariants the data model cannot express (cross-row uniqueness, temporal ordering). A schema constraint, transaction, or single documented runtime check at the point of violation suffices.

## Workflow

Use `diff` by default; `repo` for repository-wide or named-module audits.

### `diff`

1. Identify the target diff (`git diff`, staged diff, commit range, named files).
2. Trace changed lines through surrounding types, callers, state transitions, ownership, boundaries.
3. Falsify observable behavior and failure paths against the review vectors.
4. Re-read the final diff after any formatter or external process changes. An inconclusive or timed-out diagnostic is not a clean result; rerun it with a sufficient wait budget before closing the review.

### `repo`

1. State the inspected repository or module boundary and excluded areas.
2. Trace exports, call paths, types, boundaries using repository navigation tools.
3. Check duplicate helpers, custom stdlib replacements, speculative abstractions, dead surfaces. Treat dynamic imports, runtime registration, generated entrypoints, and test-only reachability as uncertainty; report deletion candidates for confirmation.

## Output format

For each finding:

- **Priority**:
  - `[P1]`: can produce incorrect observable behavior, crash, data loss, security issue, or hard invariant violation in a reachable scenario.
  - `[P2]`: allows impossible or contradictory states, or weakens a material contract, without by itself producing incorrect observable behavior.
  - `[P3]`: structural cleanup with no contract or behavioral impact.
- **Location**: `path/to/file.ext:line`
- **Tag**: one tag from the taxonomy above
- **Issue**: precise description of the defect
- **Evidence / Counterexample**: concrete input, call trace, race, or code fact demonstrating failure. For `[state]`, show the constructible value or sequence, such as a field combination the type permits.
- **Minimal Action**: smallest diff or replacement pattern (prefer GitHub ````suggestion` blocks for inline diffs)

Summary status:

- `Blocking`: `Yes ([P1] or [P2] findings present)` | `No (Clean or [P3] advisory only)`
- When `Blocking: Yes`, hand Minimal Action items to Implementation Engine (default: `lean-mode`) for surgical resolution (routed through the active Plan Coordinator (default: `spec-drive`) when present); `lean-review` remains strictly read-only.

If no issues exist for diff scope: `Diff is lean. No evidence-backed issues detected.`
If no issues exist for repo scope: `Repository is lean. No over-engineering detected.`
