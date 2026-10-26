---
name: crisp
role: Compresses prose and explicitly named documents
activation: "`/crisp`, compression request"
modification-authority: Named files only
description: Compresses response prose and explicitly named Markdown or plain-text documents without altering meaning or operational contracts.
---

# Crisp

Optimize density while preserving full meaning. Delegate code structure to `lean-*`.

## Reader Assumption

- **Expert** (spec, API, codebase): drop standard definitions; retain exact identifiers and edge conditions.
- **Cold** (newcomer, outside team): retain essential term definitions and one-line context; cut repetition.
- **Agent** (`AGENTS.md`, `SKILL.md`): keep every imperative, condition, path, and command; cut rationale.
- **Unclear:** assume action-oriented reader; retain actionable content.

## Operating Modes

1. **Response prose (default):** compress chat output without file modifications.
2. **Document compression:** compress explicitly named Markdown/plain-text files in place without weakening contracts.

## Preservation Rules

Preserve anything whose omission alters correctness, safety, contracts, or next actions:

- Exact identifiers, terms, values, commands, paths, URLs, environment variables, error strings.
- Markdown syntax, structure, headings, links, code blocks, frontmatter.
- Security rules, precedence, destructive-command guards, user constraints.
- Direct quotations, verbatim requirements, contractual text.
- Do not modify already concise text; avoid synonym churn.

## 1. Response Prose Mode (Chat Output)

Lead directly with the answer/decision without preamble or process commentary.

- **Understand:** direct answer, then qualification.
- **Decide:** recommendation, then trade-offs.
- **Act:** prerequisites, ordered sequence, expected outcome/failure path.
- **Review:** outcome, evidence, blockers, next action.
- Paragraphs for connected ideas, bullets for parallel items, numbers strictly for sequences.

## 2. Document Compression Mode (In-place File Edits)

### Workflow

1. **Inventory anchors:** note mandatory terms, paths, commands, and constraints.
2. **Prune bloat:** remove throat-clearing, redundant rationale, and duplicate concepts.
3. **Preserve nuance:** maintain boundary conditions and exceptions.
4. **Verify diff:** check anchors, links, and code blocks against original.
5. **Report headings (exact order):** `Outcome`, `Scope`, `Analysis`, `Verification`, `Next`.
