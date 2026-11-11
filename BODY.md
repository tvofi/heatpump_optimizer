R10-OUTSIDE-DISINFECTION-SETPOINT, built on outside pull request #3439 (Bankaifan, fork head f9a7bcb4ee; adopted as feeb0b6b39 with the author kept and the tool trailers dropped by the ref_privacy.py guard's attribution classes). With Pump duty control writing the hot-water set-point, a disinfection cycle wrote the everyday set-point (stock pair 55/60: 55.0 on a booked and on a held step), so the pump's own thermostat ended the cycle below its target; and the set-point repair stood permanently against the arbiter's own 55, its Fix (60) rewritten to 55 at the next step.

The rule for a cycle's temperature now has one owner on `ThermalParameters`: `dhw_disinfection_temp` (the disinfection temperature where #3398's `legionella_cycle_active` holds, else `None`: the one cycle predicate) and `dhw_cycle_temp` (the higher of the everyday set-point and that). `dhw_hard_max_temp` and the repair's `_dhw_floor` read them instead of each restating the predicate and the max. The arbiter decides when (`_dhw_write`: the step's action books `dhw_reason` legionella, or `disinfecting` holds) and every row of `desired` that writes hot water takes that one answer; the cycle's target is written on the entity's step at or below the tank's hard maximum (`dhw_hard_max_temp`: the cycle's temperature capped at 70 °C) and bounded by its range (above the range is left to the guard's unreachable notice). `dhw_gated` is generalised from "the arbiter's gate, below the everyday set-point" to "the arbiter's own write, still as written": a record exists only while the arbiter controls the pump (`_forget` clears it when Control is left), so an install where the arbiter writes nothing keeps the repair unchanged.

Alternatives not taken: the contributor's private helper computing the max inside the arbiter (a third copy of the expression the ceiling and the floor already held); a special case in the repair for the cycle (the brief asks the existing exemption to generalise, and a special case would restate the arbiter's when-rule in a second module); folding the repair's floor onto `dhw_cycle_temp` (changes the repair on an install whose everyday set-point is above the disinfection temperature with the pump reading between them, which the null controls forbid).

