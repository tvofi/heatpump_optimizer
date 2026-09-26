#!/usr/bin/env python3
"""D9 verify-v1 (round 9), finding D9-s2-02: the nightly replay cost budget
against a doubling of the coordinator cycle's loop-thread work, measured
PAIRED -- the uninjected and injected cycle ratios come from ONE replay, the
same reference solves and the same cycles, so box contention cannot move one
arm against the other (the finder's harness replays each arm in its own
interpreter at a different moment).

Metric: tests/replay.py:cost_offenders on (a) the replay's own cpu_ratio with
the loop-thread work of every cycle spun once more (scale 1 = loop x2) and
(b) that same ratio less the spun CPU (the uninjected cycle), both divided by
the same median reference solve. Loop-thread work per cycle = thread CPU of
HeatPumpOptimizerCoordinator._async_update_data minus the thread CPU of its
hass.async_add_executor_job jobs, plus the thread CPU of replay.sweep (one read
of every entity), each hooked on the production/gate symbol.
Count key: the offender list the gate's own cost_offenders returns.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/verify-v1/loop_blind_paired.py [--scale 1] [--whole]
Perturbation: --scale 4 (loop x5) -> injected offenders UP 0 -> 1.
Positive control: --whole spins the WHOLE update's thread CPU plus the sweep
(replay's own "cpu" injection shape) -> injected offenders 1.
Null control: --scale 0 -> injected == uninjected, offenders 0.
Expected: scale 1: uninjected 0, injected 0, injected/uninjected ~1.15
(+-0.05); counts exact. Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
for _p in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(ROOT / _p))
FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"
os.environ.setdefault("HASTUB_TZ", json.loads(FIXTURE.read_text()).get("time_zone") or "UTC")


def spin(seconds: float) -> None:
    until = time.process_time() + seconds
    while time.process_time() < until:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--whole", action="store_true")
    args = ap.parse_args()

    import stress  # noqa: F401  (pins BLAS before numpy)
    import replay
    from harness import FakeHass
    from heatpump_optimizer import coordinator as cm

    st = {"idx": -1, "exec": 0.0, "depth": 0, "spins": {}, "loop": {}, "cycle_thread": {}}

    real_exec = FakeHass.async_add_executor_job

    async def add_exec(self, func, *a):
        if st["depth"]:
            return await real_exec(self, func, *a)
        st["depth"] += 1
        t0 = time.thread_time()
        try:
            return await real_exec(self, func, *a)
        finally:
            st["depth"] -= 1
            st["exec"] += time.thread_time() - t0

    FakeHass.async_add_executor_job = add_exec

    real_upd = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def upd(self):
        st["idx"] += 1
        st["exec"] = 0.0
        t0 = time.thread_time()
        out = await real_upd(self)
        whole = time.thread_time() - t0
        loop = whole - st["exec"]
        st["loop"][st["idx"]] = loop
        st["cycle_thread"][st["idx"]] = whole
        s = args.scale * (whole if args.whole else loop)
        t1 = time.process_time()
        spin(s)
        st["spins"][st["idx"]] = time.process_time() - t1
        return out

    cm.HeatPumpOptimizerCoordinator._async_update_data = upd

    real_sweep = replay.sweep

    def sweep(*a, **k):
        t0 = time.thread_time()
        out = real_sweep(*a, **k)
        d = time.thread_time() - t0
        t1 = time.process_time()
        spin(args.scale * d)
        st["spins"][st["idx"]] = st["spins"].get(st["idx"], 0.0) + time.process_time() - t1
        st["loop"][st["idx"]] = st["loop"].get(st["idx"], 0.0) + d
        return out

    replay.sweep = sweep

    p0, t0 = time.process_time(), time.thread_time()
    out = replay.run_fixture(FIXTURE, None, None)
    pc, tc = time.process_time() - p0, time.thread_time() - t0

    ref = out["cost"]["ref_ms"]
    timed = [i for i in st["spins"] if i > 0 and i % 2 == 0]
    mean_spin_ms = sum(st["spins"][i] for i in timed) / len(timed) * 1000.0
    inj = out["cost"]["cpu_ratio"]
    base = inj - mean_spin_ms / ref
    budget = replay.COST_BUDGETS["synthetic-dhw-only.json"]
    off_inj = [o for o in replay.cost_offenders({"cpu_ratio": inj, "peak_kib": out["cost"]["peak_kib"]}, budget)
               if o.startswith("cpu_ratio")]
    off_base = [o for o in replay.cost_offenders({"cpu_ratio": base, "peak_kib": out["cost"]["peak_kib"]}, budget)
                if o.startswith("cpu_ratio")]
    loop_ms = sum(st["loop"][i] for i in timed) / len(timed) * 1000.0
    tag = ("whole" if args.whole else "loop") + f"x{args.scale + 1:g}"
    print(f"# offenders injected={off_inj} uninjected={off_base}")
    print(f"RESULT timed_cycles={len(timed)} count")
    print(f"RESULT uninjected.cycle_cpu_ratio={base:.4f} ref_solves")
    print(f"RESULT uninjected.offenders={len(off_base)} count")
    print(f"RESULT {tag}.cycle_cpu_ratio={inj:.4f} ref_solves")
    print(f"RESULT {tag}.offenders={len(off_inj)} count")
    print(f"RESULT {tag}.over_uninjected={inj / base:.4f} ratio")
    print(f"RESULT budget_cpu_ratio={budget['cpu_ratio']:.4f} ref_solves")
    print(f"RESULT budget_over_uninjected={budget['cpu_ratio'] / base:.4f} ratio")
    print(f"RESULT loop_ms_per_cycle={loop_ms:.3f} ms_cpu (provisional)")
    print(f"RESULT loop_share_of_uninjected_cycle={loop_ms / (base * ref):.4f} ratio")
    print(f"RESULT ref_ms={ref:.3f} ms_cpu (provisional)")
    print(f"RESULT thread_factor={pc / tc:.4f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = -1
    print(f"RESULT swapins={sw}")
    print(f"# machine: {platform.machine()} {os.cpu_count()}cpu py{platform.python_version()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
