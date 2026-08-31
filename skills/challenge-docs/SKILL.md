---
name: challenge-docs
description: Challenge assumptions and stress-test a plan or technical decision grounded in codebase context, shared domain docs (context.md), and durable decision records (ADRs).
disable-model-invocation: true
---

# Adaptive Challenge Path (Grounded)

## Operating contract

Consume a repository-grounded request or decision and produce one confirmed decision summary. Use **Fast path** only when all 6 gates pass; otherwise use **Standard path**. The user owns decisions and trade-offs. Challenge scope and trade-offs only; do not modify code, config, docs, tests, or implementation before confirmation.

## Fast path

Use only when **all 6** pass:

1. Reversible and inexpensive rollback.
2. Local to one area.
3. No changes to public API, schema, auth, state transitions, domain invariants, or ubiquitous language.
4. Minimal inspection clarifies goal, constraints, approach, and validation.
5. No unresolved material decisions affecting scope, behavior, or risk.
6. No `context.md` or ADR update required.

Provide compact plan for user confirmation: Goal & scope | Target areas | Intended change | Tests & validation | Assumptions | Risks & escalations.

## Standard path

Use when any Fast-path gate fails. Inspect repository facts, docs, code, and types first; do not ask for verifiable facts. Challenge assumptions and ask material choices one at a time in dependency order.

- **Questioning:** Ask the user one material decision at a time. Present 2-4 options with `(Recommended)` first.
- **Format:** Recommendation | Why | Trade-off / Counter-argument | Decision requested.
- **Post-answer summary:** Decision | Recommendation | Why | Risk mitigated.

## Context & Documentation

- **Discovery order:** 1. Repo guidance -> 2. Local docs (`context.md`, ADRs) -> 3. Target code & tests. Propose minimal `context.md` for new domain terms.
- **Maintain `context.md`:** Propose updates for entities, value objects, invariants, boundaries, or lifecycle rules.
- **Maintain ADRs:** Propose ADRs for hard-to-reverse or high-trade-off architectural choices.

## Controls

- **Scope:** Read-only challenge; no edits before confirmation.
- **Activate:** Explicit `/challenge` routing or a repository-grounded challenge request.
- **Deactivate:** After the decision summary and handoff.

## Output & handoff

After confirmation, update the active `mark-plan` plan when present; otherwise report only in chat. Hand off to `tdd-plan`, `lean-design`, or `lean-mode`; do not create a second planning artifact.

When resolved, output:

- **Summary:** Mode (`Challenge Docs`) | Plan | Next step | Decisions | Domain term changes | ADRs affected | Challenged assumptions | Risks | Revisit triggers.
- **Artifacts:** Record the decision and plan changes in `.plans/YYYY-MM-DD/<task-name>.md` when `mark-plan` is active; otherwise report in chat without creating ad hoc plan files.
- **Handoff:** Propose the next skill (`tdd-plan`, `lean-design`, or `lean-mode`).
