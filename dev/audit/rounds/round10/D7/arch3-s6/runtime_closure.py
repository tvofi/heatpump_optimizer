#!/usr/bin/env python3
"""ARCH3-s6 (round 10, D7): what importing one module actually loads, measured in a fresh interpreter.

The static closure (private_reach.py) is a graph count; this is the same claim at runtime: for each
module M, a fresh `python3 -c "import heatpump_optimizer.M"` with tests/hastub first on the path,
reporting the package modules loaded, whether the solver (heatpump_optimizer.optimizer) and scipy
were loaded, and the median wall time of K imports (each in its own interpreter).

Metric:   pkg_modules(M), solver(M) in {IN,out}, scipy(M) in {IN,out}, import_ms(M) median of K.
Command:  python3 dev/audit/rounds/round10/D7/arch3-s6/runtime_closure.py TREE_ROOT [K] [MODULE ...]
          TREE_ROOT holds custom_components/ (an extracted tree: origin/main or a prototype).
Perturbation: the tree (origin/main vs main+P1..P4): solver and scipy leave store, notifier,
          legionella (direction to_zero on the IN count); pkg_modules falls.
Null control: a module no patch touches and whose closure the patches do not reach
          (default: `const`) must read the same pkg_modules and solver/scipy on both trees; its
          import_ms bounds the timing noise.
"""
from __future__ import annotations

import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

PROBE = (
    "import sys,time;t=time.perf_counter();import heatpump_optimizer.{m};"
    "d=(time.perf_counter()-t)*1000;"
    "p=[k for k in sys.modules if k.startswith('heatpump_optimizer.')];"
    "print(len(p),'heatpump_optimizer.optimizer' in sys.modules,'scipy' in sys.modules,f'{{d:.1f}}')"
)


def probe(tree: Path, hastub: Path, m: str, k: int):
    env = dict(os.environ, PYTHONPATH=f"{hastub}:{tree / 'custom_components'}", PYTHONDONTWRITEBYTECODE="1")
    runs = []
    for _ in range(k):
        out = subprocess.run([sys.executable, "-c", PROBE.format(m=m)], env=env, check=True,
                             capture_output=True, text=True).stdout.split()
        runs.append(out)
    n, solver, scipy = runs[0][0], runs[0][1] == "True", runs[0][2] == "True"
    return int(n), solver, scipy, statistics.median(float(r[3]) for r in runs)


def main(argv):
    t_cpu, t_thr = time.process_time(), time.thread_time()
    tree = Path(argv[1]).resolve()
    k = int(argv[2]) if len(argv) > 2 else 5
    mods = argv[3:] or ["store", "notifier", "legionella", "debugger", "setpoint_check", "repairs", "const"]
    hastub = Path(__file__).resolve().parents[6] / "tests" / "hastub"
    in_count = 0
    for m in mods:
        n, solver, scipy, ms = probe(tree, hastub, m, k)
        in_count += solver
        print(f"RESULT {m}: pkg_modules={n} solver={'IN' if solver else 'out'} "
              f"scipy={'IN' if scipy else 'out'} import_ms={ms:.1f}")
    print(f"RESULT solver_in_count={in_count} of {len(mods)}")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
