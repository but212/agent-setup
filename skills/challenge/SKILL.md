---
name: challenge
description: Router and entry point to challenge assumptions and stress-test a plan, decision, or idea by routing to challenge-light or challenge-docs based on repository evidence.
disable-model-invocation: true
---

# Mode Detection & Routing

## Operating contract

Inspect environment context and invoke exactly one sub-skill with evidence. Never prompt for mode selection when codebase/doc evidence exists. Selected sub-skill owns questioning, challenge pass, and approval handoff.

When `mark-plan` is active, keep planning artifacts in `.plans/<task-name>.md`; otherwise keep them in the response and do not create ad hoc plan files.

## Scope and controls

- **Scope:** Route only; the selected sub-skill owns questioning, artifacts, and handoff.
- **Activate:** `/challenge` or an explicit request to stress-test assumptions.
- **Deactivate:** After routing to exactly one sub-skill.

## Routing selection

Select exactly one path:

- **`challenge-docs`:** Any repository, source file, test, architecture document, `context.md`, or ADR is available. Ground decisions in the repository; docs-only repositories use this path.
- **`challenge-light`:** No repository or project documents are available. Challenge assumptions, trade-offs, and failure modes without repository overhead.

Do not invoke both paths. The selected child owns the remainder of the interaction.
