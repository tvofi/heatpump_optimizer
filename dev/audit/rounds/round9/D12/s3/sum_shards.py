"""Run usable.py's full D12.M4 grid in N shards and sum the counts.

Metric: as usable.py (cells failing the D12.M4 bar), summed over shards.
Run from the export root:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s3/sum_shards.py [--n 4] [--perturb NAME]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B7. Expected: cells=864, failing_cells=0 (exact).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import re
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--perturb", default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    procs = []
    for i in range(a.n):
        cmd = [sys.executable, os.path.join(here, "usable.py"), "--grid", "full", "--shard", f"{i}/{a.n}"]
        if a.perturb:
            cmd += ["--perturb", a.perturb]
        procs.append(subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, env=dict(os.environ)))
    totals: dict[str, int] = {}
    for p in procs:
        out, _ = p.communicate()
        for line in out.splitlines():
            if line.startswith("FAIL"):
                print(line)
            m = re.match(r"RESULT (cells|failing_cells|fail_class_\w+)=(\d+) count", line)
            if m:
                totals[m.group(1)] = totals.get(m.group(1), 0) + int(m.group(2))
    totals.setdefault("failing_cells", 0)
    for k, v in sorted(totals.items()):
        print(f"RESULT {k}={v} count")
    print("RESULT thread_factor=1.000 (child processes pin threads; counts only)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = next((int(l.split()[1]) for l in fh if l.startswith("pswpin")), 0)
    except OSError:
        sw = 0
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
