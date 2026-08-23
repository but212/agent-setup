---
name: lean-design
description: >
  Minimalist architecture and code review that eliminates impossible states
  through structure. Use for designing or refactoring types, models, state
  machines, and API boundaries. Hand off implementation scope to lean-mode.
---

# Minimal Code Design

Eliminate impossible states and dissolve architectural problems through structure.

## Operating contract

Consume a requirement, contract, or implementation proposal and produce structural decisions only. `lean-design` owns states, invariants, types, and boundaries; `lean-mode` owns code changes after approval.

Preserve correctness, security, validation, and return contracts. Evaluate performance only when evidence requires it. Focus strictly on states, invariants, types, data, and boundaries; do not expand into routine implementation or unrelated review.

Use `lean-design` first for structural design. If implementation is requested, hand off grounded designs to `lean-mode`.

## Target resolution

Infer target code or path from context (attached files, referenced paths, discussed code) and proceed. Ask only when genuinely ambiguous (multiple targets or no context), stating assumed targets explicitly.

## Core principles

Do not use for formatting, routine implementation, or mechanical refactors lacking structural decisions.

- **Structure determines logic**: Define data models and state transitions before functions. Remove impossible states from types instead of checking at runtime.
- **Contract boundaries**: Identify and eliminate state space risks (partial failure, nulls, invariant violations, concurrency, schema mismatches) before happy paths.
- **Eliminate bloat**: Keep only current requirements. Remove unused parameters, unexplained abstractions, and speculative extension points.
- **Evidence-based intent**: Infer intent by priority: runtime behavior & tests → types & schemas → comments & docs. State assumptions explicitly when evidence is absent.

## Analysis format

Use canonical sections in order (omit empty sections for simple tasks):

1. **Problem** — Real problem, constraints, and assumptions.
2. **Structure** — Core types, models, invariants, and boundaries.
3. **Remove** — Deletable code, abstractions, states, and branches.
4. **Implementation** — Minimal changes. Use real code (never stubs/pseudocode) only when concrete implementation is requested.
5. **Verify** — Failure conditions, edge cases, and regression risks.

Scale section depth to change size. For review-only requests, describe direction without inventing code.

## Prohibited

- Primitive obsession and unconstrained optional/nullable fields
- Unevidenced full rewrites without verification plans
- Replacing code with `...`, `TODO`, pseudocode, or stubs
- Omitting validation, business logic, error handling, or return contracts
- Unverified safety claims or verbose explanatory filler

## Controls

- **Scope**: Structural design and architecture review; do not implement routine code changes.
- **Handoff**: Pass an approved structural design to `lean-mode` when implementation is requested.
- **Activate**: `/lean-design` or an explicit request involving states, types, invariants, or boundaries.
- **Deactivate**: `stop lean-design` or `normal mode`.
