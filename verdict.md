Fix review: merge c84a5fb197aa66c174e726eefd9de38051d0ef14

bus-nonce: 72d330e40b3cd729a204dfb16ee7467a

## Findings

- Residual: the meter-floor arm of `dev/audit/harnesses/r10_sav_wood_reference.py`, its `--no-wood-flag` switch and its `_wood_heated` emulation are the fixer's own instrument. They are not the finder's. The finder's harness is the `wood-plant` arm, committed by the R10-SAV-WOOD-HEAT seat (c4216e9da, 589af0074). The body uses the extension as its own and does not misattribute it. It lands in the tree with this PR. I name it here as `fix-review.md` step 9 requires. Carry: dismissed: disclosed, in the tree with this PR, nothing for a later stage to act on

## Evidence

- Round: second fix review of this PR, and the first at this head. The first review, of 091fc3bf3, was blocked on `ci-red` only.
- Head: I measured c84a5fb197aa66c174e726eefd9de38051d0ef14. `git ls-remote` showed `fix/r10-sav-meter-floor` still at that head before I wrote this verdict. The body's `## Head` names the same SHA.
- Delta since 091fc3bf3: `review_carry.py 091fc3bf3 c84a5fb19` prints FRESH-REVIEW, because the `structure_budgets.json` row moved. So this verdict is a full review. The PR's own patch to `custom_components/`, `tests/features.py` and `tests/card.mjs` is byte-identical to 091fc3bf3's three-dot patch, apart from hunk offsets. The rest of the delta is main's content and f1156e41e.
- Roles currency: `git diff 0a8033305...origin/main -- dev/governance/roles/` is empty, both at the merge base and at origin/main ba6fd7e8b.
- Step 13, merge: `git merge-tree --write-tree origin/main c84a5fb19` gives rc 0 against origin/main ba6fd7e8b, with no conflict (`ev/merge_tree.txt`).
- Step 5: the three-dot diff does not touch `VERSION`, `manifest.json` or `RELEASE_NOTES.md`.
- Step 4, claims:
  - Both claim files are untouched.
  - `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 0a8033305` printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, rc 0 (`ev/envdrift.log`).
  - `node tests/card_drift.mjs 0a8033305` printed `identical in all 45 states`, rc 0 (`ev/carddrift.log`).
- Step 1, mutation proof:
  - Each mutant ran `PYTHONPATH=tests/hastub python3 tests/features.py` on a `git archive` copy of the head (`ev/mutant_*.log`).
  - NULL: `1 of 4996 FEATURE CHECKS FAILED`, `#363 recorded_at` only. That check fails in every archive copy.
  - M1 `below_floor = False and ...`: 2 failed. Red: `a booked reference under the meter floor ... says why`.
  - M2 `applied_calibration` receives the month's `meter_calibration` in place of the wood-free pair: 8 failed. Red: the 7 wood checks the body lists.
  - M3 coordinator `"wood_heated": None`: 2 failed. Red: `the pending snapshot carries wood_heated ...`.
  - M4 `heating()` returns `self.active`: 2 failed, the same check (fading, displacing and free-heat legs).
  - M5 notifier `saving_below_meter_floor: False`: 2 failed. Red: `the receipt event says a row under the meter floor ...`.
  - M6 ledger `wood_free=False`: 4 failed, the 3 wood-free checks.
  - M7 wood-free actual line books `plan_kwh`: 4 failed, the same 3 checks.
  - Card: the receipt's `row.below_meter_floor` branch replaced with `false` gave `1 CARD CHECK(S) FAILED`, `a month under the meter floor states no saving and says why ...`. The head reads `ALL CARD CHECKS PASSED` (`ev/card-mut.log`, `ev/card-head.log`).
  - Every mutant was killed by the check the body names.
