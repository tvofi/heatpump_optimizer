Fix review: blocked 3560b69668e171c91cac0fbcf1db35490795306e harness: design-trace-missing tank floor outside a demand window

bus-nonce: 33445b77605f0bebf8e301aeaa70de19

Round 1. No earlier Fix review on this pull request, so the verdict covers the fix and the merge of `aedd50be` with `origin/main` `f07cd253`. Measured `3560b69668e171c91cac0fbcf1db35490795306e`. Evidence: `/Users/timmalmstrom/hpo-seats/r9-sw-5-review-3560/evidence`.

## Block

#1926 requires the tank floor only while the tank is inside a demand window. `boost.py` `_dhw_floor` conjoins `float(temp) <= float(floor)` with `_window_open`. Deleting `and _window_open(snap, now)` left `PYTHONPATH=tests/hastub python3 tests/block_duty.py` at rc 0, `ALL 45 BLOCK DUTY CHECKS PASSED`. Under that mutant a 45 °C tank, minimum 45 °C, windows `00:00-01:00`, at 12:00 returned `the tank is at its minimum inside a demand window`. Restored, the same call returns None. The release fixtures use `00:00-23:59` (`tests/block_duty.py`, `tests/features.py`). The empty-window fixture is paired with a tank above the floor (`dhw_temperature=50`, `dhw_min_temp=40`), so it does not pin the clause. tvofi did not waive the window. The production line was restored; `action["power"] = 0.0` and the `_window_open` conjunction are the tree at this head.

## Named mutation

`action["power"] = 0.0` replaced with `action["power"] = action["power"]`. `tests/block_duty.py` rc 1: `FAIL a space block zeroes space power and not the supply switch` and `FAIL a space block does not invent power_normalized`, `2 of 45 BLOCK DUTY CHECKS FAILED`. A slice of `tests/features.py` through that check printed `FAIL a space block zeroes space power and leaves the supply switch and DHW alone` with `'power': 1.2`, and `ok` for `with no block set the overlay adds no key and changes no value`. Restored.

## Resolution

`git merge-tree --write-tree origin/main 3560b69668e171c91cac0fbcf1db35490795306e` exited 0 with no `MERGE-CLAIM` line. `origin/main` at measurement was `1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872`. The resolved docs keep 60 sensors, including Model Restart Advisor, and 6 switches. `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py`: `RESULT claims_true=123 claims` and `RESULT claims_false=0 claims`. Committed C1 is documented=78 measured=78, C2 sensors 60, C5 is 78 entities / 60 sensors / 6 binary sensors / 4 buttons / 6 switches / 1 climate / 1 datetime. The three-dot diff does not contain `coordinator.py` or `tests/structure_budgets.json`. `PYTHONPATH=tests/hastub python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

## Harness

No committed finder harness. The issue names the tests to add. `tests/block_duty.py` is the fixer's driver; the body says so. `class BlockDhwSwitch` is absent at `f07cd253` and present in `switch.py` at this head. At this head `tests/block_duty.py` printed `ALL 45 BLOCK DUTY CHECKS PASSED`.

`tests/features.py` `a due anti-legionella cycle releases the block before the overlay zeroes it` sets the block at 2026-07-01. `apply` calls `expire` at the wall clock, so a far due of 100 h on a warm tank also leaves `dhw_power` 0.5 and drops the block. `tests/block_duty.py` sets the block at `dt_util.now()`: due 100 h keeps the block and sets `dhw_power` 0.0; due 1 h drops the block and leaves `dhw_power` 0.5.

`adopt_plan` of `power` 1.2, then a live space block, then `apply`: the stored base stayed the same object and the same values; the copy's power was 0.0 and `heat_pump_on` stayed true.

The body names no enumeration command. The list run here is #1926's release conditions. Legionella due and overdue, a disinfection hold, the room floor, the cold-rail lease, system identification, and a stale plan each have a failing direction in `tests/block_duty.py`. The tank floor's window restriction does not.

`due_in_hours` is rounded to 0.1 h. Remaining 23.96 publishes 24.0, and `24.0 < 24` is false, while `floor(23.96/0.25) = 95 < 96`, so the planner places the cycle. The brief names `due_in_hours` as the input.

## Figures re-derived at this head

- `tests/block_duty.py` — `ALL 45 BLOCK DUTY CHECKS PASSED`
- `tests/ha_floor.py check` — `RESULT checked=147 missing=0 unrecorded=0 undecidable=0`
- `tests/env_drift.py --all f07cd253c52f1012427d9869a808f1df39dafb93` — `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`
- `tests/closure.py select --diff f07cd253` — `MODE: SCOPED -- 22 script(s) run, 10 scoped out`
- three-dot diff of `VERSION`, the manifest `version`, and the `RELEASE_NOTES.md` heading is empty
- both claim files are absent from the three-dot diff

Unverified here, left as the body's figures: entities 2190, the full features run, doc_claims 160, harness_headers 105, boost_drift 43, plan_view, card, card_drift, unpinned 4698. The body's 21-script scope line is stamped to the code head before `tests/block_duty.py`.

## CI

Cited from this head's check-runs, not re-run. At the re-read before posting, `fast (3.14)`, `mutation`, `closures`, `coverage`, and Analyze (python) were `in_progress`. Completed success: `pr-contract`, `closure-scope`, `typing`, `browser`, `hassfest`, `validate-hacs`, `budget-raise-gate`, `policy-docs`, `briefs`. Completed failure: `nightly-status`, `delivery-status`.

`delivery-status` on run 37508826861 job 112424332787 printed `DELIVERY STATUS UNCHECKED — 39 rowed, 1 pending, 0 overdue` and `pending #2001`. The three-dot delivery path is `docs/delivery/1997.md`, this pull request's row. The body names `nightly-status` and `delivery-status`.

Completed failures in the range: `de8ccc657ccd9fe5acdcfc6b800d02d70c6ee9e5` and `6132233c4a1a8dc1fda61aa142624d1a4f8af38c` failed `mutation`, `mutation-autofix`, `delivery-status`, and `nightly-status`. The body names each and answers. `3301d6197d15cfbf58543f4af82fc7980c012996`, `b89154264a7eb6cca52d4605b902f4238d23240d`, and `aedd50be78debbf9d53a1599c1dfee616e2ed255` have zero check runs, so those heads are UNCHECKED. This head's `mutation` run had not finished.

## Carry

`## Forward-carry` is none. The window gap is this pull request's harness. The body head SHA is the SHA measured.
