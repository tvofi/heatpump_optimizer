# Round 9, dimension D12: verifier V3 (reach and class) report

Box G2-V3. Worktree at 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus the round-9 evidence). Venv: CPython 3.14.0rc2, numpy 2.4.6/OpenBLAS, `PYTHONPATH=tests/hastub`. Real-HA runs: a separate venv with Home Assistant core 2026.2.3 (real package, no hastub on the path), numpy/scipy/threadpoolctl symlinked in from the gate venv.

Two environment shims were needed for real HA, both stated in the harness headers:
- **mashumaro 3.22** calls `typing.ByteString`, removed in CPython 3.14; without a stand-in ABC HA core does not import.
- **The manifest's `http` dependency** is marked loaded: a flow never touches the web server, and setting up `http` needs `hass.auth`.

Everything else is real HA code: FlowManager and OptionsFlowManager, `data_schema` validation, `voluptuous_serialize` with `cv.custom_serializer`, and the `select` / `input_select` integrations and their entity services.

The register's verdict columns, GitHub and other verifiers' reports were not read. One grep over README.md and docs/*.md for "tank probe" printed one round-1 register row (D8-01, ThermalState defaults on display surfaces); it was not used in any vote.

Harnesses: `tools/audit/round9/D12/verify-v3/` — frozen_state.py, realha_flows.py, realha_select.py, onoff_delivery.py, pnorm_seams.py. Outputs and step-1 RESULT lines under `verify-v3/runs/`. The realha_* harnesses print `thread_factor` 1.05–1.39 from real HA's own executor threads (entry setup after `create_entry`); every number they produce is a count, none a timing claim.

---

## D12-s1-01: hot water without a tank probe, so the solver always starts at 55 °C

**Step 1 (re-run).** `state_seed.py --hours 24` reproduced exactly:
- Arm A: dhw mismatch 23/24, slab 5, distinct initial values dhw 1 / slab 1, 6.25 window-hours below minimum, 1.64 kWh, truth minimum 31.64 °C.
- Arm B: 0 / 0 / 0.0 h, 3.89 kWh, 43.11 °C.

`--flat`: A 23, 6.5 h, 0.3 kWh against B 0, 0.0 h, 3.65 kWh. load1 2.89 / 3.00, `thread_factor` 1.000. Within tolerance.

**Step 2 (own harness), frozen_state.py.**
- **Metric:** a field is frozen when every `_solve_snapshot` input for it is one value across N hourly solves while the previous plan's +1 h prediction is more than 1 K away in at least half the cycles.
- **Origin test:** before the first cycle the live `_current_state.dhw_temperature` was overwritten with a sentinel 47.3 °C.
- **Result:** 12 of 12 solves received exactly 47.3 °C, with 8 of 11 cycles more than 1 K from the plan. Nothing advances the field; production hands the solver whatever is present, which is the dataclass default of 55.
- **Fields frozen:** omitted arm 1 (dhw); mapped arm 0.
- **Perturbation:** `--advance` (open-loop propagation from the previous plan, patched in memory into `_solve_snapshot`) takes it to 0. load1 2.63, `thread_factor` 1.000.

Slab also held one value in 12 of 12 solves but stayed within 1 K of the plan over that horizon; the finder saw 5/24 over 24 h, so slab is a real but weaker seam. The only writer is coordinator.py:5435, inside `if dhw.ok`.

**Attacks, in step-3 order:**
- *Contention:* counts only.
- *Gate mode:* not applicable.
- *Grid artefact:* finder's leave-one-out 6.25–6.75 h; the sentinel test does not depend on the grid.
- *Null control:* present and passing (mapped arm, flat prices).
- *Reachability in real HA:* yes. The real-HA initial flow on the wizard "describe" path (realha_flows.py `cfg_wizard_describe`) creates an entry with DHW enabled and no `dhw_temp_entity`; strings.json calls the probe "Optional but recommended". The rest is coordinator code.
- *Severity by consequence:* high holds. On the switch path the pump is disabled on steps the plan leaves idle, and under pump-duty control a space-only step writes Heating only; the pump's tank thermostat cannot cover for a plan believing the tank is at 55 °C. The model puts the tank below `dhw_min` for 6.25 h inside demand windows.

**Seam rule.** Run: dhw 23, slab 5 mismatches. **Partial**: FIELDS is a hand list (dhw, slab), not derived from ThermalState. On a 4-field sweep (dhw, slab, buffer, lower) it still covers every frozen field found: buffer is not modelled without its probe in that config, and lower is re-seeded from the room reading every cycle.

**Class.** P6 confirmed.

**Vote: verify, high.**

---

## D12-s1-02: an untouched Hot water / Hot water tank options page turns DHW on

**Step 1 (re-run).**
- `phantom_dhw.py`: no-save control 0 steps / 0 kWh; options hot_water 9 / 3.16; options hot_water_tank 9 / 3.16; wizard dhw 9 / 3.16. Options pages inventing = 2.
- `--fallback-dhw`: options 0 (wizard stays at 9, as expected).
- `flow_pages.py`: 21 pages, 2 inventing (hot_water, hot_water_tank; dhw False to True).

load1 0.79–1.05, `thread_factor` 1.000. Exact.

**Step 2 (own harness, real HA), realha_flows.py.**
- **Metric:** per seam, whether the effective config after an untouched submit through the real OptionsFlowManager makes `_dhw_enabled_from_config` True on a no-DHW entry.
- **Submit:** what the real frontend would send — the step schema serialised as HA's flow view does, initial data from `computeInitialHaFormData` (suggested_value, else default).
- **Base entry:** created through the real initial flow with `finish_now`.
- **Result:** `opt_hot_water` stored `dhw_windows` (DHW on); `opt_hot_water_tank` stored `dhw_tank_volume` (DHW on); `opt_comfort` control stored nothing (off). 2 of 2 DHW pages invent the plant in real HA.
- **Perturbation:** `--perturb` (explicit `dhw_enabled` only) takes both to 0. load1 1.40 / 1.44.

**Attacks:**
- *Contention:* none. *Grid:* n/a. *Null control:* passes (no-save, comfort, the other 19 pages).
- *Reachability in real HA:* real; the real FlowManager applies `data_schema` and stores the posted defaults.
- *Refute angle tested:* the `_ABSENT_IS_NOT_DEFAULT` comment shows the DHW pair is written deliberately because it is presence-inferred. It does not rebut: no page offers a "no hot water" answer, and leaving a page by submitting is the documented back-out (`async_update_options` docstring).
- *Severity:* weaken high to medium. A bounded 3.16 kWh/day phantom DHW plan and a published DHW trajectory, with a workaround (options Quick setup writes `dhw_enabled`, honoured first at thermal_model.py:1057). Same consequence as D12-s3-01, rated medium by its own finder.

**Seam rule.** `flow_pages.py`: 21 pages, 2 inventing. **Partial**: every options page, but not the initial config flow's pages (wizard dhw and zones, D12-s3-01's seams). The two rules together cover the property; s1-02 and s3-01 share the presence rule (noted, not deduplicated).

**Class.** P2 confirmed.

**Vote: weaken, medium.**

---

## D12-s2-01: on an on/off pump the switch path switches off steps whose heat the plan books as delivered

**Step 1 (re-run).** `onoff_switch.py` exact:
- On/off: 4 of 9 failing cells (3 in leave-one-out); shoulder withheld 0.671 (8.30 of 12.38 kWh), 30 off-steps with planned heat.
- End to end: 30 turn_off calls with planned heat.
- Shoulder room: minimum 20.64 planned against 19.89 actuated, 17.23 K·h below plan, 0 K·h below minimum.
- Modulating null control: 0 cells, 0 such turn_off calls. `--perturb` (0.1 kW threshold): 0 / 0.

load1 3.56, `thread_factor` 1.000.

**Step 2 (own harness), onoff_delivery.py.**
- **Metric:** `sub_floor_heat_frac` = planned kWh in >0.1 kW steps that production marks off / total planned kWh. Room re-simulated under (a) plan-power (ON delivers planned power, the finder's model) and (b) rated-power (fixed-speed compressor at 6 kW for the whole ON step).

| Cell | sub_floor_heat_frac | K·h below plan (a / b) | K·h below minimum |
|---|---|---|---|
| shoulder | 0.671 | 17.23 / 16.85 | 0 in both |
| shoulder_two_zone | 0.296 | 6.92 / 0.61 | not reported |
| winter_two_zone_dhw | 0.122 | 9.75 / 0.10 | (a) 0.53, (b) 0 |
| flat_prices | 0.029 | 2.56 / 0.0 | not reported |

`--threshold01`: all four cells 0.

The shoulder shortfall survives the rated-power reading; in winter cells over-delivery on ON steps largely compensates. For the fixer: with the 0.1 kW fix the rated-power reading over-heats by 34–69 K·h above plan, so the solver-side fix (bang-bang or floor when min == max) is the physically safe one of the two proposed.

**Real HA, realha_select.py.** The real OptionsFlowManager saves the thermal_model page with min == max == 6.0 kW without error (`onoff_min_eq_max_accepted=1`); `_power_to_heat_pump_schedule([1.2, 6.0, 0.0])` returns `[False, True, False]`. Reachable, not stub-only.

**Attacks:** contention: counts. Grid: 4 failing cells, 3 in leave-one-out, concentrated in shoulder and two-zone. Null control: modulating arm passes. Severity: medium holds — comfort stays at or above `min_temperature` under the rated-power reading; published trajectory and savings are wrong, shoulder under-delivery is real.

**Seam rule.** 6 lines: optimizer.py:6962, :7024; pump_arbiter.py:354, :357, :358, :491. **Partial**: spelling-bound, misses coordinator.py:9736 `max(0.1, 0.5 * ...min_electrical_power)`, the compressor-start counter's copy of the same convention (a measurement seam, not actuation). It lists every actuation seam.

**Class.** P2 confirmed.

**Vote: verify, medium.**

---

## D12-s2-02: the pump-duty arbiter writes the mode with `select.select_option` whatever the slot's domain

**Step 1 (re-run).** `mode_domain.py`: select 0/0/0; input_select 5 misrouted, 9 wrong ticks, repair raised; sensor 5/9/1; failing_mode_domains = 2. `--perturb`: input_select 0/0/0; sensor keeps 9 wrong ticks (the read-only half); failing = 1. load1 0.51, `thread_factor` 1.000. Exact.

**Step 2 (own harness, real HA), realha_select.py.**
- **Metric:** of the three domains the slot accepts (`topology._MODE`: select, sensor, input_select), how many production `pump_arbiter._write` leaves unapplied after one write, against real `select` and `input_select` integrations.
- **Result:** select applied ("Heating + DHW" to "DHW only"). input_select not applied, no exception, recorded as done — what later raises the pump-does-not-hold repair. sensor not applied, recorded as done (`select.select_option` exists, so the call does not raise). Unapplied: 2 of 3.
- **Perturbation:** `--perturb` (route by target domain, in memory) gives 1; input_select applies. load1 1.94 / 1.95.

**Attacks:** contention none; null control: select passes; reachability: confirmed with real entity services — real HA silently no-ops a foreign-domain target. Severity: medium holds; `pump_duty_mode` defaults to "off", so control is opt-in; consequence is a wrong mode plus a misleading repair.

**Seam rule.** 11 `async_call` sites across pump_arbiter, coordinator and repairs, none elsewhere. Cross-checked against each slot's picker domains, exactly one is misrouted: pump_arbiter.py:457. The setpoint seam (repairs.py `_write_setpoint`) and the valve write route by domain; the frequency write hard-codes "number", matching its number-only picker. **All.**

**Class.** P2 confirmed.

**Vote: verify, medium.**

---

## D12-s2-03: on an on/off pump every full-power step publishes as "eco" and `power_normalized` runs to −60

**Step 1 (re-run).** `onoff_label.py`: on/off 149 mislabelled (118 in leave-one-out, 7 of 9 cells), `power_normalized` minimum −60.0; modulating 0 (minimum −0.2). `--min 5.0`: 0, minimum −5.0. load1 3.43 / 2.80, `thread_factor` 1.000. Exact.

**Step 2 (own harness), pnorm_seams.py.**
- **Metric:** production p_norm seams that map a full-power step to the bottom of their range.
- **Seams:** `get_current_action`, `_power_to_setpoints` (published `optimal_setpoints`), `_power_to_displace_schedule` (ECL110 displace, an actuation seam), `_zone_setpoints`.
- **Result:** modulating 0; on/off **4 of 4**, idle-step `power_normalized` −60.0. `--guard` (min 5.0) gives 0. load1 1.77, `thread_factor` 1.000.

The finding demonstrates only the label and attribute. On an ECL110 install with min == max the displace for a full-power step is d_min (−3.3 against +3.3 modulating): an actuation consequence the claim does not state.

**Attacks:** contention: counts. Grid: 7 of 9 cells, 118 in LOO. Null control: modulating passes (its −0.2 idle value is the same formula, carried by the finding as a lead). Reachability: min == max accepted by the real options flow; the sensor publishes what `get_current_action` returns. Severity: medium holds for the label; the ECL110 displace seam could justify more on the rare ECL110 + fixed-speed combination — left to the judge.

**Seam rule.** Lists 2189, 6890–6900, 6931–6933, 7031–7061: all four formulas. **All** (more than the claim demonstrates).

**Class.** P3 confirmed: the `max(p_range, 0.1)` divisor floor turns a degenerate range into ×10; three siblings clip to [0, 1], `get_current_action` does not.

**Vote: verify, medium.**

---

## D12-s3-01: the full config-flow wizard invents a DHW tank and a second zone

**Step 1 (re-run).** `flow_paths.py` (`--answers no` default): 6 paths, 2 invented, 2 DHW and 1 two-zone.
- "describe": models the tank but plans 0.00 kWh DHW; planned 11.13 vs 10.39 kWh, predicted_cost 8.344 vs 6.068.
- "thermal": DHW plus two-zone; planned 26.36 vs 21.32 kWh, cost 19.831 vs 11.421. The finding says 26.45 / 22.24 and 19.289 / 11.796: the count is exact, the consequence numbers drift (the harness appears not to freeze the clock).
- `--perturb explicit_presence`: 0.

load1 1.43 / 2.46, `thread_factor` 1.000. The harness header's "Expected paths=5, invented_paths=3" is stale against both the finding and the re-run (6 / 2): a header defect, not a vote issue.

**Step 2 (own harness, real HA), realha_flows.py.** Real FlowManager with frontend-rule untouched submits:
- `cfg_wizard_thermal` (user, user_sensors, temperature, thermal, zones, dhw, weather_sensitivity, setup_overview): `dhw_enabled=True`, `two_zone=True`.
- `cfg_wizard_describe`: `dhw_enabled=True`.
- `cfg_finish_now`: neither.
- 2 wizard paths invent a plant in real HA. `--perturb` (explicit `dhw_enabled` only) takes DHW to 0 on both; two-zone stays on thermal (only the DHW rule perturbed).

load1 1.40 / 1.44.

**Attacks:** contention none. Null control: quick-setup paths and `finish_now` invent nothing. Reachability: real; the `dhw` step has no "no hot water" answer and the real schema defaults (tank volume, windows) are stored. Severity: medium holds (bounded wrong plan; options Quick setup as workaround).

**Seam rule.** `flow_paths.py --answers no`: 6 paths, 2 inventing. **Partial**: every initial-flow menu-completion path, not the options pages (D12-s1-02's seams). Together they cover the phenomenon.

**Class.** P2 confirmed.

**Vote: verify, medium.**

---

Counts: verify 5, weaken 1, refute 0, unresolved 0.
