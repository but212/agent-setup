# Agent Skills Integration Specification

[README](../README.md) | [Philosophy](PHILOSOPHY.md)

- Status: `stable`
- Purpose: Define repository agent skills architecture, operating boundaries, routing interactions, and validation contracts.

## 1. Scope and Core Architecture

### Included

- Skill selection and routing for interactive challenge, prose compression, structural design, and adversarial review.
- Core implementation, TDD verification, conflict resolution, and communication invariants governed by AGENTS.md.
- Plan tracking via agent plan artifacts or persistent plan files.
- Dependency-free validation of frontmatter, plan paths, agent prompt ASCII Markdown, document line budgets, and AGENTS.md existence.
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

- `name`: Matches directory name (`challenge`, `crisp`, `lean-design`, `lean-review`).
- `role`: One-line responsibility summary.
- `activation`: Triggers and command aliases.
- `modification-authority`: Permitted write scope (`None` for read-only skills, `Named files only` for `crisp`).
- `description`: Single-line overview of skill purpose.

Frontmatter syntax is strictly restricted to flat scalar mappings or inline JSON arrays (`["item1", "item2"]`). Multiline block scalars (`|`, `>`) and indented nested lists (`- item`) are unsupported and rejected during validation.

Frontmatter is validated by `scripts/validate-skills.py`.

## 3. Routing and Handoffs

### 3.1 Challenge Routing

`challenge` stress-tests plans and decisions in Grounded or Light mode. Mode selection, paths, and questioning rules: [skills/challenge/SKILL.md](../skills/challenge/SKILL.md).

### 3.2 Prose and Document Compression Routing

`crisp` compresses response prose and explicitly named Markdown or plain-text documents without altering operational contracts. Modes and workflow: [skills/crisp/SKILL.md](../skills/crisp/SKILL.md). Authority is limited to named target files (`modification-authority: Named files only`).

### 3.3 Structural Design Routing

`lean-design` models domain structures, state transitions, schemas, and boundaries before coding. Principles and handoff contract: [skills/lean-design/SKILL.md](../skills/lean-design/SKILL.md).

### 3.4 Adversarial Review Routing

`lean-review` performs read-only audits (`modification-authority: None`) on diffs or repositories, falsifying behavior with concrete counterexamples or deterministic static evidence. Workflow and output format: [skills/lean-review/SKILL.md](../skills/lean-review/SKILL.md), which is the SSOT for severity definitions (`[P1]`, `[P2]`, `[P3]`).

### 3.5 Direct Handoff

Skills do not require an intermediary router. Each skill completes its specialized cognitive task (questioning, compressing, modeling, reviewing) and hands results directly to the user or to implementation governed by AGENTS.md.

### 3.6 Plan Tracking Rules

When tracking multi-step work, an agent plan artifact or a persistent plan file serves as the execution SSOT:

- Work remains in `planned` state until explicit execution approval is granted.
- Check items only upon deterministic verification pass; record deviations under decisions and deviations.

### 3.7 Deployment Rules

`scripts/deploy_agents.py --tool <agents|claude|antigravity>` (default `agents`) copies repository content into one destination per run:

| Tool | Root | Deployed |
| --- | --- | --- |
| `agents` | `~/.agents` (overridable via positional target or `AGENT_HOME`) | `AGENTS.md`, `skills/` |
| `claude` | `~/.claude` | `skills/` only |
| `antigravity` | `~/.gemini/config` | `skills/` only |

- Skills-only tools never write `CLAUDE.md` or `GEMINI.md`; `AGENT_HOME` is ignored for them and a positional target is a usage error (exit 2).
- Destination is a copy target; repository is the source of truth.
- Repository-owned skill entries are replaced in full. Top-level entries of the destination `skills/` whose names are not in the repository are preserved. Skills removed or renamed in the repository are not cleaned up automatically.
- Destination path safety (preventing repository, home, or root overwrites) is validated before write.
- Atomic deployment invariant: deployment uses a mutual-exclusion lock (`.deploy.lock`) and a staging-then-swap pattern (`.skills.tmp`); failures preserve existing destination files without leaving intermediate or partial state. Scratch paths are fixed names removed on the next run. A hard crash can leave `.deploy.lock`; the error names the holder PID, and the file must be removed manually if no deployment is running.

## 4. Quality Gates

- [x] Every skill frontmatter defines valid `name`, `role`, `activation`, `modification-authority`, and `description`.
- [x] Agent prompt Markdown files (AGENTS.md, skills/) are strictly ASCII-only.
- [x] `python3 scripts/validate-skills.py` and `python3 -m unittest discover -s tests -v` pass (`python` on Windows).

## 5. Stabilization Policy

The specification is `stable` while all of the following hold; demote to `candidate` when any fails:

1. Every `skills/*/SKILL.md` contains verified frontmatter and self-contained contracts.
2. Operational boundaries, plan lifecycle, and atomic deployment guards are validated.
3. Repository-native validation and unit tests pass cleanly without errors or skips.
