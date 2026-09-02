# D6 — verifier seat 1 of 3 (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Box: 8-core Apple M1, 8 GB, Darwin 25.6.0, Python 3.13.1, numpy 2.5.2, scipy
1.18.1, interpreter `tvofi-claude/.venv/bin/python`, `PYTHONPATH=tests/hastub`,
run from the export root. Every harness pins the five BLAS thread variables
before numpy and sets `sys.dont_write_bytecode`; none writes into the export.

My harnesses live in `/tmp/verify-D6-1/` with their captured stdout beside
them: `d6_01_names.py`, `d6_02_wind.py`, `d6_03_selectors.py`,
`d6_04_recorded.py`, `d6_05_baseline.py` (+ `.out` each) and
`claims_rerun.out`. Every number below is a count, a constant comparison or a
deterministic forward-loop sum — no timing enters a verdict, so the fan-out
does not touch them (`thread_factor=1.000`, `load1` 1.40–3.16 on every run).

**Constraint honoured.** I ran no solver, no `rolling_learning.py`, no test
suite and took no gate lock; another agent holds the box for timing re-takes.
D6-04 is verified from the finder's recorded `.out` files and from
`tests/rolling.py` source, as briefed. My D6-05 harness drives
`_compute_baseline_power`, a forward thermostat loop (0.003 s CPU), not
L-BFGS-B.

## Re-run of the finder's harness (once, as required)

```
PYTHONPATH=tests/hastub python tools/audit/round2/D6/claims.py
RESULT claims_extracted=273 claims_checked=263 claims_true=258
RESULT claims_false=1 claims_stale=4 claims_unverifiable=10
RESULT thread_factor=1.000  RESULT load1=3.16  RESULT swapins=0   EXIT 0
```

All six counts equal the finder's, and `diff` of the 273 claim rows against the
committed `claims_table.md` is empty — the table reproduced byte for byte
(links answered, so no row fell to `unverifiable`). Note for the judge: row
C293 (D6-04) is a **file read** of `rolling_learning.out`, not a measurement,
so this re-run re-verifies nothing about D6-04 on its own.

---

## D6-01 · README sensor table omits nine qualifiers — **verify** (low)

**My metric.** `readme_only` = README `### Sensors` table names that are not,
byte for byte, any `strings.json` `entity.sensor.<key>.name`; `prefix_pairs` =
how many of those are a strict prefix (`"<name> ("`) of exactly one otherwise
unmatched strings.json name. (The finder matched "exact, else name+' (' prefix"
in one pass; I split the two directions so a rename that is *not* a dropped
qualifier would show up as `readme_only > prefix_pairs`. The definitions agree
on this tree.)

```
RESULT readme_table_rows=55        RESULT strings_sensor_names=55
RESULT readme_only=9               RESULT strings_only=9
RESULT prefix_pairs=9              RESULT strings_names_with_qualifier=13
RESULT en_names_equal_strings=55   RESULT sv_names_qualified_where_strings_is=13
RESULT sensor_py_keys_unwired=0    RESULT sensor_py_attr_name_assignments=0
RESULT scope_hits_outside_table=0
RESULT perturbed_readme_only=0     RESULT negative_perturbed_readme_only=11
RESULT thread_factor=1.000  RESULT load1=2.02
```

Deciding number: **9**, at README.md:294, 298-299, 302-307 — exactly the lines
the finding names. Dropped qualifiers are ` (next 24 h)` (3) and ` (lifetime)`
(6), each resolving to exactly one strings.json name.

**Attacks.**
1. *Is the name the entity really carries?* `sensor.py` sets `_attr_name` zero
   times, uses `_attr_has_entity_name = True` + `translation_key`, and every
   one of the 55 strings.json sensor keys appears as a literal in `sensor.py`
   (`sensor_py_keys_unwired=0`). The strings.json name is the displayed name.
   `en.json` matches strings.json on all 55; `sv.json` carries a qualifier
   wherever strings.json does (13/13). Not a stub artefact.
2. *Is the metric just picky about parentheses?* No — 13 strings.json names
   carry a qualifier and the README reproduces 4 of them correctly (Buffer Tank
   Temperature (Model), Indoor/Outdoor Temperature (Optimizer), Slab
   Temperature (Estimated)). The nine misses are a clean subset: the six
   lifetime accumulators and the three 24-hour plan/cost sensors.
3. *Perturbation moves both ways.* Rewriting the nine rows to the strings.json
   names in memory → `readme_only=0`; stripping ` (Optimizer)` from
   strings.json instead → `readme_only=11`. The metric is not a constant.
