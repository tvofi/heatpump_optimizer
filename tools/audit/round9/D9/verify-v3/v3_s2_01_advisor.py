"""D9 verify-v3 (round 9, lens V3) for D9-s2-01: thermal-model work done by
topology.rank_sensor_advisor, which both plan sensors' extra_state_attributes
call (sensor._sensor_advisor_attribute) on every state write.

Metric (one line): ThermalModel.simulate_step calls and thread CPU per
rank_sensor_advisor call, direct, on real integration configs; per-cycle loop
CPU = calls x plan sensors x state writes per cycle (writes counted statically:
async_update_listeners in async_run_optimization's entry and finally, plus
DataUpdateCoordinator's own refresh), over tests/stress.py:reference_solve.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s2_01_advisor.py
Instrumented symbols: topology.rank_sensor_advisor, thermal_model.ThermalModel.simulate_step.
Perturbation: --steps 1 (in memory: topology._ADVISOR_REPLAY_STEPS 48 -> 1)
-> steps per call DOWN 48x; null control: every candidate configured -> 0 steps.
Expected: 192 steps/call with indoor configured (2 priced lanes), 288 without;
CPU/call 1-2 ms here (provisional). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse, statistics, time
import stress
from heatpump_optimizer import topology
from heatpump_optimizer.thermal_model import ThermalModel

O_STEP = ThermalModel.simulate_step
N = {"s": 0}


def step(self, *a, **k):
    N["s"] += 1
    return O_STEP(self, *a, **k)


BASE = {"tibber_token": "x", "weather_entity": "weather.home", "target_temperature": 21.0,
        "min_temperature": 17.0, "max_temperature": 23.0}
CONFIGS = {
    "minimal_no_indoor": dict(BASE),
    "indoor_outdoor": {**BASE, "indoor_temp_entity": "sensor.in", "outdoor_temp_entity": "sensor.out"},
    "all_configured_null": {**BASE, "indoor_temp_entity": "sensor.in", "outdoor_temp_entity": "sensor.out",
                            "floor_return_temp_entity": "sensor.a", "lower_floor_temp_entity": "sensor.b",
                            "dhw_temp_entity": "sensor.c", "buffer_tank_temp_entity": "sensor.d"},
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--steps", type=int, default=0)
    a = ap.parse_args()
    if a.steps:
        topology._ADVISOR_REPLAY_STEPS = a.steps
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]
    ThermalModel.simulate_step = step
    hp = [1.2, 1.4, 0.0, 2.2] * 24
    try:
        for name, cfg in CONFIGS.items():
            N["s"] = 0
            out = topology.rank_sensor_advisor(cfg, hp_kw=hp)
            steps = N["s"]
            cpu = []
            for _ in range(15):
                t0 = time.thread_time(); topology.rank_sensor_advisor(cfg, hp_kw=hp); cpu.append(time.thread_time() - t0)
            ms = statistics.median(cpu) * 1000
            t = name + (f"_steps{a.steps}" if a.steps else "")
            V.R(f"{t}.simulate_steps_per_call", steps, "count (exact)")
            V.R(f"{t}.priced_rows", sum(1 for r in (out or {}).get("candidates", []) if r.get("priced")), "count")
            V.R(f"{t}.cpu_per_call_ms", round(ms, 3), "ms (provisional)")
            # 2 plan sensors (space + DHW) x 3 writes per cycle
            V.R(f"{t}.loop_cpu_per_cycle_ms", round(ms * 2 * 3, 2), "ms (provisional; 2 sensors x 3 writes)")
            V.R(f"{t}.per_cycle_over_reference", round(ms * 6 / ref, 3), "x reference_solve")
    finally:
        ThermalModel.simulate_step = O_STEP
    V.R("reference_solve_cpu_ms", round(ref, 2), "ms (provisional)")
    V.trailer()


if __name__ == "__main__":
    main()
