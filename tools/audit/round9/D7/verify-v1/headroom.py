#!/usr/bin/env python3
"""D7-s1-01 V1 independent check: headroom of the rows the inlining moves.

Metric: budget - measured for each structure.measure() metric, at the tree
under test; a row with 0 headroom fails the ratchet on any +1.
Command (repo root): PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v1/headroom.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, io, json, sys, time
sys.path.insert(0, "tests")
import structure as S
t0, tt0 = time.process_time(), time.thread_time()
with contextlib.redirect_stdout(io.StringIO()):
    m = S.measure()["metrics"]
b = json.load(open("tests/structure_budgets.json"))
zero = []
for k in sorted(b):
    if k == "recorded_at":
        continue
    bv = b[k] if not isinstance(b[k], dict) else b[k].get("value", b[k])
    try:
        h = float(bv) - float(m[k])
    except Exception:
        continue
    print(f"RESULT headroom_{k}={h:g} count  # measured={m[k]} budget={bv}")
    if h == 0:
        zero.append(k)
print(f"RESULT zero_headroom_rows={len(zero)} count  # {','.join(zero)}")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-tt0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
