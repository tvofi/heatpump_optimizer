"""D0 verifier V2 for D0-s2-01 (round 11): independent block-challenger harness.

Metric (one line): per cell, gap_v2 = res.objective_value(production) - res.objective_value(production with
ONE extra candidate appended to the space-only _multi_start_minimize call: the best single contiguous block
at constant power P in {1.0,1.5,2.0} kW, length 1..8 h, start on the hour, ranked by that call's own objective).
Beside it: zero_starts = candidates with sum 0 in the space-only call (no args).
Command (worktree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D0/verify/v2_wood.py CELL...
  env WOOD_TANK_C=<C> overrides the s2 builder's charged-tank temperature (seam: how charged must the tank be).
  --single-zone: rewrite topology to single-zone (seam: the scaling is not two-zone-only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s2"))
import cells  # noqa: E402  (input builder only: production coordinator's _solve_record)
import numpy as np  # noqa: E402
import heatpump_optimizer.optimizer as om  # noqa: E402
REAL = om._multi_start_minimize
if os.environ.get("WOOD_TANK_C"):
    cells.WOOD_TANK_C = float(os.environ["WOOD_TANK_C"])


def blocks(n, hi):
    for P in (1.0, 1.5, 2.0):
        for L in range(4, min(n, 32) + 1, 4):
            for s in range(0, n - L + 1, 4):
                x = np.zeros(n)
                x[s:s + L] = P
                yield np.minimum(x, hi)


def solve(line, extra):
    rec, _ = cells.cell_record(line)
    info = {}

    def w(objective, candidates, bounds, args=(), *a, **k):
        if not args and "z" not in info:
            info["z"] = sum(1 for c in candidates if float(np.sum(np.asarray(c, float))) <= 0.0)
            info["n"] = len(candidates)
            if extra:
                hi = np.array([b[1] for b in bounds])
                best = min(blocks(len(bounds), hi), key=lambda x: float(objective(x)))
                info["blk_kwh"] = float(best.sum() * 0.25)
                candidates = list(candidates) + [best]
        return REAL(objective, candidates, bounds, args, *a, **k)

    with mock.patch.object(om, "_multi_start_minimize", w):
        res = rec.optimizer().optimize(inputs=rec.inputs)
    return res, info, rec


def main():
    lines = [a for a in sys.argv[1:] if not a.startswith("--")]
    sz = "--single-zone" in sys.argv
    c0, t0 = time.process_time(), time.thread_time()
    gaps = []
    for line in lines:
        if sz:
            p = line.split("/")
            p[2] = "single-zone"
            line = "/".join(p)
        r0, i0, rec = solve(line, False)
        r1, i1, _ = solve(line, True)
        g = float(r0.objective_value) - float(r1.objective_value)
        gaps.append(g)
        dt = float(rec.config.dt_hours)
        print(f"RESULT v2[{line}] zero_starts={i0.get('z')} of {i0.get('n')} "
              f"kWh_prod={np.sum(r0.power_schedule) * dt:.3f} kWh_aug={np.sum(r1.power_schedule) * dt:.3f} "
              f"J_prod={float(r0.objective_value):.4f} J_aug={float(r1.objective_value):.4f} gap_v2={g:.4f} "
              f"blk_kwh={i1.get('blk_kwh')}", flush=True)
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    if gaps:
        print(f"RESULT v2_gap max={max(gaps):.4f} min={min(gaps):.4f} "
              f"cells_gap_gt_0.01={sum(g > 0.01 for g in gaps)}/{len(gaps)}")
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
