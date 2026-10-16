# Agent Skills Integration Specification

- Status: `candidate`
- Basis: 16 current `skills/*/SKILL.md` files
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

The skill contracts define prompt engineering as input/output interfaces and a communication protocol, not persona or prose decoration:

1. **Interfaces, not spells:** Define explicit inputs and authoritative outputs; do not rely on magic keywords or role-play.
2. **Decomposition:** Split complex workflows into routed skills with explicit handoffs and separate modification authority (see Section 3).
3. **Evaluation over format:** State success criteria and edge-case handling; verify with deterministic, repository-native checks.
4. **Iterative refinement:** Start with the simplest contract and add constraints only when verification exposes a need.

### Shared Invariants

1. **Evidence first:** Infer intent in this order: runtime behavior, tests, types, schemas, and documentation. Mark unverifiable facts as assumptions. Classify material claims as `Confirmed`, `Assumption`, or `Open decision` until evidence resolves them.
2. **Minimum change:** Make the smallest change that satisfies the current requirement; avoid unrelated refactoring.
3. **Preserve boundaries:** Do not remove or weaken input validation, error handling, security, authorization, accessibility, or domain invariants.
4. **Verifiability:** Verify changed behavior with repository-native tools. Claim success only when the actual command succeeds.
5. **Separate permissions:** Read-only diagnostic skills do not modify files; implementation skills modify only approved scope.
6. **Explicit handoffs:** Hand design to implementation and test plans to implementation explicitly.
7. **Approval boundary:** Analysis and planning are read-only by default. Do not modify code, tests, or permanent documentation without user approval.
8. **Separate authority:** Permanent specifications govern domain rules, public contracts, and architecture; `.plans/YYYY-MM-DD/` tracks execution state by plan creation date only.
9. **Single source of truth:** Detailed skill workflows and operational contracts belong solely to their respective `skills/*/SKILL.md`. This specification defines catalog membership, routing, and shared invariants without duplicating internal skill contracts.
10. **Keyboard portability:** All Markdown content is ASCII-only so it can be entered on a standard US QWERTY keyboard; use ASCII equivalents for arrows, dashes, quotes, and other Unicode punctuation.

## 2. Skill Catalog

Each `skills/*/SKILL.md` declares scalar `role`, `activation`, and `modification-authority` frontmatter fields. The validator compares these fields exactly with the catalog row, so routing and write authority have one machine-checked source of parity.

| Skill | Role | Activation | Modification authority |
| --- | --- | --- | --- |
| `challenge` | Selects a challenge path using repository evidence | `/challenge`, assumption review | None |
| `challenge-docs` | Repository- and documentation-grounded decision challenge | Repository or documentation exists | None |
| `challenge-light` | Early idea challenge without repository evidence | No supporting evidence exists | None |
| `crisp` | Compresses response prose | `/crisp`, `/crisp on` | None |
| `crisp-docs` | Compresses general documentation | Named documentation compression request | Named files only |
| `crisp-agent-docs` | Compresses agent rule documents | Named `SKILL.md` or similar request | Named files only |
| `crisp-commit` | Generates evidence-based Conventional Commits | Commit-message request | None |
| `git-conflict` | Resolves Git integration conflicts while preserving contracts and unrelated work | Explicit Git conflict or non-fast-forward integration task | Approved integration scope |
| `lean-design` | Designs around states, types, and boundaries | Structural, invariant, or API design request | None |
| `lean-mode` | Makes the smallest correct code change | Implementation, fix, or refactor request | Approved code scope |
| `lean-review` | Adversarial diff or repository review | Code review or full audit request | None |
| `lean-test` | Designs, writes, or diagnoses minimal deterministic tests | Test request | Test scope only |
| `mark-plan` | Tracks execution through `.plans/` files | Planning mode or checklist request | Plan file |
| `tdd-plan` | Creates an implementation-ready TDD plan | TDD plan request | None |
| `sql-orm-indicator-audit` | Audits SQL and ORM query risks | Explicit audit request | None (read-only) |
| `spec-drive` | Coordinates contract-centered SDD | `/spec-drive`, contract-sensitive change | Contract coordination only |

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

