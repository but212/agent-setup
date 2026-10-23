---
name: crisp
role: Compresses prose and explicitly named documents
activation: "`/crisp`, compression request"
modification-authority: Named files only
description: >
  Compresses response prose and explicitly named Markdown or plain-text
  documents without altering meaning or operational contracts.
---

# Crisp

Produce the smallest clear text preserving full meaning. Optimize density; leave code structure to `lean-*` skills.

## Reader assumption

Name the reader in one line (identity, context, required action/decision) to guide pruning:

- **Expert** (spec, API, codebase): drop standard definitions; keep exact identifiers and edge conditions.
- **Cold** (newcomer, outside team): retain essential term definitions and one line of context; cut repetition.
- **Agent** (`AGENTS.md`, `SKILL.md`): keep every imperative, condition, path, and command; cut unacted rationale.
- **Unclear:** assume the reader acting on the text; keep actionable content.

## Operating modes

1. **Response prose (default):** compress chat output without editing files.
2. **Document compression:** compress explicitly named Markdown or plain-text files in place without weakening contracts.

## Common grounding and preservation rules

Preserve anything whose omission alters correctness, safety, meaning, decisions, constraints, evidence, or next actions:

- Exact terms, values, identifiers, commands, paths, URLs, numbers, environment variables, error strings.
- Markdown structure, headings, links, anchors, lists, tables, code blocks, frontmatter, machine-readable text.
- Security rules, precedence levels, destructive-command guards, explicit user constraints: immutable.
- Leave already concise text unaltered; avoid synonym churn.
- Exempt: direct quotations, verbatim requirements, legal/contractual text, creative prose.

## 1. Response Prose Mode (Chat Output)

Lead with the answer. Output only requested text without preamble, process commentary, or meta-filler.

### Reader-first form

- Open with the outcome, decision, or direct answer, followed by supporting detail.
- **Understand:** answer, then connected explanation or qualification.
- **Decide:** recommendation, then alternatives and trade-offs.
- **Act:** prerequisites, numbered steps, expected outcome or failure path.
- **Review:** outcome, evidence, blockers, next action.
- Paragraphs for connected ideas; bullets for parallel items; numbers strictly for sequences.

### Output priorities

1. Correctness and safety
2. Explicit user requirements (format, tone, length)
3. Grounding (exact terms, values, commands, errors)
4. Clarity and forcefulness (short sentences, active verbs)
5. Concision (fewest words satisfying 1-4)

## 2. Document Compression Mode (In-place File Edits)

### Workflow

1. **Inventory anchors:** identify mandatory terms, conditions, exceptions, safety rules, commands, paths, identifiers, and precedence.
2. **Cut bloat:** remove throat-clearing, redundant rationale, and duplicate concepts; keep one authoritative rule statement.
3. **Keep nuance:** preserve exceptions, conditions, and ownership boundaries.
4. **Verify diff:** compare against original text; recheck anchors, links, and code blocks.
5. **Report headings, in order:** `Outcome`, `Scope`, `Analysis`, `Verification`, `Next`.
