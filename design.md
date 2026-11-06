# R10-COMBI-TANK design note (designer seat, note 2 of at most 3)

This is the group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/r10-combi-tank` and never merges. Issue #3225 comes from an outside user; the body and its one comment were read through the GitHub MCP in round 1. **There is no finder harness: the evidence is the owner report**, that is, the issue's setup as the brief quotes it. Step 6 names the synthetic fixture that reproduces it.

**Read at.** The base is `28482eceeb6b9809e44b12d80fc994282cc21645`. The group has no `after` predecessor, so there is no handoff head to read. `git diff 198b8f7ed 28482ece -- custom_components` is empty, so every line cited by note 1 and by the verdict still holds. Carry context: `a7a683d1` and `dev/audit/rca/R10-RCA-BUFFER-STORE.md`. This round answers `Design review: revise f9ede2133b5821e37fd2ff875e36fbeda4f14511 class-open` point by point (§R1–§R4). The reviewer approved the following in substance, and they stand unchanged from note 1: the seam, the one-mixed-node shape, A1–A4, the single-probe seed helper and the learner skip.

## Premise, read at base (unchanged from note 1)

- **Two independent stores.** The buffer and the DHW tank each have their own mass and UA (thermal_model.py:440, 599-604, 718-760). Both lose heat against `TANK_ROOM_AMBIENT_TEMP`; the buffer does so at thermal_model.py:1853, and the DHW recursion's gain term `_tank_decay` (dhw_planner.py:96) uses the same constant. So a single view of the store can feed one recursion.
- **The issue's setup cannot be configured honestly.** Entering 572 l for both tanks counts the heat twice. The reporter's 10 l workaround drops `buffer_is_store` (thermal_model.py:286). One probe filling both slots is legal, and nothing compares the two.
- **The datasheet loss fits without a new field.** 3.1 kWh/24 h works out to 0.108 K/h at 572 l, which is inside `buffer_cooling_rate_bounds`.

## Owning seam

**`custom_components/heatpump_optimizer/thermal_model.py`** owns three things: the shared-store physics, the predicate `combi_tank_active`, and **one accessor**, `ThermalParameters.dhw_store`. Every other module only reads them:

- `dhw_planner.py` (the planner's recursions);
- `optimizer.py` (the flux exchange and the stored-heat sums);
- `battery.py`;
- `coordinator.py` (seed, learners, advisor);
- `dhw_learning.py`;
- `sensor.py`, `topology.py`, `config_flow.py`, `entry_config.py` and `const.py` (option and display).

There is one owner, so this is not a two-owner design.

## Shape

**Model.** One mixed node. The DHW is the buffer water seen through the exchanger. It is not a layout key, as A1 below argues.

**The const and the predicate (unchanged).**
- `CONF_DHW_COMBI_TANK_ENABLED` (default False).
- `COMBI_DHW_APPROACH_K = 5.0`.
- `combi_tank_active = dhw_combi_tank_enabled and dhw_enabled and buffer_is_store and not dhw_coil_active`.

**The accessor (R1, new).** `ThermalParameters.dhw_store -> DhwStore` returns a frozen dataclass:

```
DhwStore(capacity_kwh_per_c, ua_kw_per_c, volume_l, charge_max_temp, rating_max_temp, combi: bool)
off:   (dhw_tank_thermal_mass, dhw_tank_heat_loss_coefficient, dhw_tank_volume, dhw_max_temp, dhw_hard_max_temp, False)
combi: (_buffer_capacity(p), buffer_tank_heat_loss_coefficient, buffer_tank_volume,
        min(dhw_max_temp, buffer_max_temp), min(dhw_hard_max_temp, buffer_max_temp), True)
