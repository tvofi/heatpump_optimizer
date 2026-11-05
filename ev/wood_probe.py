"""Reviewer's own probe (not the finder's): does the reference move with the wood tank or a fire?"""
import dataclasses, inspect, sys
import numpy as np
sys.path[:0] = []
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from profiles import house
WOOD = dict(wood_furnace_enabled=True, wood_tank_top_entity="sensor.wood", wood_tank_volume=500.0)
CFGS = {
 "valved-2z-wood": dict(two_zone=True, dhw=False, mixing_valve_mode="manual", mixing_valve_target=21.0, buffer_tank_volume=500.0, **WOOD),
 "unvalved-2z-wood": dict(two_zone=True, dhw=False, buffer_tank_volume=500.0, **WOOD),
 "unvalved-1z-wood": dict(two_zone=False, dhw=False, buffer_tank_volume=500.0, **WOOD),
}
N = 96
print("WeatherSeries fields:", [f.name for f in dataclasses.fields(WeatherSeries)])
for name, cfg in CFGS.items():
    params = ThermalParameters.from_config(house(**cfg)); params.dhw_enabled = False
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0,
        min_temp=18.0, max_temp=23.0, comfort_temp_day=21.0, comfort_temp_night=21.0))
    out = {}
    for wood in (None, 20.0, 80.0):
        for fire in (0.0, 5.0):
            st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=0.0,
                upper_floor_temperature=21.0, lower_floor_temperature=21.0, dhw_temperature=52.0,
                dhw_hours_since_legionella=20.0, buffer_tank_temperature=35.0, wood_tank_temperature=wood)
            w = WeatherSeries(outdoor_temps=np.full(N, 0.0), wind_speeds=np.full(N, 2.0), precipitation=np.zeros(N),
                solar_radiation=np.zeros(N), external_heat_kw=np.full(N, fire))
            pw, _ = opt._compute_baseline_power(w, st, 0.25)
            out[(wood, fire)] = (float(pw.sum()*0.25), float(pw[0]), float(pw.min()))
    ref = out[(None, 0.0)][0]
    for k, v in out.items():
        print(f"RESULT probe {name} wood={k[0]} fire={k[1]}kW: kWh {v[0]:.3f} step0 {v[1]:.3f} min {v[2]:.3f} dkWh vs no-wood/no-fire {v[0]-ref:+.3f}")
    print("two_tank_modelled", params.two_tank_modelled, "valve", params.mixing_valve_mode)
