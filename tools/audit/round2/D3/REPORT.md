# D3 round 2 -- test-suite gaps and suite resource use

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`; worktree `audit-r2-D3` (throwaway branch `d3-mutants`, reset to the baseline after every mutant). Box: 8-core Apple M1 shared with the other auditors (load1 3.0-5.0 while this ran); every wall/CPU number here is provisional. Exposure: none (no docs read).

## Method

1. `candidates.py` parses every production module with `ast` and enumerates deletion sites of six kinds (bail-out guards, clamps, except handlers, payload keys, reason codes, other short `if` blocks): **2254 sites** (clamp 502, except_handler 170, general_if 777, guard_return 766, payload_key 36, reason_code 3). Weights = module consequence weight (money/comfort path 5 ... wording 1) x kind weight (guard/clamp 3, except/payload/reason 2, other if 1); the table is in `pool.json`. Seed **20260902**, weighted sampling without replacement, at most 4 per module, 36 mutants; each mutant is the literal deletion (an emptied block gets `pass`; an except handler becomes `except ():`). Patches: `mutants/M01..M36.patch`, list: `sample.json`.
2. `prescreen.py` applies one mutant at a time, commits it (env_drift refuses HEAD == baseline), runs `tests/env_drift.py --all <baseline>` in the worktree (shared warm cache, hit every time, no writes), rsyncs the mutated tree to a private scratch copy and runs the mutant's measured closure (`tests/closure.py select --files`) there: the cheap scripts always, the expensive ones while the mutant is alive, `features.py` stopped at its first FAIL. Not run: stress.py / edge.py / backtest.py (quiet window), golden.py (strict comparison does not reproduce here: 34/55 DIFF at the baseline), card_drift.mjs (compares the card JS at two refs; a Python mutant cannot move it). The null mutant (comment only) ran first and survived everything.
3. `solve_census.py` counts `HeatPumpOptimizer.optimize` / `scipy.optimize.minimize` / `simulate_trajectory*` calls and `  ok`/`  FAIL` lines per fast script; `closure_precision.py` records, per script, which production modules actually execute versus its recorded closure.

**Result: 18 of 36 mutants survive the pre-screen** (plus the null). Seven are gap candidates (findings D3-01..07, provisional); eleven are equivalent or purely defensive deletions that no check should fail on (listed under non-findings).

## Pre-screen table

| id | module:line | kind | w | closure scripts run | killed by | first failure |
|---|---|---|---|---|---|---|
| M01 | thermal_model.py:1187 | clamp | 15 | 9 | features.py |   FAIL coil identity holds at T_w=70  [reduced 109.11111111111111 + coil -107.111111111111 |
| M02 | optimizer.py:1421 | clamp | 15 | 9 | **survived** |  |
| M03 | coordinator.py:3975 | guard_return | 15 | 5 | env_drift.py,entities.py | TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'NoneType' |
| M04 | thermal_model.py:1943 | clamp | 15 | 9 | **survived** |  |
| M05 | price_model.py:402 | general_if | 3 | 9 | features.py |   FAIL the guessed tail is scaled by the true daily level  [known 3.0 sits on shape 1.5 →  |
| M06 | frontend.py:156 | guard_return | 6 | 6 | frontend.py |   FAIL  a shadowing copy does not stop the bundled card registering |
| M07 | optimizer.py:368 | clamp | 15 | 9 | **survived** |  |
| M08 | thermal_model.py:544 | guard_return | 15 | 9 | **survived** |  |
| M09 | coordinator.py:4926 | general_if | 5 | 9 | features.py |   FAIL an explicit cooling rate restarts the learner from it |
| M10 | optimizer.py:3371 | clamp | 15 | 9 | **survived** |  |
| M11 | optimizer.py:2401 | clamp | 15 | 9 | **survived** |  |
| M12 | coordinator.py:5401 | general_if | 5 | 9 | **survived** |  |
| M13 | coordinator.py:1676 | general_if | 5 | 9 | **survived** |  |
| M14 | inputs.py:565 | guard_return | 12 | 9 | features.py |   FAIL the convenience accessors mirror value()  [an unusable or unread key falls back to  |
| M15 | inputs.py:352 | clamp | 12 | 9 | **survived** |  |
| M16 | dhw_schedule.py:103 | guard_return | 12 | 9 | features.py |   FAIL and renders back to the string the user typed  [weekdays 06:00-08:30, Sa,Su 08:00-0 |
| M17 | topology.py:598 | general_if | 2 | 9 | features.py |   FAIL the wood abstraction is admitted in prose where it still runs  [issue #40: a flue s |
| M18 | thermal_model.py:655 | clamp | 15 | 9 | **survived** |  |
| M19 | dhw_schedule.py:433 | guard_return | 12 | 9 | **survived** |  |
| M20 | away.py:141 | general_if | 3 | 9 | features.py |   FAIL a presence-class binary sensor being on means home  [presence semantics are the inv |
| M21 | accuracy.py:382 | except_handler | 4 | 9 | **survived** |  |
| M22 | snapshots.py:185 | general_if | 2 | 9 | **survived** |  |
| M23 | sensor.py:1515 | general_if | 3 | 2 | entities.py | KeyError: 'counting_since' |
| M24 | dhw_schedule.py:131 | guard_return | 12 | 9 | features.py |   FAIL a malformed weekly spec raises, not silently empties ('Mo 25:00-26:00') |
| M25 | dhw_schedule.py:272 | general_if | 4 | 9 | features.py |   FAIL the weekday/weekend split lands on the right days  [None] |
| M26 | tariff.py:524 | guard_return | 12 | 9 | **survived** |  |
| M27 | snapshots.py:140 | general_if | 2 | 9 | features.py | ValueError: D1-01: malformed month wedges the freezer |
| M28 | grid_fee.py:255 | guard_return | 12 | 5 | env_drift.py | DRIFT coord_grid_fee: 98 leaves moved vs c398fc84eec25fc44b60d74aae05b9a2da205884 |
| M29 | sensor.py:1520 | payload_key | 6 | 2 | entities.py | KeyError: 'this_month_kwh' |
| M30 | open_meteo.py:194 | except_handler | 4 | 10 | **survived** |  |
| M31 | sensor.py:1086 | general_if | 3 | 2 | **survived** |  |
| M32 | grid_fee.py:141 | guard_return | 12 | 9 | **survived** |  |
| M33 | defrost.py:441 | clamp | 9 | 9 | features.py |   FAIL the derate survives a restart |
| M34 | inputs.py:516 | general_if | 4 | 9 | features.py |   FAIL an uninterpretable flag is refused rather than guessed  [None] |
| M35 | grid_fee.py:176 | guard_return | 12 | 9 | **survived** |  |
| M36 | open_meteo.py:145 | guard_return | 6 | 6 | open_meteo.py |   FAIL a barely-overlapping window returns None instead of a misleading value |
| NULL | optimizer.py:0 | null | 0 | 9 | **survived** |  |

Per script over the sample: entities.py 3/37, env_drift.py 2/37, card.mjs 0/34, plan_view.py 0/34, solar_alignment.py 0/34, features.py 12/30, manual_plan.py 0/30, optimality.py 0/30, validate.py 0/30, open_meteo.py 1/2, frontend.py 1/1 (killed/ran). Only M03 was killed by two scripts (entities.py and env_drift.py); overlap among the expensive scripts is unknown because a killed mutant stops there.

## Findings (provisional survivors, ranked for the quiet window)

### D3-01 (M31, medium) PredictiveInsightSensor can lose all 21 attributes and no script notices

- claim: Deleting the whole attribute-building branch of PredictiveInsightSensor.extra_state_attributes (21 published attributes become {}) fails none of entities.py (538 checks), env_drift --all (55 scenarios) or golden.py's coordinator captures.
- mechanism: entities.py drives async_setup_entry and asserts on many entities' values, but never on this sensor's attributes; golden's coordinator capture records _build_data_dict(), not entity attributes, so an entity-layer regression on published attributes is invisible to the gate.
- production line: custom_components/heatpump_optimizer/sensor.py:1086 (`if self.coordinator.data:` block; with it gone the method returns {} unconditionally)
- which check should have failed: tests/entities.py: the collected `sensor.*_predictive_optimization_insight` entity's attributes should be asserted (at least the key set: solar_reduction_factor, pre_heat_urgency, dhw_next_window_in_hours, ...); grep finds no `predictive_optimization_insight` in tests/entities.py or tests/features.py
- closure: entities.py, env_drift.py, golden.py; run: entities.py, env_drift.py; not run: tests/golden.py
- pre-screen: 0 of 2 scripts failed (entities.py, env_drift.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M31.patch`; fix scope: tests/entities.py: one attribute-key assertion per entity whose extra_state_attributes is built from coordinator.data (PredictiveInsightSensor first).

