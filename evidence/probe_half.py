import numpy as np, sys
sys.path[:0] = ["tests/hastub","tests","custom_components"]
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from heatpump_optimizer.optimizer import _thermostat_held_state
from profiles import replay_install
for cap in (None, 25.0, 30.0):
    over = dict(mixing_valve_target=10.0, heat_pump_max_power=9.0)
    if cap: over["buffer_max_temperature"]=cap
    params = ThermalParameters.from_config(replay_install(**over)); model = ThermalModel(params)
    o, s = -15.0, 600.0
    start = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=o, upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
    w = WeatherSeries(outdoor_temps=np.array([o]), wind_speeds=np.full(1,3.0), precipitation=np.zeros(1), solar_radiation=np.array([s]))
    h = _thermostat_held_state(model, start, w, 21.0)
    pl = h
    for _ in range(288): pl = model.simulate_step(pl, params.max_electrical_power, o, 3.0, 0.0, s, 0.25)
    z = lambda x: "/".join(f"{v:.3f}" for v in (x.room_temperature, x.upper_floor_temperature, x.lower_floor_temperature, x.slab_temperature))
    print(f"RESULT {sys.argv[1]} cap={cap}: held {z(h)} plant {z(pl)}")
