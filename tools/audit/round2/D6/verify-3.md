# D6 — verifier seat 3 of 3 (perturbation and scope)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python` (3.13), `PYTHONPATH=tests/hastub`.
Every number below is a count or a constant comparison, taken during the
fan-out (load1 2.07–3.96) and contention-immune; `thread_factor=1.000` on
every run, `swapins=0`. Perturbations were applied with
`/tmp/verify-D6-3/perturb.py` to full copies of the export under
`/tmp/verify-D6-3/{base,d601,d602,d603,d605}` (each replacement asserted to
occur exactly once); the export itself was not modified, and no `__pycache__`
was left in it. My own harness is `/tmp/verify-D6-3/verify3.py` (one metric
per finding, run against each copy; outputs `verify3_<copy>.out`).

## Re-run of the finder's harness

`PYTHONPATH=tests/hastub python tools/audit/round2/D6/claims.py` from the
export root, network on:

```
RESULT claims_extracted=273  claims_checked=263  claims_true=258
RESULT claims_false=1  claims_stale=4  claims_unverifiable=10
RESULT thread_factor=1.000  load1=3.96  swapins=0
```

Exact match with the header. Offline control on the unperturbed copy
(`D6_OFFLINE=1`, used for all perturbation runs): true=249, false=1, stale=4,
unverifiable=19 — the ten link rows flip to unverifiable as the header says;
false/stale are unaffected.

| copy | edit | row | before → after | false | stale | true (offline) |
|---|---|---|---|---|---|---|
| base | none | — | — | 1 | 4 | 249 |
| d601 | nine README rows qualified | C040 | 9 differ → 0, stale → true | 1 | 3 | 250 |
| d602 | services.yaml wind example/description 0.15 → 0.03 | C093 | 0.15 vs 0.03 → 0.03 vs 0.03, stale → true | 1 | 3 | 250 |
| d603 | services.yaml minima 0.0/0 → 0.01 | C092 | 2 rejected → 0, false → true | 0 | 4 | 250 |
| d605 | DISCLAIMER:71-72 reworded as the finder proposes | C305 | **stale → stale, no change** | 1 | 4 | 249 |

## D6-01 · README sensor table omits nine qualifiers

- **My number.** 9 → 0 (verify3: `d601_readme_sensor_rows_not_in_strings`),
  and the reverse difference 9 → 0; binary-sensor and button tables 0.
- **Metric.** Count of first-column names in the README `### Sensors (55
  total)` table that are not byte-equal to any `strings.json`
  `entity.sensor.*.name` — a string set difference, no roster resolution
  (the finder resolves through the real `async_setup_entry`; both give 9).
