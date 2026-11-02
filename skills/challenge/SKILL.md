---
name: challenge
role: Challenge assumptions and stress-test decisions
activation: "`/challenge`, assumption review"
modification-authority: None
description: Challenge assumptions and stress-test a plan, decision, or idea through an adaptive, focused inquiry path. Operates in grounded mode when codebase, docs (context.md), or ADRs exist, or light mode for early ideas without repository evidence.
---

# Adaptive Challenge Path

Stress-test plans and technical decisions before implementation.

## Operating Contract

Read-only: produce one confirmed decision summary in chat without modifying code, config, docs, tests, or plan files. The user owns decisions and trade-offs.

Modes:

- **Grounded mode:** Codebase, tests, `context.md`, or ADRs exist.
- **Light mode:** Grounded conditions not met (early idea; no code, tests, `context.md`, or ADRs).

## Fast Path

Applies when all applicable gates pass (Grounded: all 6; Light: 1, 2, 4, 5):

1. Reversible, inexpensive rollback.
2. Local to one area.
3. No changes to public API, schema, auth, state transitions, invariants, or domain language *(Grounded only)*.
4. Minimal inspection clarifies goal, constraints, approach, and validation.
5. No unresolved material decisions affecting scope, behavior, or risk.
6. No `context.md` or ADR update required *(Grounded only)*.

Output short-form decision summary in chat, then hand off directly to implementation under AGENTS.md rules without waiting for confirmation; this skill writes nothing itself.

## Standard Path

Triggered when any Fast-path gate fails. Inspect repository facts, docs, code, and types first; do not ask for verifiable facts.

- **Questioning:** One material decision at a time in dependency order. 2-4 options with `(Recommended)` first.
- **Question fields:** Recommendation, Why, Trade-off / Counter-argument, Decision requested.
- **Post-answer summary fields:** Decision, Recommendation, Why, Risk mitigated.

## Context & Documentation (Grounded mode)

- **Discovery order:** 1. Repo guidance -> 2. Local docs (`context.md`, ADRs) -> 3. Target code and tests.
- **Maintain `context.md`:** Propose updates for entities, value objects, invariants, boundaries, or lifecycle rules.
- **Maintain ADRs:** Propose ADRs for hard-to-reverse or high-trade-off architectural choices.
- Approved `context.md` and ADR updates are applied during implementation.

## Output & Handoff

Output decision summary in chat upon confirmation:

- **Summary fields:** Mode (`Challenge Grounded` | `Challenge Light`) | Path (`Fast` | `Standard`) | Next step | Decisions | Domain term changes / ADRs affected (if applicable) | Challenged assumptions | Risks & mitigations | Revisit triggers.
  - *Fast path:* Short form (omit unaffected domain terms, ADRs, revisit triggers).
  - *Standard path:* Full form.
- **Handoff:**
  - Fast path: Direct to implementation under AGENTS.md rules.
  - Standard path: User confirmation -> `lean-design` (if structural modeling needed) or direct to implementation.
