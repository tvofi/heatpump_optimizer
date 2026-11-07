R10-HOTFIX-NIGHTLY-STATUS: `tests / nightly-status` read red on main and every PR ("slow failed in the last verification dispatch"). The nightly now takes ~3.5 h, and the check graded the newest *concluded* run, which a newer in-flight run had already answered.

The cause has two parts. (b) The grader named a stale run. (a) The `slow` lane really is intermittently red. Actions API: dispatch 42235215315 (created 14:35:02Z, head 33e60b5) failed `slow` and concluded at 18:06:31Z. Dispatch 42242870295 (15:25:13Z) passed `slow` and concluded green at 19:17:32Z, and so did 42247578523 (15:55:42Z). For about 71 minutes the newest concluded run was the failed one while a newer run had already passed `slow`.

The lane failures are in `cycle_cost` (`tests/replay.py`): "runner class unknown: ref_ms 41.5 lies in no band of COST_RUNNER_CLASSES" (job 127950940724; ref_ms 40.1 in schedule run 41943946464), plus budget overruns in 41555367389 and 41749544997. That is the R10-REPLAY-COST-BUDGET seam, which this PR does not touch; it fixes only the grading. The lane flake is still open on main, and the orchestrator should route it to a replay-cost group.

Repair round 1 answers the blocked review (verdict/3263 at a5641182). (1) New arms kill every surviving grading-line mutant: two failed lanes with one answered, a green on another lane only, a newer `skipped` job, a newer `neutral` job, and an equal `created_at`. (2) A new check drives `main` with a stubbed `collect` and `_jobs`, and asserts that the in-flight run's jobs reach `verdict` (kills M10). (3) The code comment now gives the measured window of about 71 minutes, not "for hours". (4) This body is retaken whole. The dead `superseded` list (assigned, never read) is replaced by `all(...)`, which removes two unmutatable lines.

## Head

795e8aae20053c051a762242b28adcc5b93661a9. This is PR head b0ef8f54 with origin/main merged three times (merge-tree: no conflict each time): 80016a71f567, then 41aa9050fc87, then f2a015142714 (delivery rows only), because main moved twice during the `prepr.sh` passes. On top sit three commits: the checks and the grader edit, the harness, and `tests/closures.json`'s INERT read of the harness via `ci_predict.py --apply-inert`. Every figure below was re-taken after the last merge: harness, scope, structure, `tests/entities.py`, and `tools/pr/prepr.sh` rc=0. origin/main was re-read at 2026-11-07T01:41Z, at f2a015142714.

## Mutation proof

Mutants are applied one at a time to each changed grading line of `verdict` and of `main`'s in-flight fetch, 16 in total. M1 to M10 are the review's labels. Each mutant runs the `tests/entities.py` superseded-failure checks verbatim (sliced between their section markers) through `dev/audit/harnesses/r10_nightly_status_mutants.py`.

- At this head's check: 15 of 16 are KILLED, including the review's survivors M2 (`>` to `>=`), M4 (`== "success"` to `in OK_CONCLUSIONS`), M6 (all to any), M8 (any green name supersedes), M9 and M10 (`main` stops fetching). M11 (drop the `failing_jobs` guard) is killed by the new "concluded green fetches nothing" arm. M13 (drop the inner `except Unreadable`) is killed because the unreadable arm must read FAILED, exit 1, not UNREADABLE, exit 2. M14 (fetch the concluded run's jobs) and M15 (`verdict` not handed the jobs) are killed.
- M12 (drop the `concluded is not None` guard in `main`) SURVIVES and is equivalent. With no concluded run, `verdict` returns RUNNING before it reads `in_flight_jobs`, and `collect` returns no jobs to `failing_jobs` for a missing concluded run.
- The same 16 mutants against the old head b0ef8f54's check kill 4 (M1, M3, M5, M7) and leave 12 surviving. That reproduces the review's finding, and the reviewer's own harness (verdict/3263 `evidence/ns_check.py` arms A) gives the same split.
- Failing checks named under a killed mutant: "a failed lane is superseded only by a NEWER in-flight run that concluded the same job green; every other arm stays FAILED" (M1 to M9), and "main fetches the in-flight run's jobs and grades with them: ..." (M10, M11, M13 to M16).

## Null control

The unmutated slice reads rc=0 at this head. The same slice against the pre-fix grader at merge base 28482ece reads rc=1 (`TypeError: verdict() got an unexpected keyword argument 'in_flight_jobs'`), so the check cannot pass without the fix. A really failing lane still reads red. Ten arms must read FAILED: nothing newer; newer `slow` failed; newer `slow` pending; an in-flight run older than the concluded one; two failed with one superseded; green on another lane only; newer `skipped`; newer `neutral`; equal `created_at`. In `main`, a newer failed lane and an unreadable jobs listing both exit 1. The reviewer's harness `evidence/ns_check.py` gives PR-CHECK PASS and PROBES PASS at this head; at b0ef8f54 its probes also passed, because the production predicate was already right and only the check was vacuous.

## Figures

- `python3 dev/audit/harnesses/r10_nightly_status_mutants.py . .`: `RESULT unmutated rc=0`, `RESULT killed=15/16`. The rule is one mutant per changed grading line, and a mutant counts as killed when any sliced check fails.
- `python3 dev/audit/harnesses/r10_nightly_status_mutants.py <b0ef8f54 export> .`: `RESULT killed=4/16` (old check, same mutants: the null control for the kill count).
- `python3 dev/audit/harnesses/r10_nightly_status_mutants.py . <28482ece export>`: `RESULT unmutated rc=1` (pre-fix grader).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. `scope.run` names `tests/entities.py` and `tests/harness_headers.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: rc=0, "ALL 2642 ENTITY CHECKS PASSED" (count printed by the instrument). `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: rc=0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No budget raised.
- The 71-minute window, read from the Actions API (`get_workflow_run`): 42235215315 `updated_at` 2026-11-06T18:06:31Z (failure); 42242870295 `updated_at` 2026-11-06T19:17:32Z (success). The difference is 71 min 1 s.
- Environment: `bash tools/audit/seat/cloud-setup.sh --check` printed OK (venv-ci python3). The goldens are untouched; CI remains their authority.

## Red checks

Check runs for PR 3263 at the previous head b0ef8f54, read at about 00:40Z on 2026-11-07, every page (81 runs on one page of 100). The concluded reds are:

- `gate` (job 128239038648, run 42310451878, KIND edit, WORKSET arch-score budget-raise-gate): "FAIL run(s) [42309259823] at this head are still being judged; their gate decides".
- `gate` (job 128239026202, run 42309259823, KIND edit, same WORKSET): "FAIL run(s) [42310451878] at this head are still being judged; their gate decides".

Both are ordering reds between two edit runs, each deferring to the other's gate. This diff did not cause them; the code runs' gates (42309258015 job 128237638987, and 42318600453 job 128238186312) concluded success. Cheaper detector: none from this seat. The gate's ordering between sibling edit runs is the gate workflow's, outside this diff. Carry: R10-HOTFIX-NIGHTLY-STATUS.

`governance / instrument-self-tests` concluded success at b0ef8f54 (23:04:17Z to 23:31:05Z). It is the main-wide 30-minute timeout seam, so a timeout red at the new head would be that seam and not this diff. Carry: R10-HOTFIX-SELFTEST-TIMEOUT.

This head 795e8aae has had no CI yet.

## Forward-carry

none

## Friction

none
