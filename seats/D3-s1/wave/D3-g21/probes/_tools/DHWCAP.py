
# The production seam: a fuse-guard ceiling (SolveLimits.power_caps_extra) whose horizon minimum is at or under
# 0.1 kW makes dhw_planner.py:1138-1141 plan every hot-water step at exactly the 0.1 kW planning floor.
import logging  # noqa: E402


def dhw_cap_solve(cap_min, hour=0, dhw_temp=42.0):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    caps = np.full(24, 6.0)
    caps[20] = cap_min
    logged = []

    class _H(logging.Handler):
        def emit(self, rec):
            if rec.msg.startswith("DHW+Space optimization completed"):
                logged.append(int(rec.args[3]))
    h = _H()
    optimizer._LOGGER.addHandler(h)
    old_level = optimizer._LOGGER.level
    optimizer._LOGGER.setLevel(logging.INFO)
    try:
        r = o.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=5.0,
                               dhw_temperature=dhw_temp),
            start_time=datetime(2026, 1, 15, hour, 0),
            forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(24, 5.0)),
            limits=SolveLimits(power_caps_extra=caps)))
    finally:
        optimizer._LOGGER.removeHandler(h)
        optimizer._LOGGER.setLevel(old_level)
    d = np.asarray(r.dhw_power_schedule, float)
    return r, d, (logged[-1] if logged else None)