4. *Fix scope.* I searched README.md, DISCLAIMER.md and all `docs/*.md` for the
   nine unqualified names outside the table rows: **0 hits**. The nine README
   rows are the whole class.
5. *Severity by consequence.* Entity ids are `sensor.heat_pump_optimizer_<key>`
   and unaffected; the names remain findable by prefix in the HA UI. `low` is
   earned; I would not raise it.

**Vote: verify, severity low.** Deciding number `readme_only=9 of 55`
(`prefix_pairs=9`, `scope_hits_outside_table=0`).

---

## D6-02 · services.yaml teaches the retired 0.15 wind default — **verify** (low)

**My metric.** `wind_example_minus_default` =
`services.yaml set_thermal_parameters.fields.wind_sensitivity_factor.example`
(yaml.safe_load) − `const.DEFAULT_WIND_SENSITIVITY`; plus
`example_equals_retired`, comparing that example against the figure const.py's
own comment names as the *replaced* default. (The finder measured the same
difference; I added the retired-value identity so "stale" is proved from the
tree rather than asserted, and swept the other 27 keys for the same class.)

```
RESULT wind_example=0.15   RESULT wind_default=0.03
RESULT wind_example_minus_default=0.12 fraction_per_m_s
RESULT description_figure=0.15   RESULT description_arithmetic_true=1
RESULT retired_default_named_in_const=0.15   RESULT example_equals_retired=1
RESULT keys_with_const_default=28   RESULT examples_differing_from_default=1
RESULT tree_hits_0_15_near_wind=4   RESULT perturbed_wind_example_minus_default=0.00
RESULT thread_factor=1.000  RESULT load1=2.02
```

Deciding number: **0.12** (0.15 vs 0.03), and the example is *identical* to the
0.15 that `const.py:1036` documents as "the previous default … a physically
implausible figure". Both the `example:` (services.yaml:330) and the prose
"0.15 means 15% more heat loss per m/s" (services.yaml:327) carry it; the
description's own arithmetic is internally consistent (0.15 ↔ 15 %), so a
reader has no cue that it is stale.

**Attacks.**
1. *Is 0.15 merely a legal example rather than a taught default?* It is inside
   the selector range (0.0–0.5), so nothing rejects it — but it is the only
   example of 28 checked keys that differs from its own `DEFAULT_`
   (`examples_differing_from_default=1`), and the description states it as the
   explanatory figure. Stale, not illustrative.
2. *Fix scope — same class elsewhere?* Four tree hits of `0.15` near "wind":
   services.yaml:327 and :330 (the finding), `const.py:1036` (the comment
   explaining the retirement — correct), and `docs/how-it-works.md:277`, which
   is a **false positive**: that 0.15 is `DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT`
   (0.15 kW/°C), a different quantity. `configuration.md:183,375` teach 0.03;
   strings.json/en/sv describe the field without a number. I also swept every
   services.yaml *description* figure against its key's default: 4 flagged, 3
   of them legitimate guidance (0.02 kWh/°C per m², the 0.0/1.0 endpoints,
   SHGC 0.3–0.8). Only wind is stale. **The two-line fix scope covers the
   class.**
3. *Consequence.* A user who copies the example gets 5× the shipped wind
   sensitivity — the exact failure const.py says made "every windy forecast
   panic-charge the house". That is a real, if self-inflicted, mis-tune, and it
   is the one finding here whose severity I considered raising. It stays `low`
   because nothing publishes the value: it changes behaviour only if a user
   copies the example into a service call, and the passive learner walks the
   loss scale back.

**Vote: verify, severity low.** Deciding number `|example − default| = 0.12`
(`example_equals_retired=1`, `examples_differing_from_default=1 of 28`).

---

## D6-03 · Two services.yaml selectors admit 0 the schema rejects — **verify** (low)

**My metric.** `rejected_bounds` = count of (service, field, bound) where a
services.yaml number selector's `min` or `max`, fed as `{field: value}` to the
schema **bound to that service at its `hass.services.async_register(...)`
call**, raises `vol.Invalid`; plus `rejected_min_plus_step` for the first grid
value above `min`. (The finder read the schema from the service registry after
`async_setup_entry`; I resolved it from the register call sites instead — a
static path that needs no coordinator. Same schema objects, 11/11.)

