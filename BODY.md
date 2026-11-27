R11-SEAM-learners part 2 of 3: carries 5-9. Carries 6-9 port draw-map part B (archive/handoff/r10-draw-map-evidence-b 8c1508d9c1, its own diff cc335482ae..59cbdccb57) onto main: the power-response sweep armed only by its own button (owner ruling S1, flat price allowed), the ceiling row's source cell, the probe-only clock reader `DrawRange.probe_since` (r14), and the ceiling probe armed ahead of an unconverged fit where the pump's top is unlearned (S3, [CE] 2). Carry 5's measurement and its destination are under `## Forward-carry`.

Port conflicts resolved against main: the press is `arm_system_identification(sweep=...)`, synchronous and answering its refusal (D10-s1-02), so the sweep button reuses the system-identification button's press through a class flag instead of its own; `SystemIdentification.arm` keeps ADR-003's keyword-only `enabled` beside part B's `sweep`; the ceiling store's cells keep their whole-row refusal (`_DRAW_ROW`), the third cell included; `fold` keeps `ceiling_frozen` (D2-s3-09) around the sourced `observe_ceiling`; `_map_inputs` keeps main's high-limit top with part B's held sweep floor.

By carry:
- Carry 5: the m5_tankfall harness gains the `draw_then_charge` null arm; the measurement and its destination are under `## Forward-carry`.
- Carry 6: [CE] 2 built: `sysid.armable` arms the ceiling probe ahead of an unconverged fit where the store holds no learned top and the probe's clock allows, its armed result naming why (the part B block's [CE] 2 checks).
- Carry 7: owner rulings S1 and S3 built: the sweep arms on a flat price, its armed reason the upper cost bound (levels x 30 minutes x band top) and the metered energy in `last_sweep`; the probe-only clock reader is `DrawRange.probe_since` (r14), the learned-top lapse and the solve band keep `ceiling_since`.
- Carry 8: the routing invariant lives in `draw_range.fold` (`elif not sweep`), and its null mutant fails five checks (`## Mutation proof`).
- Carry 9: the r17 comparison is the `night` arm's `r17` row of `dev/audit/harnesses/draw_map_sweep.py` (`## Figures`).

## Head

`6dc6156688fef4bb12aca93c618bd10b5ed54df1` merges main `43ec8e3` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`2e97faf4c1d23d6ab0dd1013efa6d68d1a7dbf0d` merges the authored code head `427285fdbe9a6879f24401e881785274e40d5d95` and then merges origin/main `e84856520d` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`685c36d4f9e13fb8b34b74ce3e608ad667350baa` merges the authored code head `427285fdbe9a6879f24401e881785274e40d5d95` and then merges origin/main `e84856520d` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`cfae1f3aa3d92f0c7bdd927b07b1651617e6ecba` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

ad02493c1b76bcec94b3eca6b2d7ca155ab16ae3, merge base 7194ff84c09dd9d54a99f8208c906136981fd9dc (origin/main at measurement, 2026-11-27T00:57Z).
- Merge of origin/main at handoff/r11-merge-3933; conflicts resolved: tests/closures.json and tests/structure_budgets.json (ledger driver).

## Mutation proof

Carry 8's null mutant, `draw_range.fold`'s sweep exclusion `elif not sweep:` turned to `else:` (a sweep interval reaches `DrawRange.observe`), run as `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("<emitted prelude>").read())' "# --- R10-DRAW-MAP-EVIDENCE part B (design" 'R.section("Room history and the identifiability report")'` (prelude from `--emit-prelude` on the same block): exit 1, failing
- the routing invariant (draw_range.fold, the one place): a sweep's interval below the band top reaches no window, no idle reading and no ceiling row; at the band top it is a ceiling row marked sweep
- a sweep's band-top interval is ceiling evidence only by the probe's own rule
- the flag is the interval's: the fold reads and clears it, so the first plan interval after a sweep reaches the window again
- where the night's draws went: the band-top level is the one ceiling row, marked sweep, and the probe's clock is unmoved
- null: the window after the sweep night holds only its plan intervals

Restored: the block passes, 70 checks. The remaining added lines are drawn by `prepr.sh`'s mutant step (`MUTANT_CMD` the same block call); its survivors are listed under `## Unpinned sites` where any remain.

## Null control

