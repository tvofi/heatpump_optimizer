#!/usr/bin/env python3
# Metric: the space release steps HeatPumpOptimizer._safety_release_steps returns for a forced-off pin that holds the
#   house at its floor, with a room trajectory of n+1 entries (production) and of n entries (no initial state).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_97da0984.py
# EXPECTED RESULT n_long_baseline=[0, 1, 2] (last step pads with room[-1]), n_long_mutant=IndexError
# EXPECTED RESULT null_delta=0 count (n+1 entries)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._safety_release_steps, line 5222
#   `temp = room[i + 1] if i + 1 < len(room) else room[-1]`.
# Perturbation: key 97da0984453a53bb, `i + 1 < len(room)` -> `i + 1 <= len(room)` (CMP_BOUND), in memory.
#   Direction: an n-long trajectory raises IndexError at i = n-1 instead of reading room[-1].
# Null control: the production shape (room n+1 entries, as sensor_trajectory always carries).
# Reachability: the loop runs over len(power_schedule) = n and the trajectory has n+1 entries in every real solve
#   (reach_scan.py: traj=49 for n=48), so i + 1 <= n < len(room): the else-branch never runs on the baseline either.
from types import SimpleNamespace
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer
mut = rig.mutant(HeatPumpOptimizer, "_safety_release_steps", "if i + 1 < len(room) else room[-1]", "if i + 1 <= len(room) else room[-1]")
o = rig.bare_optimizer()
o._dhw_requirement = None


def call(fn, room, n=3):
    res = SimpleNamespace(power_schedule=[0.0] * n, sensor_trajectory=lambda tz: list(room),
                          dhw_temp_trajectory=[], dhw_power_schedule=[])
    try:
        return fn(o, res, np.full(n, 20.0), np.zeros(n), None)
    except Exception as e:
        return type(e).__name__


print(f"RESULT n_long_baseline={call(HeatPumpOptimizer._safety_release_steps, [20.0, 20.0, 20.0])}")
print(f"RESULT n_long_mutant={call(mut, [20.0, 20.0, 20.0])}")
r = [21.0, 20.0, 20.0, 20.0]
print(f"RESULT null_delta={int(call(HeatPumpOptimizer._safety_release_steps, r) != call(mut, r))} count")
rig.tail()
