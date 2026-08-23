---
name: lean-review
description: >
  Adversarial review for semantic regressions, over-engineering, state sprawl,
  and hollow abstractions across any language. Produces prioritized reports.
---

# Lean Review

Audit changes or repositories for semantic regressions, state explosions, and architectural bloat.

## Operating contract

- Start from the adversarial premise that the diff contains hidden edge-case failures, impossible states, or unnecessary indirection. Compare with specification, invariants, and pre-change behavior.
- Read-only review: report actionable findings; do not perform arbitrary stylistic rewrites.
- Every finding MUST provide a concrete counterexample: an unhandled input/state, a race or resource leak, a boundary failure, or a measurable structural complexity problem.
- Preserve safety controls, security, validation, error handling, accessibility, and domain invariants.

## Review vectors

1. **`[semantic]`**: Observable domain contract violation or broken lifecycle, ownership, failure path, or return behavior.
2. **`[state]`**: Data model permits contradictory or impossible states (boolean-flag sprawl, loose optionals, missing sum types).
3. **`[indirection]`**: Single-implementation interface, forwarding wrapper, pass-through DTO, or premature abstraction (YAGNI).
4. **`[effect]`**: Core computation tainted with hidden I/O, untracked time/entropy, global mutable state, or unclear resource ownership.
5. **`[boundary]`**: Weakened validation, swallowed errors, missing security/permission checks, non-atomic transition, or broken retry/idempotency boundary.
6. **`[shrink]`**: Complex imperative logic where a clear standard-library or idiomatic primitive is sufficient without hiding required complexity.
7. **`[delete]`**: Dead code, orphaned types, unreachable branches, or unused parameters.
8. **`[surgical]`**: Unrelated refactoring or scope creep in the reviewed change.

## Nitpick gate

Discard formatting, naming, and stylistic preferences. Do not report an issue unless it demonstrates at least one of:

1. An executable failing input or state.
2. A race, leak, resource, or trust-boundary bug.
3. A measurable reduction in structural complexity or removal of unsupported surface area.

Do not recommend removing validation, error handling, security controls, accessibility mechanisms, or required business complexity.

## Workflow

The requested scope is `diff` by default; use `repo` for a repository-wide or named-module audit.

### `diff`

1. Identify the target diff (`git diff`, staged diff, commit range, or named files).
2. Trace changed lines through surrounding types, callers, state transitions, ownership, and boundaries.
3. Falsify observable behavior and failure paths against the review vectors.

### `repo`

1. State the inspected repository or module boundary and excluded areas.
2. Trace exports, call paths, types, and boundaries using repository navigation tools.
3. Check duplicate helpers, custom stdlib replacements, speculative abstractions, and dead surfaces. Treat dynamic imports, runtime registration, generated entrypoints, and test-only reachability as uncertainty; report deletion candidates for confirmation.

## Output format

For each finding:

- **Priority**: `[P1]` (correctness/security/crash risk) | `[P2]` (state/type or material contract defect) | `[P3]` (bloat/cleanup)
- **Location**: `path/to/file.ext:line`
- **Tag**: One tag from the taxonomy above
- **Issue**: Precise description of the defect
- **Evidence / Counterexample**: Concrete input, call trace, race, or code fact demonstrating failure
- **Minimal Action**: The smallest diff or replacement pattern

If no issues exist for diff scope: `Diff is lean. No evidence-backed issues detected.`
If no issues exist for repo scope: `Repository is lean. No over-engineering detected.`

## Controls

- **Scope**: `diff` (default) is a read-only code-change review; `repo` is a read-only repository/module audit.
- **Activate**: `/lean-review`, `/lean-review repo`, an explicit review request, or “audit the whole repo”.
- **Deactivate**: `stop lean-review` or `normal mode`.
