# agent-setup

Framework- and language-agnostic operating baseline for coding agents.

## What it provides

- Framework-neutral skill contracts for challenge, design, implementation, testing, review, and specification.
- Explicit routing, handoffs, modification authority, approval boundaries, and deterministic verification.
- Minimal-change and safety guidance refusing destructive commands unless explicitly requested.
- ASCII-only Markdown content for direct entry on a standard US QWERTY keyboard.

## Design principles

Contracts define input/output interfaces and communication protocols rather than prose:

- **Interfaces, not spells:** Explicit inputs and authoritative outputs over keywords or role-play.
- **Decomposition:** Cohesive skills (`challenge`, `crisp`, `lean-*`, `spec-drive`, `git-conflict`) with explicit handoffs and authority boundaries.
- **Evaluation over format:** Success criteria and edge cases verified via deterministic checks.
- **Iterative refinement:** Minimal base contracts, adding constraints only when verification demands them.

## Inspirations

- `lean-*` - inspired by [ponytail](https://github.com/DietrichGebert/ponytail).
- `crisp` - inspired by [caveman](https://github.com/JuliusBrussee/caveman).
- `challenge` - inspired by [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me).

See NOTICE for third-party license notices.

## Layout

- `AGENTS.md` - repository-wide agent rules.
- `skills/*/SKILL.md` - individual skill contracts.
- `spec/skills-spec.md` - routing, architecture, and quality gates.
- `.plans/YYYY-MM-DD/` - tracked file-backed execution plans grouped by creation date.
- `scripts/validate-skills.py` - dependency-free frontmatter, plan path, and safety validation.
- `scripts/deploy_agents.py` - mirror `AGENTS.md` and `skills/` into `~/.agents` (`--link` symlinks global instructions).

## Use

Copy relevant files into the target repository. Adapt repository-specific commands and boundaries without adding framework-specific assumptions. Inspect repository configuration, scripts, CI definitions, and documentation before running checks. Obtain explicit approval before implementation when planning or contract-sensitive workflows are active.

Deploy with `python3 scripts/deploy_agents.py [--link]`. Set `AGENT_HOME` to override the deployment target.

## Validate this setup

Run repository checks from the root:

```sh
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests -v
```

The validator checks skill frontmatter, dated plan paths, plan status values and documented transitions, destructive-command guards, and ASCII-only Markdown content. The test suite covers deployment and repository contracts.

## Status

The skill specification is currently `stable`. Promotion criteria defined in `spec/skills-spec.md` are verified and recorded.
