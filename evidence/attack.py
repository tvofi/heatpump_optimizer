import sys, runpy, math
sys.argv=[sys.argv[0]]
g = runpy.run_path("dev/audit/harnesses/r10_ratio_anchor.py", run_name="lib")
import asyncio, copy
coord, MemStore, house = g["coordinator"], g["MemStore"], g["house"]
from heatpump_optimizer.coordinator import house_loss_confidence
cfg = dict(house(two_zone=True, dhw=False), lower_floor_temp_entity="sensor.lower_floor")
U, L = cfg["upper_floor_heat_loss"], cfg["lower_floor_heat_loss"]
def learned(c0, s, r, ns, nr):
    src = coord(c0, MemStore({})); src._apply_house_heat_loss_scale(s); src._apply_lower_floor_loss_ratio(r)
    src._house_heat_loss_samples, src._lower_floor_loss_samples = ns, nr
    asyncio.run(src._async_save_thermal_learning()); return src._thermal_learning_store.data
def load(c1, st):
    c = coord(c1, MemStore(st)); asyncio.run(c._async_load_thermal_learning()); return c
def zones(c):
    p=c._thermal_params; s=c._house_heat_loss_scale; return p.upper_floor_heat_loss*s, p.lower_floor_heat_loss*c._lower_floor_loss_ratio*s
worst=0
for s,r in ((1.567,1.922),(0.7,0.6),(1.2,0.8),(2.0,2.5)):
  for ns,nr in ((310,147),(20,10),(5,200),(200,3)):
    for fu,fl in ((s, r*s),(1.0,2.0),(1.5,1.0),(0.6,0.5),(1.0,0.7)):
      st = learned(cfg,s,r,ns,nr)
      c1 = dict(cfg, upper_floor_heat_loss=U*fu, lower_floor_heat_loss=L*fl)
      c = load(c1, st)
      a, b = house_loss_confidence(ns), house_loss_confidence(nr)
      mu, ml = U*s, L*r*s
      gu, gl = zones(c)
      s2 = c._house_heat_loss_scale; r2 = c._lower_floor_loss_ratio
      reset = c._lower_floor_loss_samples == 0 and nr
      bb = 0.0 if reset else b
      # law: lower and total
      el = (1-bb)*L*fl*s2 + bb*ml
      et = (1-a)*(U*fu + L*fl*r2) + a*(mu+ml)
      err = max(abs(gl-el)/ml, abs(gu+gl-et)/(mu+ml))
      split_moved = abs((fl/fu) - 1) > 0.05
      tag = "" if split_moved else " (split kept: total-only law)"
      if split_moved: worst=max(worst,err)
      print(f"s={s} r={r} n={ns}/{nr} edit=({fu},{fl}) -> scale {s2:.4f} ratio {r2:.4f} zones {gu*1000:.1f}/{gl*1000:.1f} vs learned {mu*1000:.1f}/{ml*1000:.1f} law_err={err:.2e}{' RESET' if reset else ''}{tag}")
print("RESULT max law residual over split-moving edits:", f"{worst:.2e}")
# path independence: A->B->C vs A->C at partial confidence
st = learned(cfg,1.567,1.922,40,20)
B = dict(cfg, upper_floor_heat_loss=U*1.3, lower_floor_heat_loss=L*1.6)
C = dict(cfg, upper_floor_heat_loss=U*1.567, lower_floor_heat_loss=L*1.922*1.567)
cB = load(B, st); cBC = load(C, copy.deepcopy(cB._thermal_learning_store.data)); cAC = load(C, st)
print("RESULT path A->B->C zones", [round(x*1000,3) for x in zones(cBC)], "A->C", [round(x*1000,3) for x in zones(cAC)])
