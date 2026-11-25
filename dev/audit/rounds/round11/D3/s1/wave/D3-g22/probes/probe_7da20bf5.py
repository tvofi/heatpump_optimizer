#!/usr/bin/env python3
# Metric: dhw_floor_breach_c (C) a real DHW-blocked solve publishes (features.py's v5.3.0 January scenario) with
#   the tank starting hot enough to coast through the horizon above its requirement (60 C and 65 C), and with a
#   tank that falls short (45 C, 55 C).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_7da20bf5.py
# EXPECTED RESULT tank60_baseline=0.0 C, tank60_mutant<0 (about -1.39 C: a negative "shortfall" published)
# EXPECTED RESULT null_delta_tank45=0.0 C (a real shortfall: the clip is inert on a positive maximum)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4917
#   `np.max(np.clip(req[:steps] - planned[:steps], 0.0, None))`, reached through HeatPumpOptimizer.optimize with
#   SolveLimits.dhw_blocked=True (the pump-mode entity reporting a heating-only mode).
# Perturbation: key 7da20bf51cc217e6, the np.clip dropped (CLAMP_DROP), patched onto HeatPumpOptimizer in memory.
#   Direction: 0.0 -> negative when the tank stays above its requirement at every step.
# Null control: a tank that falls short (45 C, 55 C start): the max is positive and both arms publish it.
# The documented effect (the method's own comment): "zero when the tank coasted through anyway".
from datetime import datetime
from unittest import mock
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer, ThermalState
import profiles
from profiles import solve_inputs
from breach_rig import mutant
mut = mutant("np.max(np.clip(req[:steps] - planned[:steps], 0.0, None))", "np.max((req[:steps] - planned[:steps]))")
opt, _ = rig.january()
n = opt.config.n_steps
start = datetime(2026, 1, 15, 0, 0)
prices = np.asarray(profiles.prices("winter_typical", start))[:n]
t, w, rn, s = profiles.weather("winter_cold", start)


def solve(t0):
    st = ThermalState(room_temperature=21.0, outdoor_temperature=-12.0, dhw_temperature=t0)
    r = opt.optimize(inputs=solve_inputs(initial_state=st, prices=prices, outdoor_temps=t[:n], wind_speeds=w[:n],
                                         precipitation=rn[:n], solar_radiation=s[:n], start_time=start,
                                         dhw_blocked=True))
    return r.predictive_info.get("dhw_floor_breach_c")


for t0 in (45.0, 55.0, 60.0, 65.0):
    b = solve(t0)
    with mock.patch.object(HeatPumpOptimizer, "_publish_breach_reports", mut):
        m = solve(t0)
    tag = f"tank{int(t0)}"
    print(f"RESULT {tag}_baseline={b} C")
    print(f"RESULT {tag}_mutant={m} C")
    if t0 == 45.0:
        print(f"RESULT null_delta_tank45={abs(b - m)} C")
rig.tail()
