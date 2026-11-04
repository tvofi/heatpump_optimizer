"""Reviewer probe: two-zone plan's comfort_kw sum (finder's house profile, two_zone=True)."""
from datetime import datetime
from profiles import house, prices, solve_inputs, weather, DT
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
cfg = house(two_zone=True, dhw=False); par = ThermalParameters.from_config(cfg); par.dhw_enabled = False
m = ThermalModel(par); opt = HeatPumpOptimizer(m, OptimizationConfig(horizon_hours=24, time_step_minutes=15,
    target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
t0 = datetime(2026, 1, 15); o, w, r, s = weather("winter_cold", t0)
plan = opt.optimize(inputs=solve_inputs(initial_state=ThermalState(room_temperature=19.0, slab_temperature=20.0,
    outdoor_temperature=float(o[0]), upper_floor_temperature=20.5, lower_floor_temperature=18.5, dhw_temperature=52.0,
    dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0), prices=prices("flat", t0), outdoor_temps=o,
    wind_speeds=w, precipitation=r, solar_radiation=s, start_time=t0))
c = [x["comfort_kw"] for x in plan.settlement_schedule]
print(f"RESULT twozone two_zone={par.two_zone_enabled} comfort_kwh {sum(c)*DT:.4f} step0 {c[0]:.4f}")
