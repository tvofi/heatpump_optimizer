OLD, NEW = "    if baseline_cost <= 0.01:", "    if baseline_cost < 0.01:"
MUT = mutant("_savings_percentage", OLD, NEW)
b, m = O._savings_percentage(0.005, 0.01), MUT(0.005, 0.01)
print(f"RESULT pct_baseline={b:.3f} %")
print(f"RESULT pct_mutant={m:.3f} %")
print(f"RESULT pct_abs_diff={abs(b - m):.3f} %")
print(f"RESULT null_baseline_cost_0p02_diff={abs(O._savings_percentage(0.005, 0.02) - MUT(0.005, 0.02)):.3f} %")
print(f"RESULT null_baseline_cost_0p009_diff={abs(O._savings_percentage(0.005, 0.009) - MUT(0.005, 0.009)):.3f} %")
tail()
