# agent-setup

A framework- and language-agnostic operating baseline for coding agents.

## What it provides

- Skill contracts for challenge, design, implementation, testing, review, planning, SQL/ORM auditing, and specification.
- Explicit routing, handoffs, modification authority, and approval boundaries.
- Evidence-first, minimal-change, deterministic-verification guidance.
- Safety rules for preserving user work and refusing destructive commands unless explicitly requested.

## Design principles

The skill contracts treat prompt engineering as input/output interface design and a communication protocol between the model and the task, not as writing polished sentences:

- **Interfaces, not spells:** Each skill defines explicit inputs (operating contracts) and expected outputs (authoritative formats), not magic keywords or persona role-play.
- **Decomposition:** Complex workflows are split into routed skills (`challenge`, `lean-*`, `tdd-plan`, `spec-drive`) with explicit handoffs and separated modification authority, instead of one monolithic prompt.
- **Evaluation criteria:** Skills state the logical criteria good output must satisfy and how edge cases are handled, verified through repository-native checks.
- **Iterative refinement:** Work starts from the simplest contract (TDD slices, `planned` plan states) and gains constraints only where verification fails.

## Inspirations

- `lean-*` — inspired by [ponytail](https://github.com/DietrichGebert/ponytail).
- `crisp*` — inspired by [caveman](https://github.com/JuliusBrussee/caveman).
- `challenge*` — inspired by [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me).

See NOTICE for third-party license notices.

## Layout

- `AGENTS.md` — repository-wide agent rules.
- `skills/*/SKILL.md` — individual skill contracts.
- `spec/skills-spec.md` — catalog, routing, shared invariants, and stabilization policy.
- `.plans/YYYY-MM-DD/` — tracked file-backed execution plans grouped by creation date.
- `scripts/validate-skills.py` — dependency-free catalog and safety validation.
- `scripts/deploy-agents.sh` — mirrors `AGENTS.md` and `skills/` into `~/.agents` (the shared agent folder); `--link` also symlinks pi's global instructions to it.

## Use

Place or copy the relevant files into an agent-enabled repository, then adapt only repository-specific commands and boundaries. Do not add framework-specific assumptions to the core contracts.

Agents should inspect the target repository's own configuration, scripts, CI definitions, and documentation before running checks. Explicit approval is required before implementation when a plan or contract-sensitive workflow is active.

## Validate this setup

Run the repository's validation script from the root:

```sh
python3 scripts/validate-skills.py
```

The script checks skill frontmatter, catalog rows, routing/authority markers, dated plan paths, and destructive-command guards. It does not validate product behavior or ecosystem-specific workflows.

## Status

The skill specification is currently `candidate`. Promotion criteria are defined in `spec/skills-spec.md`; candidate status should remain until those gates are verified and recorded.
