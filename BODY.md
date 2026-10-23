## Unit
U4 (governance): `.github/workflows/governance.yml` becomes a callee: `workflow_call` (no inputs, no secrets) plus the weekly `schedule`. The `push`, `pull_request` and `merge_group` triggers, `workflow_dispatch` and the workflow-level `concurrency` are gone. Job-level `concurrency` on `record` and `delivery-status-publish`, every job `if:` but `record`'s, and `instrument-self-tests` are byte-identical to main; `record`'s `if:` gains `github.ref == 'refs/heads/main' &&` (see `## Resume fix`). #2629's record-job API budget (M0-M3) is kept as merged.
Stacked on U0c `d22b5f303e09`, with `origin/main` (containing #2579, #2629, #2638) merged first. Head `767a06f7f6dd02bb0cf291377686e292c4bbe587`.
Files: `governance.yml`; `tools/policy/policy_lint.mjs` (+11, the R2d plant); `tests/entities.py` (+13 `_mq_problems`, U8's rule verbatim; +58 the write-job reach pin); `pr-contract-rerun.yml` (drop `Governance` from the two watched lists, as U8 did for `Budget raise gate`); `dev/audit/harnesses/r10_ci_layout_u4/{map.json,unitcheck.sh,mutants.py}`. `git diff --stat d22b5f303e09 HEAD` for U4's own delta, since the stack includes U0c.

## Interface
Consumes U0c's caller `governance`: no `with:`, no `secrets:`, grant `contents: read`, `pull-requests: read`, `issues: write`, run when the workset names `governance`. Check names `governance / policy-docs`, `governance / env-matrix`, `governance / wave-script`, `governance / delivery-status` (PR only), plus the push-only `record` and `delivery-status-publish`. Exports nothing else.
`record`'s `if:` is `github.ref == 'refs/heads/main' && github.event_name != 'pull_request' && github.event_name != 'merge_group'`: a `ci.yml` dispatch at a PR branch no longer reaches it (fixed in this head, `## Resume fix`).

## Static map
`sh dev/audit/harnesses/r10_ci_layout_u4/unitcheck.sh origin/main` (instrument read from `archive/probe/design-ci-rev4`), against current main's `governance.yml`:
```
governance.yml head:    STATIC rows 132->132 lost 0 gained 0 changed 2 (mapped 2) misplaced 0 rc 0
plant, no map:          ... changed 2 (mapped 0) ... rc 1
```
The changed rows are `|triggers` and `record|` (the guard); the `instrument-self-tests` rows are unchanged. The map is `{"changed": ["|triggers", "record|"]}`.

## Controls
- Plant, `instrument-self-tests` edited (move-PR silent revert, plan §8): `changed 3 (mapped 2) rc 1`, refused.
- Input control, caller passes no `with:`: `undeclared=[] rc 0`. Plant, caller passes `pr`: `undeclared=['pr'] rc 1`.
- R2d forward-carry (#2629 round 2). Added a plant to `assertAcceptance`'s window-cache block: a foreign seed with the same head and a different `since` half (`'0'*40..<head>`), read through both `pullsByShaShared` and `fetchWindowShared`. `python3 dev/audit/harnesses/r10_ci_layout_u4/mutants.py`:
```
R0: rc=0 green
R2c: rc=1 KILLED  FIXTURE VACUOUS: window cache ["a window cache keyed on another window was served instead of ignored"]
R2d: rc=1 KILLED  FIXTURE VACUOUS: window cache ["a window cache keyed on the same head and another since was served instead of ignored"]
RESULT survivors=0
```
Null control: the same R2d mutant on main's `policy_lint.mjs` (no plant) gives `rc 0`, no VACUOUS line, so it survives there.
- `python3 tests/entities.py`: `ALL 2411 ENTITY CHECKS PASSED` at this head (its `FAIL` lines are the suite's planted negative controls; the count line is the verdict). Before the `_mq_problems` and `pr-contract-rerun.yml` edits, 3 checks were red (the merge-queue pin twice, the follower's watched list), all caused by this trigger change.
- Scoped gate vs U0c's head: `MODE: SCOPED -- 3 script(s) run` (`doc_claims`, `entities`, `harness_headers`). `harness_headers`: 109 passed. `structure.py` PASSED; `tmp_paths --check` 0 refused; `selftest_wiring --check` 87 self-testing, 87 wired, 0 unwired; `throwaway_git --check` 0 refused; `policy_lint.mjs` TOTAL 0 errors.

## Resume fix
Defect: `record`'s `if:` ran on any `ci.yml` `workflow_dispatch` naming `governance` (`prelude.derive` gives a dispatch `code`; `CODE_UNITS` holds `governance`), so an autofix or merge-main dispatch on a PR branch ran `issues: write` over the branch's code and a full `<tag>..origin/main` window on #2629's GITHUB_TOKEN bucket. Fix: `record` runs only at `refs/heads/main`. `concurrency` and steps untouched.
Pin (`tests/entities.py`, reads the registered job's `if:` and evaluates it over literals with `_gh_eval`; rule that enumerates the seams: the jobs with a `permissions:` block in governance.yml, `_DS_OVERRIDES`, = `record`, `delivery-status-publish`, plus `pr-contract` in its own file, which is not a governance.yml job and not a dispatch/push consumer):
- Red at `f0e4a9d1d`: `FAIL record (issues: write) runs at main only...` and `FAIL record holds a write grant and is unreachable from a PR branch`, both showing `'push at a PR branch': True, 'dispatch at a PR branch': True`.
- Plant: the old `if:` text evaluated by the same reader reaches a dispatch and a push at a PR branch (check `plant: record's pre-U4-resume if: reaches a dispatch at a PR branch`, ok).
- Null controls: push, schedule and dispatch at `refs/heads/main` reach `record` (true); `pull_request` and `merge_group` do not. Green at `767a06f7f`.
- `delivery-status-publish` (`push && refs/heads/main`) passes the same rule, unchanged. No other job in governance.yml holds a permissions block (`exactly three governance jobs override...` stays ok).
- `unitcheck.sh`: `record|` added to the map as changed; rc 0 mapped, rc 1 unmapped. `mutants.py`: R0 green, R2c and R2d KILLED, `survivors=0`. `structure.py` PASSED.

## Live checks owed
The `pull_request` pair (`policy-docs`, `env-matrix`, `wave-script`, `delivery-status`) on draft PRs through `ci.yml` (delivery-status is PR-only). The `issues: write` push jobs `record` and `delivery-status-publish` are checked once after merge (R-3): no other governance job receives `issues: write` beyond the caller's cap.

## Wiring
none (no other unit's self-test steps added). Integration note: U8 carries the same `_mq_problems` hunk and `pr-contract-rerun.yml` list edit (`Budget raise gate`); the `Governance` removal is U4's, so merge both.

## Red checks
none red on main's ancestry observed locally (entities and the scoped scripts above are green at this head).

## Figures
Every count above is from the command beside it, at head `767a06f7f6dd02bb0cf291377686e292c4bbe587`.

## Head
`767a06f7f6dd02bb0cf291377686e292c4bbe587`, measured at this head; `origin/main` fetched at the time of writing, `date -u` of the run: 2026-10-23.

## Mutation proof
The guard: the pre-fix `if:` (deleting `github.ref == 'refs/heads/main' &&`) turns the two `record` checks red, shown at `f0e4a9d1d` in `## Resume fix`.
The window-cache key mutants R2c and R2d (`python3 dev/audit/harnesses/r10_ci_layout_u4/mutants.py`) are both KILLED by the acceptance's window-cache block; see `## Controls` for the output. The trigger change is proved by `unitcheck.sh`'s plants: the unmapped map reads rc 1, an edited `instrument-self-tests` reads rc 1.

## Null control
R2d on main's `policy_lint.mjs`, without the new plant, survives (`rc 0`, no `FIXTURE VACUOUS` line); the unmutated file (R0) stays green; the input control passes with the caller as it is and fails with `pr` added. Commands and output in `## Controls`.

## Forward-carry
none (the #2629 round-2 R2d carry is closed in this diff, by the plant and `dev/audit/harnesses/r10_ci_layout_u4/mutants.py`)

## Friction
none
