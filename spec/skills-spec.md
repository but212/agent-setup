# Agent Skills Integration Specification

- Status: `stable`
- Purpose: Define repository agent skills architecture, operating boundaries, routing interactions, and validation contracts.

## 1. Scope and Core Architecture

### Included

- Skill selection and routing for interactive challenge, structural design, and adversarial review.
- Core implementation, TDD verification, conflict resolution, and communication invariants governed by AGENTS.md.
- Plan tracking via agent plan artifacts or dated plan files (`.plans/YYYY-MM-DD/[task-name].md`).
- Dependency-free validation of frontmatter, plan paths, ASCII Markdown, and safety guards.
- Mirror deployment of `AGENTS.md` and `skills/` into the shared agent directory.

### Excluded

- File modifications exceeding approved skill authority.
- Speculative requirements, abstractions, or unrequested dependencies.
- Unapproved execution or scope expansion.

### Shared Invariants and Operational Rules

Authoritative behavioral rules, precedence, safety boundaries, and execution invariants are defined in [AGENTS.md](../AGENTS.md).

- **Single source of truth (SSOT):** Detailed workflows and activation triggers belong to `skills/*/SKILL.md` (scalar frontmatter and body). Core coding invariants (TDD, minimal changes, safety guards) belong to AGENTS.md.

## 2. Skill Catalog and Metadata

Each skill in `skills/*/SKILL.md` declares scalar frontmatter fields:

- `name`: Matches directory name (`challenge`, `lean-design`, `lean-review`).
- `role`: One-line responsibility summary.
- `activation`: Triggers and command aliases.
- `modification-authority`: Permitted write scope (`None`).
- `description`: Single-line overview of skill purpose.

Frontmatter is validated by `scripts/validate-skills.py`.

## 3. Routing and Handoffs

### 3.1 Challenge Routing

`challenge` stress-tests plans and decisions through an adaptive path:

- Grounded mode: Selected when repository, source files, tests, `context.md`, or ADRs exist.
- Light mode: Selected for early idea exploration without codebase context.
- Questioning presents 2-4 options with `(Recommended)` first, one decision at a time.

### 3.2 Structural Design Routing

`lean-design` models domain structures, state transitions, schemas, and boundaries before coding:

- Models sum types, state machines, and algebraic invariants.
- Eliminates impossible states and pass-through abstractions.
- Handoff contracts provide exact type signatures and transition rules for implementation.

### 3.3 Adversarial Review Routing

`lean-review` performs read-only audits on diffs or repositories:

- Falsifies behavior with concrete, constructible counterexamples.
- Categorizes findings by severity (`[P1]`, `[P2]`, `[P3]`).
- Strictly read-only (`modification-authority: None`), producing minimal action proposals for implementation.

### 3.4 Direct Handoff

Skills do not require an intermediary router. Each skill completes its specialized cognitive task (questioning, modeling, reviewing) and hands results directly to the user or to implementation governed by AGENTS.md.

### 3.5 Plan Tracking Rules

When tracking multi-step work, an agent plan artifact or a dated plan file (`.plans/YYYY-MM-DD/[task-name].md`) serves as the execution SSOT:

- Work remains in `planned` state until explicit execution approval is granted.
- Check items only upon deterministic verification pass; record deviations under decisions and deviations.

### 3.6 Deployment Mirror Rules

`scripts/deploy_agents.py` mirrors repository content into `~/.agents` (overridable via `AGENT_HOME`):

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
