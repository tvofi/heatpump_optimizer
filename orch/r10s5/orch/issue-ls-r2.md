Part of #2248. Filed by the R10-LIVESTATE pull request (design `dev/programme/designs/R10-LIVESTATE.md`, item ls-r2). These are **unprobed leads, not findings**: no harness has shown any of them lose a write.

## The leads

The constructor spawns seven store loads, and the first refresh runs while they are in flight (`custom_components/heatpump_optimizer/__init__.py:302` `HeatPumpOptimizerCoordinator(`, `:318` `async_config_entry_first_refresh`). Each load below has a per-cycle writer that adds to the state the load later replaces. Whether that writer runs inside the first refresh, before its load resolves, is not established. If it does, the loss is one cycle's increment.

| load | per-cycle writer (line numbers at the R10-LIVESTATE head; re-anchor by name) |
|---|---|
| `_async_load_thermal_learning` | `_async_learn_buffer_cooling` (`coordinator.py:5162`) |
| `DhwLearner.async_load_profile` | `async_learn_dynamics` (`coordinator.py:6461`) |
| `legionella.py` `async_load` | `async_track_cycle` (`coordinator.py:6473`) |
| `_async_load_price_model` | `_async_learn_price_shape` (`coordinator.py:5633`) |
| `_async_load_energy_totals` | `self._energy_totals["space_energy_kwh"] += space_energy` (`coordinator.py:10208`) |
| `_async_load_ledger` | `self._ledger.add(` (`coordinator.py:10219`) |
| `_async_load_accuracy` trackers | `self._accuracy.record(sample)` (`coordinator.py:9944`) |

## Probe recipe (item ls-r1's, per lead)

Replace the loader's store with a stub whose `async_load` waits on an `asyncio.Event`. Spawn the load, yield once, run one coordinator cycle (the writer) as a task, set the event, await both.

- **Metric:** the writer's increment is absent after the load resolves — 1 (lost) or 0 (kept), per lead.
- **Null control:** the same cycle run after the load resolves — must read 0. A lead whose null is not 0 is a broken probe, not a finding.
- **Precondition to establish first:** whether the writer runs in the first refresh at all (it may be gated on a sensor history or a previous-cycle value the first refresh lacks). A writer that cannot run before its load resolves is closed by that reading, with the gate cited.

## Fix shape, if a lead reproduces

The writer awaits its store's `async_wait_for_read()` before writing, as R10-LIVESTATE made `async_apply_manual_plan` and `async_clear_manual_plan` do for the manual plan store. Not a per-lead flag.

## Out of scope here

The user-command writers that race a load (house heat loss, DHW `cooling_samples`, the snapshot model) are item ls-r1, carried to R10-PARAMS-OWNER.
