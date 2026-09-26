#!/usr/bin/env python3
"""D7 verify-v2 for D7-s3-01: who calls the ten members while a whole suite script runs.

Metric (one line): during one run of a suite driver (default tests/entities.py,
which drives every platform through async_setup_entry and reads the HA
surface), the number of entries into each of the ten claimed-dead members'
code objects whose immediate caller frame is under custom_components/
(production) versus anywhere else (tests); controls: six live siblings on the
same classes must show production callers > 0.

sys.monitoring PY_START restricted (set_local_events) to the members' own code
objects; properties are instrumented through their fget. Runs the driver with
runpy as __main__, catching its sys.exit. Counts; contention-immune.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v2/member_callers.py [tests/entities.py]
Prints RESULT dead_members_with_production_caller=<n of 10>,
RESULT dead_members_with_test_caller=<n of 10>, live_controls_with_production_caller=<n of 6>.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, cloud container linux.
"""
from __future__ import annotations
import os
for _p in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_p, "1")
import importlib, runpy, sys, time  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
PROD = str((ROOT / "custom_components").resolve())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

DEAD = [
    ("coordinator", "HeatPumpOptimizerCoordinator", "last_optimization"),
    ("coordinator", "HeatPumpOptimizerCoordinator", "next_optimization"),
    ("coordinator", "HeatPumpOptimizerCoordinator", "current_action"),
    ("coordinator", "HeatPumpOptimizerCoordinator", "floor_return_temp"),
    ("defrost", "DefrostDerate", "measured"),
    ("defrost", "DefrostDerate", "samples"),
    ("inputs", "InputHealth", "healthy"),
    ("open_meteo", "IrradianceSeries", "start"),
    ("open_meteo", "OpenMeteoSolar", "last_success"),
    ("optimizer", "_Horizon", "weather"),
]
LIVE = [
    ("coordinator", "HeatPumpOptimizerCoordinator", "mode"),
    ("coordinator", "HeatPumpOptimizerCoordinator", "optimization_running"),
    ("inputs", "InputHealth", "stale_keys"),
    ("open_meteo", "IrradianceSeries", "end"),
    ("defrost", "DefrostDerate", "factor"),
    ("optimizer", "_Horizon", "timestamps"),
]
M = sys.monitoring
TOOL = M.OPTIMIZER_ID
prod_calls: Counter = Counter()
test_calls: Counter = Counter()
CODES: dict = {}


def code_of(modname, cls, member):
    mod = None
    for pkg in ("heatpump_optimizer", "custom_components.heatpump_optimizer"):
        try:
            mod = importlib.import_module(f"{pkg}.{modname}")
            break
        except ImportError:
            continue
    obj = getattr(mod, cls).__dict__[member]
    fn = obj.fget if isinstance(obj, property) else obj
    return fn.__code__


def on_start(code, offset):
    key = CODES.get(code)
    if key is None:
        return None
    caller = sys._getframe(1).f_code.co_filename
    (prod_calls if os.path.realpath(caller).startswith(PROD) else test_calls)[key] += 1
    return None


def main() -> int:
    driver = sys.argv[1] if len(sys.argv) > 1 else "tests/entities.py"
    c0, t0 = time.process_time(), time.thread_time()
    M.use_tool_id(TOOL, "v2members")
    M.register_callback(TOOL, M.events.PY_START, on_start)
    # both import spellings may load the module twice; instrument each copy
    for spec in DEAD + LIVE:
        for pkg in ("heatpump_optimizer",):
            try:
                mod = importlib.import_module(f"{pkg}.{spec[0]}")
            except ImportError:
                continue
            obj = getattr(mod, spec[1]).__dict__[spec[2]]
            code = (obj.fget if isinstance(obj, property) else obj).__code__
            CODES[code] = spec
            M.set_local_events(TOOL, code, M.events.PY_START)
    sys.argv = [driver]
    rc = 0
    try:
        runpy.run_path(driver, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        M.register_callback(TOOL, M.events.PY_START, None)
        M.free_tool_id(TOOL)
    sys.stdout.flush()
    for spec in DEAD + LIVE:
        tag = "dead" if spec in DEAD else "live"
        print(f"MEMBER {tag} {spec[0]}.{spec[1]}.{spec[2]}: production={prod_calls[spec]} tests={test_calls[spec]}")
    print(f"RESULT driver={driver} exit={rc}")
    print(f"RESULT dead_members_with_production_caller={sum(1 for s in DEAD if prod_calls[s])} count (of 10)")
    print(f"RESULT dead_members_with_test_caller={sum(1 for s in DEAD if test_calls[s])} count (of 10)")
    print(f"RESULT live_controls_with_production_caller={sum(1 for s in LIVE if prod_calls[s])} count (of 6)")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