```
RESULT services_registered_with_schema=11   RESULT schemas_resolved=11
RESULT number_selectors=39   RESULT selectors_without_schema=0
RESULT rejected_bounds=2     RESULT rejected_bounds_min=2
RESULT rejected_min_plus_step=0   RESULT perturbed_rejected_bounds=0
RESULT config_flow_min_inter_zone=0.0  RESULT config_flow_min_window_area=0.0
RESULT thread_factor=1.000  RESULT load1=1.52
```

Deciding number: **2 of 39**, both minima, with the schema's own message:

```
('set_thermal_parameters','inter_zone_heat_transfer','min',0.0,
   "value must be at least 0.01 for dictionary value @ data['inter_zone_heat_transfer']")
('set_thermal_parameters','window_area','min',0,
   "value must be at least 0.01 for dictionary value @ data['window_area']")
```

**Self-caught harness artefact — recorded because it would have been a false
refute.** My first run printed `rejected_bounds=0` with
`selectors_without_schema=25`: I had constructed the constant name from the
service name, and `set_thermal_parameters` is registered under the *abbreviated*
`SERVICE_SCHEMA_SET_THERMAL_PARAMS`, so all 25 of its selectors were silently
skipped. Resolving the schema from the `async_register` call fixed it and the
finder's number reproduced exactly. A verifier that stopped at the first number
would have refuted a true finding.

**Attacks.**
1. *Grid artefact?* No: `rejected_min_plus_step=0` — only the exact minima
   fail, so it is the bound itself, not a step-grid rounding effect.
2. *Reachable, or stub-only?* The rejection is `vol.Range(min=0.01)` from
   `_positive()`, applied by HA's own service-call validation before the
   handler runs — not a `FakeHass` path.
3. *Perturbation.* Raising the two minima to 0.01 in memory → 0 rejections.
4. *Fix scope — is narrowing services.yaml even the right direction?* This is
   my one substantive reservation, and it is about the fix, not the finding.
   The **config/options flow admits 0 for the same two keys at four sites**
   (`config_flow.py:1236, 2221` for `inter_zone_heat_transfer`; `1252, 2434`
   for `window_area`), and `ThermalParameters.from_config` keeps a stored 0 for
   both (`inter_zone_transfer=0.0`, `window_area=0.0`). So 0 is a value the UI
   offers, the model accepts, and only the *service* refuses. Raising the two
   selector minima to 0.01 (the finding's scope) removes the drift but leaves
   the service stricter than the UI for a physically sensible value (no
   windows; no inter-floor coupling). Letting `_positive` accept 0 for these
   two keys — the finding's own parenthetical alternative — reconciles all
   three. Either way the metric goes to 0; the judge should note the four
   config-flow sites are outside the stated two-line scope.
5. *Severity.* A Developer Tools form offering a value the call refuses is a
   visible-but-recoverable annoyance; `low` is earned.

**Vote: verify, severity low.** Deciding number `rejected_bounds=2 of 39`
(after `schemas_resolved=11/11`), with the fix-scope note above.

---

## D6-04 · The "6.7 → 0 degree-hours" reference run — **verify** (low), title over-stated

Per instruction I ran no solver. My metric is over the finder's records and the
test source: `out_result_lines_differing` = RESULT keys whose value differs
between `rolling_learning.out` and `rolling_learning_rerun.out`, excluding the
box lines `cpu_seconds`/`load1`; `assertions_referencing_6_7` = `R.check(...)`
conditions in `tests/rolling.py` naming the figure;
`figures_reproducing_at_quoted_precision` = of the two figures the docs quote
("6.7" and "zero"), how many the recorded run matches at the precision quoted.

```
RESULT out_result_lines_differing=0        RESULT out_result_lines_identical=11
RESULT out_box_lines_differing=2           (cpu_seconds, load1 only)
RESULT recorded_breach_uncorrected=9.634   RESULT recorded_breach_learned=0.044
RESULT recorded_breach_removed_fraction=0.9954
RESULT recorded_over_quoted_uncorrected=1.438
RESULT null_breach_uncorrected=0.000       RESULT null_breach_learned=0.000
RESULT recorded_thread_factor_max=1.000
RESULT assertions_referencing_6_7=0        RESULT comment_lines_referencing_6_7=1
RESULT guard_is_strict_inequality=1        RESULT docs_quoting_6_7=2
RESULT figures_reproducing_at_quoted_precision=1 of_2
RESULT harness_calls_matching_test=3 of_3  RESULT harness_constants_match_test=1
RESULT harness_prefix_runs_checks=0        RESULT harness_prefix_defines_helpers=1
RESULT thread_factor=1.000  RESULT load1=1.94
```

The three questions I was asked to settle:

1. **Are the two runs bit-identical?** Yes. All 11 measured RESULT keys are
   equal (`plant_error`, both breaches, `scale_start/end`,
   `scale_overshoot_past_true`, `scale_last_quarter_std`, `learner_samples`,
   `correct_model_drift`, `thread_factor`, `swapins`); only `cpu_seconds`
   (39.2 → 30.9) and `load1` differ, which are the box, not the measurement.
   The number is deterministic on this box.
2. **Is the null control 0 → 0?** Yes: `plant_error=1.0` gives
   `breach_uncorrected=0.000`, `breach_learned=0.000`. The 9.634 → 0.044 gain
   is entirely the mismatch mechanism's; there is no gain when the model is
   right. (Note the third arm — `correct_model_drift=0.0167`,
   `learner_samples=287` — is `plant_error=1.0` by construction and so is
   identical in both files; the env var perturbs only the first two arms. Not
   an error, but it means those two rows are not evidence of the perturbation.)
3. **Is "does not reproduce" about a comment quoted as fact?** Yes.
   `tests/rolling.py:452` carries "(measured: 6.7 degree-hours of breach
   uncorrected, 0.0 with learning)" in a **comment**; zero `R.check`
   conditions reference it. The only assertion is
   `breach_learned < breach_plain` (`guard_is_strict_inequality=1`), which the
   recorded run satisfies with room to spare (99.54 % of the breach removed).
   README:487 and how-it-works.md:1238 state the comment's figures as the
   "reference run" — two documents quoting an unasserted comment.

