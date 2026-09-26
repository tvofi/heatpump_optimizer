"""D2-s4 (round 9, D2.M5): stationary bias of the passive heat-loss learner's bounded Newton step.

Metric: mean of the house heat-loss scale over the last 20000 of 30000 folds of
thermal_model.learner_newton_step (coordinator's HOUSE_LOSS_ALPHA, HOUSE_LOSS_MAX_STEP,
_LEARNER_TRUST_REGION) fed residual = (true - current)*base_u*dT*dt/C + white noise,
minus the true scale, per cell of true scale x residual noise. Count key: the scale
the production step returns. Perturbation: --perturb asym replaces the symmetric trust
region with a one-sided lower clamp at 0.3 (the pre-#193 shape): the bias must go UP.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/s4/newton_bias.py [--perturb none|asym]
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B6. Expected |bias| < 0.01 at base.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer import coordinator as CO  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="none")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    step = TM.learner_newton_step
    if a.perturb == "asym":
        def step(cur, bu, cap, r, dT, dt, *, trust_region, alpha, max_step_fraction):
            t = (bu * cur - r * cap / (dT * dt)) / bu
            if t < 0.3:
                return None
            u = (1 - alpha) * cur + alpha * t
            m = cur * max_step_fraction
            return t, float(np.clip(u, cur - m, cur + m))
    base_u, cap, dT, dt = 0.17, 5.25, 15.0, 0.5
    worst = 0.0
    for true in (0.6, 1.0, 1.6):
        for sig in (0.05, 0.1, 0.2):
            rng = np.random.default_rng(7)
            cur, hist = 1.0, []
            for i in range(30000):
                r = -(true - cur) * base_u * dT * dt / cap + rng.normal(0, sig)
                out = step(cur, base_u, cap, r, dT, dt,
                           trust_region=CO._LEARNER_TRUST_REGION, alpha=CO.HOUSE_LOSS_ALPHA,
                           max_step_fraction=CO.HOUSE_LOSS_MAX_STEP)
                if out is not None:
                    cur = float(np.clip(out[1], 0.3, 3.0))
                if i >= 10000:
                    hist.append(cur)
            b = float(np.mean(hist)) - true
            worst = max(worst, abs(b))
            print(f"RESULT true{true}_sig{sig}_bias={b:+.4f} scale")
    print(f"RESULT worst_abs_bias={worst:.4f} scale")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1])


if __name__ == "__main__":
    main()
