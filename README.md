# agent-setup

Deterministic, framework-agnostic operating baseline and safety contracts for coding agents.

> For small workflows like air.

## When to Use

Skills are independent on-demand modalities, not a mandatory sequence:

- `/challenge`: Untested assumptions or ambiguous scope -> interview to confirm decisions.
- `/lean-design`: State machines, sum types, or schemas -> eliminate impossible states before coding.
- `AGENTS.md`: Standing constitution -> enforces TDD and blocks destructive actions on all tasks.
- `/lean-review`: Diff audits and pre-merge verification -> report defects backed by concrete counterexamples.
- `/crisp`: PRs, commit messages, or verbose documents -> compress text without semantic loss.

## Core Properties

- **Contract-Driven**: Explicit inputs, outputs, and modification boundaries over roleplay or prose heuristics.
- **Verification-First**: Hard separation of executed verification from deduction; unrun checks are never reported as passed.
- **Minimal Blast Radius**: Rejection of destructive git actions (`git push`, `git reset --hard`, `git clean -f`, `rm -rf`) and unrequested file drift.
- **Deterministic CI**: Multi-OS validation (Ubuntu, macOS, Windows) verifying schemas, plans, and safety invariants.

## Layout and Contracts

- `AGENTS.md` - Core operating constitution defining precedence, safety guards, TDD, and handoff.
- `skills/*/SKILL.md` - Four modal contracts: `challenge` (inquiry), `crisp` (compression), `lean-design` (types/invariants), `lean-review` (adversarial audit).
- `spec/skills-spec.md` - Architecture specification and quality gates.
- `.plans/YYYY-MM-DD/` - Tracked execution plans grouped by creation date.
- `scripts/deploy_agents.py` - Idempotent mirror harness for `~/.agents` (compatible with Antigravity, Gemini, and Claude Code).
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

The validator checks skill frontmatter, dated plan paths, plan status values, destructive-command guards, and ASCII-only Markdown content. The test suite covers deployment and repository contracts.

## Status

The skill specification is currently `stable`. Promotion criteria defined in `spec/skills-spec.md` are verified and recorded.

---

Credits: `challenge` inspired by [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me), `lean-review` by [ponytail-review](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md), and `crisp` by [caveman](https://github.com/JuliusBrussee/caveman). See NOTICE.
