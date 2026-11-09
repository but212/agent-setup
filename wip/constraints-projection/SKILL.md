---
name: constraints-projection
role: Derives minimal baseline architecture via constraints projection
activation: "`/project-constraints`, architectural baseline design, oracle-first modeling"
modification-authority: None
description: Derives minimal software architecture by positing an extreme zero-cost ideal oracle and sequentially projecting physical, runtime, and domain constraints without defensive sprawl.
---

# Constraints Projection

Architecture is the residue of an Ideal Oracle after verified constraints are projected onto it.

## Operating Contract

- Read-only: emits architectural baseline contracts; modifies no code, schemas, or documents.
- Output is typed signatures and invariants consumable by TDD or domain modeling.
- Admissible constraints are physical boundaries, platform limits, and hard requirements only. Habit, framework dogma, and defensive hunch are inadmissible.

## Laws

1. **Isolation:** Phases execute strictly in sequence; no phase reads ahead or leaks into another.
2. **Oracle Primacy:** Every design element derives from a Phase 1 assumption; none originates in a constraint.
3. **Exhaustive Projection:** Every ideal assumption is cross-checked against every constraint; no pair is skipped.
4. **Burden of Proof:** An ideal holds until a verified constraint refutes it; "infeasible" without evidence is not refutation.
5. **Minimal Relaxation:** Each refuted ideal yields the least deviation that satisfies the constraint.

## Phase 1: Ideal Oracle

Feasibility, hardware, and existing implementation do not exist. Phase 1 output contains no constraint or compromise.

- **Greenfield:** `f() -> Output`
  - Zero Input: intent is known without parameters or lookups.
  - Instant Execution: O(1) computation, 0ms latency.
  - Infinite Resource: memory, storage, bandwidth, and quota are unbounded and free.
  - Zero State Drift: concurrency conflict, divergence, and data loss are impossible.
- **Incremental (Brownfield):** Ideal Delta — existing `f(x)` yields target `f'(x) -> y'` with existing inputs preserved, zero caller modification, zero latency increase, zero side effects, and zero marginal cost.

## Phase 2: Constraint Enumeration

Enumerate, independently of Phase 1 reasoning, verified immutable boundaries conflicting with Phase 1 assumptions:

- **Physics:** network RTT, bandwidth, memory ceilings, persistence latency.
- **Environment:** platform runtime limits, third-party API contracts, cost ceilings, legacy caller compatibility.
- **Requirement:** user intent, domain safety rules, regulatory boundaries.

## Phase 3: Projection & Triage

The triage subject is always an **Ideal Assumption**; each receives exactly one verdict:

- `Accept`: the ideal guarantee survives intact and becomes a structural invariant enforced by type or schema.
- `Compromise`: the ideal is relaxed only at the external ingress boundary; the interior retains the ideal.
- `Abandon`: synchronous satisfaction is dropped; the guarantee is delivered asynchronously or eventually.

Incremental projection: compatibility conflicts resolve at an adapter boundary that leaves existing callers unbroken; performance conflicts resolve by decoupling into background execution.

## Output Schema: Projection Matrix

### 1. Baseline Function

- Function Signature: `f() -> Output` or incremental `f'(x) -> y'`
- Core Invariant: one sentence stating the unconstrained functional invariant.

### 2. Projection Matrix

One row per (assumption, conflicting constraint) pair.

| Phase 1 Ideal Assumption | Phase 2 Conflicting Constraint | Category | Triage (`Accept` / `Compromise` / `Abandon`) | Architectural Resolution |
| :--- | :--- | :--- | :--- | :--- |

### 3. Handoff Contract

- Signatures: minimal input/output types and function definitions.
- Invariants (`I-NN`): preserved or introduced domain laws.
- Failure Modes: concrete error states introduced by `Compromise` and `Abandon`.
- Next Step: handoff target (TDD implementation or algebraic domain modeling).

## Prohibited

- Phase 1 content referencing constraints or implementation compromises.
- Inadmissible constraints per Operating Contract.
- Vague prose in place of typed signatures and numbered invariants.
- Multi-agent orchestration overhead or conversational meta-explanation.
