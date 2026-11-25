#H Metric: tariff.realised_peak's answer (kW, or the exception raised) for an empty power series.
#H EXPECTED RESULT empty_baseline=0.0 ; empty_mutant=raise:ValueError (np.max of an empty window array)
#H EXPECTED RESULT nonempty_moved=0 count (null control: guard inert on non-empty series)
#H Instrumented symbol: custom_components.heatpump_optimizer.tariff:realised_peak, line 1225 `if house.size == 0:`;
#H   production caller optimizer.py:5657 (Optimizer._grid_report, unmasked branch: realised_peak(total_power, ...)).
#H Perturbation: key 2d037a10caa62e28 GUARD_OFF `    if house.size == 0:` -> `    if False:`, in memory.
#H   Direction: 0.0 -> ValueError.
#H Null control: non-empty series, where the guard is false either way.
from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402
mut = mutant(tf.realised_peak, "    if house.size == 0:", "    if False:")
moved_empty = 0
for wm, dt, off in ((15, 0.25, 0), (60, 0.25, 2), (60, 1.0, 0)):
    b = outcome(tf.realised_peak, np.array([]), np.array([]), wm, dt, off)
    m = outcome(mut, np.array([]), np.array([]), wm, dt, off)
    moved_empty += not same(b, m)
    if (wm, dt, off) == (15, 0.25, 0):
        print(f"RESULT empty_baseline={show(b)}")
        print(f"RESULT empty_mutant={show(m)}")
print(f"RESULT empty_forms_moved={moved_empty} count (of 3)")
rng = np.random.default_rng(3)
nm = 0
for n in (1, 4, 7, 96):
    p, bl = rng.uniform(0, 5, n), rng.uniform(0, 1, n)
    nm += not same(outcome(tf.realised_peak, p, bl, 60, 0.25, 1), outcome(mut, p, bl, 60, 0.25, 1))
print(f"RESULT nonempty_moved={nm} count (of 4)")
