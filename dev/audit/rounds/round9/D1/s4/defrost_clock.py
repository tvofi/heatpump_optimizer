#!/usr/bin/env python3
"""D1-s4 M3: the defrost measurement window under DST, clock jumps and unreadable flags.

Metric (one line): over the case table below, the count of DefrostWindow.close() results
whose ``seconds`` differs from the true UTC elapsed time by > 1 s, whose duty leaves [0, 1],
or which report ``observed`` for an interval containing an unreadable (None) flag.
Key: the DefrostObservation the production window returns.

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/defrost_clock.py
          [--perturb]  defrost.dt_util.as_utc replaced by identity (CPython's same-zone
                       wall-clock subtraction, the pre-#1299 shape): bad goes UP (the DST cases).
Expected (baseline): bad=0 of 9 cases; perturbed: bad>=2.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6
Instrumented: custom_components.heatpump_optimizer.defrost:DefrostWindow.observe/close/_elapsed
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock
from zoneinfo import ZoneInfo

sys.path[:0] = [".", "tests/hastub"]
t_proc0, t_thr0 = time.process_time(), time.thread_time()
from custom_components.heatpump_optimizer import defrost as D  # noqa: E402

PERTURB = "--perturb" in sys.argv
Z = ZoneInfo("Europe/Stockholm")


def utc(y, mo, d, h, mi):
    return datetime(y, mo, d, h, mi, tzinfo=timezone.utc)


def loc(t):
    return t.astimezone(Z)


# (name, [(stamp, flag)...], close_stamp, true_elapsed_s or None if unknown, expect_observed)
T_FALL = utc(2026, 10, 25, 0, 45)  # 02:45 CEST, 15 min before the fall-back
T_SPRING = utc(2026, 3, 29, 0, 45)  # 01:45 CET, 15 min before the spring-forward
cases = [
    ("dst_fall_back", [(loc(T_FALL), True)], loc(T_FALL + timedelta(minutes=30)), 1800, True),
    ("dst_spring_fwd", [(loc(T_SPRING), True)], loc(T_SPRING + timedelta(minutes=30)), 1800, True),
    ("dst_fall_back_mid", [(loc(T_FALL), False), (loc(T_FALL + timedelta(minutes=10)), True),
                           (loc(T_FALL + timedelta(minutes=20)), False)],
     loc(T_FALL + timedelta(minutes=30)), 1800, True),
    ("plain", [(utc(2026, 1, 15, 3, 0), True)], utc(2026, 1, 15, 3, 30), 1800, True),
    ("jump_back_1h", [(utc(2026, 1, 15, 3, 0), True)], utc(2026, 1, 15, 2, 0), 0, True),
    ("jump_fwd_5h", [(utc(2026, 1, 15, 3, 0), False)], utc(2026, 1, 15, 8, 0), 18000, True),
    ("unavailable_mid", [(utc(2026, 1, 15, 3, 0), False), (utc(2026, 1, 15, 3, 10), None),
                         (utc(2026, 1, 15, 3, 20), False)], utc(2026, 1, 15, 3, 30), 1800, False),
    ("naive_aware_mix", [(datetime(2026, 1, 15, 3, 0), True)], utc(2026, 1, 15, 3, 30), 0, True),
    ("future_stamp_then_now", [(utc(2026, 1, 15, 5, 0), True), (utc(2026, 1, 15, 3, 0), True)],
     utc(2026, 1, 15, 3, 30), 0, True),
]

patches = [mock.patch.object(D.dt_util, "as_utc", lambda d: d)] if PERTURB else []
for p in patches:
    p.start()
bad = 0
try:
    for name, obs, close_at, true_s, exp_obs in cases:
        w = D.DefrostWindow()
        for stamp, flag in obs:
            w.observe(stamp, flag)
        r = w.close(close_at)
        wrong = (abs(r.seconds - true_s) > 1.0 or not 0.0 <= r.duty <= 1.0
                 or (r.observed and not exp_obs))
        bad += int(wrong)
        print(f"# {name}: seconds={r.seconds:.0f} duty={r.duty:.3f} observed={r.observed} "
              f"events={r.events} {'BAD' if wrong else 'ok'}")
finally:
    for p in reversed(patches):
        p.stop()
print(f"MODE perturb={PERTURB} cases={len(cases)}")
print(f"RESULT bad={bad} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
