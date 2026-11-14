"""Reviewer's probe: _compute_baseline_power across #3587 (931970141c^1 vs 931970141c).
Run with PYTHONPATH=<tree>/tests/hastub:<tree>/custom_components and REPLAY=<post tree>/tests/replay/<fixture>."""
import json, os, sys
import numpy as np
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
N, DT = 96, 0.25
entry = json.load(open(os.environ["REPLAY"]))["entry"]
def replay(**o): return {**entry["data"], **entry["options"], **o}
def house(two_zone=False, **o):
    cfg = {"target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
           "heat_pump_max_power": 6.0, "heat_pump_min_power": 1.0, "dhw_tank_volume": 300.0,
           "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0, "dhw_daily_consumption": 200.0,
           "dhw_windows": "06:00-08:30, 17:00-22:00", "buffer_tank_volume": 200.0, "window_area": 18.0}
    cfg.update(o); return cfg
def single_valve():
    p = ThermalParameters.from_config(house()); p.mixing_valve_mode = "manual"; return p
INSTALLS = {
  "twozone_valved(replay)": lambda: ThermalParameters.from_config(replay()),
  "unvalved(replay,none)": lambda: ThermalParameters.from_config(replay(mixing_valve_mode="none")),
  "single_zone_valve": single_valve,
  "plain_house": lambda: ThermalParameters.from_config(house()),
}
for name, mk in INSTALLS.items():
    for sun in (0.0, 300.0):
        for out in (5.0, 0.0, -5.0, -15.0):
            p = mk(); m = ThermalModel(p)
            opt = HeatPumpOptimizer(m, OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0))
            w = WeatherSeries(outdoor_temps=np.full(N, out), wind_speeds=np.full(N, 3.0),
                              precipitation=np.zeros(N), solar_radiation=np.full(N, sun))
            s = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=out,
                             upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                             buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
            pw, _ = opt._compute_baseline_power(w, s, DT, np.full(N, 21.0))
            print(f"{name} sun={sun:.0f} out={out:+.0f} first={pw[0]!r} sum={float(pw.sum())!r}")
