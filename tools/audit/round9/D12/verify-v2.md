# D12 round 9: verifier V2 (independent lens)

Box G2-V2; worktree /home/claude/evid at 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus round-9 evidence); /home/claude/venv CPython 3.14.0rc2; thread pins set; PYTHONPATH=tests/hastub. Differs from the finder boxes B6/B7: venv path (/home/claude/venv, not venv314), and 3 seats ran concurrently (load1 1.0-7.4). Every number below is a count or a ratio from deterministic solves; thread_factor was 1.000 on every run (0.999 once), and swapins were 0. My harnesses: tools/audit/round9/D12/verify-v2/. Production perturbations were in memory only; there was no on-disk edit and no worktree.

Votes: 5 verify, 1 weaken (D12-s1-02, high -> medium), 0 refute, 0 unresolved. None of the six is a test-gap claim, so verifier.md step 4 does not apply.

## D12-s1-01: no tank probe, so every solve starts from the 55 C default

- **Finder re-run.** `state_seed.py --hours 24`: A dhw mismatch 23/24, distinct 1, 6.25 window-h below min, 1.64 kWh, truth min 31.64 C. B: 0, 23 distinct, 0.0 h, 3.89 kWh. Slab A: mismatch 5, distinct 1. load1 2.56, tf 1.000. Matches the finding.
- **Own harness.** `v2_dhw_seed.py --hours 24`. Metric: solves whose initial_state.dhw_temperature at `coordinator._await_optimize` (no probe) differs >1 K from a chained arm whose probe reports the previous plan's own +1 h dhw_temp_trajectory. Both arms start at 55.0 C, which is the dataclass default, so the finder's 50 C truth head start is removed. Config is coord_dhw, and prices roll with the clock.
- **Own numbers:**

