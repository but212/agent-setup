---
name: lean-mode
role: Makes the smallest correct code change
activation: Implementation, fix, or refactor request
modification-authority: Approved code scope
description: >
  Produces the smallest correct coding change adhering to lean-design models.
  Use for writing, refactoring, fixing code, and managing dependencies.
  Do not use for prose compression or read-only review; use `lean-review`.
---

# Lean Mode

Choose the smallest correct change for coding tasks based on approved structural models.

## Operating contract

- Consume an approved requirement, structural design (`lean-design`), or failing test (`lean-test`) and produce the minimal correct code change.
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

## Scope rules

- Use `lean-test` for test-only changes and `lean-review` for read-only audits.
- Use `spec-drive` for contract-sensitive or materially architectural changes.
- Do not add abstractions, factories, interfaces, or dependencies without demonstrated need.

## Verification

Run the narrowest repository-native check that covers the changed behavior and exits cleanly. Run the formatter before the final check and re-inspect the diff. Treat timeouts or inconclusive results as unverified.

## Output format

Lead immediately with the code change. When mechanisms are intentionally omitted:

```text
Skipped: <unnecessary abstraction/guard>.
Add <mechanism> when <observable trigger>.
```

## Controls

- **Scope**: Bounded coding changes and implementation.
- **Activate**: `/lean-mode` or explicit request to implement, fix, or refactor code.
- **Deactivate**: `stop lean-mode` or `normal mode`.
