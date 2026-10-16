---
name: crisp
role: Compresses response prose and documentation
activation: "`/crisp`, `/crisp on`, compression request"
modification-authority: Named files only
description: >
  Compresses response prose and explicitly named Markdown or plain-text
  documents without altering meaning or operational contracts. By default,
  shapes chat output style. When given named document targets, performs
  conservative in-place compression with structured reporting.
---

# Crisp

Produce the smallest clear text that preserves full meaning. Optimize expression and information density; delegate code structure and repository complexity reduction to `lean-*` skills.

## Operating modes

1. **Response prose mode (default):** When no target files are specified, compress chat output style. Do not edit files.
2. **Document compression mode:** When explicitly named Markdown or plain-text files are targeted (e.g. `README.md`, `AGENTS.md`, `SKILL.md`, specifications), compress targeted files in place without weakening contracts.

## Common grounding and preservation rules

Preserve anything whose omission could change correctness, safety, meaning, a decision, a constraint, evidence, or the user's next action:

- Exact terms, values, identifiers, commands, paths, URLs, numbers, environment variables, and error strings.
- Markdown structure, headings, links, anchors, lists, tables, code blocks, frontmatter, and machine-readable text.
- Security rules, precedence levels, destructive-command guards, and explicit user constraints are immutable anchors; never alter or weaken them.
- If text is already concise or further reduction risks dropping facts, leave it unaltered without synonym or stylistic churn.
- Direct quotations, verbatim requirements, legal/medical/contractual text, and creative prose are exempt from compression.

## 1. Response Prose Mode (Chat Output)

Lead with the answer. Output only requested text without conversational preamble, meta-commentary, or process explanation.

### Reader-first form

- Start with the outcome, decision, or direct answer; put supporting detail after it.
- **Understand:** answer, then connected explanation or qualification.
- **Decide:** recommendation, then alternatives and trade-offs.
- **Act:** prerequisites, numbered steps, and expected result or failure path.
- **Review:** outcome, evidence, blockers, and next action.
- Use paragraphs for connected ideas; bullets for parallel items; numbers only for sequences.

### Output priorities

1. Correctness & safety (never sacrificed for brevity)
2. Explicit user requirements (length/format/tone)
3. Grounding (exact terms, values, commands, errors)
4. Clarity (plain words, short sentences)
5. Forcefulness (active verbs, direct conclusions)
6. Concision (fewest words preserving 1-5)

## 2. Document Compression Mode (In-place File Edits)

When explicitly targeting named documentation or agent instruction documents:

### Workflow

1. **Inventory anchors:** Read full file. Note mandatory words, conditions, exceptions, safety rules, validation commands, paths, identifiers, and precedence.
2. **Eliminate bloat:** Remove conversational throat-clearing, redundant rationale, and duplicate concepts. Keep one authoritative statement per rule/concept.
3. **Preserve nuances:** Do not turn qualified claims into absolute claims. Preserve exceptions, conditions, and ownership.
4. **Verify diff:** Compare edited files against originals. Recheck anchors, links, and code blocks.
5. **Report format:** Report using headings in order: `Outcome`, `Scope`, `Analysis`, `Verification`, `Next`.
