Closes #3855

R11-OWNER-FROST-HOLD, built on the approved design e91a4e30 (design-verdict 774250ff). On every install with a heat-pump power switch, an OFF the integration would write on an idle step is held while the outdoor reading is below the *Frost hold below* option (+2 °C by default), or stale or missing; the hold clears at threshold + 1 K. The new module `frost_hold.py` is the one writer of the hold's `ArbiterState` fields and gates last in `coordinator._write_supply`, after `supply_hold.hold_supply`. The early cut-off asks `frost_hold.take_off` before it cuts. With Pump duty at Control, the arbiter serves the hold as space at `pump_arbiter._hold_floor_c`. The opt-out is `frost_hold` (default on).

Release note: On every install with a heat pump power switch, the optimizer no longer switches the pump off on idle steps while it is below +2 °C outdoors (option *Frost hold below*), or while the outdoor reading is stale or missing: the pump stays on so it can defrost and protect itself. With *Pump duty* in control it is held at its own minimum set-point; otherwise it runs on its own curve while held, which can use energy the plan does not price, and learning pauses for those runs, and for the whole hold on an install without a power sensor. Quiet off windows are held too. Turn *Frost hold* off to keep the old behaviour.

Where this departs from the design's text (no departure in behaviour):
- `frost_hold.outdoor_reading(health, forecast_c, config)` reads the sensor slot through `EntryConfig`, which gains `outdoor_temp_entity`, so the coordinator reads no key off its config mapping.
- `frost_hold.gate(held, inputs, value)` takes the coordinator's `arbiter_inputs` builder, as `supply_hold.hold_supply` does, and builds the inputs only for an OFF.
- The cut-off hook is a lambda on the existing `early_cutoff.arm` line (`frost_off=`, keyword-only after `now`, so `tests/dst_checks.py`'s positional `now` still binds), not a `cutoff_hook(coord)` function.
- `frost_hold.diagnostics_view(held, inp)` takes plain values, as `early_cutoff`'s row does.
- `freeze_reason(coord)` is a one-statement shim over `_freeze(held, inputs, now)`.

All four shapes were chosen on measurement; see `## Architecture score`.

## Head

3071796b00e0c6e113fc048b0f172dc664897cfc, on merge base 9276ddf6b122816149ecba82a607aedf38d87ba1 (origin/main at the merge). The handoff 8ea9f282 was cut on 1207ee13 and did not merge into main, so 5ee0a111 merges origin/main into it. No rebase or re-cut was done. The merge resolves seven conflicts by union. Main's R11-SEAM-actuation-release moved `pump_arbiter._verdict`, `_not_startable` and `_missed` into `duty_ledger.py`, so the frost-hold verdict is now the first branch of `duty_ledger.step_verdict`. In `coordinator._apply_action`, main's off-restore and stale-plan lines stand and the `early_cutoff.arm` call keeps `frost_off=`. The module counts are main's plus `frost_hold.py`, and the D6 claims outputs are regenerated. 3071796b re-records the structure table, with no raise. Fixer steps 2-8 re-ran at this head, inside `prepr.sh` (scoped gate, `PREPR_SKIP_CLOSURES=1`); its receipt is this body's `Prepr:` trailer.

## Mutation proof

Failing first: at the merge base the new block cannot run, because `frost_hold` does not exist there. With the gate line removed (mutant 18), its real-coordinator checks fail. Each mutant below was made one at a time in the named file. The block was then run with `python3 tools/audit/seat/features_block.py --prelude 'exec(open(P).read())' 'R.section("R11-OWNER-FROST-HOLD' 'R.section("duty-switch restart learning, part A'`, where P is written by `python3 tools/audit/seat/features_block.py --emit-prelude P` with the same two markers. Each line gives the failing count out of the block's checks (55 at the merge base 1207ee13), then one failing check's name.

1. `frost_hold._active` `out < below` to `<=`: 1 failure, `frost hold gate: inside [t, t+1): an inactive latch stays inactive at +2.0 °C`.
2. `+ CLEAR_K` dropped: 1, `frost hold gate: inside [t, t+1): a held latch stays held at +2.9 °C`.
3. None no longer sets the latch (both branches guarded `out is not None`): 4, `frost hold gate: no reading sets the latch from inactive`.
4. Opt-out branch `if not cfg.frost_hold:` to `if False:`: 4, `frost hold gate: null control: the same OFF with the option off is written`.
5. `gate`: `held.frost_holding = _active(...)` to `= False`: 4, the same check.
6. `gate`: the switch-off branch returns `None`: 2, `frost hold gate: a switch reading off is switched back on`.
7. `take_off` guard always refuses: 1, `frost hold: the cut-off below the threshold is refused and the hold takes over`.
8. `_note_run` guard to `if True:`: 2, `frost hold: null control: a held pump the meter reads idle does not`.
9. `outdoor_reading`: `got.ok` dropped: 1, `frost hold reading: a stale sensor is no reading, not the forecast`.
10. `outdoor_reading`: the no-sensor forecast branch removed: 2, `frost hold reading: no sensor configured: the forecast is the reading`.
11. `pump_arbiter._arbitrate`: the `held.frost_holding` read set to False: 6, `frost hold, control on Tuya: an idle step held writes Heating and the space floor`.
12. `_arbitrate`: the block bypass (`served = _served(...)` always): 3, the same check.
13. `_lead_mode`: the hold's `"space"` dropped: 1, `frost hold: a switch-on into a hold writes Heating ahead of it on Tuya`.
14. `_hold_floor_c`: `max(low, limit)` to `low`: 1, `frost hold floor: the controller's lower limit of 28 °C raises it`.
15. `duty_ledger.step_verdict` (main's R11-SEAM-actuation-release moved `pump_arbiter._verdict` there): the frost branch to `if False:`: 1, `frost hold: the observe ledger scores the held step frost-hold`.
16. `_observe`: `row["frost"] = False`: 1, the same check.
17. `early_cutoff.on_room_event`: the `frost_off()` guard to `if False:`: 1, `frost hold: the early cut-off writes no turn_off while the hold applies`.
18. `coordinator._write_supply`: `frost_hold.gate(...)` replaced by a pass-through: 6, `frost hold, real coordinator: an idle step at -3 °C leaves the switch on`.

`prepr.sh` step 6d also drew the diff's first 40 added-line mutants under the same block (`MUTANT_CMD`): `no survivor among the diff's first 40 mutant(s)`.

## Null control

Every check in the block pairs with its null control: the same input with `frost_hold` off, or on the warm side of the latch, gives main's OFF. The 24 h replay also runs main itself, the same coordinator with `frost_hold.gate` replaced by a pass-through. Opted out, the switch calls are byte-equal to main's. The existing switch tests that run with no outdoor reading and no forecast, or at -5 °C, now opt out explicitly: `_LC_DATA`, `_solve_coord`, `_r9egb9_make`, `_ac_calls` and `_ec_cycle_writes` in `tests/features.py`. A missing reading sets the latch, so those tests would otherwise pin the hold instead of the mechanism each was written for. The skip-log checks moved to `frost_hold._LOGGER`, where `log_skip` now logs. Their null control (the blocked-mode skip is heard once) shows that logger is the one that hears it.

A hold's switch-on waits on no minimum, and that includes the early cut-off's `MIN_OFF`, which is `runs.MIN_PAUSE`. A cut made while warm is therefore overridden by the next cycle if the reading turns cold or stale within `MIN_OFF`. Below the threshold, `take_off` refuses the cut before it is made. The cut-off's own check, `_ec_cycle_writes`, opts out for that reason.

## Figures

- Replay, design test 19: a 24 h series, the "s---" plan, the cycle every 30 min, outdoors +6 to -6 to +6 °C, the sensor stale 08:00-10:00. Over it, turn_off while latched is 0 (main: 34), the latch is set for 1020 of 1440 minutes, and opted out equals main. Instrument: the block run above, its `figure: frost hold replay` line.
- Structure ratchet: `python3 tests/structure.py`, all rows ok. Re-recorded in commit 010e3210 with no raise: class_excess_loc 17317 -> 17308, max_class_loc 7868 -> 7863, module_excess_loc 21779 -> 21774, unloaded_package_imports 14 -> 3. After the merge with main 9276ddf6, re-recorded again in 3071796b with no raise: module_excess_loc 21770 -> 21767, because pump_arbiter.py no longer carries its own copy of the step verdict (main moved it to `duty_ledger.py`). Against main's table the head is class_excess_loc 17301 -> 17292, max_class_loc 7844 -> 7839, module_excess_loc 21775 -> 21767, unloaded_package_imports 14 -> 3. seam_cut_total holds at 413.
- Payments for the module span (`MODULE_LOC_LIMIT` 2000): eleven package imports nothing read, listed by `structure.py`'s "package from-imports nothing reads" (coordinator 4, config_flow 2, pump_arbiter 2, thermal_model 3). Also history-only prose in `pump_arbiter`'s module docstring (the v6.6.12 stand-down narration), `step_duty` and `_arm_space`, and in `config_flow`'s settings-registry comment, `async_step_reconfigure` and the plumbing page docstring. Each decision those passages carried is kept in one sentence.
- Mutation ledger: seven `killed_by` pins are re-keyed, each `reason` extended with why. The lines or function names moved under this diff; no new pin is written by hand. Four follow the rename of `_ran_kw` to `ran_kw` (`_feedback` GUARD_OFF and CMP_BOUND, `_observe` CMP_BOUND, `ran_kw` RETURN_DEL). `_verdict` GUARD_OFF follows `if` becoming `elif`; main moved that function to `duty_ledger.step_verdict`, so the merge keys the pin as `duty_ledger.py/step_verdict.GUARD_OFF.af4ac328`. `desired` GUARD_OFF follows `... and not frost`. `supply_hold.freeze_span` RETURN_DEL follows that function made public. The `desired` mutant was re-run on a `git archive` copy at the head, the guard set to `if False:`, and `tests/features.py` fails under it: 9 checks, among them `R10-WATER-SETPOINT-FEEDBACK repeat, flow unit: every minute of the last 30 within 20 % of plan, one start`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 1207ee13b0e439a4acefccabace691785af2ebad` gives dS -0.0017 WORSENS (coord_footprint 2525 -> 2528). The charged list is `tools/audit/archscore/metrics/footprint.measure` on the flattened tree, head against base.
- Golden fixtures: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=1207ee13b0e439a4acefccabace691785af2ebad ./tests/run.sh` (`env_drift.py --all`, one environment). `config_flow` moves, a pure addition (19 inserted lines, 0 deleted, the two option rows and the seed's toggle). It is float-free, so it is re-recorded with `golden.py --record --only config_flow` and claimed in `tests/golden/claimed_drift.txt`. The other 55 fixtures are byte-identical to the merge base.
- Module counts the docs and harnesses state move with the new module: `docs/architecture.md` (102 modules, 37 importing `homeassistant`, `frost_hold` in the map), `dev/audit/rounds/round4/D6/claims.py`'s headers and output, and `tests/deployment_shape.py`'s #1218 note (all 121 files). These are main's counts after R11-SEAM-actuation-release, plus one. `tests/doc_claims.py`, `tests/harness_headers.py` and `tests/entities.py` read them.
- Scope: `python3 tests/closure.py select --diff 1207ee13b0e439a4acefccabace691785af2ebad` printed `MODE: SCOPED -- 30 script(s) run, 3 scoped out`; against the merged base 9276ddf6 it prints the same mode line, `MODE: SCOPED -- 30 script(s) run, 3 scoped out`. The gate's re-run at this head is `prepr.sh`'s, named under `## Head`. Gate run 2 of `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=1207ee13b0e439a4acefccabace691785af2ebad ./tests/run.sh` was at 759e0b44. Every selected script passed except `tests/features.py` and `tests/entities.py`, which are fixed in bbe5ef7f, b783e1ed and 09b08a62. `tests/features.py` and `tests/entities.py` re-run at 09b08a62, before the merge: `ALL 6028 FEATURE CHECKS PASSED` and `ALL 2748 ENTITY CHECKS PASSED`. The three commits since 759e0b44 touch `frost_hold.py` (a lazy lambda and a rename), `coordinator.py` and `pump_arbiter.py` (the rename's call and docstring), and `tests/entities.py` and `tests/features.py`.

## Architecture score

- `coord_footprint` 2525 -> 2528: +1 is `frost_hold.freeze_reason(coord)`, which the learners' `_tail_freeze` calls to note a held run at the learner's own moment. The alternative passes `coord.arbiter_inputs` from `_tail_freeze` and measured `seam_cut_total` 413 -> 419 (a learning-seam helper reaching the views method and every attribute it reads). +2 are the hold's two conditional expressions in `pump_arbiter._arbitrate`, the duty override the design places there. Moving them into helpers would only hide them from the count. Measured shapes: a `cutoff_hook(coord)` function and a `diagnostics_view(coord)` together cost +11 before they were reshaped.

## Unpinned sites

Every site is under `custom_components/`, so each is pinned by `mutation-autofix` (`ci-autofix.md`). The killer is `tests/features.py`, mostly its R11-OWNER-FROST-HOLD block. `prepr.sh` step 6d's diff-mutant run under that block found no survivor among the diff's first 40 mutants.

- `custom_components/heatpump_optimizer/config_flow.py:1695 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/duty_ledger.py:47 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/early_cutoff.py:317 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/early_cutoff.py:317 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:51 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:67 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:70 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:70 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:79 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:81 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:83 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:83 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:85 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:85 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:87 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:100 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:102 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:104 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:107 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:110 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:119 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:123 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:128 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:128 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:137 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:140 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:140 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:146 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:153 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:156 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:156 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:156 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/frost_hold.py:161 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1290 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1306 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1306 RETURN_DEL`: pinned by `mutation-autofix`

## Red checks

- `tests / mutation`, predicted red by `prepr.sh` step 6d for the 36 sites it lists at this head. They are named under `## Unpinned sites`. These are sites the diff adds with no ledger pin yet. `mutation-autofix` pins killed sites by a bot commit (`ci-autofix.md`), so this is its repair, not a hand-written pin. The cheaper detector already exists and ran: step 6d lists the same sites locally in seconds. No new detector is owed.


## Forward-carry

- The design's carries are built here, not carried. circulation-rail: `pump_schedule.space_pump_should_run`'s docstring. clear-on-off: `frost_hold.holding` masks the hold under `MODE_OFF`, and `gate` resets it on its first call. The verdict's unmetered-freeze-text and manual-off-rewritten carries are built in `docs/configuration.md`, `docs/how-it-works.md` and the option description. Carry: dismissed: built in this pull request
- Carry 0 (roster item 71b98dc2, from R11-OWNER-MODE-LEGS): its precondition, `_kept_leg`, is not on main (`git grep -c _kept_leg origin/main -- custom_components` prints nothing at origin/main 9276ddf6). So this group, landing first, has no leg to pin against. The pins "frost wins with a young DHW leg latched" are owed by MODE-LEGS when it merges second. Its legs sit upstream of `_served`, which the hold replaces in `_arbitrate` and `_lead_mode` (`held.frost_holding`). Carry: R11-OWNER-MODE-LEGS
- Carry 1 (roster item 033699bc, from R11-OWNER-FAULT-HOLD): FAULT-HOLD's module is not on main (`git grep -c fault_hold origin/main -- custom_components` prints nothing), so this group merges first and the composition is owed by FAULT-HOLD's merge, as its design 57d5d278 states. The seams it composes with are all here: the supply gate `frost_hold.gate(held, inputs, supply_hold.hold_supply(...))` in `coordinator._write_supply`, where the fault hold's gate goes outermost and frost's ON passes; the cut-off's `wiring.frost_off()` in `early_cutoff.on_room_event`, which the fault hold's consult precedes; the `frost-hold` verdict, first in `duty_ledger.step_verdict`, behind which `device-fault` is decided; the hold row served when `held.frost_holding` in `pump_arbiter._arbitrate`, which a standing fault must suppress; and `frost_hold.log_skip`, where a held OFF says why. Carry: R11-OWNER-FAULT-HOLD
- Carry 2 (roster item 50f1ee5c, from R11-OWNER-STEP-KICK, T11, design carry frost-entry): STEP-KICK's `swap_at` is not on main (`git grep -c swap_at origin/main -- custom_components` prints nothing at origin/main 3153a635), so this group lands first and has no swap to pin against. The hold's entry is here for STEP-KICK to compose with. `pump_arbiter._arbitrate` serves a held step as `space` (`served = "space" if held.frost_holding`), and `desired(..., frost=True)` writes `_hold_floor_c`, not the `_map_inputs` row. So a frost entry after hot water is a switch into space, and STEP-KICK's merge owes the T11 pin: whether that entry sets `swap_at`, and whether the held row bypasses `_map_inputs`. Carry: R11-OWNER-STEP-KICK

## Friction

none
