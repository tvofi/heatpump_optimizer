# Class sweep: N-period-rollover (round 10, phase D)

Base: `handoff/audit-r10-register` at 9355f107d. Method: `dev/governance/dimensions/D14.md` steps 3-4.

**Class mechanism.** A period reset runs before the open window is closed, so the
period's last window never reaches the period's aggregate. Finding: D2-s3-01.

**Ledger status.** `dev/audit/config/bugclasses.json` has no `N-period-rollover`
entry at this ref, so the class has no status yet (it is `open` by default). The fold has to add it.

## Enumerator

`python3 dev/audit/rounds/round10/D14/period_rollover_seams.py [ROOT] [--fixture]`

The enumerator is an AST scan of the whole package. A seam is an `if` that compares a newly derived
period key (a month, day, date, window, week or key name) with a stored `self.` attribute using `!=`.
A seam is **unsafe** when the branch resets `self.` accumulator state (`[]`, `{}`, `0`, `""`,
`None` or `.clear()`) before any call that could fold or close the open period.

| control | command | result |
|---|---|---|
| package | (no args) | `seams=5 unsafe=2` |
| positive (re-finds D2-s3-01) | (no args) | `tariff.py:234 observe [month != self.month] unsafe` |
| null (clean close-then-reset fixture) | `--fixture` | `seams=1 unsafe=0` |
| perturbation, fix (copy of tariff.py with `self._close_window(tariff)` added first in the branch) | `<copy dir>` | tariff `unsafe` 1 -> 0 (`seams=2 unsafe=0`) |
| perturbation, one-line re-introduction (reset without close) | `<dir with that file>` | `seams=1 unsafe=1` |
| behavioural probe | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D2/s3/month_last_window.py` | `last_window_reached=0 of 24`; `--perturb` 24 of 24 |

## Dispositions (every seam returned)

| seam | disposition | why |
|---|---|---|
| `tariff.py:234 PeakTracker.observe` `month != self.month` | **instance** (the D2-s3-01 site, beyond_finding=false) | resets `peaks`/`_window_*` without calling `_close_window`; probe `month_last_window.py` fails, 0 of 24 |
| `tariff.py:251 PeakTracker.observe` `key != self._window_key` | guarded | `self._close_window(tariff)` is the branch's first statement |
| `power_guard.py:108 PowerGuard.update` `window_key != self._window_key` | not applicable | the reset clears the hysteresis counters `_over_count`/`_clear_count`, not a period aggregate. Releasing the suppression on window change is the documented intent, and the sample still counts toward the new window |
| `coordinator.py:8943 _track_curve_comfort` `day != self._curve_day` | guarded | `self._curve_learner.record_day(now, self._curve_day_worst)` folds the closing day before `_curve_day_worst` is reset |
| `dhw_learning.py:550 async_learn_usage` `daytype_last_day[idx] != day` | not applicable | it counts distinct days, and nothing is reset |

Keyed-dict period accumulators that the AST pattern cannot see. I checked these by reading the code, not by running anything:
- `wear.py StartCounter`: increments `months[strftime("%Y-%m")]` and keeps no open window. Not applicable.
- `accuracy.py` promises: stored per day and pruned to the newest `PROMISE_DAYS`, with no reset. Not applicable.
- `ledger.roll_receipts` / `coordinator._roll_month`: freezes every ledger month `< current`, working from the ledger itself. Guarded against loss at rollover. Its capacity line reads `PeakTracker`, so it inherits D2-s3-01's lost window. Corrected by R10-TARIFF (#2230): the one-line fix shape (close before the reset) does **not** close it. The closed window is wiped by the same reset, and the month's last booking was made at the settlement before, so `dev/audit/harnesses/r10_month_last_window_billed.py` reads `billed_spike_reached=0 of 24` under that shape as at the baseline. The fix keeps the closed month's peaks on the tracker (`PeakTracker.billing_statements`) and `_roll_month` books them before the freeze: 24 of 24.

**Count:** 1 instance, which is the judged site itself, and 0 instances beyond the finding. Of the other seams, 2 are guarded and 2 are not applicable.

## Proposed barrier

One instance does not justify a permanent check yet (`defect-root-cause.md`'s cost test). Two things should land with the D2-s3-01 fix:
- `month_last_window.py`'s assertion (24 of 24) as a regression test in `tests/`.
- Optionally, this enumerator as a lint over `custom_components/` at near-zero gate cost: an AST pass that takes well under a second.