- Step 2, finder's harness: the `wood-plant` arm of `r10_sav_wood_reference.py`, run in real worktrees at both ends.
  - Base 0a8033305: `RESULT wood_plant_error_m0.8: mean +0.00 %`, `m1.0: mean +0.00 %`, `m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`. The no-fire m 0.8 row reads `calibration 1.0 error +25.00 %`.
  - Head: m 0.8, 1.0 and 1.2 all read `mean +0.00 % ... sd 0.00 over 9 fires`. The no-fire m 0.8 row reads `calibration 0.8 (wood_free) error +0.00 %`.
  - These match the body (`ev/h_base_woodplant.log`, `ev/h_head_woodplant.log`).
- Step 3, null controls:
  - At the head, `--no-wood-flag wood-plant` reproduces the base's RESULT lines exactly, including `+25.00 %` at m 0.8 and `-1.95 %` at m 1.2, with basis `wood_floor` (`ev/h_head_nowoodflag.log`).
  - The flat pct at m 1.0 and m 1.2 is the same at both ends: 7.588885569166417 and 7.593865152873221.
- Fixer's `meter-floor` arm at the head (`ev/h_head_meterfloor.log`):
  - All closed-loop and wood-plant rows published, with the body's percentages: valve-flat 0.556, valve-vary 25.264, wood-unforeseen 39.802, wood-cold 0.467, wood-full 92.987, wood-fire 37.371, wood-stale 4.070, wood-coast 19.336.
  - Zeroed reference: withheld. Check dropped: published. Under `MIN_CALIBRATION_KWH`: published.
  - Immersion booked over metered: 0.696, 0.522, 0.417, 0.348, read False, False, True, True. The run ends `meter-floor: SOUND`, rc 0.
  - The body's "about 1.1 times" re-derives. Pump kWh is 207.77 − 69.26 = 138.5. The floor is crossed at 289.1 kWh metered, so the immersion is 150.6 kWh, 1.09× the pump's.
- Step 6, class seams: `git grep -n "savings_sek\|savings_pct" custom_components/` returns `ledger.py`, `notifier.py`, `payload.py`, `sensor.py` and the card.
  - The card's `headline.savings_pct` hit, `headlineHtml`, reads the plan's `_plan_predicted_savings` sensor, not a ledger row. So it is outside the class.
  - No seam is open.
- Step 14, ratchet:
  - `python3 tests/structure.py` at main 0a8033305 reads `max_class_loc=7932`, `class_excess_loc=17557`, `duplication_copies=10`. At the head it reads 7931, 17554 and 9, and prints `STRUCTURE RATCHET PASSED` (`ev/struct-*.log`).
  - The −1 in f1156e41e is this PR's coordinator delta: the `interval_h` fold is −3 lines and `wood_heated` is +2.
  - Every budget moves down only, and `budget-raise-gate` is green.
- Step 10, forward-carry: both `## Forward-carry` items are `dismissed:` with reasons, and the packet's carry_audit reads `2 routed, 0 unrouted`. `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md` lines 283-285 mark the 2026-11 figure unverified, as the body says.
- Step 11, red checks:
  - `merge_train.py classify c84a5fb19 --pr 3360` read WAIT from 07:40 and then `GREEN ... pending: none red: none`, rc 0, at 08:26:12Z (`ev/poll.log`).
  - Red at this head: `gate` 129036742473 (07:34:53Z, `FAIL run(s) [42579916122] at this head are still being judged`). That is a deferral. All three runs' `gate` jobs were later re-run and concluded success.
  - Also red: `governance / delivery-status` 129036125604. It is not in `merge_train.py owed-reds`.
  - `pr-contract / pr-contract` 129053606418 started at 08:21:17Z, after the last red concluded, and concluded success. That run is the evidence that the body answers the earlier heads' reds (`tests / mutation`, `mutation-autofix`, `typing_ruler`, `stress.py`).
  - Every owed-reds context is success at this head.
- Heavy CI lanes cited, not re-run: `tests / fast (3.14)`, `closures`, `coverage`, `replay`, `browser`, `typing`, `mutation`, `arch-score` and `codeql` all concluded success at this head.
- Figures not re-derived:
  - The `wood-unforeseen` base value 40.417. I ran only the head's `meter-floor` arm, which reads 39.802.
  - The body's stress-probe counts. The first review found them refuted at the base: the bimodal probe is pre-existing. CI's stress run is green at this head.
