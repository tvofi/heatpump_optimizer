Fix review: merge 3008f4499921cb6091ce700e41959b96d05ce5bb

bus-nonce: 8f6ba3a691d18ccd67b2224c229b1383

Round 4. This round reviews only the delta `4863ec0529..3008f44999` (ruling 11-09). Round 3 gave `merge` at `4863ec0529`. `review_carry.py 4863ec0529 3008f44999` prints `FRESH-REVIEW` and exits 1 (`ev/review_carry.txt`), because fixer commit 8bf9676b is in the range, so that verdict does not carry. The range has five parts: the bot pin commit f4845ffd, the triage pin efda938a, fixer commit 8bf9676b, and two merges of main (b4a1059e and 3008f449).

## Prior findings

- Round 1, `class-open` (the fold=1 repeated hour): round 3 found it resolved. This delta touches no `custom_components/` line: the interdiff of the PR's own diff (`git diff 46d0a521 4863ec05` against `git diff 265e061f 3008f449`) differs only in hunk offsets, one context line moved by main, `tests/features.py` and the mutation ledger (`ev/own_diff_interdiff.txt`). So round 3's fold probes and round 2's census and targeted mutants still apply.
- Round 3's Note `required-red-pending` (`tests / mutation` refused 9 unpinned sites added by this diff): resolved. At this head, `tests / mutation` is green and reads `1392 unpinned site(s) of 8238 candidate sites, 1394 at the ratchet base 265e061f` (`ev/mutation_summary.txt`). The bot commit f4845ffd pinned the kills, and efda938a triaged the one timeout.

## The delta

- 8bf9676b (`tests/features.py`, `_r11pp_batch`): main brought in a test that calls `simulate_trajectory[_batch](..., start_hour=7.0)`. This PR removes that parameter (`ev/start_hour_gone.txt`: no `start_hour` is left in `thermal_model.py`), so without this commit that test would fail with a TypeError. The replacement `step_hours=(7.0 + arange(n)*0.25) % 24` is exactly what main computed internally from `start_hour` (`ev/start_hour_old_semantics.txt`), and both the batch call and the scalar call get the same array. The three parity checks keep their oracle. This change adapts a call site and does not weaken the test. The CI fast shards that run `tests/features.py` are green at this head.
- efda938a (survivor_triage `_offset_change CMP_BOUND eaeb7f67`, verdict `gap`): this seat re-derived the claim with its own probe (`ev/cmp_bound_probe.py`, built by this seat, not the finder). On Europe/Stockholm 2026-10-25 the head returns `2026-10-25 01:00:00+00:00`. With `>` changed to `>=`, the mutant does not return within 5 s (`ev/cmp_bound_probe.txt`). The pin is honest: it is recorded as a gap, not as an equivalent and not as a kill.
- f4845ffd (bot `ci: pin killed mutants`): 8 killed_by pins for the new `dhw_schedule.py` sites, plus anchor renames for code this PR changed. Every pin names `tests/features.py` as its killer. `tests / mutation` agrees with the ledger.
- The main merges: `tests/structure_budgets.json` keeps the same decrements as at round 3 (-11 `class_excess_loc`, -7 `module_excess_loc`), now on main's values. Both metrics only move down, and no raise is involved.

## Findings

- Note: required-pending: `gate`, the only required context (`ev/required.txt`), reads failure at this head. That run was the `edit` event (46113984164). Its log reads `FAIL run(s) [46113984256] at this head are still being judged; their gate decides` (`ev/gate_tail.txt`). This is a deferral, not a defect. Run 46113984256 (the `code` event) has 29 jobs successful and 8 skipped, `tests / nightly-status` failed, and `pr-contract` is still queued (`ev/judging_run.txt`). `merge_train.py classify` reads `WAIT ... pending: gate red: none` (`ev/classify.txt`). Carry: dismissed: pending, decided by the code run's gate
- Note: round-count: this is the fourth review round. The re-cut clause has no ground here: no blocking finding is open, and round 3 was `merge`. Carry: dismissed: no open block to re-cut

## Evidence

- RESULT: reviewed head `3008f4499921cb6091ce700e41959b96d05ce5bb` (`ev/HEAD.txt`), from a detached worktree. The PR head still matched it at return.
- RESULT: `git merge-tree --write-tree origin/main 3008f449` exits 0 (`ev/merge_tree.txt`). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- RESULT: the PR's own diff (`265e061f...3008f449`) touches no `VERSION`, manifest, release-notes heading or golden fixture. Its only `*_budgets.json` change is the downward `structure_budgets.json` move described above.
- RESULT: live checks at the head (`ev/checks_head.txt`): every check is success or skipped except `gate` (the deferral above), `tests / nightly-status` (failed, not required) and `pr-contract / pr-contract` (queued).
- Not re-run, because the cite-CI rule covers both: the gate and the mutation table.
