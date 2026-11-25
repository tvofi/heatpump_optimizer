#!/usr/bin/env python3
# Metric: max |power| difference (kW) and objective difference between baseline and mutant space-only plans from
#   optimize(), over scenarios where the [p_min, p_max] clip of the initial guess binds (min power 2 kW against the
#   guess's 0.2*p_max = 1 kW floor; strong sun lowering the anticipatory weights), plus the count of guess steps the
#   clip moves (spied on _seed_pinned_guess's input, the clip's only consumer).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_39a6d2e97fd44ed5.py
# EXPECTED RESULT guess_steps_moved_min2=4 count
# EXPECTED RESULT plan_maxabs_diff_kw=0.0000 kW
# EXPECTED RESULT objective_maxabs_diff=0.000000
# EXPECTED RESULT null_delta=0 count  (defaults, no sun: 5 kW * 0.2 = 1 kW = p_min, the clip is inert)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._optimize_space_only
#   (line 5478 `        initial_power = np.clip(initial_power, p_min, p_max)`).
# Perturbation: line 5478 -> `        initial_power = (initial_power)` (CLAMP_DROP 39a6d2e97fd44ed5), in memory.
#   Direction looked for: a different L-BFGS-B start, hence a different plan or objective.
# Null control: default p_min/p_max with no sun, where the clip changes no guess value.
#@PRE
NAME = "_optimize_space_only"
OLD = "initial_power = np.clip(initial_power, p_min, p_max)"
NEW = "initial_power = (initial_power)"
PR = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
SUN = np.where((np.arange(24) >= 9) & (np.arange(24) <= 15), 800.0, 0.0)


def solve(min_kw, sun, out=-5.0, prices=PR):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters(min_electrical_power=min_kw)), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    seen = []
    real = HeatPumpOptimizer._seed_pinned_guess

    def spy(guess, bounds):
        seen.append(np.array(guess, float))
        return real(guess, bounds)
    with mock.patch.object(HeatPumpOptimizer, "_seed_pinned_guess", staticmethod(spy)):
        r = o.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=out),
            start_time=datetime(2026, 1, 15, 0, 0),
            forecast=ForecastSeries(prices=prices, outdoor_temps=np.full(24, out), solar_radiation=sun)))
    return np.asarray(r.power_schedule, float), float(r.objective_value), (seen[0] if seen else None)


CASES = {"min2": (2.0, None), "sun": (1.0, SUN), "min2_sun": (2.0, SUN), "min2_mild": (2.0, None, 8.0),
         "min3_negative": (3.0, None, -5.0, PR - 1.2), "null": (1.0, None)}
B = {k: solve(*v) for k, v in CASES.items()}
with mutated(NAME, OLD, NEW):
    M = {k: solve(*v) for k, v in CASES.items()}
for k in CASES:
    if B[k][2] is not None:
        print(f"RESULT guess_steps_moved_{k}={int(np.sum(~np.isclose(B[k][2], M[k][2])))} count")
act = [k for k in CASES if k != "null"]
print(f"RESULT plan_maxabs_diff_kw={max(float(np.max(np.abs(B[k][0] - M[k][0]))) for k in act):.4f} kW")
print(f"RESULT objective_maxabs_diff={max(abs(B[k][1] - M[k][1]) for k in act):.6f}")
for k in act:
    print(f"RESULT plan_diff_{k}_kw={float(np.max(np.abs(B[k][0] - M[k][0]))):.4f} kW")
print(f"RESULT null_delta={int(not np.array_equal(B['null'][0], M['null'][0]))} count")
