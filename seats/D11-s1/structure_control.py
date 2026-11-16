#!/usr/bin/env python3
"""D11-s1 round 11: the structural ratchet's control, driven by hand (D11.md trap 2).

Metric (one line): over every metric of tests/structure_budgets.json (its keys
less recorded_at), how many the production ratchet REFUSES AS A BREACH (rc 1) when that one
budget is lowered by 1 below the measured value (a one-cap-tighter table).
A metric measured at 0 cannot be lowered (caps are non-negative) and is
reported as floor, not counted. Count key: tests/structure.py:ratchet's
return code per table; rc 2 is its separate refusal of unrecorded slack.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/structure_control.py
Expected: RESULT refused=15 of RESULT lowerable=15 (metrics=18, floor=3), exact;
null control: the committed table returns 0. Perturbation: `--perturb` swaps the
budget table for measured+1 on every key -> refused 0 (down; every table rc 2,
the slack refusal, which is not a breach).
Writes only a temp budget file; BUDGET_FILE is swapped in memory.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
Instrumented symbol: tests/structure.py:ratchet (measure() once, ratchet per table).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, "tests")
import structure  # noqa: E402

PERTURB = "--perturb" in sys.argv
c0, t0 = time.process_time(), time.thread_time()
measure = getattr(structure, "measure", None) or getattr(structure, "measure_all")
with contextlib.redirect_stdout(io.StringIO()):
    result = measure()
committed = json.loads(structure.BUDGET_FILE.read_text())
keys = [k for k in committed if k != "recorded_at"]
tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s1-st-")) / "structure_budgets.json"
real = structure.BUDGET_FILE


def run(table):
    tmp.write_text(json.dumps(table))
    structure.BUDGET_FILE = tmp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return structure.ratchet(result)
    finally:
        structure.BUDGET_FILE = real


null_rc = run(committed)
refused = floor = 0
for k in keys:
    t = dict(committed)
    m = result["metrics"].get(k)
    t[k] = (m + 1) if PERTURB else max(0, (m if m is not None else committed[k]) - 1)
    if PERTURB:
        t.update({kk: result["metrics"].get(kk, committed[kk]) + 1 for kk in keys})
    rc = run(t)
    if not PERTURB and (m or 0) == 0:
        floor += 1
    refused += 1 if rc == 1 else 0
    print(f"{k:40s} measured={m} cap={t[k]} rc={rc}")
print(f"RESULT metrics={len(keys)} metrics")
print(f"RESULT floor={floor} metrics")
print(f"RESULT lowerable={len(keys) - floor} metrics")
print(f"RESULT refused={refused} metrics")
print(f"RESULT null_rc={null_rc} rc")
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
