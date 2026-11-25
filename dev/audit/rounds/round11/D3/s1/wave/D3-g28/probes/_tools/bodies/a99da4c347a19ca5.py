OLD = "    if energy_kwh <= 0 or p_max <= 0 or dt <= 0:"
NEW = "    if energy_kwh <= 0 or p_max < 0 or dt <= 0:"
MUT = mutant("_price_ranked_start", OLD, NEW)
rng = np.random.default_rng(11)
tried, maxdiff, signdiff = 0, 0.0, 0
prices = [np.array([0.3, 0.1, 0.2, 0.4]), np.zeros(4), np.array([-1.0, 1.0, -1.0, 1.0]), rng.normal(size=96)]
for p in prices:
    for e in (1.0, 0.0, -1.0, 1e-12, 1e9, 3.0):
        for pm in (0, 0.0, -0.0, 5e-324, 1e-300):   # the only band the mutant opens is p_max == 0
            for dt in (0.25, 1.0, 1e-9):
                b, m = outcome(O._price_ranked_start, p, e, pm, dt), outcome(MUT, p, e, pm, dt)
                tried += 1
                if b[0] != m[0]:
                    maxdiff = float("inf")
                    continue
                if b[0] == "ok":
                    maxdiff = max(maxdiff, float(np.max(np.abs(b[1] - m[1]))))
                    signdiff += int(np.any(np.signbit(b[1]) != np.signbit(m[1])))
print(f"RESULT inputs_tried={tried}")
print(f"RESULT max_abs_diff={maxdiff:.3g}")
print(f"RESULT signbit_only_diffs={signdiff}")
tail()
