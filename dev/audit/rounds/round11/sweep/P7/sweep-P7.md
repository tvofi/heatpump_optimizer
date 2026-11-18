# Class P7 sweep, round 11 (D14 method steps 3-4)

Class P7 in `dev/audit/config/bugclasses.json` is naive wall-clock datetime
arithmetic across a DST transition. The class row is `barriered`: the barrier is
`tests/dst_checks.py`'s F1.1 DST tracer, which traces `-` and `+ timedelta` on
zoned datetimes. The finding in the class is D2-s3-07 (`ledger.month_hours`
counts 744 h for the 743-hour March). This sweep ran in a detached worktree at
`origin/handoff/audit-r11-register`.

## Property

A span of true time is never derived from a calendar count (days in a month,
an hour-of-day label advanced by elapsed steps) at a fixed day length. On a
transition day or month such a span is off by one hour.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-P7/enumerate_p7.py` is an AST scan of
`custom_components/heatpump_optimizer`. It generalises D2-s3-07's seam_rule
(`def month_hours|monthrange` in ledger.py) to the whole package, in two families:

- **CAL**: a call to `calendar.monthrange`.
- **DAYLEN**: a product, quotient or modulo of a non-constant operand with a
  fixed day length: 24, 1440, 86400, 96, `HOURS_PER_DAY`, `QUARTERS_PER_DAY`,
  or a constant sub-product equal to one of these.

It returns `RESULT seams=59 CAL=1 DAYLEN=58`, saved as `D14/sweep-P7/enumerate.out`.

- **Positive control**: the scan lists `ledger.py:138 month_hours`, which is D2-s3-07's site.
- **Null control**: `--fixture clean` scans a module that uses only UTC elapsed
  time and returns `seams=0`.
- **Perturbation**: `--fixture perturbed` re-introduces one line,
  `h = 24.0 * days`, and returns `seams=1`.

The scan is a text-shape rule and over-matches (hour-label wraps, nominal rates),
so every seam was then dispositioned.

## Probes

Run each probe as:

```
HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components python3 D14/sweep-P7/probe_p7.py <probe> --day spring|autumn|plain
```

Each probe compares the production value against a UTC reference.
`--day plain` (2026-05-10) is the null control: every probe exits 0 on it, and
every instance probe exits 1 on both the spring day (2026-03-29) and the autumn
day (2026-10-25).

| probe | spring | autumn | plain |
|---|---|---|---|
| `month_hours` (ledger.month_hours vs real month hours) | 744 vs 743 FAIL | 744 vs 745 FAIL | 744 vs 744 ok |
| `hours_until_next_window` (01:30 local, window opening 04:00) | 2.5 vs 1.5 FAIL | 2.5 vs 3.5 FAIL | 2.5 ok |
| `simulate_trajectory` (gains hour vs `optimizer._step_clock`) | off 1 h FAIL | off 1 h FAIL | 0 ok |
| `simulate_trajectory_batch` | off 1 h FAIL | off 1 h FAIL | 0 ok |
| `simulate_trajectory_with_dhw` (draw-rate and gains hours) | off 1 h FAIL | off 1 h FAIL | 0 ok |

## Dispositions (59 seams)

### Instances (8 seam lines in 5 symbols)

`instances` = 7 is the count of seam lines with `beyond_finding: true`. They fall in 4 symbols.

- `ledger.month_hours` (ledger.py:138). This is D2-s3-07's site, `beyond_finding: false`.
- `dhw_schedule.hours_until_next_window` (dhw_schedule.py:524, 527). It
  returns the gap between wall-clock hour labels as hours. Across the night of
  a transition, the "hours until the DHW window opens" is 1 h wrong. Three
  callers consume it:
  - `coordinator._dhw_next_window_in_hours`, the published figure.
  - `dhw_planner`'s `next_window`.
  - `pump_schedule.vvc_should_run`'s pre-heat lead, so on the spring night the
    pre-heat starts late.
- `ThermalModel.simulate_trajectory` (thermal_model.py:4404),
  `simulate_trajectory_batch` (4625) and `simulate_trajectory_with_dhw` (4882,
  4928, 4953). Each one advances a float hour of day as
  `start_hour + i*dt_hours`, with `start_hour = step_hours[0]`. After a
  transition inside the horizon, the internal-gains profile and the DHW
  draw-rate pattern are read one hour off the true local hour that
  `optimizer._step_clock` (and the solver's own `step_hours` users,
  `optimizer.py:3973` and `dhw_planner.py:890`) assign the same step. The
  simulated trajectory therefore disagrees with the solve's hour keys for the
  rest of a horizon that straddles the transition.

None of the beyond-finding instances is reached by the F1.1 tracer, which traces
datetime operators only, and these sites do float arithmetic.

### Guarded (14)

- **UTC elapsed time** (10 seams): accuracy, comfort_learning, learner_progress,
  sysid.armable x3, duty_switch, draw_range and coordinator snow x2. Each
  converts a true elapsed span from `utc_elapsed_seconds` or epoch seconds by
  86400.
- **Stored instants** (2 seams): `curve_learning._step_down` and
  `snapshots.SnapshotRing.due`. Both are guarded by the F1.1 tracer, and the
  `drift.stored_instant` offset-aware load sends the subtraction down Python's
  UTC path. This sweep did not prove that a tracer arm reaches them.
- **`tariff._day_peaks` / `_day_peaks_batch`** (2 seams): a midnight-anchored
  day index. It runs only when no `window_days` is supplied, and the optimizer
  supplies `tariff.plan_window_days` (clock-dated) whenever the plan has a start
  time.

### Not applicable (37)

- **Hour-of-day label wraps (`% 24`)** read from a real local timestamp or a
  configured wall window: price_model, quiet_windows.wall_clock, pump_schedule,
  dhw_schedule.hour_in_windows/overlap_fraction, thermal_model's profile
  indexers, `optimizer.py:3973`/`5933` and `dhw_planner.py:890`/`954` (these use
  the true `step_hours`).
- **Nominal rates and table shapes**: per-day/per-hour conversions of a
  configured or learned quantity, configured interval days as hours (legionella,
  dhw_planner), 24-slot profile lengths, and price_tiles' horizon scaling.
- **`ledger.pro_rata_factor`**: a calendar-day ratio by definition, used as the
  fallback.

The full per-seam reasons are in `sweep-P7.json`.

## Barrier

The class row says `barriered`, but the F1.1 tracer cannot reach this
sub-family: calendar counts, and float hour-of-day arithmetic advanced from a
start hour. `barriered` in this report is therefore `false`.

Proposed barrier: add `enumerate_p7.py`'s DAYLEN/CAL rule to `tests/dst_checks.py`
as a zero rule with a dispositioned allow-list (the 51 guarded or not-applicable
seams above), with this file's probes as its positive arms. Its cost is the AST
scan, under 1 s of gate time.

`root-cause.md`'s record for P7 is RCA-BULK-1, cited in the class row.