At the merge base the part B block cannot run (no `sweep_levels_kw`, `KIND_SWEEP`, `PowerResponseSweepButton`, `probe_since` or `SOURCE_SWEEP` exists). The window null is the block's own last check above: the window after a sweep night equals a window fed its four plan intervals alone. Carry 5's null is the harness arm `draw_then_charge` (a real 4 K draw, then the charge it triggers).

## Figures

- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/rounds/round11/D2/s3/m5_tankfall.py`, at the base and the head: `booked_kwh_unplanned_max` equal at both ends (the full 4 K dip of the largest store, booked as a draw), `booked_kwh_long_max` and `booked_kwh_short_max` zero at both ends; at the head `booked_kwh_draw_then_charge_max` equals the unplanned figure and `unplanned_inputs_equal_draw_then_charge=True` (the rows the learner reads, per store, compared with `==`; the null that would have shown a difference is any row of the two traces differing).
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/draw_map_sweep.py`, its `night` arm: the r17 row (carry 9) prints the ceiling store's band-top sample beside the map row's steady-minute `drawn_mean_kw` for the same level, equal to float rounding (the store takes the interval's closing meter reading); the routing row prints the window's plan intervals against the plan-only night's and `sources=['sweep']` for the one ceiling row, `probe_since=None`.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: every check passes at the head.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`, `MODE: SCOPED`; every script `scope.run` names was run at the head with `PYTHONPATH=tests/hastub` (the two `.mjs` under `node`) and exits 0. `tests/entities.py`'s `a*:`/`hb:` FAIL lines are its own negative arms and print alike at the merge base.
- `python3 tests/structure.py`: `module_excess_loc` re-recorded upward (see `## Raise justification`); every other row at or under its budget.
- `python3 tools/audit/archscore/score.py --diff origin/main`: see `## Architecture score`.

## Architecture score

Architecture score: dS +0.0006 IMPROVES (`coord_footprint` down by one: the experiment's override action is built in `sysid.override_action`, not inline in the coordinator).

## Raise justification

`module_excess_loc` rises by the lines part B adds to `sysid.py` and `pump_arbiter.py`, both past `MODULE_LOC_LIMIT` at the base; `draw_range.py`, under it, costs nothing. Raised under mandate 6893738184 (scope all, in force until 2026-12-15); the reason is in the re-record commit's message.

Architecture score: dS +0.0006 IMPROVES (the port with the raise, `score.py --diff origin/main`).

Payments tried: three, one measured and reverted; each below.
- the sweep's levels, constants and arm refusal moved to a new pure module beside `sysid.py`: dS +0.0006, unchanged from the port, 40 of the lines paid, and `unloaded_package_imports` rose by one; reverted. The rest of the sweep (`sweep_level_count`, `_begin_bounded`, `_sweep_level`, `sweep_hold_reason`, `_may_start`) reads the experiment's phase, comfort predictor and `_finish`, so moving it reads `sysid` privates across a module boundary: a mechanical split, refused by `fixer.md` step 17.
- `pump_arbiter.py`'s additions (the held sweep floor, the experiment's duty, `sweep_band_k`) are the actuator write's own: the write's module owns them.
- no dead code in either module's touched spans was found to delete; the port itself shares `_whole_bound` between the probe and the sweep and folds the night-window and price tests of `conditions_met` into `_hour_price_refusal`, which the sweep's level boundary also reads.

## Red checks

Red at head `6dc61566` (`gh pr checks 3933`, run 46028669224).

- `budget-raise-gate / budget-raise-gate`: refused, `REFUSED: tvofi's approval is on 2e97faf4c1d2, not this head 6dc6156688fe`. The `module_excess_loc` raise (21607 -> 21972) in `tests/structure_budgets.json` is justified under `## Raise justification` with its `Architecture score: dS` line; the gate wants the approving review re-posted at this head. Not repairable in code.
- `tests / mutation`: `MUTATION TABLE REFUSED` on three stale dispositions. Two are this diff's: sysid.py `conditions_met` GUARD_OFF fa6ac820 and RETURN_DEL f2ae865e name lines the diff removed; repair commit cb3915f98ecb removes the two ledger files (branch handoff/r11-repair-3933b). The third, flow_lift.py `FlowCurveBias.observe_temps` BOOLOP 04143c3f, is inherited from main and fixed by #3939; no repair here. The added unpinned sites remain for `mutation-autofix` (`mutation-pins` queued, unmeasured).
- `gate`: follows the two above.
- `tests / nightly-status`: reports the scheduled nightly, outside the owed set.

Earlier heads:

Red at head `cfae1f3a` (`gh pr checks 3933`); the logs of the still-running run 45937118637 are not yet readable, so the failing line is the job annotation `Process completed with exit code 1.`

- `budget-raise-gate / budget-raise-gate`: failed at `cfae1f3a`. Red by construction while the `module_excess_loc` raise in `tests/structure_budgets.json` awaits an approving review that cites mandate 6893738184 (`## Raise justification`). The cheaper detector is `tests/structure.py`, which printed the raise locally before the re-record; the gate is the deliberate refusal of an unreviewed raise and clears on that review, not on code.
- `governance / instrument-self-tests`: failed at `cfae1f3a` with `Process completed with exit code 1.` This diff touches no instrument under `tools/`. The failure is the D5 canary, which is cured by merging main; the code head `427285fd` merges main.
- `tests / mutation`: failed at `cfae1f3a` with `Process completed with exit code 1.` Red by construction on the 114 site(s) under `

## Unpinned sites`; `mutation-autofix` pins the killed sites after the push, and `tools/pr/ci_predict.py` (a `prepr.sh` step) named them before the handoff.
- `tests / nightly-status`: failed with `Process completed with exit code 1.` It reports the scheduled nightly on main, not this diff, and is outside the owed set.
- `gate` is red only because it follows `budget-raise-gate` and `tests / mutation`.

## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Unpinned sites

Each is a `custom_components/` site the diff adds, in `mutation-autofix`'s lane: pinned by `mutation-autofix` after the push. None of the diff's first 40 mutants survived the part B block (`prepr.sh`'s diff-mutants step).

- `custom_components/heatpump_optimizer/draw_range.py:1011 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1061 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1063 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1063 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1065 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1070 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:267 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:300 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:300 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:300 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:302 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:303 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:306 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:308 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:308 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:319 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:321 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:327 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:327 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:327 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:329 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:331 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:342 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:347 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:352 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:366 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:370 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:370 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:375 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:378 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:382 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:495 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:803 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:804 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:804 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1348 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1364 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1366 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1379 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1381 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1388 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1390 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1491 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1493 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1500 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1500 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:652 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:120 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:123 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1340 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1343 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1343 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1346 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1375 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1379 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1390 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1398 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1400 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1400 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1418 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1420 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1431 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1431 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1464 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1469 CMP_BOUND*2`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1471 CMP_BOUND*2`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1471 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1476 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1478 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1488 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1491 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1491 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1491 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1493 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1493 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1493 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1508 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1508 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1510 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1510 CMP_BOUND*2`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1510 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1513 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1528 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1531 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1533 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1533 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1545 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1546 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1561 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1564 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1564 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1581 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1585 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1591 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1595 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1597 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1618 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1620 CLAMP_DROP*2`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1621 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1621 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1624 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1626 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1631 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1680 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1796 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1802 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1802 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1873 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1965 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:1966 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:2100 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:2116 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:2123 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:2813 GUARD_OFF`: mutation-autofix

## Forward-carry

- Carry 5 (D2-s3-08's unflagged-charge arm): measured, not built. On the harness's 10-minute trace the learner's whole input (time, reading, plan flag) is identical for the pump's own unflagged charge with its start dip and for a real draw that triggers the charge (`unplanned_inputs_equal_draw_then_charge=True`, and both book the same energy), so no rule over `DhwProfileLearner`'s input books one and not the other: the triggering-draw rule the carry asks for needs an input the learner does not receive, the charge's delivered heat (the heat counter's span, `heat_energy`) set against the tank's net rise, or the pump's own hot-water flag. Precondition for the stage: a design revision choosing that input and what an install without it books; the harness's `draw_then_charge` arm is its null control, re-run at its own merge base. Routed to the group whose design models a hot-water charge as a run, which is where an unflagged charge's delivered heat would be read (#3769's stage). Carry: R11-OUTSIDE-HONEST-DHW-RUNS
- Carry 6's owner-data figure (`dev/audit/harnesses/draw_map_linearity.py --bundle`'s `experiment_cycles`, `ceiling_store_rows`) stays unmeasured: the owner's bundle is not in the tree. The mechanism it measured is closed here by [CE] 2's checks (an unconverged install with an unlearned top arms the probe first). Carry: dismissed: needs the owner's bundle, which no seat holds; the mechanism's checks are in the part B block

## Friction

none

