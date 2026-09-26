#!/usr/bin/env python3
"""V3 (round 9) D1-s4-01: the finder's duty-targeted mutant stream (store_fuzz.py,
seed 9104+1, N=250, same mutate()) replayed THROUGH the production persistence
boundary store._sanitize (what QuarantiningStore.async_load applies to every
store) before DefrostDerate.from_dict -- the route a stored payload takes in HA.

Metric (one line): of 250 duty-targeted mutants, the count whose loaded duty grid
still holds a non-finite or out-of-[0,1] cell after 24 healthy zero-duty folds
per bucket, split by whether the mutant's bad scalar was non-finite-coercible or
finite; and how many pin a bucket at DERATE_MIN.
Command:  PYTHONPATH=tests/hastub /root/venv314/bin/python tools/audit/round9/D1/verify-v3/D1-s4-01_boundary_replay.py [--no-boundary]
  --no-boundary: skip _sanitize (reproduces the finder's 53 -- the control that
  this replay draws the same stream).
Expected: measured, exact (seeded).  Baseline SHA 1936d5ca (evidence tree).
Machine: cloud 4-core box, CPython 3.14.0rc2 (V3 sub-seat for G1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests/hastub")
sys.path.insert(0, ".")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from custom_components.heatpump_optimizer import defrost as D  # noqa: E402
from custom_components.heatpump_optimizer import store as S  # noqa: E402

BOUNDARY = "--no-boundary" not in sys.argv
N, SEED = 250, 9104
NT, NH = len(D.TEMP_EDGES) - 1, len(D.HUMIDITY_EDGES) - 1
BAD_SCALARS = ["nan", "inf", "-inf", "NaN", "1e308", 1e300, -1e300, -5.0, 50.0,
               "abc", None, [], {}, True, 2 ** 70, "", "0x10"]
KEYS = ["factors", "counts", "duty", "duty_counts", "duty_events", "version"]


def healthy():
    return {"version": 2,
            "factors": [[0.9] * NH for _ in range(NT)], "counts": [[15] * NH for _ in range(NT)],
            "duty": [[0.05] * NH for _ in range(NT)], "duty_counts": [[20] * NH for _ in range(NT)],
            "duty_events": [[3] * NH for _ in range(NT)]}


def mutate(rng, payload, target_key=None):  # verbatim draw order of store_fuzz.py
    op = rng.choice(["cell", "cell", "cell", "type", "drop", "nest", "trunc", "whole"])
    key = target_key or rng.choice(KEYS)
    p = copy.deepcopy(payload)
    bad = None
    if op == "whole":
        return rng.choice(["x", 3, [], None, [p]]), op, key, bad
    if op == "drop":
        p.pop(key, None)
    elif op == "type":
        p[key] = rng.choice(["x", 3.0, None, {}, {"a": 1}])
    elif op == "nest" and isinstance(p.get(key), list):
        p[key][rng.randrange(NT)] = rng.choice([0.1, "row", {"r": 1}])
    elif op == "trunc" and isinstance(p.get(key), list):
        p[key] = p[key][: rng.randrange(NT)]
    elif isinstance(p.get(key), list):
        t, h = rng.randrange(NT), rng.randrange(NH)
        bad = rng.choice(BAD_SCALARS)
        p[key][t][h] = bad
    return p, op, key, bad


centres = [(tc, hc) for tc in D.TEMP_CENTERS for hc in D.HUMIDITY_CENTERS]
rng = random.Random(SEED + 1)
stuck = pinned = migrated = 0
by_bad = {}
for _ in range(N):
    mut, op, key, bad = mutate(rng, healthy(), "duty")
    payload = S._sanitize({"defrost": mut}).get("defrost") if BOUNDARY else mut
    try:
        inst = D.DefrostDerate.from_dict(payload)
        for _c in range(24):
            for tc, hc in centres:
                inst.observe_duty(tc, hc, 0.0, 0)
                inst.observe(tc, hc, 1.0)
    except Exception:  # noqa: BLE001
        continue
    migrated += bool(inst.migrated)
    if any(not math.isfinite(v) or v > 1 or v < 0 for r in inst.duty for v in r):
        stuck += 1
        by_bad[repr(bad)] = by_bad.get(repr(bad), 0) + 1
        if any(abs(inst.factor(tc, hc) - D.DERATE_MIN) < 1e-12 for tc, hc in centres):
            pinned += 1
print(f"MODE boundary={BOUNDARY}")
print("  stuck by bad scalar:", dict(sorted(by_bad.items())))
print(f"RESULT duty_targeted_stuck={stuck} count (of {N})")
print(f"RESULT duty_targeted_pinned_at_derate_min={pinned} count")
print(f"RESULT duty_targeted_flagged_migrated={migrated} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
