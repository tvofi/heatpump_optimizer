OLD = "    if float(np.mean(prices)) > PRICE_MEAN_GUESS_EPS:"
NEW = "    if float(np.mean(prices)) >= PRICE_MEAN_GUESS_EPS:"
MUT = mutant("_price_guess_weights", OLD, NEW)
EPS = O.PRICE_MEAN_GUESS_EPS
n = 96
p = EPS * (1.0 + 0.5 * np.sin(np.arange(n) * 2.0 * np.pi / n))   # a shaped day whose mean is the threshold
for _ in range(100):                                              # nudge one step until the float mean is exact
    m = float(np.mean(p))
    if m == EPS:
        break
    p[-1] += (EPS - m) * n if abs((EPS - m) * n) > 0 else 0.0
    if float(np.mean(p)) == m:
        p[-1] = np.nextafter(p[-1], np.inf if m < EPS else -np.inf)
print(f"RESULT mean_is_exactly_eps={int(float(np.mean(p)) == EPS)}")
b, m = O._price_guess_weights(p), MUT(p)
print(f"RESULT guess_baseline_range={float(b.min()):.4f}..{float(b.max()):.4f}")
print(f"RESULT guess_mutant_range={float(m.min()):.4f}..{float(m.max()):.4f}")
print(f"RESULT guess_max_abs_diff={float(np.max(np.abs(b - m))):.4f}")
q = np.linspace(0.5, 2.0, n)
print(f"RESULT null_ordinary_prices_diff={float(np.max(np.abs(O._price_guess_weights(q) - MUT(q)))):.3g}")
# The plan arm: the same threshold-mean price day through HeatPumpOptimizer.optimize.
r1 = golden_solve(prices=p)
with mock.patch.object(O, "_price_guess_weights", MUT):
    r2 = golden_solve(prices=p)
print(f"RESULT golden_plan_max_abs_diff={float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))):.4g} kW")
print(f"RESULT golden_cost_rel_diff={abs(r1.predicted_cost - r2.predicted_cost) / max(abs(r1.predicted_cost), 1e-12):.4g}")
tail()
