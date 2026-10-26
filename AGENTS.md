# AGENTS.md

## Purpose

Repository-wide guidance and instruction precedence for coding agents.

## Instruction precedence

1. System and developer instructions.
2. User's explicit request, except where violating absolute rules below (weakening tests/safeguards, adding secrets/sensitive values, destructive commands).
3. Nearest applicable `AGENTS.md`; deeper files override broader files.
4. Repository documentation, configuration, and established code conventions.

If instructions conflict or requirements are materially ambiguous, stop and ask. Do not silently change public contracts, data models, security boundaries, or user-visible behavior.

## Before changing files

- Inspect relevant source, tests, configuration, and documentation; search existing helpers, types, and patterns.
- Identify the smallest file and symbol set satisfying the request.
- Classify behavior claims as `Confirmed`, `Assumption`, or `Open decision` until resolved by evidence.
- Inspect working tree first; preserve unrelated changes.

## Implementation principles

- Make the smallest correct change; avoid unrelated refactors, speculative abstractions, and formatting churn.
- Prefer existing dependencies, helpers, types, and platform primitives over premature generalization.
- Make invalid states unrepresentable; handle nulls, partial failure, concurrency, and schema mismatches deliberately.
- Preserve public APIs, schemas, validation, error handling, authorization, accessibility, and domain invariants.
- Fix shared root causes. Never weaken tests or safeguards; never add secrets, credentials, personal data, or sensitive values.

## Scope and approval

- Read-only analysis and planning must not modify code, tests, or permanent documentation.
- Modify only paths needed for approved requests; do not change generated files, lockfiles, schemas, or migrations unless requested.
- Multi-step tasks track execution via an agent plan artifact or a dated plan file (.plans/YYYY-MM-DD/[task-name].md). Work remains in planned state until explicit execution approval is granted. Check items only upon deterministic verification pass.
- Keep existing plans and specifications synchronized. Permanent specifications govern domain rules, contracts, and architecture; plans track execution only.

## Verification

- Use documented, repository-native commands from configs, scripts, CI definitions, or docs; do not guess global commands. Start with narrowest relevant checks.
- Follow test-driven development for logic changes: write failing test -> minimal implementation -> verify pass.
- Add deterministic tests for changed observable behavior and regressions (boundary, transition, invalid, and failure paths).
- Control time, randomness, network, and asynchronous completion; run broader checks when warranted.
- Report exact commands and results. Never claim an unrun or failed check passed.

## Documentation and synchronization

- Update permanent documentation when behavior, contracts, architecture, operational requirements, or domain rules change.
- Permanent specifications govern architecture specs, `context.md` (domain terms), and ADRs (hard-to-reverse decisions); plans track execution only.
- Preserve commands, paths, identifiers, conditions, exceptions, links, and machine-readable content; do not invent unsupported requirements.
- Keep documentation concise, factual, and consistent with implementation.

## Communication and Git handoff

- Lead with the answer or decision. Be direct and concise without omitting requirements, constraints, identifiers, commands, errors, order, or next actions.
- Avoid repetition, filler, and unsupported certainty; preserve code blocks, commands, paths, identifiers, and machine-readable text.
- Resolve integration conflicts by preserving behavior, schema contracts, and unrelated work from both sides.
- Do not stage, commit, push, reset, discard, or clean changes, and never run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf`, unless explicitly requested.
- Review the diff before finishing for accidental files, debug output, secrets, and unnecessary changes; summarize paths, behavior, verification results, failures, assumptions, and follow-up.
