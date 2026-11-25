OLD, NEW = "        if remaining <= 0:", "        if False:"
MUT = mutant("_price_ranked_start", OLD, NEW)
rng = np.random.default_rng(13)
tried = moved = 0
worst = 0.0
example = None
for _ in range(20000):
    n = int(rng.integers(2, 97))
    p = rng.normal(size=n)
    pm = float(rng.choice([1.0, 2.0, 3.5, 6.0, float(rng.uniform(0.3, 9.0))]))
    dt = float(rng.choice([0.25, 0.5, 1.0, 1 / 3, float(rng.uniform(0.05, 1.0))]))
    e = float(rng.uniform(0.0, pm * dt * n))
    b, m = O._price_ranked_start(p, e, pm, dt), MUT(p, e, pm, dt)
    tried += 1
    d = float(np.max(np.abs(b - m)))
    if d > 0:
        moved += 1
        if d > worst:
            worst, example = d, (n, pm, dt, e, float(np.min(m)))
print(f"RESULT inputs_tried={tried}")
print(f"RESULT inputs_moved={moved}")
print(f"RESULT max_abs_diff={worst:.3g} kW")
print(f"RESULT example_n_pmax_dt_energy_mutant_min={example}")
# The plan arm: every caller hands the start to L-BFGS-B under bounds [0, p_max], which clips x0.
diffs = []
for prof, w in (("winter_typical", "winter_cold"), ("summer_negative", "summer_warm"), ("shoulder", "shoulder")):
    r1 = golden_solve(prof, w)
    with mock.patch.object(O, "_price_ranked_start", MUT):
        r2 = golden_solve(prof, w)
    diffs.append(float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))))
print(f"RESULT golden_plan_max_abs_diff={max(diffs):.3g} kW (winter_typical, summer_negative, shoulder)")
tail()
