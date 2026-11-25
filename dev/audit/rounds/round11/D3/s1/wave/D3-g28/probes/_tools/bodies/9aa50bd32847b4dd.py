OLD, NEW = "    if not scored:", "    if False:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4
cands = [np.full(4, 0.5), np.full(4, 1.5)]


def nan_obj(x, *a):
    return float("nan")          # every candidate scores non-finite


def quad(x, *a):
    return float(np.sum((np.asarray(x) - 1.0) ** 2))


b = outcome(O._multi_start_minimize, nan_obj, cands, bounds)
m = outcome(MUT, nan_obj, cands, bounds)
print(f"RESULT outcome_baseline={b[0]}:{b[1]!s}")
print(f"RESULT outcome_mutant={m[0]}:{m[1]!s}")
# The caller (HeatPumpOptimizer.optimize, the `except Exception as e` beside its
# _multi_start_minimize call) publishes `status = f"failed ({e})"`: the status text is the metric.
sb, sm = f"failed ({b[1].split(': ', 1)[1]})", f"failed ({m[1].split(': ', 1)[1]})"
print(f"RESULT status_baseline={sb!r}")
print(f"RESULT status_mutant={sm!r}")
print(f"RESULT status_differs={int(sb != sm)}")
nb, nm = outcome(O._multi_start_minimize, quad, cands, bounds), outcome(MUT, quad, cands, bounds)
print(f"RESULT null_x_max_abs_diff={float(np.max(np.abs(nb[1].x - nm[1].x))):.3g}")
tail()
