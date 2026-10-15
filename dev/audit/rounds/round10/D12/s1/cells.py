"""D12-s1 M1+M6: plant inventory and per-cell coordinator cycle fail-count.

Metric: cells = derived option-page optional-entity slots and boolean
feature toggles (seeded fixed point, as tests/golden.py:capture_config_flow);
fail = BaseException raised by tests/golden.py:capture_coordinator (real
HeatPumpOptimizerCoordinator._forecast_arrays/_build_data_dict + sensor
async_setup_entry + no-NaN invariant) for one cell config.
Key: exception raised by the production seam, not a config attribute.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D12/s1/cells.py [--shrink dhw|pv|zone|none] [--perturb-reading-ok]
Second metric: fabricated_reading_cells = cells where any sensor with a
_reading_key is available with a value although FakeHass holds no state
(sensor:_reading_ok gate). Perturbation --perturb-reading-ok must raise it.
Baseline 17f1c55fad1b, macOS arm64 (B4). Expected: see REPORT.md, exact counts.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, asyncio, time, traceback, tempfile
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp())
import golden
from harness import FakeEntry, FakeHass
from heatpump_optimizer.config_flow import HeatPumpOptimizerOptionsFlow as Flow

PERTURB = "--perturb-reading-ok" in sys.argv
if PERTURB:
    from heatpump_optimizer import sensor as _S
    _S._reading_ok = lambda *a, **k: True  # perturbation: thermometer-gate removed
shrink = sys.argv[sys.argv.index("--shrink")+1] if "--shrink" in sys.argv else "none"
BASE = {"tibber_token": "x", "weather_entity": "weather.home"}

# M1: derived inventory
seed, entity_fields, bool_fields, pages = {}, [], [], set()
for _ in range(golden._SEED_ROUNDS):
    f = Flow(FakeEntry(data=dict(BASE), options=dict(seed))); f.hass = FakeHass()
    grown = {}
    for step in Flow._MENU_LABELS:
        sch = asyncio.run(getattr(f, f"async_step_{step}")()).get("data_schema")
        for key, val in golden._presented_fields(sch):
            pages.add(step); n = str(key)
            if n in seed or n in grown: continue
            if type(val).__name__ == "EntitySelector":
                grown[n] = f"sensor.seed_{n}"; entity_fields.append(n)
            elif val is bool or type(val).__name__ == "BooleanSelector":
                grown[n] = True; bool_fields.append(n)
    if not grown: break
    seed.update(grown)
scen = golden.coordinator_scenarios()
plan_toggles = sorted({k for s in golden.SCENARIOS.values() for k in (s if isinstance(s, dict) else {})})
print(f"RESULT option_pages={len(Flow._MENU_LABELS)} pages")
print(f"RESULT optional_entity_slots={len(entity_fields)} slots")
print(f"RESULT bool_toggles={len(bool_fields)} toggles")
print(f"RESULT coordinator_scenarios={len(scen)} configs")
print(f"RESULT golden_plan_scenarios={len(golden.SCENARIOS)} scenarios")

ref = dict(scen["coord_all_features"])
SHRINK = {"dhw": ["dhw_tank_volume"], "pv": ["pv_enabled","pv_peak_kw","pv_export_price"], "zone": [], "none": []}
for k in SHRINK[shrink]: ref.pop(k, None)
if shrink == "zone":
    for k in list(ref):
        if k.startswith("upper_floor") or k.startswith("lower_floor"): ref.pop(k)
else:
    ref.update(scen["coord_two_zone"])  # richest plant: two zones on top of all features

cells = [("reference", dict(ref))]
for n in entity_fields:
    cells.append((f"map:{n}", {**ref, n: f"sensor.seed_{n}"}))
for n in bool_fields:
    cells.append((f"on:{n}", {**ref, n: True}))
    cells.append((f"off:{n}", {**ref, n: False}))
cells.append(("all_seeded", {**ref, **seed}))

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer import sensor as sensor_mod
def fabricated(cfg):
    # FakeHass has NO states: every reading sensor (``_reading_key``) that is
    # available and non-None publishes a thermometer value nobody measured.
    h = FakeHass(); e = FakeEntry(data=cfg); c = HeatPumpOptimizerCoordinator(h, e)
    c.data = c._build_data_dict(); e.runtime_data = c
    out = []; asyncio.run(sensor_mod.async_setup_entry(h, e, out.extend))
    return [getattr(x, "_key", "") for x in out
            if getattr(x, "_reading_key", "") and x.available and x.native_value is not None]
fabs = 0
fails = []
for name, cfg in cells:
    try:
        golden.dt_util.freeze(golden.START) if hasattr(golden, "dt_util") else None
        fb = fabricated(cfg)
        if fb:
            fabs += 1; print("FABRICATED", name, fb[:6])
        golden.capture_coordinator(cfg)
    except BaseException as e:
        tb = traceback.extract_tb(e.__traceback__)
        where = next((f"{os.path.basename(fr.filename)}:{fr.name}:{fr.lineno}" for fr in reversed(tb) if "heatpump_optimizer" in fr.filename), "harness")
        fails.append((name, type(e).__name__, str(e)[:120], where))
for f in fails: print("FAIL", *f)
print(f"RESULT shrink={shrink}")
print(f"RESULT cells={len(cells)} cells")
print(f"RESULT fail_cells={len(fails)} cells")
print(f"RESULT fabricated_reading_cells={fabs} cells")
print(f"RESULT perturb_reading_ok={PERTURB}")
c0 = time.process_time(); t0 = time.thread_time()
print(f"RESULT thread_factor={(time.process_time()/max(time.thread_time(),1e-9)):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
