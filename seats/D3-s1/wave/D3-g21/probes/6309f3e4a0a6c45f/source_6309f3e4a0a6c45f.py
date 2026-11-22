#!/usr/bin/env python3
# Metric: the lowest planned space power (kW) on manually pinned-ON steps, from optimize() with the pump's minimum
#   power configured at 0 kW (the config flow's heat_pump_min_power number accepts 0..10 kW), the pinned steps placed
#   in the dearest hours; and HeatPumpOptimizer._pin_on_power(5.0) itself at min power 0.0 and 0.05 kW.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6309f3e4a0a6c45f.py
# EXPECTED RESULT pin_on_power_min0_baseline=0.1 kW
# EXPECTED RESULT pin_on_power_min0_mutant=0.0 kW
# EXPECTED RESULT pinned_on_min_kw_baseline=0.1000 kW
# EXPECTED RESULT pinned_on_min_kw_mutant=0.0000 kW
# EXPECTED RESULT null_delta_kw=0.0000 kW  (min power 1.0 kW, the default: the 0.1 floor never binds)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._pin_on_power
#   (line 5283 `        floor = max(float(self.model.params.min_electrical_power), 0.1)`), read by
#   _apply_pins_to_bounds at optimizer.py:5492 (space-only) and 597 (with DHW).
# Perturbation: line 5283 -> `        floor = (float(self.model.params.min_electrical_power))` (CLAMP_DROP
#   6309f3e4a0a6c45f), in memory. Direction: the forced-on lower bound falls from 0.1 kW to the configured minimum
#   (0 kW), so a step the user pinned ON may be planned at 0 kW, i.e. not running.
# Null control: min power 1.0 kW (default), where max(1.0, 0.1) == 1.0 in both arms.
#@PRE
NAME = "_pin_on_power"
OLD = "floor = max(float(self.model.params.min_electrical_power), 0.1)"
NEW = "floor = (float(self.model.params.min_electrical_power))"
PR = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
PINS = np.full(24, np.nan)
PINS[16:20] = 1.0          # pinned ON across the four dearest hours


def mk(min_kw):
    return HeatPumpOptimizer(ThermalModel(ThermalParameters(min_electrical_power=min_kw)), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))


def pinned_min(min_kw):
    r = mk(min_kw).optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=22.0, slab_temperature=26.0, outdoor_temperature=8.0),
        start_time=datetime(2026, 1, 15, 0, 0),
        forecast=ForecastSeries(prices=PR, outdoor_temps=np.full(24, 8.0)), limits=SolveLimits(space_pins=PINS)))
    return float(np.min(np.asarray(r.power_schedule, float)[16:20]))


print(f"RESULT configured_min_kw={mk(0.0).model.params.min_electrical_power}")
b = (mk(0.0)._pin_on_power(5.0), mk(0.05)._pin_on_power(5.0), pinned_min(0.0), pinned_min(1.0))
with mutated(NAME, OLD, NEW):
    m = (mk(0.0)._pin_on_power(5.0), mk(0.05)._pin_on_power(5.0), pinned_min(0.0), pinned_min(1.0))
print(f"RESULT pin_on_power_min0_baseline={b[0]} kW")
print(f"RESULT pin_on_power_min0_mutant={m[0]} kW")
print(f"RESULT pin_on_power_min005_baseline={b[1]} kW")
print(f"RESULT pin_on_power_min005_mutant={m[1]} kW")
print(f"RESULT pinned_on_min_kw_baseline={b[2]:.4f} kW")
print(f"RESULT pinned_on_min_kw_mutant={m[2]:.4f} kW")
print(f"RESULT null_delta_kw={abs(b[3] - m[3]):.4f} kW")
