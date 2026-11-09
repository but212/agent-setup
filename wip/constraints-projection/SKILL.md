---
name: constraints-projection
role: Derives minimal baseline architecture via constraints projection
activation: "`/project-constraints`, architectural baseline design, oracle-first modeling"
modification-authority: None
description: Derives minimal software architecture by positing an extreme zero-cost ideal oracle and sequentially projecting physical, runtime, and domain constraints without defensive sprawl.
---

# Constraints Projection

Derives minimal baseline software architecture by backtracking from an Ideal Oracle to physical reality.

## Operating Contract

- Read-only analysis: outputs architectural baseline contracts; modifies no code, schemas, or documents.
- Self-contained: yields typed signatures and invariants consumable by standard TDD cycles or domain modeling workflows.
- Grounded constraints: admits only physical boundaries, platform limits, and hard requirements. Rejects habit and premature defensive branching.

## Core Principle: Isolated Three-Phase Protocol

To prevent attention dilution and premature compromise, execute phases strictly in sequence without cross-stage contamination.

### Phase 1: Ideal Oracle Baseline (Strict Feasibility Oblivion)

Assume absolute unconstrained perfection. Completely disregard physical feasibility, hardware limits, and existing implementations. While defining Phase 1, never mention constraints or compromises.

- **Greenfield Baseline:** `f() -> Output`
  - Zero Input: System derives intent with zero parameters or lookups.
  - Instant Execution: O(1) computation and zero latency (0ms).
  - Infinite Resource: Boundless memory, storage, and bandwidth at zero cost.
  - Zero State Drift: Concurrency conflicts and state divergence are structurally impossible.
- **Incremental Baseline (Brownfield / Existing Codebase):**
  - Ideal Delta: Existing f(x) yields target outcome f'(x) -> y' with zero caller modification, zero latency increase, and zero side effects.

### Phase 2: Constraint Enumeration (Independent Reality Mapping)

List verified, immutable boundaries conflicting with Phase 1 assumptions across three categories:

- **Physics:** Network RTT, bandwidth ceilings, memory ceilings, persistence latency.
- **Environment:** Platform runtime limits, third-party API contracts, legacy caller compatibility.
- **Requirement:** User intent, domain safety rules, regulatory boundaries.

### Phase 3: Projection & Triage

Project constraints onto Phase 1 assumptions. The triage subject is always the **Ideal Assumption**:

- `Accept`: Preserve the ideal guarantee as an unyielding architectural invariant (e.g. sum types, immutable append-only log).
- `Compromise`: Relax the ideal assumption minimally at external ingress boundaries (e.g. accept minimal entity ID; resolve remainder locally).
- `Abandon`: Drop synchronous satisfaction of the ideal guarantee; decouple into asynchronous queues or eventual consistency.

## Output Schema: Projection Matrix

Output the analysis in this schema:

### 1. Baseline Function

- Function Signature: `f() -> Output` or incremental `f'(x) -> y'`
- Core Invariant: Single sentence stating the unconstrained functional invariant.

### 2. Projection Matrix

| Phase 1 Ideal Assumption | Phase 2 Conflicting Constraint | Category | Triage (`Accept` / `Compromise` / `Abandon`) | Architectural Resolution |
| :--- | :--- | :--- | :--- | :--- |
| Zero Input | Caller intent unknown | Requirement | Compromise | Accept minimal entity ID at ingress boundary |
| Instant Execution | Remote I/O latency | Physics | Abandon | Asynchronous job with completion event |
| Zero State Drift | Concurrent writes | Physics | Accept | Immutable append-only log with deterministic ordering |

### 3. Handoff Contract

- Signatures: Minimal input/output types and function definitions.
- Invariants (`I-NN`): Core preserved or introduced domain laws.
- Failure Modes: Concrete error states introduced by `Compromise` and `Abandon` decisions.
- Next Step: Handoff target (TDD implementation or algebraic domain modeling).

## Prohibited

- Contaminating Phase 1 with Phase 2 constraints or speculative implementation compromises.
- Treating developer habit, framework dogma, or defensive hunch as a valid constraint.
- Emitting vague prose in place of typed signatures and numbered invariants.
- Introducing multi-agent orchestration overhead or conversational meta-explanations.
