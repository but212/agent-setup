---
name: lean-test
description: >
  Designs and writes deterministic, minimal tests against public boundaries.
  Focuses on contract verification, boundary conditions, and state transitions
  without implementation-coupled over-mocking.
---

# Lean Test

Design and write the fewest deterministic tests proving observable behavior and preventing semantic regressions.

## Operating contract

- Ground tests on public boundaries, input/output contracts, types/schemas, the existing harness, and nearby tests; never test private methods or implementation details.
- Use `lean-design` first for states, invariants, transitions, or API boundaries. Hand production changes to `lean-mode` only when explicitly requested.
- Control time, IDs, randomness, and concurrency without arbitrary sleeps (`sleep`, `setTimeout`). Mock only external I/O boundaries (HTTP, DB, hardware, filesystem, or nondeterministic services); never mock domain entities or the system under test (SUT).

## Testing matrix

| Layer | Target contract | Assertion focus |
| :--- | :--- | :--- |
| **Domain logic** | Pure calculations and transitions | Explicit inputs -> outputs; state table |
| **State machine** | Invariants and valid/invalid transitions | Allowed transitions pass; invalid transitions reject |
| **Boundary / API** | Serialization, validation, status codes | Status, error payload, and boundary gates |
| **Integration** | Persistence and transactions | Durable effects, rollback, ordering, conflict behavior |
| **External adapter** | Adapter's public contract | Translated result/error at the controlled I/O boundary |

## Case selection

Choose only applicable distinguishing cases:

1. Representative success path.
2. Empty or boundary input.
3. Each meaningful state transition, including rejected transitions.
4. Exposed invalid-input or failure path.
5. Confirmed regression case.

For stateful behavior, express cases as a transition table (`state x event -> next state or error`) and assert invariants after each transition. Do not manufacture cases solely to improve coverage percentages.

## Constraints

- Assert contract values, statuses, errors, and durable effects - not incidental call order, internal shape, or call counts. Assert call counts only when the explicit contract is the side effect (for example, sending exactly one notification).
- Assert the system-owned error contract rather than an upstream dependency's exact display string unless that string is itself public behavior.
- Gate platform-specific fixtures by the platform that guarantees them; `cfg(unix)` is insufficient for a device that exists only on one Unix target.
- Use snapshots only for intentional, stable rendering contracts; not mutable business logic.
- Avoid real network calls, shared mutable state, broad fixture builders, and duplicated setup.
- If no repository-native harness exists, report that before changing tooling; do not add dependencies without explicit request.
- If a test exposes a production defect, report the root cause and hand off to `lean-mode`; do not weaken the assertion or edit production code in this skill.

## Execution and verification

Reuse the repository's declared runner, fixtures, and package manager. Run the narrowest exact test command first, then required broader checks. When commands share a build directory or package cache, run them sequentially; a timeout caused by build-lock contention is inconclusive and must be rerun. Report the command and result; never claim success for an unrun or failing command.

## Output format

For test-only implementation, show the test change first and explain only evidence needed for correctness. For non-trivial design, use `Problem`, `Structure`, `Cases`, `Implementation`, and `Verify`, omitting empty sections.

## Controls

- **Scope**: Test design, test-only implementation, review, and focused test diagnosis.
- **Activate**: `/lean-test` or an explicit request to design, add, or diagnose tests.
- **Deactivate**: `stop lean-test` or `normal mode`.
