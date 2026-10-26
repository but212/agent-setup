# Agent Skills Integration Specification

- Status: `stable`
- Purpose: Define repository agent skills architecture, operating boundaries, routing interactions, and validation contracts.

## 1. Scope and Core Architecture

### Included

- Skill selection and routing based on request intent.
- Repository-grounded planning, design, implementation, testing, and review.
- Response prose and document compression (`crisp`) with invariant preservation.
- Git integration conflict resolution (`git-conflict`) with preserved unrelated work.
- Plan lifecycle (`.plans/YYYY-MM-DD/[task-name].md`) and permanent specification synchronization.
- Dependency-free validation of frontmatter, plan paths, ASCII Markdown, and safety guards.
- Mirror deployment of `AGENTS.md` and `skills/` into the shared agent directory.

### Excluded

- File modifications exceeding approved skill authority.
- Speculative requirements, abstractions, or unrequested dependencies.
- Unapproved execution or scope expansion.

### Shared Invariants and Operational Rules

Authoritative behavioral rules, precedence, safety boundaries, and execution invariants are defined in [AGENTS.md](../AGENTS.md).

- **Single source of truth (SSOT):** Detailed workflows, role bindings, activation triggers, and modification authority belong exclusively to `skills/*/SKILL.md`: scalar metadata in frontmatter, workflows and the `spec-drive` Role Registry in the body.

## 2. Skill Catalog and Metadata

Each skill in `skills/*/SKILL.md` declares scalar frontmatter fields:

- `name`: Matches directory name.
- `role`: One-line responsibility summary.
- `activation`: Triggers and command aliases.
- `modification-authority`: Permitted write scope.
- `description`: Multiline overview of skill purpose.

Frontmatter is validated by `scripts/validate-skills.py`.

## 3. Routing and Handoffs

### 3.1 Challenge Routing

`challenge` stress-tests plans and decisions through an adaptive path:

- Grounded mode: Selected when repository, source files, tests, `context.md`, or ADRs exist.
- Light mode: Selected for early idea exploration without codebase context.
- Questioning presents 2-4 options with `(Recommended)` first, one decision at a time.

### 3.2 Implementation Routing

1. Run `lean-design` first when state representations, types, schemas, or API boundaries are central.
2. Use `spec-drive` to coordinate contract-sensitive work, manage `.plans/` execution tracking, and slice TDD contracts.
3. Use `lean-mode` for minimal code and deterministic test changes mapped to contracts.
4. Use `lean-review` for read-only adversarial diff or repository audits.
5. Use `git-conflict` for Git integration conflicts. It is standalone: it does not route through `spec-drive`, and its Conflict report is terminal output.

Role names (Plan Coordinator, Structural Designer, Implementation Engine, Review Gate) are bound only in the `spec-drive` Role Registry. Other skills reference them by name and default.

### 3.3 Execution Modes

- `spec-drive` coordinates contract changes and defaults to a read-only specification and plan.
- Work remains in `planned` state until explicit execution approval is granted.

### 3.4 Plan Tracking Rules

When `spec-drive` execution tracking is active, `.plans/YYYY-MM-DD/[task-name].md` (or an agent plan artifact) is the execution SSOT:

- Lifecycle: `planned -> in-progress|cancelled`, `in-progress -> blocked|complete|cancelled`, or `blocked -> in-progress|cancelled`. `scripts/validate-skills.py` (`PLAN_TRANSITIONS`) enforces that `spec-drive` documents these transitions and that each plan `Status` is a known value.
- Do not execute checklist items while `planned` and awaiting approval.
- Plan structure: Goal, Scope, Evidence and assumptions, Contracts, Invariants, TDD slices and checklist, and Decisions and deviations.
- Each TDD slice item maps contract IDs (`C-NN`), Red/Green/Refactor/Verify steps, and verification commands.
- Check items only on a Verification Record with `Result: pass` (`lean-mode` format); record deviations under Decisions and deviations.

### 3.5 Deployment Mirror Rules

`scripts/deploy_agents.py` mirrors repository content into `~/.agents` (overridable via `AGENT_HOME`):

- `--link` symlinks global instructions where supported.
- Destination is a copy target; repository is the source of truth.
- Destination permissions and path safety (preventing symlink loops or root overwrites) are validated before write.

## 4. Quality Gates

- [x] Every skill frontmatter defines valid `name`, `role`, `activation`, and `modification-authority`.
- [x] Claims and decisions are grounded in code, tests, or explicit requirements.
- [x] Read-only skills make no file modifications.
- [x] Markdown files are strictly ASCII-only.
- [x] `python3 scripts/validate-skills.py` and `python3 -m unittest discover -s tests -v` pass.

## 5. Stabilization Policy

The specification remains `candidate` during active development. Promote to `stable` when:

1. Every `skills/*/SKILL.md` contains verified frontmatter and self-contained contracts.
2. Approval boundaries, plan lifecycle, and destructive-command guards are validated.
3. Repository-native validation and unit tests pass cleanly without errors or skips.
