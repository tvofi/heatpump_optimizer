# Design note: R11-SEAM-actuation-writes

Extends the architect note, ADR-001 and ADR-004 (plan 50a932de3b2a). Code read at the base 107988b792139c60e3831cbd91cfe65c4db497b3; line citations are at that SHA. Predecessors: `R11-SEAM-kernel-step` at its handoff head e265279b8df87854e10ae549db9f07d2a021cac9 (`plan_step.py` there carries `plan_step_index` and `covering_index`; `pump_arbiter.py` reads them); `R11-SEAM-actuation-release` has no handoff head, so its approved design 349d6277f25fb6855b58395bcb7f055f2e40d86d is read as the shape. Findings read whole at 50a932de3b2a: `dev/audit/rounds/round11/D16/s1/findings/D16-s1-01.json` and its eight siblings, with the judge's rows in `dev/audit/rounds/round11/JUDGE.json`.

**Revision 2**, answering design-verdict 1c3e532e352504c676bad567a5ce2b3f74370e7c on 4cfb341a0dd419b39166ed3e85d49fca202829db. Point 1 (blocking, confirmed at `pump_arbiter.py:2056`): section 2's arming, invariant 6 and the no-switch test in section 5. Note on the pending retry: section 2's step record, Notes 9. Note on the concurrent cycle: section 2's tail lock, invariant 7, Notes 10. Nothing else moved.

## 1. Owning seam

Actuation, one owner per concern, none needing two:
- **When a step's writes are re-derived**: the step tick in `pump_arbiter.py` (`pump_arbiter.py:2065` `supply_tick`), the only per-minute boundary detector, on `plan_step_start`. Its arming, its step record and its tail lock are the arbiter's, on `ArbiterState`.
- **A value on an entity's step and range**: `inputs.py` (`inputs.py:658` `bounded`, `inputs.py:728` `_on_step`). Callers: `setpoint_check.py`, the frequency target.
- **The arbiter's rows, record and loop**: `pump_arbiter.py` (`desired`, `_write`, `_lead_mode`, `_feedback`).
- **The disinfection follower**: `legionella.py` (`async_track_cycle`).
- `coordinator.py` only calls. `tests/seam_map.json` maps coordinator methods only; every method touched is in `core`.

## 2. Shape

**Step boundary (D16-s2-01, D16-s2-02).** `SupplyWiring` gains two plain callables: a re-cut and the write tail. The tick has two halves, the step half first.
- **Arming.** `note_supply` arms the tick on every install: the return at `pump_arbiter.py:2056` leaves the arming and moves into the tick, ahead of the supply half only. With no `heat_pump_switch_entity` the tick runs the step half and returns: `held.supply` is not moved and `wiring.write` is not called, so `supply_hold.py`'s hold and its `supply_held` learner freeze never arise from a tick on an install with no switch. `release_supply` drops the one listener as today.
- **Step record.** `ArbiterState` gains one pair: the step the action was last cut or refused for, and a pending flag. The step half runs when that step is not `plan_step_start(now)` or the flag is set; the guard at `pump_arbiter.py:2077` (`held.supply[0] == step`) gates the supply half only. The one cut definition stamps the step at the cut, the solve's too, so a cycle that cuts in one step and writes in the next is re-cut by the next tick.
- **Re-cut.** Where `step_supply`'s gate holds (`pump_arbiter.py:2008`: Auto or Economy, plan fresh, no experiment), the entry is not released and `plan_step_index` covers now, the action is cut again by the statement at `coordinator.py:6469` (`adopt_plan` over `get_current_action`) and the boost overlay re-applied (`coordinator.py:6097`). One definition, read by the solve and the tick. Gate and cut are one synchronous run on the live plan: `coordinator.py:6458` assigns the plan and `coordinator.py:6469` cuts it with no await between, so a re-cut never reads a plan older than the action. A refused gate stamps the step, clears the flag and runs no tail: Off and a stale plan stay the release group's.
- **Tail**, in this order, one definition read by the cycle and the tick: disinfection follower, `async_publish_current_action`, `_command_frequency`, `_command_valve_target`, `_async_drive_pumps`. The valve call leaves `coordinator.py:6499`; the frequency and pump calls leave `coordinator.py:6112`. The tail returns whether a writer's rate limit refused a target that differs from its record; today only the frequency writer can (`FREQ_WRITE_MIN_INTERVAL_S`), and it returns that fact in place of nothing. The tick stores it as the pending flag; a pending minute re-checks the gate and runs the tail, without a re-cut inside the same step.
- **Tail lock.** `ArbiterState` gains one lock taken only around re-cut plus tail. The cycle awaits it for its tail; the tick returns when it is held, leaving the record, so the next minute decides again and ticks never queue. Nothing under it awaits `held.lock` or reaches `apply`, and no restore awaits it (release invariant 3).
- `async_observe` (`legionella.py:552`) stops calling `async_track_cycle`; the tail calls it with the tank reading, after adoption, in every mode, so `legionella.py:350` reads the action of the step it lands in.
- The MQTT publish is skipped at a boundary when the displace integer and the on flag equal the last sent (`coordinator.py:7707` `_ecl110_current_displace`); the cycle publishes as today. Each writer keeps its rate limit.

