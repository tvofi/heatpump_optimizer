# Old (10d8f0433b) vs new (1dd030c424) drop_unstartable, on random plans with a
# temps_of that depends on the mutated plan (so order of drops matters).
import numpy as np
def old(plan, start_below, temps_of):
    plan = np.array(plan, dtype=float); on = plan > 0.0; i = 1
    while i < plan.size:
        if not on[i] or on[i - 1]:
            i += 1; continue
        end = i + int(np.argmin(np.append(on[i:], False)))
        if temps_of(plan)[i] >= start_below[i]:
            plan[i:end] = 0.0
        i = end
    return plan
def new(plan, start_below, temps_of):
    plan = np.array(plan, dtype=float); on = plan > 0.0
    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:
        end = i + int(np.argmin(np.append(on[i:], False)))
        if temps_of(plan)[i] >= start_below[i]:
            plan[i:end] = 0.0
    return plan
def wrong(plan, start_below, temps_of):  # control: every on-step judged as a start
    plan = np.array(plan, dtype=float); on = plan > 0.0
    for i in np.flatnonzero(on[1:]) + 1:
        end = i + int(np.argmin(np.append(on[i:], False)))
        if temps_of(plan)[i] >= start_below[i]:
            plan[i:end] = 0.0
    return plan
rng = np.random.default_rng(3531)
def temps_of(p):  # a tank that rises with charge and falls with standing loss
    t = np.empty(p.size); x = 45.0
    for k in range(p.size):
        x += 2.0 * p[k] - 0.8; t[k] = x
    return t
n = diff = diffw = 0
for trial in range(20000):
    size = int(rng.integers(0, 40))
    plan = np.where(rng.random(size) < rng.random(), rng.random(size) * 3, 0.0)
    sb = rng.uniform(40, 55, size)
    a, b, c = old(plan, sb, temps_of), new(plan, sb, temps_of), wrong(plan, sb, temps_of)
    n += 1; diff += not np.array_equal(a, b); diffw += not np.array_equal(a, c)
print(f"RESULT plans={n} old_vs_new_differ={diff} old_vs_control_differ={diffw}")
