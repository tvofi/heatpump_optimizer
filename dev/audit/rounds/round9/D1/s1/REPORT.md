# Round 9, D1 (robustness and stability), seat D1-s1

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), box B4, export
`/home/claude/audit-r9-baseline`, Python `/home/claude/venv-r9/bin/python`,
`PYTHONPATH=tests/hastub`. Cells: D1.M1-M6 over `store, ledger, snapshots,
dhw_learning, comfort_learning, curve_learning, sysid, accuracy, drift, wear,
diagnostics`.

Exposure: none. I read no earlier-round evidence (nothing under
`tools/audit/round3..round8`, no `docs/audit-*`). The only file I read under
`tools/audit/round9/` is `BASELINE.md`.

## Method

- **M2, store corruption (deep).** `fuzz.py` runs 250 seeded mutants per
  payload over 8 persisted payloads, 2000 in all. The payloads are the ledger,
  accuracy, comfort, curve, wear, the drift CUSUM, the snapshot ring and the
  DHW profile. The DHW profile is also run through its snapshot-restore twin,
  `apply_payload`. The mutation operators are:
  - type swaps and missing keys
  - NaN and ±inf, as numbers and as strings
  - negative values, `1e308` and `10**400`
  - wrong nesting and truncation
  - strings in place of containers
  - numeric strings and naive timestamps

  Each mutant is saved and re-read through the real `QuarantiningStore`, using
  Home Assistant's own orjson codec (`--stub-json` keeps the stub's stdlib
  json). The mutant is then passed to the real loader, and two cycles of
  consumer operations run on the result. The run counts loader raises,
  cycle-1 raises, cycle-2 repeats, non-finite outputs and WARNING lines.
  Directed harnesses follow each signature it found: `naive_ts.py` and
  `snap_restore.py`.
- **M3, staleness (deep for drift, snapshots and curve).** `clock_jump.py`
  covers a timestamp persisted while the clock ran ahead and re-read after it
  was corrected. It runs on the Europe/Stockholm clock across the 2026-03-29
  DST change. `naive_ts.py` also freezes the aware clock over 21 days.
- **M4, executor boundary (deep).** `mid_solve.py` takes the real
  `_solve_snapshot`. It then runs every loop-side writer of the learners in
  these cells that reach the solve: the DHW pattern and cooling rate, and the
  comfort weight. A real `ThreadPoolExecutor` worker reads the snapshot while
  the writers run.
