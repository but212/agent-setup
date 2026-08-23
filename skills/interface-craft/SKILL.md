---
name: interface-craft
description: Design guidance for new visual directions and established UI changes. Grounds frontend choices in the brief, existing product language, accessibility, and rendered behavior without forcing a template.
---

# Frontend Design

Apply when tasks alter visual hierarchy, layout, typography, color, motion, interaction presentation, or copy. Skip non-visual frontend work (state/API/routing).

## Operating contract

Consume an approved visual requirement or `interface-audit` finding and produce the minimal visible change. `interface-craft` owns visual implementation; `interface-audit` remains read-only and owns diagnosis.

Select the visual path, ground in brief/tokens, define checks, and execute the minimal visible change only after the user requests implementation or approves the plan. This skill may edit frontend source files, but must not alter unrelated product areas. Never force a new visual identity onto an established product.

## Path Selection

- **Lean path (Existing UI):** Component, layout, style, copy, accessibility, or responsive fix in established surfaces.
- **Full path (New visual direction):** New page, landing page, major redesign, or new product surface.

## Grounding Gate

Inspect target surface, nearby patterns, design tokens, and brief constraints. Define checks for: responsive behavior, keyboard focus, reduced motion, contrast, semantic structure, and rendered result.

## Lean Path: Existing UI

Preserve established visual language, tokens, component boundaries, semantics, and copy vocabulary.

Show before coding:

```text
Grounding: affected surface / existing pattern or token / constraints
Intended change: one sentence describing the visible outcome
Checks: responsive / focus / motion / contrast / render result
```

## Full Path: New Visual Direction

Express the subject's world with an intentional opening thesis.

Show before coding:

```text
Brief: audience / single job / constraints
Direction: palette / type / layout / signature
Checks: existing patterns / responsive / focus / motion / contrast / render result
```

- **Typography:** Pair display and body roles intentionally with clear scale and weights.
- **Color:** Compact palette (4–6 values); prefer existing product tokens.
- **Structure:** Use numbering, eyebrows, and dividers only to encode real relationships.
- **Motion:** One coherent motion concept respecting reduced motion.
- **Signature:** At most one memorable differentiator.
- **Defaults rule:** Do not default to cream/serif/terracotta, near-black/acid, or broadsheet layouts unless explicitly justified.

## Handoff and output

For existing UI, consume `interface-audit` findings when available. Before editing, report Grounding, Intended change, and Checks. After editing, report changed paths and rendered/keyboard/responsive verification; do not claim render verification when it was unavailable.

## Controls

- **Scope:** Frontend visual changes only; edit only approved target paths.
- **Activate:** `/interface-craft` or an explicit request to implement a UI change.
- **Deactivate:** `stop interface-craft` or `normal mode`.

## Quality Floor

- Ensure visible keyboard focus, semantic controls, responsive layouts, reduced motion compliance, and usable contrast.
- Use sentence-case, active-voice copy with consistent control labels across errors, empty, and loading states.
- Evaluate rendered output and remove or simplify an unnecessary decorative element when one is evidenced; do not remove elements merely to satisfy this checklist.
