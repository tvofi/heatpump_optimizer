"""D7 round 8, seat s2 -- runtime sentinel for the dead code s2_reach.py reports.

Metric: for each candidate production function, the number of calls whose
CALLING frame is in a production file (custom_components/...) versus a test
file, over a run of the named test scripts (default: tests/config_flow_steps.py,
tests/features.py, tests/entities.py -- the three that drive the config flow,
the services, the coordinator and every entity through HA's real setup), with
a sys.setprofile/threading.setprofile hook keyed on the function's code object.
For each candidate module-level ``_LOGGER``, the number of attribute reads on
it (the module global is swapped for a counting proxy).
The count's key: calls are keyed on the production CODE OBJECT, so any caller
reaching the function by any binding (an import alias, a getattr, a
re-export) is counted; "production caller" means the caller frame's file is
under custom_components/.

Command (from the tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/s2_sentinel.py [--perturb] [--scripts a.py,b.py]
Expected at the baseline (exact): RESULT prod_calls[grid_fee.is_valid_spec]=0,
  test_calls[...] >= 1; prod_calls[presets.describe]=0, test_calls >= 1;
  logger_reads_total=0 over the ten unused _LOGGERs.
Perturbation (--perturb): rebinds config_flow.is_valid_spec to
  grid_fee.is_valid_spec before the run (the production one-line edit
  ``from .grid_fee import is_valid_spec`` in config_flow.py); prod_calls for
  grid_fee.is_valid_spec must go UP from 0.
Scope gap: code run in a subprocess (process_worker, features.py's HASTUB_TZ
  child) is not traced; s2_reach.py's static result covers it.
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU cloud Linux
  container (audit-r8), python 3.11.15. Counts are contention-immune (exact).
Root rule: ROOT = the working directory.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import importlib
import io
import contextlib
import runpy
import sys
import threading
import time
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

FUNCS = [("grid_fee", "is_valid_spec"), ("presets", "describe")]
LOGGER_MODS = ["battery", "binary_sensor", "dhw_draws", "power_guard", "presets",
               "pump_schedule", "pv", "sensor", "switch", "tariff"]
# null control: a live function and a live _LOGGER the same run must see called
CONTROLS = [("dhw_schedule", "is_valid_spec"), ("presets", "derive")]
CONTROL_LOGGER = "coordinator"


class CountingLogger:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "reads", 0)

    def __getattr__(self, name):
        object.__setattr__(self, "reads", self.reads + 1)
        return getattr(self._real, name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--scripts", default="tests/config_flow_steps.py,tests/features.py,tests/entities.py")
    args = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()

    targets = {}
    for mod, name in FUNCS + CONTROLS:
        m = importlib.import_module(f"heatpump_optimizer.{mod}")
        targets[getattr(m, name).__code__] = f"{mod}.{name}"
    prod_calls = {v: 0 for v in targets.values()}
    test_calls = {v: 0 for v in targets.values()}
    prod_root = str(ROOT / "custom_components")

    def prof(frame, event, arg):
        if event == "call":
            key = targets.get(frame.f_code)
            if key is not None:
                caller = frame.f_back.f_code.co_filename if frame.f_back else ""
                if caller.startswith(prod_root) or "/custom_components/" in caller:
                    prod_calls[key] += 1
                else:
                    test_calls[key] += 1

    loggers = {}
    for mod in LOGGER_MODS + [CONTROL_LOGGER]:
        m = importlib.import_module(f"heatpump_optimizer.{mod}")
        proxy = CountingLogger(m._LOGGER)
        m._LOGGER = proxy
        loggers[mod] = proxy

    real_binding = None
    if args.perturb:
        cf = importlib.import_module("heatpump_optimizer.config_flow")
        gf = importlib.import_module("heatpump_optimizer.grid_fee")
        real_binding = cf.is_valid_spec
        cf.is_valid_spec = gf.is_valid_spec
    try:
        sys.setprofile(prof)
        threading.setprofile(prof)
        for script in args.scripts.split(","):
            saved_argv = sys.argv[:]
            sys.argv = [script]
            buf = io.StringIO()
            rc = None
            try:
                with contextlib.redirect_stdout(buf):
                    runpy.run_path(script, run_name="__main__")
            except SystemExit as exc:
                rc = exc.code
            finally:
                sys.argv = saved_argv
            print(f"  ran {script}: exit={rc} ({len(buf.getvalue().splitlines())} output lines)")
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
        if real_binding is not None:
            cf.is_valid_spec = real_binding
        for mod, proxy in loggers.items():
            importlib.import_module(f"heatpump_optimizer.{mod}")._LOGGER = proxy._real

    for key in prod_calls:
        role = "control" if key in {f"{a}.{b}" for a, b in CONTROLS} else "candidate"
        print(f"RESULT prod_calls[{key}]={prod_calls[key]} count  ({role})")
        print(f"RESULT test_calls[{key}]={test_calls[key]} count  ({role})")
    for mod, proxy in loggers.items():
        role = "control" if mod == CONTROL_LOGGER else "candidate"
        print(f"RESULT logger_reads[{mod}]={proxy.reads} count  ({role})")
    print(f"RESULT logger_reads_total={sum(p.reads for m, p in loggers.items() if m != CONTROL_LOGGER)} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}  (the run uses real threads; counts are not timing)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
