from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
OLD, NEW = "    elif p_max > 0:", "    elif p_max >= 0:"
MUT = mutant("_power_fraction", OLD, NEW)
zero = ThermalParameters(min_electrical_power=0.0, max_electrical_power=0.0)
b, m = outcome(O._power_fraction, 0.0, zero), outcome(MUT, 0.0, zero)
print(f"RESULT outcome_baseline={b[0]}:{b[1]}")
print(f"RESULT outcome_mutant={m[0]}:{m[1]}")
print(f"RESULT mutant_raises={int(m[0] == 'raise')}")
fixed = ThermalParameters(min_electrical_power=2.0, max_electrical_power=2.0)
print(f"RESULT null_fixed_speed_diff={abs(O._power_fraction(1.0, fixed) - MUT(1.0, fixed)):.6f}")
tail()