| Run | Solves >1 K apart | Max gap | Distinct initial values (omitted arm) | First-hour DHW kWh (omitted / propagated) | load1 |
|---|---|---|---|---|---|
| base | 19 of 24 | 12.42 K | 1 | 0.45 / 2.96 | 5.58 |
| --flat | 19 of 24 | 12.96 K | 1 | – | 5.58 |
| --perturb (seed from the previous plan's +1 h, in memory) | 2 of 24 | 1.32 K | 24 | – | 5.69 |

  The propagated arm's per-step self-mismatch is 0 of 23.
- **Attacks.** Contention: counts only. Flat control: the effect survives. Head start: removed, and the effect survives. Grid: the finder's 5-cell LOO range is 6.25-6.75 h. Code: `coordinator.py:5433-5435` is the sole writer; the default is at `thermal_model.py:1085`. Real HA: the probe slot is optional, so this is reachable.
- **Not independently measured.** The slab seam. Its only number is the finder's 5/24, distinct 1.
- **Vote: verify, high.**

## D12-s1-02: untouched Hot water / Hot water tank page turns DHW on

- **Finder re-run.** `phantom_dhw.py`: options_pages_inventing_dhw_plan=2 (9 steps, 3.16 kWh each); control 0. `--fallback-dhw`: 0. load1 1.02 / 3.06.
- **Own harness.** `v2_untouched_pages.py`. The entry comes from driving the real initial flow through "Finish setup now"; it has no dhw_enabled key. Every _TOP_MENU and _ADVANCED_MENU page is submitted untouched, frontend-style with sections nested. Key: `ThermalParameters.from_config` (dhw_enabled, two_zone_enabled).
- **Own number.** 2 of 23 pages flip: hot_water adds dhw_windows, hot_water_tank adds dhw_tank_volume. Each yields 8 DHW steps / 2.87 kWh (outdoor 0 C in mine vs -3 C in the finder's). Control 0. `--fallback`: 0 of 23. load1 5.37 / 5.39.
- **Attacks.** Reach: confirmed on a flow-built entry. Nesting: same result as the finder's flat posting. Design comment at `config_flow.py:2095-2101`: the presence inference is deliberate, but no page offers a DHW off-switch, so the defect stands.
- **Severity check.** `v2_qs_workaround.py`: after hot_water the plant is (True, False); after the options Quick setup page with "no tank" it is (False, False). With `--no-quick` it stays (True, False). load1 4.08.
- **Vote: weaken to medium.** The consequence is the same phantom DHW plan D12-s3-01 rates medium, and a workaround exists.

## D12-s2-01: on/off pump's switch path withholds planned heat

- **Finder re-run.** `onoff_switch.py`: onoff failing 4 (LOO 3) of 9; shoulder withheld 0.671; e2e turn_off-with-heat 30; Kh below plan 17.23, below min 0.00. Modulating 0. `--perturb`: 0 / 0. load1 2.55 / 5.16.
- **Own harness.** `v2_onoff_sweep.py`. 14 cells from `stress.build_case` (7 SEASONS x {1z+DHW, 2z space}), P = 5.0 kW (the shipped default max). Key: production heat_pump_on_schedule.
- **Own numbers:**

| Arm / run | Cells >10% withheld (LOO) | Pooled kWh fraction | Heat-carrying steps OFF |
|---|---|---|---|
| on/off (min = max = 5.0 kW) | 4 of 14 (3) | 0.109 | 147/497 (0.296) |
| modulating (null) | 0 of 14 | 0.005 | 28/554 |
| on/off, --perturb-threshold (0.1 kW, in memory) | 0 of 14 | 0.000 | 0/497 |
| --min-offset 1.0 (min 4 kW) | 3 of 14 | – | – |

  The last row shows the mechanism also bites a high-floor modulating pump. Flat cells: 0.037 and 0.184. load1 6.51-6.71.
- **Attacks.** Contention: counts only. Flat: the effect survives. LOO: 4 -> 3. Code: bounds (0, p_max) at `optimizer.py:3962-3970` vs threshold max(0.1, min*0.5) at `:6962`, `:7024` and `pump_arbiter.py:358`. Reach: `_power_errors` accepts min == max. Severity: 0 K*h below min.
- **Vote: verify, medium.**

## D12-s2-02: mode write hard-coded to select.select_option

- **Finder re-run.** `mode_domain.py`: input_select 5/9/1, sensor 5/9/1, select 0/0/0, failing 2. `--perturb`: input_select 0/0/0, sensor 0/9/0. load1 2.80 / 6.97.
- **Own harness.** `v2_mode_write.py`. Metrics: (a) the entities_pump page saves pump_duty_mode=control with each slot domain; (b) a direct production `pump_arbiter._write(coord, "mode", ...)` on a real coordinator.
- **Own numbers.** Accepted 3 of 3 with no error; misrouted 2 of 3 (sensor 1/1, input_select 1/1); `--route`: 0 of 3. load1 6.80.
- **Limit of my metric.** Domain equality cannot see the read-only half: sensor.select_option does not exist. The finder's wrong-ticks metric (sensor 9 under the perturbation) carries that half.
- **Attacks.** Null control: select 0. Real HA: an entity service aimed at another domain's entity resolves nothing and raises nothing, so the write is booked and the repair follows. Code: `pump_arbiter.py:457-458`.
- **Vote: verify, medium** (select slot or observe mode is the workaround).

## D12-s2-03: on/off pump publishes full power as 'eco', power_normalized to -60

- **Finder re-run.** `onoff_label.py`: onoff 149 (LOO 118, 7/9 cells), min -60.0; modulating 0, min -0.2. `--min 5.0`: 0, -5.0. load1 3.65 / 5.16.
- **Own harness.** `v2_onoff_sweep.py`, same 14 cells, key `get_current_action(t_i)`.
- **Own numbers.** On/off: 203 of 203 full-power steps not 'boost', min -50.00 (P = 5). Modulating: 0 of 189, min -0.25. `--min-offset 1.0`: 0 of 184, min -4.00.
- **Attacks.** Code: divisor max(p_range, 0.1) at `optimizer.py:7032-7037`. Consequence: climate hvac_action also reads heat_pump_on, and no actuator reads action['mode'] (only boost.py and system identification do), so this is a published label and attribute only.
- **Vote: verify, medium.**

## D12-s3-01: full wizard invents a DHW tank and a second zone

- **Finder re-run.** `flow_paths.py`: paths 6, invented 2 (DHW 2, two-zone 1). `--perturb explicit_presence`: 0. load1 3.81 / 7.38.
- **Own harness.** `v2_wizard_paths.py`. 5 hand-listed routes through the real ConfigFlow with untouched frontend-style posts. Quick setup answers all "no"; device_prefill gets no device.
- **Own numbers.** Invented 2 of 5:
  - wizard_describe: dhw_tank_volume 200, 8 DHW steps.
  - wizard_thermal: DHW plus two-zone, predicted_cost 16.437.
  - finish_now 13.495, quick_no_finish 8.448 and quick_no_wizard 8.448 (the last crosses the same dhw page) all invent 0.
  - `--explicit` (explicit-only presence rules in memory): 0 of 5. load1 6.51 / 6.20.
- **Attacks.** Code: `async_step_dhw` has no "no" answer; `async_step_zones` pre-fills zone keys; the building_describe docstring names the zones hazard. The pin at `tests/entities.py:3164-3168` is a characterization. Real HA: "Continue setup" is a shipping menu option.
- **Severity.** The Quick setup workaround exists (`v2_qs_workaround.py`).
- **Vote: verify, medium.**
