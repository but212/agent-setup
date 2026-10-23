---
name: challenge
role: Challenge assumptions and stress-test decisions
activation: "`/challenge`, assumption review"
modification-authority: None
description: >
  Challenge assumptions and stress-test a plan, decision, or idea through an
  adaptive, focused inquiry path. Operates in grounded mode when codebase, docs
  (context.md), or ADRs exist, or light mode for early ideas without repository
  evidence.
---

# Adaptive Challenge Path

Stress-test plans and technical decisions before implementation.

## Operating contract

Produce one confirmed decision summary without modifying code, config, docs, tests, or plan files (`spec-drive` owns plan files). The user owns decisions and trade-offs.

Modes:
- **Grounded mode:** Codebase, tests, `context.md`, or ADRs exist.
- **Light mode:** No codebase or project documentation exists.

## Fast path

Applies when all applicable gates pass:
1. Reversible, inexpensive rollback.
2. Local to one area.
3. No changes to public API, schema, auth, state transitions, invariants, or domain language. *(Grounded only)*
4. Minimal inspection clarifies goal, constraints, approach, and validation.
5. No unresolved material decisions affecting scope, behavior, or risk.
6. No `context.md` or ADR update required. *(Grounded only)*

Grounded mode requires all 6 gates; Light mode requires gates 1, 2, 4, and 5. Output the short-form decision summary in chat for user confirmation.

## Standard path

Triggered when any Fast-path gate fails. Inspect repository facts, docs, code, and types first; do not ask for verifiable facts.

- **Questioning:** Ask one material decision at a time in dependency order. Present 2-4 options with `(Recommended)` first.
- **Question format:** Recommendation | Why | Trade-off / Counter-argument | Decision requested.
- **Post-answer summary:** Decision | Recommendation | Why | Risk mitigated.

## Context & Documentation (Grounded mode)

- **Discovery order:** 1. Repo guidance -> 2. Local docs (`context.md`, ADRs) -> 3. Target code and tests.
- **Maintain `context.md`:** Propose updates for entities, value objects, invariants, boundaries, or lifecycle rules.
- **Maintain ADRs:** Propose ADRs for hard-to-reverse or high-trade-off architectural choices.

## Controls

- **Scope:** Read-only challenge; in-chat summaries only.
- **Activate:** Explicit `/challenge` or assumption review request.
- **Deactivate:** Concluded upon decision summary confirmation and handoff.

## Output & handoff

Output the decision summary in chat upon confirmation. When an active plan coordinator is present, hand off to it for recording.

- **Decision Summary:** Mode (`Challenge Grounded` or `Challenge Light`) | Path (`Fast` or `Standard`) | Next step | Decisions | Domain term changes / ADRs affected (if applicable) | Challenged assumptions | Risks & mitigations | Revisit triggers.
  - *Fast path:* short form omitting domain terms, ADRs, and revisit triggers if unaffected.
  - *Standard path:* full form above.
- **Handoff:**
  - Fast path: hand off directly to Implementation Engine (default: `lean-mode`) for execution, or to Plan Coordinator (default: `spec-drive`) if a formal plan is requested.
  - Standard path: hand off to Plan Coordinator (default: `spec-drive`) (or Structural Designer, default: `lean-design`, if structural modeling is required); never hand off directly from Standard path to Implementation Engine (default: `lean-mode`).
