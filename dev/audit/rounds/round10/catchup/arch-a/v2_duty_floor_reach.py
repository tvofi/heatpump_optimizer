#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, D7-arch3-04 / D7-s3-54): who reads the step_duty floor
channel, and on which thread, in the code the integration actually runs.

The finder's race needs a reader of ``planned_draw_runs`` with no floor argument on a thread other
than the event loop's while ``step_duty`` (loop) holds the attribute. The only model work that leaves
the loop is the off-loop jobs (optimize_in_process on the executor fallback, sysid step, sensor
ranking). This harness wraps planned_draw_runs in every importing module and runs (a) every golden
optimizer scenario through golden.capture, which calls HeatPumpOptimizer.optimize as the off-loop
job does, and (b) one step_duty call as the positive control.

Metric: in_optimize_floorless -- planned_draw_runs calls with modulation_floor=None while a frame
          named ``optimize`` is on the stack (what an executor-fallback solve would read);
        loop_floorless -- such calls outside optimize (the coordinator's own loop readers);
        explicit -- calls passing a floor (immune to the channel).
        Then the finder's race re-run at the DEFAULT GIL switch interval (5 ms) instead of 1 us:
        default_switch_leaked / default_switch_reads.
Count key: one call of the wrapped function.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_duty_floor_reach.py
          run from the root of the tree under test.
Null control: the counters are live -- one step_duty call (the loop reader) must read loop_floorless=2,
          and optimize_calls > 0 shows the optimizer arm ran solves.
Perturbation: D7-arch3-04 patch: the channel is gone; default_switch_leaked must read 0.
Expected (d749c986d): in_optimize_floorless 0, loop_floorless > 0, default_switch_leaked >= 0
          (reported, not asserted).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from types import SimpleNamespace  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from heatpump_optimizer import thermal_model  # noqa: E402

COUNTS = {"in_optimize_floorless": 0, "loop_floorless": 0, "explicit": 0, "off_main_thread": 0}
_real = thermal_model.planned_draw_runs


def _wrapped(space_kw, dhw_kw=0.0, *, modulation_floor=None):
    if threading.current_thread() is not threading.main_thread():
        COUNTS["off_main_thread"] += 1
    if modulation_floor is not None:
        COUNTS["explicit"] += 1
    else:
        f = sys._getframe(1)
        inside = False
        while f is not None:
            if f.f_code.co_name in ("optimize", "optimize_in_process"):
                inside = True
                break
            f = f.f_back
        COUNTS["in_optimize_floorless" if inside else "loop_floorless"] += 1
    return _real(space_kw, dhw_kw, modulation_floor=modulation_floor)


# the attribute channel lives on the function object; keep it on the real one
def install() -> int:
    n = 0
    for name, mod in list(sys.modules.items()):
        if name.startswith("heatpump_optimizer") and getattr(mod, "planned_draw_runs", None) is _real:
            setattr(mod, "planned_draw_runs", _wrapped)
            n += 1
    return n


def race_default_switch(seconds: float = 2.0) -> tuple[int, int]:
    from heatpump_optimizer import pump_arbiter
    now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    plan = SimpleNamespace(timestamps=[now - timedelta(minutes=5)], power_schedule=[1.0],
                           dhw_power_schedule=[0.0], duty_floor_kw=5.0)
    stop = time.monotonic() + seconds
    reads = leaked = 0

    def writer():
        while time.monotonic() < stop:
            pump_arbiter.step_duty(plan, now)

    t = threading.Thread(target=writer)
    t.start()
    while time.monotonic() < stop:
        reads += 1
        if not _real(0.5):
            leaked += 1
    t.join()
    return leaked, reads


def main() -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    import golden  # noqa: E402
    from heatpump_optimizer import coordinator, optimizer, pump_arbiter  # noqa: F401,E402
    installed = install()
    _orig_opt = optimizer.HeatPumpOptimizer.optimize

    def _count_opt(self, *a, **k):
        COUNTS["optimize_calls"] = COUNTS.get("optimize_calls", 0) + 1
        return _orig_opt(self, *a, **k)

    optimizer.HeatPumpOptimizer.optimize = _count_opt
    for name, spec in golden.SCENARIOS.items():
        try:
            golden.capture(name, spec)
        except Exception as err:  # a scenario needing more setup is reported, not fatal
            print(f"NOTE scenario {name} skipped: {type(err).__name__}")
    opt_floorless = COUNTS["in_optimize_floorless"]
    # Positive control: the arbiter's own loop reader must register as a floorless call.
    from types import SimpleNamespace as _NS
    _now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    pump_arbiter.step_duty(_NS(timestamps=[_now], power_schedule=[1.0], dhw_power_schedule=[0.0],
                               duty_floor_kw=5.0), _now)
    print(f"RESULT wrapped_modules={installed} count")
    print(f"RESULT optimizer_scenarios={len(golden.SCENARIOS)} count")
    print(f"RESULT in_optimize_floorless={opt_floorless} count (after optimizer arm); "
          f"{COUNTS['in_optimize_floorless']} after control")
    print(f"RESULT optimize_calls={COUNTS.get('optimize_calls', 0)} count")
    print(f"RESULT loop_floorless={COUNTS['loop_floorless']} count")
    print(f"RESULT explicit={COUNTS['explicit']} count")
    print(f"RESULT off_main_thread={COUNTS['off_main_thread']} count")
    print(f"RESULT switch_interval={sys.getswitchinterval()} s")
    for name, mod in list(sys.modules.items()):  # the race needs the real function object back
        if name.startswith("heatpump_optimizer") and getattr(mod, "planned_draw_runs", None) is _wrapped:
            setattr(mod, "planned_draw_runs", _real)
    leaked, reads = race_default_switch()
    print(f"RESULT default_switch_leaked={leaked} count")
    print(f"RESULT default_switch_reads={reads} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f} (two threads in the race arm)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
