---
name: constraints-projection
role: Derives minimal baseline design and execution plans via constraints projection
activation: "`/project-constraints`, baseline design, oracle-first modeling, task or architecture simplification"
modification-authority: None
description: Derives minimal baseline architecture, workflows, and execution plans by positing an extreme zero-cost ideal oracle and sequentially projecting verified physical, environmental, and domain constraints without defensive sprawl.
---

# Constraints Projection

A minimal design or execution plan is the residue of an Ideal Oracle after verified constraints are projected onto it.

## Operating Contract

- Read-only: emits baseline contracts, invariants, and execution plans; modifies no code, schemas, or documents.
- Output is structured specifications (typed signatures or concrete outcomes, numbered invariants, and failure modes) consumable by TDD, domain modeling, or direct execution.
- Admissible constraints are verified physical limits, environmental/platform boundaries, and hard requirements only. Habit, dogma, defensive hunch, and unverified hypotheses are inadmissible.

## Laws

1. **Isolation:** Phases execute strictly in sequence; no phase reads ahead or leaks into another.
2. **Oracle Primacy:** Every design or plan element derives from a Phase 1 assumption; none originates in a constraint.
3. **Exhaustive Projection:** Every ideal assumption is cross-checked against every verified constraint; no pair is skipped.
4. **Burden of Proof:** An ideal holds until a verified constraint refutes it; unverified guesses, "infeasible", or "that's how it's done" are not refutation.
5. **Minimal Relaxation:** Each refuted ideal yields the least deviation that satisfies the constraint, ranked by: `Reversibility > Core Outcome Preservation > Effort/Cost`.

## Phase 1: Ideal Oracle

Feasibility, cost, tools, and existing implementation or habits do not exist. Phase 1 output contains no constraint or compromise.

- **Greenfield:** `() -> PrimaryOutcome` (code: `f() -> Output`)
  - Singular Intent (Zero Input): one unambiguous `PrimaryOutcome` is known immediately without lookups, clarification, or competing goals.
  - Instant Execution: O(1) computation, 0ms latency, zero calendar time, zero effort.
  - Infinite Resource: budget, attention, memory, storage, bandwidth, and quota are unbounded and free.
  - Zero State Drift: misunderstanding, concurrency conflict, divergence, errors, and data loss are impossible.
- **Incremental (Brownfield):** Ideal Delta -- existing `f(x)` or workflow yields target `f'(x) -> y'` with existing inputs, callers, and stakeholders preserved, zero disruption, zero latency/effort increase, zero side effects, and zero marginal cost.

## Phase 2: Constraint Enumeration

Enumerate, independently of Phase 1 reasoning, verified immutable boundaries (`VerifiedFact`) conflicting with Phase 1 assumptions. Unverified guesses about human reactions, edge cases, or feasibility must be tagged `Hypothesis(claim, check_method)` and isolated -- never treated as `VerifiedFact` until tested.

- **Physics:** deadlines, human attention/working-memory ceilings, network RTT, bandwidth, memory/storage ceilings, persistence latency.
- **Environment:** platform/runtime limits, legal/policy/API contracts, budget/cost ceilings, legacy caller or stakeholder compatibility.
- **Requirement:** primary user intent, non-negotiable `Guardrails`, domain safety rules, regulatory boundaries.

## Phase 3: Projection & Triage

The triage subject is always an **Ideal Assumption**; each receives exactly one verdict:

- `Accept`: the ideal guarantee survives intact and becomes a structural invariant enforced by type, schema, rule, or fixed process.
- `Compromise`: the ideal is relaxed only at the external boundary (ingress, handoff, or communication wrapper); the interior retains the ideal.
- `Abandon`: synchronous or one-shot satisfaction is dropped; the guarantee is delivered asynchronously, eventually, or in staged milestones.

Incremental projection: compatibility conflicts resolve at an adapter or boundary layer that leaves existing callers or stakeholders unbroken; performance or capacity conflicts resolve by decoupling into background or staged execution.

## Output Schema: Projection Matrix

### 1. Baseline Target

- Signature / Target: `() -> PrimaryOutcome` (code: `f() -> Output`) or incremental `f'(x) -> y'`
- Core Invariant: one sentence stating the unconstrained primary outcome.

### 2. Projection Matrix

One row per `(Phase 1 Ideal Assumption, Phase 2 Conflicting Constraint)` pair.

| Phase 1 Ideal Assumption | Phase 2 Conflicting Constraint | Category | Triage (`Accept` / `Compromise` / `Abandon`) | Resolution |
| :--- | :--- | :--- | :--- | :--- |

### 3. Handoff Contract

- Signatures / Deliverables: minimal input/output types, function definitions, or concrete deliverable boundaries.
- Invariants (`I-NN`): preserved or introduced domain/process laws and non-negotiable `Guardrails`.
- Unverified Hypotheses: `Hypothesis` items requiring validation before they may alter the plan (omit if none).
- Failure Modes: concrete error or failure states introduced by `Compromise` and `Abandon`.
- Next Step: handoff target (TDD implementation, algebraic domain modeling, or staged execution).

## Prohibited

- Phase 1 content referencing constraints, compromises, or unprioritized competing goals.
- Inadmissible constraints per Operating Contract (including `Hypothesis` treated as `VerifiedFact`).
- Vague prose in place of concrete signatures/outcomes and numbered invariants.
- Multi-agent orchestration overhead or conversational meta-explanation.
