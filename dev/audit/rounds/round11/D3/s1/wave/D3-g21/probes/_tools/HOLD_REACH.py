
# Reach: optimize() with the valve in smart_write and a 500 L store buffer, the one production caller
# (optimizer.py:4601), on the price profile PR; spy counts the schedules the derivation proposes.
from custom_components.heatpump_optimizer import mixing_valve  # noqa: E402


def reach(prices, arm_ctx, outdoor=-15.0):
    seen = {"calls": 0, "proposed": 0}
    inner = HeatPumpOptimizer._derive_hold_schedule

    def spy(self, power, pr, floors):
        r = inner(self, power, pr, floors)
        seen["calls"] += 1
        seen["proposed"] += int(r is not None)
        return r
    params = ThermalParameters(mixing_valve_mode=mixing_valve.MODE_SMART_WRITE, buffer_tank_volume=500.0)
    o = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=len(prices), time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    c0 = time.thread_time()
    with arm_ctx():
        inner = HeatPumpOptimizer._derive_hold_schedule
        with mock.patch.object(HeatPumpOptimizer, "_derive_hold_schedule", spy):
            r = o.optimize(inputs=SolveInputs(
                state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=outdoor),
                start_time=datetime(2026, 1, 15, 0, 0),
                forecast=ForecastSeries(prices=np.asarray(prices, float), outdoor_temps=np.full(len(prices), outdoor))))
    seen["cpu_s"] = time.thread_time() - c0
    return seen, np.asarray(r.power_schedule, float), float(r.objective_value)


def base_ctx():
    return mock.patch.object(HeatPumpOptimizer, "__doc__", HeatPumpOptimizer.__doc__)
