---
name: challenge-light
description: Challenge assumptions and stress-test a plan, decision, or idea through an adaptive, focused inquiry path without requiring an existing codebase or durable project artifacts.
disable-model-invocation: true
---

# Adaptive Challenge Path

## Operating contract

Consume an early-stage request or decision without repository evidence and produce one confirmed decision summary. Use **Fast path** only when all 4 gates pass; otherwise use **Standard path**. The user owns decisions and trade-offs; challenge assumptions only, not implementation or test plans.

## Fast path

Use only when **all 4** pass:

1. Reversible and low-cost to adjust.
2. Local to one area or topic.
3. No unresolved material decisions affecting goals, constraints, or approach.
4. Minimal inspection clarifies goals, constraints, and validation criteria.

Provide compact plan for user confirmation: Goal & scope | Approach | Validation criteria | Assumptions | Risks & escalations.

## Standard path

Use when any Fast-path gate fails. Challenge core assumptions and ask material decisions one at a time in dependency order.

- **Questioning:** Ask the user one material decision at a time. Present 2-4 options with `(Recommended)` first.
- **Format:** Recommendation | Why | Trade-off / Counter-argument | Decision requested.
- **Post-answer summary:** Decision | Recommendation | Why | Risk mitigated.

## Controls

- **Scope:** Read-only challenge without repository artifacts.
- **Activate:** Explicit `/challenge` routing or a codebase-free idea challenge.
- **Deactivate:** After the decision summary and handoff.

## Output & handoff

After confirmation, update the active `mark-plan` plan when present; otherwise report only in chat. Hand off to `tdd-plan`, `lean-design`, or `lean-mode`; do not create a second planning artifact.

When resolved, output:

- **Summary:** Mode (`Challenge Light`) | Plan | Next step | Decisions | Defaults | Challenged assumptions | Risks & mitigations | Revisit triggers.
- **Artifacts:** Record the decision and plan changes in `.plans/YYYY-MM-DD/<task-name>.md` when `mark-plan` is active; otherwise report in chat without creating ad hoc plan files.
- **Handoff:** Propose the next skill (`tdd-plan`, `lean-design`, or `lean-mode`).
