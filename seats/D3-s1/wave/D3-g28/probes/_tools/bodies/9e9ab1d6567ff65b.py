import warnings  # noqa: E402
OLD = "    return 1.0 - 0.8 * ranks / float(max(len(prices) - 1, 1))"
NEW = "    return 1.0 - 0.8 * ranks / float((len(prices) - 1))"
MUT = mutant("_price_guess_weights", OLD, NEW)
warnings.simplefilter("ignore", RuntimeWarning)
for name, p in (("one_zero", np.array([0.0])), ("one_negative", np.array([-0.5]))):
    b, m = O._price_guess_weights(p), MUT(p)
    print(f"RESULT {name}_baseline={b.tolist()}")
    print(f"RESULT {name}_mutant={m.tolist()}")
    print(f"RESULT {name}_mutant_nonfinite={int(not np.all(np.isfinite(m)))}")
q = np.array([0.0, -0.1, 0.0005, -0.2])
print(f"RESULT null_four_step_diff={float(np.max(np.abs(O._price_guess_weights(q) - MUT(q)))):.3g}")
tail()
