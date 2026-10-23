# agent-setup

A framework- and language-agnostic operating baseline for coding agents.

## What it provides

- Framework-neutral skill contracts for challenge, design, implementation, testing, review, and specification.
- Explicit routing, handoffs, modification authority, approval boundaries, and evidence-first deterministic verification.
- Minimal-change and safety guidance for preserving user work and refusing destructive commands unless explicitly requested.
- ASCII-only Markdown content for direct entry on a standard US QWERTY keyboard.

## Design principles

The contracts define prompt engineering as input/output interfaces and a communication protocol, not polished prose:

- **Interfaces, not spells:** Define explicit inputs and authoritative outputs; do not rely on magic keywords or role-play.
- **Decomposition:** Split complex workflows into cohesive skills (`challenge`, `lean-*`, `spec-drive`) with explicit handoffs and separate authority.
- **Evaluation over format:** State success criteria and edge-case handling; verify with deterministic, repository-native checks.
- **Iterative refinement:** Start with the simplest contract and add constraints only when verification exposes a need.

## Inspirations

- `lean-*` - inspired by [ponytail](https://github.com/DietrichGebert/ponytail).
- `crisp*` - inspired by [caveman](https://github.com/JuliusBrussee/caveman).
- `challenge*` - inspired by [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me).

See NOTICE for third-party license notices.

## Layout

- `AGENTS.md` - repository-wide agent rules.
- `skills/*/SKILL.md` - individual skill contracts.
- `spec/skills-spec.md` - routing, architecture, and quality gates.
- `.plans/YYYY-MM-DD/` - tracked file-backed execution plans grouped by creation date.
- `scripts/validate-skills.py` - dependency-free frontmatter, plan path, and safety validation.
- `scripts/deploy_agents.py` - mirror `AGENTS.md` and `skills/` into `~/.agents` (the shared agent folder); `--link` also symlinks pi's global instructions to it.

## Use

Place or copy the relevant files into an agent-enabled repository. Adapt only repository-specific commands and boundaries; do not add framework-specific assumptions to the core contracts. Before running checks, inspect the target repository's configuration, scripts, CI definitions, and documentation. Get explicit approval before implementation when a plan or contract-sensitive workflow is active.

Deploy with `python3 scripts/deploy_agents.py [--link]`. Set `AGENT_HOME` to override the deployment target.

## Validate this setup

Run the repository checks from the root:

```sh
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests -v
```

The validator checks skill frontmatter, dated plan paths, destructive-command guards, and ASCII-only Markdown content. The test suite covers deployment and repository contracts. These checks do not validate product behavior or ecosystem-specific workflows.

## Status

The skill specification is currently `stable`. Promotion criteria defined in `spec/skills-spec.md` are verified and recorded.
