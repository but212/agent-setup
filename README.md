# agent-setup

[![skills.sh](https://img.shields.io/badge/skills.sh-agent--setup-black?logo=vercel&logoColor=white)](https://skills.sh/but212/agent-setup)

Operating rules and skill contracts for coding agents, in plain Markdown.

> For small workflows like air.

## When to Use

Skills are independent on-demand modalities, not a mandatory sequence:

- `/challenge`: Untested assumptions or ambiguous scope -> interview to confirm decisions.
- `/lean-design`: State machines, sum types, or schemas -> eliminate impossible states before coding.
- `AGENTS.md`: Standing constitution -> enforces TDD and blocks destructive actions on all tasks.
- `/lean-review`: Diff audits and pre-merge verification -> report defects backed by concrete counterexamples.
- `/crisp`: PRs, commit messages, or verbose documents -> compress text without semantic loss.

## What the repo checks

- **Contract-Driven**: Each skill declares its role, activation, and write authority in frontmatter.
- **Verification-First**: AGENTS.md tells agents to report unrun checks as Unverified. Tests check that this instruction exists.
- **Minimal Blast Radius**: AGENTS.md forbids destructive git commands and unrequested file changes. Tests check the guard wording.
- **CI**: CI runs the validator and tests on Ubuntu, macOS, and Windows.

## Layout and Contracts

- `AGENTS.md` - Core operating constitution defining precedence, safety guards, TDD, and handoff.
- `skills/*/SKILL.md` - Four modal contracts: `challenge` (inquiry), `crisp` (compression), `lean-design` (types/invariants), `lean-review` (adversarial audit).
- `spec/skills-spec.md` - Architecture specification and quality gates.
- `.plans/YYYY-MM-DD/` - Tracked execution plans grouped by creation date.
- `scripts/deploy_agents.py` - Copies AGENTS.md and skills into ~/.agents. Which tools read that directory is up to each tool.
- `scripts/validate-skills.py` - Dependency-free metadata, plan, and safety validator.
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

The validator checks skill frontmatter, dated plan paths, plan status values, AGENTS.md existence, and ASCII-only Markdown content in AGENTS.md and skills/. The test suite covers deployment, repository contracts, and safety guard wording.

## Status

The skill specification is currently `stable`. The spec's structural gates pass. This does not measure agent behavior.

---

Credits: `challenge` inspired by [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me), `lean-review` by [ponytail-review](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md), and `crisp` by [caveman](https://github.com/JuliusBrussee/caveman). See NOTICE.
