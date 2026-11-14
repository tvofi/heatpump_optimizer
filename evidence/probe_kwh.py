import numpy as np, sys
sys.path[:0] = ["tests/hastub","tests","custom_components"]
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, _thermostat_held_state
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from profiles import replay_install
for o in (5.0,0.0,-5.0,-15.0):
    params = ThermalParameters.from_config(replay_install()); model = ThermalModel(params)
    opt = HeatPumpOptimizer(model, OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0))
    w = WeatherSeries(outdoor_temps=np.full(96,o), wind_speeds=np.full(96,3.0), precipitation=np.zeros(96), solar_radiation=np.zeros(96))
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=o, upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
    h = _thermostat_held_state(model, st, w, 21.0)
    pw = opt._compute_baseline_power(w, st, 0.25, np.full(96,21.0))[0]
    print(f"RESULT {sys.argv[1]} {o:+.0f} C held {h.room_temperature:.3f} sum(power) {np.sum(pw):.4f} sum*0.25 {np.sum(pw)*0.25:.4f}")
