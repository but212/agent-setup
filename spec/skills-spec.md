# Agent Skills Integration Specification

- Status: `candidate`
- Basis: 14 current `skills/*/SKILL.md` files
- Last verified: 2026-08-24
- Purpose: Define when repository agent skills activate, what scope they cover, what they produce, and how the setup reaches stable status.

## 1. Scope and Shared Rules

### Included

- Skill selection and handoffs based on request intent
- Repository-grounded planning, design, implementation, testing, and review
- Documentation and commit-message generation and quality verification
- Synchronization between plan files and permanent specifications
- Dependency-free validation of skill metadata, catalog parity, routing markers, and safety guards
- Deployment mirroring of `AGENTS.md` and `skills/` into the shared agent folder

### Excluded

- File changes explicitly prohibited by a skill
- Unsupported requirements, abstractions, tests, or performance optimization
- Implementation or scope expansion without user approval

### Prompt Design Principles

The skill contracts implement prompt engineering as input/output interface design and a communication protocol between the model and the task, not as prose writing:

1. **Interfaces, not spells:** Every skill defines explicit inputs (operating contracts) and expected outputs (authoritative output formats); persona role-play and magic keywords are not used.
2. **Decomposition over one-shot prompts:** Complex workflows are split into routed skills with explicit handoffs and separated modification authority (see Section 3).
3. **Evaluation criteria over format:** Skills state the logical criteria good output must satisfy and how edge cases are handled; verification is repository-native and deterministic.
4. **Iterative refinement over static templates:** Work starts from the simplest contract and gains constraints only where verification fails (TDD slices, plan state transitions, stabilization policy).

### Shared Invariants

1. **Evidence first:** Infer intent in this order: runtime behavior, tests, types, schemas, and documentation. Mark unverifiable facts as assumptions.
2. **Minimum change:** Make the smallest change that satisfies the current requirement; avoid unrelated refactoring.
3. **Preserve boundaries:** Do not remove or weaken input validation, error handling, security, authorization, accessibility, or domain invariants.
4. **Verifiability:** Verify changed behavior with repository-native tools. Claim success only when the actual command succeeds.
5. **Separate permissions:** Read-only diagnostic skills do not modify files; implementation skills modify only approved scope.
6. **Explicit handoffs:** Hand design to implementation and test plans to implementation explicitly.
7. **Approval boundary:** Analysis and planning are read-only by default. Do not modify code, tests, or permanent documentation without user approval.
8. **Separate authority:** Permanent specifications govern domain rules, public contracts, and architecture; `.plans/YYYY-MM-DD/` tracks execution state by plan creation date only.

## 2. Skill Catalog

| Skill | Role | Activation | Modification authority |
| --- | --- | --- | --- |
| `challenge` | Selects a challenge path using repository evidence | `/challenge`, assumption review | None |
| `challenge-docs` | Repository- and documentation-grounded decision challenge | Repository or documentation exists | None |
| `challenge-light` | Early idea challenge without repository evidence | No supporting evidence exists | None |
| `crisp` | Compresses response prose | `/crisp`, `/crisp on` | None |
| `crisp-docs` | Compresses general documentation | Named documentation compression request | Named files only |
| `crisp-agent-docs` | Compresses agent rule documents | Named `SKILL.md` or similar request | Named files only |
| `crisp-commit` | Generates evidence-based Conventional Commits | Commit-message request | None |
| `lean-design` | Designs around states, types, and boundaries | Structural, invariant, or API design request | None |
| `lean-mode` | Makes the smallest correct code change | Implementation, fix, or refactor request | Approved code scope |
| `lean-review` | Adversarial diff or repository review | Code review or full audit request | None |
| `lean-test` | Designs, writes, or diagnoses minimal deterministic tests | Test request | Test scope only |
| `mark-plan` | Tracks execution through `.plans/` files | Planning mode or checklist request | Plan file |
| `tdd-plan` | Creates an implementation-ready TDD plan | TDD plan request | None |
| `spec-drive` | Coordinates contract-centered SDD | `/spec-drive`, `/sdd`, contract-sensitive change | Contract coordination only |

## 3. Routing and Handoffs

### 3.1 Challenge Routing

`challenge` selects exactly one child path.

- Select `challenge-docs` when a repository, source file, test, architecture document, `context.md`, or ADR exists.
- Select `challenge-light` when no project documentation exists.
- Do not run both paths.
- The result is a decision summary confirmed by the user; do not create an implementation plan or code directly.

### 3.2 Implementation Routing

