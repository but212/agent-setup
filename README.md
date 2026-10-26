# agent-setup

Deterministic, framework-agnostic operating baseline and safety contracts for coding agents.

## Overview

`agent-setup` establishes an operating baseline for coding agents across different frameworks and models. It replaces open-ended prompts with explicit operational invariants, verifiable boundaries, and deterministic safety checks.

## Key Properties

- **Contract-Driven**: Explicit inputs, outputs, and modification boundaries instead of roleplay or heuristic instructions.
- **Verification-First**: Hard separation between executed verification and deductive inference. Unrun checks are never reported as passed.
- **Minimal Blast Radius**: Rejection of destructive operations (`git push`, `git reset --hard`, `git clean -f`, `rm -rf`) and unrequested changes to lockfiles, schemas, or migrations.
- **Deterministic CI**: Validated frontmatter, plan schemas, and safety assertions tested across Ubuntu, macOS, and Windows runners.

## Architecture

- **`AGENTS.md`**: Core repository constitution defining instruction precedence, safety guards, Baseline First / Constraint Projection, TDD, and Git handoff.
- **`skills/`**: Four cohesive modal contracts:
  - `challenge`: Focused inquiry resolving assumptions before implementation.
  - `crisp`: Lossless compression of prose, commit messages, and explicitly named documents.
  - `lean-design`: Minimal algebraic data modeling that makes invalid states unrepresentable.
  - `lean-review`: Skeptical adversarial review categorizing findings (`[P1]`, `[P2]`, `[P3]`) supported by constructible counterexamples.
- **`scripts/deploy_agents.py`**: Idempotent mirror harness synchronizing configurations to `~/.agents` with symlink and traversal protections.
- **`scripts/validate-skills.py`**: Dependency-free validation of frontmatter metadata, ASCII-only constraints, dated plan paths, and destructive guard clauses.

## Inspirations

- `challenge`: Inspired by [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me).
- `lean-review`: Inspired by [ponytail-review](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md).
- `crisp`: Compression principles inspired by [caveman](https://github.com/JuliusBrussee/caveman).

See NOTICE for third-party license notices.

## Repository Layout

- `AGENTS.md` - Repository-wide agent rules and safety invariants.
- `skills/*/SKILL.md` - Modal skill contracts.
- `spec/skills-spec.md` - Architecture specification and quality gates.
- `.plans/YYYY-MM-DD/` - Tracked execution plans grouped by creation date.
- `scripts/validate-skills.py` - Metadata, plan, and safety validator.
- `scripts/deploy_agents.py` - Mirror deployment engine.
- `.github/workflows/ci.yml` - Multi-OS GitHub Actions workflow.

## Usage

1. Copy or mirror the repository into target workspaces or global agent directories.
2. Mirror configuration into `~/.agents`:

   ```sh
   python3 scripts/deploy_agents.py
   ```

   Set `AGENT_HOME` to override the destination directory.

3. Track multi-step tasks via an agent plan artifact or a dated plan file in `.plans/YYYY-MM-DD/[task-name].md`.

## Verification

Run repository checks from the root:

```sh
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests -v
```

The validator checks skill frontmatter, dated plan paths, plan status values, destructive-command guards, and ASCII-only Markdown content. The test suite covers deployment and repository contracts.

## Status

The skill specification is currently `stable`. Promotion criteria defined in `spec/skills-spec.md` are verified and recorded.
