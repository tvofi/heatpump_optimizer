"""D0 verifier V2 for D0-s3-02 (round 11): is the shipped plan worse than doing nothing?

Metric (one line): per cell, gap_lo = J(shipped) - J(lo), both scored by the scope function production's
_commit_runs returned for the plan that ships (scope[1](x, *args) of the paired _multi_start_minimize call),
where lo is the call's lower-bound vector itself (no descent, no commit) -- the cheapest possible
challenger. Counted: cells with gap_lo > 1e-4; and rel = gap_lo / |J(shipped)|.
Cells: the d0-grid summer_negative/summer_warm lines (60) and their flat twins (null control).
Command (worktree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D0/verify/v2_offscore.py [--limit N]
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import subprocess
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s3"))
import d0s3_lib as L  # noqa: E402  (cell builder only)
import numpy as np  # noqa: E402
om = L.om
MS, CM = om._multi_start_minimize, om._commit_runs


def one(cell):
    b = L.build(cell)
    log = []
    last = {}

    def ms(objective, candidates, bounds, args=(), *a, **k):
        last["args"], last["bounds"] = tuple(args), list(bounds)
        return MS(objective, candidates, bounds, args, *a, **k)

    def cm(opt, h, scope, relaxed, dhw, maxiter, rescope=None):
        out = CM(opt, h, scope, relaxed, dhw, maxiter, rescope)
        log.append((np.asarray(out[0], float), out[1], last.get("args", ()), last.get("bounds")))
        return out

    with mock.patch.object(om, "_multi_start_minimize", ms), mock.patch.object(om, "_commit_runs", cm):
        r = b["optimizer"].optimize(inputs=L.inputs_of(b))
    ship = np.asarray(r.power_schedule, float)
    pick = [e for e in log if e[0].size == ship.size and np.allclose(e[0], ship, atol=1e-6)]
    if not pick:
        return {"cell": cell, "note": "no commit matched the shipped plan", "commits": len(log)}
    x, scope, args, bounds = pick[-1]
    lo = np.array([q[0] for q in bounds], float)
    js, jl = float(scope[1](x, *args)), float(scope[1](lo, *args))
    return {"cell": cell, "J_ship": js, "J_lo": jl, "gap_lo": js - jl, "rel": (js - jl) / abs(js) if js else 0.0,
            "kwh_ship": float(ship.sum() * 0.25), "lo_kwh": float(lo.sum() * 0.25)}


def main():
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                         text=True, check=True).stdout.split()
    base = [c for c in out if c.startswith("summer_negative/summer_warm/")]
    cells = base + ["flat/" + c.split("/", 1)[1] for c in base]
    c0, t0 = time.process_time(), time.thread_time()
    R = []
    for c in cells:
        try:
            d = one(c)
        except Exception as e:  # noqa: BLE001
            d = {"cell": c, "error": repr(e)[:300]}
        R.append(d)
        print(json.dumps(d), flush=True)
    for arm in ("summer_negative", "flat"):
        sub = [d for d in R if d["cell"].startswith(arm) and "gap_lo" in d]
        pos = [d for d in sub if d["gap_lo"] > 1e-4]
        plants = {}
        for d in pos:
            p = d["cell"].split("/")[4]
            plants[p] = plants.get(p, 0) + 1
        print(f"RESULT v2_{arm}_lo_beats_ship={len(pos)}/{len(sub)} "
              f"max_gap={max([d['gap_lo'] for d in pos] or [0]):.2f} max_rel={max([d['rel'] for d in pos] or [0]):.4f} "
              f"min_gap={min([d['gap_lo'] for d in pos] or [0]):.2f} plants={json.dumps(plants, sort_keys=True)}")
    print(f"RESULT unmatched_or_error={sum(1 for d in R if 'gap_lo' not in d)}")
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
