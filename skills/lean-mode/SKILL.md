---
name: lean-mode
description: >
  Produces the smallest correct coding change adhering to lean-design models.
  Use for writing, refactoring, fixing code, and managing dependencies.
  Do not use for prose compression or read-only review; use `lean-review`.
---

# Lean Mode

Choose the smallest correct change for coding tasks based on approved structural models.

## Operating contract

Consume an approved requirement, structural design (`lean-design`), or failing test (`lean-test`) and produce the minimal correct code change.

Make changes only after tracing execution flow end-to-end through runtime behavior, tests, types, and call boundaries. Fix root causes at shared boundaries, not symptoms at caller sites. Preserve explicit domain contracts established by `lean-design`.

## Universal decision ladder

Stop at the first applicable rung:

1. **Need to exist?** (YAGNI) Skip speculative branches, extension points, and unused config knobs.
2. **Already in the codebase?** Reuse existing helpers, types, patterns, or installed dependencies.
3. **Native language / stdlib primitive?** Use standard collection pipelines, built-in pattern matching, or standard error types.
4. **Installed dependency solves it?** Reuse installed tools; reject new packages for small utilities.
5. **Parse, Don't Validate**: Parse untrusted input into strict domain types at the boundary once; never repeatedly validate raw primitives inside inner functions.
6. **One Clear Expression**: Prefer a single deterministic expression over intermediate mutable state. Avoid cryptic syntax-golfing.
7. **Smallest Local Implementation**: Write the minimal cohesive logic that satisfies the contract.

## Invariant boundaries (never minimize)

- Input sanitization and authorization gates at trust boundaries
- Explicit error handling that prevents data corruption, silent failure, or lost context
- Atomic state transitions (DB transactions, concurrency guards, compare-and-swap, or equivalent)
- Resource ownership, cleanup, and cancellation at I/O boundaries
- Explicit domain contracts established by `lean-design`

Errors must follow the repository's established propagation model consistently: return typed errors where the language uses them, or preserve meaningful exceptions where that is the contract. Do not swallow, reclassify, or duplicate handling without evidence.

## Scope rules

- Use `lean-design` first when states, types, data, or API boundaries are the main problem.
- Use `lean-test` for test-only changes and `lean-review` for read-only audits.
- Use `spec-drive` for contract-sensitive or materially architectural changes.
- Do not add abstractions, factories, interfaces, or dependencies without demonstrated need.

## Verification

Run the narrowest repository-native check covering changed behavior. Non-trivial logic (branches, loops, parsers, security, money, concurrency, or public boundaries) requires a runnable check. Never claim success unless the command exits cleanly.

## Output format

Lead immediately with the code change. When mechanisms are intentionally omitted:

```text
Skipped: <unnecessary abstraction/guard>.
Add <mechanism> when <observable trigger>.
```

## Controls

- **Scope**: Bounded coding changes and implementation.
- **Activate**: `/lean-mode` or an explicit request to implement, fix, or refactor code.
- **Deactivate**: `stop lean-mode` or `normal mode`.