- **M1, lifecycle (deep, for store.py's read gate).** `store_gate.py` runs on
  a real asyncio loop with an executor-backed load. It covers four cases: a
  normal read, a read cancelled mid-flight, a backend that raises, and two
  overlapping reads.
- **M5, guards (spot).** I injected exceptions through M2's corruptions and
  followed each one to the guard that swallows it.
- **M6, external input (deep for the one consumer in these cells).**
  `dhw_glitch.py` drives `DhwProfileLearner.async_learn_dynamics` with
  thermometer fault values.

## Findings

### D1-s1-01: a tz-naive stored timestamp raises on every cycle at three sibling seams (medium, P1)

Three loaders parse a persisted ISO timestamp with `datetime.fromisoformat` and
do nothing about a missing timezone:

- `SnapshotRing.from_dict`, which feeds `due`
- `CurveLearner.from_dict`, which feeds `_step_down`
- `ComfortLearner.from_dict`, which feeds `_decay`

The consumers subtract that value from an aware `now`. Two sibling seams already
apply a rule for this. `drift.Cusum.load` treats a naive time as UTC, and
`AccuracyTracker.from_dict` drops a naive `lead_pending` entry. These three do
not. The failure repeats on every call, because nothing rewrites the leaf.

Measured by `naive_ts.py` over 21 days on an aware clock:

| arm | snapshot heartbeat raises | snapshots taken | curve `record_day` raises | comfort override raises | comfort quiet-period raises | sibling seams raise |
|---|---|---|---|---|---|---|
| naive | 21 | 0 | 19 | 21 | 21 | 0 |
| `--aware` (control) | 0 | 3 | 0 | 0 | 0 | 0 |
| `--fix` (fromisoformat treats naive as UTC) | 0 | 3 | 0 | 0 | 0 | 0 |

`fuzz.py` found the same three signatures without being pointed at them: 7
comfort mutants, 1 curve mutant and 1 snapshot mutant. Every one of them raised
again in cycle 2. With `--fix-ts` all of them go to 0.

What this does in the running integration:

- The #42 weekly snapshot, the bias alarm and the auto-rollback stop
  permanently.
- `coordinator.py:4677` swallows the resulting error at DEBUG, so the only
  trace is a debug line on each cycle.
- The curve bias stays frozen.
- With comfort learning enabled, each setpoint change raises out of
  `climate.async_set_temperature` after the setpoint has already been written.
  `_record_quiet_comfort_period` also raises, from inside
  `async_run_optimization`'s `except Exception`. That handler logs it as a
  solve failure and skips `_command_valve_target`. I read that consequence from
  the code but could not reproduce it end to end: the quiet-period predicate
  did not hold in the scenario I built.

**Property:** no persisted timestamp reaches arithmetic with an aware clock
unless the loader has normalised it to aware.

**Seam rule:** `grep -n "fromisoformat" custom_components/heatpump_optimizer/{snapshots,curve_learning,comfort_learning,accuracy,drift,wear,ledger,dhw_learning}.py`

### D1-s1-02: a snapshot's non-numeric `temperature_bias` makes `best_restore` raise and suppresses the drift repair issue for good (medium, P1)

`SnapshotRing.from_dict` checks only that each snapshot is a dict. In
`best_restore`, `np.isfinite(bias)` raises `TypeError` when `bias` is a string,
a list or a dict. The quarantining store lets a finite numeric string such as
`"0.3"` through unchanged. The method's own docstring says it must never raise.

Measured by `snap_restore.py` over 4 variants of the bias leaf (`"0.3"`,
`"garbage"`, `[0.3]`, `{"v": 0.3}`):

| arm | restore service raises | variants with no `accuracy_drift` issue after 10 out-of-band days |
|---|---|---|
| defect | 4 | 4 |
| `--control` (bias is the number 0.3) | 0 | 0 |
| `--fix` (guarded `float()`) | 0 | 0 |

The drift heartbeat raises on the day the alarm latches, so it never reaches
`_create_issue`. From then on `observe_bias` reports no change, because the
alarm is already latched, and the issue is never raised on any later day.

**Property:** every snapshot leaf that `best_restore`, `due` or
`observe_bias` reads is type-checked at load, or read under a guard.

**Seam rule:** `grep -n "snap.get\|snapshots\[-1\]\[" custom_components/heatpump_optimizer/snapshots.py`

### D1-s1-03: one out-of-range DHW thermometer sample is booked as a physically impossible draw (medium, new)

`async_learn_dynamics` and `async_fold_draw_stats` turn a temperature drop into
drawn energy with no plausibility bound. This harness's tank holds roughly
9 kWh.

Measured by `dhw_glitch.py --day 4`, with one glitch sample on day 4 of a quiet
tank that has a single morning shower each day:

| sample | largest folded occurrence | window p90 |
|---|---|---|
| none (control) | 1.073 kWh | 1.073 kWh |
| −127 °C (DS18B20 disconnected) | 42.218 kWh | 25.760 kWh |
| 85 °C (DS18B20 power-on value) | 8.747 kWh | 5.677 kWh |
| 1e6 | 231757.047 kWh | 139054.657 kWh |

- With `--day 13` the p90 is unmoved, because the outlier sits above the 0.9
  index once a window has 11 or more occurrences. The exposure is therefore a
  young install, plus the outlier's 40-occurrence tenure in the reservoir.
- The p90 is published as `dhw_draw_stats.p90_kwh`. When
  `DHW_QUANTILE_TARGETS` is on, the plan also reads it as a readiness target.
- Perturbation: `--guard` skips samples outside [0, 100] °C. That returns the
  −127 and 1e6 rows to control. The in-range 85 °C spike does not move, so the
  property is a physical bound rather than a range.

**Property:** the energy attributed to one tick or occurrence never exceeds
what the tank can physically deliver.

**Seam rule:** `grep -n "temp_drop\|energy_kwh" custom_components/heatpump_optimizer/dhw_learning.py`

### D1-s1-04: a timestamp stored while the clock ran ahead is trusted verbatim and stretches every stale timeout by the error (low, new)

Three timers compare a persisted time with `now` and never question a stored
time that lies in the future:

- `Cusum.release_if_starved`, the 72 h release of the open-window latch that
  freezes every learner
- `SnapshotRing.due`, the weekly snapshot
- `CurveLearner._step_down`, the weekly rate cap

Measured by `clock_jump.py`, as the day each seam first acts again:

| clock ran ahead by | cusum release | snapshot due | curve step |
|---|---|---|---|
| 0 days (null control) | day 4 | day 8 | day 2 |
| 30 days | day 33 | day 37 | day 31 |
| 365 days | day 369 | day 373 | day 366 |
| 30 days, `--clamp` (clamp the stored time to `now`) | day 4 | day 8 | day 2 |

**Property:** a stored timestamp later than `now` is clamped or treated as
unknown.

**Seam rule:** `grep -n "fromisoformat" custom_components/heatpump_optimizer/{drift,snapshots,curve_learning,comfort_learning}.py`

## Non-findings

- **Ledger, wear, drift CUSUM and DHW profile loaders.** Under
  `fuzz.py --seed 9 --n 250` each shows 0 loader raises, 0 cycle-1 raises and
  0 non-finite outputs, with at most one WARNING line per mutant.
- **Accuracy loader `OverflowError` is a stub artefact.** It raised on 19 of
  250 mutants, but only under `--stub-json`. The gap is in
  `tests/hastub/homeassistant/helpers/storage.py`, which decodes with stdlib
  json: it hands `10**400` back as an exact int. Home Assistant's orjson refuses
  that value on save, and on load it refuses the file or turns the number into
  a float. Under the orjson codec the count is 0.
- **Accuracy summary non-finite output.** One mutant produced it, from
  `predicted_cost = 1e308`, a finite literal: `cost_accuracy` overflows to inf.
  I did not measure whether publication stays clean. The sensor base class's
  non-finite scrub should cover it (tools/audit/README.md), but that is outside
  these cells.
- **Executor boundary.** `mid_solve.py` shows 0 changed solve-input fields.
  With `--share`, which removes the deep copy, the count is 3.
- **Store read gate.** `store_gate.py` shows hung=0 and misordered=0 across the
  cancel, raise and overlap cases. With `--nofinally` it shows hung=2.
- **Sibling timestamp seams already safe.** In `naive_ts.py`,
  `drift.Cusum.load` and accuracy `lead_pending` both show sibling_raises=0.

## Harnesses

All are under `tools/audit/round9/D1/s1/`: `naive_ts.py`, `fuzz.py`,
`snap_restore.py`, `dhw_glitch.py`, `clock_jump.py`, `mid_solve.py` and
`store_gate.py`. Each header gives its command, expected values and
perturbation. Every number above is a count or an energy, so none of them is
contention-sensitive.

## Unfinished

- **M1.** The full coordinator setup, reload and unload cycle belongs to
  D1-s2's cells, so I did not run it. The write-before-read gate is used by only
  one of seven stores; I recorded that as a lead.
- **M3.** Not measured:
  - accuracy lead scoring under backward and forward jumps
  - the ComfortLearner decay when `last_update` lies in the future
  - wear and ledger month keys under a jump to 1970 or to a year ahead
  - `sysid` sample `dt` filtering, which I checked only by reading the code
- **M5.** Two guards are not measured. `dhw_learning.async_load_profile`
  swallows at DEBUG, and the next save may then overwrite a store that failed
  to decode; real Home Assistant's corrupt-file behaviour is not available
  here. `diagnostics._coordinator_snapshot` calls `weather_stale_hours` with no
  guard.
- **sysid.** There is no persisted payload and no external parser in it, so M2
  and M6 do not apply. M3, M4 and M5 were not measured.
