"""R10-OUTSIDE-DHW-START-HYSTERESIS: planned hot-water runs the pump would not start.

Drives the optimizer as ``tests/validate.py`` drives it, over 18 solves (price
profiles winter_typical and flat; weather winter_cold, winter_mild and
summer_warm; starting tank 45, 50 and 53 degC; everyday set-point 55; 24 h at
15 minutes), and counts the planned hot-water runs that do not begin at step 0
against a start temperature of the set-point less each of 2, 4 and 6 K.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_start_hysteresis.py [TREE] [--hysteresis K]

TREE is a checkout root (default: this one; a ``git archive`` export of the
merge base reads the gap). ``--hysteresis K`` hands the planner the pump's
start hysteresis (``ThermalState.dhw_start_hysteresis_k``); a tree without the
field prints ``hysteresis=unsupported`` and plans as it always did.

RESULT lines, each a sum over the 18 solves:
  runs_not_at_step0                      planned runs beginning after step 0
  runs_at_or_above_minus_{2,4,6}k        of those, begun on a tank at or above 55 - K
  kwh_planned / kwh_at_or_above_minus_4k planned hot-water kWh, and the share in those runs
  write_to_start_max_c                   the highest set-point that would start one of the
                                         minus-4 K runs with a 4 K hysteresis (tank + 4);
                                         above 55 it is over the user's charge limit
  floor_deficit_k_steps                  degree-steps of the simulated tank under 45 degC
  dhw_cost                               the planned hot-water energy at the day's prices
  plan_sha1                              sha1 over the 18 hot-water schedules and trajectories
Null control: ``--hysteresis`` unset and ``--hysteresis 0`` print the
plan_sha1 the merge base prints; a hysteresis of 4 prints
runs_at_or_above_minus_4k=0 only on a tree whose planner reads it.
"""
import hashlib
import os
import sys
from datetime import datetime

import numpy as np

ARGS = sys.argv[1:]
HYSTERESIS = None
if "--hysteresis" in ARGS:
    at = ARGS.index("--hysteresis")
    HYSTERESIS = float(ARGS[at + 1])
    del ARGS[at : at + 2]
TREE = os.path.abspath(ARGS[0] if ARGS else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path[:0] = [os.path.join(TREE, "tests"), os.path.join(TREE, "custom_components")]

from profiles import house, prices, solve_inputs, weather  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
SETPOINT_C, FLOOR_C, DT_H = 55.0, 45.0, 0.25
SUPPORTED = hasattr(ThermalState(), "dhw_start_hysteresis_k")


def solve(price_p: str, weather_p: str, tank_c: float):
    cfg = house()
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
    outdoor, wind, rain, sun = weather(weather_p, START)
    state = ThermalState(
        room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
        dhw_temperature=tank_c, dhw_hours_since_legionella=20.0, upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    if SUPPORTED and HYSTERESIS is not None:
        state.dhw_start_hysteresis_k = HYSTERESIS
    price = np.asarray(prices(price_p, START), dtype=float)
    result = opt.optimize(inputs=solve_inputs(
        initial_state=state, prices=price, outdoor_temps=outdoor, wind_speeds=wind,
        precipitation=rain, solar_radiation=sun, start_time=START))
    return (np.asarray(result.dhw_power_schedule, dtype=float),
            np.asarray(result.dhw_temp_trajectory, dtype=float), price)


def main() -> int:
    total = {"runs": 0, 2: 0, 4: 0, 6: 0}
    kwh = kwh_4k = deficit = cost = 0.0
    write_max = float("-inf")
    digest = hashlib.sha1()
    for price_p in ("winter_typical", "flat"):
        for weather_p in ("winter_cold", "winter_mild", "summer_warm"):
            for tank_c in (45.0, 50.0, 53.0):
                plan, temps, price = solve(price_p, weather_p, tank_c)
                digest.update(np.round(plan, 9).tobytes() + np.round(temps, 9).tobytes())
                on = plan > 0.0
                kwh += float(plan.sum()) * DT_H
                cost += float((plan * price[: plan.size]).sum()) * DT_H
                deficit += float(np.clip(FLOOR_C - temps, 0.0, None).sum())
                for i in range(1, plan.size):
                    if not on[i] or on[i - 1]:
                        continue
                    end = i + int(np.argmin(np.append(on[i:], False)))
                    total["runs"] += 1
                    for k in (2, 4, 6):
                        total[k] += int(temps[i] >= SETPOINT_C - k)
                    if temps[i] >= SETPOINT_C - 4:
                        kwh_4k += float(plan[i:end].sum()) * DT_H
                        write_max = max(write_max, float(temps[i]) + 4.0)
    shown = "unset" if HYSTERESIS is None else f"{HYSTERESIS:g}" if SUPPORTED else "unsupported"
    print(f"RESULT hysteresis={shown}")
    print(f"RESULT runs_not_at_step0={total['runs']} count")
    for k in (2, 4, 6):
        print(f"RESULT runs_at_or_above_minus_{k}k={total[k]} count")
    print(f"RESULT kwh_planned={kwh:.2f} kWh")
    print(f"RESULT kwh_at_or_above_minus_4k={kwh_4k:.2f} kWh")
    print("RESULT write_to_start_max_c=" + ("none" if write_max == float("-inf") else f"{write_max:.1f} degC"))
    print(f"RESULT floor_deficit_k_steps={deficit:.2f} K*steps")
    print(f"RESULT dhw_cost={cost:.2f} price-units")
    print(f"RESULT plan_sha1={digest.hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
