# D2-s3 report (round 10, baseline 17f1c55fad1b)

Cells: D2.M3, D2.M4, D2.M5 over `**`.

## Findings

### D2-s3-01 (M4) The last metering window of every month never reaches that month's billed peaks
`tariff.PeakTracker.observe` resets `peaks` and the open-window accumulators on the
first sample of a new month without calling `_close_window` first, so the final
window (23:00-24:00, or 23:45-24:00 at 15 min) of each month is discarded: it
is never in `peaks`, so `billed_peak_kw` and the ledger capacity line
(`coordinator._roll_month` -> `book_capacity`) never see it.
Harness: `month_last_window.py` -- 1.0 kW month with a 5.0 kW last window, 12 months x {15, 60} min.
Baseline: `last_window_reached=0 of 24`, max billed 1.000 kW. Perturbation
(close the window before the reset): `24 of 24`, 5.000 kW.

## Non-findings
- M3: `predicted_cost == sum(price * max(space+dhw - pv_surplus, 0) * dt)` on all 50 golden fixtures carrying it; max |diff| 1.3e-4 (rounding of stored arrays), shoulder/summer_dhw_only via the PV-netted form.
- M5: `sysid.identify` on an exact first-order plant: clean/drift median |UA err| 0.0000; white 0.05 C and 0.1 C quantised arms 3.0 % / 3.6 % median with 0 fits admitted at confidence >= 0.3 (`sysid_bias.py`).

## Unfinished
- M3: savings identity, terminal-credit sign vs re-simulated continuation, penalty scaling with price_weight, gradient vs finite difference -- not measured.
- M4: DST 23/25-h price folding, grid-fee window sweep, currency conversion -- not measured beyond code reading.
- M5: COP and heat-loss learner clamps -- not measured.

## Exposure
none
