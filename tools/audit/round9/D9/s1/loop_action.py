"""D9-s1 H10: loop-thread CPU of optimizer.HeatPumpOptimizer.get_current_action,
which the coordinator calls on the event loop after every solve.

Metric: thread CPU per get_current_action(result, now) call (median of 200),
in microseconds and as a fraction of tests/stress.py:reference_solve, per
cell (single / two zone, DHW).
Count key: time.thread_time() around the production call.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/loop_action.py [--hours 48]
Perturbation: --hours 48 doubles the plan the action is read from; a
per-step scan moves the number UP, a constant-time lookup does not.
Provisional (CPU). Baseline SHA 1936d5ca72a0.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import time
from datetime import timedelta

import numpy as np

import stress


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]
    for cell, spec in {"single_zone_dhw": dict(season="winter", dhw=True),
                       "two_zone_dhw": dict(season="winter", two_zone=True, dhw=True)}.items():
        run = stress.build_case(hours=args.hours, **spec)
        opt, res = run["optimizer"], run["result"]
        now = stress.START + timedelta(minutes=7)
        ts = []
        for _ in range(200):
            t0 = time.thread_time()
            opt.get_current_action(res, now)
            ts.append(time.thread_time() - t0)
        med = float(np.median(ts))
        C.result(f"{cell}_h{args.hours}.get_current_action_us", round(med * 1e6, 1), "us (provisional)")
        C.result(f"{cell}_h{args.hours}.over_reference", round(med * 1000 / ref, 5), "x reference_solve")
    C.trailer(1.0)


if __name__ == "__main__":
    main()
