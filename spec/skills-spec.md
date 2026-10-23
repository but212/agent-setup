# Agent Skills Integration Specification

- Status: `candidate`
- Purpose: Define repository agent skills architecture, operating boundaries, routing interactions, and validation contracts.

## 1. Scope and Core Architecture

### Included

- Skill selection and routing based on request intent
- Repository-grounded planning, design, implementation, testing, and review
- Response prose and documentation compression with invariant preservation
- Plan file lifecycle (`.plans/YYYY-MM-DD/[task-name].md`) and permanent specification coordination
- Dependency-free validation of skill metadata, plan conventions, ASCII Markdown, and safety guards
- Mirroring deployment of `AGENTS.md` and `skills/` into the shared agent directory

### Excluded

- File changes outside approved skill modification authority
- Speculative requirements, abstractions, or unnecessary dependencies
- Unapproved execution or scope expansion

### Shared Invariants and Operational Rules

Authoritative behavioral rules, prompt precedence, safety boundaries, and execution invariants (including evidence priority, minimum change, boundary preservation, verifiability, and approval boundaries) are defined in [AGENTS.md](../AGENTS.md). In addition, skills and maintainers adhere to:

- **Single source of truth (SSOT):** Detailed skill workflows, roles, activation triggers, and modification authority belong solely to their respective `skills/*/SKILL.md` frontmatter.

## 2. Skill Catalog and Metadata

Each skill in `skills/*/SKILL.md` declares scalar frontmatter fields:

- `name`: Matches directory name.
- `role`: One-line summary of responsibility.
- `activation`: Triggers and command aliases.
- `modification-authority`: Scope of allowable write permissions.
- `description`: Multiline overview of skill purpose.

Frontmatter serves as the sole source of truth (SSOT) and is machine-validated by `scripts/validate-skills.py`.

## 3. Routing and Handoffs

### 3.1 Challenge Routing

`challenge` stress-tests plans and decisions through an adaptive path:

- Grounded mode: Selected when repository, source files, tests, `context.md`, or ADRs exist.
- Light mode: Selected for early-stage idea exploration without codebase context.
- Questioning presents 2-4 options with `(Recommended)` first, one decision at a time.

### 3.2 Implementation Routing

1. Run `lean-design` first when state representation, types, data, or API boundaries are central.
2. Use `spec-drive` to coordinate contract-sensitive work, manage `.plans/` execution tracking, and slice TDD contracts.
3. Use `lean-mode` for minimal code and deterministic test changes mapped to contracts.
4. Use `lean-review` for read-only adversarial diff or repository audits.

### 3.3 Execution Modes

- `spec-drive` coordinates contract changes and defaults to a read-only specification and plan.

- Before explicit execution approval, work remains in `planned` state.

### 3.4 Plan Tracking Rules

When `spec-drive` execution tracking is active, `.plans/YYYY-MM-DD/[task-name].md` (or a supported agent plan artifact) is the execution SSOT:

- Lifecycle: `planned -> in-progress|cancelled`, `in-progress -> blocked|complete|cancelled`, or `blocked -> in-progress|cancelled`.
- Do not execute checklist items while the plan is `planned` and awaiting approval.
- Plan structure contains Goal, Scope, Evidence and assumptions, Contracts, Invariants, TDD slices and checklist, and Decisions and deviations.
- Each TDD slice item maps contract IDs (`C-NN`), Red/Green/Refactor/Verify steps, and verification commands.
- Check items only after verification passes; record deviations immediately under Decisions and deviations.

### 3.5 Deployment Mirror Rules

`scripts/deploy_agents.py` mirrors repository content into the shared agent folder (`~/.agents`, overridable via `AGENT_HOME`):

- Accepts `--link` to create a symlink to global instructions where supported.
- Target is a copy destination; repository is the source of truth.
- Destination permissions and path safety (avoiding symlink loops or root overwrites) are checked before write.

## 4. Quality Gates

- [ ] Every skill frontmatter defines valid `name`, `role`, `activation`, and `modification-authority`.
- [ ] Claims and decisions are grounded in code, tests, or explicit requirements.
- [ ] Read-only skills make no file modifications.
- [ ] Markdown files are strictly ASCII-only.
- [ ] `python3 scripts/validate-skills.py` and `python3 -m unittest discover -s tests -v` pass.

## 5. Stabilization Policy

The specification remains `candidate` while changes are in progress. Promote to `stable` when:

1. Every `skills/*/SKILL.md` contains verified frontmatter and self-contained contracts.
2. Approval boundaries, plan lifecycle, and destructive-command guards are validated.
3. Repository-native validation and unit tests pass cleanly without errors or skips.
