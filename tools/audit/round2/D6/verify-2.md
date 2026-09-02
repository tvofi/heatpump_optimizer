# D6 — verifier seat 2 of 3

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Box: 8-core Apple M1, 8 GB, Python 3.13 (`tvofi-claude/.venv`), `tests/hastub`
stub, fan-out still running (load1 1.6–2.5). Every number below is a count, a
constant comparison or a recorded degree-hour sum; none is a timing. Angle:
the claims table itself. Scratch: `/tmp/verify-D6-2/`. Nothing in the export
was modified except this file; no `__pycache__` was left behind.

Constraint honoured: `rolling_learning.py` and the solver were **not** run
(box held for timing re-takes). D6-04 is judged from the three committed
`.out` captures and a source-level fidelity check against `tests/rolling.py`.

## 1. Re-run of the finder's harness

```
PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D6/claims.py > /tmp/verify-D6-2/claims_rerun.md
RESULT claims_extracted=273 count
RESULT claims_checked=263 count
RESULT claims_true=258 count
RESULT claims_false=1 count
RESULT claims_stale=4 count
RESULT claims_unverifiable=10 count
RESULT thread_factor=1.000   RESULT load1=2.46   RESULT swapins=0
```

`diff` of the table body against the committed `claims_table.md` (RESULT lines
excluded): **empty**. All counts equal the finder's (exact tolerance). One
stderr line (`Comfort miss … bias reset to 0`) is the CurveLearner check C172
logging, harmless.

## 2. Sampled-row audit — 40 of the 258 "true" rows

Sample: `random.Random(20260902).sample(true_ids, 40)` (seed = date + seat),
script `/tmp/verify-D6-2/sample.py`. Each row re-checked by hand: the cited
document line(s) were read (`/tmp/verify-D6-2/doclines.py` dumps them) and the
production value was read from source or re-derived independently of
`claims.py`.

