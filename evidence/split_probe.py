"""Reviewer probe: the two-zone valve-fed law at splits other than r = 0.5.

Runs the PR's invariant (a)/(b) shape (thermostat-held state, then the plant at
its pump for 960 steps, scalar and batch) on the replay install with
upper_floor_area_ratio / radiator_power_fraction overridden.
"""
import numpy as np
from profiles import replay_install
from heatpump_optimizer.optimizer import _thermostat_held_state
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries

N = 960
for r, f in ((0.5, 0.5), (0.3, 0.7), (0.7, 0.3), (0.3, 0.5)):
    p = ThermalParameters.from_config(replay_install())
    p.upper_floor_area_ratio, p.radiator_power_fraction = r, f
    m = ThermalModel(p)
    for out in (5.0, -5.0, -15.0):
        st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=out,
                          upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                          buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
        w = WeatherSeries(outdoor_temps=np.full(N, out), wind_speeds=np.full(N, 3.0),
                          precipitation=np.zeros(N), solar_radiation=np.zeros(N))
        h = _thermostat_held_state(m, st, w, 21.0)
        s = h
        for _ in range(N):
            s = m.simulate_step(s, p.max_electrical_power, out, 3.0, 0.0, 0.0, 0.25)
        b = m.simulate_trajectory_batch(h, np.full((1, N), p.max_electrical_power), w, dt_hours=0.25)
        print(f"r {r} rad {f} out {out:+.0f}: held {h.room_temperature:.4f} scalar {s.room_temperature:.4f} "
              f"batch {float(b['room'][0, -1]):.4f} upper {s.upper_floor_temperature:.3f} lower {s.lower_floor_temperature:.3f}")
