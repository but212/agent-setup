# Constraints Projection

**English** | [한국어](constraints-projection.ko.md)

Conventional bureaucratic software engineering has historically focused on post-hoc maintenance and downside defense due to human cognitive limitations. In contrast, **Constraints Projection** is an AI-native development paradigm predicated on the pattern-matching and exhaustive search capabilities of LLMs: it begins from an extreme Ideal Oracle and projects real-world constraints in stages to converge onto an executable implementation.

---

## 1. Paradigm Shift

| Dimension | Traditional Development (Human-Centric) | Constraints Projection (AI-Native) |
| --- | --- | --- |
| **Starting Point** | Design grounded in real-world constraints (languages, frameworks, resources) | Zero-cost, zero-input Ideal Oracle model ($f() \to \text{Output}$) |
| **Primary Driver** | Defensive coding and proactive exception handling guided by human intuition | AI-driven enumeration of ideal assumptions $\to$ mapping to physical/system constraints |
| **Objective** | Failure defense and liability diffusion (downside protection) | Deriving the optimal compromise between the ideal state and physical limits |

---

## 2. Operational Process

To prevent attention dilution, each phase executes sequentially in strictly isolated contexts.

```text
[Phase 1: Ideal Assumption] --> [Phase 2: Constraints Identification] --> [Phase 3: Projection & Action]
   (Disregard reality limits)         (Enumerate physical/business constraints)   (Accept / Compromise / Abandon)
```

### Phase 1. Positing the Ideal Oracle (Ideal Assumptions)

Disregard practical feasibility and derive an ideal state where only the desired outcome is produced with zero input, zero latency, and zero cost.

```python
def solve():
    return do_anything_you_want()  # Instant execution, zero cost, zero side effects
```

* **Assumption 1 (Zero Input):** The system immediately comprehends context without requiring input parameters or state lookups.
* **Assumption 2 (Instant Execution):** Computation completes with $O(1)$ complexity and $0\text{ms}$ latency.
* **Assumption 3 (Unlimited Resource):** Memory, bandwidth, and API quotas/costs are limitless.
* **Assumption 4 (Zero State Drift):** Concurrency conflicts and data loss are fundamentally precluded.

### Phase 2. Identifying Constraints (Constraints Identification)

Independently map the real-world boundaries (laws of physics, hardware limitations, business rules) that conflict with each assumption.

* **Constraint A:** Network RTT and bandwidth limits across distributed nodes.
* **Constraint B:** Ambiguity arising from the absence of explicit user input.
* **Constraint C:** Cost ceilings on external infrastructure and LLM calls.

### Phase 3. Projecting Constraints (Projection & Decision)

Project constraints onto assumptions to determine the final signatures and implementation strategy.

* **Assumption 1 (Zero Input) $\to$ [Compromise]**
  * *Decision:* Accept only minimal essential identifiers as inputs; inject derived context automatically from local caches.

* **Assumption 2 (Instant Execution) $\to$ [Abandon]**
  * *Decision:* $0\text{ms}$ latency is impossible. Transition to eventual consistency backed by asynchronous queues (`Job/Worker`).

* **Assumption 4 (Zero State Drift) $\to$ [Accept]**
  * *Decision:* Enforce immutable event streams (Event Sourcing) to eliminate state drift entirely.

---

## 3. Application to Existing Codebases (Incremental Projection)

When extending existing features, set "preserve existing inputs + achieve target output + zero marginal cost" as the default ideal baseline.

1. **Ideal Delta:** Assume existing $f(x)$ instantly returns $f'(x) \to y'$ without modifications or side effects.
2. **Projection:**
   * Project interface compatibility constraints $\to$ Verify existing callers cannot be broken.
   * Project performance constraints $\to$ Verify synchronous computation is infeasible.
3. **Result:** Gradual convergence via Adapter patterns and background task decoupling.

---

## 4. Why This Fits AI

* **Managing Combinatorial Explosion:** While humans suffer cognitive overload when mapping many-to-many relationships between ideal assumptions and constraints, LLMs exhaustively cross-validate extensive constraint matrices without omission.
* **Eliminating Preconceptions:** LLMs uncover optimal architectures that developers prematurely discard as "impossible anyway" by backtracking from the ideal state.

---

## 5. Execution Pipeline Design (Preventing Attention Dilution)

To prevent performance degradation caused by conflating distinct phases, isolate contexts across pipeline stages:

1. **Pipeline-1 (Generator):** Enumerate exclusively ideal assumptions (prompt strictly forbidding mention of real-world constraints).
2. **Pipeline-2 (Critic):** Map system specifications, physical constraints, and runtime environments.
3. **Pipeline-3 (Resolver):** Reconcile 1 and 2 to determine accept/compromise/abandon decisions for each assumption, producing the final implementation specification.