- **Perturbation.** Finder's C040: 9 → 0, stale → true. Mine: 9 → 0 both ways.
- **Scope.** `strings.json` carries 13 qualified sensor names; four
  (`Buffer Tank Temperature (Model)`, `Indoor/Outdoor Temperature
  (Optimizer)`, `Slab Temperature (Estimated)`) are already qualified in the
  README; the other nine are exactly the finding. The unqualified forms
  occur nowhere else in README.md, DISCLAIMER.md or docs/*.md (grep). Binary
  sensor and button tables match `strings.json` byte for byte. Complete.
- **Vote: verify (low).** Deciding number 9 → 0.

## D6-02 · services.yaml teaches the retired 0.15 wind default

- **My number.** |example − `DEFAULT_WIND_SENSITIVITY`| = 0.1200 → 0.0000;
  description-quotes-the-default 0 → 1.
- **Metric.** Absolute difference between `services.yaml
  set_thermal_parameters.fields.wind_sensitivity_factor.example` and
  `const.DEFAULT_WIND_SENSITIVITY`; plus whether the description's first
  number equals the default.
- **Perturbation.** Finder's C093: observed 0.15 → 0.03 = expected, stale →
  true. Mine: 0.12 → 0.
- **Scope.** All 25 numeric `set_thermal_parameters` examples were matched to
  a `const.DEFAULT_*` (19 by name, six by alias: `DEFAULT_INTER_ZONE_TRANSFER`
  0.5, `DEFAULT_SOLAR_HEAT_GAIN_COEFF` 0.7, `DEFAULT_DHW_MIN_TEMP` 45,
  `DEFAULT_DHW_IDLE_MIN_TEMP` 20, `DEFAULT_DHW_LEGIONELLA_TEMP` 60,
  `DEFAULT_ECL110_PID_TIME_CONSTANT` 1.5): exactly one differs, the wind
  factor. `const.py` names only one replaced default (line 1036). `0.15` in
  user-facing text elsewhere is the heat-loss coefficient (services.yaml:64,
  configuration.md:128, how-it-works.md:277 — equal to
  `DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT`) or the overshoot bound
  (how-it-works.md:1235); the `strings.json`/`en.json`/`sv.json` wind
  descriptions carry no number; the rain sibling (1.15) equals its default.
  The other description numbers (economy 1.5 K/15 °C, DHW reference 45/20 °C)
  equal their constants. Complete: a single instance.
- **Vote: verify (low).** Deciding number 0.12 → 0.

## D6-03 · two selectors admit 0, the schema rejects it

- **My number.** 2 → 0 of 39 number selectors.
- **Metric.** Count of (service, field, min|max) where
  `schema({**required_examples, field: bound})` raises, the eleven schemas
  mapped statically from the `async_register` block of `__init__.py`
  (not from the runtime registry); the rejection text is recorded. Both
  rejections read "value must be at least 0.01 for dictionary value @
  data['inter_zone_heat_transfer' | 'window_area']" — the named field's
  `vol.Range`, nothing else.
- **Perturbation.** Finder's C092: 2 → 0, false → true (C091 examples and
  C094 documented ranges stay true). Mine: 2 → 0.
- **Scope.** 39/39 selectors across all 11 services checked at both bounds;
  no other rejection. 22 selectors are strictly *narrower* than their schema
  (form tighter than the API) — not a defect, listed in `verify3_base.out`.
  `config_flow.py` has no `vol.Range` at all, so the selector-vs-schema class
  has no second site in the config/options flow; its custom validations are
  token, window, fee-rule and month/hour parsing, not numeric bounds.
  configuration.md:576,578 documents 0.01 for both fields (matches the
  schema). Complete. Note for the fixer: min 0.01 with `step` 0.1 / 0.5
  leaves the slider on off-grid values; widening `_positive` to 0 is what
  the comment at `__init__.py:250-253` forbids (a zero flows into the model).
- **Vote: verify (low).** Deciding number 2 → 0.

## D6-04 · "6.7 degree-hours to zero" does not reproduce

Not re-run (the box is held for timing); judged from
`rolling_learning.py`, its three captures and `tests/rolling.py`.

- **My number.** From the captures: 9.634 → 0.044 degree-hours at
  plant_error 1.35 (two bit-identical runs); 0.000 → 0.000 at plant_error 1.0
  (`rolling_learning_null.out`, scale_end 0.9829, 287 samples both).
- **Metric.** Σ max(0, comfort floor − room) × DT over the 3-day closed loop,
  learner off vs on — the expression at `tests/rolling.py:489-493`.
- **Harness faithfulness.** The harness execs the pre-`R.section` prefix of
  `tests/rolling.py` and calls the same two arms as `rolling.py:457-462`
  (`days=3, dhw=False, plant_error=1.35, config={"heat_pump_max_power":
  4.25}`, learn on/off) and the same `floor_for`/`DT` breach. No RNG in
  `optimizer.py`, `coordinator.py`, `thermal_model.py`, `tests/profiles.py`
  or `tests/rolling.py` (`np.random`, `default_rng`, `seed` absent) and no
  module-level caches, so the suite's earlier sections cannot change the
  arm's numbers through shared state — the isolation is not the cause of
  the difference.
- **Perturbation.** `D6_PLANT_ERROR=1.0`: breach_uncorrected 9.634 → 0.000,
  breach_learned 0.044 → 0.000 — moves to zero as stated; the number is the
  mechanism's, and the harness hooks `run_rolling`, not a constant.
- **Scope.** "6.7" occurs in exactly three places: README:487,
  how-it-works.md:1238 and the comment at tests/rolling.py:452. No captured
  run output in the export carries degree-hours; the other rolling.py
  figures quoted in the docs are asserted thresholds (C290–C292, C294 true).
  Complete.
- **Residual attack.** Machine dependence (the finder's own caveat). The
  cleanest re-take is `tests/rolling.py` itself: its check at line 494-498
  prints "X -> Y degree-hours". If the quiet-box run prints 6.7 -> 0.0 the
  figure is machine-dependent rather than stale, still unasserted; the
  severity is low either way.
- **Vote: verify (low).** Deciding numbers 9.634 → 0.044 quoted as 6.7 → 0;
  null 0.000 → 0.000.

## D6-05 · DISCLAIMER calls the space baseline always-on

- **Finder's harness: void for this finding.** C305 is
  `lambda: ok(False, …, stale=True)` — a constant. On the reworded copy
  (d605) C305 stays `stale` and every count is unchanged (249/1/4/19). The
  stated perturbation ("C305 flips to true") does not happen; under the
  harness contract a RESULT computed from a constant is voided. C303 is a
  regex over `optimizer.py` docstrings (text, not behaviour).
- **My number.** 1 → 0 sentences; code anchor 1.
- **Metric.** Count of sentences in README.md, DISCLAIMER.md and
  docs/{architecture,configuration,dashboard-card,ecl110,how-it-works}.md
  matching `/always[- ]on thermostat/`; plus a code anchor — whether the
  *body* of `HeatPumpOptimizer._compute_baseline_power` (docstring stripped
  by `ast`) indexes `comfort_targets[i]` per step (optimizer.py:5207-5210;
  it does). The DHW baseline is the always-hot block at
  optimizer.py:4786-4816.
- **Perturbation.** The finder's rewording of DISCLAIMER:71-72: my count
  1 → 0. The finder's row: no movement.
- **Scope.** Grep of all user docs, `strings.json`, `en.json`,
  `services.yaml` and the card for always-on / always-hot / conventional
  thermostat / permanently hot / compares against: README:271 is correct
  ("only the hot-water half … is always-on"); README:105 and
  how-it-works.md:529 ("the always-hot baseline", in the DHW draw-scaling
  section, lines 522-530) describe the hot-water baseline, which is
  always-hot; `strings.json:684` "always on" is the open-window detector.
  DISCLAIMER:71-72 is the only document describing the space baseline as
  always-on. Complete: 1 of 8 documents.
- **Vote: verify (low)** on verify-3's number (1 → 0), with the finder's
  harness row voided — the judge should not count C305 as evidence; a
  replacement check must read DISCLAIMER.md. The substantive claim is
  correct and conservative (an always-on reference would overstate savings).

## Summary

| finding | finder's harness moves | my number | vote |
|---|---|---|---|
| D6-01 | yes, 9 → 0 | 9 → 0 (string set difference) | verify (low) |
| D6-02 | yes, 0.12 → 0 | 0.12 → 0; 1 of 25 examples off its default | verify (low) |
| D6-03 | yes, 2 → 0 | 2 → 0 of 39, named-field Range | verify (low) |
| D6-04 | yes (null .out), 9.634 → 0.000 | 9.634 → 0.044 vs quoted 6.7 → 0 | verify (low); judge re-takes on the quiet box via tests/rolling.py |
| D6-05 | **no** — C305 is a constant, void | 1 → 0 sentences; body uses comfort_targets | verify (low) on verify-3's harness |