### D3-02 (M19, medium) hours_until_next_window's inside-a-window branch is never exercised: every golden solve starts at 00:00

- claim: With the inside-a-window early return deleted, `dhw_next_window_in_hours` (published in predictive_info via optimizer.py:3672/4887 and in the DHW view via coordinator.py:4121/6704) would read the time to the FOLLOWING window while inside one, and no script fails.
- mechanism: The published value is only ever computed at hour 0.0 in the golden set (outside every window), pump_schedule.dhw_pump_should_run tests hour_in_windows itself before calling, and no unit check targets the function; the branch is dead to the suite although it is the documented contract of the function.
- production line: custom_components/heatpump_optimizer/dhw_schedule.py:433-434 (`if hour_in_windows(hour, windows): return 0.0`)
- which check should have failed: tests/features.py: a direct check `hours_until_next_window(18.0, parse_windows('06:00-08:30, 17:00-22:00')) == 0.0`; and/or one golden scenario whose START lies inside a DHW window (all 49 plan scenarios and 5 coordinator scenarios use START = 2026-01-15 00:00, tests/golden.py:48)
- closure: backtest.py, card.mjs, card_drift.mjs, edge.py, entities.py, env_drift.py, features.py, golden.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, stress.py, validate.py; run: card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py; not run: tests/backtest.py, tests/edge.py, tests/stress.py, tests/card_drift.mjs, tests/golden.py
- pre-screen: 0 of 9 scripts failed (card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M19.patch`; fix scope: tests/features.py: direct checks of hours_until_next_window inside / outside / wrapping windows; tests/golden.py: one scenario with a start time inside a demand window.

### D3-03 (M13, medium) The DHW setpoint advisor's negative-price floor is untested: a worthless-energy day is never fed to the sweep

- claim: Deleting the floor that keeps the advisor's cost ranking meaningful on a non-positive mean price (the code comment says min-cost then 'crowns the candidate using the MOST energy') fails none of features.py's three sweep checks, entities.py or env_drift --all.
- mechanism: Every coordinator scenario and every sweep check uses positive prices; the guard sits on a path the suite never reaches, so the published `dhw_advisor` recommendation on a negative-price day is unprotected.
- production line: custom_components/heatpump_optimizer/coordinator.py:1676-1677 (`if mean_price <= 1e-6: mean_price = max(abs(mean_price), 0.1)`)
- which check should have failed: tests/features.py around line 7744 ('#9 the setpoint sweep'): a sweep with a negative or zero mean price (tests/profiles.py has `summer_negative`) asserting the recommendation is still the cheapest candidate that covers the heaviest window
- closure: backtest.py, card.mjs, card_drift.mjs, edge.py, entities.py, env_drift.py, features.py, golden.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, stress.py, validate.py; run: card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py; not run: tests/backtest.py, tests/edge.py, tests/stress.py, tests/card_drift.mjs, tests/golden.py
- pre-screen: 0 of 9 scripts failed (card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M13.patch`; fix scope: tests/features.py: one sweep check under summer_negative prices.

### D3-04 (M32, low) A non-finite grid-fee rate ('= nan', '= inf') passes rule validation unnoticed

- claim: With the finiteness check deleted, `is_valid_spec('Mon-Fri = nan')` is True and a NaN rate reaches fee_vector (the coordinator's magnitude audit compares with `>` and never sees NaN); no script fails.
- mechanism: The validation checks in features.py cover unparsable tokens ('banana', 'Frunday', missing rate) but not the one float() accepts and the planner cannot price.
- production line: custom_components/heatpump_optimizer/grid_fee.py:141-142 (`if not np.isfinite(rate): raise GridFeeError`)
- which check should have failed: tests/features.py ~6351 (`not _gf.is_valid_spec(...)` family): add `not is_valid_spec('06:00-22:00 = nan')` and `= inf`
- closure: backtest.py, card.mjs, card_drift.mjs, edge.py, entities.py, env_drift.py, features.py, golden.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, stress.py, validate.py; run: card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py; not run: tests/backtest.py, tests/edge.py, tests/stress.py, tests/card_drift.mjs, tests/golden.py
- pre-screen: 0 of 9 scripts failed (card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M32.patch`; fix scope: tests/features.py: two is_valid_spec negatives.

### D3-05 (M21, low) A corrupt lead_sigma KEY in the accuracy store would abort coordinator setup; only corrupt values are tested

- claim: Neutralising the handler that skips a non-numeric lead_sigma key fails no script: the existing malformed-store check exercises a NaN value and a 'junk' value but every key is numeric.
- mechanism: The store-hardening checks were written from the values side; the key side of the same dict has its own try/except that nothing reaches.
- production line: custom_components/heatpump_optimizer/accuracy.py:382-383 (`except (TypeError, ValueError): continue` around `float(key)`)
- which check should have failed: tests/features.py ~9845 (the malformed lead_sigma store check) should also carry a non-numeric key, e.g. `{'abc': 0.4}`; `_async_load_accuracy` (coordinator.py:7230) only guards async_load, not from_dict
- closure: backtest.py, card.mjs, card_drift.mjs, edge.py, entities.py, env_drift.py, features.py, golden.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, stress.py, validate.py; run: card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py; not run: tests/backtest.py, tests/edge.py, tests/stress.py, tests/card_drift.mjs, tests/golden.py
- pre-screen: 0 of 9 scripts failed (card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M21.patch`; fix scope: tests/features.py: extend the malformed-store fixture with one bad key.

### D3-06 (M30, low) One unparsable Open-Meteo timestamp would discard the whole forecast block; the skip is untested

- claim: Neutralising the per-sample timestamp handler fails none of open_meteo.py's 30 checks or features.py; a ValueError would then propagate out of fetch() and lose the block instead of the sample.
- mechanism: open_meteo.py's checks cover nulls, out-of-range values and missing variables, not a malformed time string.
- production line: custom_components/heatpump_optimizer/open_meteo.py:194-195 (`except ValueError: continue` around datetime.fromisoformat)
- which check should have failed: tests/open_meteo.py: a block with one malformed `time` entry keeps the other samples (30 checks today, none with a bad stamp)
- closure: backtest.py, card.mjs, card_drift.mjs, edge.py, entities.py, env_drift.py, features.py, golden.py, manual_plan.py, open_meteo.py, optimality.py, plan_view.py, solar_alignment.py, stress.py, validate.py; run: card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, open_meteo.py, optimality.py, plan_view.py, solar_alignment.py, validate.py; not run: tests/backtest.py, tests/edge.py, tests/stress.py, tests/card_drift.mjs, tests/golden.py
- pre-screen: 0 of 10 scripts failed (card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, open_meteo.py, optimality.py, plan_view.py, solar_alignment.py, validate.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M30.patch`; fix scope: tests/open_meteo.py: one malformed-stamp sample.

### D3-07 (M15, low) A future-stamped sensor state yields a negative published age_minutes; the clamp is untested

- claim: Dropping the clamp fails no script; a state stamped in the future (clock skew) would publish a negative age in the input-health details.
- mechanism: No freshness check uses a future timestamp.
- production line: custom_components/heatpump_optimizer/inputs.py:352 (`max(0.0, ...)`)
- which check should have failed: tests/features.py freshness checks: a state whose last_reported is ahead of now reads age 0.0, not negative
- closure: backtest.py, card.mjs, card_drift.mjs, edge.py, entities.py, env_drift.py, features.py, golden.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, stress.py, validate.py; run: card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py; not run: tests/backtest.py, tests/edge.py, tests/stress.py, tests/card_drift.mjs, tests/golden.py
- pre-screen: 0 of 9 scripts failed (card.mjs, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, solar_alignment.py, validate.py); env_drift --all: NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84eec25fc44b60d74aae05b9a2da205884
- patch: `tools/audit/round2/D3/mutants/M15.patch`; fix scope: tests/features.py: one future-stamp reading.

Quiet-window request: full `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline>` gate for M31, M19, M13, M32, M21, M30 (then M15).

## Resource use

### D3-08 solves versus assertions versus kills (solve_census.py + prescreen)

| script | optimize() | minimize() | simulate*() | ok lines | cpu s here | recorded CI s | killed/ran |
|---|---|---|---|---|---|---|---|
| features.py | 94 | 190 | 21460 | 1576 | 31.4 | 509.8 | 12/30 |
| entities.py | 0 | 0 | 0 | 538 | 2.5 | 3.5 | 3/37 |
| manual_plan.py | 21 | 64 | 927 | 71 | 4.1 | 26.4 | 0/30 |
| optimality.py | 9 | 18 | 30498 | 11 | 33.8 | 20.8 | 0/30 |
| validate.py | 22 | 44 | 5206 | 0 | 12.7 | 223.3 | 0/30 |
| plan_view.py | 1 | 2 | 35 | 0 | 0.7 | 1.9 | 0/34 |
| solar_alignment.py | 0 | 0 | 0 | 12 | 0.6 | 1.0 | 0/34 |
| open_meteo.py | 0 | 0 | 0 | 30 | 0.6 | 0.2 | 1/2 |

validate.py asserts through 21 `issue(...)` invariant sites (no harness checks, hence 0 ok lines) and plan_view.py through 10; optimality.py spends 30,498 simulate calls on perturbation challengers for 11 checks. The four solver scripts plus plan_view/card ran 30-34 mutants each and killed none; features.py alone killed 12 of 30. That is not an argument to delete them (they guard solver quality, which guard deletions do not probe) but it is the number behind the closure question below. Census artefacts: frontend.py and dst_checks.py fail under the runpy census (argv / HASTUB_TZ ordering) and are excluded; both pass when run as the gate runs them.

### D3-09 closure precision (closure_precision.py)

- open_meteo.py: rc=0 forced=['const.py'] executed_not_in_closure=[]
- solar_alignment.py: rc=0 forced=['accuracy.py', 'away.py', 'battery.py', 'comfort_band.py', 'comfort_learning.py', 'const.py', 'currency.py', 'curve_learning.py', 'defrost.py', 'dhw_draws.py', 'dhw_schedule.py', 'diagnosis.py', 'drift.py', 'external_heat.py', 'freq_control.py', 'frontend.py', 'inputs.py', 'ledger.py', 'manual_plan.py', 'mixing_valve.py', 'narrative.py', 'power_guard.py', 'pump_schedule.py', 'pump_signals.py', 'pv.py', 'snapshots.py', 'sysid.py', 'tariff.py', 'topology.py', 'wear.py'] executed_not_in_closure=[]
- plan_view.py: rc=0 forced=['away.py', 'battery.py', 'comfort_band.py', 'comfort_learning.py', 'const.py', 'currency.py', 'curve_learning.py', 'defrost.py', 'dhw_draws.py', 'diagnosis.py', 'drift.py', 'external_heat.py', 'freq_control.py', 'frontend.py', 'grid_fee.py', 'inputs.py', 'ledger.py', 'manual_plan.py', 'narrative.py', 'open_meteo.py', 'power_guard.py', 'price_model.py', 'pump_schedule.py', 'pump_signals.py', 'pv.py', 'snapshots.py', 'sysid.py', 'topology.py', 'wear.py'] executed_not_in_closure=[]
- entities.py: rc=0 forced=['diagnosis.py', 'drift.py', 'freq_control.py', 'narrative.py', 'open_meteo.py', 'power_guard.py', 'pump_schedule.py', 'pv.py', 'snapshots.py'] executed_not_in_closure=[]
- optimality.py: rc=0 forced=['accuracy.py', 'away.py', 'battery.py', 'comfort_band.py', 'comfort_learning.py', 'coordinator.py', 'currency.py', 'curve_learning.py', 'defrost.py', 'dhw_draws.py', 'diagnosis.py', 'drift.py', 'external_heat.py', 'freq_control.py', 'frontend.py', 'grid_fee.py', 'inputs.py', 'ledger.py', 'manual_plan.py', 'narrative.py', 'open_meteo.py', 'power_guard.py', 'price_model.py', 'pump_schedule.py', 'pump_signals.py', 'pv.py', 'snapshots.py', 'sysid.py', 'topology.py', 'wear.py'] executed_not_in_closure=[]
- manual_plan.py: rc=0 forced=['away.py', 'battery.py', 'comfort_band.py', 'comfort_learning.py', 'curve_learning.py', 'dhw_draws.py', 'diagnosis.py', 'drift.py', 'freq_control.py', 'frontend.py', 'grid_fee.py', 'inputs.py', 'ledger.py', 'narrative.py', 'open_meteo.py', 'power_guard.py', 'pump_schedule.py', 'pump_signals.py', 'pv.py', 'snapshots.py', 'topology.py', 'wear.py'] executed_not_in_closure=[]
- validate.py: rc=0 forced=['accuracy.py', 'away.py', 'battery.py', 'comfort_band.py', 'comfort_learning.py', 'coordinator.py', 'currency.py', 'curve_learning.py', 'defrost.py', 'dhw_draws.py', 'diagnosis.py', 'drift.py', 'external_heat.py', 'freq_control.py', 'frontend.py', 'grid_fee.py', 'inputs.py', 'ledger.py', 'manual_plan.py', 'narrative.py', 'open_meteo.py', 'power_guard.py', 'price_model.py', 'pump_schedule.py', 'pump_signals.py', 'pv.py', 'snapshots.py', 'sysid.py', 'topology.py', 'wear.py'] executed_not_in_closure=[]
- features.py: rc=0 forced=['manual_plan.py', 'open_meteo.py'] executed_not_in_closure=[]

Per production module, CI seconds of measured fast scripts that would run for a change to it without executing it (top 20):
- open_meteo.py          forced_ci_s=  785.7 forced_by=['plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py', 'features.py'] executed_by=['open_meteo.py', 'solar_alignment.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- manual_plan.py         forced_ci_s=  756.8 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'validate.py', 'features.py'] executed_by=['entities.py', 'manual_plan.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- snapshots.py           forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- pv.py                  forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- pump_schedule.py       forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- power_guard.py         forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- narrative.py           forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- freq_control.py        forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- drift.py               forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- diagnosis.py           forced_ci_s=  276.9 forced_by=['solar_alignment.py', 'plan_view.py', 'entities.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- wear.py                forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- topology.py            forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- pump_signals.py        forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- ledger.py              forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- inputs.py              forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- frontend.py            forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- dhw_draws.py           forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- curve_learning.py      forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- comfort_learning.py    forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']
- comfort_band.py        forced_ci_s=  273.4 forced_by=['solar_alignment.py', 'plan_view.py', 'optimality.py', 'manual_plan.py', 'validate.py'] executed_by=['entities.py', 'features.py'] unmeasured_quiet=['stress.py', 'edge.py', 'backtest.py']

Caveat: 'executed' counts function bodies (CO_OPTIMIZED code objects), so const.py -- which matters only through import-time constants -- shows as forced for open_meteo/solar_alignment/plan_view although it is a real dependency; every other forced module above is code the script never calls. The mechanism is `custom_components/heatpump_optimizer/__init__.py:64-77`: the package import pulls in coordinator.py and with it the whole integration, so `sys.modules` at exit -- which closure.py records -- names every module for every script. The quiet-window trio is unmeasured here.

### Recorded seconds versus this box

closures.json's `seconds` are CI seconds: on the NULL run features.py took 36.9 s wall (recorded 509.8), validate.py 14.5 (223.3), manual_plan.py 3.9 (26.4), entities.py 2.2 (3.5), optimality.py 29.3 (20.8 -- slower here, single-thread bound on 30k simulate calls), env_drift --all 46 s with a warm baseline cache (recorded 0.7). The full gate table is the quiet window's; these are the fan-out numbers with load1 and thread_factor=1.000 recorded in prescreen_results.json.

## Non-findings

- null control: a comment-only production change survives every closure script and env_drift --all (the prescreen does not kill everything) -- `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTH` -> 0 of 9 scripts failed; env_drift: NO UNCLAIMED DRIFT: 55 scenario(s) checked
- M01 thermal_model.py:1187 clamp (max(0.0, dhw_setpoint - t_in)) is killed -- `tools/audit/round2/D3/prescreen.py --ids M01 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL coil identity holds at T_w=70  [reduced 109.11111111111111 + coil -107.11111111111111 != draw 2.0]
- M03 coordinator.py:3975 guard_return (if last is None:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M03 (full command: findings[0].evidence.command)` -> killed by env_drift.py,entities.py: TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'NoneType'
- M05 price_model.py:402 general_if (if shape_mean > 1e-6:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M05 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL the guessed tail is scaled by the true daily level  [known 3.0 sits on shape 1.5 → level 2.0; hour 12 at shape 0.5 must be 1.0, not 1.5, got 1.5]
- M06 frontend.py:156 guard_return (if not item_url or item_url.split("?")[0] != base:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M06 (full command: findings[0].evidence.command)` -> killed by frontend.py:   FAIL  a shadowing copy does not stop the bundled card registering
- M09 coordinator.py:4926 general_if (if CONF_DHW_COOLING_RATE in params:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M09 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL an explicit cooling rate restarts the learner from it
- M14 inputs.py:565 guard_return (if reading is None or not reading.ok or reading.flag is None) is killed -- `tools/audit/round2/D3/prescreen.py --ids M14 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL the convenience accessors mirror value()  [an unusable or unread key falls back to the caller's default]
- M16 dhw_schedule.py:103 guard_return (if ordered == [5, 6]:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M16 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL and renders back to the string the user typed  [weekdays 06:00-08:30, Sa,Su 08:00-09:30]
- M17 topology.py:598 general_if (if not two_tank:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M17 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL the wood abstraction is admitted in prose where it still runs  [issue #40: a flue switch without a probe still folds wood heat into the heat-pump tank, a
- M20 away.py:141 general_if (if domain == "binary_sensor":) is killed -- `tools/audit/round2/D3/prescreen.py --ids M20 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL a presence-class binary sensor being on means home  [presence semantics are the inverse of a toggle; reading on as away deep-setbacks an occupied house]
- M23 sensor.py:1515 general_if (if since:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M23 (full command: findings[0].evidence.command)` -> killed by entities.py: KeyError: 'counting_since'
- M24 dhw_schedule.py:131 guard_return (if hour > 23:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M24 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL a malformed weekly spec raises, not silently empties ('Mo 25:00-26:00')
- M25 dhw_schedule.py:272 general_if (if m:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M25 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL the weekday/weekend split lands on the right days  [None]
- M27 snapshots.py:140 general_if (if not self.alarmed and self._bias_days >= BIAS_TRIP_DAYS:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M27 (full command: findings[0].evidence.command)` -> killed by features.py: ValueError: D1-01: malformed month wedges the freezer
- M28 grid_fee.py:255 guard_return (if self.mode == MODE_RULES:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M28 (full command: findings[0].evidence.command)` -> killed by env_drift.py: DRIFT coord_grid_fee: 98 leaves moved vs c398fc84eec25fc44b60d74aae05b9a2da205884
- M29 sensor.py:1520 payload_key (attrs["this_month_kwh"] = round(month[0], 3)) is killed -- `tools/audit/round2/D3/prescreen.py --ids M29 (full command: findings[0].evidence.command)` -> killed by entities.py: KeyError: 'this_month_kwh'
- M33 defrost.py:441 clamp (max(DERATE_MIN, v)) is killed -- `tools/audit/round2/D3/prescreen.py --ids M33 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL the derate survives a restart
- M34 inputs.py:516 general_if (if flag is None:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M34 (full command: findings[0].evidence.command)` -> killed by features.py:   FAIL an uninterpretable flag is refused rather than guessed  [None]
- M36 open_meteo.py:145 guard_return (if total_weight < 0.5 * requested:) is killed -- `tools/audit/round2/D3/prescreen.py --ids M36 (full command: findings[0].evidence.command)` -> killed by open_meteo.py:   FAIL a barely-overlapping window returns None instead of a misleading value
- M02 optimizer.py:1421 clamp survived but is equivalent/defensive -- no check should fail: cop_end comes from ThermalModel.compute_cop, whose factor is floored at 0.3 x cop_nominal (thermal_model.py:1311); the 1e-6 floor is unreachable -- `tools/audit/round2/D3/prescreen.py --ids M02 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M04 thermal_model.py:1943 clamp survived but is equivalent/defensive -- no check should fail: dt_hours is the (sub-)step length, always > 0; the 1e-6 floor is unreachable -- `tools/audit/round2/D3/prescreen.py --ids M04 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M07 optimizer.py:368 clamp survived but is equivalent/defensive -- no check should fail: the divisor only degenerates for a ONE-step horizon with a non-positive mean price (rank branch); 15-min steps over >= 1 h give n >= 4. Defensive; edge.py (quiet window) is the only script with short horizons -- `tools/audit/round2/D3/prescreen.py --ids M07 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M08 thermal_model.py:544 guard_return survived but is equivalent/defensive -- no check should fail: a memoisation cache for the wood-tank UA; deleting it is behaviour-preserving (slower only) -- `tools/audit/round2/D3/prescreen.py --ids M08 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M10 optimizer.py:3371 clamp survived but is equivalent/defensive -- no check should fail: ua only multiplies (decay, gain) in the run-up walk, nothing divides by it; the 1e-6 floor changes nothing observable -- `tools/audit/round2/D3/prescreen.py --ids M10 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M11 optimizer.py:2401 clamp survived but is equivalent/defensive -- no check should fail: planned is n+1 long (trimmed to n) or already n, so steps == req.size either way; the min() is defensive against a shape the optimizer never produces -- `tools/audit/round2/D3/prescreen.py --ids M11 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M12 coordinator.py:5401 general_if survived but is equivalent/defensive -- no check should fail: a non-200 Tibber response then reaches resp.json() and either the 'errors' branch, the 'No homes' branch or the outer `except Exception` (coordinator.py:5437-5441); every path still calls _tibber_fetch_failed, only the message differs. Equivalent in effect; no fake-session test exists either way -- `tools/audit/round2/D3/prescreen.py --ids M12 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M18 thermal_model.py:655 clamp survived but is equivalent/defensive -- no check should fail: dhw_setpoint is bounded 40-65 by the config flow (config_flow.py:1308 `_number(40, 65, ...)`), so min(70, setpoint) is unreachable through validated config (ThermalParameters.clamp does not clamp it, so a hand-edited entry could reach it) -- `tools/audit/round2/D3/prescreen.py --ids M18 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M22 snapshots.py:185 general_if survived but is equivalent/defensive -- no check should fail: the deleted lines are a _LOGGER.warning only; the `continue` that matters is untouched -- `tools/audit/round2/D3/prescreen.py --ids M22 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M26 tariff.py:524 guard_return survived but is equivalent/defensive -- no check should fail: without the early return top_k is a slice of zeros and the function returns 0.0 anyway -- `tools/audit/round2/D3/prescreen.py --ids M26 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- M35 grid_fee.py:176 guard_return survived but is equivalent/defensive -- no check should fail: callers pass `config.get(..., '')` / `user_input.get(..., '')`, never None; for '' the loop yields [] anyway. Only spec=None would differ (str(None) -> GridFeeError) -- `tools/audit/round2/D3/prescreen.py --ids M35 (full command: findings[0].evidence.command)` -> 0 of 9 scripts failed
- the shared drift-baseline cache was hit on every env_drift run and nothing was written by this audit (entries added during the window belong to other worktrees: b4d08f7, e403f75, 68cae56) -- `ls ~/.cache/heatpump_optimizer/drift-baseline/; python tests/env_drift.py --cache-key --all <baseline> (with t` -> 37/37 CACHE HIT on key cc4aa9befed4...; entry count 7 -> 11, none with ref c398fc8 written after 23:19Z
- golden.py strict comparison at the baseline does not reproduce on this machine (as tests/README.md says), which is why the prescreen uses env_drift --all -- `PYTHONPATH=tests/hastub python tests/golden.py` -> 34 of 55 GOLDEN SCENARIOS CHANGED, rc=1, 53.5 s wall
- thread pin holds: process CPU / thread CPU under the five-variable pin -- `python -c '<600x600 matmul x20>' with the pin` -> thread_factor=1.000
- closures.json 'seconds' are CI seconds, not this machine's: the fast set runs ~14x faster here -- `NULL row of prescreen_results.json vs tests/closures.json recorded` -> features.py 36.9 s here vs 509.8 recorded; validate.py 14.5 vs 223.3; manual_plan 3.9 vs 26.4; optimality 29.3 vs 20.8 (slower here); env_drift 46 s here with a warm baseline cache
- the five may-drift (machine-sensitive) fixtures did not move for 36 of 37 mutants; the one that moved (M01, wood_coil) is finding D3-10 -- `grep -c MAY-DRIFT <scratch>/logs/*/env_drift.log` -> 1 MAY-DRIFT scenario in 1 of 37 runs (M01: wood_coil 458 leaves), 0 in the other 36

## Harnesses

- `tools/audit/round2/D3/candidates.py`
- `tools/audit/round2/D3/prescreen.py`
- `tools/audit/round2/D3/solve_census.py`
- `tools/audit/round2/D3/closure_precision.py`
- outputs: `pool.json` (all sites + weights), `sample.json`, `mutants/*.patch`, `prescreen_results.json` (per script rc / wall / cpu / load1 / first failures), `report.json`

## Not finished

- Full-gate confirmation of the survivors (quiet window; not mine to run).
- Kill overlap among features.py / validate.py / optimality.py / manual_plan.py: a mutant killed by the first expensive script was not run through the rest, so duplicated coverage among them is only bounded (they killed nothing on the 30 mutants that reached them).
- edge.py, backtest.py, stress.py were neither run nor traced; M07's one-step-horizon degenerate case is the only survivor edge.py plausibly reaches (it has a 6 h / 5-min case and an all-negative-prices case, not both at once).
- Coverage of the Node side: no JavaScript mutants were sampled (the brief's candidate list is production Python guards); card.mjs/card_drift.mjs kills are therefore untested here.
