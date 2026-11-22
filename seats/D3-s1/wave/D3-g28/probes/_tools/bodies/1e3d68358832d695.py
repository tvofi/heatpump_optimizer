OLD, NEW = "        if solve_index:", "        if False:"
MUT = mutant("_multi_start_minimize", OLD, NEW)
bounds = [(0.0, 3.0)] * 4
three = [np.full(4, 0.2), np.full(4, 1.5), np.full(4, 2.8)]


def quad(x, *a):
    return float(np.sum((np.asarray(x) - 1.0) ** 2))


real_sleep = time.sleep


def count_yields(fn, *a, **k):
    """Calls of time.sleep(0.002), the between-starts GIL yield, during fn."""
    n = [0]

    def spy(s):
        if s == 0.002:
            n[0] += 1
        return real_sleep(s)
    with mock.patch.object(O._time_mod, "sleep", spy):
        out = fn(*a, **k)
    return n[0], out


nb, rb = count_yields(O._multi_start_minimize, quad, three, bounds)
nm, rm = count_yields(MUT, quad, three, bounds)
print(f"RESULT yields_baseline={nb} calls")
print(f"RESULT yields_mutant={nm} calls")
print(f"RESULT x_max_abs_diff={float(np.max(np.abs(rb.x - rm.x))):.3g}")
n1b, _ = count_yields(O._multi_start_minimize, quad, three[:1], bounds)
n1m, _ = count_yields(MUT, quad, three[:1], bounds)
print(f"RESULT null_one_start_yields_delta={n1b - n1m} calls")
# The realistic arm: one golden winter_typical solve through HeatPumpOptimizer.optimize.
gb, r1 = count_yields(golden_solve)
with mock.patch.object(O, "_multi_start_minimize", MUT):
    gm, r2 = count_yields(golden_solve)
print(f"RESULT golden_yields_baseline={gb} calls")
print(f"RESULT golden_yields_mutant={gm} calls")
print(f"RESULT golden_plan_max_abs_diff={float(np.max(np.abs(np.subtract(r1.power_schedule, r2.power_schedule)))):.3g} kW")
tail()
