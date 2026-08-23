---
name: crisp-commit
description: >
  Generates high-density, crisp Conventional Commit messages grounded in git diff evidence and recent git log language.
---

# Crisp Commit

Inspect Git diffs and generate factual, high-density Conventional Commit messages.

## Operating Contract

1. Lead directly with the formatted commit message block followed by a copyable `git commit` shell snippet.
2. Ground claims strictly in `git diff` evidence; eliminate speculative or unverified commentary.
3. Detect commit language via `git log -n 5`; default to English if `git log` is unavailable or inconclusive.

## Workflow

1. **Target Identification**: Inspect `git status --short`, explicit target/range, `git diff --staged`, `git diff`, and targeted untracked files without staging or modifying files. Report if no grounded diff exists.
2. **Context & Language**: Check `git log -n 5` for commit language. Filter out non-diff remarks.
3. **Analysis**: Inventory material structural changes vs. superficial formatting/imports.
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

- **Scope:** Read-only commit-message generation; never stage, commit, or modify files.
- **Activate:** `/crisp-commit` or an explicit request for a commit message.

## Output Format

```text
<type>(<scope>): <short summary in detected language>

- <material change 1 with exact symbol/file anchor>
- <material change 2 with key rationale or impact>
```

```bash
git commit -m "<type>(<scope>): <short summary>"
```

For a complex diff, include body bullets as separate `-m` flags:

```bash
git commit -m "<type>(<scope>): <short summary>" -m "<material change 1>" -m "<material change 2>"
```