1. Run `lean-design` first when states, types, data, or API boundaries are central.
2. Use `tdd-plan` when a test-first plan is needed, then hand implementation to `lean-mode`.
3. Use `lean-test` for test-only work.
4. Use `spec-drive` to coordinate contract-sensitive work involving state transitions, persistence, security, public contracts, or major architecture decisions.
5. Use `lean-review` for read-only diff or repository audits; it does not modify files.
6. `lean-mode` does not replace `lean-review`, `tdd-plan`, or `lean-test`.

### 3.3 Execution Modes and Composed Activation

- `spec-drive` owns contract coordination. Its default output is a read-only specification, risk assessment, and plan.
- When `/crisp` is active with `/spec-drive`, `spec-drive` coordinates the task and `crisp` controls response prose only.
- Production code, tests, and permanent documentation may be modified only after explicit execution approval.
- Before approval, produce only a `planned` state or analysis; do not extend delegated skills' modification authority.
- If a permanent specification conflicts with an execution plan, stop and present the conflict and its location.

### 3.4 Plan File Rules

When `mark-plan` is active, `.plans/YYYY-MM-DD/<task-name>.md` is the execution SSOT; create the ISO-date folder when creating a plan and search all date folders when reusing one.

- State: `planned → in-progress → complete|cancelled`, or `in-progress ↔ blocked`.
- Do not execute checklist items while the plan is `planned` and awaiting approval.
- Each checklist item has acceptance criterion IDs, target paths, and a verification command.
- Do not check an item before verification; record failures, decisions, and deviations in the plan immediately.
- Do not silently reuse or resume a `complete` plan.
- Keep execution contracts in the plan and synchronize domain and architecture requirements with permanent repository documentation.
- Permanent specifications govern domain rules, public contracts, and architecture decisions.
- When copying contracts into a plan, link to their permanent specification source; the plan tracks scope, checklist, and verification state only.

### 3.5 Deployment Mirror Rules

`scripts/deploy-agents.sh` and `scripts/deploy-agents.ps1` mirror repository content into the shared agent folder (`~/.agents`, overridable via `AGENT_HOME`). The PowerShell entry point uses `-Link`; the POSIX entry point uses `--link`.

- The deployment target is a copy destination only; the repository remains the source of truth.
- Skills mirroring uses `rsync --delete` on POSIX and an equivalent scoped mirror on PowerShell; deletions are limited to stale copies inside `<target>/skills/`.
- `AGENT_HOME` resolving to `/` or `$HOME` is refused before any write.
- A real (non-symlink) file at pi's global instructions path is never overwritten; `--link` refuses instead.

## 4. Skill Contracts

### 4.1 Challenge Skills

#### `challenge-docs`

- Goal: Stress-test plans or decisions using the codebase, `context.md`, and ADRs.
- Use the Fast path only when the change is reversible, local, does not alter public APIs, schemas, authentication, state transitions, or domain invariants, and has no material ambiguity.
- Otherwise ask one material decision at a time with a recommendation, reason, counterargument, and decision request.
- Propose a `context.md` update for new domain terms and an ADR for hard-to-reverse choices.

#### `challenge-light`

- Confirm goals, constraints, approach, validation, and risks for early ideas without repository evidence.
- Use the Fast path only when reversibility, locality, decision clarity, and minimal inspection all hold.

### 4.2 Crisp Skills

#### `crisp`

Lead with the answer. Prioritize correctness, safety, explicit requirements, grounding, clarity, force, and minimalism. Do not omit identifiers, commands, errors, order, constraints, or next actions. Do not alter code blocks or machine-readable text unless asked.

#### `crisp-docs`

Compress only explicitly named general documentation in place. Preserve facts, conditions, exceptions, links, commands, and structure. Do not modify generated content, code, configuration, or machine-readable data. Stop when the target, audience, or references are ambiguous.

#### `crisp-agent-docs`

Compress only explicitly named agent rule documents such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and `SKILL.md`. Preserve mandatory terms, exceptions, safety, verification, paths, and identifiers. Do not modify when rules conflict or references are missing.

#### `crisp-commit`

Read `git status`, staged and unstaged diffs, targeted untracked files, and the five latest log entries to produce an evidence-based message. Follow recent commit language; use English when the repository language is unclear. Select an appropriate `feat|fix|refactor|style|docs|test|chore` type and never stage or commit.

### 4.3 Design, Implementation, and Test Skills

#### `lean-design`

Define data models and state transitions first, then make invalid states unrepresentable with types, enums, and constraints. Address nulls, partial failure, concurrency, and schema mismatches before happy paths. Remove unsupported abstractions, unused parameters, and speculative extension points. Output: `Problem → Structure → Remove → Implementation → Verify`; design only.

#### `lean-mode`

Make the smallest code change that satisfies an approved requirement, design, or TDD slice. Reuse existing code, helpers, types, dependencies, standard-library features, and platform primitives. Measure before optimizing. Fix bugs at the shared root cause and run the narrowest repository-native verification.

