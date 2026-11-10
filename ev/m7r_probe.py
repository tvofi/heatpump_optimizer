# Reviewer's probe: legionella_cycle_active with the combi switch on but the store inactive
import dataclasses, sys
sys.path[:0]=["tests/hastub","custom_components"]
from heatpump_optimizer.thermal_model import ThermalParameters
p=ThermalParameters()
p=dataclasses.replace(p, dhw_enabled=True, dhw_legionella_enabled=True, dhw_combi_tank_enabled=True, combi_potable_volume_l=0.0)
print("combi_tank_active", p.combi_tank_active, "buffer_is_store", p.buffer_is_store)
print("legionella_cycle_active (head)", p.legionella_cycle_active)
print("under M7r it would be", p.dhw_legionella_enabled and (not p.dhw_combi_tank_enabled or p.combi_potable_volume_l > 3.0 or p.dhw_combi_legionella_force))
