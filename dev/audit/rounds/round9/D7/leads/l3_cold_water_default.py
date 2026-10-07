"""l3_cold_water_default: how many production sites resolve the DHW cold-water default without
reading const.DEFAULT_DHW_INLET_TEMP?

Metric (one line): of 5 production sites that resolve a cold-water inlet default, those whose
resolved value does NOT move when const.DEFAULT_DHW_INLET_TEMP is moved 10.0 -> 12.5 in memory;
key = the value each site delivers (a field/argument value), not its source text.
Sites: ThermalParameters.from_config({}), the options-flow field default (config_flow._OPTION_FIELDS),
bare ThermalParameters() (thermal_model.py:469 literal 10.0), sysid._sizing_model()'s plant,
dhw_coil_draw_reduction's inlet_temp default (const.DHW_COLD_WATER_TEMP).
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_cold_water_default.py [--perturb literal] [--no-move]
Expected: sites_not_following=3 of 5 (exact); null control `--no-move` (const unmoved): sites_disagreeing=0 of 5;
          --perturb literal (one-line edit, in memory: thermal_model.py:469 `= 10.0` ->
          `= const.DEFAULT_DHW_INLET_TEMP`) -> sites_not_following=1 of 5 (the coil default).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, venv314.
Instrumented symbols: heatpump_optimizer.thermal_model:ThermalParameters.dhw_inlet_temp,
heatpump_optimizer.thermal_model:dhw_coil_draw_reduction, heatpump_optimizer.const:DEFAULT_DHW_INLET_TEMP.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib, inspect, sys, time, types
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
t0p, t0t = time.process_time(), time.thread_time()
MOVE = "--no-move" not in sys.argv
PERTURB = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "literal"
NEW = 12.5

import heatpump_optimizer  # noqa: E402  (package; submodules imported after the const move)
from heatpump_optimizer import const  # noqa: E402
if MOVE:
    const.DEFAULT_DHW_INLET_TEMP = NEW
if PERTURB:
    path = os.path.join("custom_components", "heatpump_optimizer", "thermal_model.py")
    src = open(path).read()
    old = "    dhw_inlet_temp: float = 10.0  # °C"
    assert src.count(old) == 1
    mod = types.ModuleType("heatpump_optimizer.thermal_model")
    mod.__file__, mod.__package__ = path, "heatpump_optimizer"
    sys.modules[mod.__name__] = mod
    exec(compile(src.replace(old, "    dhw_inlet_temp: float = const.DEFAULT_DHW_INLET_TEMP"), path, "exec"), mod.__dict__)
tm = importlib.import_module("heatpump_optimizer.thermal_model")
cf = importlib.import_module("heatpump_optimizer.config_flow")
sysid = importlib.import_module("heatpump_optimizer.sysid")

want = const.DEFAULT_DHW_INLET_TEMP
field = [f for f in cf._OPTION_FIELDS if f.key == const.CONF_DHW_INLET_TEMP] if hasattr(cf._OPTION_FIELDS[0], "key") else \
        [f for f in cf._OPTION_FIELDS if const.CONF_DHW_INLET_TEMP in f]
fdef = [x for x in field[0] if isinstance(x, (int, float)) and not isinstance(x, bool)][0]
sites = {
    "ThermalParameters.from_config({})": tm.ThermalParameters.from_config({}).dhw_inlet_temp,
    "config_flow option field default": fdef,
    "ThermalParameters() bare": tm.ThermalParameters().dhw_inlet_temp,
    "sysid._sizing_model plant": sysid._sizing_model(0.2, 10.0, 0.3).params.dhw_inlet_temp,
    "dhw_coil_draw_reduction inlet_temp default": inspect.signature(tm.dhw_coil_draw_reduction).parameters["inlet_temp"].default,
}
off = 0
for k, v in sites.items():
    bad = abs(float(v) - want) > 1e-9
    off += bad
    print(f"site {k:44s} value={v} follows_default={not bad}")
name = "sites_not_following" if MOVE else "sites_disagreeing"
print(f"RESULT {name}={off} of {len(sites)} count")
print(f"RESULT default_moved_to={want}")
print(f"RESULT perturbed={int(PERTURB)}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:  # noqa: BLE001
    sw = -1
print(f"RESULT swapins={sw}")
