#!/usr/bin/env python3
"""D3 round 2 -- how much of each script's MEASURED closure it actually executes.

Metric per fast script: executed_prod = number of production modules
(custom_components/heatpump_optimizer/*.py) in which at least one FUNCTION
body ran while the script ran (sys.setprofile 'call' events on code objects
with CO_OPTIMIZED; module and class bodies executing at import do not
count -- importing is what the closure records already);
closure_prod = production modules in the script's closure in
tests/closures.json; forced = closure_prod - executed_prod, the modules a
change to which runs this script although the script never executes a line
of them. Also, per production module: the CI seconds of scripts that would
run for a change to it but never execute it (closures.json 'recorded').

Run from the repository root:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    .venv/bin/python tools/audit/round2/D3/closure_precision.py [tests/<script>.py ...]

Expected on c398fc84eec25fc44b60d74aae05b9a2da205884 (8-core Apple M1):
validate.py executes ~12 of its 38 closure modules. Perturbation: add
`import heatpump_optimizer.pump_mode as _pm; _pm.__name__` plus a call into
it to tests/validate.py -> validate.py executed_prod rises by 1.
Instrumented symbol: every function in custom_components/heatpump_optimizer
(the profiler sees each call's code object filename). The quiet-window
scripts (stress.py, edge.py, backtest.py) are not run; their rows are
reported as unmeasured.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import runpy
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
PROD = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
FAST = ["tests/open_meteo.py", "tests/solar_alignment.py", "tests/plan_view.py",
        "tests/entities.py", "tests/optimality.py", "tests/manual_plan.py",
        "tests/validate.py", "tests/features.py"]
QUIET = ["tests/stress.py", "tests/edge.py", "tests/backtest.py"]


def child(script: str) -> int:
    sys.path.insert(0, "tests")
    sys.path.insert(0, "custom_components")
    seen: set[str] = set()
    prefix = PROD + os.sep

    import inspect

    def prof(frame, event, arg):
        # Only real function bodies count (CO_OPTIMIZED): module and class
        # bodies also raise a 'call' event when they are imported, and an
        # import is exactly what the closure already knows about.
        if event == "call" and frame.f_code.co_flags & inspect.CO_OPTIMIZED:
            f = frame.f_code.co_filename
            if f.startswith(prefix):
                seen.add(os.path.relpath(f, ROOT))
    sys.setprofile(prof)
    import threading
    threading.setprofile(prof)
    sys.argv = [script]
    rc = 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except BaseException as e:  # noqa: BLE001
        rc = 1
        sys.stderr.write(f"census error {e!r}\n")
    sys.setprofile(None)
    sys.stderr.write("EXECUTED " + json.dumps({"script": script, "rc": rc, "executed": sorted(seen)}) + "\n")
    return rc


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--child":
        return child(sys.argv[2])
    scripts = sys.argv[1:] or FAST
    closures = json.load(open(os.path.join(ROOT, "tests", "closures.json")))
    rec = {k: v["seconds"] for k, v in closures["recorded"].items()}
    tmp = tempfile.mkdtemp(prefix="d3prec_")
    env = dict(os.environ)
    env["HPO_PLANDATA"] = os.path.join(tmp, "plandata.json")
    executed: dict[str, set[str]] = {}
    for s in scripts:
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", s],
                           capture_output=True, text=True, env=env, cwd=ROOT)
        got = None
        for line in p.stderr.splitlines():
            if line.startswith("EXECUTED "):
                got = json.loads(line[9:])
        if got is None:
            print(f"{s}: no census line; stderr tail: {p.stderr[-300:]}")
            continue
        executed[s] = set(got["executed"])
        clo = {f for f in closures["closures"].get(s, []) if f.startswith("custom_components/") and f.endswith(".py")}
        forced = sorted(clo - executed[s])
        extra = sorted(executed[s] - clo)
        n = s.split("/")[-1]
        print(f"RESULT {n}.closure_prod={len(clo)} count")
        print(f"RESULT {n}.executed_prod={len(executed[s])} count")
        print(f"RESULT {n}.forced_modules={len(forced)} count")
        print(f"  {n}: rc={got['rc']} forced={[f.split('/')[-1] for f in forced]} executed_not_in_closure={extra}")
    # per production module: CI seconds forced by scripts that never execute it
    prod = sorted({f for fs in closures["closures"].values() for f in fs
                   if f.startswith("custom_components/") and f.endswith(".py")})
    rows = []
    for m in prod:
        forced_by = [s for s in executed if m in closures["closures"].get(s, []) and m not in executed[s]]
        needed_by = [s for s in executed if m in executed[s]]
        unmeasured = [s for s in QUIET if m in closures["closures"].get(s, [])]
        rows.append((sum(rec.get(s, 0) for s in forced_by), m.split("/")[-1], forced_by, needed_by, unmeasured))
    rows.sort(reverse=True)
    print("\nper module: CI seconds of measured fast scripts forced to run without executing the module")
    for secs, m, fb, nb, um in rows:
        print(f"  {m:22s} forced_ci_s={secs:7.1f} forced_by={[s.split('/')[-1] for s in fb]} "
              f"executed_by={[s.split('/')[-1] for s in nb]} unmeasured_quiet={[s.split('/')[-1] for s in um]}")
    print(f"RESULT modules_forced_somewhere={sum(1 for r in rows if r[0] > 0)} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
