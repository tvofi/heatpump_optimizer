"""D9-s1 H6: event-loop CPU of one sysid.SystemIdentification.step call --
the coordinator calls it synchronously inside _async_update_data (on the
loop thread, coordinator.py _run_system_identification), and the call that
ends the relax phase runs the whole two-state fit (_finish -> identify_slab).

Metric: thread CPU of the single most expensive SystemIdentification.step()
call over one production-sequence experiment (armed with a declared plant,
as the coordinator does), in ms and as a multiple of
tests/stress.py:reference_solve; plus which call it was.
Count key: time.thread_time() around the production step() call.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/sysid_loop.py [--cadence-min 5] [--no-fit]
Perturbations: --no-fit swaps SystemIdentification.identify_slab for a stub
returning the refusal result: the max per-call CPU must go DOWN to the
per-sample bookkeeping (~0.1 ms). --cadence-min changes the coordinator
cadence (15 default): more samples, fit CPU UP.
Provisional (CPU ms). Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import time
from datetime import datetime, timedelta, timezone

import numpy as np

import stress
from heatpump_optimizer.sysid import SysIdConfig, SysIdResult, SystemIdentification, PHASE_DONE
from heatpump_optimizer.thermal_model import ThermalParameters


def drive(plant, cadence_min, seed):
    rng = np.random.default_rng(seed)
    exp = SystemIdentification(SysIdConfig(enabled=True))
    night = datetime(2026, 2, 1, 23, 0, tzinfo=timezone.utc)
    cheap = np.linspace(0.5, 2.0, 96)
    assert exp.arm(night, plant=plant), exp.result.reason
    # a simple two-state house near the declared plant
    c_r, c_s = plant.room_thermal_mass, plant.slab_thermal_mass
    ua, k = plant.heat_loss_coefficient * plant.house_heat_loss_scale, plant.slab_heat_transfer
    room, slab, outdoor, cop = 21.0, 21.5, 2.0, 3.0
    when = night
    per_call = []
    dt = cadence_min / 60.0
    for _ in range(int(8 * 60 / cadence_min)):
        t0 = time.thread_time()
        p = exp.step(now=when, room_temp=room + rng.normal(0, 0.03), outdoor_temp=outdoor,
                     price=0.55, price_horizon=cheap, learner_samples=5,
                     max_power_kw=5.0, cop=cop, plan_power_kw=0.8,
                     house_ua=ua, house_capacity=c_r, house_gains=plant.internal_gains,
                     house_slab_mass=c_s, house_slab_transfer=k)
        per_call.append(((time.thread_time() - t0) * 1000, exp.phase))
        q = (p if p is not None else 0.8) * cop
        for _s in range(10):
            h = dt / 10
            slab += (q - k * (slab - room)) / c_s * h
            room += (k * (slab - room) - ua * (room - outdoor) + plant.internal_gains) / c_r * h
        when += timedelta(minutes=cadence_min)
        if exp.phase == PHASE_DONE:
            break
    return exp, per_call


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cadence-min", type=int, default=15)
    ap.add_argument("--no-fit", action="store_true")
    args = ap.parse_args()
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]
    orig = SystemIdentification.identify_slab
    if args.no_fit:
        SystemIdentification.identify_slab = lambda self: SysIdResult(completed=False, reason="stub")
    tag = f"cad{args.cadence_min}" + ("_nofit" if args.no_fit else "")
    worst = []
    tf = 1.0
    try:
        for name, plant in (("single_zone_default", ThermalParameters()),):
            for seed in range(5):
                with C.Clock() as clk:
                    exp, per_call = drive(plant, args.cadence_min, seed)
                tf = max(tf, clk.thread_factor)
                mx = max(per_call, key=lambda x: x[0])
                worst.append(mx[0])
                C.result(f"{tag}.{name}.seed{seed}.phase_final", exp.phase)
                C.result(f"{tag}.{name}.seed{seed}.samples", len(exp.samples), "count")
                C.result(f"{tag}.{name}.seed{seed}.max_step_call_ms", round(mx[0], 2), f"ms (provisional; phase after call={mx[1]})")
                C.result(f"{tag}.{name}.seed{seed}.completed", exp.result.completed if exp.result else None)
                C.result(f"{tag}.{name}.seed{seed}.reason", (exp.result.reason if exp.result else "")[:60].replace(" ", "_"))
                C.result(f"{tag}.{name}.seed{seed}.median_step_call_ms", round(float(np.median([c for c, _ in per_call])), 3), "ms (provisional)")
    finally:
        SystemIdentification.identify_slab = orig
    C.result(f"{tag}.max_step_call_ms_median_over_seeds", round(float(np.median(worst)), 2), "ms (provisional)")
    C.result(f"{tag}.max_step_call_over_reference", round(float(np.median(worst)) / ref, 2), "x reference_solve (ratio)")
    C.result("reference_solve_cpu_ms", round(ref, 2), "ms (provisional)")
    C.trailer(tf)


if __name__ == "__main__":
    main()