```

- Off, every field is the value read today, so the change is byte-identical.
- The accessor is memoised on its key, like `_dhw_ua_cache`, so the per-step reads stay cheap.
- `dhw_tank_thermal_mass` and `dhw_tank_heat_loss_coefficient` remain the separate tank's own properties. **After the fix, no module outside thermal_model.py reads them** (census, R3).
- **Correction.** Note 1 claimed that "`dhw_tank_heat_loss_coefficient` is never read in combi". That was false at base: the hits below read it. The claim becomes true only through this accessor, and the census enforces it.

**The exogenous flux (R1).** The per-step `tank_exo_kw` series is the space side's net flux into the shared store (valve charge in minus valve draw out). It is not a parameter. It rides in two places:

- **`_DhwPlanContext.tank_exo_kw`** (dhw_planner.py:240-251). This is a new field, None off. It sits beside `c_dhw`, which becomes `ctx.store`.
- **The model's DHW walk.** `simulate_dhw_step`, `extend_dhw_temps` and `simulate_dhw_only` each gain `exo_kw=None`. In combi, `simulate_dhw_step` dispatches to the extracted `combi_tank_step` (note 1). That step clamps at `store.rating_max_temp`; the rating clamp lives at thermal_model.py:3203-3215.

The LP stays linear. The exo series moves only the free trajectory, `free[i+1] = decay*free[i] + (exo[i] - draw[i])*dt/C + gain`. The influence matrix does not change.

**Solver.** This is note 1's flux exchange over the split iteration that already exists (optimizer.py:3184, 5005). `_build_dhw_requirements(..., tank_exo_kw=space_net_kw)` places the series in the context. Then `dhw_net_kw` goes back to the space steps as `buffer_exo_kw`. The first pass uses zero, and the cap is unchanged.

```
probe ─► combi_tank_seed ─► buffer_T = dhw_T
 solve_space(buffer_exo=dhw_net) ─space_net─► _build_dhw_requirements ─► ctx(store, tank_exo)
   ▲                                                  │ LP / repair / clamp / greedy / walk
   └──────────── dhw_net = P_dhw_th − draw ◄──────────┘   (all read ctx.store, ctx.tank_exo)