```
tick: lock held -> return
      step half (new step or pending): gate -> re-cut -> tail: follower, publish, frequency, valve, pumps -> record
      supply half (switch configured, new step or held): step_supply -> wiring.write
cycle: observe -> solve -> adopt (stamps step) -> experiment -> overlay -> _apply_action -> lock: tail
```

**Grid and range (D16-s1-01, D12-s3-02).** `inputs.py` gets one public function: a number on the entity's own step inside its own min and max, minimum rounded up, maximum down, no unit conversion. `write_setpoint` reads it at `inputs.py:728`; the frequency target reads it in place of the clip at `coordinator.py:10861`, before the dedup, and the owner records the value sent. `setpoint_check.py:169` asks the entity's grid (`setpoint_grid(...).bounded`, rounding up, `hi` the hard maximum) in place of `quantise_setpoint_c`: the function the arbiter bounds by, so Fix and arbiter cannot disagree. `repairs.py` is unchanged.

**Unavailable (D16-s1-05).** One predicate in `inputs.py`: the entity has a state and it is not `unavailable`. `_write` (`pump_arbiter.py:1598`) returns on it before the call, so nothing is recorded or reported. `unknown` still writes: Home Assistant delivers to it. `FakeServices.async_call` (`tests/harness.py:227`) drops a call whose target entity reads `unavailable`, pinned by a `tests/ha_contract.py` row with expect both.

**Lead mode (D16-s2-03).** `_lead_mode` drops the mode record when `_observed` reads a mode that `_differs` from it, then writes; no miss is counted. An unreadable select keeps the record.

**Indoor boost (D16-s1-03).** `desired` computes the boost fact for both units (`pump_arbiter.py:1305`), tolerating no coordinator. `_space_target`'s indoor branch under a boost bounds the action's `setpoint`, which `boost.overlay` and the Boost row set to the band top; the misdeclared-unit test still reads the plan's room value.

**Gate (D16-s1-02).** The space row with no Heating option (`pump_arbiter.py:1310`) writes the lower of `DHW_GATE_C` and the tank reading plus the read start hysteresis (zero where none is read), rounded down inside the entity's range; with no tank reading, `DHW_GATE_C` as today. `dhw_gated` compares against the record, so it follows.

**Floor loop (D16-s2-04).** In `_feedback`, a stop on a qualifying pass (`pump_arbiter.py:1020`) keeps the run and its target instead of resetting; stopped passes are zero samples for at most one `FEEDBACK_WINDOW` per stop. `_note_stop` is still called. Any non-qualifying pass resets as today. `thermal_model.py` is unchanged.

**Invariants.** (1) After a boundary's tail, every step-derived command equals the covering step's, or its writer is rate-limited and the flag is set. (2) No number leaves off the entity's step or range. (3) A record exists only for a delivered write. (4) Release invariant 2 holds: this group adds no record a restore does not empty. (5) Entities, services, payload keys unchanged. (6) Invariant 1 does not depend on a supply switch; the switch is written only where one is configured. (7) One tail runs at a time, and an action is replaced only by a cut of the live plan.

## 3. Alternatives

