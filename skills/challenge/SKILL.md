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

Challenge assumptions and stress-test a plan or technical decision before implementation.

## Operating contract

Consume a request or technical decision and produce one confirmed decision summary. The user owns decisions and trade-offs. Challenge scope and trade-offs only; do not modify code, config, docs, tests, or implementation before confirmation.

Select path based on evidence:

- **Grounded mode:** Any repository, source file, test, architecture document, `context.md`, or ADR is available.
- **Light mode:** No codebase or project documentation exists.

## Fast path

Use Fast path only when all applicable gates pass:

1. Reversible and inexpensive rollback.
2. Local to one area.
3. No changes to public API, schema, auth, state transitions, domain invariants, or ubiquitous language. *(Grounded only)*
4. Minimal inspection clarifies goal, constraints, approach, and validation.
5. No unresolved material decisions affecting scope, behavior, or risk.
6. No `context.md` or ADR update required. *(Grounded only)*

Grounded mode requires all 6 gates; Light mode requires gates 1, 2, 4, and 5. When all applicable gates pass, output the short-form decision summary for user confirmation. Do not write plan files; `challenge` produces only in-chat decision summaries.

## Standard path

Use when any Fast-path gate fails. Inspect repository facts, docs, code, and types first; do not ask for verifiable facts. Challenge assumptions and ask material choices one at a time in dependency order.

- **Questioning:** Ask the user one material decision at a time. Present 2-4 options with `(Recommended)` first.
- **Format:** Recommendation | Why | Trade-off / Counter-argument | Decision requested.
- **Post-answer summary:** Decision | Recommendation | Why | Risk mitigated.

## Context & Documentation (Grounded mode)

- **Discovery order:** 1. Repo guidance -> 2. Local docs (`context.md`, ADRs) -> 3. Target code & tests. Propose minimal `context.md` for new domain terms.
- **Maintain `context.md`:** Propose updates for entities, value objects, invariants, boundaries, or lifecycle rules.
- **Maintain ADRs:** Propose ADRs for hard-to-reverse or high-trade-off architectural choices.

## Controls

- **Scope:** Read-only challenge; no edits before confirmation.
- **Activate:** Explicit `/challenge` or request to stress-test assumptions.
- **Deactivate:** After the decision summary and handoff.

## Output & handoff

After confirmation, output the decision summary in chat without modifying files or writing plan files (`spec-drive` owns plan files). When an active plan coordinator (such as `spec-drive`) is present, hand off the confirmed decision summary to it for recording.

When resolved, output one unified decision summary:

- **Decision Summary:** Mode (`Challenge Grounded` or `Challenge Light`) | Path (`Fast` or `Standard`) | Next step | Decisions | Domain term changes / ADRs affected (if applicable) | Challenged assumptions | Risks & mitigations | Revisit triggers.
  - *Fast path:* short form omitting domain terms, ADRs, and revisit triggers if unaffected.
  - *Standard path:* full form above.
- **Handoff:**
  - Fast path: hand off directly to Implementation Engine (default: `lean-mode`) for execution, or to Plan Coordinator (default: `spec-drive`) if a formal plan is requested.
  - Standard path: hand off to Plan Coordinator (default: `spec-drive`) (or Structural Designer, default: `lean-design`, if structural modeling is required); never hand off directly from Standard path to Implementation Engine (default: `lean-mode`).
