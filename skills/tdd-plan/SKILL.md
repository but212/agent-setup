---
name: tdd-plan
description: Create an implementation-ready TDD plan from a requirement and repository evidence.
---

# TDD Planning

Create a test-first implementation plan. Do not output implementation code.

## Operating contract

Consume an approved requirement or contract and produce only deterministic test slices. `tdd-plan` owns Red/Green/Verify/Refactor sequencing; `lean-mode` owns production implementation. Do not redesign domain structure or edit production code.

1. **Grounding:** Inspect target code, nearby tests, test commands, and comparable features. Record exact paths and commands. Mark unresolved facts as assumptions.
2. **Contracts:** Map requirements to observable contracts (input/condition and expected result). Add boundary, failure, compatibility, or integration coverage only when established by requirements or repository evidence.
3. **Boundaries:** Use the smallest test boundary exercising each contract. Cross real system boundaries only when required by the behavior under test.
4. **Slicing:** Build plan in small vertical slices in dependency order:
   - **Red:** Failing test path, test name, and proved behavior.
   - **Green:** Smallest source change making the test pass.
   - **Verify:** Command proving slice and related behavior pass.
   - **Refactor:** Concrete duplication/design issue exposed after Green, or `None`.

When `mark-plan` is active, this output defines the TDD section of `.plans/<task-name>.md`; do not create a competing plan artifact.

Use this authoritative output format:

## Evidence

- Confirmed: exact repository facts, paths, conventions, and commands
- Assumptions: unresolved facts shaping the plan
- Scope note: use the smallest applicable slice for simple local changes; expand only for established boundary, failure, compatibility, or integration behavior.

## Contracts

| ID | Behavior | Condition or Input | Expected Result |
| --- | --- | --- | --- |

## Plan

### 1. [Contract or slice name]

- Red: `[test path]` — `[test name and expected failure]`
- Green: `[source path]` — `[smallest required change]`
- Verify: `[command]`
- Refactor: `[concrete change]` or `None`

Repeat for each slice in dependency order.

## Open Decisions

List only unresolved decisions producing materially different contracts or plans.

## Controls

- **Scope:** Test planning only; do not edit production code.
- **Handoff:** Pass the approved slices to `lean-mode` only when implementation is explicitly requested.
- **Activate:** `/tdd-plan` or an explicit request for an implementation-ready TDD plan.
