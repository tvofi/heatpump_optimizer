Fix review: blocked b17c78773410c7e1d77dcbbe39e8c817edf87454 class-open: covered_deferral reads a real verdict red as a deferral when any other run's job finishes after the red gate started (reviewer cases B, C), undispositioned in the body and contradicted by the module doc

bus-nonce: 2bf0ce32e008066a13845a2c987ee9c6

## Block

- Round 1, full review, at head b17c78773410c7e1d77dcbbe39e8c817edf87454 (the PR body's head, its code head 2fa16a7e plus the delivery row).
- The deferral predicate is a timing proxy: `source_after(gate.started_at, others)` is true for ANY job of ANY other run that finished after the red gate started or has not finished. That includes a job outside gate's `needs` in the green covering run (I used `tests / nightly-status`), and a job that runs after its gate in a newer run. `gate()` defers only on `busy()`, and `busy()` never reads a higher-id run whose gate has started, a `judging` run, or a completed run. So a gate whose red is a real verdict (busy() read nothing) is classed as a deferral, and it loses the dispatch it got at the merge base.
  - My cases (`ev/rev_cases.py`, not the fixer's; both ends in `ev/rev_cases.out` and `ev/rev_cases_base_sweep.out`): a real red on R1 that judged at 08:02:00, after every required source had finished, with R2 green and covering the newest event.
  - B: R2 has a report-only job that finished at 08:02:10. At base: dispatch. At head: re-run in place.
  - C: a newer review run's post-gate job finished at 08:04. At base: dispatch. At head: re-run in place.
  - A, the same real red with no late job: dispatch at both ends.
- The module doc's sentence "a red judged while another run's source was unfinished is the deferral, no verdict" is false as stated, for the reason above. The body's null control is scoped to "judged after every other run's source finished", so the overlap domain of a real red is neither guarded nor dispositioned (fix-review.md step 6: class-open, a predicate's unguarded domain).
- Harm, as I measured it: the misread red is re-run in place on the pinned programs and is not re-judged by fresh ones. I found no false green. The re-run re-reads the same failing source, so a persisting real red stays red and the PR stays blocked. A red that has since been resolved goes green, as #3400's in-place re-run already allows. The cost of the misread is the fresh-programs verdict, not correctness of the block. So either of these settles it:
  - (a) Disposition it. Correct the module-doc sentence and state in the body that a real red that overlaps a later job of another run is re-run in place, and why that is outcome-equivalent. Add B or C as a self-test check pinning that behaviour.
  - (b) Narrow the predicate to what busy() could have read: a lower-id run, or one whose gate had not started, that was unfinished at the red gate's start.

## Findings

- Each stale red in one sweep calls `covered_deferral`, which lists jobs for every other run at the head, and `judged`, which reads attempt 1 for each completed non-green dispatch at attempt 2 or later. That is O(reds × runs) API reads per sweep with no cache. It was 5 reads per red at #3544's six runs. It is bounded by the 100-run listing and the rate-limit exit, but it is unmeasured on a busy head. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- RESULT `python3 tools/ci/sweep.py --self-test` at head: `sweep self-test: 98 checks, 0 failed` (`ev/sweep_selftest_head.txt`). The body's figure re-derives.
- RESULT `python3 -I tools/ci/gate.py --self-test` at head: `gate self-test: 106 checks, 0 failed`. The body's figure re-derives.
- RESULT my targeted mutants on the diff's production lines (`ev/mut.py`, `ev/mutants.out`), all killed:
  - covered_deferral forced False: 3 failed.
  - source_after leg dropped: 9 failed.
  - covers leg dropped: 1 failed.
  - judged's first-attempt read disabled: 3 failed.
  - any readable first attempt accepted: 1 failed.
  - unreadable first attempt read as a judge: 1 failed.
- I did not re-run the body's `mutant_run.py` counts (19 drawn, 18 killed; spec 13/13), so they are not verified by me. Its one survivor, `per_page` 101, is equivalent at GitHub's cap of 100, and I agree.
- Attack (1), real red with a green from another event: see Block. Case A, the null control, dispatches at both ends.
- Attack (2), the cap and the settle bound:
  - Case E: a deferral at attempt 44 is left, and one at 43 is re-run in place. `must_rerun` runs before `stale_pin` in `judge()`.
  - A re-run that defers again is left by `settled` in settle (bot attempt, no source after it). In run() it is re-run at most once per sweep (`rerun_ids`), up to the cap. The fixer's deferred_again checks pass at head.
- Attack (3): case D, the #3261 pair (two deferral reds, nothing green), dispatches once at both ends.
- Attack (4): case F (attempt 1 returns 404) and case F2 (an attempt-1 listing with no gate row) both dispatch at head, after 4 attempt reads each.
- Attack (5), which copy of sweep.py runs, read in ci.yml at head:
  - gate-sweep.yml checks out `${{ github.sha }}` (the default branch for workflow_run) and runs `gate.py --sweep`, so main's copy.
  - ci.yml `sweep-self` restores `tools/ci/*.py` from `github.event.pull_request.base.sha`. For a dispatch it restores from `refs/heads/$INPUT_BASE` fetched at job start (ci.yml:378-396).
  - So main's copy judges in gate-sweep and in a dispatch's sweep-self. A bot-actor pull_request run's sweep-self keeps the pinned copy. The body states that exception itself, so the claim holds as the body words it.
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc=0 (`ev/merge_tree.txt`).
- VERSION, the manifest version and the RELEASE_NOTES.md heading are untouched. The three-dot diff touches only the delivery row, sweep.py and sweep_selftest.py.
- No claim files or budgets moved. carry_audit at head (packet): 1 item, routed.
- CI: classify printed `WAIT b17c78773410c7e1d77dcbbe39e8c817edf87454 pending: gate red: none` at three polls (`ev/classify.log`). CI is the authority for the code suites. There is no red on an owed-reds check at render: `tests / nightly-status` failed, and it is outside `merge_train.py owed-reds`, so nothing is owed for it.
- The finder's harness is none named. The fixer's #3544 recording in the self-test is the fixer's instrument, and cases A–F2 are mine.
