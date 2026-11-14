Fix review: merge 805bf6d00f18d70613dd5e3575fbea91c22bb2a8

bus-nonce: b0a8abd4b82802ff36864a9f0ce1a8a9
pending-ci: gate

## Summary

- Round 2 is a delta review over the blocked head b17c78773410c7e1d77dcbbe39e8c817edf87454. The delta touches only `tools/ci/sweep.py` and `tools/ci/sweep_selftest.py`. Nothing under custom_components/ changed, so the scope does not widen.
- The previous block is resolved. The reviewer offered option (b), and the fixer took it: a red is now a deferral only when `gate.busy()`, imported rather than restated, names a run in `listed_at`'s reconstruction of the head at the red gate's start.
  - My case B now dispatches.
  - My case C still re-runs in place. That is correct under gate.py, and my round-1 case was mis-specified. Reasoning under Evidence.
  - The fixer's C variants dispatch, and A, D, E, F and F2 are unchanged.
- The reconstruction still has error domains. They are all in the direction the body dispositions as conservative (a real red re-run in place, never a false green), except where noted. They are listed under Findings. None of them blocks: round 1 measured that a real red re-run in place has the same outcome, and the body's Residual adopts that measurement.

## Findings

- Reconstruction error G: a held run reads busy. `listed_at` ignores the run's status, so a held run (`action_required`, no jobs) at the head reads `in_progress`. gate.py's `busy()` skips it by status, and `read_api` lists it with `jobs={}`.
  - Measured directly: `busy()` on read_api's row returns `[]`, and on listed_at's row returns `[43531447638]`.
  - Through the sweep (`ev/rev2_cases.py` G): a real red beside a held run is re-run in place at this head, and dispatched at b17c7877.
  - Conservative direction, but the body's Residual names only latest-attempt re-stamping, not this. The fix is one line: carry `action_required` through from `run["status"]`.
  - Carry: R11-INTAKE-R10-RESIDUE
- Reconstruction error I: read lag. `t0` is the gate job's `started_at`, but gate.py reads `busy()` later, inside `judge()` after `reaches()` (git first, API reads last). A source that finishes in that window was finished to `busy()` but reads unfinished at `t0`.
  - Measured (`ev/rev2_cases.py` I): a lower-id unit finishing 10 s after the red gate started, 20 s before it completed, makes a real red re-run in place.
  - The mirror direction: a run created between `started_at` and the read is excluded by the `created_at <= t0` filter. A true deferral from it then dispatches. That is origin/main's behaviour, so it is not a regression, but it is a residual cost of the #3544 class.
  - A sound bound would use the read instant, which the gate does not stamp. Exposing it, or bracketing the read between `started_at` and `completed_at`, is follow-up work.
  - Carry: R11-INTAKE-R10-RESIDUE
- Reconstruction error J: a skipped job decided after `t0`. A skipped job always reads completed. A job GitHub listed pending at `t0` and skipped only after its needs resolved was unfinished to `busy()`. If it is a unit, a true deferral then reads as a verdict and dispatches, which is origin/main's behaviour. This is argued from the rule, not run: GitHub re-stamps skipped jobs, so no fixture stamp can tell the two apart. The body states the rule but not this direction.
  - Carry: R11-INTAKE-R10-RESIDUE
- Still unsettled from round 1: API cost. `covered_deferral` lists jobs for every other run at the head on each stale red, with no cache, so a sweep costs O(reds × runs) reads.
  - Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- HEAD: `ev/HEAD.txt` holds 805bf6d00f18d70613dd5e3575fbea91c22bb2a8. The PR body's `## Head` names the same SHA.
