#!/usr/bin/env python3
# Metric: predictive_info["dhw_required_temperature_now"] (C) from a hot-water optimize() at a start hour inside the
#   default morning demand window, baseline vs mutant, scanned over all 24 start hours (count of hours that differ).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a66e107749d0ae11.py
# EXPECTED RESULT required_now_baseline=55.0 C
# EXPECTED RESULT required_now_mutant=20.0 C
# EXPECTED RESULT hours_differ=4 count  (of 24 start hours)
# EXPECTED RESULT null_delta=0 count  (hours outside every window: ready[0] <= floor[0], both arms equal)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._optimize_with_dhw
#   (line 5945 `                    float(max(dhw_floor_temps[0], dhw_ready_temps[0]))`), published as
#   predictive_info.dhw_required_temperature_now.
# Perturbation: line 5945 -> `                    float((dhw_floor_temps[0]))` (CLAMP_DROP a66e107749d0ae11), in memory.
#   Direction: inside a demand window the published required temperature falls from the ready target to the floor.
# Null control: start hours where ready[0] <= floor[0] (outside the windows): identical.
#@PRE
NAME = "_optimize_with_dhw"
OLD = "float(max(dhw_floor_temps[0], dhw_ready_temps[0]))"
NEW = "float((dhw_floor_temps[0]))"


def required(hour):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    r = o.optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0, dhw_temperature=50.0),
        start_time=datetime(2026, 1, 15, hour, 0), forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(24, -5.0))))
    return float(r.predictive_info["dhw_required_temperature_now"])


HOURS = range(24)
b = {h: required(h) for h in HOURS}
with mutated(NAME, OLD, NEW):
    m = {h: required(h) for h in HOURS}
diff = [h for h in HOURS if b[h] != m[h]]
first = diff[0] if diff else 0
print(f"RESULT first_differing_hour={first}")
print(f"RESULT required_now_baseline={b[first]} C")
print(f"RESULT required_now_mutant={m[first]} C")
print(f"RESULT hours_differ={len(diff)} count")
print(f"RESULT differing_hours={','.join(map(str, diff))}")
print(f"RESULT null_delta={sum(b[h] != m[h] for h in HOURS if h not in diff)} count")
