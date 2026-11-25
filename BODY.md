Issues of this group (the roster's `issues`, no `fixes`, so named here and not closed by keyword): #3744, #3764, #3776, #3783, #3790, #3800.

R11-SEAM-actuation-writes (findings D16-s1-01, D16-s1-02, D16-s1-03, D16-s1-05, D16-s2-01, D16-s2-02, D16-s2-03, D16-s2-04, D12-s3-02), on the approved design `design/R11-SEAM-actuation-writes` 28bedac8a6 (design review approve at `design-verdict/R11-SEAM-actuation-writes` 1b5afe67f3). Cut from 3153a635b4 (which carries #3728 and #3812); merged with origin/main at f52e700df1 on a conflict (both sides counted the package's modules).

What is written and when:
- The step tick (`pump_arbiter.supply_tick`) is armed on every install and has two halves. The step half re-cuts the action at each plan step (`coordinator._cut_action`, one cut definition read by the solve and the tick) and runs one tail (`coordinator._async_step_tail`: disinfection follower, ECL110 publish, frequency, valve, pumps) under `ArbiterState.tail_lock`. The supply half writes the switch only where one is configured. Gate: `pump_arbiter.step_gate` over `_covering_step`, the one covering rule `step_supply` reads too.
- A frequency writer refused by its rate limit reports it (`_command_frequency` returns whether the refused target differs from the watchdog's record), and the tick retries at the first minute past `FREQ_WRITE_MIN_INTERVAL_S`.
- Values sit on the entity's grid and range (`inputs.on_entity_grid`, read by the frequency target and `setpoint_check`'s Fix); a write to an entity with no state or reading `unavailable` is neither sent nor recorded (`inputs.delivers_to`); the lead mode drops a record the select contradicts; the space gate writes the lower of `DHW_GATE_C` and the tank reading plus the start hysteresis; an indoor set-point under a live boost writes the boosted setpoint; a compressor stop on a qualifying pass keeps the feedback run for one `FEEDBACK_WINDOW`.
- The arbiter's held record and its store move to `arbiter_record.py` (`ArbiterState`, `FeedbackRun`, `state_for`, `persist_record`, `load_record`, `store_of`), which reads no coordinator: the payment for `module_excess_loc` and `coord_footprint` (`## Architecture score`).

#3749 (R11-N-unreleased-hold) is named here, not closed: its D16-s3 arms are Carry 4 (`## Forward-carry`). This PR fixes none of its duty-change arms; they close as measured under the orchestrator's ruling (inbox NOTE 5), each of the seven writes documented.

## Head

a41db633a25179e0f51e791bd4f216ef13478f02 (merge base f52e700df1, origin/main at 2026-11-25T10:13Z).

## Mutation proof

The fix reverted whole (`git checkout 3153a635b4 -- custom_components/` in a worktree at the head, the new blocks run with `tools/audit/seat/features_block.py`; production restored after):
- Block A (`# ---- R11-SEAM-actuation-writes A`): 6 of 12 fail, the six property checks: D16-s1-01 (45.4 written on a 1 Hz entity), D12-s3-02 (the Fix writes 60 above a 55 maximum), D16-s1-05 (mode recorded on an unavailable select), D16-s2-03 (a moved select not led), D16-s1-02 (gate 30.0 on a 20 degC tank), D16-s1-03 (21.0 under a live boost).
- Block B (`# ---- R11-SEAM-actuation-writes B`): every property check fails (boundary re-cut writes nothing, tail lock absent, peak guard publishes the cut's 2 not the step's 6, disinfection switch off in its window, feedback run reset at a stop); the lock-free null fails too, the base having no step half.
- Block C (`# ---- R11-SEAM-actuation-writes C`): 6 of 15 fail: the night registers (`night_before` empty, hours left at 22 and 6), the P3 full-draw sweep, and the P11 frequency, valve and pump arms. Carry 0's five checks pass at both ends.
- Block G (`# ---- R11-SEAM-actuation-writes G`): 3 of 10 fail: note 7 (bucket 3 for a value sent as 40), note 10b (the stale step's displace 2), note 10c's null (no step half).
Targeted, one production line each at the head:
- `coordinator._command_frequency`'s rate-limit return `target != self._freq_watchdog.commanded` -> `False`: `D16-s2-01 (note 9): a frequency write refused by its rate limit at the boundary is sent by a later minute's tick in the same step: ...` fails (1 of 26 in block B through G).
- `pump_arbiter._covering_step`'s power-schedule bound deleted (`return i`): the region `# --- #2261: a delivered-heat counter` .. `# --- R10-CEILING-PROBE` (`features_block.py --through "# --- R10-CEILING-PROBE"`) raises `IndexError: list index out of range` in `optimizer.get_current_action` (`power = result.power_schedule[i]`) at the check `the step tick writes nothing at a boundary under a step past the plan's power schedule`.
Diff mutants: `MUTANT_CMD='bash <scratch>/run_blocks.sh' tools/pr/prepr.sh` (the runner drives blocks A, C and B through G with `features_block.py`, 53 checks): 27 of the drawn mutants (`MUTANT_MAX` 40) survived, every one in `arbiter_record.py`'s store and slot checks moved verbatim from pump_arbiter.py, which the four blocks do not drive; each is under `## Unpinned sites`.

## Null control

Each property check above has its null beside it (the input under which nothing must change: an on-step value, a range that holds, an available select, an unmoved select, a tank at 48 degC, no boost, an unchanged step, no refusal, a free lock, no window booked, a non-qualifying pass, no Off between cycles, a register already at its value, a flow-unit target, the double that lands every call); every null passes at the base and at the head. The finder harnesses' null arms are in `## Figures`.

## Figures

Head a41db633a2 against the merge base f52e700df1, the same command at both ends; every figure below read the same against 3153a635b4 before the merge (`PYTHONPATH=tests/hastub:.`). The `dev/audit/harnesses/r11_*.py` ports exist only at the head; at the base the head's copy runs against the base's production by absolute path.
- `python3 dev/audit/rounds/round11/D16/s1/cells.py --no-gates`: clause_grid 50 -> 0; cold_tank_charge 2 -> 0 rigs; boost_indoor_between 2 -> 0 rigs; unavailable_recorded 5 -> 0 rigs; failing_rows 50 -> 0.
- `python3 dev/audit/rounds/round11/D12/s3/repairs_surfaces.py`: bad_fix_writes 8 -> 0 (fix_writes 12 both ends).
- `python3 dev/audit/harnesses/r11_actuation_ported.py dev/audit/rounds/round11/D16/s2/timing.py`: stale_share_mqtt_displace 0.5732 -> 0; stale_share_curve_offset 0.4644 -> 0; stale_share_frequency 0.4480 -> 0.1526 (the `FREQ_WRITE_MIN_INTERVAL_S` residual); cell3530_record_wrong_mode_at_on 1 -> 0 (null 0 both).
- the same, `--no-switch`: mqtt_displace 0.5732 -> 0; curve_offset 0.4644 -> 0; frequency 0.4480 -> 0.1526; stale_share_supply 0.7490 at both (no switch configured: the supply half does not run, design invariant 6).
- the same, `--phases 1`: mqtt_displace 0.5020 -> 0; curve_offset 0.4462 -> 0; frequency 0.2000 -> 0.1000; cell 3530 1 -> 0.
- the same, `--interval 15 --phases 0`: mqtt_displace 0 both; curve_offset 0 both; late channels 2 -> 0.
- `python3 dev/audit/harnesses/r11_actuation_ported.py dev/audit/rounds/round11/D16/s2/disinfect.py`: on_in_window 0 -> 30 of 30; on_outside 30 -> 0; long_on_in_window 59 -> 90 of 90; null_on_minutes 0 both.
- `python3 dev/audit/harnesses/r11_actuation_ported.py dev/audit/rounds/round11/D16/s2/effect.py`: min-cold-tank starts at lift 8: 30 -> 4, at lift 10: 38 -> 6; dhw_only_tank40_ent0_delivered_share 0.6336 both (null).
- Carry 2 (1), P3: `python3 dev/audit/harnesses/r11_full_draw_lift.py`: contradictions 210 -> 0 of 1170 cells. The finder's `dev/audit/rounds/round11/sweep/P3/D14/sweep-P3/probe_full_draw.py` reads 210 at the base and raises at the head (its inputs carry no `state`, which the shared lift reads): the port is its head reading.
- Carry 2 (2), P11: `python3 dev/audit/harnesses/r11_actuation_lost_writes.py`: set_pump/frequency/valve lost commands 1/1/1 -> 0/0/0; `--double fake` 0 at both (null). The finder's `p11_probes.py` raises at both ends (`_async_set_pump` left the coordinator in #3812): the port is its reading.
- Carry 2 (3), N-stale-step-actuation: `python3 dev/audit/harnesses/r11_actuation_ported.py dev/audit/rounds/round11/sweep/N-stale-step-actuation/harness/probe_peak_guard.py`: published 4 -> 6 (the step's 6), release_publishes_other_step 1 -> 0; `--at 5` and `--recut` 0 at both (nulls).
- Carry 4: `python3 dev/audit/harnesses/r11_actuation_ported.py dev/audit/rounds/round11/D16/s3/m6_restore.py`: unrestored_duty_change 7 and 7, unrestored_duty_change_disinfecting 7 and 7; every other unrestored arm 0, every null_unrestored_* 0 (9 arms), every restored_more_than_once_* 0, at both ends.
- Design note 3: the `timing.py` main walk (271 minutes, phase 1, interval 30) sends 14 `number.curve_offset` writes at the head (7 at the base) against `heat_curve.write_cap_per_day(30)` = 96 per day; no day-long walk exists in the harness.
- Design note 6: `cells.py` drives no unavailable supply switch (its unavailable state sets `select.hp_mode`, `number.hp_dhw`, `number.hp_space` only), so the supply switch's row is unmeasured.
- Carry 5: the `D16-s3-02 null control (off|unload|remove)` checks under `TZ=HASTUB_TZ=Asia/Kolkata` (the nightly slow lane's zone, `.github/workflows/nightly.yml`): 3 of 6 fail at 3153a635b4 and at the head before the fixture commit; 6 of 6 pass at the head under UTC, Asia/Kolkata, America/Chicago and Pacific/Kiritimati.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: ALL 6191 FEATURE CHECKS PASSED; under `TZ=HASTUB_TZ=Asia/Kolkata`: ALL 6184 FEATURE CHECKS PASSED.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2762 ENTITY CHECKS PASSED.
- Gate scope: `python3 tests/closure.py select --diff 3153a635b4`: `MODE: SCOPED`; every script `scope.run` names ran at the head except `tests/stress.py` (CI's mutation check), each exiting 0 at b40fbf388a before the merge; after it, at the merged head, `features.py` (both zones), `entities.py`, `finite_boundary.py`, `guard_pins.py`, `block_duty.py`, `doc_claims.py`, `deployment_shape.py`, `harness_headers.py`, `typing_ruler.py --mypy` and `structure.py` again, each exiting 0.
- `python3 tests/structure.py`: no row breached; the rows this change lowered are recorded in the head (class_excess_loc, max_class_loc, module_excess_loc, seam_cut_total).

## Architecture score

`python3 tools/audit/archscore/score.py --diff f52e700df1 HEAD`: Architecture score: dS +0.0017 IMPROVES (coord_footprint 2533 -> 2530)
- `module_excess_loc` (pump_arbiter.py past its 2000-line limit) was paid by extraction, as the orchestrator answered the raise (inbox NOTE 5): `arbiter_record.py` holds the record, its slot sets and its store and reads no coordinator (`load_record(held, open_store, hass)`, `persist_record(held, store)`); the coordinator-keyed wrappers stay in pump_arbiter.py. dS of the move alone against the pre-move head: +0.0000. No budget raised.
- `coord_footprint` 2535 at the resumed head against 2521 at 3153a635b4: paid by the record's load and persist no longer taking the coordinator (2517 after them, 2518 with the frequency writer's typed returns).
- Considered and not taken: a step-tick module (the design's section 3 rejects it); moving the flow set-point computation (`_flow_target` and its 387-line closure) out of pump_arbiter.py, a larger move through a hot file that other groups' diffs touch, where the record's 152 lines already paid.

## Red checks

- `tests / mutation` (predicted by `tools/pr/ci_predict.py`, step 7d: sites the diff adds with no pin, and the diff mutants' survivors, every one in `custom_components/`): each is listed under `## Unpinned sites`, pinned by `mutation-autofix`, the lane `ci-autofix.md` names as this red's repair. The cheaper detector is that prediction, run here before the handoff in seconds at no standing cost beyond `prepr.sh`; no countermeasure is owed.

## Unpinned sites

- `custom_components/heatpump_optimizer/arbiter_record.py:28 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:40 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:136 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:139 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:170 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:174 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:176 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:184 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:184 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:192 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:192 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:201 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:202 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:203 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:205 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:206 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:207 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/circulation.py:58 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:673 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:7638 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:7656 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:7668 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:7671 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:7688 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:10812 CLAMP_DROP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:10829 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:10832 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:576 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:583 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:626 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:626 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:640 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:641 CLAMP_DROP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:642 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:643 CLAMP_DROP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/inputs.py:644 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:571 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:803 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:803 CMP_BOUND`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:804 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:809 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:966 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:966 CMP_BOUND`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:967 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:967 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:987 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:987 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:990 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:993 CMP_BOUND`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:995 CLAMP_DROP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:997 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1003 CMP_BOUND`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1249 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1254 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1254 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1768 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1809 CLAMP_DROP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1809 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1900 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1994 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1999 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2005 CMP_BOUND`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2005 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2010 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2010 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2015 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2017 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2090 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2093 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2096 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2102 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2102 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2106 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2108 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2112 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2122 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2123 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2123 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2125 BOOLOP`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2126 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2224 GUARD_OFF`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:2269 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/arbiter_record.py:35 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:40 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:57 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:89 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:107 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:160 CALL_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:171 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:177 CALL_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:181 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:202 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:204 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:204 CONST_SWAP`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:206 RETURN_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:31 STMT_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:34 STMT_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:57 STMT_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)
- `custom_components/heatpump_optimizer/arbiter_record.py:61 STMT_DEL`: pinned by `mutation-autofix` (its lane mutates custom_components/) (a diff mutant this branch's four blocks leave alive: moved verbatim from pump_arbiter.py with the record's store, whose killers are tests/finite_boundary.py and tests/guard_pins.py)

## Forward-carry

- Carry 0 (design invariant 2 after a release): `tests/features.py` block C checks the four owners' records empty after Off and the first write after On sent; they pass at the base and the head, a held invariant, not a defect here. Built in this PR. Carry: dismissed: built here, held at both ends
- Carry 1 (the GCHV night registers): `pump_arbiter._write_night_schedule` captures each register's reading before the first write (`ArbiterState.night_before`, persisted, declared in `store.DOMAINS`) and the row release writes it back; block C's check fails at the base. Built in this PR. Carry: dismissed: built here
- Carry 2 (P3, P11, N-stale-step-actuation sweeps): built; figures above, each sweep's port reads 0 at the head. Carry: dismissed: built here
- Carry 3 (sweep origin in `pump_arbiter.pass_origin`): not built. The sweep kind does not exist at the merge base (`grep -n "KIND_" custom_components/heatpump_optimizer/sysid.py` prints `KIND_FIT` and `KIND_PROBE` only); the sweep experiment is archive/handoff/r10-draw-map-evidence-b 8c1508d9c1's feature. Routed by the orchestrator's ruling (inbox NOTE 5) to the sysid/learner seam's owner, with the archive ref and the KIND_ grep as its control. Carry: dismissed: owed to R11-ARCH-fabric-learner by the orchestrator's ruling (inbox NOTE 5), for the relay to land; carry_audit's group token cannot spell that id (see Friction)
- Carry 4 and #3749 (R11-N-unreleased-hold, its D16-s3 duty-change arms): not fixed; closes as measured by the orchestrator's ruling (inbox NOTE 5). Each of the seven re-written entities is documented as written: `switch.hp` by `pump_duty_mode`'s text ("With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan"); the ECL110 command and displace topics, the curve offset, the frequency, the valve and the VVC pump each by their own option's text (`ecl110_displace_set_topic`, `heat_curve_displace_entity`, `freq_control_mode`, `mixing_valve_write_entity`, `vvc_pump_entity`), which `pump_duty_mode`'s "writes none" (the operating mode and set-points) does not govern. #3749's other arms (off, unload, remove and their Modbus and disinfecting variants) read 0 at both ends. Carry: dismissed: closes as measured under the orchestrator's ruling, all seven writes documented
- Carry 5 (nightly slow red since #3812): a test defect, fixed: the null arm's literal circulation window missed the frozen clock outside UTC, so the null drove a non-baseline command; the release wrote nothing over an equal value. Carry: dismissed: fixed here
- The design's stub change for D16-s1-05 (`FakeServices.async_call` dropping a call to an `unavailable` entity, pinned by a `tests/ha_contract.py` row) is not made: `FakeServices` is `tests/harness.py`'s, not the stub package `ha_contract.py` runs against real Home Assistant, so its row would have no upstream to run; production refuses the call before it is made (`inputs.delivers_to`), which block A pins. A departure from the approved design, raised for the reviewer's and the orchestrator's ruling. Carry: dismissed: pending orchestrator ruling on this group's own design (carry_audit's group token cannot spell R11-SEAM-actuation-writes)

## Friction

- `finding-propagation`: contradiction: `tools/audit/carry_audit.py`'s `GROUP_TOK` (`\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z`) refuses every mixed-case roster id (`R11-ARCH-fabric-learner`, `R11-SEAM-actuation-writes`, the brief's own list of valid `Carry:` targets), and the upper-cased spelling is "not a group of the roster": `python3 -I tools/audit/carry_audit.py --repo x/y --roster-ref origin/handoff/audit-r11-roster check --body <body>` read both such lines UNROUTED; `git grep -hoE "Carry: R11-[A-Za-z0-9-]+" -- dev/programme dev/audit .claude` finds no mixed-case destination ever routed. Carry: dismissed: carry_audit's grammar is the orchestrator's; Carry 3 above names its destination for the relay
