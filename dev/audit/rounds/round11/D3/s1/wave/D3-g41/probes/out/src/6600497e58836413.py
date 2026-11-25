#H Metric: (a) tariff.window_factors' return for n_windows = 0 with an active #13 mask (None vs an array); (b) count of
#H   downstream consumer outputs (billed_windows, peak_cost, peak_cost_smooth, the _grid_report peak figure from each of its
#H   two branches) that differ between the baseline and mutant factors.
#H EXPECTED RESULT direct_n0_baseline=None ; direct_n0_mutant=[] (size-0 float array)
#H EXPECTED RESULT downstream_moved=0 count (every consumer reads a size-0 factor array as None: billed_windows line 873)
#H Instrumented symbol: custom_components.heatpump_optimizer.tariff:window_factors, line 674
#H   `if start_time is None or n_windows <= 0 or not mask_active(tariff):`; production caller optimizer.py:4155
#H   (Optimizer._peak_window_factors), where n_windows = metering_windows(np.zeros(n_steps)).size is 0 only for n_steps 0.
#H Perturbation: key 6600497e58836413 CMP_BOUND `n_windows <= 0` -> `n_windows < 0`, in memory. Direction: None -> [].
#H Null control: n_windows in (1, 24), where both arms return the same factors; and n_windows = -1.
from datetime import datetime, timezone  # noqa: E402
from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402
mut = mutant(tf.window_factors,
             "    if start_time is None or n_windows <= 0 or not mask_active(tariff):",
             "    if start_time is None or n_windows < 0 or not mask_active(tariff):")
mask = tf.CapacityTariff(enabled=True, window_minutes=60, months=frozenset({1, 2}), peak_hours=(7, 8, 9),
                         weekdays_only=True, offpeak_factor=0.5)
assert tf.mask_active(mask)
start = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
b0, m0 = outcome(tf.window_factors, mask, start, 0, 0.25), outcome(mut, mask, start, 0, 0.25)
print(f"RESULT direct_n0_baseline={show(b0)}")
print(f"RESULT direct_n0_mutant={show(m0)}")
nullm = sum(not same(outcome(tf.window_factors, mask, start, n, 0.25), outcome(mut, mask, start, n, 0.25))
            for n in (1, 24, -1))
print(f"RESULT null_moved={nullm} count (of 3: n_windows 1, 24, -1)")
fb, fm = b0[1], m0[1]
down = tried = 0
empty = np.array([])
for thr in (0.0, 2.0):
    billb = tf.PeakBilling(threshold_kw=thr, price_per_kw=40.0, window_minutes=60, dt_hours=0.25, window_factors=fb)
    billm = tf.PeakBilling(threshold_kw=thr, price_per_kw=40.0, window_minutes=60, dt_hours=0.25, window_factors=fm)
    for f in (tf.peak_cost, tf.peak_cost_smooth):
        tried += 1
        down += not same(outcome(f, empty, empty, billb), outcome(f, empty, empty, billm))
tried += 1
down += not same(outcome(tf.billed_windows, empty, fb), outcome(tf.billed_windows, empty, fm))
# _grid_report's two branches (optimizer.py:5656-5674): factors None -> realised_peak; else billed window max or 0.0
def grid_peak(factors):
    if factors is None:
        return tf.realised_peak(empty, empty, 60, 0.25, 0)
    w = tf.metering_windows(empty, 60, 0.25, 0)
    return float(np.max(tf.billed_windows(w, factors))) if w.size else 0.0
tried += 1
gb, gm = outcome(grid_peak, fb), outcome(grid_peak, fm)
down += not same(gb, gm)
print(f"RESULT grid_peak_baseline={show(gb)} kW")
print(f"RESULT grid_peak_mutant={show(gm)} kW")
print(f"RESULT downstream_tried={tried} count")
print(f"RESULT downstream_moved={down} count")
