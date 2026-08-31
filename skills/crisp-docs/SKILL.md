---
name: crisp-docs
description: >
  Conservatively compress explicitly named general documents such as README.md,
  specifications, guides, release notes, issue text, and Markdown or plain-text
  prose. Use when the user asks to make documentation concise, remove bloat,
  improve clarity, or preserve meaning with fewer words. This skill edits prose,
  not code structure or agent rules.
disable-model-invocation: true
---

# Crisp Docs

Compress explicitly named documents without weakening their meaning, usability, or factual precision. `crisp` handles response prose and output style; `crisp-agent-docs` handles agent instruction contracts; this skill handles general documentation.

## Scope and defaults

- **Named targets only:** Process only documents explicitly named or unambiguously selected; do not rewrite a documentation tree by default.
- **Supported prose:** Markdown, plain text, and other human-readable documentation. Do not modify source code, configuration, generated files, lockfiles, or machine-readable data as prose.
- **In-place editing:** Edit targeted files in place unless the request is review, analysis, or no-edit.
- **Audience first:** Preserve audience, purpose, language, voice, and formality unless asked otherwise.
- **Structure preservation:** Keep headings, links, anchors, lists, tables, code blocks, frontmatter, identifiers, commands, paths, numbers, and machine-readable text intact. Change surrounding explanation only when safe.

## Reader-first form

Shape the document around the reader's task and reading path:

- Put the purpose, answer, decision, or required action near the beginning.
- Use focused prose for concepts, relationships, and qualifications; bullets for parallel reference content; numbered lists for procedures.
- Use headings for distinct questions or stages and tables only for comparable fields. Keep list items parallel and self-contained; do not fragment connected reasoning.
- Preserve a meaningful existing structure. Keep prerequisites before actions and expected results or failure paths near the relevant procedure.

Do not add structure merely for appearance. Match form to document type: explanatory prose for concepts, numbered steps for procedures, bullets or tables for reference material, and explicit prose or structured lists for policies and conditions.

## Compression rules

- Preserve facts, scope, dates, names, definitions, conditions, exceptions, warnings, examples, references, and next actions.
- Lead with the conclusion, decision, instruction, or key context the reader needs.
- Merge repeated ideas into one authoritative statement; remove filler, throat-clearing, and redundant rationale.
- Replace indirect or vague phrasing with short, concrete sentences and active voice.
- Keep necessary nuance. Do not turn qualified claims into absolute claims or omit uncertainty, prerequisites, trade-offs, or ownership.
- Prefer one clear term for each concept. Preserve established terminology and do not invent synonyms that could change meaning.
- Keep useful scanning structure. Split overloaded paragraphs, but do not create headings or lists merely to make the document look shorter.
- Do not remove content solely because it is uncommon; remove it only when it is redundant, obsolete, outside scope, or explicitly unwanted.

## Workflow

1. Read the complete target and its directly referenced documents when they are needed to interpret meaning.
2. Identify audience, purpose, required actions, factual anchors, dependencies, and format-sensitive content.
3. Separate binding information from repetition, filler, examples, and optional context.
4. Rewrite in place using the smallest safe reduction. Preserve code blocks and machine-readable content verbatim.
5. Compare the result with the original. Recheck every anchor, link, qualification, and action.
6. Report changed files, what was compressed, preserved uncertainties, and verification performed.

## Stop conditions

Stop and ask or report instead of rewriting when:

- the target or intended audience is ambiguous;
- referenced material is missing and the omission could alter meaning;
- the source contains conflicting requirements or facts;
- a requested reduction would remove necessary safety, legal, accessibility, technical, or operational detail;
- the file is generated, machine-readable, or otherwise outside this skill's scope.

## Controls

- **Scope:** Explicitly targeted general documents; no code or agent-rule edits.
- **Activate:** `/crisp-docs` or an explicit request to compress, simplify, or clarify a named document.
- **Deactivate:** After verification and the required report.

## Output

Use these headings in order: `Outcome`, `Scope`, `Changes`, `Verification`, `Next`. Keep the outcome and scope in short prose; use bullets for changed files, preserved anchors, verification results, and risks. Use a paragraph when several details form one explanation, and omit empty sections. For edits, report changed files and concise evidence of preserved meaning. For review-only requests, list prioritized reductions and risks without modifying files. If no safe reduction exists, leave the document unchanged and say why.
