"""Reviewer's probe: the reference on warm houses, to tell floor-in-loop from floor-at-return."""
import numpy as np
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from profiles import house
N = 96
for name, cfg, room, out in (("plain-1z warm", dict(two_zone=False, dhw=False), 23.5, 18.0),
                             ("plain-2z warm", dict(two_zone=True, dhw=False), 23.5, 18.0),
                             ("plain-1z swing", dict(two_zone=False, dhw=False), 22.5, None)):
    params = ThermalParameters.from_config(house(**cfg)); params.dhw_enabled = False
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0,
        min_temp=18.0, max_temp=23.0, comfort_temp_day=21.0, comfort_temp_night=21.0))
    temps = np.full(N, out) if out is not None else 12.0 + 8.0 * np.sin(np.linspace(0, 2 * np.pi, N))
    st = ThermalState(room_temperature=room, slab_temperature=room + 0.5, outdoor_temperature=float(temps[0]),
        upper_floor_temperature=room, lower_floor_temperature=room, buffer_tank_temperature=30.0)
    w = WeatherSeries(outdoor_temps=temps, wind_speeds=np.full(N, 2.0), precipitation=np.zeros(N), solar_radiation=np.full(N, 150.0))
    pw, end = opt._compute_baseline_power(w, st, 0.25)
    print(f"RESULT floor {name}: kWh {pw.sum()*0.25:.4f} min {pw.min():.4f} end room {end.room_temperature:.3f}")
