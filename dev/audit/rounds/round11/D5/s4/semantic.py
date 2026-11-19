#!/usr/bin/env python3
"""D5-s4 M4 (C1): executed checks that named docstrings/comments in the seat's cells are true of the
code they sit on -- each check drives the production function, never reads another comment.
Metric: unit claims that the executed behaviour contradicts (failed); checks = claims driven.
Run:  PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s4/semantic.py [--perturb]
  --perturb swaps pump_schedule.plan_commands_heat's empty-plan answer to (False, False) in memory:
  failed goes up by 1 (the ``no plan yet -- the rails treat unknown as ON`` comment).
Expected at 92d38ecb: RESULT checks=16 failed=0 (exact). Machine: box B11. No timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import logging, sys, time
sys.path.insert(0, ".")
from datetime import datetime, timedelta, timezone  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import (log_latch, plan_slots, plan_step, pump_schedule,  # noqa: E402
                                                 silent_mode)
from custom_components.heatpump_optimizer.const import CAPACITY_FLOOR_FRACTION  # noqa: E402
from custom_components.heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402

if "--perturb" in sys.argv:
    _orig = pump_schedule.plan_commands_heat
    pump_schedule.plan_commands_heat = lambda s, i: (False, False) if not s else _orig(s, i)


class Rec(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG); self.levels = []
    def emit(self, r):
        self.levels.append(r.levelname)


rec = Rec(); log_latch._LOGGER.addHandler(rec); log_latch._LOGGER.setLevel(logging.DEBUG)
log_latch._LOGGER.propagate = False


class Owner:
    pass


C = []
o = Owner()
for args in ((True, "x"), (True, "x"), (False,)):
    log_latch.log_held(o, "k", *args)
C.append(("log_held: WARNING at start, DEBUG while held, INFO on clear", rec.levels == ["WARNING", "DEBUG", "INFO"]))
rec.levels.clear(); log_latch.log_held(None, "k", True, "x"); log_latch.log_held(None, "k", True, "x")
C.append(("log_held: owner None logs every call", rec.levels == ["WARNING", "WARNING"]))
rec.levels.clear(); log_latch.log_held(Owner(), "k", True, "x", exc_info=ValueError("e"))
C.append(("log_held: exc_info makes the start an ERROR", rec.levels == ["ERROR"]))
o2 = Owner(); log_latch.log_held(o2, "k", True, "x"); log_latch.forget_held(o2); rec.levels.clear()
log_latch.log_held(o2, "k", True, "x")
C.append(("forget_held: each condition warns afresh", rec.levels == ["WARNING"]))
C.append(("log_held returns active", log_latch.log_held(Owner(), "k", True, "x") is True
          and log_latch.log_held(Owner(), "k", False) is False))

tz = timezone(timedelta(hours=1))
t = datetime(2026, 10, 25, 2, 37, 41, 5, tzinfo=tz, fold=1)
s = plan_step.plan_step_start(t)
C.append(("plan_step_start: floored to the 15-min grid, fold and tzinfo carried",
          (s.minute, s.second, s.microsecond, s.fold, s.tzinfo) == (30, 0, 0, 1, tz)))
C.append(("PLAN_STEP_HOURS is one plan step in hours", plan_step.PLAN_STEP_HOURS * 60 == plan_step.PLAN_STEP_MINUTES))

st = datetime(2026, 1, 5, 20, 0, tzinfo=timezone.utc)
w = parse_windows("22:00-06:00")
C.append(("silent caps: fraction 1.0 returns None", silent_mode.caps(st, 96, 0.25, w, 1.0, 5.0) is None))
C.append(("silent caps: no window returns None", silent_mode.caps(st, 96, 0.25, [], 0.5, 5.0) is None))
cp = silent_mode.caps(st, 96, 0.25, w, 0.01, 5.0)
C.append(("silent caps: floored at CAPACITY_FLOOR_FRACTION, nameplate outside",
          cp is not None and abs(cp.min() - CAPACITY_FLOOR_FRACTION * 5.0) < 1e-12 and cp.max() == 5.0))
extra = np.full(96, 4.0)
C.append(("silent compose: same object when silent mode caps nothing",
          silent_mode.compose(extra, {}, st, 96, 0.25, 5.0) is extra))

C.append(("vvc: no windows -> run", pump_schedule.vvc_should_run(3.0, [], 30)[0] is True))
C.append(("vvc: within the lead before a window opens -> run",
          pump_schedule.vvc_should_run(21.75, w, 30)[0] is True and pump_schedule.vvc_should_run(21.0, w, 30)[0] is False))
C.append(("space pump: freezing outside forces ON", pump_schedule.space_pump_should_run(
    plan_heat_now=False, plan_heat_next=False, curve_driven=False, zone_temps=[25.0], floor_temp=18.0,
    outdoor_temp=-1.0)[0] is True))
C.append(("plan_commands_heat: no plan yet, the rails treat unknown as ON",
          pump_schedule.plan_commands_heat([], 0) == (True, True)))
ts = [datetime(2026, 1, 1, 0, 15 * i) for i in range(4)]
sl = plan_slots.plan_slots(ts, [2, 2, 0, 0], [1, 1, 1, 1], 0.25, other_powers=[0, 0, 0, 0])
C.append(("plan_slots: zero-overlap slots carry no shared_kwh key", len(sl) == 1 and "shared_kwh" not in sl[0]))

failed = 0
for what, ok in C:
    print(("ok   " if ok else "FAIL ") + what); failed += not ok
print(f"RESULT checks={len(C)} count")
print(f"RESULT failed={failed} count")
print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')), 'na'))
