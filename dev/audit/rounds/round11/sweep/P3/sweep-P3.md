# Round 11 class sweep: P3

Class P3 in `dev/audit/config/bugclasses.json` is "a capacity floor or divisor
applied inconsistently across sibling formulas". Its status is `barriered`.
The barrier is R9-P3 in `tests/features.py`. Arm (a) covers `max(E, c>0)`
floors on a `ThermalParameters` quantity, and arm (b) covers the two-zone floor
price. The class record already names the gap: "a sibling disagreement that is
not a floor ... is pinned per pair, not class-wide".

The one round-11 survivor sits in that gap:

| finding | shape |
|---|---|
| D16-s2-04 (verified, medium) | The modulation floor is stated twice: as a power the plan books (`min_electrical_power`, the band bottom) and as a set-point lift over the inlet (`start_flow_min_lift_k`). `pump_arbiter._flow_target` books the first and writes the second, and nothing relates them. On a plant lifting 8 K/kW, a step booked at 1.0 kW runs 30 starts at 0.602 kW. |

The R9-P3 arms pass this tree, and neither arm reads the lift, so
`sweep-P3.json` sets `barriered` to `false`.

Measured at `handoff/audit-r11-register` @ 28b864af6, detached worktree, venv-ci
Python 3.14.7, Linux x86_64, `OPENBLAS_CORETYPE=Haswell`. All the figures are
counts or set-point comparisons, so timing does not affect them.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P3/enumerate.py [--null | --perturb] [--json PATH]`

It walks the AST of the whole package and lists nothing by hand. The only
named exception is the lift's owner chain in `thermal_model` (three
functions). A seam is any function that reads the modulation floor in either
unit:
- **power**: a load of `min_electrical_power`, or a call to a same-module
  helper that loads it;
- **lift**: `FLOW_MIN_LIFT_K`, the option key or its default,
  `configured_flow_min_lift_k`, `start_flow_min_lift_k` or
  `modulation_floor_flow_c`.

| arm | seam rule | flagged |
|---|---|---|
| M | reads both units, names no plant gain (`*per_kw*`, `*_gain`), and is outside the owner chain: it books one floor and writes the other | 1 |
| L | reads a lift other than the owner `start_flow_min_lift_k` (the raw constant, the option, or `configured_flow_min_lift_k`), outside the owner chain | 1 |
| P | every other reader of either unit, listed for disposition | 55 |

`RESULT tree M=1 L=1 P=55 seams_total=57`. The full listing is in
`D14/sweep-P3/seams.json`.

**Positive control.** M flags `pump_arbiter._flow_target`, the site of
D16-s2-04, and the script exits 0 only when it does. The finder's harness was
re-run on this tree:
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s2/effect.py`.
It prints `min-cold-tank_k8.0_starts=30 measured_kw=0.602` and
`k10.0_starts=38 measured_kw=0.5`; k 2.0-6.5 give 1 start at 1.0 kW.

**Null control.** `--null` runs over `D14/sweep-P3/fixture_clean/`. In that
fixture the floor write is priced by a plant gain
(`p_min * lift_k_per_kw`) and every lift goes through `start_flow_min_lift_k`.
It prints `M=0 L=0 P=5`.

**Perturbation.** `--perturb` copies the package and makes one one-line
re-introduction: in `pump_arbiter._nudged`, the floor fallback `or 0.0`
becomes `or FLOW_MIN_LIFT_K`, which puts a lift into a power formula. It prints
`perturb_delta M=+1 L=+1 (expected +1 +1)`.

## Disposition of every seam

**Instance at a judged site** (`beyond_finding: false`):

| seam | probe |
|---|---|
| M `pump_arbiter._flow_target` | `effect.py` -> `min-cold-tank_k8.0_starts=30 measured_kw=0.602` against the 1.0 kW booked (D16-s2-04) |

**Instance beyond the finding** (`beyond_finding: true`, 1):

