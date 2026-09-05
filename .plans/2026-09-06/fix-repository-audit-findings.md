# Plan: Fix repository audit findings

- Status: `blocked`
- Updated: 2026-09-06
- Owner: agent

## Goal

Resolve the seven repository audit findings with fail-before-write deployment boundaries, machine-checkable skill contracts, consistent planning authority and lifecycle rules, and a complete documented validation path.

## Scope

- In: `scripts/deploy-agents.sh`, `scripts/deploy-agents.ps1`, `scripts/validate-skills.py`, `tests/test_deploy_agents.py`, affected `skills/*/SKILL.md`, `spec/skills-spec.md`, and `README.md`.
- Out: new dependencies, CI setup, unrelated skill rewrites, deployment atomicity beyond the reported preflight defects, and promotion of the specification from `candidate` to `stable`.

## Evidence and assumptions

- Confirmed: the working tree was clean before this plan was created.
- Confirmed: `scripts/deploy-agents.ps1` writes to the deployment target before checking protected destination reparse points and checks the pi instructions entry only after deployment writes.
- Confirmed: `scripts/deploy-agents.sh` accepts a directory at `<target>/AGENTS.md`, exits successfully, and creates `<target>/AGENTS.md/AGENTS.md`.
- Confirmed: changing the `crisp` catalog authority to `All production files` still lets `python3 scripts/validate-skills.py` exit successfully.
- Confirmed: `.plans/2026-99-99/test.md` passes the current date-shape validation.
- Confirmed: `challenge-docs` and `challenge-light` declare read-only scope but directly instruct plan-file updates when `mark-plan` is active.
- Confirmed: `mark-plan` defines cancellation for stopped tasks but omits `planned -> cancelled` from valid transitions.
- Confirmed: `README.md` documents only `python3 scripts/validate-skills.py`; `python3 -m unittest -v` discovers no tests, while `python3 -m unittest discover -s tests -v` passes 12 tests.
- Confirmed: no PowerShell executable is available in the current environment.
- Assumption: deployed skill consumers tolerate additional scalar frontmatter keys. This must be confirmed before using frontmatter as the catalog parity source.

## Intent and boundaries

The change must reject unsafe deployment destination states before any write, make catalog parity validation specific to each skill, delegate plan writes to `mark-plan`, permit cancellation while awaiting execution approval, reject impossible calendar dates, and document a command sequence that runs both policy validation and deployment regression tests. Existing safe deployment behavior, skill names, and read-only boundaries remain unchanged.

Changing the plan lifecycle is an additive public state-transition change under the repository policy. Recommended compatibility decision: allow `planned -> cancelled`; existing plans require no migration, and rollback is a documentation revert because no persisted runtime schema exists.

## General laws

| ID | Law | Scope / Preconditions | Limits / Counterexample | Linked Contracts |
| --- | --- | --- | --- | --- |
| `L-01` | If any protected deployment destination has an unsafe type or reparse boundary, deployment fails before the first write. | POSIX and PowerShell entry points; target, `AGENTS.md`, `skills/`, and pi agent destinations. | A canonical real directory with a regular `AGENTS.md` file and real `skills/` directory remains deployable. | `C-01`, `C-02`, `C-03` |
| `L-02` | A validation success claim is emitted only after every contract named by that claim has been checked. | Catalog parity, plan paths, and documented repository validation. | Product behavior and ecosystem-specific workflows remain outside `validate-skills.py`. | `C-04`, `C-07`, `C-08` |

## Invariants and state rules

- Safe deployment performs all destination validation before copying, mirroring, deleting, or linking.
- Existing protected symlinks or reparse points are never traversed.
- `<target>/AGENTS.md` is absent or a regular file; `<target>/skills` is absent or a real directory.
- Every catalog skill has exactly one matching declared role, activation, and modification authority.
- Challenge skills remain read-only; only active `mark-plan` authority records challenge outcomes in a plan file.
- Valid plan transitions include `planned -> cancelled` and preserve all existing transitions.
- Plan directory names are real ISO calendar dates, not only `YYYY-MM-DD` shapes.
- The documented repository validation path runs policy validation and all repository tests.
- Forbidden states: partial writes after a known-invalid preflight condition, successful deployment into an `AGENTS.md` directory, catalog mismatch with validator exit code 0, direct challenge-owned file edits, and invalid calendar-date plan folders accepted as valid.

## Contracts