- `spec-drive` owns contract coordination and defaults to a read-only specification, risk assessment, and plan.
- With `/crisp` and `/spec-drive`, `spec-drive` coordinates the task while `crisp` controls response prose only.
- Before explicit execution approval, produce only a `planned` state or analysis; afterward, modify production code, tests, or permanent documentation only within the approved authority.
- If a permanent specification conflicts with an execution plan, stop and present the conflict and its location.

### 3.4 Plan File Rules

When `mark-plan` is active, `.plans/YYYY-MM-DD/<task-name>.md` is the execution SSOT. Create the ISO-date folder for new plans and search all date folders when reusing one.

- State: `planned -> in-progress|cancelled`, `in-progress -> blocked|complete|cancelled`, or `blocked -> in-progress`.
- Do not execute checklist items while the plan is `planned` and awaiting approval.
- Each checklist item has acceptance criterion IDs, target paths, and a verification command.
- Check items only after verification; record failures, decisions, and deviations immediately.
- Do not silently reuse or resume a `complete` plan.
- Keep execution contracts, scope, and progress in the plan; synchronize domain and architecture requirements with permanent specifications. Link copied contracts to their permanent source.

### 3.5 Deployment Mirror Rules

`scripts/deploy_agents.py` (and its wrappers `scripts/deploy-agents.sh` and `scripts/deploy-agents.ps1`) mirror repository content into the shared agent folder (`~/.agents`, overridable via `AGENT_HOME`). The CLI entry points accept `--link` (or `-Link` in PowerShell).

- The deployment target is a copy destination only; the repository remains the source of truth.
- Skills mirroring uses a scoped Python mirror (with deletions limited to stale copies inside `<target>/skills/`), invoked directly or via POSIX (`sh`) and PowerShell (`ps1`) wrappers.
- `AGENT_HOME` is canonicalized before writes; resolving to `/` or `$HOME` is refused.
- Existing symlinked targets or destination entries (`AGENT_HOME`, `AGENTS.md`, `skills/`, or pi's agent directory) are refused before writes.
- A real (non-symlink) file at pi's global instructions path is never overwritten; `--link` refuses instead.
- Relative `AGENT_HOME` values are supported and produce an absolute pi global-instructions link.

## 4. Quality Gates

- [ ] The selected skill matches the request scope and modification authority.
- [ ] Core claims and decisions are grounded in code, tests, documentation, or explicit user requirements.
- [ ] Validation, error handling, security, and accessibility at public boundaries are preserved.
- [ ] Every executable contract has deterministic verification; non-executable contracts record a verification method.
- [ ] When a plan is used, every checklist item and acceptance criterion has a recorded verification result.
- [ ] Read-only skills did not modify files.
- [ ] Permanent domain and architecture specifications are synchronized with the change.
- [ ] No authority conflict exists between the plan and permanent specifications.
- [ ] The actual `skills/*/SKILL.md` files match the catalog's names, activation rules, and modification authority.
- [ ] Markdown content is ASCII-only.
- [ ] `python3 scripts/validate-skills.py` and `python3 -m unittest discover -s tests -v` pass when the validation script and tests exist, including dated plan-path, Markdown ASCII, deployment, and catalog validation.

## 5. Stabilization Policy

The specification remains `candidate` while any required contract, catalog, safety, documentation, or validation gate is incomplete. Promote it to `stable` only when all of the following are true:

1. Every `skills/*/SKILL.md` has valid metadata and exactly one catalog entry.
2. Catalog entries match actual names, activation rules, roles, handoffs, and modification authority.
3. Approval boundaries, plan lifecycle, authority separation, and destructive-command restrictions are explicit and reviewed.
4. Routing and handoff rules have representative, ecosystem-neutral verification cases.
5. `AGENTS.md` and `README.md` describe the same safety and discovery model without contradictory instructions.
6. The repository-native validation command passes, and the final diff has been reviewed.
7. No unresolved breaking-change decision, blocker, unsupported requirement, or open stabilization question remains.

A change that invalidates any gate returns the status to `candidate` until the gate is restored and recorded.

## 6. Current Repository Documentation State

The repository currently contains the 16 skill documents under `skills/`; no product code, APIs, or domain models were found. The repository now has dependency-free regression tests for deployment and catalog contracts. This document therefore defines skill operations and does not invent product contracts. When product functionality is added, document its specification separately and update this document only for skill-operation changes.
