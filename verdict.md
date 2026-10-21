Fix review: merge 4b215f4be037df2d519b7d189663fd04d3e37c5b

bus-nonce: e692bc9e894afe85b252a0c8a90e73fe

Round 2: the re-review after `blocked 441d19932` (comment 6322582323, `ev/previous-verdict-6322582323.md`). Measured at `4b215f4be037df2d519b7d189663fd04d3e37c5b` from detached worktrees; its merge base with origin/main is `1ebc737e7` (origin/main's tip when I started). Re-read before posting: the PR head is still `4b215f4be037df2d519b7d189663fd04d3e37c5b` (`ev/head-at-post.txt`). Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, at both `1ebc737e7` and the later main `5a755f53e`.

What the fixer changed this round (`c34330926..29435d2fa`): the card's `degreeRow` now checks order only (`save >= 0 && cost >= 0`), with no convexity check. The features seam check now runs at two frozen instants (03:07, 15:07 UTC) and two starting rooms (19 and 23 °C). It requires the held figure to be equal across the two rooms and the plan's figure to differ by more than 1.0. There is a new ledger-save check, plus harness arms (`rotation`) and doc and card-test edits. The round adds no Python production line.

## Block

None. Each blocking item of the previous verdict (round 1, at `441d19932`) is resolved:
1. MB5 is now killed, independent of the clock (Evidence).
2. MX1 is now killed (Evidence).
3. Both carries are on the roster with their controls, at `origin/handoff/audit-r10-roster` `903d137b6` (an ancestor of the current `8138db551`) (Evidence).

The earlier round-1 block B1 (convexity hiding true rows) is answered by the order-only predicate. I re-measured it with the rotation arm (Evidence).

## Findings

- Non-blocking: MX4 still survives at this head. I replaced the mean of daily means in `price_tiles.published` with a pooled mean (`sum(sums)/sum(counts)`), and `tests/features.py` reads `ALL 4282 FEATURE CHECKS PASSED`, rc 0 (`ev/mut-MX4.diff`, `ev/MX4-features.log`). The horizon check still cannot tell the two estimators apart, because every day it builds holds the same sample count. The body's "mean of their daily means" is not pinned against a pooled mean. A check needs days with unequal counts. Carry: #2257
- Non-blocking: the tile prices a degree held (+54.4 in the `null` arm). The plan delivers only −0.514 K and +0.327 K per degree of setting, so the row overstates what pressing the button saves, by roughly 1.8× and 3×. The body discloses this and leaves the copy question to the judge or owner. Nothing in this round changes it. Carry: #2257

## Evidence

- RESULT head `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4282 FEATURE CHECKS PASSED`, rc 0 (`ev/wt-features.log`). This matches the body's 4282.
- RESULT head `node tests/card.mjs` (after `tests/plan_view.py`): `ALL CARD CHECKS PASSED`, rc 0 (`ev/wt-card.log`).
- RESULT mutant MB5 (`simulated.baseline_cost - result.baseline_cost` → `simulated.predicted_cost - result.predicted_cost` in `async_simulate`'s `monthly_held_cost_delta`): rc 1, `1 of 4282 FEATURE CHECKS FAILED`, namely `#2257: the held figure prices a degree from a steady start …`. The detail reads `(15,19.0): (-126.08, 84.77), (15,23.0): (-78.35, 56.4)` and `(3,19.0): (-116.07, 140.78)` / `(3,23.0): (-114.95, 138.63)`. These are exactly the body's figures, although my run was at about 21:30–21:49Z, a different wall time from the fixer's. The figures are reproducible under the freeze. I also checked the code path: `_solve_coord` anchors its prices on `dt_util.now()`, which `_fi_dt.freeze` pins, and the coordinator passes `start_time` into the optimizer (coordinator.py:5659, 11024), so the optimizer's `datetime.now()` fallback is not reached. The check is not vacuous in either half: at the head, held is equal across the rooms and the plan's figures differ by more than 1.0, and under MB5 the held figure becomes the plan's, so the equality fails. (`ev/mut-MB5.diff`, `ev/MB5-features.log`)
- RESULT mutant MX1 (the `"price_tiles": price_tiles.book(self),` line deleted from `_async_save_ledger`): rc 1, `1 of 4282 FEATURE CHECKS FAILED`, namely `#2257: the ledger save carries the price tiles' book, day by day [None]` (`ev/mut-MX1.diff`, `ev/MX1-features.log`).
- RESULT card mutants (`ev/card-mutants.txt`). MC1, MC2, MC7 and MC8 go red on exactly the checks the body names, with rc 1 each and 3, 2, 2 and 1 failures. Two extra mutants of my own:
  - MC9 drops `cost >= 0`: 2 red (the screenshot pair; "a warmer degree that saves …").
  - MC10 drops `save >= 0`: 1 red ("a degree cooler that costs more …").
  Each half of the order predicate is pinned on its own.
- RESULT fixer harness `dev/audit/harnesses/r10_advisor_degree.py rotation` at the head, sha1 `41ee4a43725dac312d95037575bc612f866af709` (the same as the body's). Every line reproduces the body exactly (`ev/harness-rotation.log`):
  - precondition: real `[67.9, 80.02, 74.03]` = stub;
  - 30 / 60 / 120 min: 40 shown, 0 hidden, gaps -2.29..+0.55 / -1.82..+1.22 / -2.50..+2.06;
  - null: 40 shown, gap +0.38;
  - `VERDICT rotation the card shows the row every evening at every cadence`, rc 0.
  The 30 and 120 min gap ranges are identical to round 1's reviewer probe (`probe/rev-2572-e25f00fd`), so the estimator did not move and only the predicate did.
- Step 2/9: no finder harness exists for owner items 6 to 8 (the owner's screenshot). The body now states in words that `r10_advisor_degree.py` is "this PR's instrument, not the finder's", which settles round 1's step-9 note. I did not rebuild a harness this round and did not re-run the `days`, `null` or `timing` arms. Those figures were confirmed at round 1's head, and this round moves no estimator line, so I carry them, not re-derive them.
- Step 4: no golden or claim file moved this round (`git diff 441d19932 4b215f4be` over `tests/golden/*claimed_drift.txt` and `structure_budgets.json` is empty). Round 1's single `advisor_page` card claim stands. I did not re-run `card_drift` myself; the body's `1 state(s) moved and claimed, 39 identical` is the fixer's, and CI's `fast` is green.
- Step 5: `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched (three-dot diff empty).
- Step 6, class: the round's class rule (the card's tile reads) returns the four sites the body dispositions. No second consumer of a tile pair exists.
- Step 7: the body's `## Head` names `4b215f4be037df2d519b7d189663fd04d3e37c5b` and its code head `b11f008c5`. The final merge `07e75418b` → `4b215f4be` brings in origin/main `1ebc737e7` with no conflict.
- Step 10: both carries are on the roster at `903d137b6`, and each states its control as a precondition:
  - R10-LIVESTATE item 4c077302: "a word-bounded grep for _price_tiles in coordinator.py returns nothing";
  - R10-UX-HEALTH item 6ce59610: "node tests/card.mjs green with advisor:settings absent from PENDING".
  Both groups are live. The friction carry is on R10-ORCH-MACHINERY.
- Step 11: 48 check runs at the head, all concluded: 31 success, 16 skipped, 1 failure (`ev/check-runs.tsv`). The one red is `nightly-status` (run 119495733978), which grades main; this diff does not reach what it reads, and the body's `## Red checks` says so. `mutation`, `closures`, `coverage` and `fast (3.14)` are green. This round adds no Python production line, so the `mutation` lane's green says nothing about the card lines; my card mutants above cover them.
- Step 13: `git merge-tree --write-tree origin/main 4b215f4be…`:
  - at `1ebc737e7`: rc 0, tree `520d73934d8e`;
  - at the later main `5a755f53e`: rc 0, tree `4b12216d7419`, `LEDGER-MERGE: resolved tests/closures.json` (merged as a set).
  No `MERGE-CLAIM` line printed (`ev/merge-tree*.txt`).
- Step 14: this round moves no budget, ledger or score file. Round 1's `structure_budgets.json` lowerings stand as round 1's review judged them.
- Step 15: the added lines are the card predicate and tests only, inside the Advisor's owning seam. No breach.
- Round: 2 for this group's fixer, so the round-4 re-cut rule does not apply.
