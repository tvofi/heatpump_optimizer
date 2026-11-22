OLD, NEW = "        if remaining <= 0:", "        if remaining < 0:"
MUT = mutant("_price_ranked_start", OLD, NEW)
rng = np.random.default_rng(14)
tried, maxdiff, signdiff, exact_zero = 0, 0.0, 0, 0
cases = []
for pm in (1.0, 2.0, 0.5, 4.0):                      # energy an exact multiple of p_max*dt: remaining hits 0.0
    for dt in (0.25, 0.5, 1.0, 0.125):
        for k in range(0, 9):
            cases.append((pm, dt, pm * dt * k))
for _ in range(5000):
    pm, dt = float(rng.uniform(0.3, 9.0)), float(rng.uniform(0.05, 1.0))
    cases.append((pm, dt, float(rng.uniform(0.0, pm * dt * 40))))
for pm, dt, e in cases:
    p = rng.normal(size=40)
    b, m = O._price_ranked_start(p, e, pm, dt), MUT(p, e, pm, dt)
    tried += 1
    rem = e
    for _i in range(40):
        take = min(pm, rem / dt)
        rem -= take * dt
        if rem == 0.0:
            exact_zero += 1
            break
        if rem < 0:
            break
    maxdiff = max(maxdiff, float(np.max(np.abs(b - m))))
    signdiff += int(np.any(np.signbit(b) != np.signbit(m)))
print(f"RESULT inputs_tried={tried}")
print(f"RESULT inputs_reaching_remaining_exactly_zero={exact_zero}")
print(f"RESULT max_abs_diff={maxdiff:.3g}")
print(f"RESULT signbit_only_diffs={signdiff}")
tail()
