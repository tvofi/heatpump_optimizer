import sys, os, itertools
import numpy as np
from datetime import datetime
TREE = sys.argv[1]
sys.path[:0] = [os.path.join(TREE, "tests"), os.path.join(TREE, "custom_components")]
from profiles import house, prices, solve_inputs, weather
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import dhw_planner
START = datetime(2026, 1, 15, 0, 0)
def solve(price_p, weather_p, tank, hyst, leg_hours=20.0, ext=False, cfgmod=None):
    cfg = house()
    if cfgmod: cfg.update(cfgmod)
    params = ThermalParameters.from_config(cfg); params.dhw_enabled = True
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
    outdoor, wind, rain, sun = weather(weather_p, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
        dhw_temperature=tank, dhw_hours_since_legionella=leg_hours, upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    st.dhw_start_hysteresis_k = hyst
    if ext: st.external_heat_active = True
    r = opt.optimize(inputs=solve_inputs(initial_state=st, prices=np.asarray(prices(price_p, START), float),
        outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain, solar_radiation=sun, start_time=START))
    return params, r
def judge(params, r, hyst):
    plan = np.asarray(r.dhw_power_schedule, float); temps = np.asarray(r.dhw_temp_trajectory, float)
    leg = None
    for name in ("dhw_legionella_step", "legionella_step"):
        if hasattr(r, name): leg = getattr(r, name)
    dp = getattr(r, "dhw_plan", None)
    if leg is None and dp is not None: leg = getattr(dp, "legionella_step", None)
    start = dhw_planner.dhw_start_temps(params, hyst, plan.size, leg)
    on = plan > 0; bad = []
    if start is not None:
        for i in range(1, plan.size):
            if on[i] and not on[i-1] and temps[i] >= start[i]: bad.append((i, round(float(temps[i]),2), round(float(start[i]),2)))
    return plan, temps, leg, bad
if __name__ == "__main__":
    print("result attrs with legionella:", [a for a in dir(solve("flat","winter_mild",50.0,None)[1]) if "legion" in a.lower() or a=="dhw_plan"])
    tot = 0
    for label, kw in [("base",{}),("cycle_due",{"leg_hours":400.0}),("external_heat",{"ext":True}),("cycle_due+ext",{"leg_hours":400.0,"ext":True})]:
        for hyst in (None, 1.0, 4.0, 6.0, 10.0, 20.0):
            nbad = 0; peak = []; mins=[]; legs=[]; ex=None
            for pp, wp, tank in itertools.product(("winter_typical","flat"),("winter_cold","summer_warm"),(45.0,53.0)):
                params, r = solve(pp, wp, tank, hyst, **kw)
                plan, temps, leg, bad = judge(params, r, hyst)
                nbad += len(bad); peak.append(float(temps.max())); mins.append(float(temps.min())); legs.append(leg)
                if bad and ex is None: ex = (pp, wp, tank, bad[:3])
            tot += nbad
            print(f"RESULT {label} hyst={hyst} unstartable_runs={nbad} tank_peak_min={min(peak):.1f} tank_peak_max={max(peak):.1f} tank_min={min(mins):.1f} legionella_steps={legs} example={ex}")
    print("RESULT total_unstartable", tot)
