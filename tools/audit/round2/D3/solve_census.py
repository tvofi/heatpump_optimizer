#!/usr/bin/env python3
"""D3 round 2 -- how much each fast test script solves versus how much it asserts.

Metric per script: optimize_calls = calls to
`heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize`; minimize_calls =
calls to `scipy.optimize.minimize` (the L-BFGS-B starts); sim_calls = calls
to `heatpump_optimizer.thermal_model:ThermalModel.simulate_trajectory` +
`simulate_trajectory_batch` + `simulate_trajectory_with_dhw`; checks = lines
the script printed that begin with `  ok` or `  FAIL` (tests/harness.py's
Results.check format); cpu_s / wall_s of the script's own process.

Run from the repository root:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    .venv/bin/python tools/audit/round2/D3/solve_census.py [tests/<script>.py ...]

Expected on c398fc84eec25fc44b60d74aae05b9a2da205884 (8-core Apple M1,
fan-out load, so cpu numbers are provisional): features.py optimize_calls
~30 with ~1400 checks; validate.py ~23 optimize calls with 0 `ok` lines.
Perturbation: delete one `run(...)` line in tests/validate.py ->
validate.py optimize_calls drops by exactly 1.
Runs only the fast scripts (never stress.py, edge.py, backtest.py -- those
are the quiet window's). Each script runs in its own subprocess of this
file (`--child <script>`), which installs the counters and then executes
the script with runpy as __main__.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import io
import json
import resource
import runpy
import subprocess
import tempfile
import time

FAST = ["tests/frontend.py", "tests/open_meteo.py", "tests/solar_alignment.py",
        "tests/plan_view.py", "tests/entities.py", "tests/dst_checks.py",
        "tests/optimality.py", "tests/manual_plan.py", "tests/validate.py",
        "tests/features.py"]


class _Tee(io.TextIOBase):
    def __init__(self, sink):
        self.sink = sink
        self.ok = 0
        self.fail = 0
        self.buf = ""

    def write(self, s):
        self.buf += s
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            if line.startswith("  ok"):
                self.ok += 1
            elif line.startswith("  FAIL"):
                self.fail += 1
        return self.sink.write(s)

    def flush(self):
        return self.sink.flush()


def child(script: str) -> int:
    sys.path.insert(0, "tests")
    sys.path.insert(0, "custom_components")
    counts = {"optimize": 0, "minimize": 0, "simulate": 0}
    import scipy.optimize as so
    from heatpump_optimizer import optimizer as opt_mod
    from heatpump_optimizer import thermal_model as tm

    def wrap(obj, name, key):
        orig = getattr(obj, name)

        def w(*a, **k):
            counts[key] += 1
            return orig(*a, **k)
        setattr(obj, name, w)

    wrap(opt_mod.HeatPumpOptimizer, "optimize", "optimize")
    wrap(so, "minimize", "minimize")
    wrap(opt_mod, "minimize", "minimize") if hasattr(opt_mod, "minimize") else None
    for n in ("simulate_trajectory", "simulate_trajectory_batch", "simulate_trajectory_with_dhw"):
        if hasattr(tm.ThermalModel, n):
            wrap(tm.ThermalModel, n, "simulate")
    tee = _Tee(sys.stdout)
    sys.stdout = tee
    sys.argv = [script]
    if script.endswith("dst_checks.py"):
        os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
    t0 = time.time()
    rc = 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        rc = int(e.code or 0) if isinstance(e.code, int) or e.code is None else 1
    except BaseException as e:  # noqa: BLE001
        rc = 1
        print(f"  FAIL census: {e.__class__.__name__}: {e}")
    sys.stdout = tee.sink
    ru = resource.getrusage(resource.RUSAGE_SELF)
    out = {"script": script, "rc": rc, "wall_s": round(time.time() - t0, 1),
           "cpu_s": round(ru.ru_utime + ru.ru_stime, 1), "ok": tee.ok, "fail": tee.fail,
           "optimize_calls": counts["optimize"], "minimize_calls": counts["minimize"],
           "sim_calls": counts["simulate"], "load1": round(os.getloadavg()[0], 2)}
    sys.stderr.write("CENSUS " + json.dumps(out) + "\n")
    return rc


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--child":
        return child(sys.argv[2])
    scripts = sys.argv[1:] or FAST
    tmp = tempfile.mkdtemp(prefix="d3census_")
    env = dict(os.environ)
    env["HPO_PLANDATA"] = os.path.join(tmp, "plandata.json")
    rows = []
    for s in scripts:
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", s],
                           capture_output=True, text=True, env=env)
        rec = None
        for line in p.stderr.splitlines():
            if line.startswith("CENSUS "):
                rec = json.loads(line[7:])
        if rec is None:
            rec = {"script": s, "rc": p.returncode, "error": p.stderr[-300:]}
        rows.append(rec)
        print(json.dumps(rec), flush=True)
    for r in rows:
        n = r["script"].split("/")[-1]
        for k in ("optimize_calls", "minimize_calls", "sim_calls", "ok", "fail", "cpu_s", "wall_s"):
            if k in r:
                print(f"RESULT {n}.{k}={r[k]} {'s' if k.endswith('_s') else 'count'}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
