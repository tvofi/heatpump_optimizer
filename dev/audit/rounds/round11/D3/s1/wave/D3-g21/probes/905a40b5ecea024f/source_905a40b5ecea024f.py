#!/usr/bin/env python3
# Metric: what HeatPumpOptimizer._derive_hold_schedule returns ("None", an array, or the exception raised) on a
#   length-mismatched and on an empty (power, prices) pair, baseline vs mutant; plus the same through the one
#   production caller (optimize(), smart-write valve, buffer store), whose arguments are counted for mismatch.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_905a40b5ecea024f.py
# EXPECTED RESULT mismatch_baseline=None
# EXPECTED RESULT mismatch_mutant=raise:ValueError
# EXPECTED RESULT empty_baseline=None
# EXPECTED RESULT empty_mutant=raise:IndexError
# EXPECTED RESULT null_delta=0 count  (matched length 8: the guard is false, both arms return the same)
# EXPECTED RESULT reach_calls_mismatched=0 count  (of reach_calls_total production calls)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5044 `        if n == 0 or len(prices) != n:`), caller optimizer.py:4601.
# Perturbation: line 5044 -> `        if False:` (GUARD_OFF 905a40b5ecea024f), applied in memory (method recompiled from
#   its own source, patched onto the class for the mutant arm only). Direction: None -> an exception.
# Null control: a matched-length pair, where the guard is false in both arms.
#@PRE
NAME = "_derive_hold_schedule"
OLD, NEW = "if n == 0 or len(prices) != n:", "if False:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(horizon_hours=2, time_step_minutes=15))
fn = lambda: HeatPumpOptimizer._derive_hold_schedule  # noqa: E731
power8 = np.array([6.0, 6.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0])
prices8 = np.array([0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 3.0, 3.0])
floors8 = np.full(8, 19.0)
cases = {
    "mismatch": (power8, np.append(prices8, 1.0), floors8),
    "empty": (np.zeros(0), np.zeros(0), np.zeros(0)),
    "matched": (power8, prices8, floors8),
}
res = {}
for arm in ("baseline", "mutant"):
    ctx = mutated(NAME, OLD, NEW) if arm == "mutant" else mock.patch.object(HeatPumpOptimizer, "__doc__", HeatPumpOptimizer.__doc__)
    with ctx:
        for c, args in cases.items():
            res[(c, arm)] = outcome(lambda *a: HeatPumpOptimizer._derive_hold_schedule(opt, *a), *args)
print(f"RESULT mismatch_baseline={res[('mismatch', 'baseline')]}")
print(f"RESULT mismatch_mutant={res[('mismatch', 'mutant')]}")
print(f"RESULT empty_baseline={res[('empty', 'baseline')]}")
print(f"RESULT empty_mutant={res[('empty', 'mutant')]}")
print(f"RESULT null_delta={int(res[('matched', 'baseline')] != res[('matched', 'mutant')])} count")

# Reach: the production caller with the valve in smart_write and a store buffer, spying on the arguments.
from custom_components.heatpump_optimizer import mixing_valve  # noqa: E402
calls = {"total": 0, "mismatch": 0}
real = HeatPumpOptimizer._derive_hold_schedule


def spy(self, power, prices, floors):
    calls["total"] += 1
    calls["mismatch"] += int(len(power) == 0 or len(prices) != len(power))
    return real(self, power, prices, floors)


try:
    params = ThermalParameters(mixing_valve_mode=mixing_valve.MODE_SMART_WRITE, buffer_tank_volume=500.0)
    o = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    with mock.patch.object(HeatPumpOptimizer, NAME, spy):
        for n_prices in (24, 30):
            o.optimize(inputs=SolveInputs(
                state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
                start_time=datetime(2026, 1, 15, 0, 0),
                forecast=ForecastSeries(prices=np.resize(pr, n_prices), outdoor_temps=np.full(n_prices, -5.0))))
except Exception as exc:
    print(f"RESULT reach_error={type(exc).__name__}")
print(f"RESULT reach_calls_mismatched={calls['mismatch']} count")
print(f"RESULT reach_calls_total={calls['total']} count")
