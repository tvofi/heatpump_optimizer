# RCA: the savings estimate books a tank-decided first step

Trigger: a defect reached released versions (v7.0.4 and v7.1.1 measured below), on
the third owner report on savings in three weeks: 2026-10-14 (R10-SAV-BASELINE,
#2255, PR #2411), 2026-10-19 (R10-SAVINGS-NEGATIVE, PR #2463) and 2026-11-04. The
fix is `fix-savings-est`'s, on `handoff/r10-hotfix-sav-estimate`; this seat edits
no production code. Class: **N-unmetered-reference** (minted here), `rca`
`R10-RCA-SAV-ESTIMATE`.

The evidence is the owner's diagnostics export. Only ratios are recorded here.
The tables come from `dev/audit/harnesses/r10_rca_sav_estimate.py`, whose arms are
named beside them.

## Result

- **Cause.** The month row books one step of the thermostat reference per re-plan
  (`optimizer.py` `get_current_action`, `action["baseline_kw"]`). #2411 made that
  step steady by holding the zones and the slab, and left the tanks as measured.
  Behind a valve, the measured tanks decide the step. Two independent mechanisms
  each zero its space term, so the fixer's report is true but incomplete.
- **Process state.** (c): the process was followed and did not produce the
  intended result.
- **Cost test.** Passes: at most 2.1 h per release against 6.8 h per release.
- **Audit class.** Yes: six instances in round 10, so a barrier is owed rather
  than a refusal.
- **Countermeasure.** A two-part barrier. A census of installs and tank states in
  CI, shown red on the defect, and a meter floor on the published row, which is the
  only part that reaches installs no fixture has. Its ceiling is rejected (the
  owner's no-wood ruling, triage `dev/programme/triage/s6-batch122.md#P387`), so
  the class is not fully barriered: an inflated reference on a wood house has no
  meter oracle.

## The cause, reproduced

### The figure

| month | booked thermostat kWh over metered kWh |
|---|---|
| 2026-09 (before #2411) | 3.30 |
| 2026-10 (#2411 from v7.0.1) | 0.72 |
| 2026-11 (v7.1.x) | 0.18 |

At the four snapshots in the export, the plan's own saving read +9.2, +12.0, +11.9
and +11.0 % beside the open row's -20.7, -100, -100 and -100 %. These two figures
share one reference, disagree in sign, and nothing compares them. The -100 is
`ledger.savings_pct`'s clip: the card's -599 % clipped to -100 % hides how far out
the row is.

### Which mechanism, measured

`attrib` runs `_compute_baseline_power` on the export's four tank states, tree by
tree. Each cell is step 0 over the horizon mean of the space term. The parameters
come from `from_config` with flat weather and no learned scales, so these are
attribution ratios and not a replay of the install's solves.

| tree | tanks measured | wood cold only | buffer at curve only | both |
|---|---|---|---|---|
| v7.0.4 | 0.53, 0, 0, 0 | 1.03, 1.21, 1.05, 1.04 | 1.01, 0, 0, 0 | 1.00, 1.01, 0.99, 1.00 |
| v7.1.1 and main | 0, 0, 0, 0 | 0, 0, 0, 0 | 0.70, 0, 0, 0 | 0.69, 0.26, 0.80, 0.50 |

1. **v7.0.4: the wood term alone.** `wood_share` returns 1 once the measured wood
   tank is at or above the flow setpoint, and the reference multiplies its demand
   by `1 - w`. Cooling the wood tank restores a step near the horizon mean. That
   branch dates from v3.15.0 (`8420922dc`, 2026-08-25), before #2411.
2. **v7.1.0 onward: a second, independent cause.** `valve_charge_demand`
   (`a0cfb763e`, #2887) adds a charge term `C * (goal - tank) / dt`. It is negative
   for a tank above the lowest temperature whose draw meets the need, and it
   floors the demand at zero. Removing the wood term no longer helps: 0, 0, 0, 0.
3. **The residual.** With both removed, step 0 still reads 0.26 to 0.80 of the
   mean, because the reference's tank starts above its goal and draws down.

The direction was checked in the log: the reference moved under the check.
`_thermostat_held_state` arrived at `55f48c0a4` (#2411), and the tank law later at
`a0cfb763e`. Its docstring states the limit: "Tanks and every other field stay as
measured; the thermostat does not own them."

### How far the cause reaches: not only a wood tank

`census` uses one steady day, booked through `get_current_action`, and reports the
booked step over the reference's horizon mean:

| cell | v7.0.4 | v7.1.1 |
|---|---|---|
| single, no tank | 1.00 | 1.00 |
| unvalved two-zone | 0.92 | 0.92 |
| 750 L manual valve, no wood, tank near curve | 0.23 | 0.00 |
| 750 L manual valve, no wood, tank charged | 0.24 | 0.00 |
| valve and wood tank, warm | 0.00 | 0.00 |
| valve and wood tank, hot | 0.00 | 0.00 |

Every valved install is affected, with no wood tank needed. At v7.0.4 the valved
ratio is low for a different reason: the horizon mean is inflated by the reference
charging its tank past the curve, which #2887 fixed (3.6 to 3.8 times v7.1.1's mean in
a scratch probe of these shapes). The closed-loop matrix over
48 re-plans (scratch, not committed) finished its unvalved arms only, at
booked/horizon 1.04 and 0.96; the valved arms hit its time bound, so **no
closed-loop valved figure is claimed**.

## Why the harnesses did not see it

They did see a first-step reference. #2411's body names it. What they never ran
was step 0 on a house whose step 0 the tanks decide.

1. **The metric cannot see it.** #2411's `transient` arm measures the spread of
   step 0 across four room and slab starts, with the tanks fixed. `blind` runs
   that metric on the installs it never ran. At v7.0.4 on a valve and wood house
   it reads step 0 `[0.0, 0.0, 0.0, 0.0]`, spread 0.000, `SOUND`. At v7.1.1 the
   valved house with no wood reads the same. The check that pins it in
   `tests/features.py` adds `0.0 < first`, which would catch this, but it runs two
   cells, neither valved.
2. **The fixtures.** `dev/audit/harnesses/r10_sav_baseline.py` hard-codes
   `house(two_zone=False)`. The name search `wood|mixing_valve|two_tank|buffer_tank_volume`
   finds nothing in any of the six savings harnesses.
3. **The review ran step 6, on the fixer's population.** `fix-review.md` step 6
   asks for "the other topologies". Round 2's verdict on #2411 records its own
   probe: single- and two-zone, with and without DHW, three weather and price
   pairs, `12/12 SOUND`. No cell has a valve. It is the fixer's metric again, and
   point 1 shows it would have read sound with a valve too.
4. **No finder's harness existed.** `fix-review.md` step 2 requires the finder's
   harness, "never the fixer's". The finder here was the owner, and the issue
   records a screenshot as its only evidence, so the fixer wrote the instrument and
   the reviewer re-ran it. The independence the rule buys had nothing to bind to.
5. **The reporter's install was never a cell.** The brief carried the flat-price
   null and no requirement to reproduce on the reporter's shape, though the tree
   recorded it: `wood_share`'s docstring cites the owner's valve setting from issue
   #40.
6. **#2887 straddled the seam from the other side.** Its `reference` arm runs a
   valved house but reads `np.sum(r.baseline_power_schedule)`
   (`r10_buffer_store.py`), the horizon. So #2411 measured step 0 with no valve, and
   #2887 measured the horizon with one. The ledger books step 0 with one, and
   nothing measured that. #2887 could not trip #2411's "booked step is the steady
   holding power" check because that check has no valved cell.

## Process state: (c)

The process existed and was followed: an owner-required null, a mutation proof
(M0 to M16 killed), the harness at both ends, and four review rounds with step 6
performed and recorded. It did not produce the intended result, because its unit
is the fixture population the fix's author chose, and the meter never enters.

- **Not (a).** Step 6 exists and names topologies.
- **Not (b).** Round 1 disclosed having run no other configuration, round 2 ran
  twelve, and rounds 3 and 4 carried them with production unchanged. A firmer step
  6 would have produced more green cells of the same blind metric.
- **Not (d).** The wood branch predates #2411 by eight weeks, so v7.0.4 needed no
  changed precondition. #2887's tank law does look like (d) for v7.1.0, but the
  check could not notice the change only because of the same unit, so one state
  covers both.

## The class

`fold_ledger.py check` reads 0 violations, and that is not a clearance: no class
in `bugclasses.json` carries a savings instance, so nothing could be owed. The
mechanism is **N-unmetered-reference**: a figure published from a modelled
counterfactual is checked only on fixtures its author chose and never against the
meter reading of the same interval. Instances in round 10:

| instance | what the row showed | ratio to the meter available at the time |
|---|---|---|
| #2255 item 1 | 81 % saved on the reference's recovery transient | 3.30 |
| R10-SAVINGS-NEGATIVE, #2463 | a coverage factor in the thousands on an upgraded month | not checked |
| #2492, the meter basis | a model that under-reads the meter booked as a loss | not checked |
| #2887's class-open block | the valved reference paid for heat its tank refused, read as savings | not checked |
| the wood branch at step 0 | this report, v7.0.4 | 0.72 over the mixed month |
| `valve_charge_demand` at step 0 | this report, v7.1.0 onward | 0.18 |

That is ≥3 in one round, so a barrier is owed. Nearest existing class is **P11**,
which differs: P11's oracle is a double for an external system that the implementer
wrote, while here the external reading exists, the meter on the same interval, and
nothing compares the reference with it. Earlier non-round instances are PR #2 and
PR #32.

### Other first-step-only bookings

Searched with `grep -n '_current_action.get(\|_current_action\[' coordinator.py`
(16 sites) and the `baseline_kw` and `_schedule[` readers.

- **`baseline_kw` is the only counterfactual booked per step.** The other
  `_pending_prediction` fields (power, split, mode, reasons) are the step the pump
  was actuated on, where step 0 is the correct unit.
- **`_baseline_dhw_economics` is the same shape over a horizon.** It holds the
  initial wood temperature for the whole day and spreads that one value across the
  schedule, so the hot-water term is also set by the measured tank. Its comment
  calls this conservative. The space term's "understated, never inflated" reasoning
  is the same one-sided belief: this report is what it costs on the understated
  side.

### Other figures published with no check against the meter

| figure | basis | meter check |
|---|---|---|
| `savings_months` (card, `monthly_savings` sensor, `notifier.py:90`) | modelled reference over metered, scaled by `meter_calibration` | none; the calibration scales a wrong reference further (0.74 here) |
| `predicted_savings`, `savings_percentage` (sensor, climate attributes) | modelled on both sides | none, and no cross-check with the row |
| `baseline_cost` (sensor) | modelled | none |
| `price_tiles` `monthly_*_delta`, `fuse_advisor.cost_delta_sek_month` | two solves, one horizon scaled to a month by `per_month` | none, labelled as what-ifs |
| `contract_comparison` | metered ledger lines | is the meter |

`accuracy.power_ratio` is the only model-to-meter comparator. It read 0.75 to 1.11
across the snapshots, published beside a row a factor of five out, and gates
nothing.

### Rows already booked

The ledger is append-only. September's 81 %, fixed in #2411's reference, was still
published unchanged in all four snapshots three weeks later, and November's row
will keep its booked lines after this fix. That is the fix seat's to dispose of,
carried below.

## Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock per
release, over the eight release intervals v7.0.0 to v7.1.2.

- **P(recurrence): 0.375 per release.** Three owner reports over eight intervals.
  The six class instances would give 0.75; the lower figure is used.
- **cost(defect): 18.1 h per occurrence.** First commit to merge on #2411 (29.9 h),
  #2463 (4.3 h), #2745 (78.2 h) and #3145 (6.4 h), median. The mean is 29.7 h. Seat
  and review time beyond elapsed, and the owner's lost trust in the figure, are
  excluded.
- **Right side: 6.8 h per release.**
- **cost(countermeasure, census): at most 2.1 h per release.**
  - 71 s per run contended and 21 s CPU, for 6 solves (`/usr/bin/time`).
  - `git log --first-parent --merges` finds 757 merges, 95 per release, and each
    push to main runs full.
  - 33 of the 757 touch `optimizer`, `thermal_model`, `ledger`, `mixing_valve` or
    `dhw_planner`: about 4 per release, and at 3 gate runs each, 12 PR runs.
  - (95 + 12) x 71 s = 2.1 h. At the CPU figure it is 0.6 h.
- **cost(countermeasure, meter floor): one fix group.** R10-SAV-METER-FLOOR, a
  fixer seat and a reviewer seat; at run time one comparison per published row,
  and no CI lane.

**Verdict: passes**, by a factor of 3.2 contended and about 11 at CPU cost. The
margin is modest for the census at its contended figure. The solve is the whole
cost and the census reads only the reference, so a cheaper form that skips the
solver is available if the fix leaves a seam to read.

## Countermeasure

Addresses state (c): both parts change the unit, one the population and one the
oracle. Neither is a firmer instruction.

### 1. The census (CI): shown failing and passing

Command: `PYTHONPATH=tests/hastub:tests:custom_components python3
dev/audit/harnesses/r10_rca_sav_estimate.py census`. It exits 1 on any cell out of
`BAND` (0.5 to 1.5).

| tree | rc | out of band |
|---|---|---|
| v7.0.4 | 1 | 4 of 6, as above |
| v7.1.1 | 1 | 4 of 6, as above |
| main | 1 | 4 of 6 |
| main plus a planted booking of the horizon mean | 0 | 0 of 6 |
| `handoff/r10-hotfix-sav-estimate` | owed | not on origin when this was written |

- **The planted arm is a weak pass**, since it makes the ratio 1 by construction.
  The real pass is the fix's head, and that run is owed before this part is
  claimed.
- **Null control.** The `single` and `unvalved` cells stay in band on every
  defective tree, so the check is not reading the install's size.
- **No green by skipping.** A missing `baseline_kw` raises, and a cell that did not
  run exits 1.
- **Wiring.** It must land with or after the fix, or it reddens main. It is carried
  to the fix seat, and registering it as a `tests/` script moves the class to
  `barriered`. Until then the class is `detector`.

The census covers enumerated installs only. "A harness's configurations are its
parameters, not its population" (`fix-review.md`), so it cannot be the whole
barrier, which is why part 2 exists.

### 2. The meter floor (production, R10-SAV-METER-FLOOR): the part that reaches the population

`savings_months` reads each row's booked thermostat kWh over its metered kWh and,
where that is under `METER_FLOOR` (0.5, `ledger.py`) on a row of the current
reference basis with at least `MIN_CALIBRATION_KWH` metered, publishes no saving
and says why (`below_meter_floor`). The ceiling the band first had (2.0) is
rejected under the owner's no-wood ruling: the reference holds no wood term, so
wood raises the ratio without limit and a high ratio on a wood house cannot be
told from wood by the meter. Do not build a ceiling without a measured instance
above it on an install with no wood (triage P387).

- **On the defect:** `ledger` reads 2026-09 at 3.30, above the floor and so not
  caught, and 2026-11 under it. The 2026-11 figure (0.18 above) is this seat's
  reading of the owner's export, which is on no ref; the R10-SAV-METER-FLOOR
  fixer could not re-run the arm on it, so the figure is unverified, not
  re-derived.
- **Null:** the flat-price arm `valve-flat` of
  `dev/audit/harnesses/r10_sav_wood_reference.py` publishes; its `meter-floor`
  arm runs every valve and wood arm through the floor and asserts each publishes.
- **Known limit:** a low-side check only. It would not catch October's -23 %, nor
  any reference inflated above the meter.

This changes production and what the card shows, so it needs its own fixer. It
changes no policy. Nothing here asks for a rule change, and the #2411 state being
(c), no instruction is proposed.

## Carries

- **To the fix (`handoff/r10-hotfix-sav-estimate`):** the second cause (a fix on the
  wood term alone stays at 0, 0, 0, 0 on v7.1.x); valved installs with no wood; the
  already-booked rows; wiring the census.
- **`notifier.py` `_monthly_receipt`** sends the row too, so the floor gates it as
  well as the card and the sensor: the event carries `saving_below_meter_floor`.
