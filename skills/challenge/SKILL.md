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
disable-model-invocation: true
---

# Adaptive Challenge Path

Challenge assumptions and stress-test a plan or technical decision before implementation.

## Operating contract

Consume a request or technical decision and produce one confirmed decision summary. The user owns decisions and trade-offs. Challenge scope and trade-offs only; do not modify code, config, docs, tests, or implementation before confirmation.

Select path based on evidence:

- **Grounded mode:** Any repository, source file, test, architecture document, `context.md`, or ADR is available.
- **Light mode:** No codebase or project documentation exists.

## Fast path

Use Fast path only when all gates pass:

- **Grounded mode (all 6 gates):**
  1. Reversible and inexpensive rollback.
  2. Local to one area.
  3. No changes to public API, schema, auth, state transitions, domain invariants, or ubiquitous language.
  4. Minimal inspection clarifies goal, constraints, approach, and validation.
  5. No unresolved material decisions affecting scope, behavior, or risk.
  6. No `context.md` or ADR update required.

- **Light mode (all 4 gates):**
  1. Reversible and low-cost to adjust.
  2. Local to one area or topic.
  3. No unresolved material decisions affecting goals, constraints, or approach.
  4. Minimal inspection clarifies goals, constraints, and validation criteria.

Provide compact plan for user confirmation: Goal & scope | Target areas / Approach | Intended change | Tests & validation | Assumptions | Risks & escalations.

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

After confirmation, output the decision summary in chat without modifying files. When an active plan coordinator (such as `spec-drive`) is present, hand off the confirmed decision summary to it for recording. Hand off to `spec-drive`, `lean-design`, or `lean-mode`.

When resolved, output:

- **Summary:** Mode (`Challenge Grounded` or `Challenge Light`) | Plan | Next step | Decisions | Domain term changes / ADRs affected (if applicable) | Challenged assumptions | Risks & mitigations | Revisit triggers.
- **Handoff:** Propose next skill (`spec-drive`, `lean-design`, or `lean-mode`).
