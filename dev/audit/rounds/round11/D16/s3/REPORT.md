# D16-s3 — round 11, actuator write: hold and release (M5), restore (M6)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B11 (shared). Cells: `check_scopes.py --seat D16-s3`
prints `M5+M6` over every package file (95 lines). The hold and write sites all sit in `coordinator.py`,
`heat_curve.py`, `inputs.py`, `off_restore.py` and `pump_arbiter.py`; the rest carry none (`enumerate.py d16-writes`).
Exposure: none (no `docs/`, no GitHub).

## Method

- **M5** ranges over `python3 tools/audit/enumerate.py d16-writes | grep '^hold'` (30 lines). `m5_holds.py`
  enters each latch through production (a write that raises, a reading that goes unavailable, a target the
  entity ignores, a full day's cap, an option pair, a misdeclared range, a stamp ahead of the clock, a worker
  timeout, an empty price/weather/solar input), then lets the plant alone clear it, and counts the service calls
  to the held entity afterwards. A latch that gates no write is held on while a fresh-plan cycle runs, and the
  writes are counted.
- **M6** ranges over `python3 dev/audit/rounds/round11/D16/s3/enum_m6.py`: each write site times off, unload,
  remove and a duty-mode change (32 lines). `m6_restore.py` runs the real coordinator on `coord_all_features`
  with every actuator slot configured. The harness builds the plan itself: a hot-water-only step and then an idle step
  on a Tuya select, space-only steps on a Modbus select, and the same with the disinfection program held on.
  It then fires each trigger through production (`async_set_mode`, `async_unload_entry`, `async_remove_entry`, an
  observe-mode reload) and compares each written entity's state with its pre-write baseline. Null arm: the plan
  starts two hours ahead and every command equals its baseline, so all nine `null_unrestored_*` arms read 0.

Every number is a count (contention-immune); `thread_factor=1.000`, `load1` 1.7-2.0.

## Findings

| id | step | severity | claim | number | perturbation |
|---|---|---|---|---|---|
| D16-s3-01 | M6 | high | Entering Off leaves the arbiter's mode (Tuya: DHW only) and a Modbus tank set-point (gate 40, not 50) at the optimizer's last write | `unrestored_off__select.pump_mode=1`, `unrestored_off_modbus__number.dhw_set=1` | `--perturb arbiter` (Off writes release()'s baseline row): both 0 |
| D16-s3-02 | M6 | high | Power switch, frequency, valve target and circulation pump have no restore owner: off, unload and remove leave them at the optimizer's value (the pump switched off on an idle step stays off after removal) | `unrestored_{off,unload,remove}_unregistered=4` | `--perturb consumers` (registered with off_restore): 0 |
| D16-s3-03 | M6 | high | Unload or remove during a held disinfection run leaves the tank set-point at 60 (cycle target), not the configured 50: release() reads the live memo | `unrestored_unload_disinfecting__number.dhw_set=1` | `--perturb memo` (hold dropped before release): 0 |
| D16-s3-04 | M5 | medium | A restore that fails at the change into Off is never retried while Off: space set-point keeps the gate 25 (not 45), heat-curve offset keeps +3 K | `writes_again_off_restore_failed_while_off=0`, `..._neutral_...=0` over 6 h | `--perturb retry_off_restore`: 1 each, finals 45 and 0 |

D16-s3-01 changes a rule the tree pins on purpose. The `pump_arbiter` docstring says *"The mode, the hot-water
set-point and the silent switch are not restored"*, and `tests/features.py` checks that Off writes *"the space
set-point's baseline back, once, and nothing else"*. The brief's off row (owner ruling 2026-11-15) owes each
written entity its baseline.

## Non-findings

- The space set-point, the heat-curve offset, both ECL110 MQTT topics and the disinfection switch go back to
  baseline once on off, unload and remove. `restored_more_than_once_*` is 0 in every arm.
- Unload, remove and the duty-mode reload write the arbiter's baseline row through `pump_arbiter.release`.
- Every `heat_curve.py` hold releases without a person. Its next target, a returning entity, a landed write and
  the 24 h window each give `writes_again_*=1`.
- The worker and off-loop timeouts release on the next job.
- The price, weather, solar and solve-failure latches gate no write. Five were held and the cycle still made
  9 calls.
- An unreadable space baseline holds the write until the controller reports again.
- A failed valve write is retried on the next cycle. Both option flows refuse the flow kind without two zones.
- An input stamped ahead of the clock is released once the clock passes the stamp.
- The misdeclared-indoor guard is released by the entity's range or the unit option, both corrections of
  configuration.
- No writer escapes `enumerate.py d16-writes`.

## Unfinished

- M6: the silent-switch and night-mode slots of `pump_arbiter.py:1610` were not driven. The site's cells were
  examined through its mode and tank slots. The space circulation pump was not configured; its hot-water twin was.

## Leads

- **D16-s1:** under `pump_duty_mode` observe, the supply, frequency, valve, circulation-pump, heat-curve and MQTT
  writers keep writing. In the duty_change arm the reloaded coordinator writes each of them again.
- **D16-s1:** `enumerate.py` lists only `log_held` holds. These write-gating latches have no line:
  `_freq_fallback`, `ArbiterState.retry/misses`, `supply_hold`, the early cut-off and `DisinfectionSwitch.memo`.
- **D1-s3:** after `WORKER_FALLBACK_CAP`, `_await_optimize` never tries the in-process solve again. A deterministic
  worker fault therefore stops every write, with no automatic release.
- **D16-s2:** `desired(..., None, ...)` carries the cycle target into any baseline row served during a cycle step.

## Harnesses

`m6_restore.py`, `m5_holds.py` and `enum_m6.py`, all under this directory. Each header gives its command, the
expected values and its perturbations.
