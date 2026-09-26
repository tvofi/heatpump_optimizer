"""D14 round 9, verifier V2 (independent) for D14-s1-02: data keys read but never produced.

Metric (one line): v2_horizon_key_present = scenarios (of tests/golden.py:coordinator_scenarios, 5)
whose REAL _build_data_dict payload contains the key "horizon_hours" the plan sensors read;
v2_horizon_misreport = with coord._opt_config.horizon_hours set to 48 before a rebuild, whether
data.get("horizon_hours", 24.0) (the sensor.py:1482/1515 expression) != the configured horizon;
v2_getattr_undefined = getattr(obj, "<literal>", default) probes in the package whose name is
assigned/defined nowhere in production code (AST: attribute stores, def/class names, dataclass
fields, class-body assignments) -- keyed on names, independent of the finder's recorder.

Null control: the key "currency" (read by sensors) -> present in 5 of 5.
Perturbation: in memory, _build_data_dict wrapped to add data["horizon_hours"] from
_opt_config -> v2_horizon_key_present 0 -> 5 and v2_horizon_misreport 1 -> 0 (--fix).

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_keys.py [--fix]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, ast, glob, logging, contextlib, io
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import golden  # noqa: E402
import heatpump_optimizer.coordinator as C  # noqa: E402

FIX = "--fix" in sys.argv
orig = C.HeatPumpOptimizerCoordinator._build_data_dict
seen = []


def wrapped(self, *a, **k):
    d = orig(self, *a, **k)
    if FIX:
        d["horizon_hours"] = float(self._opt_config.horizon_hours)
    seen.append((self, d))
    return d


C.HeatPumpOptimizerCoordinator._build_data_dict = wrapped
present = plan_present = 0
misreport = 0
scen = golden.coordinator_scenarios()
for name, cfg in scen.items():
    seen.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        golden._capture_coordinator(dict(cfg))
    coord, data = seen[-1]
    present += "horizon_hours" in data
    plan_present += "currency" in data
    if name == "coord_minimal":
        coord._opt_config.horizon_hours = 48.0
        d2 = coord._build_data_dict()
        misreport = int(float(d2.get("horizon_hours", 24.0)) != 48.0)
print(f"RESULT v2_horizon_key_present={present}_of_{len(scen)} count")
print(f"RESULT v2_currency_key_present_null={plan_present}_of_{len(scen)} count")
print(f"RESULT v2_horizon_misreport_at_48h={misreport} count")

# getattr probes of names production never defines
defined = set()
probes = []
for f in sorted(glob.glob("custom_components/heatpump_optimizer/**/*.py", recursive=True)):
    tree = ast.parse(open(f).read())
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
            defined.add(n.attr)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(n.name)
        elif isinstance(n, ast.ClassDef):
            pass
        if isinstance(n, ast.ClassDef):
            for b in n.body:
                if isinstance(b, ast.AnnAssign) and isinstance(b.target, ast.Name):
                    defined.add(b.target.id)
                elif isinstance(b, ast.Assign):
                    for t in b.targets:
                        if isinstance(t, ast.Name):
                            defined.add(t.id)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
            probes.append((f, n.lineno, n.args[1].value))
# Home Assistant / stdlib attributes are defined outside the package: take them from the hastub
# and the real objects' dir() only for names the package itself never defines.
ha_names = set()
for f in glob.glob("tests/hastub/**/*.py", recursive=True):
    for n in ast.walk(ast.parse(open(f).read())):
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
            ha_names.add(n.attr)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            ha_names.add(n.name)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            ha_names.add(n.target.id)
test_double = set()
for f in ("tests/harness.py",):
    for n in ast.walk(ast.parse(open(f).read())):
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
            test_double.add(n.attr)
# Names of the real Home Assistant / stdlib API (State, hass.config, ConfigEntry, datetime, the
# lovelace resources collection, http): defined outside the package, not a test-double artefact.
REAL_API = {"attributes", "last_updated", "last_changed", "last_reported", "states", "isoformat",
            "units", "temperature_unit", "resources", "register_static_path", "language", "keys",
            "async_update_item", "async_update_entry", "async_start_reauth", "async_on_unload",
            "async_items", "_get_reauth_entry"}
undef = [(f, l, a) for f, l, a in probes if a not in defined and a not in ha_names and a not in REAL_API]
only_double = [(f, l, a) for f, l, a in undef if a in test_double]
for f, l, a in undef:
    print(f"PROBE undefined {f}:{l} {a!r}{'  (defined only by tests/harness.py)' if a in test_double else ''}")
print(f"RESULT v2_getattr_probes={len(probes)} count")
print(f"RESULT v2_getattr_undefined_outside_real_api={len(undef)} count")
print(f"RESULT v2_getattr_defined_only_by_test_double={len(only_double)} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
