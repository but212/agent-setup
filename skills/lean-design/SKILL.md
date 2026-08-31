---
name: lean-design
description: >
  Minimalist architecture and API design that eliminates impossible states
  through algebraic data types and structural boundaries. Use for designing
  or refactoring types, state machines, and contracts before implementation.
---

# Minimal Code Design

Eliminate impossible states and dissolve architectural complexity through structure.

## Operating contract

Consume a requirement, contract, or proposal and produce structural decisions only. `lean-design` owns state spaces, invariants, types, and boundaries; `lean-mode` owns code changes after approval. Preserve correctness, security, validation, and domain invariants. Infer intent from runtime behavior and tests, then types/schemas, then comments/docs; state assumptions when evidence is absent. Evaluate performance only with profiling or hot-path evidence.

## Core principles

- **Make impossible states unrepresentable**: Replace boolean-flag combinations and leaky optionals/nulls with explicit sum types (enums, tagged unions, sealed interfaces).
- **Functional Core, Imperative Shell**: Isolate pure domain logic (deterministic transitions) from boundary I/O (time, network, database, entropy/randomness, and global mutable state).
- **Structure determines logic**: Define data models and state transitions before writing functions. Never check invariants at runtime that the type system can prove at compile time.
- **Contract boundaries**: Identify failure domains (partial failure, network retry, idempotency, concurrency, schema mismatch) at boundaries before drawing happy paths.
- **Dissolve hollow indirection**: Eliminate single-implementation interfaces, 1:1 pass-through DTOs, and speculative factories/builders. Keep concrete types until polymorphic need is proven.
- **Bounded scope**: Keep only current requirements; do not invent caching, plugin systems, or extension points without evidence.

## Target resolution

Infer the target code or path from attached files, referenced paths, and discussed code. Ask only when genuinely ambiguous (multiple targets or no context), stating assumptions explicitly.

## Analysis format

Use canonical sections in order (omit empty sections for simple tasks):

1. **Problem** - Real problem, constraints, assumptions, and edge boundaries.
2. **Structure** - Core sum types, state transitions, domain invariants, and I/O boundaries.
3. **Remove** - Impossible states, hollow interfaces, pass-through layers, and speculative parameters.
4. **Handoff Contract** - Exact type signatures, transition rules, failure behavior, and invariants for `lean-mode` / `lean-test`.

Do not implement routine code. If implementation is requested, provide the grounded design and hand off to `lean-mode`.

## Prohibited

- Primitive obsession and unconstrained optional/nullable sprawl
- Pure logic reaching into hidden side effects (clock, global state, or random)
- Unevidenced full rewrites or unsupported universal abstractions
- Replacing models with `...`, `TODO`, or pseudocode
- Omitting validation, business logic, error handling, or return contracts
- Premature caching or speculative plugin systems

## Controls

- **Scope**: Structural design and architecture; do not implement routine code.
- **Activate**: `/lean-design` or an explicit request involving states, types, invariants, or boundaries.
- **Deactivate**: `stop lean-design` or `normal mode`.
