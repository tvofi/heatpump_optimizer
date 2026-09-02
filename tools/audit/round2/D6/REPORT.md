# D6 — README and documentation claim verification (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`
(no `.git`, no audit records, no backlog, no release notes). Box: 8-core Apple
M1, 8 GB, macOS Darwin 25.6.0, Python 3.13.1, numpy 2.5.2, scipy 1.18.1,
node v20.10.0, the `tests/hastub` Home Assistant stub. Everything ran during
the fan-out (load1 1.9–3.8, eleven auditors on the box); every number here is
a count, a constant comparison or a deterministic degree-hour sum, none is a
timing, so all are contention-immune. `thread_factor` was 1.000 on every run.

## Method

1. Read `README.md`, `DISCLAIMER.md`, `docs/architecture.md`,
   `docs/configuration.md`, `docs/dashboard-card.md`, `docs/ecl110.md`,
   `docs/how-it-works.md` in full; `services.yaml`, `strings.json`,
   `translations/{en,sv}.json`, `manifest.json`, `hacs.json`; the plan
   documents only far enough to check the one README sentence that cites
   them (see *Exposure*).
2. Extracted 273 claims — every number, default, entity/service name, field,
   unit, range, behaviour, version and link — and wrote one executed check per
   claim into `tools/audit/round2/D6/claims.py`. The checks drive:
   - the five platform `async_setup_entry`s over `tests/harness.py:FakeCoordinator`
     with the `DATA` payload of `tests/entities.py` (read as a literal, because
     that module runs on import), for counts, names, units, categories,
     registry defaults, recorder exclusions, attributes and per-feature
     availability;
   - `heatpump_optimizer.__init__:async_setup_entry` on a recording
     `FakeServices`, for the service registry, `supports_response`, the
     voluptuous schemas, and `services.yaml` fields/examples/selectors fed
     through those schemas;
   - `HeatPumpOptimizerConfigFlow` / `HeatPumpOptimizerOptionsFlow.async_step_*`
     rendered through the stub, for page counts, field counts and every
     documented number range (`NumberSelector` min/max/step);
   - `const.py` and the module constants for every documented default;
   - `FrequencyWatchdog`, `GuardState`, `CurveLearner`, `SnapshotRing`,
     `resolve_currency` driven directly for the behavioural sentences;
   - regex source scans for mechanisms described in prose (marked as such in
     the table — they are checks of the description, not measurements);
   - `HEAD` requests for every external link; file existence for internal ones;
   - `tools/audit/round2/D6/rolling_learning.py`, which re-executes the one
     closed-loop learning arm the README quotes a number from, by running the
     helper block of `tests/rolling.py` in a private namespace and calling its
     `run_rolling` verbatim.
3. Verdicts: `true` / `false` / `stale` (wrong because the code moved on) /
   `unverifiable` (historical measurement, or a document the export removed).

