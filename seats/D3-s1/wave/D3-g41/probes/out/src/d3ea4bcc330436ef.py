#H Metric: count of batch inputs on which tariff.peak_cost_batch's per-row cost array differs (value or exception) between
#H   baseline and mutant; secondary: rows sent to _plateau_aware_topk_sum_batch (work, not value).
#H EXPECTED RESULT moved_inputs=0 count (excess = max(0, .), so a row with no positive excess costs 0 either way)
#H Instrumented symbol: custom_components.heatpump_optimizer.tariff:peak_cost_batch, line 1196
#H   `above = np.flatnonzero(np.any(excess > 0, axis=1))`.
#H Perturbation: key d3ea4bcc330436ef CMP_BOUND `excess > 0` -> `excess >= 0`, in memory. Direction if it moved: a below-
#H   threshold row's cost 0 -> nonzero.
#H Null control: the baseline function against itself.
from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402
mut = mutant(tf.peak_cost_batch, "    above = np.flatnonzero(np.any(excess > 0, axis=1))",
             "    above = np.flatnonzero(np.any(excess >= 0, axis=1))")
rng = np.random.default_rng(11)
tried = moved = null = 0
for n in (0, 1, 4, 8, 24, 96):
    for B in (1, 3, 7):
        mats = [rng.uniform(0, 4, (B, n)), np.zeros((B, n)), np.full((B, n), 2.5)]
        if n:
            m2 = rng.uniform(0, 4, (B, n)); m2[0, 0] = np.nan; mats.append(m2)
        for M in mats:
            for thr in (0.0, 1.0, 2.5, 5.0, 100.0, np.inf):
                for price in (0.0, 1.0, 37.5):
                    for k in (1, 3):
                        for dd in (False, True):
                            for wf in (None, np.ones(max(n, 1)), np.zeros(max(n, 1))):
                                bill = tf.PeakBilling(threshold_kw=thr, price_per_kw=price, window_minutes=15,
                                                      dt_hours=0.25, peaks_averaged=k, window_factors=wf,
                                                      window_days=(np.arange(n) // 4) if dd else None, distinct_days=dd)
                                base = np.zeros(n)
                                b, m = outcome(tf.peak_cost_batch, M, base, bill), outcome(mut, M, base, bill)
                                tried += 1
                                moved += not same(b, m)
                                null += not same(b, outcome(tf.peak_cost_batch, M, base, bill))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null} count")
rows = []
real = tf._plateau_aware_topk_sum_batch
spy = lambda c, k: (rows.append(c.shape[0]), real(c, k))[1]  # noqa: E731
M = np.array([[1.0, 1.0, 1.0, 1.0], [3.0, 3.0, 3.0, 3.0], [0.5, 0.5, 0.5, 0.5]])
bill = tf.PeakBilling(threshold_kw=2.0, price_per_kw=10.0, window_minutes=15, dt_hours=0.25, distinct_days=False)
with mock.patch.object(tf, "_plateau_aware_topk_sum_batch", spy):
    vb = tf.peak_cost_batch(M, np.zeros(4), bill); rb = sum(rows); rows.clear()
    vm = mut(M, np.zeros(4), bill); rm = sum(rows)
print(f"RESULT work_rows_costed_baseline={rb} count")
print(f"RESULT work_rows_costed_mutant={rm} count")
print(f"RESULT work_case_value_baseline={show(('ok', vb))}")
print(f"RESULT work_case_value_mutant={show(('ok', vm))}")
# The case the sweep moves on: a row wholly below the threshold (excess all 0) with more than k windows tied at that 0
# peak goes, under the mutant, to the smooth top-k arm instead of the 0 the baseline returns for a row with no excess.
first = None
for n in (4, 8, 24, 96):
    for k in (1, 3):
        M = np.vstack([np.full(n, 1.0), np.full(n, 3.0)])
        bill = tf.PeakBilling(threshold_kw=2.0, price_per_kw=37.5, window_minutes=15, dt_hours=0.25, peaks_averaged=k,
                              distinct_days=False)
        b, m = tf.peak_cost_batch(M, np.zeros(n), bill), mut(M, np.zeros(n), bill)
        print(f"RESULT below_row_cost_n{n}_k{k}_baseline={b[0]!r} ; mutant={m[0]!r} (price units; row 2's cost {b[1]!r} / {m[1]!r})")
        if first is None and b[0] != m[0]:
            first = (n, k, b[0], m[0])
print(f"RESULT first_moved_case={first}")
sc = tf.peak_cost_smooth(np.full(24, 1.0), np.zeros(24), tf.PeakBilling(threshold_kw=2.0, price_per_kw=37.5,
                         window_minutes=15, dt_hours=0.25, peaks_averaged=3, distinct_days=False))
print(f"RESULT scalar_peak_cost_smooth_below_row={sc!r} (the scalar twin the batch must match, #948)")
# The sweep's every moved input holds a NaN window: NaN excess is not > 0, so the baseline leaves a row whose other windows
# sit at or below the threshold uncosted (0); the mutant's `>= 0` admits it on the zero windows and the NaN reaches top-k.
import warnings  # noqa: E402
warnings.simplefilter("ignore", RuntimeWarning)
row = np.array([[np.nan, 1.0, 1.0, 1.0], [3.0, 3.0, 3.0, 3.0]])
bill = tf.PeakBilling(threshold_kw=2.0, price_per_kw=37.5, window_minutes=15, dt_hours=0.25, peaks_averaged=1,
                      distinct_days=False)
b, m = tf.peak_cost_batch(row, np.zeros(4), bill), mut(row, np.zeros(4), bill)
sc = outcome(tf.peak_cost_smooth, row[0], np.zeros(4), bill)
print(f"RESULT nan_row_cost_baseline={b[0]!r} ; nan_row_cost_mutant={m[0]!r}")
print(f"RESULT nan_row_scalar_peak_cost_smooth={show(sc)}")
print(f"RESULT nan_row_finite_row_cost_baseline={b[1]!r} ; mutant={m[1]!r}")
