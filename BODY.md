Closes #1955. Leaves #201 open.

Planner power on a switch-plus-setpoint install that has no frequency entity. One probe, `probe_install` in `thermal_model.py`, reports writes, measured power and frequency. (a), (c) and (d) read it. A fully metered report, and `OptimizationConfig()` with the flag left at its default, keep the duty-cycle bounds, so those plans stay byte-identical. `clamp_planned_levels: false` is the opt-out.

(a) Projects a planned level in `(0, p_min)` up to `p_min` and leaves 0 off. The closed interval `[p_min, p_max]` was refused: it would force the pump on for the horizon. The objective and the published schedule both use the projection, and only when the probe says the surface cannot duty-cycle.

(b) A heating flow follows the planned level, from the return temperature (or the 35 °C hold when no return is configured) at the modulation floor up to `flow_heat_c` (default the existing heating-flow constant) at full power. A non-positive planned level, including a boost over an idle plan, still holds that ceiling. A missing power band keeps the constant, which is what the arbiter stubs pin.

(c) The house-heat-loss learner freezes with reason `unmetered_power` when the probe reports no measured power and no duty-cycle mechanism, ranked with the boost freeze after ventilation. A frequency install without a power meter still learns from the commanded figure, because the compressor can realize it. An install with no write surface configured is not reclassified.

(d) `planned_draw_runs` refuses a level in `(MIN_RUNNING_DRAW_KW, p_min)` when given `modulation_floor`. `step_duty` stays a two-parameter function; the floor rides on the result as `duty_floor_kw` when the solve clamped, so a caller cannot hand it a threshold.

(e), the optional thermal-power entity, is not in this diff. The card recommendation is R9-UX-9 (#1956), which already says it consumes this probe and not a second one.

## Head

afbf64f3a396dc26ead7ef70d1151d7b1953a733

Merged `origin/main` at `6001b09a557259f37319b400d219cf83e02c563f` (`2026-10-06T21:12:46Z`).

## Mutation proof

Each line restored after the run. The instrument is the production function the features.py check imports.

- `projected[gap] = lo` replaced with a no-op assignment. `project_planned_levels` on `[0, 0.3, 0.5, 3, 14, 20]` at `p_min` 3, `p_max` 14 left `0.3` and `0.5` in place. Check that goes red: "a switch-plus-setpoint install clamps a sub-minimum level up to p_min and keeps off off".
- `return floor + frac * (heat - floor)` replaced with `return heat`. Check that goes red: "the heating flow is the ceiling at full power and the inlet at p_min, and a configured ceiling moves it".
- `return UNMETERED_POWER_FREEZE` replaced with `return None`. Check that goes red: "the house learner freezes on an unmetered switch-plus-setpoint install and not on a metered one".
- The sub-minimum branch of `planned_draw_runs` returned the duty-cycle comparison. Check that goes red: "null control: the duty-cycle reading of 0.3 kW still runs when no floor is passed" (the floor arm).

`stress.py` is left to CI's mutation check. No local `--pin-killed`.

## Null control

`OptimizationConfig()` leaves `clamp_planned_levels` false. `from_mapping` on an empty config and on a config with a power entity plus a frequency entity leaves it false. `planned_draw_runs(0.3)` with no floor is true. `learner_unmetered` on that metered config is `None`. `step_duty` on a plan of 0.15 kW space plus 2.0 kW hot water, then 1.5 kW space, is `both` then `space`, and its signature has two parameters.

## Figures

none

## Red checks

`tests/features.py` "R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it" printed the same pair on this branch and on unmodified `origin/main` at `a28fd0ae` (optimizer.py is unchanged from there to `6001b09a`). The branch did not move it. Cheaper detector: none; that check is the measurement.

`tests/features.py` "R9-F2.4 P2: the arbiter splits a step's duty on the plan's own running rule, so no caller can hand it a threshold" went red while `step_duty` had a third parameter. The parameter is gone. The final tree's signature has two parameters and the duties are `both`, `space`.

## Forward-carry

none

## Friction

none