#### `tdd-plan`

Inspect code, tests, runners, and fixtures, then express contracts as conditions and expected results. Write vertical slices in dependency order as `Red → Green → Verify → Refactor`. Plan only; do not write code. Record exact paths and commands and mark unknowns as assumptions.

#### `lean-test`

Test observable public boundaries with the smallest set covering representative success, applicable empty/boundary/transition states, exposed invalid input or failure, and confirmed regressions. Control time, randomness, and async completion deterministically. Do not weaken assertions or modify production code.

### 4.4 Review Skills

#### `lean-review`

Assume the change is wrong and falsify semantic preservation, scope, structure, YAGNI, boundary integrity, duplication, and dead surfaces. Every finding includes location, reproduction condition, failure mechanism, evidence, and the smallest alternative. Use P1/P2/P3 and the defined tags. Review only; do not modify files.

### 4.5 Coordination and Synchronization Skills

#### `mark-plan`

`.plans/YYYY-MM-DD/<task-name>.md` is the single source of truth for scope, decisions, progress, and verification. Wait for review during planning and switch to `in-progress` only after explicit execution approval. Check items only after verification. Do not complete a plan with unresolved criteria, checks, failures, blockers, or open questions.

#### `spec-drive`

Own contract coordination and delegate structural design to `lean-design`, test slices to `tdd-plan`, and production edits to `lean-mode`. Its four phases are:

1. **Crisp Specification:** Define intent and boundaries, condition-to-guarantee laws, invariants and state rules, and a contracts table. Record linked invariants, test paths/names, implementation boundaries, and permanent specification paths where applicable; record verification methods for non-executable contracts.
2. **Lean Structural Design:** Make invalid states unrepresentable and remove failure-boundary risks.
3. **Surgical TDD:** Execute `Red/Green/Verify/Refactor` vertical slices for each contract.
4. **Quality & Sync:** Check contract and law coverage, repository quality, and permanent specification synchronization.
   - Classify material claims as `Confirmed`, `Assumption`, or `Open decision`.
   - Compare the catalog with actual `skills/*/SKILL.md` names, activation rules, and modification boundaries.
   - Check domain models, APIs, business rules, and platform invariants; update permanent specifications in the same change when affected.

Adopt a law only when supported by at least two distinct cases, repeated cross-boundary evidence, or explicit domain evidence. Record scope, preconditions, exceptions, counterexamples, and linked contracts. Keep one-case restatements and unsupported generalizations at the case-contract level.

- Classify changes to public inputs/outputs, error meaning, state transitions, persistence schemas, authentication, or authorization as breaking changes. Require user approval and compatibility, migration, and rollback decisions.
- Resolve ambiguity with the user before implementation.

## 5. Quality Gates

- [ ] The selected skill matches the request scope and modification authority.
- [ ] Core claims and decisions are grounded in code, tests, documentation, or explicit user requirements.
- [ ] Validation, error handling, security, and accessibility at public boundaries are preserved.
- [ ] Every executable contract has deterministic verification; non-executable contracts record a verification method.
- [ ] When a plan is used, every checklist item and acceptance criterion has a recorded verification result.
- [ ] Read-only skills did not modify files.
- [ ] Permanent domain and architecture specifications are synchronized with the change.
- [ ] No authority conflict exists between the plan and permanent specifications.
- [ ] The actual `skills/*/SKILL.md` files match the catalog's names, activation rules, and modification authority.
- [ ] `python3 scripts/validate-skills.py` passes when the validation script exists, including dated plan-path validation.

## 6. Stabilization Policy

The specification remains `candidate` while any required contract, catalog, safety, documentation, or validation gate is incomplete. Promote it to `stable` only when all of the following are true:

1. Every `skills/*/SKILL.md` has valid metadata and exactly one catalog entry.
2. Catalog entries match actual names, activation rules, roles, handoffs, and modification authority.
3. Approval boundaries, plan lifecycle, authority separation, and destructive-command restrictions are explicit and reviewed.
4. Routing and handoff rules have representative, ecosystem-neutral verification cases.
5. `AGENTS.md` and `README.md` describe the same safety and discovery model without contradictory instructions.
6. The repository-native validation command passes, and the final diff has been reviewed.
7. No unresolved breaking-change decision, blocker, unsupported requirement, or open stabilization question remains.

A change that invalidates any gate returns the status to `candidate` until the gate is restored and recorded.

## 7. Current Repository Documentation State

The repository currently contains the 14 skill documents under `skills/`; no product code, tests, APIs, or domain models were found. This document therefore defines skill operations and does not invent product contracts or executable tests. When product functionality is added, document its specification separately and update this document only for skill-operation changes.
