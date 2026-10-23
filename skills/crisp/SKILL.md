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

Produce the smallest clear text that keeps full meaning. Optimize expression and information density. Leave code structure and repository complexity to `lean-*` skills.

## Reader assumption

Before compressing, name the reader in one line: who reads, what they know, what they must do or decide. Let that decide what stays:

- **Expert** (spec, API, codebase): drop definitions of standard terms; keep exact identifiers and edge conditions.
- **Cold** (newcomer, outside team): keep term definitions and one line of context; cut repetition only.
- **Agent** (`AGENTS.md`, `SKILL.md`): keep every imperative, condition, path, and command; cut rationale the agent does not act on.
- **Unclear:** assume the reader who acts on the text; keep what that reader needs to act.

## Operating modes

1. **Response prose (default):** no target files. Compress chat output. Edit no files.
2. **Document compression:** explicitly named Markdown or plain-text files (e.g. `README.md`, `AGENTS.md`, `SKILL.md`, specs). Compress in place without weakening contracts.

## Common grounding and preservation rules

Preserve anything whose omission could change correctness, safety, meaning, a decision, a constraint, evidence, or the next action:

- Exact terms, values, identifiers, commands, paths, URLs, numbers, environment variables, error strings.
- Markdown structure, headings, links, anchors, lists, tables, code blocks, frontmatter, machine-readable text.
- Security rules, precedence levels, destructive-command guards, explicit user constraints: immutable. Never alter or weaken them.
- Already concise, or further reduction would drop facts: leave unaltered. No synonym churn.
- Exempt from compression: direct quotations, verbatim requirements, legal, medical, and contractual text, creative prose.

## 1. Response Prose Mode (Chat Output)

Lead with the answer. Output only the requested text: no preamble, meta-commentary, or process explanation.

### Reader-first form

- Open with the outcome, decision, or direct answer; supporting detail follows.
- **Understand:** answer, then connected explanation or qualification.
- **Decide:** recommendation, then alternatives and trade-offs.
- **Act:** prerequisites, numbered steps, expected result or failure path.
- **Review:** outcome, evidence, blockers, next action.
- Paragraphs for connected ideas; bullets for parallel items; numbers only for sequences.

### Output priorities

1. Correctness and safety (never sacrificed for brevity)
2. Explicit user requirements (length, format, tone)
3. Grounding (exact terms, values, commands, errors)
4. Clarity (plain words, short sentences)
5. Forcefulness (active verbs, direct conclusions)
6. Concision (fewest words that keep 1-5)

## 2. Document Compression Mode (In-place File Edits)

For explicitly named documentation or agent instruction files.

### Workflow

1. **Inventory anchors:** read the full file. Note mandatory words, conditions, exceptions, safety rules, validation commands, paths, identifiers, precedence.
2. **Cut bloat:** remove throat-clearing, redundant rationale, duplicate concepts. Keep one authoritative statement per rule.
3. **Keep nuance:** never turn a qualified claim into an absolute one. Keep exceptions, conditions, ownership.
4. **Verify diff:** compare against the original. Recheck anchors, links, code blocks.
5. **Report headings, in order:** `Outcome`, `Scope`, `Analysis`, `Verification`, `Next`.
