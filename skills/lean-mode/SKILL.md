---
name: lean-mode
description: >
  Produces the smallest correct coding change. Use for writing, adding,
  refactoring, fixing code, choosing dependencies, or implementing requested
  changes. Do not use for read-only code or diff review; use `lean-review`.
  Also use when
  the user requests a minimal, simple, lazy, YAGNI, short-path, or non-bloated
  solution. Use after `lean-design` when structural design is also required.
  Do not use for prose compression, document style, or non-coding requests.
---

# Lean Mode

Choose the smallest correct change for coding tasks. `crisp-*` handles prose; this skill handles executable code and repository changes. `lean-review` owns read-only diff and repository reviews.

Invoke `lean-design` first when state, type, data, or API design is the main problem. If `lean-design` is inactive, perform a brief structural pass over states, invariants, and boundaries before editing.

## Operating contract

Consume an approved requirement, structural design, or TDD slice and produce the smallest correct code change. `lean-mode` owns production edits; it does not replace `tdd-plan` for test planning or `lean-review` for read-only review.

Make the smallest correct change after grounding in runtime behavior, tests, types, and call boundaries. Trace real flow end-to-end before choosing implementation.

## Routing precedence

- Use `lean-review` for read-only diff or repository audits.
- Use `lean-design` before implementation when states, invariants, types, data, or API boundaries are the main problem.
- Use `tdd-plan` for a test-first implementation plan; use `lean-test` for test-only implementation or test diagnosis.
- Use `spec-drive` instead of assembling these steps manually when the change is contract-sensitive or architecturally material.

## Performance and complexity gate

- **Performance gate**: Measure before optimizing. Change performance only when a representative baseline identifies a dominant path.
- **Required complexity**: Do not simplify away necessary complexity demanded by input, business, or environmental constraints.

## Decision ladder

Stop at first applicable rung:

1. **Need to exist?** Skip speculative work; state assumptions (YAGNI).
2. **Already in codebase?** Reuse existing helper, util, type, pattern, or installed dependency.
3. **Stdlib does it?** Use standard library.
4. **Native platform feature covers it?** Use declarative UI/CSS, DB constraints, or native primitives.
5. **Installed dependency solves it?** Use existing dependencies; do not add new packages for trivial lines.
6. **One clear line?** Prefer a single readable expression over multi-line code. Avoid unreadable ternaries or golfed hacks.
7. **Local implementation**: Write the smallest local implementation that works.

## Bug fix rule

Fix bugs at shared root cause, not symptoms in individual callers. Trace callers before editing.

## Boundaries (When NOT to minimize)

Never simplify away:

- Input validation at trust boundaries
- Error handling preventing data loss
- Security controls
- Accessibility basics
- Explicitly requested features/requirements

Avoid unrequested abstractions: single-implementation interfaces, single-product factories, or static configs for fixed values.

## Output format

For implementation requests, output the smallest code change first. For dependency selection or no-edit requests, lead with recommendation and evidence. Add at most two short lines when mechanisms are skipped:

```text
Skipped: <unnecessary mechanism>.
Add <mechanism> when <observable trigger>.
```

## Verification

Choose the narrowest repository-native check that covers the changed behavior. Non-trivial logic (branch, loop, parser, security/money path) requires a runnable check. A one-line change still requires validation when it affects a public boundary, configuration, schema, security control, or user-visible behavior; otherwise no test is required.

## Controls

- **Scope**: Bounded coding changes and implementation.
- **Activate**: `/lean-mode` or an explicit request to implement, fix, or refactor code.
- **Deactivate**: `stop lean-mode` or `normal mode`.
