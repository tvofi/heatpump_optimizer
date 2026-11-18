"""D0 verifier V2 for D0-s3-03 (round 11): does dropping _terminal_cost breach the comfort floor in ANY zone?

Metric (one line): per cell and comfort_weight w, dmin = min over the last 8 steps and over every zone
trajectory the result carries (room, upper, lower) of (temperature - per-step floor); a breach is dmin < -1e-3;
counted: cells where the no-credit plan breaches and the credit plan does not (or breaches less, by > 1e-3 K).
Weights: 1.0 (COMFORT_WEIGHT_MIN), the config default, 40.0 (COMFORT_WEIGHT_MAX), and 0.05 (control, outside
the learnable range). Cells: my own set, not the finder's -- every d0-grid 24h line with price winter_typical
and weather winter_cold or shoulder (cold-to-mild coasting days), plus the same at 48h for plain.
Command (worktree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D0/verify/v2_terminal.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import subprocess
from datetime import timedelta
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s3"))
import d0s3_lib as L  # noqa: E402  (cell builder only)
import numpy as np  # noqa: E402
from golden import START  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402
TAIL = 8
ORIG = HeatPumpOptimizer._terminal_cost


def zero_tc(self, *a, **k):
    ORIG(self, *a, **k)
    return (lambda *x, **y: 0.0), (lambda traj: np.zeros(next(iter(traj.values())).shape[0]))


def run(cell, w, credit):
    b = L.build(cell)
    opt = b["optimizer"]
    if w is not None:
        opt.config.comfort_weight = w
    if credit:
        r = opt.optimize(inputs=L.inputs_of(b))
    else:
        with mock.patch.object(HeatPumpOptimizer, "_terminal_cost", zero_tc):
            r = opt.optimize(inputs=L.inputs_of(b))
    n = len(r.power_schedule)
    fl = []
    for i in range(n):
        t = START + timedelta(minutes=15 * (i + 1))
        fl.append(opt.config.get_temp_bounds(t.hour + t.minute / 60.0)[0])
    fl = np.array(fl)
    dmin = np.inf
    for tr in (r.room_temp_trajectory, getattr(r, "upper_temp_trajectory", None),
               getattr(r, "lower_temp_trajectory", None)):
        if tr is None:
            continue
        t = np.asarray(tr, float)[1:n + 1]
        if t.size < n:
            continue
        dmin = min(dmin, float(np.min(t[-TAIL:] - fl[-TAIL:])))
    return dmin, float(np.sum(np.asarray(r.power_schedule, float)[-TAIL:]) * 0.25), opt.config.comfort_weight


def main():
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                         text=True, check=True).stdout.split()
    cells = [c for c in out if c.startswith("winter_typical/") and c.split("/")[1] in ("winter_cold", "shoulder")
             and c.endswith("/24h")]
    cells += [c for c in out if c.startswith("winter_typical/winter_cold/") and "/plain/48h" in c]
    lim = int(os.environ.get("V2_LIMIT", "0") or 0)
    if lim:
        cells = cells[:lim]
    weights = [float(x) if x != "default" else None for x in os.environ.get("V2_WEIGHTS", "1.0,default,40.0,0.05").split(",")]
    c0, t0 = time.process_time(), time.thread_time()
    for w in weights:
        worse = breach_nc = dump = 0
        worst = 0.0
        wv = None
        for c in cells:
            dc, kc, wv = run(c, w, True)
            dn, kn, _ = run(c, w, False)
            if dn < -1e-3 and dn < dc - 1e-3:
                worse += 1
            breach_nc += int(dn < -1e-3)
            dump += int(kn < kc - 1e-3)
            worst = min(worst, dn)
            print(f"w={wv} {c} dmin credit={dc:.4f} nocredit={dn:.4f} tail_kwh {kc:.3f}->{kn:.3f}", flush=True)
        print(f"RESULT v2_w={wv} worse_tail_floor_cells={worse}/{len(cells)} nocredit_breach_cells={breach_nc} "
              f"tail_dump_cells={dump}/{len(cells)} worst_nocredit_margin={worst:.4f} K", flush=True)
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
