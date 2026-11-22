OLD = "        if np.isfinite(score) and score < best_score:"
NEW = "        if np.isfinite(score) and score <= best_score:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4


def plateau(x, *a):
    """Zero on [0, 2]^4, rising past 2: every start inside the plateau is its own minimum, all scoring 0."""
    return float(np.sum(np.maximum(np.asarray(x) - 2.0, 0.0) ** 2))


def tilted(x, *a):
    return plateau(x) + 0.01 * float(np.sum(x))


cands = [np.full(4, 0.5), np.full(4, 1.5)]
rb, rm = O._multi_start_minimize(plateau, cands, bounds), MUT(plateau, cands, bounds)
print(f"RESULT score_tie={int(plateau(rb.x) == plateau(rm.x))}")
print(f"RESULT x_baseline={float(rb.x[0]):.6f}")
print(f"RESULT x_mutant={float(rm.x[0]):.6f}")
print(f"RESULT x_max_abs_diff={float(np.max(np.abs(rb.x - rm.x))):.6f}")
nb, nm = O._multi_start_minimize(tilted, cands, bounds), MUT(tilted, cands, bounds)
print(f"RESULT null_tilted_x_max_abs_diff={float(np.max(np.abs(nb.x - nm.x))):.6f}")
diffs = []
for prof, w in (("winter_typical", "winter_cold"), ("summer_negative", "summer_warm"), ("flat", "winter_mild")):
    r1 = golden_solve(prof, w)
    with mock.patch.object(O, "_multi_start_minimize", MUT):
        r2 = golden_solve(prof, w)
    diffs.append(float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))))
print(f"RESULT golden_plan_max_abs_diff={max(diffs):.3g} kW (winter_typical, summer_negative, flat)")
tail()
