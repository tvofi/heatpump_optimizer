#!/usr/bin/env python3
"""D7 verify-v3 (D7-s3-01): over one whole suite driver, which callers invoke
the ten members D7-s3-01 names dead -- production frames or test frames?

Metric (one line): for each named member, PY_START count split by the
immediate caller frame's file: under custom_components/ (production) versus
anything else (tests/harness); headline dead_called_from_production = members
with >=1 production-caller start, over the whole driver run.
Count key: the caller frame's co_filename (sys.monitoring PY_START on the
member's own code object), so a production reader moves it and a test read never does.
Live controls (must show production calls > 0): DefrostDerate.factor,
InputHealth.stale_keys, IrradianceSeries.end, HeatPumpOptimizerCoordinator.mode.
Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/verify-v3/member_trace.py tests/entities.py
Perturbation: --perturb patches sensor.NextOptimizationSensor.native_value to read
self.coordinator.next_optimization (compiled under sensor.py's filename; a harness FakeCoordinator
without the member falls back to the data key):
next_optimization production calls must rise 0 -> >=1.
Machine: cloud container linux x86_64 (4 cores, shared). Counts are contention-immune.
"""
from __future__ import annotations
import os
for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")
import runpy, sys, tempfile, time  # noqa: E401,E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
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
    ("defrost", "DefrostDerate", "factor"),
    ("inputs", "InputHealth", "stale_keys"),
    ("open_meteo", "IrradianceSeries", "end"),
    ("coordinator", "HeatPumpOptimizerCoordinator", "mode"),
]


def code_of(modname: str, cls: str, member: str):
    import importlib
    # Import through the same package name the drivers use.
    m = importlib.import_module(f"heatpump_optimizer.{modname}")
    obj = getattr(m, cls).__dict__[member]
    fn = obj.fget if isinstance(obj, property) else obj
    return fn.__code__


def main() -> int:
    perturb = "--perturb" in sys.argv
    driver = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    c0, t0 = time.process_time(), time.thread_time()
    os.environ.setdefault("HPO_PLANDATA", str(Path(tempfile.mkdtemp(prefix="d7v3_mt_")) / "plan.json"))
    codes = {}
    for spec in DEAD + LIVE:
        codes[code_of(*spec)] = ".".join(spec[1:])
    if perturb:
        import heatpump_optimizer.sensor as sensor_mod
        src = ("\n" * 0 + "def native_value(self):\n"
               "    c = self.coordinator\n"
               "    return _as_datetime(c.next_optimization if hasattr(c, 'next_optimization')\n"
               "                        else c.data.get('next_optimization'))\n")
        ns = dict(vars(sensor_mod))
        exec(compile(src, sensor_mod.__file__, "exec"), ns)
        sensor_mod.NextOptimizationSensor.native_value = property(ns["native_value"])
    prod = Counter()
    other = Counter()
    pkg = str((ROOT / "custom_components").resolve())
    mon = sys.monitoring
    TOOL = 3
    mon.use_tool_id(TOOL, "d7v3mt")

    def on_start(code, offset):
        name = codes.get(code)
        if name is None:
            return None
        caller = sys._getframe(1).f_back
        while caller is not None and caller.f_code.co_filename.endswith("/abc.py"):
            caller = caller.f_back
        fn = caller.f_code.co_filename if caller else "?"
        (prod if fn.startswith(pkg) else other)[name] += 1
        return None

    mon.register_callback(TOOL, mon.events.PY_START, on_start)
    for code in codes:
        mon.set_local_events(TOOL, code, mon.events.PY_START)
    sys.argv = [driver]
    rc = 0
    try:
        runpy.run_path(driver, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except Exception as e:  # noqa: BLE001 -- a driver crash is reported, not hidden
        rc = f"crash:{type(e).__name__}"
    finally:
        for code in codes:
            mon.set_local_events(TOOL, code, 0)
        mon.free_tool_id(TOOL)
    sys.stdout.flush()
    print(f"\nRESULT driver_rc={rc}")
    dead_prod = 0
    for spec in DEAD:
        n = ".".join(spec[1:])
        print(f"RESULT dead_{n}_production={prod[n]} other={other[n]} count")
        dead_prod += int(prod[n] > 0)
    live_ok = 0
    for spec in LIVE:
        n = ".".join(spec[1:])
        print(f"RESULT live_{n}_production={prod[n]} other={other[n]} count")
        live_ok += int(prod[n] > 0)
    print(f"RESULT dead_called_from_production={dead_prod} count  # of {len(DEAD)}")
    print(f"RESULT dead_called_from_tests={sum(1 for s in DEAD if other['.'.join(s[1:])] > 0)} count")
    print(f"RESULT live_controls_production={live_ok} count  # of {len(LIVE)}")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "n/a")
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
