# D15-s2 — round 10, baseline fe01b938f71b

Cells: D15.M5, D15.M6 (no file axis).

## D15.M5 timeline replay — unfinished
The bundle's `debug.replay` is null and no `tools/replay/export.py` document
was supplied, so `debug_replay.py --bundle` has no replay half to run over.

## D15.M6 monitor re-run — deep, no finding
Harness `m6_monitor.py`: rebuilds `AccuracyTracker` from the bundle's accuracy
store (192 samples, 2026-10-05..2026-10-14), folds each calendar day's
`temperature_bias` into `SnapshotRing.observe_bias`, compares with the stored latch.

- Real bundle, offset 0: window bias 0.221 C, MAE 0.275 C (equal to the
  bundle's `diagnostics.accuracy`); per-day bias 0.22..0.31, all inside
  `BIAS_BAND_C`=0.5; re-run latch False, recorded `alarmed` False, bias_days 0: agree.
- Perturbation offset +1.0 C on actual_temp: bias -0.78, latch trips (bias_days 7), disagrees — the harness moves.
- Null control (dbg_bundle_gen synthetic): offset 0 no trip; +1.0 trips.
- `Cusum` is not on the accuracy_drift path (only `_vent_cusum`, `_cop_health_cusum`); no Cusum latch is recorded to compare.
- Sample days 10-10..10-12 are absent from the capped sample list; the per-day
  re-run cannot cover them.

Command: `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round10/D15/s2/m6_monitor.py --bundle <diag.json> [--offset 1.0]`
