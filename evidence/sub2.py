import sys, numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_setpoint_boost as sb
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
import heatpump_optimizer.thermal_model as tm
p = ThermalParameters(); p.mixing_valve_mode="manual"; p.buffer_tank_volume=0.0; p.two_zone_enabled=True
p.min_electrical_power, p.max_electrical_power = sb.CFG_MIN, sb.CFG_MAX
p.dhw_enabled=False; p.house_heat_loss_scale=1.0
m = ThermalModel(p)
print("mass", repr(p.buffer_tank_thermal_mass), "file", tm.__file__)
for w in (0.0, 3.0, 8.0):
    for dt in (0.25, 1/12):
        print(w, dt, m._substeps_and_loss(w, 0.0, dt))
