import itertools, numpy as np, sys
sys.path[:0] = ["tests/hastub","tests","custom_components"]
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from heatpump_optimizer.optimizer import _thermostat_held_state
from profiles import replay_install
rows=[]
for outdoor, solar, curve in itertools.product((5.0,-5.0,-15.0),(0.0,150.0,300.0),(None,3.0,10.0)):
    over = {} if curve is None else dict(mixing_valve_target=curve)
    params = ThermalParameters.from_config(replay_install(**over)); model = ThermalModel(params)
    start = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=outdoor, upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
    w = WeatherSeries(outdoor_temps=np.array([outdoor]), wind_speeds=np.full(1,3.0), precipitation=np.zeros(1), solar_radiation=np.array([solar]))
    h = _thermostat_held_state(model, start, w, 21.0)
    pl = h
    for _ in range(288): pl = model.simulate_step(pl, params.max_electrical_power, outdoor, 3.0, 0.0, solar, 0.25)
    zs = lambda x:(x.room_temperature,x.upper_floor_temperature,x.lower_floor_temperature)
    gap = max(abs(a-b) for a,b in zip(zs(h),zs(pl)))
    lvl = h.upper_floor_temperature==h.lower_floor_temperature
    print(f"RESULT {sys.argv[1]} out={outdoor:+.0f} sun={solar:.0f} curve={curve}: held {h.room_temperature:.3f} level={lvl} plant {pl.room_temperature:.3f}/{pl.upper_floor_temperature:.3f}/{pl.lower_floor_temperature:.3f} gap {gap:.3f}")
