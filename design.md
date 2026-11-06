# R10-COMBI-TANK design note (designer seat, note 3 of at most 5)

This is the group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/r10-combi-tank` and never merges. Issue #3225 comes from an outside user; the body and its one comment were read through the GitHub MCP in round 1. **There is no finder harness: the evidence is the owner report**, that is, the issue's setup as the brief quotes it. Step 6 names the synthetic fixture that reproduces it.

**Read at.** The base is `28482eceeb6b9809e44b12d80fc994282cc21645`. The group has no `after` predecessor, so there is no handoff head to read. `git diff 198b8f7ed 28482ece -- custom_components` is empty, so every line cited by note 1 and by the verdict still holds. Carry context: `a7a683d1` and `dev/audit/rca/R10-RCA-BUFFER-STORE.md`. Note 2 answered `Design review: revise f9ede2133b5821e37fd2ff875e36fbeda4f14511 class-open` point by point (§R1–§R4), and all four were approved, including the PR A / PR B split. This note 3 answers `Design review: revise 964d7611a4d73a658ae7fe5428170a664393fa4b class-open` (carry 0 is designed in §C0, not deferred) and the owner's carry 1 (af5bbf070: a physically sourced survey of combi tank types, with the type as data, in §T). The issue body and its comment were re-read through the GitHub MCP for this note. `WebFetch` is refused by the session's network policy for every datasheet host tried (iea-shc.org, igte.uni-stuttgart.de, manualzz.com, badundheizungshop.de), so the sources in §T were read as search excerpts and the issue's own datasheet quotes; each figure is marked accordingly. The reviewer approved the following in substance, and they stand unchanged from note 1: the seam, the one-mixed-node shape, A1–A4, the single-probe seed helper and the learner skip.

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
- `combi_tank_active = dhw_combi_tank_enabled and dhw_enabled and buffer_is_store and not dhw_coil_active`.
- **Changed by §T (owner carry 1):** note 2's single constant `COMBI_DHW_APPROACH_K = 5.0` is replaced by two numeric parameters on `ThermalParameters`, `combi_dhw_effectiveness` (ε, 0 < ε ≤ 1) and `combi_potable_volume_l` (litres of potable water held inside the store). The tank type is the pair of numbers, chosen from a data table or entered; §T derives both and shows that the old 5 K is the coil preset's value at the reference point.

**The accessor (R1, new).** `ThermalParameters.dhw_store -> DhwStore` returns a frozen dataclass:

```
DhwStore(capacity_kwh_per_c, ua_kw_per_c, volume_l, charge_max_temp, rating_max_temp,
         effectiveness, inlet_c, combi: bool)
off:   (dhw_tank_thermal_mass, dhw_tank_heat_loss_coefficient, dhw_tank_volume, dhw_max_temp,
        dhw_hard_max_temp, 1.0, dhw_inlet_reference, False)
combi: (_buffer_capacity(p), buffer_tank_heat_loss_coefficient, buffer_store_volume,
        min(dhw_max_temp, buffer_max_temp), min(dhw_hard_max_temp, buffer_max_temp),
        combi_dhw_effectiveness, dhw_inlet_reference, True)