| row | doc says (cited line) | tree says | verdict holds |
|---|---|---|---|
| C005 | manifest `documentation` URL | `curl -I` → 200 | yes |
| C009 | README:23 strutsfarm/ecl110 link | `curl -I` → 200 | yes |
| C011 | README:10 home-assistant.io | `curl -I` → 200 | yes |
| C017 | README:623 links docs/how-it-works.md | file exists | yes |
| C024 | README:134,258 names are translated | `en.json` == `strings.json` bytes (harness eq; unambiguous) | yes |
| C033 | README:338 "Buttons (4 total)" | 4 `_OptimizerButtonBase` subclasses, button.py:73-135 | yes |
| C050 | README:582-586 lists 7 DHW attrs | sensor.py:963-975 publishes all 7 | yes |
| C057 | README:333 evidence + frozen learners | binary_sensor.py:105-109 `stale_inputs`, `learners_frozen`, `learner_freeze_reason` | yes |
| C087 | README:395-405 Returns: 3×"—", simulate "Always", 7×"Optional" | `__init__.py`: simulate_plan `SupportsResponse.ONLY`, 7 `OPTIONAL`, 3 none | yes |
| C097 | README:400 "up to 20 hours" | `MANUAL_PLAN_WINDOW_HOURS = 20` | yes |
| C100 | README:398 "Rate-limited" (no figure) | `SIMULATE_MIN_INTERVAL_SECONDS = 3.0` | yes — the "3 s" in the claim text is from const.py, not the doc; doc claim is weaker and true |
| C113 | README:194, configuration.md:84-85: 07–22 | `DEFAULT_DAY_START_HOUR=7`, `_END=22` | yes |
| C115 | README:222, how-it-works:575 | `True / 60.0 / 7.0` | yes |
| C131 | configuration.md:150-152, how-it-works:310-313 | `10.0 / 0.7 / 0.7 / 0.4` | yes |
| C133 | configuration.md:284-287 (off, 45, 3, 1 hour) | `False / 45.0 / 3 / 60` | yes |
| C134 | configuration.md:292-296 | `0 / 3 / False / False / 0.5` | yes |
| C137 | configuration.md:445, how-it-works:771-773 | `90.0 / 2.0 / 45.0 / False` | yes |
| C138 | configuration.md:232-234,270; how-it-works:1137,1143 | `0.8 / 0.8 / 0.75 / False` | yes |
| C151 | how-it-works:686-687 | price_model.py:52-56 `5 / 0.2 / 3.0` | yes |
| C154 | how-it-works:886-888 | away.py:33,36 `1.0 / 24.0` | yes |
| C156 | how-it-works:108-110 two starting points | optimizer.py:121 `_MULTI_START_SOLVES = 2` | yes |
| C160 | README:99 "optional hot-water inlet coil" | `DEFAULT_DHW_WOOD_COIL_ENABLED=False`, `…EFFECTIVENESS=0.5` | yes — "0.5" is not a doc claim, the doc only says optional; true either way |
| C161 | how-it-works:909-910 60/60/180/30 | const.py:152-157 | yes |
| C173 | README:86, how-it-works:1154 "last eight" | `RING_SIZE = 8`; 12 takes → 8 kept | yes |
| C183 | configuration.md:104 20–1000/5 | config_flow `_number(20, 1000, 5)` ×2 pages | yes |
| C186 | configuration.md:114 0–10/0.5 | `_number(0, 10, 0.5)` ×3 pages | yes |
| C196 | configuration.md:146 0.0–3.0 | `_number(0.0, 3.0, 0.1)` ×2 | yes |
| C203 | configuration.md:167 50–1500/10 | `_number(50, 1500, 10)` ×2 | yes |
| C205 | configuration.md:169 35–55 | `_number(35, 55, 1)` ×2 | yes |
| C210 | configuration.md:177 1–30 | `_number(1, 30, 1)` ×2 | yes |
| C233 | configuration.md:318 10–55 | `_number(10, 55, 1)` | yes |
| C238 | configuration.md:423 0.3–1.0/0.01 | `_number(0.3, 1.0, 0.01)` | yes |
| C242 | configuration.md:441 15–360/15 | `_number(15, 360, 15)` | yes |
| C246 | configuration.md:469 0.25–6.0/0.25 (ecl110.md:90 is a blank line; table starts :91) | `_number(0.25, 6.0, 0.25)` | yes — cite off by one, verdict unaffected |
| C261 | README:126-127, how-it-works:906-907 over-age → missing, learners freeze | `coordinator._learning_frozen` (5294-5358) returns `f"{problem}:{key}"` for any configured reading with `not reading.ok` (stale included via `inputs.InputHealth.stale_keys`); every learner returns early on it (e.g. 3111-3113, 4146) | yes — the harness check is only a word scan, but the mechanism is real |
| C264 | dashboard-card.md:153 900x380 | card.js:973-974 | yes |
| C266 | dashboard-card.md:461,510 | card.js:8037 `hours <= 0 \|\| hours > 168` | yes |
| C280 | architecture.md:8 "45 modules" | `ls *.py \| wc -l` = 45 | yes |
| C283 | architecture.md:66-135 module map | my own `diff` of tree names vs `ls`: SETS EQUAL | yes |
| C306 | cited README:281 does **not** carry this claim; it lives at README:457-460 (three sources in priority order, Open-Meteo opt-in, weather default) | `DEFAULT_SOLAR_FORECAST_SOURCE="weather"`, `SOLAR_SOURCES=("weather","open_meteo")` | yes — wrong cite, right verdict |

