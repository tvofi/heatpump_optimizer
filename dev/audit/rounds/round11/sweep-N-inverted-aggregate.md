# Class sweep: N-inverted-aggregate (round 11, D14 steps 3-4)

Mechanism: an aggregate takes the wrong order statistic (the minimum for a peak, the k smallest for the k largest), understating a billed or tracked figure. Finding in class: D2-s3-05 (`tariff._one_per_day`).

## Enumerator

`HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep_n_inverted_aggregate.py`

It lists every sort, max, min, keep-compare or top-k slice inside a peak, top-k, threshold or ranked function in every module of the package (17 seams; it starts from the finding's seam_rule `_one_per_day|distinct_days`). Then it probes each aggregate on a fixture with a known answer: for x=[1,9,2,8,3] the top-2 sum is 17 and the top-1 is 9; a day with 1 and 5 kW keeps 5; the billed mean of the top 2 of [9,8,1] is 8.5.

- Positive control: `--perturb oneperday` (the finding's planted re-introduction, `kw > best` to `kw < best`) gives INSTANCES 1 on `_one_per_day`, which re-finds D2-s3-05.
- Null control: the tree at `handoff/audit-r11-register` and the finding's baseline 92d38ec both give INSTANCES 0.
- Perturbation: the one-line change above moves the count from 0 to 1.

The finding's value comes from a planted copy. At both the baseline and this tree the line already reads `kw > best[day][0]`, so the site is not a live instance here.

## Dispositions

| seam | disposition |
|---|---|
| tariff.py:491 `_one_per_day` | judged site (D2-s3-05); the probe passes at the tree and fails on the planted copy |
| tariff.py:328 `_close_window` sort reverse=True | guarded: descending sort, which the `_billed_peak_kw`/`threshold_kw` reads depend on |
| tariff.py:392-393 `threshold_kw` peaks[n-1]/peaks[-1] | guarded: reads the nth entry of a descending list (sorted at 328/532) |
| tariff.py:500 `_billed_peak_kw` | guarded: probe ok (8.5) |
| tariff.py:532 `_stored_peaks` sort reverse=True | guarded: restores in descending order |
| tariff.py:749/760, 805/816 smooth top-k max/min | guarded: probes ok (17 within 0.5); the min is only a bisection bracket bound, not the aggregate |
| tariff.py:918 `_exact_topk_sum` [-k:] | guarded: probe ok |
| tariff.py:933/943 `_plateau_aware_topk_sum_batch` | guarded: probe ok |
| tariff.py:955 `_plateau_aware_topk_sum` | guarded: probe ok |
| tariff.py:1150 `_day_peaks_batch` top-1 | guarded: delegates to the probed top-k with k=1 |
| tariff.py:1227 `realised_peak` np.max | guarded: max of the metering windows, as documented |
| topology.py:959 `rank_sensor_gaps` | not applicable: ranks sensor gaps by value, not a billed or tracked peak |

Instances beyond the finding: 0. No barrier is proposed; the probe set can be promoted to a `tests/` script if the class gains an instance. `dev/audit/config/bugclasses.json` has no entry for this class at this tree.
