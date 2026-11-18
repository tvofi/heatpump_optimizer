"""P4 probe: the all-off gap per production multi-start call SITE, including
_relaxed_plans' free-room re-run (optimizer.py, the second _multi_start_minimize
in _relaxed_plans), which runs only where a switch has a price: a stop is
learned (config.duty_switch_stop_probability > 0) and cycling_cost > 0.

Metric per call: gap = f(x_prod) - f(x_off) on the call's own descent objective,
where x_off is production's _multi_start_minimize from the lower-bound vector
alone (same objective, bounds, args, maxiter, batch objective). A site fails
when any cell has gap > GAP_EPS. Cells: D0-s3-02's universe
(summer_negative/summer_warm, every d0-grid line with hot water, so the
_solve_space path runs) with a learned stop forced on.
  --null     the flat-price twins (nothing pays the pump to run): expected 0
  --limit N  first N cells
Exit 1 when the free-room site fails.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P4/probe_offstart_sites.py [--null] [--limit N]
"""
from __future__ import annotations

import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "dev/audit/rounds/round11/D0/s3"))
import numpy as np  # noqa: E402
import d0s3_lib as L  # noqa: E402

GAP_EPS = 1e-4
STOPS = (0.5, 0.5)
CYCLING = 0.5


def cells(null: bool) -> list[str]:
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                         text=True, check=True, cwd=ROOT).stdout.split()
    base = [c for c in out if c.startswith("summer_negative/summer_warm/") and "/dhw/" in c]
    return ["flat/" + c.split("/", 1)[1] for c in base] if null else base


def main(argv: list[str]) -> int:
    null = "--null" in argv
    cs = cells(null)
    if "--limit" in argv:
        cs = cs[: int(argv[argv.index("--limit") + 1])]
    om = L.om
    worst = defaultdict(lambda: [0, 0, 0.0, ""])  # site -> calls, gap calls, max gap, cell
    for cell in cs:
        b = L.build(cell)
        o = b["optimizer"]
        o.config.duty_switch_stop_probability = STOPS
        if not o.config.cycling_cost > 0:
            o.config.cycling_cost = CYCLING
        rec = []

        def ms(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, move_starts=None):
            fr = sys._getframe(1)
            kw = {} if move_starts is None else {"move_starts": move_starts}
            res = L.ORIG_MS(objective, candidates, bounds, args, maxiter=maxiter,
                            batch_objective=batch_objective, **kw)
            rec.append((f"{fr.f_code.co_name}:{fr.f_lineno}", objective, bounds, args, maxiter,
                        batch_objective, np.asarray(res.x, dtype=float)))
            return res

        with L.mock.patch.object(om, "_multi_start_minimize", ms):
            o.optimize(inputs=L.inputs_of(b))
        for site, f, bounds, args, mi, bf, x in rec:
            lo = np.array([q[0] for q in bounds], dtype=float)
            xo = np.asarray(L.ORIG_MS(f, [lo], bounds, args, maxiter=mi, batch_objective=bf).x, dtype=float)
            gap = float(f(x, *args)) - float(f(xo, *args))
            w = worst[site]
            w[0] += 1
            if gap > GAP_EPS:
                w[1] += 1
            if gap > w[2]:
                w[2], w[3] = gap, cell
    free = None
    for site, (n, g, mx, cell) in sorted(worst.items()):
        print(f"site {site} calls={n} gap_calls={g} max_gap={mx:.4f} {cell}")
        if site.startswith("_relaxed_plans") and int(site.split(":")[1]) > 246:
            free = g
    print(f"RESULT {'null' if null else 'tree'} cells={len(cs)} free_room_gap_calls={free}")
    return 1 if free else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
