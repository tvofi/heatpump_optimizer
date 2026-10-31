Fix review: merge d5ce36c662d21c6376cad6701d77f6c5ad15fe4d

bus-nonce: 3c94e7ff500ce57a3476566e1d1d0fae

## Scope

Round 4, a delta review of PR #3022 (R10-HOTFIX-LEARNER-INPUTS) at head d5ce36c662d21c6376cad6701d77f6c5ad15fe4d. Round 3 returned merge at 2e4f3ebe0811a3b1a079c41ec269233ac5395871. The only new commit is d5ce36c66, which merges origin/main cabfaadc3 into the branch; `review_carry.py 2e4f3ebe d5ce36c6` prints FRESH-REVIEW, so the brief's four checks were run. This is a merge-only delta rather than a repair, so the round-4 re-cut rule in fixer.md does not apply. dev/governance/roles/ is unchanged between the merge base and origin/main, so the contract is current.

## Findings

None.

## Evidence

- (1) The merge carries no resolution. `git merge-tree --write-tree 2e4f3ebe cabfaadc3` gives tree 58777f5c526d0885c2f6712bdca5a8ec42454bcd, which equals `d5ce36c66^{tree}`. The only driver output is `LEDGER-MERGE: resolved tests/closures.json` (merged as a set), which is the automatic driver, not a hand edit (ev/mergetree-parents.txt).
- (2) In coordinator.py, main's hunks against the merge base 861f949ae are:
  - `_fold_flow_lift` attribution (~L856);
  - the `frozen=` partial with `room_air=False` (~L3394);
  - the COP-ratio frozen check, `heat_kw` now read first (~L5006–5037);
  - `_async_first_refresh_light`, which now awaits `boost.session_restored` (~L5833);
  - the `_learning_frozen(..., room_air=True)` keyword (~L6563);
  - `_resolve_away` (~L9598);
  - the DHW temperature freeze (~L9913).

  The branch's hunks are at ~L4248 and ~L4383 (load and save), L5171–5279 (`_void_heat_loss_learners`, `async_reset_heat_loss_learners`, `_reanchor_house_heat_loss_scale`) and ~L9325 (snapshot restore). None of main's hunks overlaps or calls into them. The branch functions read `stored`, `_heat_loss_anchors()` (config, `heat_energy.meter_of(self).earned`) and `_lower_floor_loss_ratio`. Main's merge touches only away.py, coordinator.py and sensor.py under custom_components/; heat_energy.py, thermal_model.py and boost.py are unchanged. `_learning_frozen`'s new `room_air` keyword defaults to True, which is the old behaviour. Inputs, ordering and call sites of the reset and swap-void path are unchanged.
- tests/features.py at d5ce36c66 (PYTHONPATH=tests/hastub): `ALL 4657 FEATURE CHECKS PASSED`, rc=0. All 8 checks in "A zone-sensor swap and the reset action void the heat-loss learners" are `ok` (ev/features-head.txt).
- The round-2 mutant is killed at this head. Reading `ratio_was` after the void (the swap at ev/mutant-void-before-ratio.diff) gives `3 of 4657 FEATURE CHECKS FAILED`, rc=1. The three failures are:
  - "a lower-floor sensor swap voids the ratio and leaves the scale intact";
  - "a reload over the swapped sensor voids nothing more";
  - "a lower-floor swap with a nameplate edit past the gate, in one load, keeps the ratio voided ..." (ev/features-mutant.txt).
- (3) For tests/features.py and tests/entities.py, the branch's +/- lines (merge base..2e4f3ebe) equal the merge's lines against main (cabfaadc3..d5ce36c66). Main's +/- lines (merge base..cabfaadc3) equal the merge's lines against the branch (2e4f3ebe..d5ce36c66). Each side's change carries over line for line, with nothing lost. The two entities.py additions are distinct: the branch adds the heat-loss reset button and service checks, main adds the R10-COP-GATE model-status cop row. No check is duplicated.
- (4) CI: `merge_train.py classify d5ce36c6` prints `GREEN d5ce36c662d21c6376cad6701d77f6c5ad15fe4d pending: none red: none`, exit 0, at the start of the review and again just before writing this verdict (ev/ci1.txt, ev/ci-final.txt). There are no reds to answer.
- Mergeability: origin/main has since moved to 0d33c9348 (#3029, #3033, #3034). `git merge-tree --write-tree origin/main d5ce36c66` exits 0 with tree 83b32b04 and no conflicts (ev/mergetree-main.txt).
- Head re-read before writing: refs/heads/fix/r10-hotfix-learner-inputs and refs/pull/3022/head are both d5ce36c662d21c6376cad6701d77f6c5ad15fe4d.
- review_packet.py render ran with rc=0 and no refusal signal (ev/review-packet.md).
