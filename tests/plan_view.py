import os, sys, json
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from profiles import prices, weather, house, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

START = datetime(2026,1,15,0,0)
cfg = house(two_zone=False, dhw=True)
p = ThermalParameters.from_config(cfg); p.dhw_enabled = True
oc = OptimizationConfig(horizon_hours=24, time_step_minutes=15,
    target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
    max_temp=cfg["max_temperature"])
opt = HeatPumpOptimizer(ThermalModel(p), oc)
pr = prices("winter_typical", START)
ot, wind, rain, sol = weather("winter_cold", START)
st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
    outdoor_temperature=float(ot[0]), dhw_temperature=50.0,
    dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
r = opt.optimize(st, pr, ot, wind, rain, sol, START)

class Fake:
    _opt_config = oc
    _build_plan_views = Coord._build_plan_views
    _plan_slots = staticmethod(Coord._plan_slots)
views = Fake()._build_plan_views(r)

for key in ("space_plan","dhw_plan"):
    v = views[key]
    print("==", key, "points", len(v["forecast"]), "slots", len(v["slots"]),
          "kWh", v["total_energy_kwh"], "cost", v["total_cost"], "active", v["active_now"])
    print("  first fc:", json.dumps(v["forecast"][0]))
    if v["slots"]:
        print("  first slot:", json.dumps(v["slots"][0]))
        print("  last slot :", json.dumps(v["slots"][-1]))

# ---- reason codes and price provenance (items 16, 7) ---------------------
#
# The plan sensors used to publish which slots were chosen but never why, which
# made an unexpected slot indistinguishable from a bug. Check the codes survive
# the whole path from the optimizer to the sensor payload the card reads.
issues = []
for key, power_key in (("space_plan", "space_power"), ("dhw_plan", "dhw_power")):
    forecast = views[key]["forecast"]
    heating = [p for p in forecast if (p.get(power_key) or 0.0) > 0.05]
    if heating and any(p.get("reason") in (None, "idle") for p in heating):
        issues.append(f"{key}: heating steps with no reason code")
    if any("price_known" not in p for p in forecast):
        issues.append(f"{key}: forecast points missing price provenance")
    slots = views[key]["slots"]
    if slots and any("reason" not in s for s in slots):
        issues.append(f"{key}: slots missing a dominant reason")

reasons = sorted({p.get("reason") for p in views["space_plan"]["forecast"]} - {None})
print("space reasons:", reasons)
print("dhw reasons  :", sorted({p.get("reason") for p in views["dhw_plan"]["forecast"]} - {None}))
if not any(r in reasons for r in ("cheap_price", "comfort_floor", "preheat_weather")):
    issues.append("space plan produced no recognisable reason codes")
if issues:
    print("PLAN VIEW ISSUES:")
    for i in issues:
        print("  -", i)
else:
    print("plan reason codes and price provenance OK")

# cross-check totals against the raw schedule
sp = np.asarray(r.power_schedule).sum()*DT
dw = np.asarray(r.dhw_power_schedule).sum()*DT
print("raw space kWh", round(sp,2), "raw dhw kWh", round(dw,2))
slot_e = sum(s["energy_kwh"] for s in views["space_plan"]["slots"])
print("slot-sum space kWh", round(slot_e,2))
slot_d = sum(s["energy_kwh"] for s in views["dhw_plan"]["slots"])
print("slot-sum dhw kWh", round(slot_d,2))

with open("/tmp/plandata.json","w") as f:
    json.dump(views, f)
print("wrote /tmp/plandata.json")

sys.exit(1 if issues else 0)
