---
name: git-conflict
role: Resolves Git integration conflicts while preserving contracts and unrelated work
activation: Explicit Git conflict or non-fast-forward integration task
modification-authority: Approved integration scope
description: Resolve Git pull, merge, rebase, cherry-pick, and push integration conflicts by preserving behavior, schema contracts, tests, and unrelated work.
---

# Git Conflict Resolution

Resolve conflicts, non-fast-forward states, or history mismatches from `git pull`, merge, rebase, cherry-pick, or push with the smallest correct semantic change.

## Operating contract

- Preserve unrelated working-tree changes and protected data.
- Never use `git reset --hard`, `git clean`, force-push, or automatic `ours`/`theirs` checkouts.
- Do not stash, commit, or push unless the user explicitly requests that operation.
- Read both versions of every conflicted file, schemas, specifications, callers, and tests before editing.
- Ground resolutions on existing code, documented invariants, and tests; state assumptions explicitly.

## Workflow

### 1. Establish repository state

Inspect state before changing files:

```bash
git status --short --branch
git rev-parse -q --verify MERGE_HEAD
git rev-parse -q --verify REBASE_HEAD
git rev-parse -q --verify CHERRY_PICK_HEAD
git log --oneline --decorate --graph -12
```

Preserve unrelated worktree changes. For remote integration, fetch the target remote and compare histories:

```bash
git fetch <remote>
git log --oneline --left-right HEAD...<remote>/<branch>
```

Resolve `<remote>` and `<branch>` from user input or upstream config; do not assume `origin`. Identify merge, rebase, or cherry-pick state before proceeding; do not loop `git pull` without evidence.

### 2. Inventory conflicts and contracts

List unmerged paths and inspect diffs:

```bash
git diff --name-only --diff-filter=U
git diff --cc
git diff --check
```

Inspect `HEAD`, incoming, and working versions against project `AGENTS.md`, schemas, migrations, callers, and tests. Classify each conflict by contract/intent and identify owning requirements before editing.

### 3. Resolve by responsibility

- Remove conflict markers while retaining compatible behavior; prefer semantic integration over picking one side.
- Preserve stronger validation, authorization, tenant scoping, locking, retries, accessibility, and error handling.
- Do not reintroduce deleted fields, reference absent columns, or drop tests without evidence.
- For migration conflicts, inspect actual schema state; never edit already-applied migrations.
- Catch only intended failure classes; rethrow unrelated exceptions.
- Update specifications and tests if resolved behavior changes.

### 4. Validate before completing integration

Verify marker removal and cleanliness:

```bash
rg -n '^(<<<<<<< |>>>>>>> |\|\|\|\|\|\|\| )' --glob '!vendor/**' .
git diff --check
git status --short
```

Marker search and unmerged status must be empty. (Separator markers are evaluated in context to permit Markdown underlines).

Run narrowest affected tests, repository checks, and diagnostics on edited source files. Do not edit vendored files or discard diagnostics without evidence.

Inspect the diff for accidental files, secrets, debug output, and formatting churn. After staging, verify:

```bash
git diff --cached --check
git diff --cached --name-only --diff-filter=U
```

### 5. Finish safely

- If conflict resolution only was requested: stop with resolved files, validation evidence, and remaining actions.
- If completion was explicitly requested: stage resolved paths, create the commit, and verify history.
- Fetch before pushing if the remote changed; never force-push without explicit authorization and history review.
- Report commit hash, push results, test/diagnostic evidence, assumptions, and blockers.

## Conflict report format

```text
State: merge | rebase | cherry-pick | non-fast-forward push
History: local/base/incoming commits
Resolved paths: exact list
Contract decisions: one line per semantic conflict
Validation: marker search / diff check / focused tests / full checks / diagnostics
Integration: commit hash and push result, or explicit remaining action
Blockers: none or exact blocker
```

## Controls

- **Scope:** Git integration state and minimum files needed to resolve it.
- **Activate:** Explicit Git conflict or non-fast-forward integration task.
- **Deactivate:** Concluded when verified; avoid unrelated cleanup.
