# AGENTS.md

## Precedence and Invariant Hierarchy

System instructions establish immutable safety boundaries. Explicit user intent directs task objectives within those boundaries. Repository invariants in `AGENTS.md` govern code architecture, verification, and contracts over general conventions.

- Clarify before modifying files only when ambiguity yields divergent behavioral outcomes or execution is blocked; proceed on reasonable default assumptions otherwise.
- Do not stage, commit, push, reset, discard, or clean changes, and do not run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf`, without explicit user request.
- Safeguards, security boundaries, and existing regression tests must never be weakened.

## Minimal Blast Radius and Scope Gating

Every state mutation must be the minimal closed subset resolving the approved task.

- Read-only analysis must not alter files, schemas, tests, or documentation.
- Modify only paths needed for approved requests; never touch lockfiles, generated assets, schemas, or migrations without explicit instruction.
- Multi-step tasks track execution via an agent plan artifact for single-session workflows, or a dated plan file (.plans/YYYY-MM-DD/[task-name].md) for persistent cross-session changes. Execution of persistent plans or contract-breaking changes remains paused until explicit user approval; single-session workflows proceed on reasonable default assumptions.
- Fix shared root causes at domain boundaries (e.g. normalize or validate once at schema or ingress rather than patching symptoms across scattered call sites). Remove only symbols rendered unused by the current edit; do not prune pre-existing dead code.

## Contract Soundness and State Modeling

- Baseline First: Model minimal algebraic domain representations satisfying core functional invariants before applying non-functional constraints (performance optimizations, caching, concurrency, or backwards-compatibility hooks).
- Eliminate impossible states at the type and schema level; avoid defensive branching in internal domain logic, while strictly validating and parsing untrusted inputs at external boundaries (network, storage, user input).
- Classify external assumptions into Environment (platform facts), Requirement (intent), and Design (chosen model). Ground every constraint in observable evidence.
- Dissolve speculative abstractions and single-impl interfaces, except where repository patterns, test mocks (e.g. traits), or established conventions explicitly warrant them; repository patterns take precedence.
- When authoring or modifying SKILL.md, emit only single-line scalar strings or inline JSON arrays in frontmatter; never use multiline block scalars (| or >) or indented list items.

## Empirical Verification and TDD

Logical deduction cannot substitute for empirical execution.

- Follow test-driven development for logic changes: write failing test -> minimal implementation -> verify pass.
- Write deterministic regression tests isolating time, randomness, and concurrency. Verify invariant laws, type contracts, state transitions, and boundary edge cases.
- Forbid brittle assertion of detailed phrasing, exact prose wording, or cosmetic formatting that breaks under benign edits; assert observable functional outcomes, typed data contracts, and failure exit states.
- Never assert or report verification for unrun commands, unexecuted branches, or unverified failure paths. When missing toolchains or network barriers prevent execution, explicitly report checks as Unverified with blocker details.
- Execute repository-native test commands starting from the narrowest relevant vector.

## Adversarial Falsification

- Scope: Active only during explicit review tasks or final diff audits; do not apply during implementation.
- Audit changes skeptically against regressions, invalid states, and hollow indirection.
- Every reported defect is admissible if and only if accompanied by a constructible counterexample or deterministic static evidence (e.g. zero referencing call sites, unreachable branches, single-caller pass-through wrappers):
  - `[P1]`: Broken invariant, security breach, or data corruption.
  - `[P2]`: Unsound contract, unhandled state transition, or unverified branch.
  - `[P3]`: Dead symbol (report for awareness; do not delete pre-existing dead code), unneeded complexity, or structural redundancy (e.g. indirection without polymorphism or transformation).

## Handoff and Integration Integrity

- Deliver answers directly: lead with the decision or outcome without conversational preamble, restatements, or speculative commentary.
- Resolve integration conflicts by preserving behavior, schema contracts, and unrelated work from both sides.
- Audit the final diff before handoff to guarantee absence of untracked assets, debug noise, secret leakage, or incidental whitespace changes.
