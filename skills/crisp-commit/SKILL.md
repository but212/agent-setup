---
name: crisp-commit
description: >
  Generates high-density, crisp Conventional Commit messages grounded in git diff evidence and recent git log language.
---

# Crisp Commit

Generate factual, high-density Conventional Commit messages from Git diffs.

## Operating Contract

1. Lead directly with the formatted commit message block followed by a copyable `git commit` shell snippet.
2. Ground claims strictly in `git diff` evidence; eliminate speculative or unverified commentary.
3. Detect commit language via `git log -n 5`; default to English if `git log` is unavailable or inconclusive.

## Workflow

1. **Target:** Inspect `git status --short`, explicit target/range, `git diff --staged`, `git diff`, and targeted untracked files without staging or modifying files. Report if no grounded diff exists.
2. **Context:** Check `git log -n 5` for commit language; default to English when unavailable or inconclusive, and filter non-diff remarks.
3. **Analysis:** Separate material structural changes from superficial formatting/imports.
4. **Format Selection**:
   - **Simple diff**: Single-line subject (`<type>(<scope>): <summary>`).
   - **Complex diff**: Subject line + bulleted body with exact symbol/file anchors.
   - **Commit command**: Pass additional `-m` arguments for complex body bullets; use one `-m` for simple subject.

## Conventional Commit Types

- `feat`: New feature or capability.
- `fix`: Bug fix or error resolution.
- `refactor`: Code reorganization without behavioral change.
- `style`: Formatting, whitespace, or lint-only fixes.
- `docs`: Documentation or comment updates.
- `test`: Test additions or updates.
- `chore`: Tooling, build, dependency, or agent skill/rule updates.

## Controls

- **Scope:** Read-only; never stage, commit, or modify files.
- **Activate:** `/crisp-commit` or an explicit commit-message request.

## Reader-first form

Optimize for someone scanning history later:

- Make the subject a self-contained summary of the observable change; do not make the reader infer it from the body.
- For a simple diff, use the subject alone. For a complex diff, add a body paragraph only for shared context or qualification, then use parallel bullets for independent material changes.
- Keep bullets concrete, limited to material changes, and anchored to files or symbols when useful for verification. Number only ordered changes.
- Describe unrelated changes separately instead of inventing a unifying rationale; omit cosmetic details and speculation.
- Do not add a preamble outside the commit message and command. Omit empty body sections and keep the command consistent with the displayed message.

## Output Format

For a simple diff, output only the subject:

```text
<type>(<scope>): <short summary in detected language>
```

For a complex diff, use the subject, an optional shared-context paragraph, and material-change bullets:

```text
<type>(<scope>): <short summary in detected language>

<optional shared context or qualification>

- <material change 1 with exact symbol/file anchor>
- <material change 2 with key rationale or impact>
```

Follow the displayed message with a copyable command. For a simple diff:

```bash
git commit -m "<type>(<scope>): <short summary>"
```

For a complex diff, pass the paragraph and each bullet as separate `-m` arguments, omitting the paragraph argument when it is absent:

```bash
git commit -m "<type>(<scope>): <short summary>" -m "<optional shared context>" -m "<material change 1>" -m "<material change 2>"
```
