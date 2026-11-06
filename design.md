# R10-COMBI-TANK design note (designer seat)

The group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/r10-combi-tank` and never merges. Issue #3225 (outside user). The body and its one comment were read through the GitHub MCP at seat time. **No finder harness: owner report.** The evidence is the issue's setup, quoted in the brief. Step 6 names the synthetic fixture that reproduces it.

**Read at.** Base `198b8f7ed21fdd10dc3407aa95b92f906b6bb27a`, which is `origin/main` at seat time. The group has no `after` edge, so there is no predecessor head. Carry context: `a7a683d1` (`BODY.md`, r10-demand-overbook) and `dev/audit/rca/R10-RCA-BUFFER-STORE.md`.

## Premise, read at base

- **Two independent stores.** `ThermalParameters` holds `buffer_tank_volume` and `dhw_tank_volume` as separate masses. Each has its own UA: `buffer_tank_heat_loss_coefficient` and `dhw_tank_heat_loss_coefficient` (thermal_model.py:601-770).
- **The trajectory moves them separately.** `ThermalModel.simulate_trajectory_with_dhw` (thermal_model.py:4355) runs `simulate_step` for space, which moves `buffer_tank_temperature`, and then `simulate_dhw_step` (3130) on `dhw_temperature`. P_dhw never touches the buffer. The only DHW↔buffer text is a comment at 3203.
- **The DHW plan does not see the buffer.** DHW is planned as fixed blocks by `DhwPlanner._build_dhw_requirements` (dhw_planner.py:933) on its own tank simulation. `_optimize_with_dhw` (optimizer.py:4964) then solves space around those blocks and iterates the split.
- **Actuation follows the DHW plan.** `pump_arbiter.py:346-374` commands DHW mode from `dhw_power_schedule`.
- **The topology catalog is space hydraulics only.** `topology.LAYOUTS` (topology.py:348-388) and `const.topology_layout_valid` (const.py:417) take no DHW input. The DHW edge `("heat_pump","dhw_tank")` rides every layout (topology.py:466). The nearest DHW option, `dhw_wood_coil_enabled` / `dhw_coil_active` (thermal_model.py:314-327), is a boolean predicate beside the layout, not a layout key.
- **Nothing honest is configurable.** Both real sizes count 572 l twice. The reporter's workaround (`buffer_tank_volume: 10`) falls below `BUFFER_STORE_MIN_VOLUME`, so `buffer_is_store` is false (thermal_model.py:286) and the tank is never pre-charged for heating.
- **One probe, two slots.** Both slots read the same entity. `_update_current_state` (coordinator.py:6550-6568) seeds each field from its own slot. No code compares the two entity ids, and none needs to.
- **Datasheet loss is in range.** 3.1 kWh/24 h at DIN 4753 (ΔT 45 K) gives UA 2.87 W/K. At the 25 K reference that is 0.108 K/h, inside `buffer_cooling_rate_bounds(572)` = 0.031–1.25 K/h. The prior is 0.156 K/h. So the user can enter the datasheet rate without a new field.

## Owning seam

**`custom_components/heatpump_optimizer/thermal_model.py`** owns the shared-store physics and its one predicate. That is the existing pattern of `two_tank_modelled` and `dhw_coil_active`. Every other module only reads `params.combi_tank_active` or calls the new step:

- `optimizer.py`: the co-solve flux exchange.
- `dhw_planner.py`: the planner's tank step, floor and ceiling.
- `coordinator.py`: orchestration only — the seed and the learner gates. Its seams are `_update_current_state` (core) and `_async_learn_buffer_cooling` (learning) in `tests/seam_map.json`.
- `config_flow.py`, `entry_config.py`, `const.py` and `topology.py`: the option and its display.

Only one owner computes, so this is not a two-owner design.

## Shape

**The model: one mixed node.** The DHW is the buffer water, seen through the exchanger. This is not a new layout key.

- `const.py`:
  - `CONF_DHW_COMBI_TANK_ENABLED = "dhw_combi_tank_enabled"`, default `False`.
  - `COMBI_DHW_APPROACH_K: Final = 5.0`. This is the fresh-water exchanger's outlet deficit against the tank. It is a constant beside the coil's `DHW_WOOD_COIL_EFFECTIVENESS` until a real exchanger is measured, and it errs toward promising less hot water.
- `ThermalParameters`:
  - a new field `dhw_combi_tank_enabled: bool`;
  - `combi_tank_active = dhw_combi_tank_enabled and dhw_enabled and buffer_is_store and not dhw_coil_active` (a coil heats a *separate* DHW tank, so the two are exclusive);
  - wired in the config loader beside `dhw_wood_coil_enabled` (thermal_model.py:1050-1055).
- `ThermalModel.combi_tank_step(tank_c, p_dhw_thermal_kw, dhw_draw_kw, exo_kw, ambient_c, dt_h) -> float`. This is the one balance, `C_buf dT = (P_dhw - draw + exo - UA_buf (T - T_amb)) dt`, using `_buffer_capacity(p)` and `buffer_tank_heat_loss_coefficient`. It is clamped at `min(buffer_max_temp, dhw_max_temp)`. The standby loss is booked once: in combi, `dhw_tank_heat_loss_coefficient` is never read. `dhw_tank_volume` is ignored, and diagnostics show it as unused.
- **The space steps take an exogenous tank flux.** `buffer_exo_kw` is a per-step series, default `None`, which keeps non-combi installs byte-identical. It is added to the buffer balance in all three sites (step 5). In combi it carries `P_dhw_thermal - dhw_draw` for each step.
- **The trajectory.** In combi, `simulate_trajectory_with_dhw` passes `buffer_exo_kw` into the space step. It sets `dhw_temperature := buffer_tank_temperature` after each step instead of calling `simulate_dhw_step`. So `dhw_temp_trajectory` equals `buffer_temps` elementwise, and that equality is an invariant.

**The solver: exchange fluxes across the iteration that already exists.** In combi, `_optimize_with_dhw`:

1. gets `space_net_kw[i]` (valve charge in minus valve draw out, loss excluded) from the space solve's simulated buffer flows;
2. passes it to `planner._build_dhw_requirements(..., tank_exo_kw=space_net_kw)`. The planner's tank simulation calls `combi_tank_step` with that series. This replaces `simulate_dhw_step`'s `draw_power` path for combi only.
3. passes `dhw_net_kw` back into `solve_space`.

The first pass uses `space_net_kw = 0`. The existing iteration cap holds, and the fixer reports the iteration count per arm. There is no new objective term and no buffer floor penalty: none exists at base, and adding one would be a parallel mechanism.

The DHW floor and ceiling in combi:

- `floor_temps` (dhw_planner.py:874) adds `COMBI_DHW_APPROACH_K` inside windows;
- the DHW top (thermal_model.py:3094) uses `min(dhw_max_temp, buffer_max_temp)`.

```
probe(1250mm) ─► seed T ─► buffer_tank_temperature = dhw_temperature = T
                              │
 DhwPlanner(tank_exo=space_net) ─► P_dhw blocks ─► pump_arbiter DHW mode (unchanged)
          ▲                                │ dhw_net = P_dhw_th - draw
          └── space_net ◄── solve_space(buffer_exo=dhw_net) ◄─┘   (existing split iteration)