| seam | what disagrees | probe |
|---|---|---|
| L `pump_arbiter._full_draw_c` | On a return target, the headroom that makes the ceiling "the set-point that commands the pump's maximum draw" (`FlowCommand.ceiling_c`, the meaning `draw_range` reads it with) is keyed on the rated `FLOW_MIN_LIFT_K` (5 K). The floor write is keyed on `start_flow_min_lift_k`: the configured 0.5-15 K, never below the read start hysteresis. With a lift above 5 K and the inlet within that lift of the ceiling, the floor set-point clips to the ceiling. The step booked at `p_min` then writes exactly the value `_full_draw_c` calls the full-draw command. | `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep-P3/probe_full_draw.py` exits 1 with `cells=1170 contradictions=210 off_default_lift=210`, lifts 5.5-15 K. Example: lift 15 K, inlet 40 C, ceiling 45 C. `--null` (rated 5 K) gives 0, and `--fixed` (`_full_draw_c` keyed on `start_flow_min_lift_k`) gives 0. |

This probe measures only the code-level contradiction. It does not measure
what `draw_range` then learns from those draws; see "Not done".

**Guarded:**

| seam | guard |
|---|---|
| `thermal_model.start_flow_min_lift_k`, `configured_flow_min_lift_k`, `modulation_floor_flow_c` | the owner chain itself: one constant, the configured lift, and the hysteresis max taken once |
| P `ThermalParameters.flow_lift_power_floor_kw`, `on_threshold_kw` | proportional to `min_electrical_power` with the constants pinned by R9-P3's per-floor value checks (`tests/features.py`) |
| P `pump_arbiter._feedback_on`, `_nudged` (and `_feedback`, which reads neither unit directly) | The closed loop that should reconcile the two units. It reads the power floor only, as the deadband base `max(planned, floor)`. D16-s2-04 shows the guard failing: the run resets on every stop. That failure is the judged instance, not a second seam. |

**Not applicable** (they read the power floor and nothing else, so they cannot
hold a power-versus-lift disagreement; power-only floor disagreements are R9-P3
arm (a)'s domain):

| file | seams |
|---|---|
| optimizer.py (29) | `_duty_floor`, `_stop_availability`, `_with_stop_availability`, `_shipped_and_received`, `_switch_cost_fn`, `_start_cost_fn`, `_avoid_priced_switches`, `_projection`, `_run_plans`, `_space_scope`, `_stage_box`, `_resolved_runs`, `_best_runs`, `_commit_runs`, `_power_fraction`, `_zone_setpoints`, `_build_result`, `_co_optimize`, `optimize._solve`, `_pin_on_power`, `_solve_objectives`, `objective`, `objective_batch`, `_optimize_space_only`, `_optimize_with_dhw`, `_power_to_setpoints`, `_power_to_displace_schedule`, `_idle_action`, `get_current_action` |
| thermal_model.py (9) | `ThermalParameters.clamp`, `_tabled_values`, `from_config`, `_partload_derate`, `partload_factor`, `heat_per_cop_kw`, `power_for_heat_per_cop_kw`, `refill_power_kwh`, `added_power_for_heat_per_cop_kw` |
| draw_range.py (5) | `power_floor_kw`, `fold`, `planned_range`, `diagnostics_view`, `solve_band` |
| pump_arbiter.py (2) | `_level_kw`, `_band_kw` (the power side of the M instance, read through it) |
| coordinator.py (2) | `_band_fields`, `_solve_hubs` |
| dhw_planner.py (1) | `DhwPlanner._build_dhw_requirements` |

## Barrier proposal

Add arm (c) to R9-P3 in `tests/features.py`. It runs this enumerator's M and L
arms as zero-group checks:
- **L**: no lift is read outside the owner chain except through
  `start_flow_min_lift_k`. This clears `_full_draw_c` once the headroom takes
  the owned lift.
- **M**: no function both books the power floor and writes the lift floor
  unless it names a plant gain. Today no lift-per-kW quantity exists anywhere
  in the package, so M's fix is a learned or configured K/kW. The arm cannot
  pass until that fix lands. Until then it pins `_flow_target` as the one named
  exception, with D16-s2-04 cited.

Both checks are AST-only, about 0.3 s of gate time over the package.

## Not done

- These files are untracked. A committer must classify `D14/sweep-P3/`
  (`enumerate.py`, `probe_full_draw.py`, `seams.json`, `fixture_clean/`), or
  `tests/entities.py` fails.
- The `_full_draw_c` probe measures the contradiction between the two set-point
  meanings, not its effect on the learned band. A `draw_range` fold over a
  plant run at a lift above 5 K is the next measurement.
- Arm M keys gain names lexically. A gain under another name would read as
  absent, which over-flags; it cannot under-flag.
