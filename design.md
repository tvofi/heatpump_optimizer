# Design note: R11-SEAM-actuation-writes

Extends the architect note, ADR-001 and ADR-004 (plan 50a932de3b2a). Code read at the base 199de0d83ac1d4c3a7a9860914226c492ce2f5c3; line citations are at that SHA. Predecessors: `R11-SEAM-kernel-step` at its handoff head e265279b8df87854e10ae549db9f07d2a021cac9 (`plan_step.py` there carries `plan_step_index` and `covering_index`; `pump_arbiter.py` reads them); `R11-SEAM-actuation-release` has no handoff head, so its approved design 349d6277f25fb6855b58395bcb7f055f2e40d86d is read as the shape. Findings read whole at 50a932de3b2a: `dev/audit/rounds/round11/D16/s1/findings/D16-s1-01.json` and its eight siblings, with the judge's rows in `dev/audit/rounds/round11/JUDGE.json`.

## 1. Owning seam

Actuation, one owner per concern, none needing two:
- **When a step's writes are re-derived**: the step tick in `pump_arbiter.py` (`pump_arbiter.py:2065` `supply_tick`), the only per-minute boundary detector, on `plan_step_start`.
- **A value on an entity's step and range**: `inputs.py` (`inputs.py:658` `bounded`, `inputs.py:728` `_on_step`). Callers: `setpoint_check.py`, the frequency target.
- **The arbiter's rows, record and loop**: `pump_arbiter.py` (`desired`, `_write`, `_lead_mode`, `_feedback`).
- **The disinfection follower**: `legionella.py` (`async_track_cycle`).
- `coordinator.py` only calls. `tests/seam_map.json` maps coordinator methods only; every method touched is in `core`.

## 2. Shape

**Step boundary (D16-s2-01, D16-s2-02).** `SupplyWiring` gains two plain callables: a re-cut and the write tail. When `supply_tick` sees a new step it calls the re-cut, then the tail, then decides the supply as today.
- Re-cut: where `step_supply`'s gate holds (`pump_arbiter.py:2008`: Auto or Economy, plan fresh, no experiment) and `plan_step_index` covers now, the action is cut again by the statement at `coordinator.py:6469` (`adopt_plan` over `get_current_action`) and the boost overlay re-applied (`coordinator.py:6097`). One definition, read by the solve and the tick.
- Tail, in this order, one definition read by the cycle and the tick: disinfection follower, `async_publish_current_action`, `_command_frequency`, `_command_valve_target`, `_async_drive_pumps`. The valve call leaves `coordinator.py:6499`; the frequency and pump calls leave `coordinator.py:6112`.
- `async_observe` (`legionella.py:552`) stops calling `async_track_cycle`; the tail calls it with the tank reading, after adoption, in every mode, so `legionella.py:350` reads the action of the step it lands in.
- The MQTT publish is skipped at a boundary when the displace integer and the on flag equal the last sent (`coordinator.py:7707` `_ecl110_current_displace`); the cycle publishes as today. Each writer keeps its rate limit; a writer refused by one leaves the step pending and the tick calls the tail again next minute.

```
tick(new step) -> re-cut -> tail: follower, publish, frequency, valve, pumps -> supply
cycle: observe -> solve -> adopt -> experiment -> overlay -> _apply_action -> tail
```

**Grid and range (D16-s1-01, D12-s3-02).** `inputs.py` gets one public function: a number on the entity's own step inside its own min and max, minimum rounded up, maximum down, no unit conversion. `write_setpoint` reads it at `inputs.py:728`; the frequency target reads it in place of the clip at `coordinator.py:10861`, before the dedup, and the owner records the value sent. `setpoint_check.py:169` asks the entity's grid (`setpoint_grid(...).bounded`, rounding up, `hi` the hard maximum) in place of `quantise_setpoint_c`: the function the arbiter bounds by, so Fix and arbiter cannot disagree. `repairs.py` is unchanged.

**Unavailable (D16-s1-05).** One predicate in `inputs.py`: the entity has a state and it is not `unavailable`. `_write` (`pump_arbiter.py:1598`) returns on it before the call, so nothing is recorded or reported. `unknown` still writes: Home Assistant delivers to it. `FakeServices.async_call` (`tests/harness.py:227`) drops a call whose target entity reads `unavailable`, pinned by a `tests/ha_contract.py` row with expect both.

