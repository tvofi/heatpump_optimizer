# D12 verify-v1 (round 9, lens V1 reproduce)

Tree: /home/claude/wt/D12, evidence commit 6f51db2c (baseline 1936d5ca + round9/). Python 3.14 venv, PYTHONPATH=tests/hastub. Box: 4 vCPU cloud container shared with the other G2-V1 seats. Every number below is a count or ratio (contention-immune); load1 was 2.5-5.9 and thread_factor 1.000 on every run. No production file was edited on disk; perturbations were applied in memory.

Exposure: a grep for "tank probe" over docs/*.md returned one line of docs/audit-2026-09.md (row D8-01, not a D12 finding). It was not sought, and it was not used.

Tally: verify 6, weaken 0, refute 0, unresolved 0.

## D12-s1-01: no tank probe, so the solver starts every cycle from the 55 C default. Vote: verify, high (conditional)
- Re-run `s1/state_seed.py --hours 24`: A 23/24 mismatches, 1 distinct initial value, 6.25 window-h below min, 1.64 kWh, truth min 31.64 C. B 0, 23 distinct, 0.0 h, 3.89 kWh. Same as the finder.
- `--flat`: A 23 / 6.5 h / 0.3 kWh, B 0 / 0.0 h / 3.65 kWh. Same as the finder.
- `--grid`: 5 cells, 6.25..6.75 h; 6.500 h with the most favourable cell dropped. Same as the finder.
- Perturbation (arm B): 23 -> 0 and 6.25 -> 0.0 h.
- Own harness `verify-v1/dhw_default.py`:
  - One-line in-memory production perturbation, ThermalState.dhw_temperature default 55 -> 45: executed DHW 1.64 -> 16.0 kWh, window-h 6.25 -> 0.0. The solver's DHW plan tracks the constant.
  - Control, truth tank started at 55 C: 21 mismatches, 5.75 h. The result does not depend on the harness's 50 C start.
- Writers: coordinator.py:5435 is the only assignment to `_current_state.dhw_temperature`.
- Method: the "truth" tank is heated only by the plan's DHW. Cold-tank hours are a real consequence only where the plan's DHW is actuated. Where the pump's thermostat heats the tank, the defect is a wrong plan and cost (medium). This is left to V3's reach lens.
- The slab half is weaker: 5/24 mismatches at time-varying prices, 0/24 at flat.
- Metric: count of solves whose `_solve_snapshot` dhw_temperature differs >1 K from the model-truth tank.

## D12-s1-02: an untouched Hot water or Hot water tank page enables DHW. Vote: verify, high
- Re-run `s1/phantom_dhw.py`: 2 pages, each 9 steps and 3.16 kWh. The no-save control gives 0/0. `--fallback-dhw` gives 0 (the wizard seam stays at 9/3.16, which is D12-s3-01's seam). Same as the finder.
- Own harness `verify-v1/phantom_undo.py`: re-saving the page with the DHW field omitted leaves the key stored and dhw_enabled True on 2/2 pages. The options flow never writes dhw_enabled. No in-UI undo was found, so high stands.
- Design attack: config_flow.py:2095-2101 records storing the DHW pair as deliberate. The fallback perturbation would also remove the only way to switch on a probe-less default tank, so the fix needs an explicit answer.
- Seam-rule instrument `s1/flow_pages.py`: `--no-omit`, its declared perturbation ("count up"), prints 2, the same as the baseline. The rule's own perturbation is void on this tree, so "the other 19 pages invent nothing" cannot be attributed to `_omit_unstored_defaults`.
- The same presence rule underlies D12-s3-01.
- Metric: option pages whose untouched submit yields a plan with DHW power > 0.

## D12-s2-01: the on/off switch path switches off planned sub-floor heat. Vote: verify, medium
- Re-run `s2/onoff_switch.py`:
  - on/off arm: 4 of 9 cells fail (3 with the worst dropped); mean 0.136 (0.069 with the worst dropped); shoulder 0.671 (8.30 of 12.38 kWh).
  - End-to-end switch.turn_off calls on steps with planned heat: 30 on/off, 0 modulating.
  - Shoulder: min room 20.64 C planned vs 19.89 C actuated, 17.23 K*h below the plan, 0.00 K*h below min.
  - All within the finder's tolerance.
- `--perturb`: 4 -> 0 cells, e2e 30 -> 0. `--min 1.0`: 4 -> 0, e2e 30 -> 0. Null control (modulating arm): 0 cells, e2e 0.
- Own harness `verify-v1/onoff_delivered.py`: net_ratio counts every ON step at 6 kW, as an on/off pump switched ON delivers. Range 0.485..1.652. Only 1 of 9 cells (shoulder, 0.485) delivers less than 90% of the plan. The other three "failing" cells come out at 0.957, 1.008 and 0.928.
- Consequence: withheld_frac and the finder's consequence arm are one-sided, because they ignore rounding up. The 4/9 headline overstates net under-delivery. The shoulder net shortfall of 51% is real, and it stays bounded (0 K*h below min, with an hourly re-plan).
- Metric: withheld_frac as the finder defines it.

## D12-s2-02: the arbiter writes the mode with select.select_option on any domain. Vote: verify, medium
- Re-run `s2/mode_domain.py`: input_select 5 misrouted writes / 9 wrong ticks / repair raised; sensor 5 / 9 / 1; select 0 / 0 / 0; failing domains 2.
- `--perturb`: input_select 0 / 0 / 0; sensor 0 / 9 / 0 (the read-only half, as the header predicts); failing domains 1.
- Code: pump_arbiter.py:456-461 hard-codes the "select" domain; topology.py:100 accepts select, sensor and input_select in the mode slot.
- The harness models HA routing itself. Real-HA behaviour is V3's lens.
- Metric: mode-slot calls whose service domain differs from the target's domain.

## D12-s2-03: on an on/off pump, full-power steps publish "eco" and power_normalized reaches -60. Vote: verify, medium
- Re-run `s2/onoff_label.py`: 149 mislabelled full-power steps (118 with the worst cell dropped; 7/9 cells; range 0..31), power_normalized min -60.0. Modulating arm: 0 mislabelled, min -0.2 over 585 steps (the finder's lead).
- `--min 5.0`: 0 mislabelled, min -5.0.
- Own (`verify-v1/onoff_delivered.py`): the same `max(range, 0.1)` divisor sends all 149 full-power on/off steps to setpoint == min_temp in `_power_to_setpoints`. The modulating arm gives 0. `_power_to_displace_schedule` has the same form.
- If an on/off install drives a setpoint or displace path, the consequence is actuation, not only a label. This is left to V3.
- Metric: full-power steps whose HeatPumpActionSensor state is not "boost".

## D12-s3-01: the full wizard invents a DHW tank and a second zone. Vote: verify, medium
- Re-run `s3/flow_paths.py`: 6 paths, 2 inventing (DHW 2, two-zone 1). `--answers no` and `--answers shipped` give the same. `--perturb explicit_presence` gives 0. Null control: the 4 quick-setup paths give 0.
- Harness header defect: it states "Expected paths=5, invented_paths=3 (exact)"; the executed and recorded values are 6 / 2.
- Secondary numbers differ from the record: thermal path 26.36 vs 21.32 kWh and cost 19.831 vs 11.421, where the record has 26.45 / 22.24 and 19.289 / 11.796. The source was not isolated. The headline count is exact.
- Both invented-DHW paths plan 0.00 kWh DHW in the first cycle, so the first-cycle cost gap comes from the invented second zone.
- Metric: completion paths whose first update publishes an unaffirmed DHW tank or second zone.

## Harnesses written (tools/audit/round9/D12/verify-v1/)
- dhw_default.py: D12-s1-01 in-memory default perturbation and start-state control.
- phantom_undo.py: D12-s1-02 in-UI undo check.
- onoff_delivered.py: D12-s2-01 net_ratio and D12-s2-03 setpoint seam.

## Not done
- Nothing was checked in real HA; that is V3's lens.
- The drift in D12-s3-01's secondary kWh and cost numbers was not traced to its source.