- Merge with main: `git merge-tree --write-tree origin/main 805bf6d0` rc=0 (`ev/merge_tree.txt`).
- Previous verdict's cases (`ev/rev_cases.py`, round 1's, unchanged), at this head (`ev/rev_cases_head.out`):
  - A: dispatch.
  - B: dispatch. It re-ran in place at b17c7877, so it is resolved.
  - C: re-run in place.
  - D: dispatch.
  - E: attempt 44 left, attempt 43 re-run in place.
  - F and F2: dispatch after 4 attempt reads each.
  - At b17c7877 (`ev/rev_cases_b17c.out`): B and C re-run in place, as recorded in round 1.
- The fixer's claim about C, judged against gate.py: it holds.
  - My C's newer run R3 was created at 07:59, before the red's `t0` of 08:02. Its gate had not started then: it started at 08:03 and is listed `waiting`, so `started()` is false.
  - R3 lists `governance / delivery-status-publish`, unfinished at `t0`. `judging()` treats every listed job whose prefix is in UNITS as one that must be completed, and `governance` is a unit prefix, so `judging(R3)` is False.
  - R3's id is higher, but its gate had not started, so the tie-break does not exclude it. `busy()` therefore names R3: the red gate deferred, and an in-place re-run is right.
  - My round-1 C asserted a real red that gate.py would not have judged. With a non-unit job (the fixer's `refresh` variant), or with R3's gate already running at `t0`, it dispatches.
  - Whether `judging()` should count a post-gate report job like delivery-status-publish is gate.py's question, outside this diff.
- Reconstruction checks against `busy()` at the instant:
  - Unstarted job: reads queued. Running job: in progress. Both are pinned by the self-test.
  - Skipped job: always completed (J above).
  - Re-stamped non-skipped job (my H, `ev/rev2_cases.py`): a lower-id run completed at `t0`, with one unit re-run after it, makes a real red re-run in place. This is the body's dispositioned Residual (latest-attempt stamps, conservative direction).
  - Run created after `t0`: absent. A run with no jobs: busy, which matches busy() for `queued` but not for `action_required` (G).
  - Ties to the second: a completion, a start or a creation in `t0`'s own second reads done, started or present. Since the real read is later than `t0`, that is the side consistent with it.
- My mutants on listed_at and covered_deferral (`ev/mut2.py`, `ev/mutants_listed_at.out`), all killed:
  - created_at filter dropped: 5 failed.
  - skipped clause dropped: 1 failed.
  - started-at tie made strict: 1 failed.
  - completed-at tie made strict: 1 failed.
  - busy leg forced True: 16 failed.
  - jobless run read completed: 1 failed.
- Body figures re-derived at this head (`ev/selftests_head.txt`, `ev/figures_head.txt`):
  - `sweep self-test: 108 checks, 0 failed`
  - `gate self-test: 106 checks, 0 failed`
  - `STRUCTURE RATCHET PASSED`
  - `RESULT replay reruns=1 max_attempt=2 sim_minutes=1 alarm=no`
  - `RESULT replay wait_s=0 first=FAIL swept=yes final=PASS`
  - `SWEEP-ARM rc 0`
  - All match the body.
- Not re-run by me, so not verified: the body's `mutant_run.py` counts (30 drawn, 28 killed; spec 23, 22 killed) and its round-2 failing-test-first count (101 checks, 3 failed).
  - Of its survivors, `per_page 101` and `others-include-self` are equivalent, and I agree.
  - The `created_at <` survivor sits on the conservative side, as stated.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched. No claim files or budgets are in the diff.
- CI: classify printed `WAIT 805bf6d00f18d70613dd5e3575fbea91c22bb2a8 pending: gate red: none` at every poll (`ev/classify.log`). The hotfix's prepr scope was owner-ruled, and CI is the authority for the code suites, so I am returning with `pending-ci: gate` and not waiting it out.
- No red sits on an owed-reds check at render. `tests / nightly-status` failed, and it is not owed. Red checks: none owed.
- Finder's harness: none named. The fixer's #3544 recording and C variants are the fixer's instruments. Cases A–F2 (round 1) and G–I (`ev/rev2_cases.py`) are mine.