- **A second listener for the step half, armed by `_listen`**: `_listen` is reached only through `apply`, and `apply` drops its listeners when the duty mode is off (`pump_arbiter.py:1857`), so a curve-only install loses it; two detectors of one boundary.
- **Arming only where a step-derived writer is configured**: a second copy of five writers' configuration tests, stale after an options change; an unconfigured writer already returns at its own first line.
- **`held.supply` as the step record**: the supply half leaves it unmoved where `step_supply` does not speak, so the step half would run every minute; and it is not moved at all with no switch.
- **The tick awaiting the tail lock**: a send blocked past a minute queues one tick per minute behind it.
- **A timer per writer**: four boundary detectors and four copies of the gate at `pump_arbiter.py:2008`; `coordinator.py` grows per writer.
- **Each writer reads its plan series by index**: bypasses `boost.overlay` and the experiment override, which only the action carries; two sources for one command.
- **A new step-tick module**: moves `held.supply` off `ArbiterState`, which the release design's supply restore reads; a new tracked file for one function.
- **The record check inside `_write` for every slot** (D16-s2-03's general form): a pass inside `ECHO_GRACE_S` rewrites a value not yet echoed, and `_note_sent` already drops records on purpose.
- **`hold` before the lead**: it compares set-points the pump reports as its own while off (`_pump_off`) and counts misses toward `ISSUE_IGNORED`.
- **Quantising in `freq_control.py`**: a second on-step rule beside `inputs.py:600`, the class N-step-grid.
- **A larger default lift** (D16-s2-04's perturbation): fixes one plant, moves every other plant's floor.

## 4. Sibling sites

- `python3 tools/audit/enumerate.py d16-writes | grep '^write'`: eight. Covered: `_command_frequency`, `_write`, `write_setpoint`; boundary-driven: both `publish_ecl110_topics` sites, `_async_set_pump`, `_disinfection_switch`. `switch_supply` keeps the supply half.
- The arming rule, `grep -n 'async_track_time_interval(' custom_components/heatpump_optimizer/pump_arbiter.py`: two. `pump_arbiter.py:2062` fixed; `pump_arbiter.py:2168` is the arbiter pass, which reads no plan step.
- D16-s1-05's rule, `grep -n 'held.written\[slot\]\|_pump_commanded\[\|_freq_last_write = \|_valve_commanded_target = ' custom_components/heatpump_optimizer/*.py`: four records. The arbiter's is fixed; the other three move to owners in the release group and read the same predicate before their send. `disinfection.py:215` already refuses an unread flag.
- D12-s3-02's rule, `grep -n 'write_setpoint(\|quantise_setpoint_c(\|write_setpoint_c(' custom_components/heatpump_optimizer/*.py`: `setpoint_check.py:169` fixed; `inputs.py:776` receives arbiter values already bounded and restore values read from the entity.
- Out of scope: `optimizer.py:6592`, a covering-step copy with no end rule. The re-cut calls it only where `plan_step_index` covers now, so the two cannot disagree there; the file is not this seam's.

## 5. Evidence, by file

- **Failing tests first, `tests/features.py`**, each with the finder's null: beside `tests/features.py:1059` an off-step frequency (null: 0.5 Hz step); beside `tests/features.py:47179` a Fix on an entity capped under the floor (null: range holding it); beside `tests/features.py:85892` an unavailable select leaves no record (null: available), and a select moved while off is led (null: unmoved); beside `tests/features.py:85844` a boundary between cycles re-cuts and writes frequency, displace and valve, run twice, with `switch.hp` configured and with no supply switch (nulls: an unchanged step writes nothing; with no switch no `switch` call is made and `supply_held` stays false); there too a frequency write refused by its interval is sent by a later minute's tick (null: no refusal, no later write), and a tick fired while the cycle's tail holds the lock writes nothing and the next minute's does (null: lock free); beside `tests/features.py:40530` the switch on inside the booked window (null: none booked); beside `tests/features.py:91198` a stop on a qualifying pass keeps the run (null: a non-qualifying pass resets); the cold-tank gate (null: tank at 48); the indoor boost (null: no boost).
- **Finder harnesses, both ends, at 50a932de3b2a**: `dev/audit/rounds/round11/D16/s1/cells.py --no-gates` (clause_grid, cold_tank_charge, boost_indoor_between, unavailable_recorded to 0; nulls unchanged); `dev/audit/rounds/round11/D16/s2/timing.py` (three stale shares to the rate-limit residual, reported, with and without a switch entity in its config; `--phases 1` cell 3530 to 0; `--interval 15 --phases 0` stays 0); `dev/audit/rounds/round11/D16/s2/disinfect.py`; `dev/audit/rounds/round11/D16/s2/effect.py` (starts at lift 8 and 10 down, lifts 2 to 6.5 at one start); `dev/audit/rounds/round11/D12/s3/repairs_surfaces.py` (bad_fix_writes 0).
- **Score and ratchet**: `tools/audit/archscore/` before and after; `coord_footprint`, `private_cross_module`, `layer_violations` not above the merge base.
- **Goldens**: no solver path changes; both claim files byte-identical.
- **Mutation targets**: the switch condition's place in the tick (back on the arming must fail the no-switch test); the step half's new-step test, the pending flag's set and clear, the re-cut gate and the stamp at the solve's cut; the lock-held return; the on-step function's two rounding directions; the availability predicate; the lead's record drop; the gate's minimum; the kept run and the one-window bound; the follower's position after adoption.

## 6. Hot files, position, decisions

Hot: `pump_arbiter.py`, `coordinator.py`, `inputs.py`, `legionella.py`, `setpoint_check.py`, `freq_control.py`, `tests/harness.py`, `tests/ha_contract.py`, `tests/features.py`. Third on the actuation chain, after both predecessors merge; `R11-SEAM-product-text` follows. Receives release invariant 2 with its control (a valve write after Off then On is sent). If the stub change must register with a base-pinned grader: p1 is `tests/harness.py` and the contract row, p2 the production change.

- decision: orchestrator. `inputs.py`, `tests/ha_contract.py` and `tests/features.py` join the roster's hot files; `heat_curve.py`, `disinfection.py`, `thermal_model.py` and `repairs.py` leave them.
- decision: owner. D16-s2-04 changes the feedback loop on every install with the option on; the alternative is a per-plant setting.

## Notes for the fixer

1. Re-read the release group's merged diff first: the frequency and valve tails move to `freq_control.py` and `mixing_valve.py`, and the predicate goes before their send there. Carry: R11-SEAM-actuation-writes (item 1)
2. The tail and re-cut must not raise `coord_footprint`: fold `coordinator.py:6106` to `coordinator.py:6116` into the one tail. If it cannot be paid, stop and ask before pushing. Carry: R11-SEAM-actuation-writes (item 2)
3. `heat_curve.py:346` `write_cap_per_day` is sized on the cycle interval; run `timing.py` with an offset entity and report the day's writes. A write the day's cap refuses is not pending. Carry: R11-SEAM-actuation-writes (item 3)
4. `_async_peak_guard_transition` publishes its own displace; test a boundary under a held guard. Carry: R11-SEAM-actuation-writes (item 4)
5. `check_overdue` now runs before the follower in a cycle; test that an attempt stamped by the follower still clears its notice within one cycle. Carry: R11-SEAM-actuation-writes (item 5)
6. Measure `cells.py`'s unavailable row on the supply switch: `note_supply` records before the write. A non-zero count is a sibling for a carry, not this diff. Carry: R11-SEAM-actuation-writes (item 6)
7. A step narrower than a decile can round a mid into the next bucket; test the map's evidence bucket for the value sent. Carry: R11-SEAM-actuation-writes (item 7)
8. The DHW notice on a capped plant now asks for the entity's maximum; its text and the gate's doc table follow the behaviour. Carry: R11-SEAM-product-text
9. The supply half returns at `pump_arbiter.py:2077` once `held.supply[0] == step`, so the pending retry reads only the step record's flag, never `held.supply` or `supply_held`. Null control: a refused frequency write retried by the next minute's tick, and no retry once it is sent. Carry: R11-SEAM-actuation-writes (item 9)
10. Test a tick queued across a solve: fired between `coordinator.py:6469` and `_apply_action`, in the same step it changes nothing, and across a boundary the action the cycle then writes is the newer step's, cut from the new plan, with `boost.apply` at `coordinator.py:6097` landing on an action the re-cut already overlaid and changing nothing. A re-cut after `_adopt_system_identification` must be refused by the gate. Carry: R11-SEAM-actuation-writes (item 10)
