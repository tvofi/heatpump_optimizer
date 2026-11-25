from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
OLD = "    if p_max - p_min >= _MIN_MODULATION_BAND_KW:"
NEW = "    if p_max - p_min > _MIN_MODULATION_BAND_KW:"
MUT = mutant("_power_fraction", OLD, NEW)


def pf(fn, lo, hi, power):
    return fn(power, ThermalParameters(min_electrical_power=lo, max_electrical_power=hi))


print(f"RESULT band_is_exactly_threshold={int(0.2 - 0.1 == O._MIN_MODULATION_BAND_KW)}")
b, m = pf(O._power_fraction, 0.1, 0.2, 0.15), pf(MUT, 0.1, 0.2, 0.15)
print(f"RESULT fraction_baseline={b:.6f}")
print(f"RESULT fraction_mutant={m:.6f}")
print(f"RESULT fraction_abs_diff={abs(b - m):.6f}")
# Null: a 0.1 kW band that starts at 0 grades identically on both branches; an ordinary band never
# reaches the boundary.
print(f"RESULT null_zero_floor_diff={abs(pf(O._power_fraction, 0.0, 0.1, 0.05) - pf(MUT, 0.0, 0.1, 0.05)):.6f}")
print(f"RESULT null_ordinary_band_diff={abs(pf(O._power_fraction, 0.6, 3.0, 1.2) - pf(MUT, 0.6, 3.0, 1.2)):.6f}")
tail()
