"""D9 verify-v3 (round 9, lens V3) for D9-s1-03: does SystemIdentification.step
stall a REAL asyncio event loop when it finishes the experiment (the fit)?

Metric (one line): the longest gap between 1 ms heartbeat ticks of a task on a
real asyncio loop while a coroutine calls SystemIdentification.step() once per
coordinator cadence (as HeatPumpOptimizerCoordinator._run_system_identification
does synchronously inside _async_update_data), median over 5 seeds; beside it
the thread CPU of the finishing step() call over tests/stress.py:reference_solve.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s1_03_sysid_loop.py [--cadence-min 30] [--no-fit]
Instrumented symbol: sysid.SystemIdentification.step (and identify_slab, stubbed
by --no-fit, the null control: the gap must fall to the ~1-2 ms tick floor).
Perturbation: --cadence-min 10 (the config flow's minimum interval) -> more
samples -> the finishing call's CPU goes UP versus 30 (the default).
Expected: finishing-call CPU 1-3x reference_solve (provisional, +-30 %);
max gap ~ that CPU in ms. Wall numbers are provisional under contention.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse, asyncio, statistics, time
from datetime import datetime, timedelta, timezone
import numpy as np
import stress
from heatpump_optimizer.sysid import SysIdConfig, SysIdResult, SystemIdentification, PHASE_DONE
from heatpump_optimizer.thermal_model import ThermalParameters


async def experiment(plant, cadence, seed):
    rng = np.random.default_rng(100 + seed)
    ex = SystemIdentification(SysIdConfig(enabled=True))
    t = datetime(2026, 1, 15, 22, 30, tzinfo=timezone.utc)
    assert ex.arm(t, plant=plant), ex.result.reason
    ua = plant.heat_loss_coefficient * plant.house_heat_loss_scale
    k, cr, cs = plant.slab_heat_transfer, plant.room_thermal_mass, plant.slab_thermal_mass
    room, slab, out, cop = 21.2, 21.6, 0.0, 2.8
    horizon = np.linspace(0.4, 1.8, 96)
    fin_cpu = 0.0; ncalls = 0
    for _ in range(int(12 * 60 / cadence)):
        t0 = time.thread_time()
        p = ex.step(now=t, room_temp=room + rng.normal(0, 0.02), outdoor_temp=out,
                    price=0.45, price_horizon=horizon, learner_samples=5, max_power_kw=5.0,
                    cop=cop, plan_power_kw=0.7, house_ua=ua, house_capacity=cr,
                    house_gains=plant.internal_gains, house_slab_mass=cs, house_slab_transfer=k)
        c = time.thread_time() - t0; ncalls += 1
        if ex.phase == PHASE_DONE:
            fin_cpu = c
        q = (p if p is not None else 0.7) * cop
        h = cadence / 60.0 / 20
        for _s in range(20):
            slab += (q - k * (slab - room)) / cs * h
            room += (k * (slab - room) - ua * (room - out) + plant.internal_gains) / cr * h
        t += timedelta(minutes=cadence)
        await asyncio.sleep(0.003)  # the rest of the loop's life between cycles
        if ex.phase == PHASE_DONE:
            break
    return ex, fin_cpu, ncalls


async def one(plant, cadence, seed):
    gaps = []; stop = False
    async def beat():
        last = time.perf_counter()
        while not stop:
            await asyncio.sleep(0.001)
            now = time.perf_counter(); gaps.append(now - last); last = now
    hb = asyncio.create_task(beat())
    await asyncio.sleep(0.01)
    ex, fin, n = await experiment(plant, cadence, seed)
    stop = True; await hb
    return ex, fin, n, max(gaps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cadence-min", type=int, default=30)
    ap.add_argument("--no-fit", action="store_true")
    a = ap.parse_args()
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]
    orig = SystemIdentification.identify_slab
    if a.no_fit:
        SystemIdentification.identify_slab = lambda self: SysIdResult(completed=False, reason="stub")
    tag = f"cad{a.cadence_min}" + ("_nofit" if a.no_fit else "")
    fins, gaps = [], []
    try:
        for seed in range(5):
            ex, fin, n, g = asyncio.run(one(ThermalParameters(), a.cadence_min, seed))
            V.R(f"{tag}.seed{seed}.phase", ex.phase)
            V.R(f"{tag}.seed{seed}.completed", bool(ex.result and ex.result.completed))
            V.R(f"{tag}.seed{seed}.samples", len(ex.samples), "count")
            V.R(f"{tag}.seed{seed}.finishing_call_cpu_ms", round(fin * 1000, 2), "ms (provisional)")
            V.R(f"{tag}.seed{seed}.max_heartbeat_gap_ms", round(g * 1000, 2), "ms wall (provisional)")
            fins.append(fin * 1000); gaps.append(g * 1000)
    finally:
        SystemIdentification.identify_slab = orig
    V.R(f"{tag}.finishing_call_over_reference", round(statistics.median(fins) / ref, 2), "x reference_solve (median of 5)")
    V.R(f"{tag}.max_heartbeat_gap_ms_median", round(statistics.median(gaps), 2), "ms wall (provisional)")
    V.R("reference_solve_cpu_ms", round(ref, 2), "ms (provisional)")
    V.trailer()


if __name__ == "__main__":
    main()
