import sys, runpy
sys.argv=[sys.argv[0]]
g = runpy.run_path("dev/audit/harnesses/r10_ratio_anchor.py", run_name="lib")
import asyncio
coord, MemStore, house = g["coordinator"], g["MemStore"], g["house"]
from heatpump_optimizer.coordinator import house_loss_confidence
from heatpump_optimizer.thermal_model import reanchor_heat_loss
cfg = dict(house(two_zone=True, dhw=False), lower_floor_temp_entity="sensor.lower_floor")
U, L = cfg["upper_floor_heat_loss"], cfg["lower_floor_heat_loss"]
def run(s, r, ns, nr, fu, fl):
    src = coord(cfg, MemStore({})); src._apply_house_heat_loss_scale(s); src._apply_lower_floor_loss_ratio(r)
    src._house_heat_loss_samples, src._lower_floor_loss_samples = ns, nr
    asyncio.run(src._async_save_thermal_learning()); st = src._thermal_learning_store.data
    c1 = dict(cfg, upper_floor_heat_loss=U*fu, lower_floor_heat_loss=L*fl)
    c = coord(c1, MemStore(st)); asyncio.run(c._async_load_thermal_learning())
    a, b = house_loss_confidence(ns), house_loss_confidence(nr)
    then, now = (U, L), (U*fu, L*fl)
    joint = reanchor_heat_loss(then, now, s, r, (a, b), ratio_bounds=(0.3, 3.0))
    # the consistent landing: scale evidence void (a=0), solved again
    cons = reanchor_heat_loss(then, now, s, r, (0.0, b), ratio_bounds=(0.3, 3.0))
    p = c._thermal_params
    lower_head = p.lower_floor_heat_loss * c._lower_floor_loss_ratio * c._house_heat_loss_scale
    lower_cons = L*fl * (cons[1] if not cons[2] else 1.0) * cons[0]
    print(f"RESULT s={s} r={r} n={ns}/{nr} edit=({fu},{fl}): joint solve scale {joint[0]:.3f} (out of bounds) ratio {joint[1]:.4f}; "
          f"head applies scale {c._house_heat_loss_scale:.3f} ratio {c._lower_floor_loss_ratio:.4f} samples {c._house_heat_loss_samples}/{c._lower_floor_loss_samples} "
          f"-> lower {lower_head*1000:.1f} W/K; re-solved at zero scale confidence: scale {cons[0]:.3f} ratio {cons[1]:.4f} reset={cons[2]} -> lower {lower_cons*1000:.1f} W/K; "
          f"measured lower {L*r*s*1000:.1f} W/K, base (ratio verbatim) lower {L*fl*r*1000:.1f} W/K")
run(2.0, 2.5, 310, 147, 0.6, 0.5)
run(2.6, 1.3, 310, 147, 0.7, 0.9)
run(2.6, 1.3, 310, 147, 0.8, 0.6)
run(0.5, 0.8, 310, 147, 1.8, 1.4)
run(0.4, 1.6, 310, 147, 1.5, 1.5*0.8)
