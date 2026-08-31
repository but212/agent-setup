---
name: challenge
description: Router and entry point to challenge assumptions and stress-test a plan, decision, or idea by routing to challenge-light or challenge-docs based on repository evidence.
disable-model-invocation: true
---

# Mode Detection & Routing

## Operating contract

Inspect context and invoke exactly one sub-skill with evidence. If repository or documentation evidence exists, choose the mode instead of asking the user to choose it. The selected child owns questioning, artifacts, and the approval handoff.

When `mark-plan` is active, keep planning artifacts in `.plans/YYYY-MM-DD/<task-name>.md`; otherwise report in chat and create no ad hoc plan files.

## Controls

- **Scope:** Route only; the selected child owns the remainder.
- **Activate:** `/challenge` or an explicit request to stress-test assumptions.
- **Deactivate:** After routing to exactly one sub-skill.

## Routing selection

Select exactly one path:

- **`challenge-docs`:** Any repository, source file, test, architecture document, `context.md`, or ADR is available. Ground decisions in the repository; docs-only repositories use this path.
- **`challenge-light`:** No repository or project documents are available. Challenge assumptions, trade-offs, and failure modes without repository overhead.

Do not invoke both paths. The selected child owns the remainder of the interaction.
