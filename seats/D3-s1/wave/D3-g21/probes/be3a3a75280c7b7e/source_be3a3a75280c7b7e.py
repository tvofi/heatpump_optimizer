#!/usr/bin/env python3
# Metric: what HeatPumpOptimizer._normalise_pins returns (the padded array, or the exception) for a pin array SHORTER
#   than the horizon, baseline vs mutant; the same through optimize(space_pins=short); and, as the reach arm, the
#   plan's max |power| difference when the pins are as long as the price array the coordinator sizes them from
#   (coordinator.py:6289 `_manual_pins(solve_now, len(horizon.prices))`), including a shorter weather series.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_be3a3a75280c7b7e.py
# EXPECTED RESULT short_baseline=array:1,0,nan,nan
# EXPECTED RESULT short_mutant=raise:ValueError
# EXPECTED RESULT optimize_short_pins_baseline=ok
# EXPECTED RESULT optimize_short_pins_mutant=raise:ValueError
# EXPECTED RESULT null_delta=0 count  (pins as long as or longer than the horizon: identical arrays)
# EXPECTED RESULT reach_plan_maxabs_diff_kw=0.0000 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._normalise_pins
#   (line 5016 `        take = min(n_steps, src.size)`), callers optimizer.py:4432-4433 in optimize().
# Perturbation: line 5016 -> `        take = (n_steps)` (CLAMP_DROP be3a3a75280c7b7e), in memory. Direction: NaN padding
#   -> ValueError (broadcast of a shorter source into n_steps slots) for a short pin array.
# Null control: pins of horizon length and longer (both arms identical).
#@PRE
NAME = "_normalise_pins"
OLD, NEW = "take = min(n_steps, src.size)", "take = (n_steps)"
f = lambda *a: outcome(lambda: HeatPumpOptimizer._normalise_pins(*a))  # noqa: E731
short, exact, longer = np.array([1.0, 0.0]), np.array([1.0, 0.0, np.nan, 1.0]), np.array([1.0, 0.0, 1.0, 0.0, 1.0, 1.0])
b = (f(short, 4), f(exact, 4), f(longer, 4))
with mutated(NAME, OLD, NEW):
    m = (f(short, 4), f(exact, 4), f(longer, 4))
print(f"RESULT short_baseline={b[0]}")
print(f"RESULT short_mutant={m[0]}")
print(f"RESULT null_delta={int(b[1:] != m[1:])} count")


def solve(pins, n_out=24):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    r = o.optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
        start_time=datetime(2026, 1, 15, 0, 0),
        forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(n_out, -5.0)), limits=SolveLimits(space_pins=pins)))
    return np.asarray(r.power_schedule, float)


short24 = np.array([1.0, 1.0, 0.0])
full24 = np.full(24, np.nan)
full24[:3] = [1.0, 1.0, 0.0]
ob = outcome(lambda: solve(short24))
pb, pb2 = solve(full24), solve(full24, n_out=20)
with mutated(NAME, OLD, NEW):
    om = outcome(lambda: solve(short24))
    pm, pm2 = solve(full24), solve(full24, n_out=20)
print(f"RESULT optimize_short_pins_baseline={'ok' if ob.startswith('array') else ob}")
print(f"RESULT optimize_short_pins_mutant={'ok' if om.startswith('array') else om}")
print(f"RESULT reach_plan_maxabs_diff_kw={max(float(np.max(np.abs(pb - pm))), float(np.max(np.abs(pb2 - pm2)))):.4f} kW")