**Lead mode (D16-s2-03).** `_lead_mode` drops the mode record when `_observed` reads a mode that `_differs` from it, then writes; no miss is counted. An unreadable select keeps the record.

**Indoor boost (D16-s1-03).** `desired` computes the boost fact for both units (`pump_arbiter.py:1305`), tolerating no coordinator. `_space_target`'s indoor branch under a boost bounds the action's `setpoint`, which `boost.overlay` and the Boost row set to the band top; the misdeclared-unit test still reads the plan's room value.

**Gate (D16-s1-02).** The space row with no Heating option (`pump_arbiter.py:1310`) writes the lower of `DHW_GATE_C` and the tank reading plus the read start hysteresis (zero where none is read), rounded down inside the entity's range; with no tank reading, `DHW_GATE_C` as today. `dhw_gated` compares against the record, so it follows.

**Floor loop (D16-s2-04).** In `_feedback`, a stop on a qualifying pass (`pump_arbiter.py:1020`) keeps the run and its target instead of resetting; stopped passes are zero samples for at most one `FEEDBACK_WINDOW` per stop. `_note_stop` is still called. Any non-qualifying pass resets as today. `thermal_model.py` is unchanged.

**Invariants.** (1) After a boundary's tail, every step-derived command equals the covering step's, or its writer is rate-limited and pending. (2) No number leaves off the entity's step or range. (3) A record exists only for a delivered write. (4) Release invariant 2 holds: this group adds no record a restore does not empty. (5) Entities, services, payload keys unchanged.

## 3. Alternatives

