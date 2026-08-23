---
name: lean-review
description: >
  Adversarial review for semantic regressions, over-engineering, structural drift,
  YAGNI, and surgicality drift. Supports diff-level and repository-wide scopes and
  produces a prioritized report without modifying files.
---

# Lean Review

Audit changes or the repository for semantic regressions, over-engineering, structural drift, YAGNI, and surgicality drift by synthesizing `lean-design` and `lean-mode`. Use `diff` for the default change review or `repo` for a repository-wide (or module-wide) audit.

## Operating contract

- Start from adversarial hypothesis that the diff is wrong. Independently compare with specification, invariants, and pre-change behavior; seek executable counterexamples to meaning preservation (ownership/lifetime, failure paths, boundaries, observable behavior) even when compilation and tests pass.
- Read-only review: report prioritized, evidence-backed findings from changed lines and direct call/type boundaries; do not edit files or conflate review with fixing.
- Every finding needs a concrete reproduction condition and failure mechanism.
- Scale falsification to the diff: for documentation, formatting, or trivial changes, verify affected contract without inventing exhaustive execution scenarios.
- Preserve safety controls, security gates, input validation, error handling, accessibility, and domain invariants.

## Core Review Vectors

1. **Semantic Preservation (`[semantic]`)**: Changed observable behavior or broken specification, invariant, ownership/lifetime, or failure-path contracts; require a concrete counterexample.
2. **Surgicality & Scope (`[surgical]`)**: Opportunistic refactoring, non-essential edits, diff scope creep, or dead code left behind (`lean-mode`).
3. **Structural Drift (`[drift]`)**: Unconstrained types, optional/nullable sprawl, loose primitives, or missing state invariants (`lean-design`).
4. **Speculative Abstractions (`[yagni]`)**: Single-implementation interfaces, unused generics, premature factories, unnecessary wrappers, or dead flexibility (`lean-design`).
5. **Boundary Integrity (`[boundary]`)**: Stripped input validation, weakened error handling, or missing auth/permission checks.
6. **Repository Redundancy (`[consolidate]`, `[stdlib]`)** *(repo scope)*: Duplicate helpers across module boundaries or custom utilities that reinvent stdlib/platform APIs (`lean-mode`).
7. **Dead Surfaces (`[delete]`)** *(repo scope)*: Unused functions, exports, types, constants, parameters, or unreachable branches (`lean-mode`).

## Non-Negotiables

Never recommend removal or simplification of:

- Input validation at trust boundaries
- Error handling preventing data loss or crashes
- Security controls, auth checks, and permission gates
- Accessibility mechanisms
- Required domain complexity and business invariants

## Workflow

The requested scope is `diff` by default. Keep synthesis and report generation common to both paths.

### `diff`

1. **Identify**: Target the diff (`git diff`, `git diff --cached`, commit range, or files).
2. **Evidence Gathering**: Compare observable behavior before and after; trace call paths, surrounding types, ownership/lifetime, and invariants.
3. **Falsification**: Test the change against the core vectors and decision ladders before assessing style or approval.

### `repo`

1. **Scope Identification**: Determine whether the request targets the full repository or named modules. Prefer named modules when the repository is large; state the inspected boundary and any excluded areas.
2. **Evidence Gathering**: Trace call paths, types, exports, and boundaries using repository-native navigation tools, `module_report`, and targeted search.
3. **Cross-Module Detection**: Check for duplicate helpers across module boundaries, custom utilities replaceable by stdlib/platform APIs, and dead or orphaned export surfaces. Treat dynamic imports, runtime registration, generated entrypoints, and test-only reachability as uncertainty sources; report deletion candidates for confirmation rather than asserting they are dead.

### Common Synthesis and Report Generation

1. **Synthesis**: Evaluate evidence against the core vectors, decision ladders, and structural design principles; scale falsification to the scope.
2. **Report Generation**: Provide prioritized findings with locations, evidence, and the smallest alternative. For trivial or documentation-only diffs, do not invent exhaustive execution scenarios.

## Output Format

For each finding:

- **Priority**: `[P1]` (correctness/security/release-blocking risk) | `[P2]` (material contract/design risk) | `[P3]` (minor cleanup)
- **Location**: `path/to/file.ext:12`; use clickable workspace links in final reports when supported.
- **Tag**: One tag from the [Tag taxonomy](#tag-taxonomy).
- **Issue**: Concise explanation of the contract break, semantic regression, over-engineering, or structural defect.
- **Evidence**: Reproduction condition, execution order, call path, type/export reference, command result, or code fact proving the issue.
- **Expected / Actual**: For `[semantic]` or `[boundary]`, state both and why compilation or tests miss the defect.
- **Minimal Alternative / Action**: Direct minimal alternative, removal target, or refactoring target.

### Tag Taxonomy

| Tag | Meaning | Replacement action |
| --- | --- | --- |
| `[semantic]` | Observable behavior or domain contract violation. | Restore the contract with the smallest verified change. |
| `[surgical]` | Unrelated refactoring or scope creep. | Revert non-essential lines. |
| `[drift]` | Type model permits impossible states. | Restrict the union or domain type. |
| `[yagni]` | Indirection, single-implementation interface, unused factory, or premature abstraction. | Inline the implementation or use direct logic. |
| `[boundary]` | Weakened safety validation or error control. | Restore the control. |
| `[delete]` | Unused code, dead exports, or orphaned variables. | Remove them. |
| `[shrink]` | Over-complex logic or wrappers. | Replace with direct, simpler logic. |
| `[retype]` | Suboptimal type permitting invalid states. | Retype with stricter domain bounds. |
| `[consolidate]` | Duplicate helper across files or modules. | Reuse an existing shared boundary or smallest local implementation. |
| `[stdlib]` | Custom code duplicating a stdlib or platform API. | Use the built-in feature. |

If no issues exist for diff scope: `Diff is lean. No evidence-backed issues detected.`
If no issues exist for repo scope: `Repository is lean. No over-engineering detected.`

## Controls

- **Scope**: `diff` (default) is a read-only diff / PR code-change review; `repo` is a read-only repository- or module-wide audit.
- **Activate**: `/lean-review`, `/lean-review repo`, an explicit request to review a diff, or natural language such as “audit the whole repo” or “find over-engineering across the codebase.”
- **Deactivate**: `stop lean-review` or `normal mode`.
