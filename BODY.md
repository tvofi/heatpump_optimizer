R10-OUTSIDE-DISINFECTION-SETPOINT part 2, the round-down ruling (`dev/programme/triage/s6-batch226.md#P681`, ruling (1)): the no-cycle hot-water write never exceeds the charge limit `dhw_max_temp`, and the set-point repair's Fix never exceeds the hard maximum its row is judged against. Carry 0 (#3452's no-cycle ceiling item 7052beca) and Carry 2 (that ruling) are built here; Carry 1 (#3452's credit-threshold item 9ac8c410) moved to R10-DISINFECTION-STEP-NOTICE, which owns the ruling on `dhw_hard_max_temp`.

The no-cycle hot-water write (`pump_arbiter._dhw_write`) rounded an off-step everyday set-point to the nearest step, so it could hold the tank above the user's own charge limit for good (everyday 58, step 5: 60). It now goes through `_bounded`'s existing ceiling, `hi=` the parameters' `dhw_max_temp`, which `quantise_setpoint_c` rounds down onto the entity's step in the entity's own unit: no second statement of the cap. The ceiling is the charge limit, not `dhw_hard_max_temp`, which rises to the disinfection temperature while the cycle is enabled and not running (mutant M14 below).

Class seam, the set-point repair (`setpoint_check._dhw`): its Fix rounded the floor up with no ceiling (offstep install, disinfection 60.3, step 1: Fix 61 against a hard maximum of 60.3, which the arbiter writes back as 60, so the notice stood for good on an install whose arbiter writes nothing but whose user pressed Fix). The floor is now quantised once, up onto the step and never above `dhw_hard_max_temp` (`quantise_setpoint_c`'s `hi_c`, rounded down), and the reading is judged against that quantised floor, so a Fix never exceeds the ceiling its row is judged against and a pump at that step raises nothing. An on-step floor at or below the ceiling is unchanged: rounding up only moves an off-step floor, and a reading on the step at or above the floor is at or above its step-up.

A ceiling can now sit under the entity's own minimum (`tests/features.py`'s L2 row: everyday 3 °C on a climate entity whose minimum is 44.6 °F), where `quantise_setpoint_c` applies `hi_c` last and would write below the range the entity accepts. `_bounded`'s contract is a value inside the entity's range, so a caller's ceiling under the entity's minimum rounded up onto its step is dropped (the `hi` test in `_bounded`) and that minimum is written, as at the base (45 °F there). Two earlier forms were refused by their own checks and replaced: clamping the ceiling to the minimum (`4498df97`) rounded an off-step minimum down, under the range (44 °F, the L2 check); comparing the ceiling with the raw minimum (`ec29e0dd`) kept a ceiling between an off-step minimum and its step-up and rounded it under the range (30.6 over a 30.4 minimum, step 1: 30; mutant M20).

The ruling's `lo=` (the write at or above `dhw_min_temp` plus `DHW_MIN_TEMP_SETPOINT_MARGIN`) is not added: it cannot change any write. With `hi=` the everyday set-point (`dhw_max_temp` is `min(70, dhw_setpoint)`) and the value the everyday set-point, the nearest step is at or above the step-down of `hi`; where the step-up of `lo` is at or below the step-down of `hi`, the `max` with it is therefore a no-op, and where it is above, `quantise_setpoint_c` applies `hi_c` last and the ceiling wins. A `lo=` would be an always-surviving mutant. The ruling's alternative, reporting the rows where the two bounds leave no step, is taken: the harness's `below_floor` field (`## Figures`).

Alternatives not taken: `rounding="down"` with no `hi=` (a second statement of the cap that `dhw_max_temp` owns, and it would not hold a set-point above 70 at 70); `hi=dhw_hard_max_temp` (mutant M14: survives a census keyed on the hard maximum with the cycle disabled, counts 64 of the 104 rows with it enabled); for the repair, extending `dhw_gated` alone (covers an arbiter install, where the arbiter's own write is already excused, but not the Fix value above the ceiling on an install the arbiter does not write).

## Head

c5b48730d9063440e8df53a5a14928d9e96f0078 (the authored head 43095bdec3bba091bfe1a5a38abf172987e7ceb8 merged with origin/main 7617c7cf4a, conflict-free, review_carry.py CARRY), seven authored commits on origin/main ef579d9ba689 (`c9258994` the failing checks, `20d22eae` the fix with the harness and runner, `05a56e58` M11 retired, `4498df97` the entity-minimum clamp in `_bounded` and the test fakes, `ec29e0dd` that clamp replaced by dropping a ceiling under the minimum, `4342f022` the minimum taken on its step and the diff's survivors killed, `43095bde` the repair's redundant guard dropped and the killed sites pinned); merge base ef579d9ba689dcb48b0d4aa95222f1ce83d99c2d, origin/main's tip at 2026-11-12T03:33:29Z (`date -u`).

## Mutation proof

`python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` (each mutant applied to a detached worktree of HEAD, `tests/block_duty.py` run there; exit 0 only when NULL survives and every other mutant is killed), at 43095bde (exit 0), and at 20d22eae for M11:

- `NULL`: survives, 70 of 70 pass.
- `M14-limit-hard-max` (the no-cycle `hi=` set to `dhw_hard_max_temp`), `M15-limit-dropped` (`hi=` dropped: main's nearest step), `M16-limit-round-up` (`rounding="up"` in place of `hi=`): killed by "no no-cycle write exceeds the charge limit (dhw_max_temp), the cycle enabled and not running or disabled, ..." and "an off-step everyday set-point is written on the step at or below it, never rounded up ...".
- `M17-fix-uncapped` (`setpoint_check._dhw`: `hi_c` dropped, #2805's uncapped round-up) and `M18-active-raw-floor` (the reading judged against the unquantised floor): killed by "the hot-water repair's Fix never exceeds the tank's hard maximum it is judged against, ...".
- `M19-ceiling-under-min` (`_bounded`'s ceiling kept under the entity's minimum) and `M20-ceiling-under-raw-min` (compared with the raw minimum, not its step-up): killed by "a charge limit below the entity's minimum writes the entity's minimum, never a value it refuses" (that check also holds at the base, where no ceiling reached under the minimum).
- `prepr.sh`'s diff mutants (`MUTANT_CMD="python3 tests/block_duty.py"`) at ec29e0dd left three survivors, each now killed or removed: `pump_arbiter.py` `_bounded` CMP_BOUND (`>=` to `>`; killed by the same check's 72 °C everyday on a 70 °C minimum, whose ceiling sits exactly on the minimum's step); `setpoint_check.py` `_dhw` CMP_BOUND (`<` to `<=`; killed by a reading exactly one `MIXING_VALVE_WRITE_EPSILON` under the floor, in "the hot-water repair's Fix never exceeds ..."); `setpoint_check.py` CONST_SWAP on the Fix value's `round(..., 6)`, a line this diff no longer changes (the name `on_step_c` is kept).
- M1-M10, M12, M13 of part 1: killed as before.
- `M11-everyday-cycle-nearest` (route a cycle at or below the everyday set-point through the no-cycle return) SURVIVED at 20d22eae and is retired in `05a56e58` as equivalent: on those rows `dhw_cycle_temp` is the everyday set-point, so `dhw_hard_max_temp` equals `dhw_max_temp` and both returns are the same `_bounded` call.

Failing first: `PYTHONPATH=tests/hastub python3 tests/block_duty.py` at c9258994 (origin/main's production code) prints `4 of 69 BLOCK DUTY CHECKS FAILED`: the three checks above and part 1's "an everyday set-point the nearest step rounds up is held below it on a cycle ...", whose everyday-step conjunct pinned main's nearest write (58 on step 5: 60) and now asserts 55. At 20d22eae: `ALL 69 BLOCK DUTY CHECKS PASSED`.

## Null control

`dev/audit/harnesses/r10_disinfection_setpoint.py` (this PR, sha1 6ced0aeb71d5fc00734eaf4098e65e5e665891e8) copied over a worktree of origin/main ef579d9b and run there and at 20d22eae (both outputs byte-identical at 43095bde: `cmp`), default mode and `--grid` (2340 lines: arms `held`, `idle`, `disabled` x 5 steps x 12 everyday set-points x 13 disinfection temperatures):

- `diff <(grep '^null_' base) <(grep '^null_' head) >/dev/null && echo IDENTICAL || echo DIFFER` printed IDENTICAL over the 80 `null_*` lines (cycle disabled, everyday 60 and 62, no entity).
- The `held` arm's lines with the repair fields cut (`sed 's/ fix=.*//'`): IDENTICAL, 780 of 780: no cycle write moved.
- Per no-cycle arm (`idle`, `disabled`), the write fields differ on exactly 104 lines, each `over_limit=1` at the base (`diff ... | grep '^<' | grep -c over_limit=1`: 104 of 104 in each); the 676 lines `over_limit=0` at the base, the 455 on-step rows among them, are IDENTICAL.
- Default mode: only the `offstep` install's `repair_none` moves (20 lines): 61 to 60 where the arbiter writes the everyday step, and 61 to `-` on the cycle rows, where the pump reads the arbiter's 60, the floor's step at the hard maximum. `repair_own` stays `-` on every line.

## Figures

Taken at 43095bde against merge base ef579d9b unless a line names 20d22eae; origin/main's tip 7617c7cf4a at the last fetch, `git merge-tree --write-tree origin/main HEAD` clean.

<!-- figure-block: scope-line mb=26072317b5556a2baa1ff562d8fbbc9588e2ba5c head=c5b48730d9063440e8df53a5a14928d9e96f0078 -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out`; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`: `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN` at ec29e0dd (4342f022 and 43095bde change `_bounded`'s ceiling test, `setpoint_check._dhw` and `tests/block_duty.py`, inside the same scope: `tests/block_duty.py` 70 of 70, `tests/guard_pins.py` 61 of 61 and `tests/features.py` `ALL 5287 FEATURE CHECKS PASSED` re-run at 43095bde) (the 22 the scope names and the `run_always` lines); at 4498df97 `tests/features.py` failed 1 of 5287, "a climate set-point slot is clamped to its own min_temp/max_temp ... (L2)", repaired in ec29e0dd (see above), then `ALL 5287 FEATURE CHECKS PASSED`; `tests/block_duty.py` 70 of 70, `tests/guard_pins.py` 61 of 61.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- Census, `python3 dev/audit/harnesses/r10_disinfection_setpoint.py --grid`, per arm `grep "arm=<arm> " | grep -c <field>=1`:
  - `over_limit=1` (write above `dhw_max_temp`): `idle` 104 at the base, 0 at the head; `disabled` 104, 0; by step at the base 26 at each of 0.5, 1, 2 and 5, 0 at 0.1 (the same rule over `tests/block_duty.py`'s `_nocycle_grid_over_limit`). `held` 341 at both: a cycle is written above the charge limit by design, bounded by the hard maximum (`over=1`: 0 at both).
  - `fix_over=1` (repair Fix above `dhw_hard_max_temp`, no arbiter write, pump reading 30): `held` 272 at the base, 0 at the head; `idle` 272, 0; `disabled` 0, 0 (the floor there is `dhw_min_temp`). By step at the base, over the same rows in `tests/block_duty.py`'s `_repair_grid_over_hard_max`: 12 at 0.1 (the disinfection temperature 72, above the 70 cap), 56 at 0.5, 59 at 1, 64 at 2, 81 at 5.
  - `below_floor=1` (write under `dhw_min_temp` plus `DHW_MIN_TEMP_SETPOINT_MARGIN`, no step between the two bounds): 0 in every arm at the head; the grid's `dhw_min_temp` is 40, and the config flow refuses a minimum above the set-point less the margin (`config_flow.py`, `DHW_MIN_TEMP_SETPOINT_MARGIN`).
- Class seams (`fixer.md` step 8). Rule: `git grep -n '"dhw_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py` (every hot-water write of the arbiter) and `git grep -n quantise_setpoint_c -- custom_components/heatpump_optimizer/setpoint_check.py` (every rounding of the repair). Dispositions:
  - `_dhw_write` no-cycle return: closed in this diff, census 0 in both no-cycle arms.
  - `_dhw_write` cycle return: part 1's, bounded by `dhw_hard_max_temp`, `over=1` 0, unchanged (the `held` lines IDENTICAL).
  - the space-only gate row (`DHW_GATE_C`, rounded down): a 30 °C gate, below every charge limit the census reaches (lowest everyday 50): already within the ceiling.
  - `setpoint_check._dhw` Fix: closed in this diff, `fix_over` 0 in every arm.
- Mutants: `## Mutation proof`.

## Unpinned sites

None left. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/block_duty.py,tests/guard_pins.py,tests/env_drift.py` at the commit before 43095bde printed `PIN KILLED: 5 pinned, 1 left unpinned` (null control `pump_arbiter.py` NULL_COMMENT survived every driver): `pump_arbiter.py` `_bounded` BOOLOP (killed by `tests/guard_pins.py`), CMP_BOUND and GUARD_OFF, `setpoint_check.py` `_dhw` GUARD_OFF and CMP_BOUND (each killed by `tests/block_duty.py`); 43095bde commits those pins, less the `_dhw` GUARD_OFF one, whose site it removes with the survivor, `_dhw` BOOLOP on `if entity_id and pump is not None:`. That guard was redundant: the repair is active only with an entity and a reading, and `quantise_setpoint_c` reads a missing entity at the default step, so the floor is quantised unconditionally (the harness's `null_noentity` lines and `tests/block_duty.py`'s no-entity null control unchanged).

## Red checks

none

## Forward-carry

none

## Friction

none
