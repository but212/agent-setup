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

Choose the smallest correct change for coding and testing tasks, based on approved structural models.

## Operating contract

- Consume an approved requirement or structural model; produce the minimal correct code and test changes.
- Before editing, trace execution end-to-end: runtime behavior, tests, types, call boundaries.
- Fix root causes at shared boundaries, not caller symptoms.
- Preserve domain contracts, including each invariant's location (`type`, `schema`, `boundary`, `runtime`).
- Prefer structural design first when states, types, data, or API boundaries are the main problem.

## Sub-Contract 1: Minimal Implementation

### Universal decision ladder

Stop at the first applicable rung:

1. **Need to exist?** (YAGNI) Skip speculative branches, extension points, unused config.
2. **Already in the codebase?** Reuse existing helpers, types, patterns.
3. **Native language / stdlib primitive?** Use standard collections, pattern matching, standard error types.
4. **Installed dependency solves it?** Reuse installed tools; reject new packages for small utilities.
5. **Smallest Local Implementation**: minimal cohesive logic that satisfies the contract.
Prefer one deterministic expression over intermediate mutable state ("One Clear Expression").

### Invariant boundaries (never minimize)

- Input sanitization, authorization gates, partition isolation at trust boundaries
- Explicit error handling that prevents data corruption, silent failure, or lost context
- Atomic state transitions, concurrency guards, bounded resource acquisition
- Serialization format stability and backward compatibility across versions
- Resource ownership, cleanup, and cancellation at I/O boundaries
- Explicit domain contracts established by structural design

Follow the repository's error propagation model. Do not swallow, reclassify, or duplicate handling without evidence.

### Enforcement placement

Apply the location assigned to each invariant:

- **Trust boundary**: parse and validate once into domain types. Never redundant; never removed.
- **`type` or `schema`**: no re-check in the core. If the type or constraint makes the violation unconstructible on every path, the re-check is dead code. Remove it.
- **`runtime`**: check at the single point of violation. No scattered copies.
- **No location in handoff**: state the assumed location before editing. Do not guess silently.

Remove a check only when the type, schema, or boundary parse already makes its violation impossible on every path that reaches it.

### Output format

Lead with the code/test change. When mechanisms are intentionally omitted:

```text
Skipped: <unnecessary abstraction/guard>.
Add <mechanism> when <observable trigger>.
```

## Sub-Contract 2: Deterministic Testing

When designing or writing tests (via `/lean-mode test` or test requests):

- Ground tests on public boundaries, input/output contracts, types/schemas. Never test private implementation details.
- Control time, IDs, randomness, concurrency without arbitrary sleeps (`sleep`, `setTimeout`). Mock only external I/O boundaries (HTTP, DB, hardware, filesystem). Never mock domain entities or the SUT.
- Assert on contract values, statuses, errors, durable effects. Not on incidental call order or intermediate shape.
- Choose distinguishing cases: success path, boundary/empty input, state transitions, exposed invalid input, regressions.
- For `type` or `schema` invariants, test that the invalid state cannot be constructed or inserted, not that a re-check fires.

## Scope & Verification

### Scope rules

- Use `lean-review` for read-only audits.
- Use `spec-drive` for contract-sensitive or materially architectural changes.
- No abstractions, factories, interfaces, or dependencies without demonstrated need.

### Verification

Run the narrowest repository-native check that covers the changed behavior and exits cleanly. Run the formatter before the final check, then re-inspect the diff. Treat timeouts or inconclusive results as unverified.

## Controls

- **Scope**: bounded coding and test implementation.
- **Activate**: `/lean-mode`, `/lean-mode test`, or explicit request to implement, test, fix, or refactor code.
- **Deactivate**: `stop lean-mode` or `normal mode`.
