#!/usr/bin/env python3
# Metric: HeatPumpOptimizer._pv_self_consumed (kWh) for a power schedule longer than the stored surplus, and for the
#   production shape (equal lengths, the surplus padded to n_steps by _prepare_series at optimizer.py:4700-4707).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_9fe0782a.py
# EXPECTED RESULT long_power_baseline=1.5 kWh, long_power_mutant=ValueError (broadcast); RESULT null_delta=0.0 kWh
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._pv_self_consumed, line 5701
#   `n = min(len(power), len(self._pv_surplus))`.
# Perturbation: key 9fe0782a9839475e, `min(len(power), len(self._pv_surplus))` -> `(len(power))` (CLAMP_DROP),
#   in memory. Direction: power longer than surplus: a number -> ValueError; power shorter: identical.
# Null control: equal lengths 48/48.
# Reachability: the surplus is sliced/padded to exactly n_steps before it is stored (optimizer.py:4695-4707) and every
#   caller passes an n_steps power schedule (reach_scan.py RESULT pvsc_power_longer_than_surplus=0 over 7 solves).
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer
mut = rig.mutant(HeatPumpOptimizer, "_pv_self_consumed", "n = min(len(power), len(self._pv_surplus))", "n = (len(power))")
o = rig.bare_optimizer()


def call(fn, pw, s, dt=0.25):
    o._pv_surplus = s
    try:
        return fn(o, pw, dt)
    except Exception as e:
        return type(e).__name__


s = np.r_[np.zeros(4), np.full(4, 3.0)]
print(f"RESULT long_power_baseline={call(HeatPumpOptimizer._pv_self_consumed, np.full(10, 1.5), s)} kWh")
print(f"RESULT long_power_mutant={call(mut, np.full(10, 1.5), s)} kWh")
print(f"RESULT short_power_delta={int(call(HeatPumpOptimizer._pv_self_consumed, np.full(6, 1.5), s) != call(mut, np.full(6, 1.5), s))} count")
s48 = np.r_[np.zeros(20), np.full(8, 3.0), np.zeros(20)]
b, m = call(HeatPumpOptimizer._pv_self_consumed, np.full(48, 2.0), s48), call(mut, np.full(48, 2.0), s48)
print(f"RESULT null_delta={abs(b - m)} kWh")
print("RESULT reach_power_longer_than_surplus=0 count  (reach_scan.py RESULT pvsc_power_longer_than_surplus)")
rig.tail()
