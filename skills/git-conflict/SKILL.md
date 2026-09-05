---
name: git-conflict
description: Resolve Git pull, merge, rebase, cherry-pick, and push integration conflicts by preserving behavior, schema contracts, tests, and unrelated work.
---

# Git Conflict Resolution

Apply when `git pull`, merge, rebase, cherry-pick, or push reports a conflict, non-fast-forward state, or an integration failure that requires comparing local and remote history. Resolve the smallest correct change; do not treat conflict resolution as a text-only operation.

## Operating contract

- Preserve unrelated working-tree changes and protected data.
- Never use `git reset --hard`, `git clean`, force-push, or broad `ours`/`theirs` checkout as an automatic recovery.
- Do not stash, commit, or push unless the user explicitly requests that operation or the approved task necessarily requires completing the integration.
- Read both versions of every conflicted file and the relevant schema, specification, callers, and tests before editing.
- Treat the current code, documented invariants, and executable tests as evidence; state unresolved assumptions instead of silently choosing a public-contract change.

## Workflow

### 1. Establish repository state

Run bounded, read-only inspection before changing files:

```bash
git status --short --branch
git rev-parse -q --verify MERGE_HEAD || true
git rev-parse -q --verify REBASE_HEAD || true
git rev-parse -q --verify CHERRY_PICK_HEAD || true
git log --oneline --decorate --graph -12
```

If the worktree contains unrelated changes, preserve them and confirm their paths before editing. For a remote integration, fetch only the requested remote and compare histories explicitly:

```bash
git fetch <remote>
git log --oneline --left-right HEAD...<remote>/<branch>
```

Resolve `<remote>` and `<branch>` from the user's request or the current branch's upstream configuration; do not assume the remote is named `origin`.

Do not run `git pull` repeatedly without new evidence. Identify whether the repository is in a merge, rebase, or cherry-pick state before proceeding.

### 2. Inventory conflicts and contracts

List unmerged paths and inspect the combined diff:

```bash
git diff --name-only --diff-filter=U
git diff --cc
git diff --check
```

For each path, inspect `HEAD`, the incoming side, and the working file. Then inspect the relevant:

- project-scoped `AGENTS.md` and applicable skills
- schema, migration, enum, route, API, and configuration contracts
- callers and dependents
- focused regression tests and repository-native verification commands

Classify each conflict by behavior, data contract, security boundary, accessibility, documentation, or test intent. Record which side owns each requirement before resolving it.

### 3. Resolve by responsibility

- Remove only the conflict markers; retain compatible behavior from both sides.
- Prefer a small semantic integration over choosing an entire side.
- Preserve stronger validation, authorization, tenant scoping, locking, retry behavior, accessibility, pagination, and error handling when they are supported by the current contract.
- Do not reintroduce removed states or fields, reference columns absent from the current schema, or discard existing tests without evidence.
- For database or migration conflicts, inspect the actual current schema and index names. Never edit an already-applied migration merely to make the merge pass.
- For exception handling, absorb only the intended constraint or failure class; rethrow unrelated failures.
- Update specifications and tests when the resolved behavior changes, and avoid duplicating the same rule across documents.

### 4. Validate before completing integration

Run these checks after editing:

```bash
rg -n '^(<<<<<<< |>>>>>>> |\|\|\|\|\|\|\| )' --glob '!vendor/**' .
git diff --check
git status --short
```

The marker search must return no opening, base, or closing conflict markers, and the status must contain no unmerged entries. The separator marker is checked in context by the opening and closing markers; this avoids treating valid Markdown `=======` underlines as conflicts. Run the narrowest affected tests first, then the repository's documented checks for the target project; do not assume a language, package manager, or framework.

Run language-server or project diagnostics on every edited source file. Review diagnostics for real errors separately from expected findings in ignored vendored dependencies. Do not edit vendored files or remove a scanner finding without evidence that it belongs to project code.

Before staging, inspect the final diff for accidental files, secrets, debug output, generated-file churn, and unrelated formatting. After staging, re-run:

```bash
git diff --cached --check
git status --porcelain=v1 | grep -E '^(U|AA|DD|AU|UA|DU)' || true
```

### 5. Finish safely

- If the user requested only conflict resolution, stop with resolved files, validation evidence, and the remaining commit/push action clearly stated.
- If the user explicitly requested completion, stage only resolved paths, create the required merge or rebase commit, and verify the resulting history.
- Before pushing, fetch again if the remote may have changed. Never force-push unless the user explicitly authorizes it and the history rewrite is reviewed.
- Report the exact merge/rebase commit, push result, tests, diagnostics, assumptions, and blockers.

## Conflict report format

Use this compact handoff after resolution:

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

- **Scope:** Git integration state and the minimum source, test, specification, or configuration files needed to resolve it.
- **Activation:** Use for an explicit Git conflict or non-fast-forward integration task.
- **Deactivation:** Stop after the requested integration state is verified; do not perform unrelated cleanup.
