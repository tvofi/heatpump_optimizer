# R10-CI-LAYOUT P2b unit U8: budget-raise-gate as a called workflow (topic r10-ci-layout-p2-u8)

Part of #2495. Head measured: `e56c58263c81d598f7097c6098fab67de3e45ca3`, stacked on U0c `d22b5f303e09`. U10 (`merge-main.yml`, `pr-contract-rerun.yml`) is not in this unit.

## Unit
Files, `git diff --stat d22b5f303..HEAD`: 9 files, 153 insertions, 432 deletions (net -279; production lines: the workflow, `budget_raise_gate.py` -174).
- `.github/workflows/budget-raise-gate.yml`: `on: workflow_call` with inputs `pr`, `base`, `head` (`type: string`, `default: ""`). The `pull_request`, `pull_request_review` and `merge_group` triggers and the top-level `concurrency:` are gone. The merge-queue naming step is dropped, since the prelude derives `pr`/`head` for a queue entry. The restore step and the gate step take the base SHA from the caller's payload (`github.event.pull_request.base.sha || github.event.merge_group.base_sha`) and fall back to `refs/remotes/origin/<inputs.base>` on a dispatch. The step fails if `inputs.pr` or `inputs.head` is empty. Still one job, no `if:`, workflow-level `contents/pull-requests/issues: read`, program restored from the base and run under `python3 -I`.
- `.github/workflows/budget-raise-gate-rerun.yml`: deleted.
- `tools/policy/budget_raise_gate.py`: the `--rerun-stale` arm, `stale_run`, `rerun_stale`, `_gh_json` and the 20 `rerun:` self-test rows are deleted (self-test now 224 checks, 0 failed). Not re-implemented in the sweep (see Controls).
- `tests/entities.py`, `tests/closures.json`, `tools/audit/round4/D11/governance_cost.py`: pins follow (see Wiring).
- `dev/audit/harnesses/r10_ci_layout_u8/{unitcheck.sh,map.json}`: the static map and the input control.
- `.github/workflows/pr-contract-rerun.yml`: one edit outside my files, see Wiring.

## Interface
Consumes U0c's caller `budget-raise-gate`: `with: pr, base, head` = `needs.prelude.outputs.{pr,base,head}`; caller grant `contents: read`, `pull-requests: read`, `issues: read`. Check name `budget-raise-gate / budget-raise-gate`. The callee keys on the caller's `github.event.*`, for example `pull_request.base.sha`, which a `pull_request_review` payload also carries. The review trigger (`pull_request_review: submitted, edited, dismissed`) is `ci.yml`'s, from U0c. Exports nothing else.

## Static map
`sh dev/audit/harnesses/r10_ci_layout_u8/unitcheck.sh d22b5f303e09` (instrument read from `archive/probe/design-ci-rev4`):
```
budget-raise-gate.yml head:           STATIC rows 7->7 lost 0 gained 0 changed 3 (mapped 3) misplaced 0 rc 0
plant, no map (want rc 1):            STATIC rows 8->7 lost 1 gained 0 changed 3 (mapped 0) misplaced 0 rc 1
input control, callee as it is:       undeclared=[] rc 0
plant, `head` declaration deleted:    undeclared=['head'] rc 1
```
The map admits: the dropped step "Name the pull request a queue entry carries", and the changed rows for the gate step, the restore step and `|triggers`.

## Controls
- Input control: every `with:` key of `ci.yml`'s `budget-raise-gate` caller is declared. The harness above and two new `tests/entities.py` checks (`every `with:` key ... is declared`, and a null control with one declaration deleted, which reads `['head']`).
- `_brg_defects` now pins: only `workflow_call`, exactly the three string inputs, no top-level `concurrency:`, one unguarded job, restore before the program, `python3 -I`, the permission triple. Its existing restore-removed null control still passes.
- Sweep coverage of the retired arm (`python3 tools/ci/sweep.py --self-test`, 21 checks, 0 failed): `a red older gate is re-run`, `a green run and the triggering run are never re-run`, `a triggering run whose gate is red re-runs nothing`. The retired self-test's "an older red run beside a newer green one is re-run" is that first row under U0c's `gate`-job model (the triggering run is the green one; the older red run's `gate` is re-run, #2009's every-red-twin rule). The sweep does not re-run the budget-raise-gate run itself, because that job is now re-judged through `gate`; U0c's design item 4 and M-2 own that.
- Mutation proof: `ci.yml` caller control above is the mutant of the declaration (one deleted gives rc 1). Not run per mutant locally, beyond that.
- `PYTHONPATH=tests/hastub python tests/entities.py` at this head: `1 of 2398 ENTITY CHECKS FAILED`, the same single red (`the template arm turns the acceptance red ...`) as at `d22b5f303` (`1 of 2400`), which is the known red U0c recorded. Two reds appeared at the first commit (`and is accepted when it does`, `inert_reads ...`): both from `tests/closures.json` still listing the deleted workflow, fixed by removing its two lines; CI owns re-derivation.
- `python3 tests/structure.py`: PASSED. `tmp_paths.py --check`: 0 refused. `selftest_wiring.py --check`: 87 self-testing, 87 wired, 0 unwired. `budget_raise_gate.py --self-test`: 224 checks, 0 failed.

## Live checks owed
Orchestrator, on a draft probe that raises a budget, with `ci.yml` and this unit's callee:
1. As tvofi submit a review, then dismiss it. Expect one review run each: `gate` pass, then FAIL, with no code unit re-run.
2. M-2 readings with the sweep disabled (no driver running): a red code-run `gate` beside a newer green review-run `gate` at one head. Record the PR's `statusCheckRollup` and `check-runs?check_name=gate&filter=latest`, and whether `mergeStateStatus` reports the check blocking, as observations.
3. With `python3 tools/audit/seat/sweep_driver.py --nochain` running: the code run's `gate` re-runs green and nothing else is re-run.
4. A `workflow_dispatch` naming a PR exercises the `origin/<inputs.base>` fallback, which nothing offline runs.

## Wiring
- U9b: `_EDITED_FILES` and `_CC_TWIN_ROUTE` in `tests/entities.py` lose `budget-raise-gate.yml`. Already done here, because those pins went red; the rest (`arch-score.yml`, `pr-contract.yml`) stays with U6, U7 and U9b.
- `_GOV_FILES` swaps `budget-raise-gate-rerun.yml` for `gate-sweep.yml`; `governance_cost.py` `GOV` swaps `rerun-stale-verdict` for `sweep` (the pin requires `GOV` and the files' jobs to agree).
- The merge-queue pin (`_mq_problems`) accepts a producer that is a `workflow_call` callee when `ci.yml` lists `merge_group` and has a caller job `uses`-ing that file; it does not evaluate the caller's `if:`. This is the general rule U6, U7 and U11 need as well. The null control for tests.yml is unchanged.
- The `_BRG_DOC` concurrency twin check is removed (a callee has no `concurrency:`); its three null controls now corrupt `ci.yml`'s block.
- `pr-contract-rerun.yml` (U10's file, which U10 deletes): `Budget raise gate` is removed from its two `workflows:` lists, because the follower's pin derives that list from workflows with a `pull_request` trigger, which the callee no longer has. U10 can take or discard this edit.
- `tests/closures.json`: two lines for the deleted file removed.

## Red checks
One: `the template arm turns the acceptance red on a template that fails its own contract` (`tests/entities.py`), red at `d22b5f303` and at this head, unchanged by this unit (U0c's known red, `policy_lint` interaction).
