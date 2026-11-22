Design review: approve 57d5d278f0c5dc55b99c214f66abf4babca3fefa

Delta review of design/R11-OWNER-FAULT-HOLD 6244553e45..57d5d278f0, against the revise points R1-R3 and the seven carries of design-verdict 207901803f. Code was read at origin/main 3a98735a7e. The serial order, per the orchestrator's ruling, is FLOWCAP, FROST, FAULT, LEGS, then KICK.

## Prior points
- R1 resolved, with a different placement. The consult sits in `heat_curve.publish` (heat_curve.py:269), not in `async_publish_ecl110_command`. `publish` has one caller, coordinator.py:7671, inside `async_publish_ecl110_command`. So the cycle, the peak-guard engage (coordinator.py:8829) and its release (8840) all reach it, and every downstream displace path, `publish_ecl110_topics`, `write_displace` and `write_persistent`, sits below it. Coverage is the same as at the coordinator method, and it costs no coordinator-class line. `heat_curve` importing the leaf `fault_hold` makes no cycle: `fault_hold` imports const, entry_config, inputs and issues, and none of those imports `heat_curve`. Test 6 covers the peak-guard engage. The placement is sound, and alternative 4 states the trade.
- R2 resolved. This consult reads with `read_bool(..., max_age_minutes=UNBOUNDED)` (inputs.py:94). The 60-minute horizon still governs only the learner freeze. `since` is re-seeded from `last_changed` on the first consult after On and after a reload, and it is kept through unusable readings. Test 7 pins Off→On and a reload after 70 min on an on-change source, with the fresh-off null control.
- R3 resolved. Each over-limit file names its own payment:
  - pump_arbiter.py moves the step ledger to `duty_ledger.py`. It imports only `plan_step`, and pump_arbiter passes `ran`, `dhw_mode` and `start_below` in, so there is no cycle.
  - config_flow.py replaces three helpers with `_select`. `_meter_source_selector`, `_freq_mode_selector` and `_solar_source_selector` (config_flow.py:1174-1214) each re-spell `_select` (1163). Their four `_F` rows (1745, 1748, 1750, 1758) take `_select(...)`. This is a real deduplication.
  - coordinator.py has a named fallback.
  - The mandate route is settled before the push.
- The seven prior carries are taken into the note's behaviour, tests or carries: entry-released, supply-after-clear (the held mark), ignored-repair, unload-row, onset-step (in the docs), cc-headroom and bundle-latch-count.

## Payment collisions, checked
- FLOWCAP pays with a docstring paragraph in `config_flow._number` (config_flow.py:652). It also moves `_silent_rows` and `_inside_silent` to quiet_windows.py; those two are in pump_arbiter.py:1209-1258, not config_flow.py. This note pays in config_flow.py:1163-1214 and in pump_arbiter.py's ledger (1847-1923). No line is shared.
- MODE-LEGS moves `_valid_months_spec` (config_flow.py:1115). FROST pays with `_write_supply`'s debug branch. STEP-KICK moves `FLOW_INLET_KEYS`. None of these overlaps this note's moves. FROST's `_verdict` branch lands before this group and moves with the ledger.

## Notes for the fixer
- Carry: R11-OWNER-FAULT-HOLD (item publish-released). `heat_curve.publish` has no `entry_released`, so a peak-guard transition after unload can raise `pump_fault_hold` again. Pass `released`, or return before the consult once the entry is released.
- Carry: R11-OWNER-FAULT-HOLD (item reported-displace). `async_publish_ecl110_command` sets `_ecl110_last_payload` and `_ecl110_current_displace` (coordinator.py:7668-7669) before `publish` returns. Under the hold, the reported displace (coordinator.py:8077-8082) is one that was never sent. State this, or let diagnostics show the hold.
- Carry: R11-OWNER-FAULT-HOLD (item duty-off-latch-age). `gate` and `cutoff_hook` read `held(entry)` without a read. With duty off, the latch moves only at the cycle's consults, so the step tick and the cut-off lag at both edges by up to one optimization interval. Let both call `holding`, or state the lag in the docs.
- Carry: R11-OWNER-FAULT-HOLD (item fallback-private-reach). The coordinator fallback `supply_hold.write_gated(coord, on)` would read `_pump_signals` and `_ctx._config`, and `coordinator_private_reach` is at 0/0. Pass both values in from the class.
- Carry: R11-OWNER-FAULT-HOLD (item ledger-constants). `TANK_RISE_C` and `RUN_SETTLE` (= `_TICK`) live in pump_arbiter.py:258 and :271. Move them to `duty_ledger` or pass them in, so the no-cycle claim holds.
- Carry: R11-OWNER-FAULT-HOLD (item publish-config). `publish` receives an `EntryConfig`, while `holding` reads the slot through `InputReader(hass, mapping)`. Hand it the entry's mapping, not the dataclass.

Seat token count: not reported by the harness.
