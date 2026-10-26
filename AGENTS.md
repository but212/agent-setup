# AGENTS.md

## Precedence and Invariant Hierarchy

System instructions establish immutable safety boundaries. Explicit user intent directs task objectives within those boundaries. Repository invariants in `AGENTS.md` govern code architecture, verification, and contracts over general conventions.

- Ambiguity or contract collisions require immediate clarification before modifying files.
- Do not stage, commit, push, reset, discard, or clean changes, and never run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf`, unless explicitly requested.
- Safeguards, security boundaries, and existing regression tests must never be weakened.

## Minimal Blast Radius and Scope Gating

Every state mutation must be the minimal closed subset resolving the approved task.

- Read-only analysis must not alter files, schemas, tests, or documentation.
- Modify only files required for the approved scope; never touch lockfiles, generated assets, schemas, or migrations without explicit instruction.
- Multi-step tasks track execution via an agent plan artifact or a dated plan file (.plans/YYYY-MM-DD/[task-name].md). Execution remains paused until plan approval.
- Isolate shared root causes at domain boundaries. Remove only symbols rendered unused by the current edit; do not prune pre-existing dead code.

## Contract Soundness and State Modeling

- Baseline First: Model minimal algebraic domain representations satisfying core invariants before applying non-functional constraints.
- Eliminate impossible states at the type and schema level; avoid reliance on defensive branching or convention-based caller discipline.
- Classify external assumptions into Environment (platform facts), Requirement (intent), and Design (chosen model). Ground every constraint in observable evidence.
- Dissolve pass-through indirection, single-impl interfaces, and speculative abstractions. Match repository patterns exactly.

## Empirical Verification and TDD

Logical deduction cannot substitute for empirical execution.

- Follow test-driven development for logic changes: write failing test -> minimal implementation -> verify pass.
- Write deterministic regression tests isolating time, randomness, and concurrency. Test observable contracts, transitions, and boundary failures rather than private implementation details.
- Never assert or report verification for unrun commands, unexecuted branches, or unverified failure paths.
- Execute repository-native test commands starting from the narrowest relevant vector.

## Adversarial Falsification

- Audit changes skeptically against regressions, invalid states, and hollow indirection.
- Every reported defect is admissible if and only if accompanied by a constructible counterexample:
  - `[P1]`: Broken invariant, security breach, or data corruption.
  - `[P2]`: Unsound contract, unhandled state transition, or unverified branch.
  - `[P3]`: Dead symbol, unneeded complexity, or structural redundancy.

## Handoff and Integration Integrity

- Deliver answers directly: lead with the decision or outcome without conversational preamble, restatements, or speculative commentary.
- Resolve integration conflicts by preserving behavior, schema contracts, and unrelated work from both sides.
- Audit the final diff before handoff to guarantee absence of untracked assets, debug noise, secret leakage, or incidental whitespace changes.
