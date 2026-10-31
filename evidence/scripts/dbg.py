import asyncio, sys, os
WT=os.path.abspath(sys.argv[1]); sys.argv=[sys.argv[0],WT]; sys.path[:0]=[os.path.dirname(__file__)]
import probe
from swap_energy import BASE, mk, written
import heatpump_optimizer.coordinator as co
orig_pair, orig_re = co.heat_loss_anchor_pair, co.reanchor_heat_loss
def pair(*a, **k):
    r = orig_pair(*a, **k); print("pair", a, k, "->", r); return r
def re(*a, **k):
    r = orig_re(*a, **k); print("reanchor", a, "->", r); return r
co.heat_loss_anchor_pair, co.reanchor_heat_loss = pair, re
EDIT = dict(lower_floor_heat_loss=0.3, upper_floor_heat_loss=0.2)
for sw in (dict(lower_floor_temp_entity="sensor.t6"), {}):
    st = written(); c = mk(dict(BASE, **EDIT, **sw), st); asyncio.run(c._async_load_thermal_learning())
    print("final", c._house_heat_loss_scale, c._lower_floor_loss_ratio, c._lower_floor_loss_samples)
