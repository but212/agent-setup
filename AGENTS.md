# AGENTS.md

## Purpose

This file provides repository-wide guidance for coding agents. Follow it together with the user's request, repository documentation, and any more-specific `AGENTS.md` files.

## Instruction precedence

1. System and developer instructions.
2. The user's explicit request.
3. The nearest applicable `AGENTS.md`; deeper files override broader files.
4. Repository documentation, configuration, and established code conventions.

If instructions conflict or a requirement is materially ambiguous, stop and ask for clarification. Do not silently choose a behavior that changes a public contract, data model, security boundary, or user-visible behavior.

## Before changing files

- Inspect relevant source, tests, configuration, and documentation first; search for existing helpers, types, and patterns.
- Identify the smallest file and symbol set that can satisfy the request.
- Classify behavior claims as `Confirmed`, `Assumption`, or `Open decision` until evidence resolves them.
- Check the working tree first and preserve unrelated changes.

## Implementation principles

- Make the smallest correct change; avoid unrelated refactors, speculative abstractions, and formatting churn.
- Prefer existing dependencies, helpers, types, and platform primitives; choose simple local solutions over premature generalization.
- Make invalid states unrepresentable and handle nulls, partial failure, concurrency, and schema mismatches deliberately.
- Preserve public APIs, schemas, validation, error handling, authorization, accessibility, and domain invariants unless explicitly changed.
- Fix shared root causes. Never weaken tests or safeguards, or add secrets, credentials, personal data, or sensitive values.

## Scope and approval

- Read-only analysis and planning must not modify code, tests, or permanent documentation.
- Modify only paths needed for the approved request; do not change generated files, lockfiles, schemas, or migrations unless required.
- Keep existing plans and specifications synchronized. Permanent specifications govern domain rules, contracts, and architecture; plans track execution only.

## Verification

- Discover and use documented, repository-native commands from configs, scripts, CI definitions, or docs; do not guess or execute arbitrary global commands. Start with the narrowest relevant checks.
- Add deterministic tests for changed observable behavior and regressions, including applicable boundary, transition, invalid, and failure paths.
- Control time, randomness, network, and asynchronous completion where applicable; run broader checks when warranted.
- Report exact commands and results. Never claim an unrun or failed check passed.

## Documentation and synchronization

- Update permanent documentation when behavior, contracts, architecture, operational requirements, or domain rules change.
- Preserve commands, paths, identifiers, conditions, exceptions, links, and machine-readable content; do not invent unsupported requirements.
- Keep documentation concise, factual, and consistent with implementation.

## Communication and Git handoff

- Lead with the answer or decision. Be direct and concise without omitting requirements, constraints, identifiers, commands, errors, order, or next actions.
- Avoid repetition, filler, and unsupported certainty; preserve code blocks, commands, paths, identifiers, and machine-readable text unless asked to change them.
- Do not stage, commit, push, reset, discard, or clean changes unless explicitly asked.
- Never run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf` unless explicitly requested.
- Preserve unrelated work. Before finishing, review the diff for accidental files, debug output, secrets, and unnecessary changes; summarize paths, behavior, verification results, failures, assumptions, and follow-up.
