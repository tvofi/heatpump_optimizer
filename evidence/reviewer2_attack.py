"""Round-2 reviewer's attack (the reviewer's instrument, adapted from round 1's ev/reviewer_attack.py):
planned hot-water runs after step 0 that begin at or above the start temperature, on stepped set-point
entities, over configurations the builder's harness does not hold (cycle due, external heat, other steps).
Two judges per run: the code's own dhw_start_temps, and the reviewer's own arithmetic for a non-cycle step
(min(set-point, charge limit) floored onto the step, less the hysteresis).

    PYTHONPATH=tests/hastub python3 reviewer2_attack.py TREE
"""
import sys, os, itertools, math
import numpy as np
from datetime import datetime
TREE = sys.argv[1]
sys.path[:0] = [os.path.join(TREE, "tests"), os.path.join(TREE, "custom_components")]
from profiles import house, prices, solve_inputs, weather
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import dhw_planner
from heatpump_optimizer.inputs import SetpointGrid
START = datetime(2026, 1, 15, 0, 0)


def solve(price_p, weather_p, tank, hyst, setpoint, grid, leg_hours=20.0, ext=False):
    cfg = house()
    cfg["dhw_setpoint"] = setpoint
    params = ThermalParameters.from_config(cfg); params.dhw_enabled = True
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
    outdoor, wind, rain, sun = weather(weather_p, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
        dhw_temperature=tank, dhw_hours_since_legionella=leg_hours, upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    st.dhw_start_hysteresis_k = hyst
    st.dhw_setpoint_grid = grid
    if ext: st.external_heat_active = True
    r = opt.optimize(inputs=solve_inputs(initial_state=st, prices=np.asarray(prices(price_p, START), float),
        outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain, solar_radiation=sun, start_time=START))
    return params, st, r


def judge(params, st, r, hyst, grid):
    plan = np.asarray(r.dhw_power_schedule, float); temps = np.asarray(r.dhw_temp_trajectory, float)
    on = plan > 0
    begins = [i for i in range(1, plan.size) if on[i] and not on[i - 1]]
    # the code's own judge: the most lenient reading over every possible cycle step is the cycle target's,
    # so a run is counted bad for the code only when it is at or above the cycle step's start as well
    own_every = dhw_planner.dhw_start_temps(params, st, plan.size, None)
    own_cycle = dhw_planner.dhw_start_temps(params, st, plan.size, 0)
    cyc = None if own_cycle is None else float(own_cycle[0])
    bad_code = [] if own_every is None else [i for i in begins if temps[i] >= own_every[i]]
    bad_code_even_as_cycle = [i for i in bad_code if cyc is None or temps[i] >= cyc]
    # the reviewer's arithmetic for a non-cycle step
    target = min(float(params.dhw_setpoint), float(params.dhw_max_temp))
    if grid is not None:
        target = math.floor(target / grid.step + 1e-9) * grid.step
    mine = None if not hyst else target - hyst
    bad_mine = [] if mine is None else [i for i in begins if temps[i] >= mine]
    agree = own_every is None or mine is None or abs(float(own_every[-1]) - mine) < 1e-9
    return len(begins), len(bad_code), len(bad_code_even_as_cycle), len(bad_mine), agree, (None if own_every is None else float(own_every[-1])), mine, cyc


if __name__ == "__main__":
    grids = [("58/none", 58.0, None), ("58/step5", 58.0, SetpointGrid("°C", 5.0, 30.0, 70.0)),
             ("57/step5", 57.0, SetpointGrid("°C", 5.0, 30.0, 70.0)), ("55/step0.5", 55.0, SetpointGrid("°C", 0.5, 30.0, 70.0)),
             ("53/step2", 53.0, SetpointGrid("°C", 2.0, 30.0, 70.0)), ("58/step5/max52", 58.0, SetpointGrid("°C", 5.0, 30.0, 52.0))]
    which = sys.argv[2:] or ["base", "cycle_due", "external_heat", "cycle_due+ext"]
    kws = {"base": {}, "cycle_due": {"leg_hours": 400.0}, "external_heat": {"ext": True}, "cycle_due+ext": {"leg_hours": 400.0, "ext": True}}
    tot_code = tot_mine = 0
    for label in which:
        for gname, sp, grid in grids:
            for hyst in (None, 1.0, 4.0, 10.0):
                nb = nc = ncc = nm = 0; ok = True; own = mine = cyc = None
                for pp, wp, tank in itertools.product(("winter_typical", "flat"), ("winter_cold", "summer_warm"), (45.0, 53.0)):
                    params, st, r = solve(pp, wp, tank, hyst, sp, grid, **kws[label])
                    b, c, cc, m, agree, own, mine, cyc = judge(params, st, r, hyst, grid)
                    nb += b; nc += c; ncc += cc; nm += m; ok &= agree
                if hyst:
                    tot_code += ncc; tot_mine += nm
                print(f"RESULT {label} grid={gname} hyst={hyst} runs_after_step0={nb} at_or_above_code_everyday_start={nc} "
                      f"of_those_also_at_or_above_cycle_start={ncc} at_or_above_reviewer_everyday_start={nm} "
                      f"code_everyday_start={own} reviewer_everyday_start={mine} code_cycle_start={cyc} judges_agree={ok}", flush=True)
    print("RESULT total_at_or_above_even_as_cycle", tot_code, "total_at_or_above_reviewer_everyday_start", tot_mine)
