---
name: lean-test
description: >
  Designs and writes the smallest deterministic tests for existing codebases,
  including unit, integration, API, component, and regression tests. Use when
  translating behavior or requirements into executable cases, adding coverage
  for a feature or bug fix, diagnosing flaky tests, or reviewing test quality;
  use with lean-design for invariants. Hand production implementation to
  lean-mode only when the user explicitly requests it.
---

# Lean Test

Design the fewest deterministic tests proving observable behavior, protecting contracts, and preventing regressions.

## Operating contract

- Ground tests in runtime behavior, public boundaries, types/schemas, existing harness, and nearby tests.
- Use `lean-design` first for states, invariants, transitions, or API boundaries.
- Hand production implementation to `lean-mode` only when explicitly requested; keep edits test-only.
- Test nearest stable public boundary, not private details observable above it.
- Preserve validation, security, accessibility, error handling, persistence, and return contracts.

## Workflow

1. **Define the contract:** Record precondition, action, observable result, side effect, or error; do not invent requirements.
2. **Inspect the harness:** Reuse location, runner, fixtures, factories, mocks, and setup without adding dependencies for a few assertions.
3. **Choose the smallest distinguishing set:** Select only applicable cases (representative success; empty/boundary/transition state; exposed invalid-input/failure path; confirmed regression). Avoid redundant tests.
4. **Test through the boundary:** Keep one behavior per test with clear Arrange, Act, Assert phases. Assert contract values, statuses, errors, and durable effects—not incidental call order or internal shape.
5. **Verify:** Run narrowest repository-native test, then required broader checks. Confirm test distinguishes regressions without leaving temporary production changes.

## Boundary selection

| Behavior | Smallest useful test |
| --- | --- |
| Pure deterministic logic | Unit test with explicit inputs and outputs |
| Module or use-case contract | Test module's public entrypoint |
| Database transaction, ordering, rollback, or conflict | Integration test through persistence boundary |
| HTTP status, headers, validation, or serialization | Request-level test through route boundary |
| External service adapter | Focused adapter test with only external boundary controlled |
| UI behavior | Component or browser test only when lower layers cannot prove user-visible contract |

## Constraints

- Control time, randomness, IDs, and async completion with existing helpers; never use arbitrary sleeps.
- Avoid real network calls, shared mutable state, broad fixture builders, and duplicated setup. Mock only external/nondeterministic side effects—never the system under test.
- Prefer targeted assertions. Use snapshots only for intentional, stable rendering contracts.
- Avoid asserting call counts, private methods, or internal structures unless they are explicit contracts.
- For stateful flows, cover invariants and meaningful transitions. For persistence, cover ordering, stale-version conflicts, and `PublicId` formats.
- Do not chase coverage percentages or speculative behavior.

## Execution boundaries

- If `lean-design` is unavailable or the change is trivial/stateless, state inferred precondition, action, and observable result in 1–3 bullets.
- For simple local behavior, plan only the applicable contract and verification slice; reserve full state/invariant coverage for stateful or boundary-sensitive changes.
- Keep production code outside this skill's scope. If a test exposes a required production change, report root cause and hand off to `lean-mode`.
- If no repository-native harness exists, report before changing tooling; do not add dependencies without explicit request.
- Never claim success unless the exact test command exits cleanly. If blocked, report command, error, blocker, and next step.
- For persistence tests, use isolated test database, transaction rollback, schema sandbox, or deterministic cleanup. Never target non-test data or run destructive cleanup against non-test databases.
- For UI tests, prefer accessible role-and-name queries; assert keyboard, focus, validation messages, or disabled states only when contract-exposed.

## Failure handling

- Compare failures with contract; do not weaken assertions to get green.
- For flakes, control nondeterministic input or cleanup boundary.
- If behavior is hard to test, apply `lean-design` before adding seams or abstractions.
- Place regressions at shared root-cause boundary.

## Output and verification

- For implementation requests, show test change first and explain only evidence needed for correctness.
- For non-trivial design, use `Problem`, `Structure`, `Cases`, `Implementation`, and `Verify`; omit empty sections.
- Use repository's declared scripts and package manager detected from lockfiles/config. Never switch package managers.
- Report exact targeted command and result, including skipped broader validation and rationale.

## Controls

- **Scope:** Test design, test-only implementation, review, and focused test diagnosis.
- **Activate:** `/lean-test` or an explicit request to design, add, or diagnose tests.
- **Deactivate:** `stop lean-test` or `normal mode`.
