# Class sweep: N-silent-zero (round 11, PLAN phase D)

Mechanism: a derivation's failure path returns the same empty value as its
success path, so a count over a set never enumerated reads as a clean zero.
Status in `dev/audit/config/bugclasses.json`: `kind: instrument`, rounds [10],
2 instances in round 10, barrier = the census arm of `field_coverage.mjs`
(it registers `structure.py` dead_* only). None of this round's sites is
registered there, so the barrier does not reach the class as it stands.

Baseline: `handoff/audit-r11-register` at 28b864af6d (detached worktree).

## Detector (D14 step 3)

`python3 dev/audit/rounds/round11/D14/sweep-N-silent-zero/enumerate.py`
lists every seam in four families, each the generalised seam_rule of a
verified finding:

| family | rule | from |
|---|---|---|
| R1 | a service-schema `cv.string` field other than an id, parsed later | D10-s1-01 |
| R2 | a platform action (`async_press`, or any action handing work to `off_the_action` / `publish_then_refresh`) in button, switch, datetime, climate | D10-s1-02 |
| R3 | a replay/debugger line printing a count or verdict derived by `N - len(...)` or `.get(..., 0)`, a `spread(...)` field, and a bundle generator that never drives `SnapshotRing.observe_bias` | D15-s1-03, D15-s2-03, D15-s3-01 |
| R4 | the snapshot restore selectors `best_restore`, `undo_target` | D17-s3-03 |

Controls (`controls.py` in the same folder, exit 0):

- positive: `positive_refound=7/7` (the six findings; D10-s1-02 has two sites)
- null: `null_seams=0` on a clean fixture tree
- perturbation: `perturbed_seams=1` with one planted `cv.string` field

Count on the baseline: `COUNT 34`.

## Dispositions (D14 step 4)

| seam | disposition |
|---|---|
| services.py `return_time@183` | instance: D10-s1-01 (`D10/s1/svc_set_away.py`) |
| services.py `dhw_windows@148,250,496` | guarded: `parse_windows` / `parse_weekly_windows` raise `ServiceValidationError` (`*_invalid_dhw_windows`). Read, not executed |
| services.py `quiet_silent_windows`, `quiet_off_windows` @152,153,254,255,499,500 | guarded: `_quiet_schedule_fields` / `_canonical_quiet_spec` refuse with the `*_invalid_quiet_windows` keys. Read, not executed |
| services.py `expires_at@284` | guarded: services.py 1124-1141 raises `manual_plan_invalid_expires_at` |
| button.py `ForceOptimizationButton.async_press` | guarded: raises `HomeAssistantError` on any non-None reason |
| button.py `SystemIdentificationButton.async_press` | instance: D10-s1-02 |
| button.py `DiagnoseIntervalButton.async_press` | instance: D10-s1-02 |
| button.py `ResetComfortWeightButton` / `ResetHeatLossButton.async_press` | guarded: the reset is awaited in the press and its exception propagates. Only the refresh runs off the action |
| button.py `DebugFinalizeButton.async_press` | guarded: `available` is False when `collector_for` is None or final, and HA refuses a press on an unavailable entity |
| switch.py `OptimizerEnableSwitch.async_turn_on/off` | not applicable: turning on a switch that is already on is a correct no-op, and `async_set_mode` is awaited |
| switch.py `AwaySwitch.async_turn_on/off`, datetime.py `AwayReturnDateTime.async_set_value` | guarded: `async_set_away` is awaited and HA types the datetime value. The string path is R1's `return_time` |
| **switch.py `TimedDutySwitch._press`** | **instance, beyond the findings**: `boost.set_block` drops a refused on-press (live safety floor) and returns normally, so the switch action reports success for a block that never took effect. This is D10-s1-02's shape on a fourth action. Probe: `D14/sweep-N-silent-zero/probe_block_refusal.py` -> `refused_presses_acknowledged=1`, exit 1. With `--clean`: blocked=1, 0, exit 0 |
| climate.py `_async_set_mode` | guarded: `async_set_mode` is awaited. The displace publish after the refresh is logged, and it is a side effect, not the action's result |
| debug_ingest.py `stages_ok@297`, `smoke_verdict@298` | instance: D15-s1-03 |
| **debug_replay.py `line@215` + `smoke_verdict@219`** (one seam) | **instance, beyond the findings**: a zero-width window replays 0 cycles, every `counts.get(name, 0)` reads 0, and `smoke_verdict=pass`, exit 0. Probe: `D14/sweep-N-silent-zero/probe_replay_empty_window.py` -> `vacuous_pass=1`, exit 1 |
| debugger.py `missing@267` (sensor_sanity range) | guarded: `missing` is printed next to the range, so an absent field is counted rather than read as zero |
| debugger.py `row_gaps_h@294` | not applicable: fewer than two stamps gives None, not a zero spread, and `cycles` is printed beside it |
| debugger.py `week_solve_ms@330` | instance: D15-s3-01 |
| dbg_bundle_gen.py `snapshot_ring_without_observe_bias` | instance: D15-s2-03 |
| snapshots.py `best_restore` | instance: D17-s3-03 |
| snapshots.py `undo_target` | guarded: it returns the reset's undo point only (user-held by its documented rule) and otherwise delegates to `best_restore`. That instance is already counted |

Totals: 9 instances (7 judged sites, 2 beyond the findings), the rest guarded
or not applicable. `instances` = 2 (beyond_finding true).

## Proposed barrier

The class is not barriered. Each family needs its own barrier:

- R2: a `tests/` check that drives every platform action under a refusal and
  requires it to raise, as the D10 harness does for the two buttons.
  `TimedDutySwitch` joins that check.
- R3: register `debug_replay` and `debug_ingest` in `field_coverage.mjs`'s
  census, so a run that enumerated nothing must refuse rather than print zero.

The gate-second cost is not measured here.

## Board lines

This sweep surfaced no board lines. The two new instances are recorded here
and in `sweep-N-silent-zero.json` for `fold_ledger.py`. No issue was filed.
