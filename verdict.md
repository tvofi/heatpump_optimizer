Fix review: merge 4b78f35ce09943bf4dacdb090786ef17b7adad35

bus-nonce: dc52ecc781326c927f0088c0a31f83c7
pending-ci: gate (classify prints `WAIT 4b78f35ce09943bf4dacdb090786ef17b7adad35 pending: gate red: none`; no concluded red seen)

Round: second (delta). Resumed from verdict/3471 at 50f67556e112 (blocked bdf48d98 mutation-vacuous: M4, M5, M8). Repair range bdf48d98..4b78f35c: commits 31654ad9a and 1131843cf (code), plus main merges, which are not reviewed here. The delta touches only tools/audit/seat instruments, so nothing widens the review.

## Evidence

- Each previous block item at this head, with the owning `--self-test` (ev/mutants.txt):
  - M4 `self.log(pulse)` in `Train.wait_ci` replaced by `pass`: merge_train 614 checks, 1 failed (killed; was 0 failed).
  - M5 `done[-BASELINE_JOBS:]` replaced by `done`: 614 checks, 2 failed (killed; was 0 failed).
  - M8 the single remaining `stranded.sort(...)` replaced by `pass`: orchestrator_tick 315 checks, 1 failed (killed; the body's named mutant now reproduces).
  - Extra: `HELD_TOPIC` narrowed to triage only: 315 checks, 2 failed; `held = 0`: 315 checks, 1 failed. Both killed.
- Block item 2 (duplicates): `HELD_TOPIC` is defined once (orchestrator_tick.py:185) and the sort/held pair appears once (:2441-2442).
- Block item 3 (figure): the body now says merge_train 614, and I measure 614 checks, 0 failed at the head. orchestrator_tick 315/0 (ev/selftest_head.txt).
- Fixture repair: the 9000 s run is now the oldest, so the window drops it and the max stays 60m. `wait_ci` is driven end to end and its log is asserted.
- `git merge-tree --write-tree origin/main <head>` exits 0 (ev/merge-tree.txt).
- CI: `merge_train.py classify` exits 3, `WAIT ... pending: gate red: none` (ev/classify.txt). I did not poll for 30 minutes; the review is complete, so the verdict is returned with the pending-ci line above.
- Not re-run: owed_unactioned.py was not touched by the delta (the previous verdict's 60/0 stands); I did not re-run mutant M11 or M1, M2, M3, M6, M7, which the previous verdict killed and the delta did not touch.
- Prior findings: the previous verdict listed none.

## Findings

none
