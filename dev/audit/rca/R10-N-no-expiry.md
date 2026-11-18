# RCA: a last-known value is published and booked as current with no age bound

Seat: round-10 root-cause, class `N-no-expiry` (#2229). R10 has 3 instances (1 judged, 2
beyond the finding), which meets the per-round trigger. Tree: `handoff/audit-r10-register`
at `2c3272eb7`. This seat fixes nothing.

## Root cause

### Cause, reproduced

Three coordinator lookups find "the entry covering now" in a time series by taking
`bisect_right(starts, now) - 1`, under the rule *each entry holds until the next one
begins*. That rule gives the last entry no end. Once the source stops extending the series,
the last entry stays "current" indefinitely. It is then published as a current value and,
for the price, booked into the ledger. None of the three lookups compares `now` with the end
of the entry it returns.

Reproduced at `2c3272eb7`:

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/stale_price.py` prints:
  - `uncovered_current_price_published=4` and `uncovered_price_booked=4` over
    `uncovered_cycles=4`;
  - `control_covered_published=2`.

  The judge's `--perturb` moved published from 4 to 0 and booked from 4 to 0.
- `PYTHONPATH=.:tests/hastub python3 dev/audit/rounds/round10/D14/probe_n_no_expiry.py`
  prints:
  - `forecast_outdoor_now past_end=0.0 FAIL` and `_open_loop_plan_value past_end=44.5 FAIL`,
    both 47 h past the end of their series;
  - the covered control: `forecast=-2.0 plan=49.5`.
- `dev/audit/rounds/round10/D14/sweep_n_no_expiry.py` reports `seams=9 unbounded=6` in
  0.54 s. Its null fixture gives 0. Dropping the one end-bound line from
  `_known_prices_for` gives 1.

### Class search

The R10 sweep (`dev/audit/rounds/round10/sweep-N-no-expiry.md`) gave each of the 9
`bisect_right(...) - 1` seams a disposition:

- **3 instances.**
  - `_current_spot_price`, published and booked.
  - `forecast_outdoor_now`. It is written to `outdoor_temperature` when the thermometer is
    not ok, and published as `outdoor_forecast_temperature`.
  - `_open_loop_plan_value`. It seeds `dhw_temperature` with no `_plan_is_stale` gate.
- **1 not applicable.** `_weather_series` builds the future horizon. Padding past the last
  entry is documented extrapolation there and is never published as current.
- **5 guarded.** Each is guarded by an end bound or by a caller that returns None past the
  plan end.

Outside this seam rule, a last-known scalar cache with no series is not enumerated. That is
the sweep's stated limit.

The same unguarded shape was introduced by **fixes**:

| seam | introduced or reshaped by | what that fix bounded |
|---|---|---|
| `_current_spot_price` | `6c1834977` 2026-09-28, round-9 F1.3 (D2-s3-01, #1644): "the entry whose [start, next start) covers now" | the start side: a one-hour span read a quarter up to 45 min stale. The last entry's end was left open |
| `forecast_outdoor_now` | `f4c6a2d22` 2026-09-03, #368 (D8-01 remainder): "A published temperature is a reading or it says it is not" | it matched the entry by its own timestamp instead of index 0. "Each entry holds until the next one begins" gives the last entry no end |
| `_open_loop_plan_value` | `3110b24df` 2026-09-27, round-9 F1.2 (coordinator open-loop seed) | it seeds from the plan, with no age gate |

### Process state: (c) followed and did not produce the intended result

`dev/governance/dimensions/D1.md` step 3 has named *"a price list that stops updating"* as
a staleness perturbation since `58a1f2a7a` (2026-09-02). Round 9 executed it:
`dev/audit/rounds/round9/D1/s2/staleness.py` freezes the price entity at `t0` and walks
`now` to t0+60 h. Its metric, though, is the **plan horizon**: `known_steps` from
`_forecast_arrays`, `plan_stale`, and whether a price-staleness key is published. It never
reads the scalar the cycle publishes as the current price, and never reads the ledger
booking. So the step was run, and its unit missed the published and booked value.

Each of the three fixes above was reviewed and merged against a finding about the **other**
edge of the same lookup: index 0, or the start of the covering entry. The covering rule
they wrote, "holds until the next one begins", is exactly the open end. This is (c), not
(a): the perturbation existed and was driven. It is not (b): the harness did what the step
says, and the step does not name the published current value as its read point.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per release.

- **Standing cost.** The static check is the sweep enumerator plus a reasoned allow-list.
  It runs in 0.54 s (measured). At about 18.5 PRs per release (314 PRs over 17 release
  intervals, `v6.7.1..v7.0.0`), with one run charged to every PR, that is 10 s per release.
- **P(recurrence).** 2 of the 3 instance seams arrived after `v4.0.0`
  (`forecast_outdoor_now` 2026-09-03, `_open_loop_plan_value` 2026-09-27). Over 122 release
  intervals to `v7.0.0` that is 0.016 per release. The third was reshaped by a fix on
  2026-09-28.
- **cost(defect).** The lower bound is the round-9 per-finding fix cost, #1718: 21.75 h
  over 5 findings, so 4.35 h. That excludes finder, verify and judge seats. The field
  severity is high: a stale spot price is booked as the cost of energy for as long as the
  feed is down.
- **Verdict.** 2/122 x 4.35 h = 0.071 h = 257 s per release, against 10 s. The barrier
  passes by a factor of about 25.

### Countermeasure (a class barrier, proposed; not built by this seat)

It addresses (c) twice.

1. **One covering-slot helper.** It returns the entry whose `[start, end)` covers `now`, or
   None. `end` is the next start, or for the last entry its own declared span (the price
   resolution, or the forecast step). The three instance sites go through it. Of the
   guarded seams, `_known_prices_for` already keeps the end bound
   (`if step_start >= end: break`), and the helper should be extracted from that rule.
2. **A static `tests/` arm.** It is the enumerator's AST rule and refuses an unbounded
   `bisect_right(...) - 1` lookup that is not on a reasoned allow-list. Today the
   allow-list would hold the 3 non-instance seams the enumerator flags `UNBOUNDED`:
   - `_weather_series` (horizon extrapolation);
   - `pump_arbiter._planned_room` (its caller's `step_duty` is None past the plan end);
   - `early_cutoff._planned_room` (index-bounded).

   The arm must show:
   - red on this tree (3 instances);
   - green once the instances are fixed;
   - null control: the clean fixture gives 0;
   - perturbation: dropping the `_known_prices_for` end bound gives 1;
   - non-vacuity: the number of seams read is at least 9.

**Brief carry (proposal; the orchestrator delivers it).** D1 step 3 should name its read
point: *the value the cycle publishes and books as current*, not only the plan horizon.
`dev/governance/dimensions/D1.md` is policy, so this needs tvofi's approval.

## Needs tvofi

1. The D1 step-3 sentence above. It addresses (c).
2. No budget raise is foreseen. The helper replaces three local lookups.