```

**Sensors and the seed (owns R10-BUFFER-STORE carry 1).**

- In combi the tank has one state. A pure helper `combi_tank_seed(buffer_c, dhw_c, open_loop_c)` in `thermal_model.py` chooses, in order: the buffer reading, else the DHW reading, else `_open_loop_plan_value(result, "dhw_temp_trajectory", now)`, else `None` (keep the state).
- `_update_current_state` assigns the result to both fields. With the reporter's single probe, the DHW seed is therefore **measured**, not open-loop. The same probe in both slots, or only one slot filled, both work. The `dhw_temp_entity`-truthiness reads (topology.py:813-815) treat the buffer probe as the DHW probe in combi.
- Mean-of-two-probes (top and bottom wells) and a two-node model wait until the user adds probes; see A4.

**Learners in combi** (coordinator.py:6656-6664):

- `dhw_learning.async_learn_dynamics(tank)` is skipped. Valve draws on the shared probe would otherwise be booked as DHW usage (`async_fold_draw_stats`) and DHW standby. Usage falls back to the configured profile.
- The fixer reads `_async_learn_buffer_cooling` (coordinator.py:5420-5494). If its sample gate admits intervals with a planned DHW draw, it gets the same skip on those intervals. Otherwise it stays as it is.
- `legionella.async_observe` is unchanged.

**The option.**

- An `_F("hot_water", CONF_DHW_COMBI_TANK_ENABLED, ..., bool)` row, patterned on config_flow.py:1703, plus an entry_config label beside entry_config.py:296, plus strings and translations.
- The page refuses enabling it without `buffer_is_store`, or together with the wood coil. The error key is `combi_needs_store`.
- `topology.layout_edges` swaps `("heat_pump","dhw_tank")` for `("buffer_tank","dhw_tank")` in combi, and `describe_setup` adds `"dhw_source": "combi"`.

**Invariants.**

- With the option off, every plan and golden is byte-identical.
- In combi, the stored heat is counted once: `C_buf·ΔT` over the horizon equals `ΣP_dhw_th + Σspace_in - Σdraws - Σloss`, within float tolerance.
- In combi, `dhw_temp_trajectory == buffer_temps`.

## Alternatives (why each lost)

- **A1, a new topology key `combi_tank_valve`.** `topology_layout_valid` and the catalog partition *space* hydraulics. Combi is orthogonal: a `valve_upper_direct_slab` house can have one too. A key would double the catalog for every layout, and a second module would have to read it, because the DHW path never reads `topology_layout`. That makes two owners for one fact, which is class P2.
- **A2, parameterisation only (volumes, no model change).** No pair of volumes is honest, as the issue shows. Either the heat is doubled, or `buffer_is_store` is lost.
- **A3, fold DHW into the space solve (no DhwPlanner in combi).** `dhw_power_schedule` would be empty, so `pump_arbiter.py:346-374` would never command DHW mode, and the pump's own DHW charging would run unplanned. It would also need a per-step buffer floor penalty the objective lacks, which is a parallel mechanism.
- **A4, a two-zone stratified store.** With one probe the second state is unobservable, so its seed would be a guess (`fixer.md` step 17: missing input refuses, never guess).

## Sibling sites (step 5)

Each command is run at `198b8f7ed`:

- `grep -n "_buffer_capacity(p)" custom_components/heatpump_optimizer/thermal_model.py`
  - **Fix:** the buffer balance in `_simulate_step_single` (3299), `_simulate_step_two_zone` (3486) and the batch simulation (4099) each take `buffer_exo_kw`.
  - **Out of scope, no tank balance:** 1851, 1952, 1977 (charge-demand laws) and 3808/3837 (the stability row). Unchanged.
- `grep -n "simulate_dhw_step(" custom_components/heatpump_optimizer/*.py` (thermal_model.py:4463, dhw_planner.py:1872 and `simulate_dhw_only` 3236). Each branches to `combi_tank_step` in combi.
- `grep -n "_open_loop_plan_value(" custom_components/heatpump_optimizer/*.py`. The DHW seed is fixed here. The slab site is closed (`_propagated_slab`).
- `grep -n "async_learn_dynamics\|_async_learn_buffer_cooling(" custom_components/heatpump_optimizer/coordinator.py`. Gated as above.
- `grep -n "dhw_coil_active\|buffer_is_store" custom_components/heatpump_optimizer/optimizer.py`. Read only; the store credit (2888, 5261) already values the 572 l once.

## Evidence plan (step 6)

- **Failing test** in `tests/features.py`, beside the R10-BUFFER-STORE block (features.py:10871). The fixture:
  - 572 l, smart_write valve, both slots on `sensor.tank`;
  - a spread price day with an evening DHW window.

  The issue arm sets `buffer_tank_volume=dhw_tank_volume=572` with the option off. It **fails at base** on the invariant "stored heat counted once": the plan holds about 2× the tank's heat between the two trajectories. The combi arm passes three checks: the energy-balance invariant, `dhw_temp_trajectory == buffer_temps`, and a cheap-hour pre-charge above the DHW floor. The workaround arm (10 l / 502 l) shows `buffer_is_store` false and no space pre-charge.
- **Harness (new):** `dev/audit/harnesses/r10_combi_tank.py`, with arms `issue`, `workaround`, `combi`, `null_flat` and `off_identity`. The fixer reruns it at both ends.
- **Null controls.**
  - `null_flat`: combi at flat prices charges no more than the DHW floor needs. The rise has to come from arbitrage, not from the new branch.
  - `off_identity`: the option off reproduces base plans byte for byte. `GOLDEN_MODE=drift` must print NO UNCLAIMED DRIFT.
- **Goldens.** Neither claim file is touched, and no new golden is recorded: a value-bearing combi golden would need the canonical environment, so the assertions use tolerances.
- **Mutation targets:**
  - `buffer_exo_kw` added in each of the three step sites;
  - each conjunct of `combi_tank_active`;
  - the single-loss line in `combi_tank_step`;
  - the dual assignment in the seed;
  - the learner skip.
- **Census.** Extend `_P2_CENSUSES` (tests/entities.py:4130, the `zoned_store_*` family) with `combi_flux_live` across the single-zone, two-zone and batch steps. This is the P2 shape: one fact, three sites.
- **CPU.** Run `dev/audit/harnesses/r10_buffer_store.py bench` with a combi arm. The cost is one add per step plus planner re-runs inside the existing cap. Report the median and the worst.

## Hot files, serial position, size

- **Hot files:** `thermal_model.py`, `optimizer.py`, `dhw_planner.py`, `coordinator.py`.
- **Serial position:** behind any in-flight group holding `optimizer.py` or `thermal_model.py`; the orchestrator places it.
- **Size: XL, one pull request.** The estimate is +350–500 production lines across 8 modules, plus the option's strings. Splitting the learner gates from the model would ship a mode that books valve draws as DHW usage, which is unsound, so it stays one PR.
- **Ratchet.** The new branch in the two-zone step is near `functions_cc_over_15`, so pay by extracting `combi_tank_step` rather than inlining it.

## Notes for the fixer

- Carry 1 is owned and closed here for the measured case: the combi DHW is seeded from the buffer probe. The remainder has no measurement to seed from. Carry: dismissed: separate DHW tank without probe has no measured temperature, and no learner replays from that seed (item R10-BUFFER-STORE-carry-1-remainder)
- Sibling observed, not fixed: `buffer_tank_temperature` without a probe is never advanced (coordinator.py:6565-6567 has no `else`). That is the R9 D12-s1-01 class, outside combi. Carry: orchestrator (item buffer-open-loop-seed)
- The datasheet standing loss goes in as `buffer_cooling_rate` 0.108 K/h. Document the conversion in the option's help text, not as a new field. Carry: R10-COMBI-TANK (item datasheet-loss-help)
- Two-node model once the reporter adds the 1480 mm and 465 mm probes. Carry: dismissed: needs probes the install does not yet have (item two-node-store)
