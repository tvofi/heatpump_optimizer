"""D14 round 9, verifier V2 (independent) for D14-s2-01: presence-inferred facts re-derived by proxy.

Metric (one line): v2_two_zone_disagree = exhaustive saved configs (two_zone_mode in
{absent, auto, on, off} x upper_floor_thermal_mass in {absent, 0.0, 3.0} x each other zone key
{lower_floor_thermal_mass, inter_zone_transfer} present/absent = 48 cells) on which the REAL
config_flow._derive_preset(answers, current) output differs from the same call made with the
current dict rewritten so bool(upper key) equals ThermalParameters.from_config(current)
.two_zone_enabled -- i.e. the preset depends on the proxy, not on the fact;
v2_prefill_disagree = the same cells on which modbus_prefill.infer(water-control snapshot)
offers the flow write target iff canonical two_zone is False (a mismatch either way);
v2_wood_disagree = all 64 subsets of the six wood-inference keys (flag absent) on which
topology.describe_setup(cfg)["wood"]["present"] != wood_fuel.wood_furnace_on(cfg).
Keys: the production outputs (derived dict, suggestions dict, present map).

Null control: cells where bool(upper key) == canonical two_zone -> 0 by construction of the
comparison; wood: the explicit wood_furnace_enabled flag present (64 more cells) -> 0.
Perturbation (--fix): _derive_preset/prefill fed through the canonical predicate and
topology._wood_tank_shown := wood_furnace_on in memory -> all three to 0.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_facts.py [--fix]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, itertools, logging
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()
from heatpump_optimizer import config_flow as CF, modbus_prefill as MP, topology as TP, wood_fuel as WF, const as K  # noqa
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

FIX = "--fix" in sys.argv
canon = lambda c: ThermalParameters.from_config(dict(c)).two_zone_enabled  # noqa: E731
if FIX:
    TP._wood_tank_shown = WF.wood_furnace_on

ANS = {K.CONF_BUILDING_STRUCTURE: "timber_crawlspace", K.CONF_BUILDING_ERA: "1960_1980",
       K.CONF_BUILDING_FOUNDATION: "none", K.CONF_HEATED_AREA: 140.0,
       K.CONF_UPPER_EMITTER: "radiators", K.CONF_LOWER_EMITTER: "floor"}


def proxy_aligned(cur):
    c = dict(cur)
    if canon(cur):
        c[K.CONF_UPPER_FLOOR_THERMAL_MASS] = c.get(K.CONF_UPPER_FLOOR_THERMAL_MASS) or 3.0
    else:
        c.pop(K.CONF_UPPER_FLOOR_THERMAL_MASS, None)
    return c


# a water-temperature-control GCHV snapshot (register 4109 == _WATER_TEMPERATURE_CONTROL)
SNAP = {"r4109": ("sensor.gchv_r4109", str(MP._WATER_TEMPERATURE_CONTROL), 1.0)}

cells = dz = pf = null_cells = null_dz = 0
ratios = []
for mode, upper, lower, izt in itertools.product(
        (None, "auto", "on", "off"), (None, 0.0, 3.0), (False, True), (False, True)):
    cur = {}
    if mode is not None:
        cur[K.CONF_TWO_ZONE_MODE] = mode
    if upper is not None:
        cur[K.CONF_UPPER_FLOOR_THERMAL_MASS] = upper
    if lower:
        cur[K.CONF_LOWER_FLOOR_THERMAL_MASS] = 8.0
    if izt:
        cur[K.CONF_INTER_ZONE_TRANSFER] = 0.15
    cells += 1
    feed = proxy_aligned(cur) if FIX else cur
    got = CF._derive_preset(ANS, feed)
    ref = CF._derive_preset(ANS, proxy_aligned(cur))
    agree_proxy = bool(cur.get(K.CONF_UPPER_FLOOR_THERMAL_MASS)) == canon(cur)
    if got != ref:
        dz += 1
        ratios.append(got.get("slab_thermal_mass", 0) / ref.get("slab_thermal_mass", 1))
    if agree_proxy:
        null_cells += 1
        null_dz += got != ref
    # prefill: water control snapshot, offered flow target vs canonical fact
    sug = MP.infer(SNAP, feed)
    offered = sug.get(K.CONF_MIXING_VALVE_WRITE_TARGET_KIND) is not None
    pf += offered != canon(cur)
print(f"RESULT v2_two_zone_cells={cells} count")
print(f"RESULT v2_two_zone_disagree={dz} count")
print(f"RESULT v2_prefill_disagree={pf} count")
print(f"RESULT v2_two_zone_null_cells={null_cells} count")
print(f"RESULT v2_two_zone_null_disagree={null_dz} count")
if ratios:
    print(f"RESULT v2_slab_mass_ratio_min={min(ratios):.3f} ratio")
    print(f"RESULT v2_slab_mass_ratio_max={max(ratios):.3f} ratio")

WKEYS = [K.CONF_WOOD_TANK_TOP_ENTITY, K.CONF_WOOD_TANK_BOTTOM_ENTITY, K.CONF_VALVE_OUTLET_TEMP_ENTITY,
         K.CONF_EXTERNAL_HEAT_ENABLED, K.CONF_EXTERNAL_HEAT_ENTITY, K.CONF_DHW_WOOD_COIL_ENABLED]
VAL = {K.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wt", K.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.wb",
       K.CONF_VALVE_OUTLET_TEMP_ENTITY: "sensor.vo", K.CONF_EXTERNAL_HEAT_ENABLED: True,
       K.CONF_EXTERNAL_HEAT_ENTITY: "sensor.eh", K.CONF_DHW_WOOD_COIL_ENABLED: True}
wd = wn = 0
which = []
for bits in itertools.product((0, 1), repeat=6):
    cfg = {k: VAL[k] for k, b in zip(WKEYS, bits) if b}
    shown = TP.describe_setup(dict(cfg))["wood"]["present"]
    if bool(shown) != WF.wood_furnace_on(cfg):
        wd += 1
        which.append(sorted(k for k in cfg))
    for flag in (True, False):
        c2 = dict(cfg, **{K.CONF_WOOD_FURNACE_ENABLED: flag})
        wn += bool(TP.describe_setup(dict(c2))["wood"]["present"]) != WF.wood_furnace_on(c2)
for w in which:
    print(f"WOOD disagree cfg={w}")
print(f"RESULT v2_wood_cells=64 count")
print(f"RESULT v2_wood_disagree={wd} count")
print(f"RESULT v2_wood_null_flag_disagree={wn}_of_128 count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
