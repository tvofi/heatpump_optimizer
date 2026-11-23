# BLOCKED: r11-seam-actuation-writes at f3330c7ff3 (base origin/main 3153a635b4)

Question: `python3 tests/structure.py` at f3330c7ff3 refuses one row, `module_excess_loc` 21898 > 21775 (+123): the lines this group's nine findings and Carries 1 and 2 add to `pump_arbiter.py`, past its 2000-line `MODULE_LOC_LIMIT`. May the row be raised (CLAUDE.md rule 2; under the scope-all mandate, decision 0013's `## Raise justification`), or is a payment wanted that this seat has not found? Two rulings ride with it: (a) Carry 4 asks `unrestored_duty_change` and `_disinfecting` at 0, but the seven entities (both MQTT topics, number.freq, number.offset, number.valve, switch.hp, switch.vvc) are written by the observe-mode reload as `strings.json`'s `pump_duty_mode` text documents ("Observe writes none either ... the heat pump on/off switch ... is still switched by the plan"; frequency, valve and circulation pumps have their own enables): should Observe stop those writes (a product change) or does the carry close as measured? (b) Carry 3's part B maps a sweep kind that does not exist at the merge base (`grep -n "KIND_" custom_components/heatpump_optimizer/sysid.py` prints KIND_FIT and KIND_PROBE only); the sweep experiment is archive/handoff/r10-draw-map-evidence-b 8c1508d9c1's 81-file feature. Not built here: which group owns it?

## Payments taken (structure.py at each step, same tree otherwise)

- Eight rows breached at the first measure: class_excess_loc +57, coordinator_attrs +1, coordinator_multiassigned_attrs +1, duplication_copies +1, functions_cc_over_15 +3, max_class_loc +49, module_excess_loc +189, seam_cut_total +5.
- No coordinator attribute: the cut takes its cutter (`_cut_action(by)`), the re-cut builds one from the live model.
- One gate/re-cut/tail definition in pump_arbiter (`_step_writes`), read by the tick and the peak guard (`step_transition`); the guard's coordinator method calls it once (seam cuts back to 413).
- CC: `supply_tick` -> `_supply_half`; `_feedback` -> `_sampled`; `_load` -> `_restored`.
- Duplication: `inputs._range_attrs` read by `setpoint_range_c` and `on_entity_grid`.
- Coordinator and legionella additions compacted (no `_supply_wiring`, `_recut_step`, `async_follow`).
- Left: module_excess_loc +123. Not taken: a new step-tick module (the approved design's section 3 rejects it, and fixer.md step 17 refuses code moved to an unmeasured path); trimming other authors' prose in pump_arbiter.py for the row.

## Measured at f3330c7ff3 (head) against 3153a635b4 (base), same command at both ends

- `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D16/s1/cells.py --no-gates`: clause_grid 50 -> 0, cold_tank_charge 2 -> 0, boost_indoor_between 2 -> 0, unavailable_recorded 5 -> 0.
- `... dev/audit/rounds/round11/D12/s3/repairs_surfaces.py`: bad_fix_writes 8 -> 0.
- `... dev/audit/harnesses/r11_actuation_ported.py dev/audit/rounds/round11/D16/s2/timing.py` (finder's rig ported to the step tail; unchanged at the base): stale_share_mqtt_displace 0.5732 -> 0, stale_share_curve_offset 0.4644 -> 0, stale_share_frequency 0.4480 -> 0.1713 (rate-limit residual), cell3530_record_wrong_mode_at_on 1 -> 0 (null 0 both); `--no-switch` the same shares to 0; `--phases 1` 0.5020/0.4462 -> 0; `--interval 15 --phases 0` 0 at both.
- `... r11_actuation_ported.py .../D16/s2/disinfect.py`: on_in_window 0 -> 30 of 30, long_on_in_window 59 -> 90 of 90 (base unported 0 and 59), on_outside 30 -> 0.
- `... r11_actuation_ported.py .../D16/s2/effect.py`: min-cold-tank starts at lift 8 and 10: 30 -> 4, 38 -> 6.
- Carry 2: `dev/audit/harnesses/r11_full_draw_lift.py` 210 -> 0 contradictions (null 0 both); `dev/audit/harnesses/r11_actuation_lost_writes.py` set_pump/frequency/valve 1/1/1 -> 0/0/0 (`--double fake` 0 both); peak guard `r11_actuation_ported.py .../probe_peak_guard.py` published 4 -> 6 (the step's 6), `--at 5` and `--recut` 0 at both.
- Carry 4: `r11_actuation_ported.py dev/audit/rounds/round11/D16/s3/m6_restore.py`: every other arm 0, duty_change 7 and 7 at both ends, every null 0, restored_more_than_once 0.

## Owed after the ruling (the next fire, from this ref)

1. features.py: the failing-first tests the design's section 5 names, Carry 0's design-invariant-2 checks, a night-register restore check (Carry 1), and the existing checks the predicate moves (first seen: "the pump is commanded on the first tick and not again without a change" -- its pump entity has no state, which `inputs.delivers_to` refuses). A full run stopped there.
2. Notes 3 to 7 and 10 of the design; the stub change (`FakeServices` + `tests/ha_contract.py` row) the design names for D16-s1-05.
3. Mutation proof, closures classification of the three new harness files (`ci_predict.py --apply-inert`), prepr.sh, body (Forward-carry: Carries 0-4, #3749 arms), body_push.sh.
