## Unit
U4 (governance): `.github/workflows/governance.yml` becomes a callee: `workflow_call` (no inputs, no secrets) plus the weekly `schedule`. The `push`, `pull_request` and `merge_group` triggers, `workflow_dispatch` and the workflow-level `concurrency` are gone. Job-level `concurrency` on `record` and `delivery-status-publish`, every job `if:` (including the `push` guards) and `instrument-self-tests` are byte-identical to main. #2629's record-job API budget (M0-M3) is kept as merged.
Stacked on U0c `d22b5f303e09`, with `origin/main` (containing #2579, #2629, #2638) merged first. Head `f0e4a9d1d3645e93d5540ca14174cdaaa46c9b49`.
Files: `governance.yml`; `tools/policy/policy_lint.mjs` (+11, the R2d plant); `tests/entities.py` (+13, `_mq_problems`, U8's rule verbatim); `pr-contract-rerun.yml` (drop `Governance` from the two watched lists, as U8 did for `Budget raise gate`); `dev/audit/harnesses/r10_ci_layout_u4/{map.json,unitcheck.sh,mutants.py}`. `git diff --stat d22b5f303e09 HEAD` for U4's own delta, since the stack includes U0c.

## Interface
Consumes U0c's caller `governance`: no `with:`, no `secrets:`, grant `contents: read`, `pull-requests: read`, `issues: write`, run when the workset names `governance`. Check names `governance / policy-docs`, `governance / env-matrix`, `governance / wave-script`, `governance / delivery-status` (PR only), plus the push-only `record` and `delivery-status-publish`. Exports nothing else.
`record`'s `if:` is `github.event_name != 'pull_request' && != 'merge_group'`, unchanged, so a `ci.yml` `workflow_dispatch` whose workset names governance would also run `record` (the old file's dispatch arm did the same). Flagged for the coordinator, not changed.

## Static map
`sh dev/audit/harnesses/r10_ci_layout_u4/unitcheck.sh origin/main` (instrument read from `archive/probe/design-ci-rev4`), against current main's `governance.yml`:
```
governance.yml head:    STATIC rows 132->132 lost 0 gained 0 changed 1 (mapped 1) misplaced 0 rc 0
plant, no map:          ... changed 1 (mapped 0) ... rc 1
```
The one changed row is `|triggers`; the `instrument-self-tests` rows are unchanged. The map is `{"changed": ["|triggers"]}` only.

## Controls
- Plant, `instrument-self-tests` edited (move-PR silent revert, plan §8): `changed 2 (mapped 1) rc 1`, refused.
- Input control, caller passes no `with:`: `undeclared=[] rc 0`. Plant, caller passes `pr`: `undeclared=['pr'] rc 1`.
- R2d forward-carry (#2629 round 2). Added a plant to `assertAcceptance`'s window-cache block: a foreign seed with the same head and a different `since` half (`'0'*40..<head>`), read through both `pullsByShaShared` and `fetchWindowShared`. `python3 dev/audit/harnesses/r10_ci_layout_u4/mutants.py`:
```
R0: rc=0 green
R2c: rc=1 KILLED  FIXTURE VACUOUS: window cache ["a window cache keyed on another window was served instead of ignored"]
R2d: rc=1 KILLED  FIXTURE VACUOUS: window cache ["a window cache keyed on the same head and another since was served instead of ignored"]
RESULT survivors=0
```
Null control: the same R2d mutant on main's `policy_lint.mjs` (no plant) gives `rc 0`, no VACUOUS line, so it survives there.
- `python3 tests/entities.py`: `ALL 2407 ENTITY CHECKS PASSED`. Before the `_mq_problems` and `pr-contract-rerun.yml` edits, 3 checks were red (the merge-queue pin twice, the follower's watched list), all caused by this trigger change.
- Scoped gate vs U0c's head: `MODE: SCOPED -- 3 script(s) run` (`doc_claims`, `entities`, `harness_headers`). `harness_headers`: 109 passed. `structure.py` PASSED; `tmp_paths --check` 0 refused; `selftest_wiring --check` 87 self-testing, 87 wired, 0 unwired; `throwaway_git --check` 0 refused; `policy_lint.mjs` TOTAL 0 errors.

## Live checks owed
The `pull_request` pair (`policy-docs`, `env-matrix`, `wave-script`, `delivery-status`) on draft PRs through `ci.yml` (delivery-status is PR-only). The `issues: write` push jobs `record` and `delivery-status-publish` are checked once after merge (R-3): no other governance job receives `issues: write` beyond the caller's cap.

## Wiring
none (no other unit's self-test steps added). Integration note: U8 carries the same `_mq_problems` hunk and `pr-contract-rerun.yml` list edit (`Budget raise gate`); the `Governance` removal is U4's, so merge both.

## Red checks
none red on main's ancestry observed locally (entities and the scoped scripts above are green at this head).

## Figures
Every count above is from the command beside it, at head `f0e4a9d1d3645e93d5540ca14174cdaaa46c9b49`.

## Head
`f0e4a9d1d3645e93d5540ca14174cdaaa46c9b49`, measured at this head; `origin/main` fetched at the time of writing, `date -u` of the run: 2026-10-23.

## Mutation proof
The window-cache key mutants R2c and R2d (`python3 dev/audit/harnesses/r10_ci_layout_u4/mutants.py`) are both KILLED by the acceptance's window-cache block; see `## Controls` for the output. The trigger change is proved by `unitcheck.sh`'s plants: the unmapped map reads rc 1, an edited `instrument-self-tests` reads rc 1.

## Null control
R2d on main's `policy_lint.mjs`, without the new plant, survives (`rc 0`, no `FIXTURE VACUOUS` line); the unmutated file (R0) stays green; the input control passes with the caller as it is and fails with `pr` added. Commands and output in `## Controls`.

## Forward-carry
none (the #2629 round-2 R2d carry is closed in this diff, by the plant and `dev/audit/harnesses/r10_ci_layout_u4/mutants.py`)

## Friction
none
