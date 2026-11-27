Fix review: merge 4863ec0529f6eb7802288add93a5612557d5c2b8

bus-nonce: 330a3ff9d2e9c500a131ef1820c22402

Round 3. This is a delta review of `411932cae1..4863ec0529`, the head the round-1 verdict blocked, against that verdict (`blocked 411932cae1 class-open`) and the round-2 verdict (`blocked 6ccf3e03e2 head-moved`, which found no defect at `6ccf3e03e2`).

## Prior blocking findings

- Round 1, `class-open` (fold=1 `now` in the autumn repeated hour): resolved. This seat re-ran the probe on its own script (`ev/fold_probe.py`, `ev/fold_probe_head.txt`). Europe/Stockholm 2026-10-25, window 02:45-03:15, reads 0.25 for `now` 02:30 at fold 0 and at fold 1. Round 1 read -0.75 at fold 1. Australia/Sydney 2026-04-05 and America/New_York 2026-11-01 agree in both passes.
- The edges of the repeated hour also read right (`ev/fold_probe2_head.txt`, 5 of 5 OK). The second pass of a passed start opens in 0.667 h. A start passed in both passes rolls to the next day, 23.667 h. Starts before and after the hour read 0.167, 1.0 and 23.0.
- Round 2, `head-moved`: resolved. `git diff 6ccf3e03e2 4863ec0529` touches only `tests/open_meteo.py` (`ev/delta_6ccf3e03_4863ec05.diff`). `review_carry.py 6ccf3e03e2 4863ec0529` prints `FRESH-REVIEW`, so this round reads that delta. Round 2's figures for `411932cae1..6ccf3e03e2` carry, because that move changes no file they read: the census at 0 of 71040, 0 of 76416 and 0 of 73728, the wrap oracle at 0 of 5376, and the targeted mutants M1 to M13.

## The residual delta (`tests/open_meteo.py`)

- The new check pins `diagnostics()`'s `observed_points` against a planted observed series. That series is 3 points long and the forecast series is 5. A fixture assert refuses equal lengths.
- Mutant: `open_meteo.py:510` reads `self._forecast.times` in place of `self._observed.times`. The test goes from rc 0 to rc 1 with 2 checks failed, the new check among them (`ev/open_meteo_mutant.txt`). The file was then restored and `git status` reads clean. At the head the test reads `ALL OPEN-METEO CHECKS PASSED` (`ev/open_meteo_head.txt`).
- The delta has no `custom_components/` change, so nothing widens the review.

## Findings

- Note: required-red-pending: `tests / mutation` is red at this head. Its log reads `MUTATION TABLE REFUSED -- 1825 unpinned site(s) against 1818 ... 9 of them added by this diff` (`ev/mutation_summary.txt`). Those are the 9 sites round 2 matched to the body's `## Unpinned sites`, and the body's `## Red checks` answers them. `tests / mutation-pins (1)` and `(2)` were still `in_progress` at 06:04Z, after about an hour (`ev/pins_state.txt`). `gate` fails with `FAIL run(s) [45933914492] at this head are still being judged; their gate decides` (`ev/gate_tail.txt`). That is a deferral to the mutation run, and `merge_train.py classify` reads `WAIT ... pending: gate red: none` (`ev/classify.txt`). The autofix pin commit, or a red from it, decides. This verdict carries to the pin head only if `review_carry.py` prints `CARRY`. Carry: dismissed: ci-autofix pins in flight, answered by the body's Red checks
- Note: the round-2 stale-body note is resolved. The body now has one copy of each heading, and its `## Head` names `4863ec0529`.

## Evidence

- RESULT: head reviewed `4863ec0529f6eb7802288add93a5612557d5c2b8` (`ev/HEAD.txt`), from a detached worktree. The PR head still matched it at return.
- RESULT: `git merge-tree --write-tree origin/main 4863ec0529` exits 0 (`ev/merge_tree.txt`). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- RESULT: `411932cae1..4863ec0529` touches no `VERSION`, manifest, release-notes heading or `*_budgets.json` (`ev/delta_411932ca_4863ec05.diff`). Round 2 checked the mutation-ledger moves in that range by run.
- Not re-run: the gate and the mutation table. The cite-CI rule applies to both.
- `tests / nightly-status` is red, but it is not required.
