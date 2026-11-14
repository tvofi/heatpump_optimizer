import itertools, numpy as np, sys
sys.path[:0] = ["tests/hastub","tests","custom_components"]
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from heatpump_optimizer.optimizer import _thermostat_held_state
from profiles import replay_install
out=[]
for o, s, pump in itertools.product((5.0,-5.0,-15.0,-25.0),(0.0,300.0),(1.0,2.0,4.0,9.0)):
    params = ThermalParameters.from_config(replay_install(mixing_valve_mode="none", heat_pump_max_power=pump)); model = ThermalModel(params)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=o, upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
    w = WeatherSeries(outdoor_temps=np.array([o]), wind_speeds=np.full(1,3.0), precipitation=np.zeros(1), solar_radiation=np.array([s]))
    h = _thermostat_held_state(model, st, w, 21.0)
    out.append(f"{o:+.0f}/{s:.0f}/{pump}:{h.room_temperature.hex()}/{h.upper_floor_temperature.hex()}")
print("\n".join(out))
