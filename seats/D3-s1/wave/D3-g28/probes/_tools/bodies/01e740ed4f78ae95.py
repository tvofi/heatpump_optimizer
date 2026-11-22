OLD = "    if energy_kwh <= 0 or p_max <= 0 or dt <= 0:"
NEW = "    if energy_kwh <= 0 or p_max <= 0 or dt < 0:"
MUT = mutant("_price_ranked_start", OLD, NEW)
p = np.array([0.3, 0.1, 0.2, 0.4])
b, m = outcome(O._price_ranked_start, p, 1.0, 2.0, 0.0), outcome(MUT, p, 1.0, 2.0, 0.0)
print(f"RESULT dt0_baseline={b[0]}:{b[1] if b[0] == 'raise' else b[1].tolist()}")
print(f"RESULT dt0_mutant={m[0]}:{m[1] if m[0] == 'raise' else m[1].tolist()}")
print(f"RESULT dt0_mutant_raises={int(m[0] == 'raise')}")
print(f"RESULT null_dt_quarter_diff={float(np.max(np.abs(O._price_ranked_start(p, 1.0, 2.0, 0.25) - MUT(p, 1.0, 2.0, 0.25)))):.3g}")
tail()
