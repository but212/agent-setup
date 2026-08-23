---
name: crisp-agent-docs
description: >
  Conservatively compress explicitly named agent instruction documents such as
  AGENTS.md, CLAUDE.md, GEMINI.md, SKILL.md, and similar Markdown files. Use
  when the user asks to make agent rules crisp, remove instruction bloat, merge
  duplicated guidance, or improve instruction context efficiency while
  preserving operational meaning. This is document compression, not code or
  repository complexity reduction.
disable-model-invocation: true
---

# Crisp Agent Docs

Compress explicitly named agent instruction documents without weakening operational contracts. `crisp` handles prose/output style; `lean-*` handles code and repository complexity; this skill handles document structure.

## Operating contract

Report using this skill's own format: `Outcome → Scope → Analysis → Verification → Next`. Report-only requests use the same structure without editing files.

## Scope and defaults

- **Named targets only:** Process only explicitly named Markdown guidance files (`SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, workflows, rules). Report non-Markdown files as unsupported; do not auto-discover.
- **In-place editing:** Edit files in place by default. Return report/proposed patch without editing if analysis, review, or no-edit mode is requested.
- **Preservation:** Keep Markdown structure, links, code blocks, tables, identifiers, commands, paths, numbers, frontmatter, metadata, and machine-readable text intact. Preserve ordering inside code blocks, tables, and other machine-readable content; reorder ordinary prose only when it improves rule priority without changing meaning. If unsure whether text carries operational meaning, keep it and report uncertainty.
- **No extra assets:** Do not add dependencies, scripts, generated files, or auxiliary documents.

## Workflow

1. **Ground the source:** Read full file and referenced rules. Inventory operational anchors (mandatory words, conditions, exceptions, safety rules, validation commands, paths, identifiers, precedence). Separate binding rules from rationale and repetition. Stop and report if rules conflict or referenced rules are missing.
2. **Reduce variance:** Order: preserve anchors → merge duplicates → remove dead context → move high-priority rules earlier. Maintain one authoritative statement per rule using direct imperative phrasing.
3. **Preserve correctness:** Never remove or weaken security, data-loss prevention, validation, error handling, accessibility, package-manager, migration, or explicit user rules. Preserve exceptions, conditions, precedence, and unique clarifying examples. Do not alter code blocks or machine-readable content.
4. **Improve context efficiency:** Remove dead context for inactive branches, eliminate duplicate concepts, and place high-impact constraints first. Never hide required detail in vague summaries.
5. **Verify before reporting:** Compare edited files using `git diff` (or local tools). Recheck all inventory items. If no safe reduction exists, leave the file unchanged and report result.

## Controls

- **Scope:** Explicitly named Markdown guidance files only; edit in place unless review-only is requested.
- **Activate:** An explicit request to compress or audit a named agent instruction document.
- **Deactivate:** After verification and the required report.

## Output

Lead with the result (`Outcome → Scope → Analysis → Verification → Next`). For edits, report changed files (or no change), reductions, preserved constraints, validation, and uncertainties. For report-only mode, list prioritized candidates with proposed reductions and risks.
