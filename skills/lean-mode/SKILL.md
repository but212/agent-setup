---
name: lean-mode
role: Makes minimal code changes and writes deterministic tests
activation: "`/lean-mode`, `/lean-mode test`, implementation, test, or refactor request"
modification-authority: Approved code and test scope
description: >
  Produces the smallest correct coding and test changes adhering to
  lean-design models. Use for writing code, refactoring, fixing bugs, and
  creating deterministic minimal tests. Do not use for prose compression
  or read-only review; use `lean-review`.
---

# Lean Mode

Choose the smallest correct change for coding and testing tasks based on approved structural models.

## Operating contract

- Consume an approved requirement or structural design (`lean-design`) and produce the minimal correct code and test changes.
- Before editing, trace execution end-to-end through runtime behavior, tests, types, and call boundaries.
- Fix root causes at shared boundaries, not caller symptoms.
- Preserve `lean-design` contracts.
- Prefer `lean-design` first when states, types, data, or API boundaries are the main problem.

## Universal decision ladder

Stop at the first applicable rung:

1. **Need to exist?** (YAGNI) Skip speculative branches, extension points, and unused config.
2. **Already in the codebase?** Reuse existing helpers, types, patterns, or installed dependencies.
3. **Native language / stdlib primitive?** Use standard collections, pattern matching, or standard error types.
4. **Installed dependency solves it?** Reuse installed tools; reject new packages for small utilities.
5. **Parse, Don't Validate**: Parse untrusted input into strict domain types at the boundary once.
6. **One Clear Expression**: Prefer a single deterministic expression over intermediate mutable state.
7. **Smallest Local Implementation**: Write the minimal cohesive logic that satisfies the contract.

## Invariant boundaries (never minimize)

- Input sanitization, authorization gates, and partition isolation at trust boundaries
- Explicit error handling that prevents data corruption, silent failure, or lost context
- Atomic state transitions, concurrency guards, and bounded resource acquisition
- Serialization format stability and backward compatibility across versions
- Resource ownership, cleanup, and cancellation at I/O boundaries
- Explicit domain contracts established by `lean-design`

Follow the repository's established error propagation model. Do not swallow, reclassify, or duplicate handling without evidence.

## Deterministic Testing Rules

When designing or writing tests (activate via `/lean-mode test` or test requests):

- Ground tests on public boundaries, input/output contracts, and types/schemas; never test private implementation details.
- Control time, IDs, randomness, and concurrency without arbitrary sleeps (`sleep`, `setTimeout`). Mock only external I/O boundaries (HTTP, DB, hardware, filesystem); never mock domain entities or the SUT.
- Focus assertions on contract values, statuses, errors, and durable effects - not incidental call order or intermediate shape.
- Choose distinguishing cases: success path, boundary/empty input, state transitions, exposed invalid input, and regression cases.

## Scope rules

- Use `lean-review` for read-only audits.
- Use `spec-drive` for contract-sensitive or materially architectural changes.
- Do not add abstractions, factories, interfaces, or dependencies without demonstrated need.

## Verification

Run the narrowest repository-native check that covers the changed behavior and exits cleanly. Run the formatter before the final check and re-inspect the diff. Treat timeouts or inconclusive results as unverified.

## Output format

Lead immediately with the code/test change. When mechanisms are intentionally omitted:

```text
Skipped: <unnecessary abstraction/guard>.
Add <mechanism> when <observable trigger>.
```

## Controls

- **Scope**: Bounded coding and test implementation.
- **Activate**: `/lean-mode`, `/lean-mode test`, or explicit request to implement, test, fix, or refactor code.
- **Deactivate**: `stop lean-mode` or `normal mode`.
