OLD, NEW = "    if best is None:", "    if False:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4
cands = [np.full(4, 0.5), np.full(4, 1.5)]


def make_obj(limit):
    """Finite on the scoring pass (one call per candidate), then every solve's evaluation raises."""
    calls = [0]

    def obj(x, *a):
        calls[0] += 1
        if calls[0] > limit:
            raise FloatingPointError("solver blow-up")
        return float(np.sum((np.asarray(x) - 1.0) ** 2))
    return obj


b = outcome(O._multi_start_minimize, make_obj(len(cands)), cands, bounds)
m = outcome(MUT, make_obj(len(cands)), cands, bounds)
print(f"RESULT outcome_baseline={b[0]}:{b[1]!s}")
print(f"RESULT outcome_mutant={m[0]}:{m[1]!r}")
print(f"RESULT mutant_returns_none={int(m == ('ok', None))}")
# What HeatPumpOptimizer.optimize then publishes: `result.x` on None raises inside its try, so the
# status becomes `failed (<that error>)` instead of the solver's own error.
sm = outcome(lambda: m[1].x)[1] if m[0] == "ok" else m[1]
print(f"RESULT status_baseline={'failed (' + b[1].split(': ', 1)[1] + ')'!r}")
print(f"RESULT status_mutant={'failed (' + sm.split(': ', 1)[1] + ')'!r}")
nb = outcome(O._multi_start_minimize, make_obj(10 ** 9), cands, bounds)
nm = outcome(MUT, make_obj(10 ** 9), cands, bounds)
print(f"RESULT null_x_max_abs_diff={float(np.max(np.abs(nb[1].x - nm[1].x))):.3g}")
tail()