- **A timer per writer**: four boundary detectors and four copies of the gate at `pump_arbiter.py:2008`; `coordinator.py` grows per writer.
- **Each writer reads its plan series by index**: bypasses `boost.overlay` and the experiment override, which only the action carries; two sources for one command.
- **A new step-tick module**: moves `held.supply` off `ArbiterState`, which the release design's supply restore reads; a new tracked file for one function.
- **The record check inside `_write` for every slot** (D16-s2-03's general form): a pass inside `ECHO_GRACE_S` rewrites a value not yet echoed, and `_note_sent` already drops records on purpose.
- **`hold` before the lead**: it compares set-points the pump reports as its own while off (`_pump_off`) and counts misses toward `ISSUE_IGNORED`.
- **Quantising in `freq_control.py`**: a second on-step rule beside `inputs.py:600`, the class N-step-grid.
- **A larger default lift** (D16-s2-04's perturbation): fixes one plant, moves every other plant's floor.

## 4. Sibling sites

- `python3 tools/audit/enumerate.py d16-writes | grep '^write'`: eight. Covered: `_command_frequency`, `_write`, `write_setpoint`; boundary-driven: both `publish_ecl110_topics` sites, `_async_set_pump`, `_disinfection_switch`. `switch_supply` keeps its own tick.
- D16-s1-05's rule, `grep -n 'held.written\[slot\]\|_pump_commanded\[\|_freq_last_write = \|_valve_commanded_target = ' custom_components/heatpump_optimizer/*.py`: four records. The arbiter's is fixed; the other three move to owners in the release group and read the same predicate before their send. `disinfection.py:215` already refuses an unread flag.
- D12-s3-02's rule, `grep -n 'write_setpoint(\|quantise_setpoint_c(\|write_setpoint_c(' custom_components/heatpump_optimizer/*.py`: `setpoint_check.py:169` fixed; `inputs.py:776` receives arbiter values already bounded and restore values read from the entity.
- Out of scope: `optimizer.py:6592`, a covering-step copy with no end rule. The re-cut calls it only where `plan_step_index` covers now, so the two cannot disagree there; the file is not this seam's.

## 5. Evidence, by file

- **Failing tests first, `tests/features.py`**, each with the finder's null: beside `tests/features.py:1059` an off-step frequency (null: 0.5 Hz step); beside `tests/features.py:47179` a Fix on an entity capped under the floor (null: range holding it); beside `tests/features.py:85892` an unavailable select leaves no record (null: available), and a select moved while off is led (null: unmoved); beside `tests/features.py:85844` a boundary between cycles re-cuts and writes frequency, displace and valve (null: unchanged step writes nothing); beside `tests/features.py:40530` the switch on inside the booked window (null: none booked); beside `tests/features.py:91198` a stop on a qualifying pass keeps the run (null: a non-qualifying pass resets); the cold-tank gate (null: tank at 48); the indoor boost (null: no boost).
- **Finder harnesses, both ends, at 50a932de3b2a**: `dev/audit/rounds/round11/D16/s1/cells.py --no-gates` (clause_grid, cold_tank_charge, boost_indoor_between, unavailable_recorded to 0; nulls unchanged); `dev/audit/rounds/round11/D16/s2/timing.py` (three stale shares to the rate-limit residual, reported; `--phases 1` cell 3530 to 0; `--interval 15 --phases 0` stays 0); `dev/audit/rounds/round11/D16/s2/disinfect.py`; `dev/audit/rounds/round11/D16/s2/effect.py` (starts at lift 8 and 10 down, lifts 2 to 6.5 at one start); `dev/audit/rounds/round11/D12/s3/repairs_surfaces.py` (bad_fix_writes 0).
- **Score and ratchet**: `tools/audit/archscore/` before and after; `coord_footprint`, `private_cross_module`, `layer_violations` not above the merge base.
- **Goldens**: no solver path changes; both claim files byte-identical.
- **Mutation targets**: the tick's new-step test, pending retry and re-cut gate; the on-step function's two rounding directions; the availability predicate; the lead's record drop; the gate's minimum; the kept run and the one-window bound; the follower's position after adoption.

## 6. Hot files, position, decisions

Hot: `pump_arbiter.py`, `coordinator.py`, `inputs.py`, `legionella.py`, `setpoint_check.py`, `freq_control.py`, `tests/harness.py`, `tests/ha_contract.py`, `tests/features.py`. Third on the actuation chain, after both predecessors merge; `R11-SEAM-product-text` follows. Receives release invariant 2 with its control (a valve write after Off then On is sent). If the stub change must register with a base-pinned grader: p1 is `tests/harness.py` and the contract row, p2 the production change.

- decision: orchestrator. `inputs.py`, `tests/ha_contract.py` and `tests/features.py` join the roster's hot files; `heat_curve.py`, `disinfection.py`, `thermal_model.py` and `repairs.py` leave them.
- decision: owner. D16-s2-04 changes the feedback loop on every install with the option on; the alternative is a per-plant setting.

## Notes for the fixer

1. Re-read the release group's merged diff first: the frequency and valve tails move to `freq_control.py` and `mixing_valve.py`, and the predicate goes before their send there. Carry: R11-SEAM-actuation-writes (item 1)
2. The tail and re-cut must not raise `coord_footprint`: fold `coordinator.py:6106` to `coordinator.py:6116` into the one tail. If it cannot be paid, stop and ask before pushing. Carry: R11-SEAM-actuation-writes (item 2)
3. `heat_curve.py:346` `write_cap_per_day` is sized on the cycle interval; run `timing.py` with an offset entity and report the day's writes. Carry: R11-SEAM-actuation-writes (item 3)
4. `_async_peak_guard_transition` publishes its own displace; test a boundary under a held guard. Carry: R11-SEAM-actuation-writes (item 4)
5. `check_overdue` now runs before the follower in a cycle; test that an attempt stamped by the follower still clears its notice within one cycle. Carry: R11-SEAM-actuation-writes (item 5)
6. Measure `cells.py`'s unavailable row on the supply switch: `note_supply` records before the write. A non-zero count is a sibling for a carry, not this diff. Carry: R11-SEAM-actuation-writes (item 6)
7. A step narrower than a decile can round a mid into the next bucket; test the map's evidence bucket for the value sent. Carry: R11-SEAM-actuation-writes (item 7)
8. The DHW notice on a capped plant now asks for the entity's maximum; its text and the gate's doc table follow the behaviour. Carry: R11-SEAM-product-text
