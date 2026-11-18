# Class sweep: N-unreleased-hold (round 11, D14 steps 3-4)

Mechanism: an actuator the optimizer took over has no release or restore owner on some exit (stale plan, Off, unload, remove, failed restore), so the device keeps the optimizer's last write.
Ledger status: not yet a key of `dev/audit/config/bugclasses.json` at the register head; `barriered: false`.
Findings: D16-s1-04, D16-s3-01, D16-s3-02 (high), D16-s3-04 (medium).

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/enum_unreleased_hold.py`. The universe is every actuator write site `tools/audit/enumerate.py d16-writes` lists (8) crossed with every exit: off, unload, remove and duty-mode change (each also mid-disinfection, and Off on the Modbus select), the stale plan, and a failed restore. The D16 finders' harnesses give the behaviour, run on this tree: `D16/s3/m6_restore.py` (per exit and entity, left off its baseline or not), `D16/s1/cells.py` (stale plan), `D16/s3/m5_holds.py` (failed restore while Off). Each held cell is mapped to its owning write symbol; cells with the same owner and exit fold into one seam.

At the register head: held_cells=51, seams=24 (full listing: `enum.out` in the report directory).

Controls:
- positive: re-finds every judged cell (D16-s1-04, D16-s3-01, D16-s3-02, D16-s3-04; see JSON `controls`);
- null: `--null` reads the harnesses' null arms (commands equal each baseline): held_cells=0, seams=0;
- perturbation: `--perturb all` (m6's in-memory fixes) moves seams 24 -> 9; `m6_restore.py --perturb memo` alone (one change: drop the disinfection hold before `release()`) moves the new seam's cells 1 -> 0.

## Dispositions

Instances (probes fail at the register head):

| file::symbol | exits | probe | beyond finding |
|---|---|---|---|
| `custom_components/heatpump_optimizer/pump_arbiter.py::release` | unload, remove (and the unload inside a duty-mode change) while the disinfection hold is live | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m6_restore.py  RESULT unrestored_unload_disinfecting__number.dhw_set=1 and unrestored_remove_disinfecting__number.dhw_set=1 (fail; tank left at 60); null_unrestored_*=0; --perturb memo -> 0 | true |
| `custom_components/heatpump_optimizer/pump_arbiter.py::switch_supply (stale-plan exit, via coordinator._apply_action)` | stale plan | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s1/cells.py --no-gates  RESULT baseline_switch_off=5 (fail) | false |
| `custom_components/heatpump_optimizer/pump_arbiter.py::_arbitrate (MODE_OFF branch) / _write` | off (Tuya, Modbus, disinfecting) | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m6_restore.py  unrestored_off__select.pump_mode=1, unrestored_off_disinfecting__number.dhw_set=1, unrestored_off_modbus__number.dhw_set=1 | false |
| `custom_components/heatpump_optimizer/pump_arbiter.py::switch_supply` | off, unload, remove, duty-mode change | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m6_restore.py  unrestored_<off|unload|remove|duty_change>__switch.hp=1 | false |
| `custom_components/heatpump_optimizer/coordinator.py::HeatPumpOptimizerCoordinator._command_frequency` | off, unload, remove, duty-mode change | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m6_restore.py  unrestored_<arm>__number.freq=1 | false |
| `custom_components/heatpump_optimizer/coordinator.py::HeatPumpOptimizerCoordinator._command_valve_target` | off, unload, remove, duty-mode change | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m6_restore.py  unrestored_<arm>__number.valve=1 | false |
| `custom_components/heatpump_optimizer/coordinator.py::HeatPumpOptimizerCoordinator._async_set_pump` | off, unload, remove, duty-mode change | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m6_restore.py  unrestored_<arm>__switch.vvc=1 | false |
| `custom_components/heatpump_optimizer/off_restore.py::async_restore (failed restore, no retry while Off)` | failed restore | PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s3/m5_holds.py  writes_again_off_restore_failed_while_off=0 and writes_again_off_restore_neutral_failed_while_off=0 (fail; heat-curve offset left at 3 K too) | false |

Beyond the findings, one seam: **`pump_arbiter.release` on unload or remove during a disinfection cycle** leaves the tank set-point (`number.dhw_set`) at the cycle target 60. `release()` writes `desired(...)` while the disinfection memo is still live, so the baseline row it writes still carries the cycle's tank target; after unload or remove nothing lowers it. D16-s3-01 judged this only for Off, through `_arbitrate`'s MODE_OFF branch, which is a different owner. The duty-mode change has the same cell, because it goes through the same unload.

The four unregistered actuators also hold across a **duty-mode change**. That is D16-s3-02's seam (no restore owner at all), reached through the unload the options save performs. It is listed under that judged site, not counted again. D16-s3-04's failed restore also leaves the heat-curve offset at 3 K (m5 `writes_again_off_restore_neutral_failed_while_off=0`), through the same `async_restore` path.

Guarded / not applicable:

| seam | disposition | reason |
|---|---|---|
| heat_curve.publish_ecl110_topics / heat_curve.write_persistent x duty-mode change (mqtt ecl110 topics, number.offset) | not applicable | the unload inside the change restores them (unload arm: 0); the harness's reloaded observe-mode coordinator, given the old plan, writes them again. That is a question of what observe mode may write, not a hold left without a release owner; left as a lead for D16, not counted |
| heat curve, heat-curve MQTT, space set-point x off / unload / remove | guarded | off_restore consumers registered at import (heat_curve, heat_curve_mqtt, pump_arbiter_space); m6 arms 0 for these entities |
| disinfection switch (switch.dis) x every exit | guarded | DisinfectionSwitch.release / release_blind on every _drive_switch pass and on unload; m6 arms 0 |
| arbiter slots (mode, tank, water set-point) x unload / remove outside disinfection | guarded | pump_arbiter.release writes the baseline row on unload; m6 unload/remove arms 0 for the arbiter slots |
| other actuators x stale plan | guarded | cells.py: clause_stale=0, clause_freq/valve/circ/mqtt=0 rows; only the supply switch holds (judged) |

`instances` = 1 (beyond the findings); `instance_list` also carries the seven judged owners with `beyond_finding: false`.

## Barrier (proposed)

A `tests/` property over the m6 matrix: for each actuator a write site owns, each exit arm ends at the baseline, or the entity is on an allow-list with its reason. It costs about the m6 run (a couple of minutes of gate CPU on this box), so it should run nightly rather than per PR, with a static half in the per-PR gate: every `d16-writes` site must have an `off_restore.register_consumer` or a named release owner.
