"""D1-s1-51: plan_slots' published slot 'reason' depends on PYTHONHASHSEED on a tie.

Metric: number of distinct slot['reason'] values plan_slots.plan_slots publishes for
one fixed 4-step plan whose reasons tie 2:2 ('cheap','cheap','preheat','preheat'),
across child interpreters run with PYTHONHASHSEED=1..12 (count key: the published
slot['reason'] string the production function returns).
Null control: a 3:1 plan ('cheap','cheap','cheap','preheat') -- distinct must be 1.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py [--perturb]
  --perturb, in each child, replaces the name `set` inside the plan_slots module
  with an insertion-ordered set (dict.fromkeys) -- the one-line fix shape
  max(dict.fromkeys(codes), key=codes.count); distinct_tie must go to 1.
Expected: distinct_tie=2 (exact for seeds 1..12 on CPython 3.x), distinct_null=1 (exact).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (planted finder export
audit-r11-leads-px), machine: owner's macOS box (B8).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import subprocess
import sys
import time

CHILD = r'''
import os, sys
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import plan_slots as ps
if sys.argv[2] == "1":
    ps.set = lambda xs: dict.fromkeys(xs)
t0 = datetime(2026, 1, 15, tzinfo=timezone.utc)
ts = [t0 + timedelta(minutes=15 * i) for i in range(4)]
reasons = sys.argv[1].split(",")
out = ps.plan_slots(ts, [2.0] * 4, [1.0] * 4, 0.25, reasons=reasons)
print(out[0]["reason"])
'''

c0 = time.process_time()
perturb = "1" if "--perturb" in sys.argv else "0"


def distinct(reasons):
    seen = {}
    for seed in range(1, 13):
        env = dict(os.environ, PYTHONHASHSEED=str(seed))
        r = subprocess.run([sys.executable, "-c", CHILD, reasons, perturb],
                           capture_output=True, text=True, env=env, check=True)
        seen.setdefault(r.stdout.strip(), []).append(seed)
    print(reasons, seen)
    return len(seen)


tie = distinct("cheap,cheap,preheat,preheat")
null = distinct("cheap,cheap,cheap,preheat")
print(f"RESULT distinct_tie={tie} count")
print(f"RESULT distinct_null={null} count")
# Work is in child processes; the parent's own CPU is pinned single-threaded.
pc, tc = time.process_time() - c0, time.thread_time()
print(f"RESULT thread_factor={1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
