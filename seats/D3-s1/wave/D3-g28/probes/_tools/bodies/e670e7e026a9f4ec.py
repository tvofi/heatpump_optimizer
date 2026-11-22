OLD = "    return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))"
NEW = "    return float((savings / baseline_cost * 100.0))"
MUT = mutant("_savings_percentage", OLD, NEW)
for tag, s, c in (("over", 2.0, 1.0), ("under", -3.0, 1.0)):
    print(f"RESULT {tag}_pct_baseline={O._savings_percentage(s, c):.3f} %")
    print(f"RESULT {tag}_pct_mutant={MUT(s, c):.3f} %")
print(f"RESULT null_inside_band_diff={abs(O._savings_percentage(0.4, 1.0) - MUT(0.4, 1.0)):.3f} %")
# The plan arm: HeatPumpOptimizer.optimize on six golden.make cells; savings_percentage is what the
# plan_savings_percentage sensor publishes.
cells = [("summer_typical", "summer_warm", True), ("summer_typical", "summer_warm", False),
         ("summer_negative", "summer_warm", True), ("summer_negative", "summer_warm", False),
         ("shoulder", "shoulder", False), ("winter_typical", "winter_cold", True)]
moved = []
for prof, w, dhw in cells:
    r1 = golden_solve(prof, w, dhw=dhw)
    with mock.patch.object(O, "_savings_percentage", MUT):
        r2 = golden_solve(prof, w, dhw=dhw)
    print(f"RESULT cell_{prof}_{'dhw' if dhw else 'nodhw'}_pct_baseline_mutant={r1.savings_percentage:.2f},{r2.savings_percentage:.2f}")
    if abs(r1.savings_percentage - r2.savings_percentage) > 1e-9:
        moved.append(prof + ("_dhw" if dhw else "_nodhw"))
print(f"RESULT golden_cells={len(cells)}")
print(f"RESULT golden_cells_moved={len(moved)} {moved}")
tail()