**Attacks.**
1. *Is the finder's harness faithful to the test?* Yes: 3 of 3 `run_rolling`
   calls are argument-identical to the test's (`days=3, dhw=False,
   plant_error=TRUE_ERROR, learn=True, config=BOUND_PUMP`, the same without
   `learn`, and `days=2, dhw=False, plant_error=1.0, learn=True`); `TRUE_ERROR
   = 1.35` and `{"heat_pump_max_power": 4.25}` match; the prefix it execs
   defines both `run_rolling` and `floor_for` and runs **0** `R.check`s, so it
   re-uses the test's code without running the suite.
2. *Is the title right?* **Partly, and I weaken it.** The docs quote a pair.
   The endpoint *does* reproduce at the precision quoted — 0.044 degree-hours
   over three days is "zero" to one decimal, exactly as README and
   how-it-works word it. The start does not: 9.634 vs 6.7 is **1.438×**. So
   `figures_reproducing_at_quoted_precision=1 of 2`; "the reference run does
   not reproduce" should read "the 6.7 figure does not reproduce; the 'to zero'
   claim does". This is a wording correction, not a severity change — the
   finding's own evidence field already states 9.634 → 0.044.
3. *Is this really documentation drift, or box-dependence?* The tolerance
   matters: degree-hours below a floor is `sum(max(0, floor − room))`, a
   **hinge functional**. Room temperatures that differ in the third decimal
   near the floor move the sum by tens of percent, so a 1.44× gap is fully
   consistent with the last-decimal solver differences `tools/audit/README.md`
   already documents between this box and the fixture machine — it is *not*
   evidence the mechanism changed. That cuts both ways for the fix: re-recording
   the comment from a run on any one machine re-creates the same trap, so of
   the finding's two proposed branches, **"state only the asserted property"
   (as how-it-works.md:1247-1250 itself recommends) is the sound one**, and
   re-recording is not. The judge's re-execution on the quiet box may well give
   a third pair; that would confirm the fragility rather than refute the
   finding.
4. *Severity.* Nothing the integration publishes depends on it; the asserted
   property holds. `low` earned.

**Vote: verify, severity low**, with the title weakened to "the quoted 6.7
figure does not reproduce (9.634 here, 1.438×); the 'to zero' half does".
Deciding numbers: `out_result_lines_differing=0` (deterministic),
`assertions_referencing_6_7=0` with `docs_quoting_6_7=2` (a comment quoted as
fact), null control `0.000 → 0.000`. My evidence is from the records and the
source, as briefed — the re-execution is the judge's to take on the quiet box.

---

## D6-05 · DISCLAIMER calls the baseline an always-on thermostat — **verify** (low)

**My metric.** I drove production `HeatPumpOptimizer._compute_baseline_power`
over one 24 h winter day (96 steps, `winter_cold`, `profiles.house`) twice:
once with `comfort_targets=None` (a flat 21 °C held around the clock — what an
"always-on thermostat" is) and once with the schedule built by **production
`OptimizationConfig.get_comfort_temp`** at its shipped defaults (21.0 day /
19.5 night, 07:00–22:00). `night_energy_ratio` = night-hour baseline kWh
(schedule) ÷ (flat). An always-on baseline gives exactly 1.0; a
schedule-following one gives < 1.0. (The finder compared documents against the
docstring — a source comparison. Mine is an executed behavioural number, so the
two are complementary rather than comparable; the judge should treat mine as
the measurement of what the code does.)

```
RESULT steps=96
RESULT baseline_kwh_flat=77.132   RESULT baseline_kwh_schedule=74.447
RESULT night_energy_ratio=0.5722  RESULT night_steps=36
RESULT night_steps_below_flat=34  RESULT flat_equals_explicit_21=1
RESULT perturbed_night_energy_ratio=1.0000
RESULT dhw_baseline_constant_series=1
RESULT docstring_says_follows_schedule=1
RESULT production_call_sites=3
RESULT production_call_sites_passing_comfort_targets=3
RESULT docs_calling_space_baseline_always_on=1
RESULT forward_loop_cpu_seconds=0.003   RESULT thread_factor=1.000  RESULT load1=1.40
```

Deciding number: **`night_energy_ratio = 0.5722`** — the baseline draws 43 %
less energy through the night than an always-on thermostat would, on 34 of 36
night steps. The space baseline is not always-on; DISCLAIMER.md:71-72 says it
is.

**Attacks.**
1. *Is the schedule-following branch dead code the disclaimer could fairly
   ignore?* No: all **3** production call sites of `_compute_baseline_power`
   pass `comfort_targets` (`optimizer.py:2849, 4781` and the two-zone path).
   The always-on arm is reachable only by passing `None`, which nothing does.
2. *Is my "flat" arm a fair stand-in for "always-on"?* Yes:
   `comfort_targets=None` falls back to `self.config.target_temp`, and feeding
   an explicit 21 °C array is byte-identical (`flat_equals_explicit_21=1`).
3. *Is the DISCLAIMER sentence perhaps about the hot-water half?* No — it
   describes the whole baseline ("the baseline it compares against is a
   simulated always-on thermostat"). The DHW half genuinely *is* always-hot
   (one `np.full(n_steps, (baseline_draw + standby_loss) / cop_dhw)` series),
   and README:271 states that split correctly ("Only the hot-water half of the
   baseline is always-on"). One document of two is wrong, matching the
   finding's count of 1.
4. *Fix scope.* `always-on`/`always-hot` across README, DISCLAIMER and
   `docs/*.md` gives three hits: DISCLAIMER.md:72 (wrong), README.md:271
   (correct), and how-it-works.md:529 "the always-hot baseline" — which is in
   the DHW ready-energy passage and is **correct**. The one-sentence scope
   covers the class.
5. *Severity by consequence.* The error is conservative in the user's
   direction: an always-on baseline is *more* expensive than the scheduled one,
   so a reader discounts the reported savings more than necessary. It
   understates the product, it does not oversell it. `low` earned; I would not
   raise it despite the document being the legal one.

**Vote: verify, severity low.** Deciding number `night_energy_ratio=0.5722`
(34/36 night steps below flat; 3/3 production call sites pass
`comfort_targets`).

---

## Summary

| Finding | My number | Vote |
|---|---|---|
| D6-01 | `readme_only=9 of 55`, `prefix_pairs=9`, `scope_hits_outside_table=0` | verify (low) |
| D6-02 | `example − default = 0.12`, `example_equals_retired=1`, 1 of 28 keys | verify (low) |
| D6-03 | `rejected_bounds=2 of 39` (both minima), `schemas_resolved=11/11` | verify (low), fix-direction note |
| D6-04 | `out_result_lines_differing=0`; null `0.000 → 0.000`; `assertions_referencing_6_7=0`, `docs_quoting_6_7=2`; `1 of 2` figures reproduce | verify (low), title weakened |
| D6-05 | `night_energy_ratio=0.5722`, `3/3` call sites pass `comfort_targets` | verify (low) |

All five reproduced independently. Two notes carry to the judge: the D6-03 fix
scope omits four `config_flow.py` sites that admit 0 for the same two keys (so
narrowing services.yaml makes the service stricter than the UI), and D6-04's
figure is a hinge functional and therefore cross-machine fragile — re-recording
it would rebuild the same trap, so the "state only the asserted property"
branch is the one to take. No finding's severity should move off `low`; none
changes what the integration does.
