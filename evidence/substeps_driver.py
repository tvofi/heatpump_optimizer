"""Reviewer's own driver: _substeps_and_loss on two-zone + single-zone valved installs."""
import sys
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
for two in (True, False):
    for mode in ("manual", "none"):
        for vol in (0.0, 1e-6, 1.0, 35.0, 200.0, 750.0):
            p = ThermalParameters()
            p.two_zone_enabled = two
            p.mixing_valve_mode = mode
            p.buffer_tank_volume = vol
            m = ThermalModel(p)
            for dt in (0.25, 1.0):
                out = m._substeps_and_loss(3.0, 0.0, dt)
                print(two, mode, vol, dt, repr(p.buffer_tank_thermal_mass), repr(out))