| ID | Behavior | Condition / Input | Expected Output / Error | Invariant | Test path/name | Implementation boundary | Permanent spec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-01` | PowerShell rejects reparse destinations before writes. | Target, `AGENTS.md`, `skills/`, or pi agent directory is a symlink/junction/reparse point. | Non-zero exit; protected destination and external target remain unchanged. | `L-01` | `tests/test_deploy_agents.py::DeployAgentsTests` PowerShell reparse cases | `scripts/deploy-agents.ps1` preflight | `spec/skills-spec.md` Section 3.5 |
| `C-02` | Both deployment scripts reject a non-file `AGENTS.md` destination. | `<target>/AGENTS.md` exists as a directory or other non-file entry. | Non-zero exit before deployment writes; no nested copy is created. | `L-01` | POSIX and PowerShell `test_rejects_agents_directory_before_write` | Both deployment entry points | `spec/skills-spec.md` Section 3.5 |
| `C-03` | Link-mode validation precedes deployment effects. | Pi destination is an existing real file or unsafe reparse directory. | Non-zero exit and deployment target remains untouched. | `L-01` | PowerShell equivalents of existing POSIX pi preflight tests | `scripts/deploy-agents.ps1` preflight ordering | `spec/skills-spec.md` Section 3.5 |
| `C-04` | Catalog parity is checked per skill. | A skill role, activation, or authority differs from its catalog row. | Validator exits non-zero and identifies the skill and mismatched field. | `L-02` | `RepositoryContractTests.test_catalog_contract_mismatch_fails` parameterized subtests | `scripts/validate-skills.py` and canonical skill metadata | `spec/skills-spec.md` Sections 2, 5, and 6 |
| `C-05` | Challenge plan recording uses `mark-plan` authority. | Challenge completes while `mark-plan` is active. | Challenge hands the decision to `mark-plan`; challenge itself remains read-only. | Read-only authority | Non-executable contract review plus validator catalog parity | `skills/challenge-docs/SKILL.md`, `skills/challenge-light/SKILL.md`, and `skills/challenge/SKILL.md` if needed | `spec/skills-spec.md` Sections 2 and 3 |
| `C-06` | A planned task can be cancelled. | User stops or replaces a plan before execution approval. | `planned -> cancelled` is valid; no checklist item executes. | Plan lifecycle | `RepositoryContractTests.test_planned_plan_can_be_cancelled` | `skills/mark-plan/SKILL.md` | `spec/skills-spec.md` Section 3.4 |
| `C-07` | Plan folders require valid calendar dates. | A plan path uses a shaped but impossible date such as `2026-99-99`. | Validator exits non-zero with the plan path. | `L-02` | `RepositoryContractTests.test_invalid_plan_calendar_date_fails` | `scripts/validate-skills.py` | `spec/skills-spec.md` Sections 3.4 and 5 |
| `C-08` | Documented validation runs all checks. | A maintainer follows `README.md` validation instructions. | Both skill validation and all 12 or more repository tests execute; zero-test discovery is not presented as success. | `L-02` | Run commands exactly as documented | `README.md`; optional test package marker only if the documented command requires it | `README.md` and `spec/skills-spec.md` Sections 5 and 6 |

## Structural design

- Keep POSIX validation as direct shell predicates; add only the missing destination type guard before `cp`.
- In PowerShell, centralize reparse/type inspection in one local preflight helper and invoke it for each protected path before `New-Item`, `Copy-Item`, deletion, or link creation. Do not introduce deployment classes or external modules.
- Prefer explicit scalar skill metadata for `role`, `activation`, and `modification-authority` only if consumer compatibility is confirmed. Parse one canonical representation and compare exact normalized values against the four catalog columns. Do not rely on repository-wide marker strings.
- Parse plan folder dates with Python standard-library calendar validation after the existing shape check.
- Preserve challenge read-only authority by changing ownership wording, not by granting challenge skills file-write permission.
- Add only the lifecycle edge required by the existing cancellation semantics.

## TDD slices and checklist

- [ ] `C-01` **PowerShell reparse preflight** - Red: add PowerShell integration cases in `tests/test_deploy_agents.py`; Green: add preflight checks in `scripts/deploy-agents.ps1`; Verify: `python3 -m unittest discover -s tests -v` under an environment with `pwsh` or `powershell`.
- [ ] `C-02` **Reject invalid AGENTS.md destination types** - Red: add POSIX and PowerShell directory-destination regressions; Green: reject non-file entries before writes in both scripts; Verify: `python3 -m unittest discover -s tests -v`.
- [ ] `C-03` **Move PowerShell link checks before writes** - Red: add pi real-file and reparse-directory no-write assertions for PowerShell; Green: complete all `-Link` preflight before target creation/copy; Verify: `python3 -m unittest discover -s tests -v` under PowerShell.
- [x] `C-04` **Validate per-skill catalog contracts** - Red: mutate each catalog field independently and assert failure; Green: add the approved canonical metadata and exact comparison in `scripts/validate-skills.py`; Verify: `python3 -m unittest discover -s tests -v` and `python3 scripts/validate-skills.py` - passed: all three mismatch subtests, current catalog parity, and `/spec-drive`-only activation regression.
- [x] `C-05` **Clarify challenge plan-write ownership** - Update challenge skill wording so active `mark-plan` records the result; synchronize the catalog/spec without changing challenge authority; Verify: `python3 scripts/validate-skills.py` plus manual contract review of the three challenge files - passed.
- [x] `C-06` **Add pre-execution cancellation transition** - Red: add a repository contract test for `planned -> cancelled`; Green: update `skills/mark-plan/SKILL.md` and `spec/skills-spec.md`; Verify: `python3 -m unittest discover -s tests -v` - passed.
- [x] `C-07` **Validate calendar dates** - Red: add impossible-month and impossible-day cases; Green: use standard-library date parsing; Verify: `python3 -m unittest discover -s tests -v` - passed: `2026-99-99` rejected.
- [x] `C-08` **Document complete validation** - Update `README.md` and the quality/stabilization text to run both exact commands; Verify: execute the documented commands from a clean repository root and confirm the test count is non-zero - passed: 23 tests ran, 5 skipped only for unavailable PowerShell.
- [ ] `C-01,C-02,C-03,C-04,C-05,C-06,C-07,C-08` **Final quality and spec sync** - Review the final diff for contract consistency and ASCII-only Markdown; Verify: `sh -n scripts/deploy-agents.sh`, `python3 -m py_compile scripts/validate-skills.py tests/test_deploy_agents.py`, `python3 scripts/validate-skills.py`, `python3 -m unittest discover -s tests -v`, `git diff --check`, and PowerShell parser/runtime verification.

## Decisions and deviations

- 2026-09-06: Keep specification status `candidate`; this task repairs gates but does not independently prove all stabilization criteria.
- 2026-09-06: Recommend retaining challenge authority as `None` and delegating plan-file recording to active `mark-plan`.
- 2026-09-06: Recommend the additive `planned -> cancelled` transition with no migration; rollback is a synchronized documentation revert.
- 2026-09-06: User approved execution of the recommended plan on 2026-09-06.
- 2026-09-06: Approved adding canonical scalar `role`, `activation`, and `modification-authority` frontmatter fields; these fields will be validated as exact catalog contracts.
- 2026-09-06: Approved the additive `planned -> cancelled` transition with no migration and documentation-revert rollback.
- 2026-09-06: C-04 through C-08 implemented and verified; C-01 through C-03 remain pending PowerShell runtime verification.
- 2026-09-06: Status changed to `blocked` because no PowerShell runtime is available in this environment.
- 2026-09-06: User clarified that `spec-drive` must activate only via `/spec-drive`; `/sdd` is not an allowed alias.
- 2026-09-06: Added PowerShell coverage for target, `AGENTS.md`, `skills/`, and `-Link` preflight boundaries.
- 2026-09-06: Clarified `spec-drive` activation: only `/spec-drive` is a command alias; `/sdd` is forbidden. Validator and regression test pass.

## Verification

- [x] `python3 scripts/validate-skills.py` before plan creation - passed: 16 skills and current catalog parity.
- [x] `python3 -m unittest discover -s tests -v` before plan creation - passed: 12 tests.
- [x] `sh -n scripts/deploy-agents.sh` before plan creation - passed.
- [x] Python LSP diagnostics before plan creation - no diagnostics.
- [ ] PowerShell runtime verification - unavailable in the current environment; five PowerShell regression tests are present but skipped.
- [x] `python3 scripts/validate-skills.py` after implementation - passed: 16 skills, exact catalog metadata parity, valid plan dates, and safety markers.
- [x] `python3 -m unittest discover -s tests -v` after implementation - passed: 23 tests, 5 skipped because PowerShell is unavailable.
- [x] `sh -n scripts/deploy-agents.sh` and Python bytecode compilation - passed.
- [x] `git diff --check` - passed.
- [ ] Final quality gate - blocked until PowerShell parser/runtime verification is available.

## Blockers and open questions

- Blocker for final completion: a PowerShell runtime is required to execute `C-01`, `C-02`, and `C-03`; local skipped tests or static inspection alone will not count as full verification.
