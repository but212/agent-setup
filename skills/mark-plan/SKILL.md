---
name: mark-plan
description: >
  File-backed planning and execution tracking for coding agents without a native
  plan mode. Use `.plans/<task-name>.md` as the single source of truth.
---

# Mark Plan

Use a Markdown plan file instead of a UI plan state machine. Create or update
`.plans/<task-name>.md`, then execute its checklist while keeping the file
accurate. The plan is local execution state; synchronize durable domain or
architectural requirements into the repository's appropriate documentation when
the task changes them.

## Operating contract

1. **Create the SSOT:** Before non-trivial implementation, search `.plans/` for
   a matching task. Reuse one matching `planned`, `in-progress`, or `blocked`
   plan. Do not silently reuse a `complete` or `cancelled` plan; ask whether to
   reopen it or create a new plan. If several active plans match, ask which one
   to use. Otherwise create `.plans/<task-name>.md` with lowercase kebab-case.
2. **Define authority:** The plan is authoritative for this task's scope,
   decisions, progress, blockers, and verification results. It does not override
   user requirements or repository guidance.
3. **Ground the plan:** Inspect the relevant code, tests, conventions, and
   repository commands. Record confirmed paths and commands; label unresolved
   facts as assumptions or open questions.
4. **Bound the work:** State the goal, in-scope work, out-of-scope work, and
   acceptance criteria. Do not add speculative tasks.
5. **Make it executable:** Give acceptance criteria stable IDs and map each
   checklist item to one or more IDs. Order items by dependency; name target
   paths and a concrete verification command or observable result.
6. **Update as truth changes:** Mark items only after completion and verification.
   Record decisions, deviations, blockers, and verification results in the plan;
   do not hide them only in chat.
7. **Protect user control:** Planning ends in review. Do not execute checklist
   items until the user explicitly approves execution (for example, “execute the
   plan”, “start implementation”, or equivalent); merely creating or reviewing a
   plan is not approval. Pause and ask when requirements are materially
   ambiguous, scope expands, a breaking change is needed, or a
   destructive/unrecoverable action is proposed.
8. **Finish honestly:** Do not mark the plan complete while required criteria,
   checklist items, failed checks, blockers, or open decisions remain unresolved.
   A checked item requires its verification result to be recorded; a complete
   plan requires every required item and criterion to be checked.

## Plan file format

Create the smallest useful file with this structure:

```markdown
# Plan: [Task name]

- Status: `planned`
- Updated: [YYYY-MM-DD]
- Owner: [agent or user]

## Goal
[One concise outcome]

## Scope
- In: [explicit boundaries]
- Out: [explicit exclusions]

## Evidence and assumptions
- Confirmed: [paths, existing behavior, commands]
- Assumption: [unverified fact], or `None`

## Acceptance criteria
- [ ] `C-01` — [Observable requirement]

## Checklist
- [ ] `C-01` **[Step name]** — `[target paths]`; verify: `[command or result]`

## Decisions and deviations
- [Decision, reason, and date], or `None`

## Verification
- [ ] [Command] — [result]

## Blockers and open questions
- [Question or blocker], or `None`

Allowed plan statuses: `planned`, `in-progress`, `blocked`, `complete`, and
`cancelled`.

- `planned`: plan exists and is awaiting review or execution approval; no
  checklist item is being executed.
- `in-progress`: the user approved execution and work is underway.
- `blocked`: execution cannot continue without an external answer, approval, or
  fix; record the exact blocker and resume as `in-progress` only after it is
  resolved.
- `complete`: every required criterion and checklist item is verified; this is a
  terminal state and must not be reused silently for new work.
- `cancelled`: the user stopped the task or replaced it with another plan; this
  is terminal unless the user explicitly reopens it.

Valid transitions are `planned -> in-progress`, `in-progress -> blocked`,
`blocked -> in-progress`, and `in-progress -> complete` or `cancelled`.
Reopening a terminal plan requires explicit user direction and a recorded
Decision; otherwise create a new plan.

Keep scope and acceptance criteria stable. If a discovered change is required,
ask before expanding scope and record the decision under **Decisions and
deviations**. Put optional work in **Out** or create a separate plan.

## Workflow

### Plan

- Read the request and repository guidance.
- Search the relevant implementation and tests before proposing steps.
- Create or update the plan file with evidence, boundaries, acceptance criteria,
  and dependency-ordered checklist items.
- Set status to `planned` and report the plan for review.
- Do not execute checklist items until the user requests execution or gives
  explicit approval using a clear action signal; then record that decision and
  set status to `in-progress` before the first checklist item.

### Execute

For each checklist item:

1. Confirm the plan and working tree have not changed unexpectedly. If another
   agent or process changed the plan, stop and reconcile it first.
2. Read the named target before editing.
3. Make the smallest change satisfying that item.
4. Run its verification command or record the observable result.
5. Check the item only after verification passes. On failure, leave it unchecked,
   record the command and failure, and set `blocked` when execution cannot
   continue.
6. Update `Updated`, status, decisions, and blockers immediately when they change.

Keep unrelated changes out of the plan. A required newly discovered task needs
approval before it enters scope; optional work belongs in **Out**, and an
independent task belongs in a separate plan.

### Close

- Run the relevant repository-native checks and record exact commands/results.
- Confirm every acceptance criterion and required checklist item is checked.
- Resolve or explicitly record all blockers and open questions.
- Set status to `complete` only then; use `blocked` when an unresolved external
  dependency prevents progress, or `cancelled` when the user stops or replaces
  the task. If the task changes scope, stop and record the decision before
  continuing.

## Output

When activated, report briefly in this order:

1. **Plan:** path and current status
2. **Now:** plan review, current checklist item, or `waiting for approval`
3. **Verification:** command/result, or `not run`
4. **Next:** next item, blocker, or completion

The plan file is authoritative. Chat summarizes it; it does not replace it.

## Controls

- **Activate:** `/mark-plan` or when the user asks for a file-backed plan,
  checklist-driven execution, or plan-mode behavior.
- **Deactivate:** `stop mark-plan` or `normal mode`.
