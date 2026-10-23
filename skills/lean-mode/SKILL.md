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

Choose the smallest correct change for coding and testing tasks based on approved models.

## Operating contract

- Consume approved requirements or structural models; produce minimal correct code and test changes.
- Trace execution end-to-end (runtime behavior, tests, types, call boundaries) before editing.
- Fix root causes at shared boundaries rather than symptoms at call sites.
- Preserve domain contracts and invariant locations (`type`, `schema`, `boundary`, `runtime`).
- Prefer structural design first when states, types, data, or API boundaries are central.

## Sub-Contract 1: Minimal Implementation

### Universal decision ladder

Stop at the first applicable rung:

1. **Need to exist?** (YAGNI) Skip speculative branches, extension points, and unused config.
2. **Already in codebase?** Reuse existing helpers, types, and patterns.
3. **Language/stdlib primitive?** Use standard collections, pattern matching, and standard error types.
4. **Installed dependency?** Reuse installed packages; reject new dependencies for small utilities.
5. **Smallest Local Implementation:** minimal cohesive logic satisfying the contract; prefer one clear expression over intermediate mutable state.

### Invariant boundaries (never minimize)

- Input sanitization, authorization gates, and partition isolation at trust boundaries.
- Explicit error handling preventing data corruption, silent failure, or lost context.
- Atomic state transitions, concurrency guards, and bounded resource acquisition.
- Serialization stability and backward compatibility.
- Resource cleanup and cancellation at I/O boundaries.
- Explicit domain contracts from structural design.

Follow the repository error propagation model; do not swallow, reclassify, or duplicate handling without evidence.

### Enforcement placement

- **Trust boundary:** parse and validate once into domain types; never remove or make redundant.
- **`type` or `schema`:** omit core re-checks if violation is unconstructible on every reaching path.
- **`runtime`:** check at single point of violation; avoid scattered copies.
- **Unspecified location:** state assumed location before editing; do not guess silently.

### Output format

Lead with code/test changes. When omitting mechanisms intentionally:

```text
Skipped: <unnecessary abstraction/guard>.
Add <mechanism> when <observable trigger>.
```

## Sub-Contract 2: Deterministic Testing

- Test public boundaries, input/output contracts, and types/schemas; never test private details.
- Control time, IDs, randomness, and concurrency without arbitrary sleeps (`sleep`, `setTimeout`).
- Mock only external I/O boundaries (HTTP, DB, hardware, filesystem); never mock domain entities or the SUT.
- Assert on contract values, statuses, errors, and durable effects, not incidental call order.
- Cover success, empty/boundary input, transitions, exposed invalid input, and regressions.
- For `type` or `schema` invariants, test that invalid states cannot be constructed or inserted.

## Scope & Verification

- Delegate audits to `lean-review` and contract-sensitive planning to `spec-drive`.
- Run the narrowest repository-native check covering changed behavior; format before the final check and inspect the diff. Treat timeouts or inconclusive runs as unverified.

## Controls

- **Scope:** bounded coding and test implementation.
- **Activate:** `/lean-mode`, `/lean-mode test`, or implementation/test/refactor request.
- **Deactivate:** `stop lean-mode` or `normal mode`.