```

**Sensors, seed, learners, option (unchanged from note 1).**
- `combi_tank_seed` (buffer, else DHW, else open-loop, else None) writes both fields. It owns R10-BUFFER-STORE carry 1.
- `dhw_learning.async_learn_dynamics` is skipped in combi. `_async_learn_buffer_cooling` is skipped on intervals that contain a planned draw.
- The `hot_water` row and the `combi_needs_store` refusal stay as specified.
- The DHW edge comes from `buffer_tank`, and `describe_setup` gains `"dhw_source": "combi"`.

**Invariants.**
1. With the option off, every plan and golden is byte-identical.
2. In combi, the heat is counted once in three places:
   - the trajectory: `C_buf·ΔT = ΣP_dhw_th + Σspace_in − Σdraw − Σloss`;
   - the battery: Σ component capacities = `C_buf`, with no `dhw_tank` component;
   - `_stored_thermal_energy`: one `C_buf` term.
3. `dhw_temp_trajectory == buffer_temps`.
4. Outside thermal_model.py, nothing reads the separate-tank C or UA.

## Sibling sites (step 5): R1 + R2

The enumeration runs at 28482ece:

`grep -n "dhw_tank_heat_loss_coefficient\|dhw_tank_thermal_mass\|c_dhw" custom_components/heatpump_optimizer/*.py`

It returns 55 hits. `binary_sensor.py:273` (`suppressing_electric_dhw`) is a substring false positive. The rest group by function:

| Site (function) | Lines | Disposition |
|---|---|---|
| `_baseline_dhw_economics` | dhw_planner.py:373 | `store.ua`. The baseline holds *this* store at setpoint. |
| `_dhw_legionella_ceilings` | 583, 609-649 | `store` C, UA and rating. The walk subtracts `exo[nxt]*dt/C`. |
| `_dhw_window_floors` | 817, 905, 909, 924 | `store` C and UA. Space flux enters through the recursions that check the floor, not through `needed_delta`. |
| context build / pass-through | 691, 720, 972, 1022, 1079-1086 | `ctx.store` and `ctx.tank_exo_kw` |
| `_plan_dhw_min_cost` (LP) | 1367-1387 | `ctx.store`, plus exo in `free` |
| `_repair_dhw_floor` | 1625-1640, 1708, 1723 | `ctx.store`. Its `_dhw_shortfall` → `simulate_dhw_only(exo_kw=ctx.tank_exo_kw)` |
| `_clamp_dhw_to_capacity` | 1817-1818, 1870 | `store.capacity`, `store.ua`, `store.charge_max_temp`. `allowed` subtracts exo, and the step passes it on. |
| `_plan_dhw_cheapest_first` | 2062-2148 | `ctx.store`, plus exo through `_dhw_shortfall` and `extend_dhw_temps` |
| other `simulate_dhw_only` / `extend_dhw_temps` calls | 485, 1200, 1501, 1933, 1978, 2010, 2166 | Pass `ctx.tank_exo_kw`. 485 is the baseline replay, which passes None: a reference house has no space flux. |
| `dhw_coast_hours` / `dhw_hold_hours` | thermal_model.py:3094-3128 | `store` |
| `simulate_dhw_step` | thermal_model.py:3157, 3194 | Dispatches to `combi_tank_step` |
| `battery.build` | battery.py:322-333 | Combi: **drop `dhw_tank`**. The `buffer_tank` component (always present, since combi implies `buffer_is_store`) is the store. |
| `_deferred_energy_cost` | optimizer.py:5425-5433 | Combi: one entry for the shared store. Skip `dhw` when `two_zone_enabled` already appended `buffer`; otherwise the `dhw` entry reads `store`. |
| `_stored_thermal_energy` | optimizer.py:5640-5665 | Same rule: skip the `dhw` term when the `two_zone_enabled` branch counted the buffer. |
| `_dhw_mixed_water` (`litres_40c`) | coordinator.py:4206 | `store.volume_l` at `T − COMBI_DHW_APPROACH_K` in combi |
| `_dhw_setpoint_sweep` | coordinator.py:4232, 4268, 4277 | `store.capacity` and `store.ua` |
| `_max_pump_rise("dhw")` | coordinator.py:4919 | `store.capacity` |
| `async_fold_draw_stats` | dhw_learning.py:421 | `store.capacity`. It is inert in combi, because the learner is skipped. It is routed anyway so the census has no allowlist. |
| `_gap_probe_terms` / advisor miss | sensor.py:2909, topology.py:813-815 | Combi with a buffer probe: the miss price is 0 (fixer carry). |

**Checked against the `dhw_tank_volume` readers.** The remaining readers are found by `grep -n "dhw_tank_volume" custom_components/heatpump_optimizer/*.py`. Two are inputs, not models: coordinator.py:2477 (the service parameter map) and services.py:478 (the service schema). The note 1 line "diagnostics show `dhw_tank_volume` as unused" is **withdrawn**. The value stays readable and settable. In combi no model reads it, and `describe_setup`'s `dhw_source: combi` is what diagnostics show instead.

The note 1 sibling commands for the space steps, the seed and the learners still stand: `_buffer_capacity(p)`, `_open_loop_plan_value(` and `async_learn_dynamics\|_async_learn_buffer_cooling(`.

## Alternatives (why each lost)

A1–A4 are as in note 1: a layout key, volumes only, folding into the space solve, a two-node store. This round adds A5.

**A5: make `dhw_tank_thermal_mass` and `dhw_tank_heat_loss_coefficient` themselves return the buffer's values in combi** (zero site edits). It lost for two reasons:
- The exo series is not a parameter, so every recursion site changes anyway to carry it.
- The aggregators (battery.py:322, optimizer.py:5431 and 5665) would silently add the same store twice. A view with `combi` set is the only way a reader can tell that it is the buffer. An alias would also invalidate the `_dhw_ua_cache` key semantics that the learner's in-place writes rely on.

## Evidence plan (step 6): R3

- **Fixture.** The failing test sits in `tests/features.py` beside the R10-BUFFER-STORE block. The fixture and the issue, combi and workaround arms are as in note 1.
- **New arm `lp_flux`.** A combi plan on a fixed price day with an evening window, run twice:
  - first `tank_exo_kw = 0`;
  - then with a 2 kW valve draw over the hours before the window.
  
  The arm asserts two things:
  - planned ΣP_dhw rises, and the plan ends at or above the window's ready temperature;
  - the plan with the option off is unchanged by the same series. This is the null control: the exo series has to be dead off.
  
  Mutating the exo term out of the LP's `free` recursion, or out of `_dhw_shortfall`'s walk, kills the arm.
- **Energy balance, extended.** The combi arm also asserts invariant 2 on `battery.build(...)`: no `dhw_tank` component, and the stored kWh equals `C_buf·(T−T_min)`. It does the same on `_stored_thermal_energy`. The issue arm fails both at base.
- **Census (P2).** In `_P2_CENSUSES` (tests/entities.py:4130):
  - `combi_store_view` counts readers of `dhw_tank_thermal_mass|dhw_tank_heat_loss_coefficient` outside thermal_model.py and must be 0;
  - `combi_flux_live` counts the exo terms: the three space steps plus five planner recursion sites. The five are the LP `free` recursion, the legionella walk, the clamp's `allowed`, the clamp's step call, and the `_dhw_shortfall` and `extend_dhw_temps` pair.
- **Harness.** `dev/audit/harnesses/r10_combi_tank.py` runs the arms `issue`, `workaround`, `combi`, `lp_flux`, `null_flat` and `off_identity`.
  - `off_identity` must print NO UNCLAIMED DRIFT under `GOLDEN_MODE=drift`.
  - No claim file is touched, and no golden is recorded.
- **Mutation targets.** Note 1's list, plus:
  - each `combi` branch of `dhw_store`;
  - the exo term in each of the five planner sites;
  - the battery drop;
  - the two optimizer skips.
- **CPU.** Run `dev/audit/harnesses/r10_buffer_store.py bench` with a combi arm. Off, the change costs one None check per step.

## Cost (R4) and split

**Re-estimate.**
- Accessor and `combi_tank_step`: about 70 lines.
- Exo plumbing through the context, the three model walks and eight planner sites: about 120.
- Readers in battery, optimizer, coordinator, learning and sensor: about 40.
- Flux exchange in `_optimize_with_dhw`: about 60.
- Space-step exo: about 40.
- Option, loader, refusal, topology and display: about 90.
- Seed and learner gates: about 60.

The total is **+480–650 production lines across 11 modules**, plus strings, over the fixer's XL budget of 300 k tokens. **Split into two PRs. The learner gate rides with the option:**

- **PR A, `R10-COMBI-TANK-STORE` (L).** Covers:
  - the `dhw_store` accessor and `combi_tank_step`;
  - the exo plumbing;
  - every reader in the table;
  - the space-step `buffer_exo_kw` and the flux exchange.
  
  `dhw_combi_tank_enabled` exists as a parameter field only. No loader wires it and no option shows it, so no install can reach combi. Tests construct it directly. Evidence: `lp_flux`, the energy-balance arms, both censuses, and `off_identity`.
- **PR B, `R10-COMBI-TANK` (M), after A.** Covers:
  - the option row, loader wiring and `combi_needs_store`;
  - `combi_tank_seed` (carry 1);
  - the learner skips;
  - topology and describe_setup;
  - the advisor probe price.
  
  This is the first PR that makes combi reachable, and it ships the learner gate in the same merge, so no released mode books valve draws as DHW use. Evidence: the issue and workaround arms end to end, and seed and learner mutation.

## Hot files, serial position

**Hot files:**
- PR A: thermal_model.py, dhw_planner.py, optimizer.py, battery.py, coordinator.py (advisor readers only), dhw_learning.py.
- PR B: config_flow.py, entry_config.py, const.py, topology.py, sensor.py, coordinator.py (`_update_current_state`, learners), tests/features.py, tests/entities.py.

**Order (the reviewer's):**
- Serialise with R10-COP-GATE and R10-ADVISOR-WHATIF on optimizer.py and coordinator.py, and with R10-HEAT-METER on thermal_model.py. These bind PR A.
- Run after R10-CONFIGFLOW-PAGES (config_flow.py, position 3 of 3) and after r10-livestate (the seed lands in `_update_current_state`). These bind PR B.
- No edge to R10-UX-HEALTH or r10-ceiling-probe.

## Notes for the fixer

- Carry 1 is closed by PR B for the measured case. Carry: dismissed: separate DHW tank without probe has no measured temperature, and no learner replays from that seed (item R10-BUFFER-STORE-carry-1-remainder)
- Carry: orchestrator (item buffer-open-loop-seed). `buffer_tank_temperature` without a probe is never advanced (coordinator.py:6565-6567). This is the class outside combi.
- Carry: R10-COMBI-TANK (item datasheet-loss-help). The help text converts the datasheet's Wh/24 h into `buffer_cooling_rate`.
- Carry: dismissed: needs probes the install does not yet have (item two-node-store)
- Carry: R10-COMBI-TANK (item ceiling-citation). thermal_model.py:3094 is `top` in `dhw_hold_hours`, not a clamp. The rating clamp is in `simulate_dhw_step` (3203-3215), and the everyday limit is the planner's per-step `max_temp`. In combi, `combi_tank_step` clamps at `store.rating_max_temp`, and the planner's `max_temp` and `_clamp_dhw_to_capacity` read `store.charge_max_temp`, which is min(dhw_max_temp, buffer_max_temp).
- Carry: R10-COMBI-TANK (item advisor-probe-combi). topology.py:813-815 and sensor.py:2909 zero the DHW-probe miss price in combi when a buffer probe is configured.
- Carry: R10-COMBI-TANK (item legionella-combi-ceiling). `boost_top` reads `store.rating_max_temp`. When the buffer rating sits below the cycle temperature, the walk's existing `need > boost_top` exit handles it. Assert the cycle is reported unreachable, not silently skipped.
- The harness reports no token count for this seat.
