---
name: interface-audit
description: Audit an existing web interface surface for visual hierarchy, interaction quality, accessibility, responsive behavior, and copy using evidence from the target project. Use when asked to audit, review, critique, or assess a route, component, screen, screenshot, or UI change. Produce a prioritized report only; do not edit files.
---

# Interface Audit

Audit the specified UI surface and report evidence-backed improvements. Never edit source files, configuration, docs, or design assets.

## Audit Contract

`interface-audit` owns evidence-based read-only diagnosis; `interface-craft` owns approved visual implementation. The audit output is the only handoff artifact between them.

- **Scope:** Target route, component, screen, screenshot, or UI change + nearby patterns/tokens.
- **Output:** Prioritized report only. Never modify project files.
- **Evidence:** Classify as `observed`, `documented`, or `inferred`. Cite file:line, test, or render state.
- **Priority:** User impact and urgency over aesthetic preference.

## Workflow

1. **Gate & Define Input:** Confirm target surface and single job. Infer job/audience from project evidence when missing and state assumptions. For screenshots without source access, perform static visual audit.
2. **Establish Local Truth:** Inspect target component, styles, dependencies, nearby screens, design tokens, responsive conventions, and docs. Prefer existing patterns over generic design advice.
3. **Gather Visual Evidence:** Check rendering availability across desktop and mobile viewports. Record route/artifact, viewport, state, and static vs. rendered status. Visual claims without code/token/render backing must use medium/low confidence.
4. **Select Dimensions:** Apply Hierarchy/Layout (always), Typography/Color (text/themes), Semantics/Interaction (controls/focus), Motion/Resilience (animations/overflow/failures), Copy/States (labels/empty/loading/disabled).
5. **Write Findings:** Format each finding as:

```text
ID: IA-###
Severity: blocker | high | medium | low
Location: file:line, selector, component, route, or rendered state
Evidence type: observed | documented | inferred
Evidence: concrete code, token, document, test, or render observation
User impact: affected user & risk/friction
Principle: applicable local rule or quality criterion
Recommended direction: smallest effective change
Confidence: high | medium | low
```

- **blocker:** Prevents primary task; requires `observed`/`documented` evidence.
- **high:** Materially harms task/accessibility/responsive use; requires `observed`/`documented` evidence.
- **medium:** Noticeable friction/inconsistency. `inferred` evidence capped at `medium`.
- **low:** Polish or minor clarity issue.
  _Sort order:_ Severity → User impact → Confidence.

## Report Format

1. **Surface and intent:** Target, single job, audience, states, and assumptions.
2. **Evidence checked:** Files, tokens, docs, tests, viewport states, missing verification.
3. **Findings:** Formatted and sorted findings (or state none with supporting evidence).
4. **What is working:** Grounded strengths to preserve (omit if none).
5. **Verification gaps:** Unresolved uncertainties, unavailable render checks, missing intent.
6. **Priority summary:** Smallest ordered set of impactful changes.

## Controls

- **Scope:** Read-only UI audit; never edit source, configuration, docs, or design assets.
- **Activate:** `/interface-audit` or an explicit request to audit a UI surface.
- **Handoff:** Pass prioritized findings to `interface-craft` only after the user requests implementation.

## Self-Check & Harness Rules

Before returning the report, confirm target/job clarity, complete finding fields, correct severity caps/sorting, viewport specs for rendered evidence, and zero project file edits. Follow workflow sequence for deterministic audits.
