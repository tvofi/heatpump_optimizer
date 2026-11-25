OLD = "    if energy_kwh <= 0 or p_max <= 0 or dt <= 0:"
NEW = "    if False:"
MUT = mutant("_price_ranked_start", OLD, NEW)
p = np.array([0.3, 0.1, 0.2, 0.4])


def show(tag, *a):
    b, m = outcome(O._price_ranked_start, p, *a), outcome(MUT, p, *a)
    fmt = lambda o: o[1] if o[0] == "raise" else [round(float(v), 6) for v in o[1]]  # noqa: E731
    print(f"RESULT {tag}_baseline={b[0]}:{fmt(b)}")
    print(f"RESULT {tag}_mutant={m[0]}:{fmt(m)}")
    return b, m


b, m = show("pmax_neg", 1.0, -1.0, 0.25)
print(f"RESULT pmax_neg_mutant_min_kw={float(np.min(m[1])):.3f} kW")
show("dt_zero", 1.0, 2.0, 0.0)
show("dt_neg", 1.0, 2.0, -0.25)
show("energy_neg", -1.0, 2.0, 0.25)
show("pmax_zero", 1.0, 0.0, 0.25)
print(f"RESULT null_ordinary_diff={float(np.max(np.abs(O._price_ranked_start(p, 1.0, 2.0, 0.25) - MUT(p, 1.0, 2.0, 0.25)))):.3g}")
tail()
