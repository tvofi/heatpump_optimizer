# D12 — Generalization (round 7)

Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave fully
merged). Finder: Fable 5. Box: 8-core Apple M1, 8 GB, shared with the other
round-7 finders — every wall/CPU number here is provisional; only the counts
and ratios are contention-immune.

## Method

The tree already exposes five coordinator topologies (`coord_minimal`,
`coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`) and 49
plan `SCENARIOS`. Those leave a set of plant cells *uncovered at the
coordinator level*, and the D12 question is whether those cells are usable.
I inventoried the plant from the options and the topology slot table
(`topology._SLOTS`) and enumerated the installation axes: hydronic layout
(`none` / `manual` / `smart_write` valve; `no_valve` / `single_tank_valve` /
`two_tank_4way` / `valve_upper_direct_slab`), DHW present/absent, wood
present/absent (flag-only, probe, coil), solar/PV present/absent, on/off
(`heat_pump_switch_entity`) vs modulating (`compressor_freq_*`), and the
different control surfaces (climate, switch, number, smart_write valve).

For each cell I drove setup + one full solve cycle the way
`tests/entities.py` `collect`/`_honest_coordinator` and `_d801_publications`
do — `_update_current_state`, `async_run_optimization`, `_build_data_dict`,
then every platform's `async_setup_entry` — and counted failures on the
"usable" bar: setup does not complete, no plan publishes without a named
refusal, or a non-finite value is published. `grid.py` is the committed
instrument. `plant_conditioning.py` checks the other half of the bar — that
the solver does not invent a tank/zone/DHW/buffer channel the config omitted.

## Findings

### D12-01 — smart_write "flow" valve target saved on a single-zone install, then never actuates

**Severity:** medium (stop-rule class: bug, provisional).

**Claim.** A config with `two_zone_mode="off"` and the (unerasable) zone keys
still present passes the options-flow guard for `mixing_valve_write_target_kind="flow"`
— because that guard tests `current.get("upper_floor_thermal_mass")` instead of
the model's `two_zone_enabled` — and the saved flow target then issues **zero**
valve writes on every cycle, so the smart_write valve silently does nothing.

**Instrumented symbol:** `custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._command_valve_target`.

**Executed number** (`tools/audit/round7/D12/valve_flow_target.py`):

```
flow_target.two_zone_mode_off_writes = 0
flow_target.two_zone_mode_on_writes  = 1
indoor_target.two_zone_mode_off_writes = 1   (null control)
indoor_target.two_zone_mode_on_writes  = 1   (null control)
```

**Perturbation.** `two_zone_mode` `off -> on` (zone keys and `flow` target held
constant) moves the write count `0 -> 1`. The null control (`kind="indoor"`)
writes once under both modes, so the collapse is specific to `flow`.

**Mechanism.** "Is this install two-zone" is decided twice, divergently.
`ThermalParameters.from_config` honours the explicit `two_zone_mode` override
(`off` wins over the presence of `upper/lower_floor_thermal_mass` — keys the
initial flow writes into `entry.data` where the options flow cannot erase
them). The config-flow guard (`config_flow.py`, the
`flow_target_needs_two_zone` branch) tests only
`not current.get(CONF_UPPER_FLOOR_THERMAL_MASS)`, which is always False once
the initial flow has run. So a single-zone install (mode `off`) saves a flow
target, and `_command_valve_target` then hits its own
`mixing_valve_write_target_kind=flow needs two-zone` guard and returns without
writing, every cycle, with only a log line.

**Proposed fix scope.** Make the config-flow guard use the same two-zone
derivation as the model (call `ThermalParameters.from_config(merged).two_zone_enabled`
or test the explicit `two_zone_mode`), rather than the mass-key presence.

**Files.** `custom_components/heatpump_optimizer/config_flow.py` (the guard),
`custom_components/heatpump_optimizer/coordinator.py` (`_command_valve_target`).

## Non-findings (checked, and the number that showed it)

- **58 coordinator-level plant cells: 0 crashes, 0 non-optimal-without-refusal,
  0 non-finite.** `grid.py` (`RESULT usable_failures=0`) across the full
  hydronic-layout x DHW x wood x PV x on/off x modulating grid.
- **The solver does not invent a plant.** `plant_conditioning.py`
  (`RESULT invented_channels=0`): `wood_temp_trajectory` empty with no wood,
  `dhw_power_schedule` empty with `dhw=False`, `upper/lower_setpoints` empty in
  single-zone, `buffer_temp_trajectory` empty with no valve — each axis's
  channel is empty when the axis is absent and non-empty when present.
- **Single-zone two-tank is a documented gate, not a silent bug.** A single-zone
  wood install resolves to `single_tank_valve` (`two_tank_modelled` requires
  `two_zone` in `topology_layout_valid`) and `describe_setup` draws the wood
  tank with the honest "modelled as heat into the heat-pump tank" caption.
  This is a documented modelling limit, not a hidden invention.
- **`slab_shunt` cannot reach the model.** `from_config` drops it (not in the
  whitelist) and `topology_layout_valid` returns False; `layout_edges` only
  draws it in the catalog's non-selectable display.
- **On/off vs modulating actuation is guarded.** `_apply_action` (switch
  toggle), `_command_frequency` (number write, rate-limited, clamped) and
  `_command_valve_target` (climate/number write) each swallow their exceptions
  and log, so a missing/balky entity never breaks the cycle.
- **The `peak_threshold_kw` +inf is the documented "no capacity tariff" value**
  (golden.py note), the one non-finite published on every otherwise-finite cell.

## Harnesses

- `tools/audit/round7/D12/valve_flow_target.py` — the D12-01 number.
- `tools/audit/round7/D12/grid.py` — the cell inventory and fail count.
- `tools/audit/round7/D12/plant_conditioning.py` — the no-invented-plant check.

## Exposure

Empty. No `docs/` read for this dimension; no GitHub read.

## Not finished

None — the round is one finding plus a documented dry grid. The `load1`
figures in the RESULT blocks were taken on a busy shared box (load1 6.95-8.41);
the numbers the finding rests on are counts and therefore contention-immune.
