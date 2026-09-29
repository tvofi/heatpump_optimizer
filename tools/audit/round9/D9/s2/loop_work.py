#!/usr/bin/env python3
"""D9-s2 (round 9, D9.M1) -- loop-thread work per coordinator cycle.

METRIC (brief's definition): time.thread_time() on the loop thread across one
cycle, excluding the executor: [HeatPumpOptimizerCoordinator._async_update_data
thread CPU - CPU inside hass.async_add_executor_job jobs] + the CPU of one read
of every published entity's state and attributes (tests/replay.py:sweep, which
is what one async_write_ha_state of every entity evaluates). Reported in ms and
as a ratio to tests/stress.py:reference_solve (the ruler; median of 7).
Also, contention-immune: ThermalModel.simulate_step calls made on the loop
thread (outside any executor job) per cycle, split by who made them, and the
calls/CPU of topology.rank_sensor_advisor (the #1269 sensor_advisor attribute,
computed inside _PlanSensorBase.extra_state_attributes) per entity read.
Count key: calls the production path makes (hooked at the class/module symbol).
DRIVER: tests/replay.py:run_fixture over tests/replay/synthetic-dhw-only.json
(48 real cycles; the in-process worker makes the solve an executor job).
Only even cycles >= 2 are timed (replay traces cycle 0, tracemallocs odd ones).
COMMAND (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D9/s2/loop_work.py
PERTURBATIONS:
  --advisor-steps 1   (in memory: topology._ADVISOR_REPLAY_STEPS 48 -> 1)
      -> loop_simulate_steps_per_cycle DOWN (to ~1/48 of the advisor share),
         advisor_share_of_loop DOWN.
  --options '{"lower_floor_temp_entity": "sensor.x", "floor_return_temp_entity":
      "sensor.y", "buffer_tank_temp_entity": "sensor.z", "outdoor_temp_entity":
      "sensor.outdoor_temperature"}'  (config: every advisor candidate
      configured, rank returns None) -> advisor counts TO_ZERO.
EXPECTED (baseline, this box): loop_simulate_steps_per_read=384 exact (2 plan
  sensors x 2 priced lanes x 2 edges x 48 steps), advisor_calls_per_read=2
  exact; timings provisional (+-25 %).
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: round-9 box B5
    (Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, numpy 2.4.6 / scipy 1.17.1, Python 3.14.0rc2).
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "tools" / "audit" / "round9" / "D9" / "s2"))
import _rig  # noqa: E402

STATE = {"phase": None, "steps": {"update": 0, "sweep": 0}, "adv_calls": 0,
         "adv_cpu": 0.0, "adv_steps": 0, "in_adv": 0}


def install_hooks() -> None:
    from heatpump_optimizer import thermal_model as tm
    from heatpump_optimizer import topology

    real_step = tm.ThermalModel.simulate_step

    def step(self, *a, **k):
        if _rig.PROBE.exec_depth == 0 and STATE["phase"]:
            STATE["steps"][STATE["phase"]] += 1
            if STATE["in_adv"]:
                STATE["adv_steps"] += 1
        return real_step(self, *a, **k)

    tm.ThermalModel.simulate_step = step

    real_rank = topology.rank_sensor_advisor

    def rank(*a, **k):
        STATE["adv_calls"] += 1
        STATE["in_adv"] += 1
        t0 = time.thread_time()
        try:
            return real_rank(*a, **k)
        finally:
            STATE["adv_cpu"] += time.thread_time() - t0
            STATE["in_adv"] -= 1

    topology.rank_sensor_advisor = rank


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", default="{}")
    ap.add_argument("--advisor-steps", type=int, default=None)
    args = ap.parse_args()

    if args.advisor_steps is not None:
        from heatpump_optimizer import topology
        topology._ADVISOR_REPLAY_STEPS = args.advisor_steps

    import replay

    per_cycle: list[dict] = []

    def wrap_update(real):
        async def upd(self):
            STATE["phase"] = "update"
            try:
                return await real(self)
            finally:
                STATE["phase"] = None
        return upd

    real_sweep = replay.sweep

    def sweep(entities, action, errors, t):
        s0 = dict(STATE["steps"])
        a0, ac0, as0 = STATE["adv_calls"], STATE["adv_cpu"], STATE["adv_steps"]
        STATE["phase"] = "sweep"
        t0 = time.thread_time()
        try:
            return real_sweep(entities, action, errors, t)
        finally:
            dt = time.thread_time() - t0
            STATE["phase"] = None
            c = _rig.PROBE.cycles[-1]
            per_cycle.append({
                "loop_update_cpu": c["thread_cpu"] - c["exec_cpu"],
                "exec_cpu": c["exec_cpu"],
                "sweep_cpu": dt,
                "listener_updates": c["listener_updates"],
                "sweep_steps": STATE["steps"]["sweep"] - s0["sweep"],
                "adv_calls": STATE["adv_calls"] - a0,
                "adv_cpu": STATE["adv_cpu"] - ac0,
                "adv_steps": STATE["adv_steps"] - as0,
            })

    _rig.install(extra_update_wrap=wrap_update)
    install_hooks()
    replay.sweep = sweep  # _rig.run wraps this again; both run
    from stress import reference_solve

    p0, t0 = time.process_time(), time.thread_time()
    reference_solve()
    refs = [reference_solve()[1] for _ in range(4)]
    out = _rig.run(1, options=json.loads(args.options))
    refs += [reference_solve()[1] for _ in range(3)]
    pc, tc = time.process_time() - p0, time.thread_time() - t0
    ref = statistics.median(refs)

    timed = [c for i, c in enumerate(per_cycle) if i >= 2 and i % 2 == 0]
    n = len(per_cycle)
    upd_steps = STATE["steps"]["update"]
    mean = lambda key: statistics.mean(c[key] for c in timed) * 1000.0  # noqa: E731
    loop_upd, sweep_ms, exec_ms, adv_ms = (mean("loop_update_cpu"), mean("sweep_cpu"),
                                           mean("exec_cpu"), mean("adv_cpu"))
    writes = statistics.mean(c["listener_updates"] for c in per_cycle) + 1.0
    loop_real = loop_upd + writes * sweep_ms
    adv_real = writes * adv_ms
    print(f"cycles={n} timed={len(timed)} replay_counts={out['counts']} ref_ms={ref:.2f}")
    print(f"RESULT cycles={n} count")
    print(f"RESULT loop_update_simulate_steps_per_cycle={upd_steps / n:.2f} count")
    print(f"RESULT loop_simulate_steps_per_read={sum(c['sweep_steps'] for c in per_cycle) / n:.2f} count")
    print(f"RESULT advisor_calls_per_read={sum(c['adv_calls'] for c in per_cycle) / n:.2f} count")
    print(f"RESULT advisor_simulate_steps_per_read={sum(c['adv_steps'] for c in per_cycle) / n:.2f} count")
    print(f"RESULT entity_writes_per_cycle={writes:.2f} count "
          f"(listener updates inside the update + the refresh's own one)")
    print(f"RESULT ref_solve_ms={ref:.3f} ms_cpu")
    print(f"RESULT loop_update_cpu_ms={loop_upd:.3f} ms_cpu")
    print(f"RESULT entity_read_cpu_ms={sweep_ms:.3f} ms_cpu")
    print(f"RESULT advisor_cpu_per_read_ms={adv_ms:.3f} ms_cpu")
    print(f"RESULT executor_cpu_ms={exec_ms:.3f} ms_cpu")
    print(f"RESULT loop_cpu_per_real_cycle_ms={loop_real:.3f} ms_cpu "
          f"(update loop part + writes x one read of every entity)")
    print(f"RESULT loop_cpu_per_real_cycle_ratio={loop_real / ref:.4f} ref_solves")
    print(f"RESULT advisor_share_of_loop={adv_real / loop_real:.4f} ratio")
    print(f"RESULT advisor_share_of_entity_read={adv_ms / sweep_ms:.4f} ratio")
    print(f"RESULT loop_share_of_cycle={loop_real / (loop_real + exec_ms):.4f} ratio")
    _rig.tail(pc / tc if tc else float("nan"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
