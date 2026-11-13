import sys, os
TREE = sys.argv[1]; sys.path[:0] = [os.path.join(TREE, "tests"), os.path.join(TREE, "custom_components")]
from profiles import house
from heatpump_optimizer import setpoint_check as sc
from heatpump_optimizer.thermal_model import ThermalParameters
class S:
    def __init__(s, v, u): s.state, s.attributes = v, ({"unit_of_measurement": u} if u else {})
class H:
    def __init__(s, st): s.states = s; s._s = st
    def get(s, e): return s._s.get(e)
seen = []
sc.set_issue = lambda hass, key, active, **kw: seen.append((key, bool(active), kw.get("placeholders")))
cfg = house(); cfg["dhw_hysteresis_entity"] = "number.h"
for label, mod in (("house() as it stands", {}), ("hot water explicitly disabled", {"dhw_enabled": False})):
    c = dict(cfg); c.update(mod); p = ThermalParameters.from_config(c)
    for v in ("2", "4", "10", "20"):
        seen.clear(); sc._dhw_start(H({"number.h": S(v, "K")}), c, p)
        print("RESULT", label, "dhw_enabled", p.dhw_enabled, "setpoint", p.dhw_setpoint, "min", p.dhw_min_temp, "hysteresis", v, "->", seen[0][1], seen[0][2])
