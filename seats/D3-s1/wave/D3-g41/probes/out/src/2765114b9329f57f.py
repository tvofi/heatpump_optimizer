#H Metric: count of inputs (series x window x step x offset) on which tariff.metering_windows' output (value or raised exception)
#H   differs between baseline and mutant.
#H EXPECTED RESULT moved_inputs=0 count (pieces is never empty for a non-empty series; the empty series returns before it)
#H Instrumented symbol: custom_components.heatpump_optimizer.tariff:metering_windows, line 588 `if not pieces:`.
#H Perturbation: key 2765114b9329f57f GUARD_OFF `    if not pieces:` -> `    if False:`, in memory (function re-compiled from its
#H   own source with the line swapped). Direction if it moved: a [mean] fallback -> ValueError from np.concatenate([]).
#H Null control: the baseline function against itself (null_moved must be 0).
from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402
mut = mutant(tf.metering_windows, "    if not pieces:", "    if False:")
series = [np.array([]), np.array([np.nan]), np.array([np.inf, -np.inf]), np.array([1e308, 1e308])]
series += [np.arange(n, dtype=float) for n in range(1, 26)]
tried = moved = null = 0
for h in series:
    for wm in (0, 1, 7, 15, 30, 60, 120, 1440):
        for dt in (0.0, 1e-9, 1 / 60, 1 / 12, 0.25, 0.5, 1.0, 2.0):
            for off in (-7, -1, 0, 1, 3, 5, 1000):
                b = outcome(tf.metering_windows, h, wm, dt, off)
                m = outcome(mut, h, wm, dt, off)
                tried += 1
                moved += not same(b, m)
                null += not same(b, outcome(tf.metering_windows, h, wm, dt, off))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null} count")
