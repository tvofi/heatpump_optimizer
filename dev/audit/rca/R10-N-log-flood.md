# RCA: a persisting condition logged at WARNING on every cycle

Seat: round-10 root-cause, class `N-log-flood` (#2226). R10 has 7 instances (1 judged, 6
beyond the finding), which meets the per-round trigger. Tree: `handoff/audit-r10-register`
at `2c3272eb7`. This seat fixes nothing.

## Root cause

### Cause, reproduced

The coordinator handles a missing or misconfigured input with an `if` branch that logs at
WARNING and falls back. Examples are no weather entity, no price data, no Open-Meteo
coordinates, and a malformed peak-months or peak-hours option. The branch has no state, so
it logs again on every cycle for as long as the condition holds. A cycle is
`DEFAULT_OPTIMIZATION_INTERVAL` = 30 min by default, and a configuration fault holds
indefinitely. The fix for this shape already exists, but only
locally: `_tibber_fetch_failed` and `_weather_fetch_failed` keep outage counters, and
`_check_pump_mode_expired` and legionella's `check_mode_block` keep a transition notice.
That pattern was written per site and was never a helper, so a new branch does not inherit
it.

Reproduced at `2c3272eb7`:

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` runs
  4 cycles per arm in 15.8 s. It prints `control.floods=0` and a flood on all 7 condition
  arms:
  - `no_weather_entity`, `weather_fetch_fails`, `open_meteo_no_coord`, `bad_peak_months`
    and `bad_peak_hours` print 1 each;
  - `open_meteo_bad_coord` and `no_prices` print 2 each.

  The judge's `--perturb` latch moved the finding's arm from 4 records to 1.
- `dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer`
  prints `sites=85 latched=6 seams=79` in 0.36 s.

### Class search

The R10 sweep (`dev/audit/rounds/round10/sweep-N-log-flood.md`) gave all 85 static sites a
disposition:

- 7 instances, probed at runtime;
- 5 more on static evidence only (`_apply_action`, `_command_valve_target`,
  `_note_solve_failure`, `pump_arbiter._space_target`, `inputs._age_gate`), with a runtime
  probe still owed;
- 12 guarded by counters or transition notices that the static predicate does not
  recognise;
- the rest not applicable, because they are not reached per cycle.

Growth of unlatched WARNING/ERROR sites, by the same enumerator over `git archive` exports
of the package:

| tree | sites | latched | unlatched |
|---|---|---|---|
| `v4.0.0` | 49 | 1 | 48 |
| `v6.7.1` | 77 | 5 | 72 |
| `2c3272eb7` | 85 | 6 | 79 |

All 7 probed instances are older than `v4.0.0` or date from that week (first commits
`ec45dc4d5` 2026-04-03, `6232ea638` 2026-08-21, `bf10e28aa` 2026-08-22, `a2afe9334`
2026-08-25). The class is old. It was not found earlier, and the next section says why.

### Process state: (c) followed and did not produce the intended result

Two processes look at exactly this, and both were run.

- **D10, the `log-when-unavailable` rule.** The rule is Silver in
  `dev/governance/dimensions/D10.md`, and the round-10 D10 seat graded it `done`
  (`dev/audit/rounds/round10/D10/s1/quality_scale.yaml:38`). The evidence is
  `dev/audit/rounds/round10/D10/s1/rules.py:241`:
  `"_tibber_fetch_failed" in co and "_tibber_fetch_recovered" in co`, labelled *"latched
  fail/recover pair present"*. That is an existence test for one latched site. Round 3's
  `qs_register.py` used the same predicate, and round 3's `log_once_rule.py` drove the
  Tibber path only. The rule grades the integration. The check graded one site, and any
  tree with one latched site passes it. The same round's D1 found 7 floods.
- **D1, steps 5 and 6.** *"Every `try/except` that swallows: does it log once"* and
  *"the failure logs once"*. Their unit is the exception handler and the external-input
  parser. All 7 instances are plain `if` branches on a persistent condition, with no
  exception, so the step that asks the right question was not aimed at them.

Both processes existed and were followed, and each one's unit missed the site. That is
(c), not (a) or (b). In the shape of `defect-root-cause.md`'s #2073 example, it is a check
whose unit covers one direction of what it claims.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per release.

- **P(recurrence).** Unlatched sites grew by 31 over 122 release intervals (`v4.0.0` to
  head), 0.25 per release. Of today's 79 unlatched sites, 12 are instances or static
  candidates, a 0.15 share. So P is about 0.254 x 0.152 = 0.039 new flood sites per release.
  This is an estimate: the share assumes new sites flood at the rate old ones do.
- **cost(defect).** The lower bound is the round-9 per-finding fix cost, 4.35 h (#1718:
  21.75 h over 5 findings). The severity is low (hygiene), so this figure probably
  overstates a single flood. The field cost at the default 30-min cycle is 48
  WARNINGs a day per condition in the user's log, and 192 a day for each tariff option,
  which logs 4 times a cycle.
- **Standing cost, two forms.**
  - (i) The runtime probe as a gate script: 15.8 s x 18.5 PRs per release = 292 s per
    release.
  - (ii) A static arm: 0.36 s x 18.5 = 7 s per release.
- **Verdict.** The expected defect cost is (31/122) x (12/79) x 4.35 h = 604 s per release.
  - (i) passes by only 2x, against a cost(defect) that is probably high.
  - (ii) passes by about 85x.

  So the static form is chosen, and the runtime probe stays an audit instrument.

### Countermeasure (a class barrier, proposed; not built by this seat)

It addresses (c) by making the latch structural instead of per site, and by aiming the
check at every site rather than one.

1. **A transition-latch helper.** It logs at WARNING once when a keyed condition becomes
   true, at DEBUG while it persists, and at INFO when it clears. It extracts the existing
   `_tibber_fetch_failed` and `_weather_fetch_failed` counter pattern, and the 7 instance
   sites route through it.
2. **A static `tests/` arm.** It uses the R10 enumerator's AST rule and refuses an
   unlatched `_LOGGER.warning` or `_LOGGER.error` in a function reached from the cycle,
   unless the site goes through the helper or is on the reasoned list the sweep already
   wrote (load, restore, setup and service paths; per-event actuation failures). The arm
   must show:
   - red on this tree (the 7 instances);
   - green once they are fixed;
   - null control: the latched fixture gives 0;
   - perturbation: replacing the latch with `if True:` gives 1;
   - non-vacuity: the number of sites read is at least 85.
3. **D10's `log-when-unavailable` evidence.** It should cite that arm, not a substring test
   for one site. That evidence is a D10 instrument, not policy.

## Needs tvofi

Nothing is policy here. The helper and the arm sit in the package and in `tests/`. A
structure-budget raise, if the fix needs one, is tvofi's decision, asked before the push.