**Result: 40/40 verdicts hold; 0 false things marked true.** Three rows carry
a cite or claim-text drift that does not move the verdict (C100, C160, C306;
plus C246's off-by-one). Nothing in the sample is a tautology: every row reads
a production value, though C261 reads it as a regex.

## 3. The 4 stale, 1 false and 10 unverifiable rows

- **Stale (4)** = exactly the four finding rows C040, C093, C293, C305; each is
  handled under its finding below. **C305 is not a measurement**: it is
  `lambda: ok(False, …)` (claims.py:1179), the only hard-coded verdict in the
  table (`grep -nE 'ok\((True|False),'` finds nothing else). The perturbation
  the report gives for D6-05 ("C305 flips to true") cannot happen as the
  harness stands. Replaced by an executable check in my harness (§4, D6-05).
- **False (1)** = C092; reproduced independently (§4, D6-03).
- **Unverifiable (10)**: C022 (`docs/backlog.md` — absent from the export by
  design; README:610,617,628 and how-it-works:1279 link it, so the judge should
  confirm it exists at the baseline SHA), C295–C300 (historical performance
  figures — would need quiet-box harnesses; correctly not attempted during the
  fan-out), C301 (needs backlog.md), C302 and C308 (need git history the
  export lacks). All ten are legitimately unverifiable here; none is a
  checkable falsehood being hidden behind the label.

## 4. The five findings

My harness: `/tmp/verify-D6-2/mine.py`, output `/tmp/verify-D6-2/mine.out`
(`thread_factor=1.000`, `load1=1.59`, `swapins=0`); D6-01 perturbation in
`/tmp/verify-D6-2/perturb_d601.py` on a scratch copy of README.

### D6-01 · README sensor table vs strings.json names — **verify, low**

- **My metric.** Count of README `### Sensors` rows whose first cell is not a
  member of `{strings.json entity.sensor.*.name}` (independent table parse,
  set membership, no prefix logic in the count).
- **My number.** 55 rows; **9** not in strings.json; each resolves to exactly
  one qualified name by `name + " ("`; strings.json has exactly 9 names
  ending in `(lifetime)` / `(next 24 h)` — the same 9. Perturbation (rewrite
  the nine rows on a scratch copy): 9 → **0**.
- **Attacks.** (a) Is README:258-259 a claim of identity? Yes: "the tables
  below show the English names". (b) Deliberate abbreviation style? No — the
  other 46 rows are byte-equal, including rows that carry parentheticals
  ("Buffer Tank Temperature (Model)"), so the omission is not a house style.
  (c) Consequence: a user searching the registry for "Total Energy" finds
  "Total Energy (lifetime)"; nothing misbehaves. Severity low is earned and is
  the schema's floor.
- **Vote:** verify (low). Deciding number: 9/55.

### D6-02 · services.yaml wind example 0.15 — **verify, low (as "stale", not "false")**

- **My metric.** Over the 25 `set_thermal_parameters` fields that have both an
  `example` and a `DEFAULT_*` constant: count with example == default, and
  |example − default| for wind.
- **My number.** **24/25** examples equal the shipped default; the single
  exception is `wind_sensitivity_factor` (example 0.15, default 0.03,
  |Δ| = 0.12), and 0.15 is exactly the value const.py:1036 names as "the
  previous default". The rain sibling's example (1.15) equals its default.
- **Is 0.15 contradicted by const.py?** Not as a *statement*: the yaml
  description ("0.15 means 15% more heat loss per m/s") is a correct reading
  of the model's `(1 + sensitivity × wind)` and never calls 0.15 a default
  (`'default' in description` = False). What const.py:1031-1040 contradicts is
  the *choice* of example — it calls 0.15 "physically implausible" and says it
  "made every windy forecast panic-charge the house". So this is a stale
  example (the finder's own verdict), not a false sentence. The report's
  "pre-fills" is slightly strong: HA shows `example` through "Fill example
  data" in YAML mode rather than pre-filling the UI number box; the value is
  still what the project hands the user as its worked example.
- **Attacks.** Path reachable in real HA (services.yaml is what Developer
  Tools renders); constant comparison, contention-immune; perturbation
  (example → 0.03) trivially zeroes |Δ|.
- **Vote:** verify (low, class hygiene, verdict "stale"). Severity is already
  at the schema floor, so there is nothing to weaken to; the register should
  carry it as a stale example, not a false claim. Deciding number: 1/25
  examples off-default, and that one equals the retired default.

### D6-03 · two selector minima rejected by the registered schema — **verify, low**

- **My metric.** Feed each `services.yaml` number-selector `min`/`max`
  through the schema actually registered by
  `heatpump_optimizer.async_setup_entry` (read back from
  `FakeServices._schemas`); count rejections.
- **My number.** 39 number selectors; **2** bounds rejected:
  `inter_zone_heat_transfer` min 0.0 and `window_area` min 0, both with
  `value must be at least 0.01` (`_positive` = `vol.Range(min=0.01, …)`,
  `__init__.py:254-255`). Fed as int `0` as well: rejected. Perturbation
  (0.01): accepted for both → count 0.
- **Attacks.** (a) Reachable in real HA: selectors are UI metadata only; HA
  validates the call against the registered voluptuous schema, so picking 0
  in Developer Tools produces exactly this error. (b) Which side is wrong?
  The config flow's own selectors for the same two keys accept 0
  (`_number(0, 50, 0.5)` window_area, `_number(0.0, 3.0, 0.1)` inter-zone,
  config_flow.py:1238,1253,2436), so a value the options page stores cannot be
  set through the service — the schema may be the odd one out rather than the
  yaml; either fix zeroes the count and the finding's perturbation names both.
  (c) Consequence: a validation error with a one-keystroke workaround → low.
- **Vote:** verify (low). Deciding number: 2/39 (both minima), 0 after
  perturbation.

### D6-04 · the "6.7 → 0 degree-hours" reference run — **verify, low (from the recorded captures)**

- **Not re-run** (box held). Judged from `rolling_learning.out`,
  `rolling_learning_rerun.out`, `rolling_learning_null.out` and a source-level
  fidelity check of the harness against `tests/rolling.py`.
- **Fidelity of the harness to the test.** The harness execs rolling.py
  lines 1–266 (everything before the first `R.section(` at :267) and calls
  `run_rolling(days=3, dhw=False, plant_error=1.35, learn=True, config={"heat_pump_max_power": 4.25})`,
  the learner-off twin, and `run_rolling(days=2, dhw=False, plant_error=1.0, learn=True)`
  — argument-for-argument the calls at rolling.py:457-462 and :503. The
  breach metric (`floor_for(learned["config"], steps)`, Σ max(0, bound − room)
  × DT, DT = 0.25 from `profiles.py:5`) is the test's own at :488-493. Could
  skipping the three earlier sections change the numbers? Only through shared
  mutable state: `grep` finds **no** `np.random` / `random.` / `default_rng` /
  `seed(` anywhere in the package, `tests/profiles.py` or `tests/harness.py`;
  `dt_util.freeze` is set and cleared inside `run_rolling`; the coordinator is
  built fresh per call. So the harness reproduces the test's arm.
- **Recorded numbers.** `breach_uncorrected=9.634`, `breach_learned=0.044`
  degree-hours; `scale 1.000 → 1.3312` (truth 1.35), 287 samples,
  `correct_model_drift=0.0167`; the two captures are bit-identical. Null
  control (`D6_PLANT_ERROR=1.0`): `0.000 → 0.000`, `scale_end 0.9829` — the
  breach is entirely the mis-model's, and the learner leaves a correct model
  alone. `thread_factor=1.000` on all three; not a timing number.
- **The docs.** README:486-487 and how-it-works.md:1237-1238 quote "from 6.7
  degree-hours to zero" as "the reference run recorded in the test". The test
  carries 6.7 / 0.0 only as a comment ("measured", rolling.py:452-453) and
  asserts `breach_learned < breach_plain` (:494-497). 9.63 vs 6.7 is a 44 %
  gap — not a last-decimal BLAS difference — and 0.044 is not "zero" either,
  though negligible. how-it-works.md:1247-1250 itself warns against quoting
  unasserted figures and then quotes one.
- **Attacks.** Contention: deterministic degree-hour sum, not provisional.
  Grid artefact: n/a. Null control: present and clean. Severity: the
  asserted property holds (99.5 % of the breach removed), only the quoted
  figures are wrong → low/hygiene is earned.
- **Residual.** If the judge's quiet-box or fixture-machine re-take lands at
  6.7 → 0.0 the finding narrows to "machine-specific figure quoted as fact";
  it would still be a documentation defect, weaker. The 44 % gap makes that
  unlikely; the comment more plausibly predates later model changes.
- **Vote:** verify (low). Deciding number: 9.634 → 0.044 vs the quoted
  6.7 → 0 (two identical captures).

### D6-05 · DISCLAIMER "always-on thermostat" — **weaken (low): simplification, not contradiction**

- **My metric (executable, replacing the hard-coded C305).** Over the two
  user documents that describe the savings baseline (README:271,
  DISCLAIMER:71-72): count that (i) say "always-on" of the space baseline,
  (ii) state a flat/around-the-clock setpoint, (iii) mention the comfort
  schedule; plus whether the operative claim "simulated, not measured" is
  present.
- **My number.** (i) **1** (DISCLAIMER); (ii) **0** — neither document says
  the space reference holds a flat target; (iii) README 1, DISCLAIMER 0;
  DISCLAIMER's "rather than a measurement" = present. Docstring
  (optimizer.py:5177-5189) confirmed: "following the comfort schedule … the
  thermostat tracks the same per-step comfort targets"; DHW baseline
  (optimizer.py:4786) "an always-hot tank held at the setpoint".
- **Contradiction or simplification?** The sentence's job is to say the
  baseline is simulated, not measured, and that is correct. "Always-on
  thermostat" does not say "flat setpoint"; a thermostat following a
  day/night schedule is still "always on" in plain English. The contradiction
  appears only in the project's own vocabulary, where "always-on"/"always-hot"
  is reserved for "held at setpoint around the clock" (README:271 "Only the
  hot-water half of the baseline is always-on"; how-it-works.md:529
  "always-hot baseline" for DHW), and README:271 explicitly contrasts it with
  the schedule-following space half. Read that way the DISCLAIMER describes
  the retired flat-target reference; read plainly it is a simplification. The
  docstring names the thing that would be wrong — "holding the flat
  target_temp around the clock" — and the DISCLAIMER does not say that.
- **Harness defect.** C305 is `ok(False, …)`: the "stale" verdict is asserted,
  not measured, and the report's perturbation ("C305 flips to true") is not
  executable. My check above is the executable form; the fix (one clause in
  DISCLAIMER) is unchanged.
- **Vote:** weaken (low — the schema floor, so the severity does not move;
  the claim should be narrowed from "contradicts the optimizer's baseline" to
  "ambiguous wording that, in the README's own vocabulary, reads as the
  retired flat-setpoint baseline; the operative claim — simulated, not
  measured — is correct"). Class stays hygiene. Deciding number: 1/2
  documents use "always-on" for the space baseline; 0/2 state a flat setpoint.

## 5. Summary

| finding | my number | vote |
|---|---|---|
| D6-01 | 9/55 README names ∉ strings.json; perturbation → 0 | verify (low) |
| D6-02 | 24/25 examples = default; wind 0.15 vs 0.03 (Δ 0.12), = retired default | verify (low, stale example, not a false sentence) |
| D6-03 | 2/39 selector bounds rejected by the registered schema (0 and 0.0 → "at least 0.01"); 0.01 accepted; config flow accepts 0 for both keys | verify (low) |
| D6-04 | recorded 9.634 → 0.044 dh (two identical captures), null 0 → 0; harness faithful to rolling.py:457-503; not re-run | verify (low), conditional on the judge's re-take not landing at 6.7/0.0 |
| D6-05 | 1/2 docs say "always-on" of the space baseline, 0/2 say flat setpoint; C305 hard-coded | weaken (low): simplification contradicted only by the project's own vocabulary |

Claims-table audit: harness re-run reproduces the committed table exactly;
40/40 sampled "true" rows hold with 0 false-marked-true; the 4 stale rows are
the finding rows (one, C305, hard-coded); the 1 false row reproduces; the 10
unverifiable rows are legitimately so.