The full table is committed as `tools/audit/round2/D6/claims_table.md`
(the harness's stdout).

## Numbers

```
RESULT claims_extracted=273 count
RESULT claims_checked=263 count
RESULT claims_true=258 count
RESULT claims_false=1 count
RESULT claims_stale=4 count
RESULT claims_unverifiable=10 count
RESULT thread_factor=1.000   RESULT load1=1.86   RESULT swapins=0
```

Command: `PYTHONPATH=tests/hastub python tools/audit/round2/D6/claims.py`
(from the export root; `D6_OFFLINE=1` turns the 10 link checks into
unverifiable rows; `D6_ROLLING_OUT` points C293 at a `rolling_learning.py`
output).

## Findings

All five are documentation hygiene at severity `low`: none changes what the
integration does, none publishes a wrong value. They are grouped by
mechanism (renamed entities; a changed default; selector metadata drifting
from the schema; a quoted test number; a changed baseline definition).

### D6-01 · README sensor table omits the qualifiers of nine entity names (stale)

- **Claim.** README:259 says "the tables below show the English names", but
  nine rows of the 55-row sensor table are not the `strings.json` English
  names the entities actually carry.
- **Evidence.** `claims.py` row C040: 9 of 55 names differ. `DHW Heating
  Cost`, `Space Heating Plan`, `DHW Heating Plan` lack "(next 24 h)";
  `Space Heating Energy`, `Hot Water Energy`, `Total Energy`, `Space Heating
  Cost`, `Hot Water Cost`, `Total Heating Cost` lack "(lifetime)". Every other
  README name is byte-equal to `strings.json` (and `en.json` is byte-equal to
  `strings.json`, `sv.json` has the same 866 keys — rows C024, C025).
- **Instrumented symbol.** `heatpump_optimizer.sensor:async_setup_entry`
  (the roster) against `strings.json:entity.sensor.<translation_key>.name`.
- **Perturbation.** Rewrite the nine README rows to the qualified names (or
  drop the qualifiers from the three translation files): C040 goes to zero.
- **Metric.** Count of README sensor-table rows whose name is not the
  strings.json English name of the entity it resolves to (by exact match,
  else by `name + " ("` prefix).
- **Severity / class.** low / hygiene. Fix scope: nine README lines.

### D6-02 · services.yaml still teaches the retired 0.15 wind default (stale)

- **Claim.** `services.yaml` `set_thermal_parameters.wind_sensitivity_factor`
  has `example: 0.15` and the description "0.15 means 15% more heat loss per
  m/s of wind speed". `const.DEFAULT_WIND_SENSITIVITY` is 0.03, and the
  const comment says the 0.15 default was replaced as physically
  implausible ("+150 % at 10 m/s … made every windy forecast panic-charge the
  house"). README:227, configuration.md:183 and how-it-works.md:291 all say
  0.03.
- **Evidence.** Row C093: example 0.15 vs default 0.03.
- **Instrumented symbol.** `heatpump_optimizer.const:DEFAULT_WIND_SENSITIVITY`
  vs `services.yaml:set_thermal_parameters.fields.wind_sensitivity_factor.example`.
- **Perturbation.** Set the example to 0.03 and reword the description:
  |example − default| goes to zero and the row flips to true.
- **Metric.** |services.yaml example − shipped default| for the field (0.12).
- **Severity / class.** low / hygiene. The Developer Tools form pre-fills a
  value the project itself calls implausible. Fix scope: two lines of
  `services.yaml` (the `rain_heat_loss_multiplier` sibling is correct).

### D6-03 · two services.yaml selectors admit a value the schema rejects (false)

- **Claim.** `services.yaml` declares number selectors with `min: 0.0` for
  `inter_zone_heat_transfer` and `min: 0` for `window_area`; the registered
  schema `SERVICE_SCHEMA_SET_THERMAL_PARAMS` binds both through
  `_positive(...)` = `vol.Range(min=0.01, …)`. A user who slides either to 0
  in Developer Tools gets a validation error; configuration.md:576,578
  documents 0.01 correctly, so the yaml is the odd one out.
- **Evidence.** Row C092: 2 of 39 selector bounds rejected by their own
  schema; row C094: all 25 documented set_thermal_parameters ranges match the
  schema at both bounds (so the schema, not the doc, is the reference).
- **Instrumented symbol.**
  `heatpump_optimizer.__init__:SERVICE_SCHEMA_SET_THERMAL_PARAMS`, taken from
  the registry after `async_setup_entry`.
- **Perturbation.** Raise the two selector minima to 0.01 (or widen `_positive`
  to 0 for those two keys): the count goes to zero.
- **Metric.** Count of (service, field, bound) where the services.yaml number
  selector's `min`/`max` fails the service's voluptuous schema.
- **Severity / class.** low / hygiene (a form value rejected with an error;
  workaround: type 0.01).

### D6-04 · the "6.7 degree-hours to zero" reference run does not reproduce (stale)

- **Claim.** README:486-487 and how-it-works.md:1237-1238: the self-learning
  correction "cuts the comfort breach it exists to fix — in the reference run
  recorded in the test, from 6.7 degree-hours to zero". The figures live in a
  comment in `tests/rolling.py:452-453`; the test asserts only
  `breach_learned < breach_plain`.
- **Evidence.** `rolling_learning.py` re-executes the arm with the test's own
  `run_rolling` (plant_error 1.35, 4.25 kW pump, three days):
  `breach_uncorrected=9.634`, `breach_learned=0.044` degree-hours, scale
  1.000 → 1.331 (truth 1.35, overshoot −0.019), last-quarter std 0.0077,
  287 samples, correct-model drift 0.0167. Two runs are bit-identical
  (`rolling_learning.out`, `rolling_learning_rerun.out`). The asserted
  property holds — learning removes 99.5 % of the breach — but neither
  quoted figure reproduces.
- **Null control.** `D6_PLANT_ERROR=1.0` (the house *is* the model):
  `breach_uncorrected=0.000`, `breach_learned=0.000`
  (`rolling_learning_null.out`) — the number is entirely the mechanism's.
- **Instrumented symbol.** `tests/rolling.py:run_rolling` driving
  `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator` with
  `learn=True` (the heat-loss learner) against the mis-modelled plant.
- **Perturbation.** `D6_PLANT_ERROR=1.0` → `breach_uncorrected` to zero
  (observed 0.000).
- **Metric.** Σ max(0, comfort floor − room) × DT over the 3-day closed loop,
  learner off versus on.
- **Caveat.** `tools/audit/README.md` records that solver floats do not
  reproduce across BLAS builds and the golden fixtures were recorded on
  another machine; the judge may see a third pair of numbers on the fixture
  machine. That is the point: a number the test does not assert, quoted as a
  fact in two documents, is not stable. how-it-works.md:1247-1250 itself
  warns against "documentation that outruns its assertions". Not a timing
  number, so not provisional in the timing sense; machine-dependent.
- **Severity / class.** low / hygiene. Fix scope: re-record the comment and
  the two sentences from a current run, or drop the figures and keep the
  asserted property (the wording how-it-works.md:1247 already recommends).

### D6-05 · DISCLAIMER describes a savings baseline the optimizer no longer uses (stale)

- **Claim.** DISCLAIMER.md:71-72: "the baseline it compares against is a
  simulated always-on thermostat rather than a measurement". The space
  baseline is `HeatPumpOptimizer._compute_baseline_power` — "Simulate a
  conventional thermostat following the comfort schedule … Holding the flat
  target_temp around the clock instead made the reference heat to the *day*
  temperature all night, and a configured night setback was then booked as
  optimizer savings" (optimizer.py:5177-5189). Only the hot-water baseline is
  always-hot (optimizer.py:4786). README:271 says exactly that ("Only the
  hot-water half of the baseline is always-on"), so the two documents
  disagree, and the disclaimer describes the pre-change baseline.
- **Evidence.** Rows C303 (README wording matches the code: true) and C305
  (DISCLAIMER wording: stale) — source scan of the two baseline sites.
- **Instrumented symbol.**
  `heatpump_optimizer.optimizer:HeatPumpOptimizer._compute_baseline_power`
  (docstring and per-step comfort-target tracking) and the always-hot DHW
  baseline block at optimizer.py:4786-4816.
- **Perturbation.** Reword DISCLAIMER.md:71-72 to "a simulated conventional
  thermostat following your comfort schedule, with the hot-water tank kept
  permanently hot": C305 flips to true (documents contradicting the code: 1 → 0).
- **Metric.** Count of documents (README:271, DISCLAIMER:71-72) whose
  baseline description contradicts the optimizer's baseline docstring.
- **Severity / class.** low / hygiene. It errs on the conservative side (an
  always-on reference would *overstate* savings; the real one is stricter),
  which is why it is not higher.

## Non-findings (checked and held)

Command for all: `PYTHONPATH=tests/hastub python tools/audit/round2/D6/claims.py`, row id in brackets.

| What | Value |
|---|---|
| 65 entities = 55 sensors + 4 binary + 4 buttons + 1 switch + 1 climate, through the real platform `async_setup_entry`s [C030-C034] | 55/4/4/1/1 |
| README sensor table has 55 rows; binary/button tables match the rosters by name [C035-C037] | 55, 4, 4 |
| six disabled-by-default sensors are exactly the six named [C039, C043] | match |
| every sensor unit as tabulated (CUR→SEK, CUR/kWh, %, °C, kW, W/m², kWh, L, Hz, —) [C041] | 55/55 |
| Diagnostic marks ⇔ `EntityCategory.DIAGNOSTIC` for all 55+4 rows [C042] | 0 mismatches |
| Not-recorded marks declare `_unrecorded_attributes`; timestamp sensors; energy TOTAL_INCREASING/ENERGY; cost TOTAL/MONETARY [C044-C047] | true |
| Solar Radiation retired in v5.0.0 (`RETIRED_ENTITIES`); CUR = instance currency, SEK fallback [C048-C049] | true |
| DHW Temperature's 7 documented attributes; plan sensors publish `manual_override`, `manual_plan_window_hours=20`, `plan_kind` space/dhw/solar; Measured Power `recommended_power`; Prediction Accuracy `temperature_bias`+`last_diagnosis`; `_freq_view` has `evidence_exhausted`; Input Problem / Away / External Heat attributes [C050-C059] | all present |
| feature-gated availability: Monthly Peak, Solar Surplus, Measured Power, Observed COP, Contract Comparison, Power Headroom, DHW Advisor, Mixed Hot Water, Heavy Day, Optimization Score, Frequency Advisor flip to unavailable when their gate is off; all 55 still exist on a bare payload [C060-C071] | 11/11, 55 |
| Optimize Now unavailable in flight; sysid arm re-reads the option (default off); Heat Pump Action vocabulary; switch turn-on acts only from off; climate modes/presets; set_temperature records an override; climate target = comfort target [C072-C078] | true |
| 11 services registered = README table = services.yaml; 28 set_thermal fields; 11 simulate fields; apply_schedule 5+entry_id; 7 services take entry_id; Returns column = `supports_response`; set_mode = OPERATION_MODES [C080-C088] | 11, 28, 11, 6, 7 |
| services.yaml field sets, required flags and all 35 examples agree with the schemas [C089-C091] | 0 mismatches, 35/35 |
| 25 documented set_thermal ranges hold at both bounds; 21 assignable keys; 4 selectable layouts and slab_shunt refused; 20-hour manual window; `[]` vs omitted; economy 1.5 K / 15 °C; 3 s simulate rate limit; day hour bounds [C094-C101] | true |
| 41 default/constant claims (temperatures, windows, legionella, wind/rain, interval, weights, ring 8, 5-day drift, CUSUM 1.5×, curve 0.5 K/week [−4,0], 300 s writes, 3 ticks, 2/2 guard, tank/buffer/solar/two-zone defaults, tariff, fuse, away, external heat, outage, margins, learners, ECL110, price shape, defrost, fee bound, recovery, 6-h window, 2 starts, 24 h/15 min, p90, hold 20 min, coil) [C110-C161] | all equal |
| watchdog trips on the third active divergent tick, idle resets; guard 2-in/2-out; curve bias −0.4 K after 7 days then reset on a miss; ring keeps 8 of 12 [C170-C173] | as documented |
| 13 option pages = 6 + 7, overview has no fields, labels match both docs; 8 ECL110 fields; entities 22, comfort 10, hot water 23; only token+weather required; no ECL110 field at setup [C174-C181] | true |
| 71 documented selector ranges across setup and options pages (target/min/max/day/night/hours, heated area, COP, powers, masses, losses, interval, weights, zones, buffer, windows, DHW, legionella, wind/rain, fRsi, inlet, greywater, shower, VVC, cycling, λ, wear, tariff, fuse, guard, fees, away, valve, wood, PV, staleness, external heat, ECL110) [C182-C246] | 71/71 match |
| ECL110 threshold half-floor ≥ 0.1 kW, 8-hour anticipation window, integer displace, comfort +4/boost max/off min; slab 0.7/0.3 merge; 48 repair rounds; 70 °C cap; irradiance precedence; sysid bounds; DHW presence trio; freeze on stale input [C250-C261] | source scan true |
| the COP-sample gate is 0.3 × nameplate floored at 0.2 kW — how-it-works says "a third"; treated as true (30 % ≈ a third) [C258] | 0.3 |
| card: one file, no CDN; served path; 900×380; label steps; hours ≤ 168; seven series keys; 232 strings in both languages, none missing; CARD_VERSION 5.4.17 logged; window-hours and plan_kind lookups; legacy storage key; what_if [C262-C272] | true |
| 45 modules; exactly the ten named import homeassistant at module level; inputs only inside a function; module map complete both ways [C280-C284] | 45, 10, 0/0 |
| rolling.py carries the documented constants and assertions (1.35, 4.25 kW, 3 days, >10 samples, +0.15, 0.05, 0.12/2 days, 1.25, 5–35 °C, 3 dh, 1.6×) [C290-C292, C294] | present |
| VERSION = manifest 6.2.14; HA 2024.1.0 in hacs.json and README; numpy+scipy in the manifest (plus threadpoolctl, unnamed); hacs name; platforms; LICENSE verbatim MIT; NOTICE names strutsfarm [C001-C004, C007, C014-C016] | true |
| 10 external links answer (GitHub ×4, hacs.xyz, home-assistant.io, developer.tibber.com, shields.io, api.open-meteo.com); 5 doc files exist [C005-C013, C017-C021, C023] | HTTP < 400 |
| 36 proposals and tranches T0–T8 in plan-v4.0.0-program.md; first refresh skips the solve [C304, C307] | true |

Observations that are not claims (nothing in the docs is wrong, something is
merely unsaid): Solar Irradiance keeps its `forecast` attribute out of the
recorder like the plan sensors but the README row does not say so (C044);
`threadpoolctl` is a third manifest requirement the README's "numpy and
scipy" does not name (C003).

## Unverifiable (10)

- C022 `docs/backlog.md` is linked four times (README:610,617,628;
  how-it-works.md:1279) and is absent from the export **by design** — the
  judge should confirm it exists at the baseline; C301 (backlog items 1–33)
  lives in it.
- C295–C300: historical measurements in how-it-works.md (2.6–4.7 kWh
  displaced; 2.2 % / 0.2 % from starts; 28.55 vs 23.28 SEK; ~5 % smoothness
  term; 4–6 % shoulder; 1–2 SEK/day valve; the comfort-weight table). Each is
  presented as a past measurement, several on the author's house; re-measuring
  them needs a quiet-box harness per claim and was outside the two-hour
  budget. Any re-take is a performance number and provisional under the
  fan-out.
- C302 (v5.0.0 shipped card 4.3.0) and C308 (fork at upstream 2.2.0): no
  history in the export.

## Harnesses

- `tools/audit/round2/D6/claims.py` — the table; prints it and the RESULT counts.
- `tools/audit/round2/D6/rolling_learning.py` — the learning arm (D6-04).
- Committed outputs: `claims_table.md`, `rolling_learning.out`,
  `rolling_learning_rerun.out` (determinism), `rolling_learning_null.out`
  (plant_error 1.0 null control).

Both set `sys.dont_write_bytecode`; no `__pycache__` was left in the export.
Neither touches `/tmp`, `HPO_PLANDATA` or the gate lock.

## What was not finished

- The six historical performance figures (C295–C300) were not re-measured.
- `docs/plan-*.md` were not claim-mined beyond the one README sentence about
  them; they are program plans, not user documentation.
- The Swedish translation was checked for key parity only, not for meaning.

## Exposure

Required reading: `tools/audit/briefs/COMMON.md`, `briefs/D6.md`,
`tools/audit/README.md`, `round2/BASELINE.md`. Audit-era material I had to
open because the README cites it: `docs/plan-v4.0.0-program.md` (section
headers and lines 1–53 via grep, to check "36 proposals, T0–T8"), the first
30 lines of `docs/plan-open-issues.md` (a program plan mentioning issues
#86–#101 and CodeQL alerts; no findings read) and of
`docs/plan-card-decomposition.md` (card size figures only). In code, comments
citing earlier ids were seen in passing (`optimizer.py:_multi_start_minimize`
"widened by D9-01"; issue numbers throughout `const.py`); none was used as a
lead. `docs/backlog.md`, the audit records and `RELEASE_NOTES.md` were not
present and were not sought elsewhere.
