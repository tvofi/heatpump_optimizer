"""V2 (independent) check of D9-s1-03: sysid's two-state fit on the event loop.

Metric (own definition): the longest gap between ticks of a 1 ms heartbeat
task on a REAL asyncio event loop (not FakeHass) while a coroutine drives a
full production-sequence SystemIdentification experiment by calling
SystemIdentification.step synchronously once per cycle, as
coordinator.async_run_optimization -> _run_system_identification does
(no await, no executor). Reported in ms (wall, provisional) and over the
median wall of tests/stress.py:reference_solve taken in the same process;
plus the thread CPU of the identify_slab call alone (hooked) and the number
of samples it fitted.
Count key: time.perf_counter() between heartbeat wake-ups; time.thread_time()
around the production identify_slab.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v2/v2_sysid_heartbeat.py [--cadence-min 30] [--no-fit]
Perturbation: --no-fit replaces identify_slab by a stub refusal: the max gap
must fall to the heartbeat's own jitter (~1-2 ms); --cadence-min 5 raises it.
Expected (1936d5ca, this box, provisional): max gap tens of ms at 30 min.
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import asyncio
import statistics
import time
from datetime import datetime, timedelta, timezone

import numpy as np

import stress
from heatpump_optimizer.sysid import SysIdConfig, SysIdResult, SystemIdentification, PHASE_DONE
from heatpump_optimizer.thermal_model import ThermalParameters

FIT = {"cpu": [], "n": []}
ORIG_FIT = SystemIdentification.identify_slab


def hooked_fit(self):
    t0 = time.thread_time()
    try:
        return ORIG_FIT(self)
    finally:
        FIT["cpu"].append((time.thread_time() - t0) * 1000)
        FIT["n"].append(len(self.samples))


async def experiment(cadence_min, seed, stop):
    plant = ThermalParameters()
    rng = np.random.default_rng(1000 + seed)
    exp = SystemIdentification(SysIdConfig(enabled=True))
    t = datetime(2026, 1, 20, 22, 30, tzinfo=timezone.utc)
    assert exp.arm(t, plant=plant), exp.result.reason
    ua = plant.heat_loss_coefficient * plant.house_heat_loss_scale
    cr, cs, k = plant.room_thermal_mass, plant.slab_thermal_mass, plant.slab_heat_transfer
    room, slab, out = 20.8, 21.2, -3.0
    horizon = np.linspace(0.4, 1.8, 96)
    for _ in range(int(10 * 60 / cadence_min)):
        # synchronous call from a coroutine, exactly as the coordinator does
        p = exp.step(now=t, room_temp=room + rng.normal(0, 0.02), outdoor_temp=out,
                     price=0.5, price_horizon=horizon, learner_samples=6,
                     max_power_kw=plant.max_electrical_power, cop=2.8, plan_power_kw=1.0,
                     house_ua=ua, house_capacity=cr, house_gains=plant.internal_gains,
                     house_slab_mass=cs, house_slab_transfer=k)
        q = (1.0 if p is None else p) * 2.8
        h = cadence_min / 60.0 / 20
        for _s in range(20):
            slab += (q - k * (slab - room)) / cs * h
            room += (k * (slab - room) - ua * (room - out) + plant.internal_gains) / cr * h
        t += timedelta(minutes=cadence_min)
        await asyncio.sleep(0.005)  # the loop runs other work between cycles
        if exp.phase == PHASE_DONE:
            break
    stop.set()
    return exp


async def heartbeat(stop, gaps):
    last = time.perf_counter()
    while not stop.is_set():
        await asyncio.sleep(0.001)
        now = time.perf_counter()
        gaps.append((now - last) * 1000)
        last = now


async def one(cadence_min, seed):
    stop, gaps = asyncio.Event(), []
    hb = asyncio.create_task(heartbeat(stop, gaps))
    exp = await experiment(cadence_min, seed, stop)
    await hb
    return exp, gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cadence-min", type=int, default=30)
    ap.add_argument("--no-fit", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()
    ref_wall = []
    for _ in range(5):
        w0 = time.perf_counter(); stress.reference_solve(); ref_wall.append((time.perf_counter() - w0) * 1000)
    ref = statistics.median(ref_wall)
    SystemIdentification.identify_slab = (
        (lambda self: SysIdResult(completed=False, reason="stub")) if args.no_fit else hooked_fit)
    tag = f"cad{args.cadence_min}" + ("_nofit" if args.no_fit else "")
    maxgaps, p99 = [], []
    try:
        for seed in range(args.seeds):
            exp, gaps = asyncio.run(one(args.cadence_min, seed))
            maxgaps.append(max(gaps)); p99.append(float(np.percentile(gaps, 99)))
            V.result(f"{tag}.seed{seed}.phase", exp.phase)
            V.result(f"{tag}.seed{seed}.completed", bool(exp.result and exp.result.completed))
            V.result(f"{tag}.seed{seed}.max_heartbeat_gap_ms", round(max(gaps), 2), "ms wall (provisional)")
    finally:
        SystemIdentification.identify_slab = ORIG_FIT
    V.result(f"{tag}.max_gap_median_over_seeds_ms", round(statistics.median(maxgaps), 2), "ms wall (provisional)")
    V.result(f"{tag}.p99_gap_median_ms", round(statistics.median(p99), 2), "ms wall (provisional)")
    V.result(f"{tag}.max_gap_over_reference_solve_wall", round(statistics.median(maxgaps) / ref, 3), "ratio")
    if FIT["cpu"]:
        V.result(f"{tag}.identify_slab_calls", len(FIT["cpu"]), "count")
        V.result(f"{tag}.identify_slab_thread_ms_median", round(statistics.median(FIT["cpu"]), 2), "ms (provisional)")
        V.result(f"{tag}.identify_slab_samples", int(statistics.median(FIT["n"])), "count")
    V.result("reference_solve_wall_ms", round(ref, 2), "ms (provisional)")
    V.trailer()


if __name__ == "__main__":
    main()
