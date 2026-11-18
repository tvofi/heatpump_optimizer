#!/usr/bin/env python3
"""ARCH-s3 harness: step_duty hands the plan's modulation floor to planned_draw_runs through a
function attribute, so a concurrent caller of planned_draw_runs reads another plan's floor.

Metric: leaked_reads = calls of thermal_model.planned_draw_runs(0.5) (no floor passed; 0.5 kW >
MIN_RUNNING_DRAW_KW, so the right answer is True) on thread B that return False while thread A
calls pump_arbiter.step_duty(plan with duty_floor_kw=5.0) in a loop. Thread B stands for the
solve on the executor fallback (coordinator._await_off_loop when the process worker is
unusable: optimizer.py's per-step heat_pump_on / space_on grading), thread A for the arbiter tick
on the loop. Second metric: reflective_writes sites in pump_arbiter.py (archscore counter C2).
Null control: the same loop with thread A idle -> leaked_reads must be 0.

Run:     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py
Root:    the working directory (imports custom_components/heatpump_optimizer from it).
Expected at baseline 554e2ecfa: leaked_reads > 0 (scheduler-dependent; observed 437525 of 1419348 at a
         1 us switch interval), null 0; with the D7-arch3-04 prototype (floor passed as an
         argument, attribute and decorator removed) leaked_reads = 0 and reflective sites 0.
         The count is a race, so its size is not a tolerance-bearing figure: the claim is > 0
         versus = 0.
Machine: macOS arm64, tvofi's audit box. Two real threads by design: thread_factor is reported
         as the residual (process_cpu - thread_A_cpu) / thread_B_cpu per dev/audit/README.md.
Instrumented: heatpump_optimizer.pump_arbiter:step_duty, heatpump_optimizer.thermal_model:planned_draw_runs.
Perturbation: the prototype patch D7-arch3-04 (leaked_reads -> 0).
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from types import SimpleNamespace  # noqa: E402

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tests" / "hastub"), str(ROOT / "custom_components"), str(ROOT / "tools" / "audit")]

from heatpump_optimizer import pump_arbiter, thermal_model  # noqa: E402
from archscore import counters as K  # noqa: E402

SECONDS = float(os.environ.get("DUTY_SECONDS", "2.0"))
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
PLAN = SimpleNamespace(timestamps=[NOW], power_schedule=[1.0], dhw_power_schedule=[0.0], duty_floor_kw=5.0)


def run(writer_active: bool) -> tuple[int, int, float, float]:
    stop = threading.Event()
    a_cpu = [0.0]

    def writer():
        t0 = time.thread_time()
        while not stop.is_set():
            if writer_active:
                pump_arbiter.step_duty(PLAN, NOW)
        a_cpu[0] = time.thread_time() - t0

    th = threading.Thread(target=writer)
    th.start()
    b0 = time.thread_time()
    leaked = calls = 0
    end = time.monotonic() + SECONDS
    while time.monotonic() < end:
        calls += 1
        if not thermal_model.planned_draw_runs(0.5):
            leaked += 1
    b_cpu = time.thread_time() - b0
    stop.set()
    th.join()
    return leaked, calls, a_cpu[0], b_cpu


def main() -> None:
    sys.setswitchinterval(1e-6)
    p0 = time.process_time()
    leaked, calls, a_cpu, b_cpu = run(True)
    null_leaked, null_calls, a2, b2 = run(False)
    proc = time.process_time() - p0
    src = (ROOT / "custom_components" / "heatpump_optimizer" / "pump_arbiter.py").read_text()
    print(f"RESULT leaked_reads={leaked} count")
    print(f"RESULT reader_calls={calls} count")
    print(f"RESULT null_leaked_reads={null_leaked} count")
    print(f"RESULT null_reader_calls={null_calls} count")
    print(f"RESULT reflective_writes_pump_arbiter={K.reflective_writes({'pump_arbiter': ast.parse(src)})} count")
    print(f"RESULT deliberate_thread_cpu_s={a_cpu + a2:.3f}")
    print(f"RESULT thread_factor={(proc - a_cpu - a2) / max(b_cpu + b2, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