Repair for the blocked verdict at 0aed6ccb (null-control-leak): `8da43a2f` routed every cycle write through the round-up, so an off-step everyday set-point above the disinfection temperature was written a step above itself (everyday 57, disinfection 50, step 5: 60, where 49a45dd8 and the no-cycle row write 55), above `dhw_hard_max_temp` 57; and `feeb0b6b`'s round-up already did the same for an off-step disinfection temperature above the everyday set-point (60.3 at step 1: 61). `de817c3a` bounds the cycle's write by the hard maximum through `_bounded`'s existing ceiling (`hi=`, rounded down onto the step, in the entity's own unit): no cycle write exceeds it, every row where 49a45dd8 stayed within it is unchanged, and the no-cycle write is untouched. This reverses `8da43a2f`'s row (everyday 60.4, disinfection 60.2, step 1: 60 again, 49a45dd8's value): the only on-step values are 60, below the disinfection temperature, and 61, above the hard maximum, and the hard maximum wins. Alternatives not taken: restoring `cycle <= everyday` (keeps 49a45dd8's nearest step, which writes 60 over a hard maximum of 58 at everyday 58, step 5); a ceiling at `dhw_cycle_temp` (drops the 70 °C cap, mutant M13); rounding down without the ceiling (a second statement of the cap, which `dhw_hard_max_temp` owns).

`dhw_target_temperature` (`optimizer.py` predictive_info, copied onto every step's action) is left the everyday set-point: it is published beside `dhw_min_temperature` as the configured target, no production code reads it to act (`git grep -n dhw_target_temperature -- custom_components`: the optimizer's two writes, the sensor attribute, the payload type), and a cycle step already says so through its `dhw_reason` legionella; moving it would move every golden fixture that records it for a label change.

The space-only gate row (`DHW_GATE_C`) stays a gate on a step the plan booked for a cycle only when a block removed hot water from it; a held cycle turns a space step into Heating + DHW, whose write is the cycle's temperature (pinned).

## Head

f4ae78eb64bf6ecb7add66138b1b13e82f319c4b, on the PR head 0aed6ccb (three commits: `7c004817` the failing checks and the harness's `--grid`, `de817c3a` the fix, `f4ae78eb` the ledger pin; the figures were taken at de817c3a, whose tree differs from the head only under `tests/mutation_ledger/`); merge base cbd23f1c8b; origin/main's tip 0e28afd38b at 2026-11-11T15:34:37Z (`date -u`), `git merge-tree --write-tree origin/main HEAD` clean.

## Merge resolution (delta from 1713468b)

`git merge origin/main` at 1713468b conflicted in three files against #3398 (R10-COMBI-TANK-PR-B), which replaced the readers' `dhw_legionella_enabled` with `ThermalParameters.legionella_cycle_active` (enabled, and not an active combi store at or under `COMBI_LEGIONELLA_POTABLE_LIMIT_L` unless forced). Each hunk keeps both behaviours:

- `thermal_model.py` `dhw_hard_max_temp`: this group's form (`min(70.0, dhw_setpoint if dhw_cycle_temp is None else dhw_cycle_temp)`), and `dhw_disinfection_temp` now reads `legionella_cycle_active` where it read `dhw_legionella_enabled`. Main's `if self.legionella_cycle_active: top = max(top, dhw_legionella_temp)` is that expression through the owner, so main's ceiling is unchanged and #3398's gating now reaches the arbiter's write and the repair too.
- `setpoint_check.py` `_dhw_floor`: this group's form (`max(floor, dhw_disinfection_temp)` where not `None`), equal to main's `legionella_cycle_active` branch through the same owner.
- `tests/features.py`, three fakes (`_p8_setpoint`, `_pa_mbs._thermal_params`, the `_df_sc.evaluate` space-slot check): this group's real `ThermalParameters` (`_r9f12_tp`), from which `legionella_cycle_active` derives (combi off by default, so equal to the flag); main's namespace fakes carried `legionella_cycle_active` by hand and no `dhw_disinfection_temp`.

Commits after the merge: `b8736ad3` adds a `tests/block_duty.py` check on an active combi store holding 2 L (forced and unforced, over the three cycle bookings), retargets M7's anchor to the merged line and adds M10; `1aa850c2` records `class_excess_loc` down (main's own reduction under this branch's recorded budget); `49a45dd8` deletes #3398's two `killed_by` pins on the rewritten lines (`_dhw_floor` GUARD_OFF ea9e613f, `dhw_hard_max_temp` GUARD_OFF f3c560aa), which `ci_predict.py` named STALE PIN.

## Mutation proof

`python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` (this PR): each mutant applied to a detached worktree of HEAD, `tests/block_duty.py` run there, worktree removed; exit 0 only when NULL survives and every other mutant is killed. Exit 0 at de817c3a; killed:

- `NULL` (no change): survives, 66 of 66 checks pass.
- `M2-round-up` (`_dhw_write`: 0aed6ccb's `rounding="up"` in place of the hard-maximum ceiling, the verdict's defect): killed by "an off-step disinfection temperature above the everyday set-point is written on the step at or below it, never above the tank's hard maximum", "a cycle whose temperature is an off-step everyday set-point (the disinfection temperature at or below it) writes the step at or below it, as 49a45dd8 and the same install's everyday step do" and three more, the census "no cycle write exceeds the tank's hard maximum, over every step size and the disinfection temperature below, at and above the everyday set-point, on and off the step" among them.
- `M12-no-hard-max` (`_dhw_write`: drop `hi=`, the nearest step): killed by "an everyday set-point the nearest step rounds up is held below it on a cycle: the tank's hard maximum is the everyday set-point there (the everyday step's own nearest write is main's)", "a disinfection temperature above 70 degC is written at the tank's 70 degC hard maximum" and the census.
- `M13-cap-cycle-not-hard-max` (`hi=float(cycle)`): killed by "a disinfection temperature above 70 degC is written at the tank's 70 degC hard maximum" and the census.
- `M11-everyday-cycle-nearest` (`_dhw_write`: restore `or cycle <= float(inp.params.dhw_setpoint)`, 49a45dd8's routing): killed by "an everyday set-point the nearest step rounds up is held below it on a cycle ..." and the census.
- `M1-no-cycle-write`, `M3-booking-ignored`, `M4-hold-ignored`, `M5-gate-only-excuse`, `M6-excuse-any-reading`, `M7-flag-ignored`, `M10-enabled-not-active`, `M8-cycle-not-max`, `M9-floor-no-disinfection`: killed as before, each by the checks the runner prints (M1 by ten, among them "a commanded or held disinfection cycle writes its temperature, not the configured set-point").

Failing first: `tests/block_duty.py` at `7c004817` (0aed6ccb's production code) fails 5 of 66, the five checks above, the census printing 407 of 780 rows over the hard maximum; at de817c3a 66 of 66 pass, the census at 0.

## Null control

`dev/audit/harnesses/r10_disinfection_setpoint.py` (this PR, sha1 a05019506dfb2250252af943cf784ef436083783) copied over worktrees of origin/main cbd23f1c, 49a45dd8 and 0aed6ccb and run there and at de817c3a, default mode and `--grid`:

- `diff <(grep '^null_' base) <(grep '^null_' head) >/dev/null && echo IDENTICAL || echo DIFFER` printed IDENTICAL against each of the three bases over the 80 `null_*` lines (the cycle disabled, an everyday set-point at 60 and above 62 the disinfection temperature, no entity).
- The same over the 780 `--grid` lines with `cycle=0` (every step and pair, the everyday write): IDENTICAL against each base. Had the fix leaked into the no-cycle write, those lines would differ.
- Against 49a45dd8, 284 of the 780 `cycle=1` grid lines differ, and every one of the 284 is `over=1` at 49a45dd8; no `over=1` line of 49a45dd8 is unchanged at the head. So the head departs from 49a45dd8 exactly where 49a45dd8 wrote above the hard maximum, and nowhere else.
- The default mode's `offstep` install (disinfection 60.3, step 1) changes 14 lines against 0aed6ccb, write 61.0 to 60.0; its `repair_none` (the repair on an install whose arbiter wrote nothing, reading 60) now fixes to 61, while `repair_own` stays `-`: the arbiter's own write is excused by `dhw_gated` as before.

## Figures

Taken at de817c3a against merge base cbd23f1c (origin/main 0e28afd38b at 2026-11-11T15:34:37Z).

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ran them: `1 TEST SCRIPT(S) FAILED`, `tests/features.py` alone, 1 of 5237, the combi_type_branch census inherited from origin/main (`## Red checks`); every other script green. `tests/block_duty.py` 66 of 66. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0023 IMPROVES`.
- Census (`python3 dev/audit/harnesses/r10_disinfection_setpoint.py --grid`, `grep -c over=1` over its `cycle=1` and `cycle=0` lines): 780 cycle rows (5 steps x 12 everyday set-points x 13 disinfection temperatures) and 780 no-cycle rows. Cycle rows over the hard maximum: origin/main 64, 49a45dd8 284, 0aed6ccb 407, de817c3a 0. No-cycle rows over it: 104 at every one of the four (`## Forward-carry`).
- Credit cost of the hard maximum, from the same grid lines, over cycle rows with the disinfection temperature above the everyday set-point and at most 70 °C (330): writes below the guard's instant-credit threshold (`legionella.py`, disinfection temperature less 1.0) 34 at de817c3a, 0 at 49a45dd8, 265 at origin/main; below the hold-verified threshold (less 0.5) 71, 0, 286. By step (the same lines, grouped): instant 10 at step 2 and 24 at step 5; hold-only 18 at step 1, 11 at step 2, 8 at step 5; none at 0.1 or 0.5. Main writes the everyday set-point there. `## Forward-carry`.
- Class seams (`fixer.md` step 8). Rule: every rounding path `_dhw_write` takes, enumerated by the census above (each step size 0.1, 0.5, 1, 2, 5; the disinfection temperature below, at and above the everyday set-point; on and off the step; at, near and past the 70 °C cap and the entity's maximum), its precondition asserted in `_cycle_grid_over_hard_max` (all three orderings present); and `git grep -n '"dhw_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py` (every hot-water write of the arbiter). Dispositions:
  - `_dhw_write` cycle branch: closed in this diff, census at 0.
  - `_dhw_write` no-cycle branch (nearest step of the everyday set-point): 104 census rows above the hard maximum, identical at origin/main; outside this diff and held unchanged by the brief: `## Forward-carry`.
  - the space-only gate row (`DHW_GATE_C`, rounded down): `DHW_GATE_C` 30 °C rounded down, a gate rather than a cycle write, and below every hard maximum the census reaches (its lowest everyday set-point is 50); not a rounding path of the cycle, left as is.
  - `thermal_model.py`, `setpoint_check.py`, `dhw_planner.py`, `legionella.py`, `coordinator.py` readers of the cycle's predicate and temperature: unchanged since cb7f294a's dispositions (`git diff 0aed6ccb HEAD --stat` touches none).
- Mutants: `## Mutation proof`.

## Unpinned sites

None left: `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/block_duty.py,tests/guard_pins.py,tests/env_drift.py` at de817c3a printed `PIN KILLED: 1 pinned, 0 left unpinned` (`pump_arbiter.py` `_dhw_write` RETURN_DEL, the rewritten return, killed by `tests/block_duty.py`; the null control `pump_arbiter.py:194 NULL_COMMENT` survived), and `f4ae78eb` commits it beside the deletion of the stale pin on 0aed6ccb's line (RETURN_DEL e7e1a636), which `ci_predict.py` named STALE PIN. The other nine pins of cb7f294a stand.

## Red checks

Each in `python3 tools/audit/seat/merge_train.py owed-reds`' set:

- `tests / fast (3.14)`: red on `tests/features.py`, 1 of 5237: "combi_type_branch census ... no product or vendor name in the package's Python", inherited from origin/main since #3398, hotfix in flight as #3466; each hit is a `Luxtronik` comment present at main, none in this diff's hunks. No commit of this branch turned it red: no root-cause answer is this branch's.
- `tests / mutation`: red at d2ab2743 on 11 added unpinned sites, repaired in `8da43a2f` and `cb7f294a`. The cheaper detector exists: `tools/pr/ci_predict.py` (prepr.sh step 6d) listed all 11 locally before that handoff at no standing cost beyond the prepr run every seat makes; the miss was the seat's (state (b)): no further countermeasure.

`governance / instrument-self-tests` is red on main (R10-HOTFIX-PUSHER-CENSUS) and outside the owed set: neither answered nor a block here.

## Forward-carry

- The no-cycle write rounds an off-step everyday set-point to the nearest step, which can exceed `dhw_hard_max_temp` (everyday 58, step 5: 60): 104 of 780 census rows at origin/main and at this head alike; this repair's brief holds that row unchanged from 49a45dd8, so the ceiling there is the orchestrator's call. Control: `--grid`'s `cycle=0` lines, `grep -c over=1`. Carry: R10-OUTSIDE-DISINFECTION-SETPOINT
- Bounding a cycle by the hard maximum leaves an off-step disinfection temperature above the everyday set-point a step short of the legionella guard's credit thresholds on coarse steps (34 of 330 rows under the instant rule, 71 under the hold rule; 0 at 49a45dd8, which wrote above the hard maximum instead; 265 and 286 at origin/main). Whether the hard maximum should rise to the step above the disinfection temperature is a ruling on `dhw_hard_max_temp`, outside this repair. Control: the same grid lines against `legionella.py`'s thresholds. Carry: R10-OUTSIDE-DISINFECTION-SETPOINT

R10-OUTSIDE-DISINFECTION-SETPOINT Carry 1 landed on the roster at 2ad7130319 (origin/handoff/audit-r10-roster).

R10-OUTSIDE-DISINFECTION-SETPOINT Carry 2 landed on the roster at ff4fefa44e (origin/handoff/audit-r10-roster).

## Friction

none
