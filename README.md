# agent-setup

A framework- and language-agnostic operating baseline for coding agents.

## What it provides

- Skill contracts for challenge, design, implementation, testing, review, UI work, planning, and specification.
- Explicit routing, handoffs, modification authority, and approval boundaries.
- Evidence-first, minimal-change, deterministic-verification guidance.
- Safety rules for preserving user work and refusing destructive commands unless explicitly requested.

## Layout

- `AGENTS.md` — repository-wide agent rules.
- `skills/*/SKILL.md` — individual skill contracts.
- `spec/skills-spec.md` — catalog, routing, shared invariants, and stabilization policy.
- `.plans/` — optional file-backed execution plans when planning mode is active.
- `scripts/validate-skills.py` — dependency-free catalog and safety validation.

## Use

Place or copy the relevant files into an agent-enabled repository, then adapt only repository-specific commands and boundaries. Do not add framework-specific assumptions to the core contracts.

Agents should inspect the target repository's own configuration, scripts, CI definitions, and documentation before running checks. Explicit approval is required before implementation when a plan or contract-sensitive workflow is active.

## Validate this setup

Run the repository's validation script from the root:

```sh
python3 scripts/validate-skills.py
```

The script checks skill frontmatter, catalog parity, routing/authority markers, and destructive-command guards. It does not validate product behavior or ecosystem-specific workflows.

## Status

The skill specification is currently `candidate`. Promotion criteria are defined in `spec/skills-spec.md`; candidate status should remain until those gates are verified and recorded.
