# Reviewer's own probe (not the finder's, not the fixer's): envelope_score vs
# the RATIO-SITES formula tau = mass / ((U + L*r) * s), graded 20-100 h.
import sys; sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
from dataclasses import replace, fields
import numpy as np
from heatpump_optimizer import coordinator as c
from heatpump_optimizer.thermal_model import ThermalParameters
names={f.name for f in fields(ThermalParameters)}
base=ThermalParameters()
worst=0.0
for two in (False, True):
  for r in (0.5,0.8,1.0,1.25,2.0):
    for s in (0.3,1.0,2.6,3.0):
      kw=dict(two_zone_enabled=two, house_heat_loss_scale=s)
      kw["lower_floor_loss_ratio"]=r
      p=replace(base,**kw)
      g,why=c.envelope_score(p,2000,{})
      u=(p.upper_floor_heat_loss+p.lower_floor_heat_loss*r) if two else p.heat_loss_coefficient
      tau=p.room_thermal_mass/round(u*s,4)
      want=float(np.clip((tau-20)/80,0,1))*100
      gap=abs((g if g is not None else -999)-want)
      worst=max(worst,gap)
      print(f"two={int(two)} r={r} s={s}: envelope={g} why={why} formula={want:.4f} gap={gap:.2e}")
print(f"RESULT probe_max_gap={worst:.2e}")
print("RESULT samples49", c.envelope_score(replace(base,house_heat_loss_scale=1.0),49,{}), "samples50", c.envelope_score(replace(base,house_heat_loss_scale=1.0),50,{}))
print("RESULT refit_edge", [c._refit_disagrees({"refit":{"scale":x,"band_percent":25}},2.0) for x in (2.5,2.51,1.5,1.49)])