DhwStore.store_temp_for_tap(t)  # combi: inlet + (t - inlet) / ε ; off: returns t itself
DhwStore.tap_temp_for_store(T)  # combi: inlet + ε (T - inlet)   ; off: returns T itself
```

- **`buffer_store_volume`** (new property, thermal_model.py) is `buffer_tank_volume + combi_potable_volume_l` in combi and `buffer_tank_volume` itself otherwise (the object, not `x + 0.0`). `buffer_tank_thermal_mass`, the `_buffer_ua_cache` key and `buffer_cooling_rate_bounds` read it, so every space step and the battery's `buffer_tank` component see the same C as the DHW recursions. That is the one node's single capacity; without it the space side and the DHW side would integrate one temperature against two masses, and invariant 2 would fail by `c_p·V_potable·ΔT`.
- The off branches return their inputs unchanged rather than computing `inlet + (t − inlet)/1.0`, which is not bitwise `t`; this keeps invariant 1 byte-exact.
- The two transforms are the only place ε is read. Every DHW **temperature limit stated at the tap** (`dhw_min_temp`, `dhw_idle_min_temp`, the window ready temperature, the legionella target) passes through `store_temp_for_tap` before it meets the store's temperature; every displayed tap quantity (`litres_40c`) through `tap_temp_for_store`. ε never enters an energy term (§T, invariant 5).

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
5. ε moves limits, and moves energy only where physics says it does: the draw debit `dhw_draw_scale` reads the **tap** temperature `tap_temp_for_store(T)`, so a store too cold to give 40 °C at the tap debits only the rise it delivers. While the tap stays at or above `DHW_MIXED_USE_TEMP` the debit is nominal and the trajectory under a fixed power schedule is independent of ε (§T.3).
6. No product or vendor name, and no comparison against a tank-type slug, appears in `custom_components/` outside the preset table's own definition and the config flow that copies a preset's numbers into the two fields (§T.4).

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
| `_dhw_mixed_water` (`litres_40c`) | coordinator.py:4206 | Combi: `store.capacity·(T − store_temp_for_tap(40))⁺ / (c_p·(40 − inlet))`, the heat above the point where the tap stops reaching 40 °C. Off: today's expression, unchanged. |
| Draw debit at the tap (§T) | thermal_model.py:3190 (inside the combi dispatch, so `combi_tank_step`), dhw_planner.py:1859 (`_clamp_dhw_to_capacity`) | `dhw_draw_scale(store.tap_temp_for_store(T), inlet)`. Found by `grep -n "dhw_draw_scale(" custom_components/heatpump_optimizer/*.py`; thermal_model.py:4539 is the wood coil's debit, out of scope because `combi_tank_active` excludes `dhw_coil_active`. |
| Tap-side limits (§T) | dhw_planner.py:811-813 (`dhw_min_temp`, `idle_min_temp`), 915 (ready temperature), the legionella target in `_dhw_legionella_ceilings`; thermal_model.py:3094-3095 (`dhw_hold_hours`' `top`/`floor`) | `store.store_temp_for_tap(...)`. Found by `grep -n "dhw_min_temp\|dhw_idle_min_temp\|dhw_ready_margin_c\|legionella_temp" custom_components/heatpump_optimizer/{dhw_planner,thermal_model}.py`; each hit reading a tap limit against the store goes through the accessor, the census `combi_tap_limit` counts them. |
| `_dhw_setpoint_sweep` | coordinator.py:4232, 4268, 4277 | `store.capacity` and `store.ua` |
| `_max_pump_rise("dhw")` | coordinator.py:4919 | `store.capacity` |
| `async_fold_draw_stats` | dhw_learning.py:421 | `store.capacity`. It is inert in combi, because the learner is skipped. It is routed anyway so the census has no allowlist. |
| `_gap_probe_terms` / advisor miss | sensor.py:2909, topology.py:813-815 | Combi with a buffer probe: the miss price is 0 (fixer carry). |

**Checked against the `dhw_tank_volume` readers.** The remaining readers are found by `grep -n "dhw_tank_volume" custom_components/heatpump_optimizer/*.py`. Two are inputs, not models: coordinator.py:2477 (the service parameter map) and services.py:478 (the service schema). The note 1 line "diagnostics show `dhw_tank_volume` as unused" is **withdrawn**. The value stays readable and settable. In combi no model reads it, and `describe_setup`'s `dhw_source: combi` is what diagnostics show instead.

The note 1 sibling commands for the space steps, the seed and the learners still stand: `_buffer_capacity(p)`, `_open_loop_plan_value(` and `async_learn_dynamics\|_async_learn_buffer_cooling(`.

## §T Combi tank types: survey, heat-transfer paths, conservation, type as data (owner carry 1)

### T.1 Survey (what a "combi tank" is in the field)

"Combi" covers any store where **one body of heating water** is charged by the heat pump and serves both the space-heating circuit and domestic hot water, the DHW never being charged separately. Five constructions are in common use; the fifth is listed because it looks like a combi and is not one.

| # | Type | How DHW is made | Potable water held in the store | Where it is documented |
|---|---|---|---|---|
| 1 | **Internal fresh-water coil** ("hygiene" / multifunction store; the MFS 600 S) | Cold mains flows through a long stainless (often corrugated) coil immersed in the heating water and leaves hot, on demand. | The coil's content: a few litres to ~40 l. | MFS 600 S: issue #3225's datasheet quotes (572 l heating water, coil 39 l / 7.5 m², loss 3 100 Wh/24 h per DIN 4753, zoned ports at 765 / 400 mm). Retail listings found by search: 95 °C max, 3 bar, coil 7.5 m², solar coil 1.5 m², 552-572 l net. Manufacturer and retailer pages on corrugated-coil hygiene stores (Durchlaufprinzip: no standing potable volume). IEA SHC Task 26 generic systems with immersed horizontal finned coils (appendix reports). |
| 2 | **Tank-in-tank** | A potable inner tank (typically 100-200 l) sits inside the heating water and is heated through its wall; DHW is drawn from the inner tank. | The inner tank, 100-200 l. | IEA SHC Task 26, Subtask B "hot water performance": the potable volume inside the exchanger ranges "from a few litres in an immersed coil to several hundred litres in a tank-in-tank store". A KoreaScience solar combistore study, 700 l heating + 150 l DHW inner tank. A Danish DTU thesis on tank-in-tank flow structure (core.ac.uk 13736991). |
| 3 | **External fresh-water station on a buffer** | A plate exchanger outside the tank, fed from the buffer top by a speed-controlled primary pump, returns cooled primary water to the buffer bottom. | ~1 l in the plate exchanger. | Station datasheets (Weinmann & Schanz / PAW product sheets found by search): primary flow ~55-70 °C, primary return down to ~15 °C at high draw, return height to be chosen to match return temperature so stratification is kept; 70 °C primary cap against scaling. |
| 4 | **Stratified multifunction store** (any of 1-3 with stratifying inlets or zoned ports) | As 1-3; the heat pump has a DHW return high and a heating return low, so a DHW charge heats only the upper zone. | As the DHW path used. | Issue #3225 (MFS port heights). EN 12977-4 (performance test of combistores ≤ 3 000 l without burner) characterises such stores by a multi-node model with an effective vertical conductivity; its round-robin report (Stuttgart ECO, WP8) lists "UA-value, hot water heat exchanger" as a fitted parameter. |
| 5 | **Two stores in one shell** (stacked "2-in-1" heat-pump cylinders, a small buffer section under a DHW cylinder) | A separate DHW cylinder and a separate buffer, partitioned. | The whole DHW section. | OEG "2-in-1" heat-pump store datasheet (found by search): ~100 l buffer section, the rest a DHW section. **Not a combi**: two waters, two temperatures. The existing two-store configuration models it correctly; the option's help text says so. |

The issue's install is type 1 with type-4 ports.

### T.2 Heat-transfer paths and their parameters

The model keeps the approved **one mixed node** (temperature T, capacity C, loss UA). Each path below is written in the node's terms; the label after each figure is **[datasheet]**, **[measured]**, **[standard]** or **[assumed]**.

- **Capacity.** C = c_p·(V_heat + V_potable), c_p = `WATER_SPECIFIC_HEAT` 0.00116 kWh/(l·K) [standard property]. The potable water inside the store is at the store's temperature between draws and is heat the store holds. MFS 600 S: V_heat 572 l [datasheet], V_potable 39 l [datasheet], C = 0.709 kWh/K. Tank-in-tank: V_potable is the inner tank [datasheet per product]. Station: V_potable ≈ 0 [assumed: plate exchanger content].
- **Standing loss.** UA from the datasheet's 24-hour standing loss Q₂₄ at the standard's test difference: DIN 4753-8 and EN 12897 rate it at 65 °C store / 20 °C room, ΔT = 45 K [standard; test points as recalled by this seat, not re-read: the fetch was refused]. MFS: UA = 3 100 Wh / 24 h / 45 K = 2.87 W/K, which is 0.108 K/h at the code's 25 K reference over 572 l (`DHW_COOLING_REFERENCE_DELTA`, const.py:1269), inside `buffer_cooling_rate_bounds` [derived from datasheet]. Over 611 l (with the coil) it is 0.101 K/h. EU 812/2013 labels report the same quantity as a standing loss S in W (example in EPREL: 90 W at 294 l) [standard]. The help text converts either form; no new field.
- **DHW draw (the exchanger).** A counter-flow or immersed exchanger delivers T_tap = T_in + ε·(T − T_in), with ε = 1 − exp(−NTU), NTU = UA_hx / (ṁ·c_p) for a store side that is effectively isothermal [standard ε-NTU relation for one fluid at constant temperature]. ε is evaluated at the install's design draw, `shower_flow_lpm` (coordinator.py:4208).
  - Coil, MFS: A = 7.5 m² [datasheet]; U for an immersed coil under natural convection outside, forced inside, 200-500 W/(m²·K) [assumed: textbook range, not sourced to a fetched page]; UA_hx = 1.5-3.75 kW/K; at 12 l/min ṁc_p = 0.84 kW/K; NTU 1.8-4.5; ε = 0.83-0.99. **Preset ε = 0.85**, the conservative end. At T_in 10 °C and a 45 °C need, the store must hold 10 + 35/0.85 = 51.2 °C: an approach of 6.2 K. Note 2's fixed 5 K was this preset at ε ≈ 0.875; the parameter replaces it.
  - Tank-in-tank: the draw takes stored potable water already at ≈ T. **Preset ε = 0.95** [assumed]: the inner tank lags the outer water by a few kelvin after a charge, and a draw longer than the inner volume degrades towards a coil with the inner wall's small UA; the per-step draw series cannot see single events, so this limit is recorded, not modelled.
  - Station: ε from the station's own table, ε = (T_out − T_in)/(T_primary − T_in) at the design flow. Search excerpts give primary 55-70 °C delivering 45 °C at the table's flows, i.e. ε ≈ 0.7-0.8 [datasheet ranges, not a single product]. **Preset ε = 0.75** [assumed], to be replaced from the installed station's table.
  - The **energy** the draw removes is what the potable water gains, ṁ·c_p·(T_tap − T_in): the exchanger is inside the insulation (types 1, 2) or its loss is negligible beside the draw (type 3) [assumed]. Behind a thermostatic mixer at the tap this is the nominal draw while T_tap ≥ `DHW_MIXED_USE_TEMP`, and `dhw_draw_scale` of it below. That is today's rule read at the tap temperature instead of the tank's (invariant 5).
- **Space-heating draw.** The valve draws the space side's heat from the same node: `tank_exo_kw` (Shape, note 2). Unchanged by type.
- **Stratification and mixing.** Not modelled: one node, approved; the two-node store stays dismissed until the install has top and bottom probes (carry two-node-store). Its **direction** is bounded: in a stratified store the DHW zone (top) is hotter than the volume mean after a heating draw from the bottom, so a mean-temperature floor check plans DHW energy earlier than needed, a cost error, never a cold tap; and the probe re-seeds the node each cycle (§C0), so the error does not accumulate. The opposite case, a DHW-only charge through the upper return heating only the upper zone, makes the mean understate the top and overstate the bottom; it again errs towards more DHW charge, and the space side sees heat that is physically there. A probe mounted low in the store under-reads the DHW zone the same way. Recorded as a carry for the help text (item probe-height).

### T.3 Energy conservation across both volumes

With the potable and heating volumes in one node, "both volumes" are one C, and the stated balance over a plan of N steps of length Δt is

```
C·(T_N − T_0) = Σ (P_dhw_th,i + P_space_in,i − P_valve_draw,i − P_draw,i − UA·(T̄_i − T_amb))·Δt
```

with P_draw,i = nominal draw · `dhw_draw_scale(tap_temp_for_store(T_i), T_in)` and T̄_i the step's mean temperature as `combi_tank_step` integrates it (the same exact-exponential form as the buffer step at thermal_model.py:1853).

Tests (`tests/features.py`, combi block):
- **Invariant `combi_energy_balance`.** Run `combi_tank_step` over a 48-step day with a varying charge, valve draw and DHW draw; compute the right-hand side from the step's own reported terms with `math.fsum`; assert `|C·ΔT − RHS| ≤ 1e-9 kWh`. Also assert the battery's stored kWh and `_stored_thermal_energy` equal `C·(T − T_min)` with no `dhw_tank` component (invariant 2).
- **Null control, UA = 0.** The same run with `buffer_cooling_rate` forced to give UA = 0 (a parameter override in the test) conserves `Σ(in − out)·Δt` to `1e-12` relative: the loss term is identically zero, so the only residual is float summation. A mutation that double-counts V_potable (capacity from `buffer_tank_volume` on one side, `buffer_store_volume` on the other) breaks it by `c_p·V_potable·ΔT`, which is above the tolerance for any ΔT > 1e-6 K.
- **Null control, ε.** The same schedule with the tap kept above `DHW_MIXED_USE_TEMP`, run at ε = 0.6 and ε = 1.0: identical trajectories. A mutation that applies ε to the debit above the mixer threshold kills it.

### T.4 Tank type as configuration, never vendor branches

The code reads **numbers only**: `combi_dhw_effectiveness`, `combi_potable_volume_l`, plus the existing `buffer_tank_volume` and `buffer_cooling_rate`. A preset table in const.py, `COMBI_TANK_PRESETS: Final[Mapping[str, CombiTankPreset]]`, is keyed by **physical type slug** and is used in one place, the config flow, to pre-fill the two fields; the user can overwrite either.

| slug | ε | V_potable default | source |
|---|---|---|---|
| `internal_coil` | 0.85 | 30 l | ε assumed from the T.2 range; volume a mid value [assumed]; the MFS user enters 39 l [datasheet] |
| `tank_in_tank` | 0.95 | 150 l | ε assumed; volume from the cited studies' 150 l [paper] |
| `external_station` | 0.75 | 0 l | ε from station table ranges [datasheet ranges]; volume assumed |
| `custom` | user | user | — |

- No preset is named after a product. The MFS 600 S is a worked example in the help text, not a key.
- Census `combi_type_branch` in `_P2_CENSUSES`: zero comparisons against a preset slug outside const.py and config_flow.py, and zero occurrences of a manufacturer or product name in `custom_components/` Python (`grep -rniE "alpha.?innotec|mfs ?[0-9]|luxtronik" custom_components/heatpump_optimizer/*.py`, run at base: the fixer records the base count and asserts it does not grow).
- A type-5 store is not offered; its help line points to the two-store configuration.

## §C0 Carry 0: the no-probe buffer is never advanced (D12-s1-01), designed in

**Site.** coordinator.py:6565-6568 (the read at 6566), `_update_current_state`: `buffer_reading = reader.read(CONF_BUFFER_TANK_TEMP_ENTITY)`; `if buffer_reading.ok: state.buffer_tank_temperature = buffer_reading.value`. Without an ok reading the field keeps the `CurrentState` default 40.0 (thermal_model.py:1741) or the last value, cycle after cycle, and the solver starts every plan from it. The DHW branch directly above (6550-6563) already fixes the same class with `_open_loop_plan_value(self._optimization_result, "dhw_temp_trajectory", dt_util.now())` (helper coordinator.py:2315; the field `OptimizationResult.buffer_temp_trajectory`, optimizer.py:1886).

**Shape.** One primitive, one ordering, shared by combi and non-combi:

```
_seed_store(reading, result, attr, now) -> float | None
    reading.value if reading.ok
    else _open_loop_plan_value(result, attr, now)        # None: no plan, empty trajectory, stale plan
```

- **Non-combi:** `buffer = _seed_store(buffer_reading, result, "buffer_temp_trajectory", now)`; `dhw = _seed_store(dhw, result, "dhw_temp_trajectory", now)`. Each writes its field only when not None. The DHW line is today's branch re-expressed, behaviour identical (the existing DHW open-loop tests are its null control).
- **Combi:** `combi_tank_seed` = first non-None of (buffer reading ok, DHW reading ok, open-loop `buffer_temp_trajectory`), written to both fields. It is the same `_seed_store` primitive applied in that order, so there is one seed path, not two; by invariant 3 the two trajectories are equal, and the buffer's is the one read.
- **Which buffers (carry item buffer-open-loop-nonstore, decided):** every buffer whose last plan published a trajectory, not only `buffer_is_store`. The plan publishes `buffer_temp_trajectory` whenever the valve throttles (optimizer.py:3059-3064), and the solver simulates the buffer from `state.buffer_tank_temperature` whenever it is modelled (thermal_model.py:286's docstring: "the physics stay modelled either way"), so a never-advanced constant is equally wrong for a small tank. Without a throttling valve the trajectory is empty, the helper returns None and **the field stays as it is, never fabricated**.
- **Observation stays measured.** `ExternalHeatObservation.buffer_temp` and `hp_tank_temp` (coordinator.py:5029, 5038) are rise detectors (external_heat.py:241-246); fed a planned value they would read the plan's own rise as evidence. They take `buffer_reading.value if buffer_reading.ok else None` through a per-cycle measured value the coordinator keeps beside the state. The DHW observation at 5028 has the same exposure since R9 (it reads the open-loop-seeded `dhw_temperature`); it is a sibling of the same class and is covered in the same edit, with its own arm.

**Tests** (`tests/features.py`, beside the R9 DHW open-loop block):
- **Failing first:** no buffer probe, a throttling valve, a prior `OptimizationResult` whose `buffer_temp_trajectory` moves 40 → 47 °C across the covering steps; two cycles of `_update_current_state`. At base `state.buffer_tank_temperature` stays 40.0; after the fix it equals the trajectory at the covering step.
- **Null control:** the same arms with a buffer probe reading ok: unchanged, the reading wins.
- **Empty trajectory:** no throttling valve, so the trajectory is empty: the field is unchanged across cycles (not fabricated).
- **Observation:** with no probe, the external-heat observation's `buffer_temp` and `dhw_temp` are None while the state carries the seed; with a probe they carry the reading.
- **Mutation targets:** drop the open-loop branch of `_seed_store` for the buffer (the failing arm fails); feed the seeded value to the observation (the observation arm fails).

**Placement and size.** **PR B** carries it: the edit is in `_update_current_state` beside `combi_tank_seed`, so the one primitive lands once and both paths use it, and it lands after r10-livestate, which owns that method's recent shape. It does not need the option, so PR B ships it for every install, combi or not. Size: +20-25 production lines (the primitive, the buffer call, the measured observation values) and about +60 test lines. PR B stays M.

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
- **Type and conservation arms (§T.3):** `combi_energy_balance`, its UA = 0 and ε null controls, and the census `combi_type_branch`. Harness arms `balance`, `ua_zero`, `eps_null`, and `presets` (each preset's ε and V_potable reproduce the T.2 approach and capacity: coil at 45 °C need gives a 51.2 °C store floor).
- **Carry 0 (§C0):** its own failing test, null control, empty-trajectory and observation arms; harness arm `no_probe`.
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

The total is **+480–650 production lines across 11 modules**. Note 3 adds: §T in PR A, `buffer_store_volume`, the ε transforms and their tap-limit and draw-debit sites, about +50; §T in PR B, the preset table, two option fields and help, about +40; §C0 in PR B, about +25. **New total +595–765**, plus strings, over the fixer's XL budget of 300 k tokens. **Split into two PRs. The learner gate rides with the option:**

- **PR A, `R10-COMBI-TANK-STORE` (L).** Covers:
  - the `dhw_store` accessor and `combi_tank_step`;
  - the exo plumbing;
  - every reader in the table;
  - the space-step `buffer_exo_kw` and the flux exchange;
  - §T's `buffer_store_volume`, the ε transforms, and the tap-limit and draw-debit sites (parameters settable only in tests).
  
  `dhw_combi_tank_enabled` exists as a parameter field only. No loader wires it and no option shows it, so no install can reach combi. Tests construct it directly. Evidence: `lp_flux`, the energy-balance arms, both censuses, and `off_identity`.
- **PR B, `R10-COMBI-TANK` (M), after A.** Covers:
  - the option row, loader wiring and `combi_needs_store`;
  - `combi_tank_seed` (carry 1);
  - the learner skips;
  - topology and describe_setup;
  - the advisor probe price;
  - the §T preset table and the two type fields in the option flow;
  - §C0, the shared `_seed_store` primitive and the measured observation (carry 0).
  
  This is the first PR that makes combi reachable, and it ships the learner gate in the same merge, so no released mode books valve draws as DHW use. Evidence: the issue and workaround arms end to end, and seed and learner mutation.

## Hot files, serial position

**Hot files:**
- PR A: thermal_model.py, dhw_planner.py, optimizer.py, battery.py, coordinator.py (advisor readers only, and `litres_40c`), dhw_learning.py.
- PR B: config_flow.py, entry_config.py, const.py, topology.py, sensor.py, coordinator.py (`_update_current_state`, learners), tests/features.py, tests/entities.py.

**Order (the reviewer's):**
- Serialise with R10-COP-GATE and R10-ADVISOR-WHATIF on optimizer.py and coordinator.py, and with R10-HEAT-METER on thermal_model.py. These bind PR A.
- Run after R10-CONFIGFLOW-PAGES (config_flow.py, position 3 of 3) and after r10-livestate (the seed and §C0 land in `_update_current_state`). These bind PR B; carry 0 rides in PR B, so it adds no new edge.
- §C0 also touches the external-heat observation at coordinator.py:5022-5040: PR B is serialised with any group whose diff edits `ExternalHeatObservation` construction (none on the roster at this note's base: `git grep -n "ExternalHeatObservation(" 28482ece -- custom_components` names only that site).
- No edge to R10-UX-HEALTH or r10-ceiling-probe.

## Notes for the fixer

- Carry 1 is closed by PR B for the measured case. Carry: dismissed: separate DHW tank without probe has no measured temperature, and no learner replays from that seed (item R10-BUFFER-STORE-carry-1-remainder)
- Carry: R10-COMBI-TANK (item buffer-open-loop-seed). Carry 0, D12-s1-01: designed in §C0, delivered by PR B for every install.
- Carry: R10-COMBI-TANK (item buffer-open-loop-nonstore). Decided in §C0: every buffer with a published trajectory; an empty `buffer_temp_trajectory` leaves the value as it is, never fabricated.
- Carry: R10-COMBI-TANK (item exo-sign-check). In `lp_flux`, assert that a large valve draw (2 kW over the four hours) before a window raises the energy `_repair_dhw_floor` adds, against the same plan with zero exo; mutating exo out of `_dhw_window_floors`' checking recursions kills it, so a floor computed without exo cannot under-plan silently.
- Carry: R10-COMBI-TANK (item observation-measured). The external-heat observation reads measured values only (§C0); the DHW observation is the sibling of the same class, covered with its own arm.
- Carry: R10-COMBI-TANK (item probe-height). The help text says the one node reads the probe as the store's mean; a probe high in the DHW zone over-reads it, so for a single probe the general well (MFS: 1 250 mm) is the right one, and the empty top well (1 480 mm) is for a later two-node store.
- Carry: R10-COMBI-TANK (item preset-figures). Every preset figure marked [assumed] in §T is replaced when the fixer, or a later seat with network access to the datasheets, reads a sourced value; `tests/features.py`'s `presets` arm records the figure's source label beside it.
- Carry: R10-COMBI-TANK (item datasheet-loss-help). The help text converts the datasheet's Wh/24 h into `buffer_cooling_rate`.
- Carry: dismissed: needs probes the install does not yet have (item two-node-store)
- Carry: R10-COMBI-TANK (item ceiling-citation). thermal_model.py:3094 is `top` in `dhw_hold_hours`, not a clamp. The rating clamp is in `simulate_dhw_step` (3203-3215), and the everyday limit is the planner's per-step `max_temp`. In combi, `combi_tank_step` clamps at `store.rating_max_temp`, and the planner's `max_temp` and `_clamp_dhw_to_capacity` read `store.charge_max_temp`, which is min(dhw_max_temp, buffer_max_temp).
- Carry: R10-COMBI-TANK (item advisor-probe-combi). topology.py:813-815 and sensor.py:2909 zero the DHW-probe miss price in combi when a buffer probe is configured.
- Carry: R10-COMBI-TANK (item legionella-combi-ceiling). `boost_top` reads `store.rating_max_temp`. When the buffer rating sits below the cycle temperature, the walk's existing `need > boost_top` exit handles it. Assert the cycle is reported unreachable, not silently skipped.
- The harness reports no token count for this seat.
