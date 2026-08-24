# Backlog

Started at the end of the v2.7.0 release session, kept up to date since.

**Status as of v3.11.0.** Items 1-31 are done, released across v2.8.0
through v3.11.0 (29 lacks only `smart_write`). See the notes appended to each item for what was
actually built and what was found along the way. v3.8.0 is the audit release
(`docs/audit-2026-08.md` records everything it fixed); v3.10.0 is the release
where the buffer tank finally charges — the discharge law, the hard
temperature cap, the size threshold and the recommendation sensor, with the
empirical sizing measured in `tests/backtest.py`.

### What is actually left, shortest first

- ~~**Delete `get_state_matrices`** (item 27).~~ Done in v3.8.0.
- ~~**Surface the dumb-valve recommendation** (item 29).~~ Done in v3.10.0 —
  the Valve Target Recommendation diagnostic sensor.
- ~~**A tank size threshold** (item 27).~~ Done in v3.10.0 —
  `BUFFER_STORE_MIN_VOLUME`, 100 L.
- ~~**`buffer_max_temp` as a hard constraint in the solve** (item 29).~~ Done
  in v3.10.0 — a tighten-and-re-solve loop mirroring the pin-safety pattern.
- ~~**Find out why the optimizer will not charge** (item 29).~~ Answered in
  v3.8.0, and the prescribed discharge-law fix is **implemented in v3.10.0**:
  the optimizer now deliberately charges. See the v3.10.0 block in item 29's
  status for what it is measured to be worth and the honest limit a fixed
  valve imposes.
- **`smart_write` valve mode** (item 29). Needs an actuation path. Now also
  the key to the remaining storage value: a commandable valve could *hold*
  charge for the peak instead of feeding it out right after charging.
- ~~**Item 28**, the wood furnace, in full.~~ Done in v3.11.0 — the
  per-step free-heat harness, the measured payoff, the outlet-sensor
  displacement and the tank-pair decay cut-off. See its status block.
- **Items 32 and 33**, the setup diagram and the card page.

**Item 29 is done except `smart_write`** — see its status blocks. **Item 27 is
done** through the same work. **Item 28 is done as of v3.11.0** — see its
status block. **Items 32 and 33** were added 2026-08-23 and are planned but
not built.

Scope decision (user, 2026-08-23): 26, 24+25, 30 and 31 were done first, one PR
each, and all shipped. The wood-furnace cluster (27-29) was deferred, re-planned
once item 27's modelling fork was settled, and then partly built -- see the
status blocks on 27 and 29.

Items 27-31 are one cluster, added 2026-08-23, about a house with a wood
furnace, a second buffer tank and a mixing valve. **Item 27 was a modelling bug
blocking 28 and 29**, and its physics half is now fixed. Read them in order: 27
is why the tank could not store anything, 29 is why a mixing valve means it can,
and 28 is the sensors that would tell it what the furnace is doing. They were
correctly judged a release of their own rather than an afternoon -- 27 and 29
together took five releases (v3.6.1 through v3.7.1) and are still not finished.

**Items 30 and 31 are a chain and should be done first.** Item 30 is a second
modelling bug in the two-zone lower floor; item 31 adds learning for the
coupling coefficients, which are confirmed *not* learned today. 31 depends
strictly on 30 — the coefficient it most wants to fit is currently
unidentifiable, so building 31 first would produce confidently wrong numbers.

Item 22 was **inverted on 2026-08-23**: it used to say "remove the comfort
slider", it now says keep it and pair it with a hot water minimum. If you are
working from memory of this file, re-read it.

Item 4, the refactor, was excluded from the first pass but *was* completed
later, in v3.0.0 — see the "Refactored" section of `RELEASE_NOTES.md` for the
before/after measurements. Its stated precondition was honoured rather than
waved away: `tests/golden.py` (37 scenarios, byte-for-byte, sensitivity
demonstrated) was built first, and every refactoring change was made with its
diffs empty. `tests/stress.py` and `tests/rolling.py` came with it. So the
"safety net is too thin" caveat recorded in item 4 no longer applies — the net
is the thing that got built.

Item 21's what-if simulator shipped, but v3.2.0's slot editor has largely
superseded its original framing; item 22 covers what to do about the remnant.

The items below are kept as written, including the ones now shipped, because
they record the reasoning and the caveats that shaped the implementations.

## 1. The popup legend renders poorly (resolution and font size)

**Symptom:** in the enlarged `<dialog>` view the legend chips look low
resolution and the font is too small relative to the much larger chart.

**Likely cause, to confirm before changing anything.** The legend is plain HTML,
not SVG, so it cannot be "low resolution" by itself. Two candidates:

- The chips use `font-size: 0.82em`, which is relative to the inherited card
  font size. The dialog does not scale that up, so at a much larger chart size
  the legend stays at card size and reads as too small. This is the likely one.
- The chart *text* inside the SVG is a different matter: the SVG uses
  `preserveAspectRatio="none"` with fixed `font-size="10"` in viewBox units, so
  when the viewBox is scaled up the glyphs are scaled bitmaps of vector text at
  a small nominal size. They stay sharp (SVG text is re-rasterized), but the
  *relative* size shrinks as the chart grows, which reads as blurry or cramped.

**Fix direction.** In `dialog.expanded`, scale the legend up (its own
`font-size`, chip padding, and dot size), and consider reducing the SVG's
in-viewBox `font-size` values proportionally, or setting an explicit larger
base font on the dialog so `em` units cascade correctly. Verify in a real
browser, not just `tests/card.mjs` — the stub does not lay anything out. The
previous session used a throwaway static page plus the browser canvas and
`evaluate_javascript` to measure `getBoundingClientRect`, which caught a real
overflow bug the stub could not.

Files: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
(`_styleBlock`, `_legendHtml`, `_valueAxis`, `_timeAxis`).

## 2. Add a solar irradiance toggle to the card

The card already has six togglable series in `SERIES_DEFS`. Add solar
irradiance as a seventh.

**Data source already exists.** v2.7.0 added the Open-Meteo client, and the
coordinator publishes:

- `solar_forecast` - list of `{t: <ISO interval start>, ghi: <W/m2>}`, built by
  `_solar_forecast_view()` in `coordinator.py`.
- `solar_source`, `solar_diagnostics`.

There is also a `SolarIrradianceSensor` in `sensor.py` whose `forecast`
attribute carries the horizon. Decide which the card should read: the plan
sensors are discovered via the `plan_kind` attribute, so the solar sensor needs
an equivalent stable marker rather than a hardcoded entity id. Do not hardcode
`sensor.heat_pump_optimizer_solar_irradiance` - `has_entity_name` means ids are
derived from the device name and are not a contract. That exact mistake caused
the v2.6.1 bug where the card never found its sensors.

**Axis.** W/m2 is a third unit. The chart currently groups axes into `temp`,
`power` and `price`. Either add a fourth axis or scale irradiance into the
existing power axis (kW/m2). A fourth axis needs somewhere to put it - both the
left and right edges are already occupied.

**Note the interval convention.** `_solar_forecast_view` already converts
Open-Meteo's end-of-interval timestamps to interval starts for charting, so the
card should not shift them again.

## 3. Add an entity to force an optimization run

**Most of this already exists.** `heatpump_optimizer.run_optimization` is a
registered service (`services.yaml`, handler `handle_run_optimization` in
`__init__.py` around line 144) which calls `coord.async_run_optimization()` on
every loaded coordinator. What is missing is an entity so it can be triggered by
tapping a dashboard card rather than by calling a service.

**Prefer a `button` entity over a switch.** Forcing a run is a momentary action
with no lasting state, which is exactly what HA's `ButtonEntity` is for. A
toggle would have to bounce itself back off, and until it did, the UI would
imply a state that does not exist. If a switch is wanted anyway, note that its
state is meaningless between presses.

Worth considering instead of, or alongside, the button: expose "optimization in
progress" as the button's availability or as a separate binary sensor, so a user
who taps it gets feedback that something happened. A run is not instantaneous
(it fetches prices and weather, then solves), so a control that appears to do
nothing for several seconds invites repeated presses.

**Work involved.**

- New `button.py` platform with a `ForceOptimizationButton` on the existing
  device, calling `coordinator.async_run_optimization()` in `async_press`.
- Add `"button"` to `PLATFORMS` in `const.py` (currently
  `["sensor", "climate", "switch"]`).
- Follow the existing entity conventions: `CoordinatorEntity` subclass,
  `_attr_has_entity_name = True`, and `coordinator.device_info`, as
  `OptimizerEnableSwitch` in `switch.py` does.
- Guard against overlapping runs. `async_run_optimization` is presumably not
  reentrant; check before wiring a control that a user can press repeatedly and
  faster than a run completes.
- Add `strings.json` and both `translations/*.json` entries, and keep
  `strings.json` in sync - it had already drifted twice by v2.7.0.
- Document it in `README.md` under the entity list.

## 4. Refactor for compactness, modularity and efficiency

> **DONE in v3.0.0.** Everything below is kept for the reasoning, but the
> measurements are historical. The characterization harness this item demanded
> as a precondition was built first (`tests/golden.py`, `tests/stress.py`,
> `tests/rolling.py`) and the refactor was carried out against it with empty
> diffs. See the "Refactored" section of `RELEASE_NOTES.md` for before/after
> line counts. Do not re-plan this work from the numbers below.


Requested as a general cleanup: more compact, modular and efficient code with
**all functionality retained**. That last clause is the hard part, so read the
precondition below before touching anything.

### Precondition: the safety net is too thin for this

The integration is ~11,400 lines. The tests are ~1,300 lines of end-to-end
scripts that assert on outcomes (savings percentages, comfort bounds, "optimal"
status), not unit tests over internals. They would catch a refactor that makes
the optimizer obviously worse. They would **not** catch one that quietly shifts
a plan by one interval, drops a constraint in a rare branch, or changes a
learned parameter's convergence.

Refactoring a 467-line LP builder against that is how functionality gets lost
silently. So the first task is not refactoring:

1. Add a **characterization harness** first: pin current behaviour by recording
   the full output of the existing scenarios (schedules, per-step setpoints,
   costs, learned parameters) as golden fixtures, and diff against them.
2. Only then refactor, one module at a time, with the golden diffs staying
   empty. A refactor that changes output is either a bug or a deliberate,
   separately justified change.

Without step 1, "retaining all functionality" is a hope rather than a claim.

### Where the actual weight is

    optimizer.py     2487    coordinator.py   2298    config_flow.py   1428
    thermal_model.py 1286    card.js          1198    sensor.py         946

Longest functions:

| Function | Lines | Note |
|---|---|---|
| `optimizer._optimize_with_dhw` | 467 | see duplication below |
| `optimizer._optimize_space_only` | 321 | |
| `thermal_model.ThermalParameters.from_config` | 195 | flat config plumbing |
| `optimizer._plan_dhw_min_cost` | 185 | |
| `optimizer._build_dhw_requirements` | 174 | |
| `coordinator._build_data_dict` | 167 | one dict literal |
| `coordinator.__init__` | 149 | ~40 attributes |
| `coordinator._prepare_forecast_data` | 134 | |
| `config_flow.async_step_*` | 115-136 each | repetitive schema building |

### Highest-value target, measured

`_optimize_with_dhw` and `_optimize_space_only` are **58% similar**, with 149
lines sitting in contiguous identical runs of 4+ lines (measured with
`difflib.SequenceMatcher` over comment-stripped, whitespace-normalised lines).
The shared parts are the bounds and comfort-band setup, the anticipatory
weighting, and the solver invocation and result unpacking.

That is a genuine extraction: a common LP-assembly core with the DHW block as
an optional set of columns and constraints. It is also the single riskiest
change in the codebase, so it should come last, after the golden harness exists
and after the easier wins have shaken out any harness gaps.

Easier, lower-risk wins to do first:

- `from_config` (195 lines): table-driven parameter mapping instead of a long
  sequence of near-identical `config.get(...)` assignments.
- `_build_data_dict` (167 lines): compose from small per-domain builders
  (space, DHW, solar, learning diagnostics).
- `coordinator.__init__` (149 lines): group the ~40 attributes into small
  dataclasses by concern; this also makes the test fixtures in
  `tests/solar_alignment.py` less brittle, since they currently have to know
  exactly which attributes a method touches.
- `config_flow`: the `async_step_*` methods differ mainly in their schema
  contents; a declarative step/field table would collapse most of the 1,428
  lines.

### On "efficient"

Do not assume the LP is the bottleneck without measuring: `tests/validate.py`
already prints per-scenario solve times (the 2-zone winter case was ~8 s). If
speed matters, profile first and confirm whether time goes to problem assembly
(NumPy work, worth optimizing) or to the solver itself (where restructuring
Python buys nothing). Compactness and speed are separate goals and can conflict
- vectorising a loop usually makes it denser but less readable.

### Scope note

Consider doing this as a series of small PRs, one module per PR, rather than
one large one. A single sweeping "refactor everything" diff is close to
unreviewable, and if a regression does slip through, a bisect over small PRs
finds it; a bisect over one giant commit does not.

## 5. Detect an external heat source (wood furnace) and adapt the strategy

Detect when something other than the heat pump is heating the DHW tank and the
water loop - typically a wood furnace tied into the same buffer - and change
the plan while it is running. Burning electricity to heat water that is already
being heated for free is the single most expensive mistake the optimizer can
make, and right now nothing stops it.

### The learners already half-know about this

`coordinator.py` line ~244 documents `HOUSE_LOSS_MAX_RESIDUAL` as rejecting
"a door left open, **a wood stove**, or a sensor glitch". So the house-loss
learner already discards these intervals as outliers, and the tank learners
mostly reject them too: they are lower-envelope estimators, and an externally
heated tank produces a negative cooling rate that falls outside
`*_COOLING_RATE_MIN` and is skipped.

Two consequences:

- **Learner corruption is not the main risk**; the guards mostly hold. Do not
  justify this feature on that basis without checking. The one place to verify
  is the buffer learner: an interval that is only *partly* externally heated can
  look like genuinely slower cooling, and `BUFFER_COOLING_ALPHA_UP = 0.02` will
  absorb it slowly rather than reject it.
- **Detection turns discarded data into labelled data.** Today those intervals
  are silently thrown away. Once the state is explicit, the learners can freeze
  deliberately, and the diagnostics can say why samples were skipped.

### Detection

No new hardware should be required; infer it from what is already sensed:

- Buffer tank or DHW temperature **rising while the heat pump is commanded off**
  (or while its power draw is ~0 - note there is currently **no** measured power
  entity; see item 6, which this depends on for the strongest signal).
- Floor loop return temperature rising with no pump output.
- Rate of rise well beyond what the heat pump could produce, which catches the
  case where the pump is also running.

Needs hysteresis and a minimum dwell time, otherwise a defrost cycle, a
thermosiphon, or sensor noise will flap the state and thrash the plan. Also
needs a decay/timeout: a fire dies down gradually, so "external heat active"
should fade rather than switch off cleanly, and the optimizer should not
immediately re-plan a full charge the moment it clears.

Expose it as a binary sensor with the evidence in its attributes, so a user can
see why it triggered. Consider also allowing an explicit user-provided entity
(a flue thermostat, a stove switch) to override the inference, since anyone who
has that will trust it more than a heuristic.

### Strategy changes while active

- Suppress planned electric DHW slots; the tank is being charged for free.
- Treat the buffer as charged for space heating and defer compressor starts.
- Let the anti-legionella cycle be **satisfied** by the external source when the
  tank actually reaches the disinfection temperature, rather than scheduling a
  separate electric cycle afterwards. This is a real saving and easy to miss.
- Re-plan promptly on both edges. The plan is built against an assumed tank
  trajectory, and that assumption has just been invalidated.
- Freeze the DHW, buffer and house learners for the duration plus the decay
  window, and record the reason.

### Watch out for

- **False positives are asymmetric in cost.** Wrongly believing an external
  source is running means skipping a cheap-hours charge and paying peak prices
  later, or running out of hot water. Bias the detector towards missing a fire
  rather than inventing one.
- Solar gain into the loop, and a hot-water draw that pulls stratified heat
  upward past the sensor, can both look like an external source.
- Configuration should default this **off** for the many users with no such
  source, so the feature cannot cost anything it does not save.

## 6. Add a measured power draw sensor

**Check what exists before starting.** `sensor.py` already has a
`CurrentPowerSensor`, but it publishes **"Recommended Power"** - the value the
optimizer is commanding, in kW, taken from the current action. There is no
config option anywhere for a *measured* power entity: `const.py` has
`CONF_HEAT_PUMP_MAX_POWER` / `MIN_POWER` (nameplate limits) and no
`CONF_*_POWER_ENTITY`. So the gap is the input side, not the output side.

Add an optional config entity for actual electrical draw, alongside the other
optional sensors in the config flow and options flow.

### Why it is worth more than it looks

- **It unblocks item 5.** The external heat source detector's cleanest signal is
  "tank temperature rising while the heat pump is drawing ~0 W". Without a
  measured power entity that has to be inferred from what the optimizer
  *commanded*, which is exactly the assumption that breaks when something else
  is driving the system, or when the heat pump runs on its own internal logic.
- **Real COP instead of a modelled one.** The model currently derives COP from a
  nominal figure and an outdoor-temperature curve. With measured electrical
  input against modelled thermal output, COP becomes observable and can join the
  existing learners. That feeds directly into cost accuracy, since every plan is
  priced through COP.
- **Closes the loop on savings claims.** `PredictedSavingsSensor` and
  `PredictedCostSensor` are currently predictions with nothing to check them
  against. Measured draw allows predicted vs actual reporting, which is both a
  user-facing feature and the fastest way to notice the model drifting.
- **Makes defrost cycles and any auxiliary or immersion heater visible.** Both
  consume electricity the model does not account for and both otherwise show up
  as unexplained residuals in the house-loss learner.

### Notes

- Naming needs care: "Recommended Power" and a measured power sensor sitting on
  the same device will be confused constantly. Consider renaming the existing
  one to make the planned/actual distinction obvious, but treat that as a
  breaking change to entity ids and handle it as such - the v2.6.1 card bug came
  from exactly this area.
- Accept both W and kW and normalise, the way `_wind_speed_scale` handles the
  weather entity's units. Do not assume kW because the internal model uses it.
- Everything above must degrade cleanly when the entity is absent. It is
  optional, and most installs will not have one.
- If a measured *energy* (kWh) entity is available too, actual cost accounting
  becomes possible; worth considering as a second optional input rather than
  integrating power over time.

## 7. Model the unknown price horizon instead of repeating the last price

`coordinator.py` (~line 1920) pads the price series past the known horizon with
`prices[-1]`, i.e. a flat repeat of the last known value:

```python
while len(prices) < n_steps:
    prices.append(prices[-1] if prices else 0.5)
```

Nord Pool / Tibber publish tomorrow's prices around 13:00 local time. Before
that, a large fraction of a 24h+ horizon is a constant. A flat tail has no
trough, so the optimizer cannot see a cheap period ahead worth waiting for and
systematically under-defers load in the morning. It also interacts badly with
the terminal-cost term (optimizer.py ~599 and ~1568), which values stored heat
against a price that is itself fictitious.

Proposed approach:

- Learn a normalised diurnal price shape from stored history (mean profile by
  hour-of-day, ideally split weekday/weekend), then scale it to the recent
  price level to fill unknown steps.
- Attach a confidence marker to padded steps so the plan sensors and the card
  can show where the plan rests on a prior rather than on published prices.
- Optionally damp commitment in the padded region: prefer plans that keep
  options open when the tail is a guess.

Care needed: do not let the prior dominate. If tomorrow's prices are known,
the learned shape must not be used at all. Validate with a backtest (item 11).

## 8. Peak-power (capacity) tariff awareness

Nothing in the codebase models a capacity tariff. `grep -i peak` only finds
solar peak hours and DHW peak usage hours; there is no monthly peak-power term.

Swedish (and increasingly Nordic) DSOs bill a monthly effekttariff, commonly
the mean of the three highest hourly consumption peaks in the month. The
optimizer minimises energy cost only, so it will happily stack DHW and space
heating into the same cheap hour. A single new monthly peak can easily cost
more than the energy that stacking saved.

Proposed approach:

- Optional config: tariff SEK/kW, the peak definition (number of peaks
  averaged, hourly or 15-minute window) and a house baseline load entity, since
  the peak is whole-house, not just the heat pump.
- Track the current month's realised peaks in coordinator state so the cost of
  exceeding them is known during planning.
- Add a soft penalty for exceeding the running peak, rather than a hard cap
  which would fight the comfort constraints.

This is probably the highest-value item in this list for Swedish users, and it
is the one most likely to change plan shape visibly.

## 9. PV self-consumption

There is no PV support anywhere (`grep -i "pv\|photovolt\|surplus\|export"`
finds only an unrelated comment). For a house with solar, heating DHW or the
buffer from surplus production beats exporting it at spot-minus-fees.

The v2.7.0 Open-Meteo work already provides most of the forecasting machinery:
`open_meteo.py` fetches irradiance for a chosen coordinate and aligns it to the
optimizer step grid. What is missing is a production model and the economics.

Proposed approach:

- Optional config: a PV production entity (measured), installed kWp and an
  export compensation value (or entity).
- Forecast surplus as production minus baseline house load, using the existing
  irradiance forecast scaled to the array.
- Price each step at the marginal cost of consuming: export compensation while
  in surplus, import price otherwise. This falls out of the existing cost
  formulation without needing a new optimizer structure.

Depends on the measured power entity (item 6) to know baseline house load.

## 10. Compressor cycling cost

`optimizer.py` (~line 740) sets `bounds = [(0.0, p_max)] * n_steps` and reads
sub-minimum values as duty cycling within a step. There is no minimum runtime,
start cost, switching penalty or hysteresis anywhere in either optimizer path.
Nothing stops a plan from chattering between steps.

Each compressor start has real costs: oil dilution and wear, the loss while
the system re-establishes steady state, and on some units a defrost penalty.

Proposed approach:

- First, measure. Add a cycling metric to the validation harness and check
  whether realistic plans actually chatter. If they do not, this is not worth
  paying for.
- If they do, a smooth switching penalty (an L1 term on the step-to-step power
  difference) keeps the problem continuous and is much cheaper than a true
  minimum-runtime constraint, which would make the problem a MILP.
- A hard minimum-runtime constraint should be a last resort; check the solver
  time budget before going there.

## 11. Closed-loop accuracy reporting and backtesting

Nothing verifies the savings claims. `PredictedSavingsSensor` publishes a
prediction with no realised counterpart, and there is no mechanism to detect
model drift beyond the learners' own guard thresholds.

Proposed approach:

- With the measured power entity (item 6) plus stored history, record
  predicted vs realised power, temperature and cost per interval.
- Publish a rolling accuracy figure so drift is visible, and feed it back as a
  trust signal for the learners.
- Build a replay harness that takes historical prices and weather and scores
  alternative strategies (current optimizer, a naive always-on baseline, a
  simple night-tariff schedule). This turns the savings figure from a
  simulation result into an observed one.

The replay harness overlaps usefully with the golden harness in item 4: one
pins behaviour, the other scores it. Building the recording layer once serves
both.

## 12. Input staleness watchdog

`coordinator.py` guards every sensor read against `unavailable`/`unknown`
(lines ~1514-1595) but never checks `state.last_updated`. The only freshness
bound in the codebase is for the satellite solar sample (`const.py:51`).

A dead battery in a tank probe, or a dropped Zigbee room sensor, leaves a
perfectly valid-looking constant in the state machine indefinitely. Two things
then go wrong, and the second is worse:

1. The optimizer plans against a fiction.
2. The learners observe a flatline, attribute it to thermal behaviour, and
   corrupt learned parameters that are then persisted to `Store`. A dead
   sensor quietly poisons the model, and the damage survives a restart.

Proposed approach:

- Per-input max age (a room temperature may reasonably be minutes old; an
  outdoor forecast, hours). Treat over-age values as missing, not as data.
- Freeze the learners for any input that is stale, rather than feeding them a
  constant. Fail closed: a learner that stops learning is recoverable, one
  that learns from a flatline is not.
- Publish a diagnostic sensor naming which inputs are stale, so the failure is
  visible instead of silent.
- Degrade gracefully: fall back to the last good value with a widened
  uncertainty, or to a default, depending on the input.

Do this before the other items. It protects everything downstream, and it is
cheap.

## 13. Away / holiday mode

Nothing presence-related exists anywhere in the codebase (`grep -i
"away\|vacation\|presence\|holiday"` finds only unrelated prose).

A week away is the single largest saving a heating system can offer: a deep
setback plus DHW suppressed entirely, except for a legionella cycle timed to
complete before return.

What makes this more than an `input_number` is the *return time*. Knowing when
the house must be comfortable again lets the optimizer buy the recovery heat in
the cheapest hours beforehand, instead of panic-heating on arrival at whatever
the spot price happens to be. That is exactly the machinery the DHW planner
already has for guaranteed slots, applied to the building.

Proposed approach:

- Accept away state from a `person`/`device_tracker`, a calendar entry, or a
  plain `input_boolean`, plus an expected return datetime.
- Away setpoints (space and DHW) as config, separate from comfort mode.
- Reuse the existing deadline-driven planning to schedule recovery, and reuse
  the legionella deadline logic so the cycle lands before return, not after.

Care needed: a wrong return time is a comfort failure the user will notice.
Prefer conservative early recovery, and make manual override obvious.

## 14. Defrost and cold-humid capacity derate

`defrost` does not appear anywhere in the codebase. The model assumes a clean
COP-versus-outdoor-temperature relationship.

Air-source units lose real capacity and efficiency in roughly the 0 to +5 C
humid band, because of frost accumulation and the defrost cycles that clear it.
That band is precisely the Swedish shoulder season, and precisely where the
plan is most aggressive about coasting on stored heat. Plans made there quietly
under-deliver, and the shortfall shows up as a comfort miss rather than as an
obvious fault.

Proposed approach:

- Learn a capacity/COP derate as a function of outdoor temperature and, if the
  weather integration supplies it, humidity, from observed predicted-versus-
  actual performance.
- Apply the derate in the optimizer's power-to-heat conversion so the planner
  knows heat is more expensive in that band and stores more beforehand.

Depends on item 11 (closed-loop accuracy), which supplies the
predicted-versus-actual signal this learns from. Do not hand-code a derate
curve from a datasheet; units vary too much.

## 15. Energy dashboard and long-term cost statistics

Every monetary sensor is `SensorStateClass.MEASUREMENT` (sensor.py:156-233).
Nothing is `TOTAL_INCREASING`, so none of it reaches Home Assistant's Energy
dashboard and there is no long-term cost history.

The result is that the integration's central claim, that it saves money, is
invisible in the one place HA users look for exactly that.

Proposed approach:

- Add accumulating cost and energy sensors with `TOTAL_INCREASING`, split DHW
  versus space heating so the split is visible.
- Register them with the Energy dashboard as a device consumption source with
  an associated cost.
- Consider `async_add_external_statistics` for backfilling, if history exists.

Depends on item 6 (measured power) for the accumulators to reflect reality
rather than the commanded plan.

## 16. Plan reason codes

The plan sensors publish which slots were chosen but never why. A slot could
be cheapest-price, deadline-driven, legionella, terminal-value, or a comfort
floor, and nothing distinguishes them.

The practical consequence: an unexpected slot is indistinguishable from a bug.
That makes the optimizer hard to trust and hard to support, and it makes bug
reports much weaker than they could be.

Proposed approach:

- Tag each planned slot with a short reason code at the point the optimizer
  decides it, and carry it through to the plan sensor attributes.
- Surface it in the card, in the tooltip or the expanded popup, where there is
  already room.

Small change, disproportionate effect on user confidence. It also pairs well
with item 11: a reason code plus a realised outcome makes drift diagnosable.

## 17. Building type presets and emitter selection

**This is the highest-value item in the 17-21 block. It should be done first,
and it makes items 18 and 19 land better.**

`config_flow.py` `async_step_thermal` (~line 412) asks the user for
`house_thermal_mass` in kWh/degC and `slab_thermal_mass` as raw numbers. No
homeowner knows either value. Worse, the shipped defaults quietly encode one
specific house:

```
DEFAULT_LOWER_FLOOR_THERMAL_MASS = 8.0  # kWh/degC - heavy concrete slab
DEFAULT_UPPER_FLOOR_THERMAL_MASS = 3.0  # kWh/degC - lighter (radiators + air)
```

That is a two-zone house with a slab downstairs and radiators upstairs. Any
other house starts wrong, and the learners then spend weeks walking away from a
bad prior, constrained by guard thresholds that exist precisely because the
prior might be bad.

Proposed approach: ask what the user actually knows, and derive the physics.

**Structure (drives thermal mass):**

- Timber frame, suspended floor / crawl space (regelstomme, krypgrund or
  torpargrund) - very light. Little heavy mass inside the insulation envelope,
  and the floor itself is a loss path rather than a store.
- Timber frame on concrete slab (platta pa mark) - light walls, heavy floor.
- Concrete or brick, slab - heavy throughout.
- Stone or masonry (typically older) - very heavy, and usually paired with
  higher losses.
- Basement (kallare) as a separate foundation option, since a heated basement
  adds both mass and loss area.

**Era (drives the heat loss coefficient):** pre-1960, 1960-1980, 1980-2005,
post-2005 (BBR), and low-energy/passive. Era plus heated area gives a far
better loss estimate than any single default, and Swedish era bands map
reasonably well onto insulation standards of their time.

**Emitters, selectable per zone:**

- Floor heating in both zones
- Radiators in both zones
- Floor heating in one zone, radiators in the other (either way round)

This matters for two separate reasons, and it is worth keeping them distinct:

1. **Mass.** A heated screed or slab is a large thermal store that is
   *actively charged*. Floor heating therefore raises effective thermal mass
   well beyond the same house with radiators.
2. **Response time.** Radiators respond in minutes, floor heating in hours.
   That directly bounds how far ahead the optimizer can usefully shift load,
   and how quickly it can recover from a setback. A slow emitter makes
   pre-heating both more valuable and more necessary.

Note that `CONF_RADIATOR_POWER_FRACTION` already exists, so part of the
plumbing is there; what is missing is the *type* selector and the parameter
derivation behind it.

**Design notes:**

- Presets set *starting values only*. The existing learners must remain
  authoritative and converge to the real house. Make this explicit in the UI,
  or users will treat the preset as a claim about their building.
- Keep the derived numbers inspectable and overridable. An advanced user with
  a real energy declaration should still be able to type exact values, so keep
  the current numeric path available rather than replacing it.
- Scale mass and loss by heated area rather than shipping absolute numbers per
  archetype; area is something users reliably know.
- Consider seeding the learner confidence lower for preset-derived values than
  for user-entered ones, so they move faster initially.

This is the single biggest usability win available: it replaces two
unanswerable questions with three answerable ones, and it improves accuracy at
the same time.

## 18. Active system identification at commissioning

Every learner in the codebase is passive. It waits for the house to happen to
do something informative, which is why parameters take weeks to converge and
why the guard thresholds (`HOUSE_LOSS_MAX_RESIDUAL` and friends, coordinator.py
205-244) must be so conservative: normal operation provides poor excitation, so
most observations are ambiguous and have to be rejected.

Standard practice in process control is to stop waiting and run an experiment.

Proposed approach:

- During a mild, cheap night, inject a deliberate step change and record the
  response. A step gives clean excitation, so the time constant and loss
  coefficient fall out in days rather than weeks.
- Gate it on conditions that make it both safe and cheap: mild outdoor
  temperature, low prices, house unoccupied or asleep, user opt-in.
- Feed the result in as a high-confidence prior, then let the normal passive
  learners continue from there.

Care needed: the step must be small enough that the user does not notice, which
bounds how much information you can extract. Treat comfort as a hard
constraint on the experiment, not a cost term. Also make it abortable, and
never run it twice in a row on a house that already converged.

Pairs naturally with item 17: presets give a good starting point, active
identification confirms or corrects it quickly.

## 19. Revealed-preference comfort tuning

`comfort_weight` defaults to 5.0 (optimizer.py:237) and sets the exchange rate
between money and degrees in the objective (`optimizer.py:24`). It is the most
consequential number in the configuration and the least knowable: it has no
intuitive units, and no user can reason about what 5.0 means.

But users constantly reveal the answer. Every manual override is the user
saying the plan went too far in one direction. Override upward during an
expensive coast means comfort_weight is too low; never overriding while paying
for a very flat temperature profile suggests it is too high.

Proposed approach:

- Record overrides with context: the setpoint delta, direction, indoor
  temperature, and what the plan was doing at that moment.
- Adjust `comfort_weight` slowly from the accumulated evidence, with the same
  kind of guard rails the thermal learners already use.
- Show the current learned value and let the user reset it. An invisible
  self-adjusting objective would be alarming.

This deletes the hardest configuration question in the integration and replaces
it with something users already do without being asked.

Care needed: overrides are noisy and sometimes have nothing to do with the
plan (a party, illness, an open window). Require consistent evidence before
moving, and never move fast.

## 20. The house as a declared virtual battery

The building fabric plus the buffer and DHW tanks together form real energy
storage, but nothing in the integration exposes it as such. It is modelled
internally and never published.

Proposed approach:

- Publish state of charge in kWh, usable capacity, charge and discharge rate
  limits, and an effective round-trip efficiency (which is where the COP and
  the standing losses show up).
- Define SoC against the comfort band: energy stored above the minimum
  acceptable temperature is what is actually available.

Two payoffs:

1. Other Home Assistant energy automations can then reason about the heat pump
   as a battery alongside a real one, rather than as an opaque load.
2. It is the precondition for flexibility market participation (FCR-D, mFRR
   via an aggregator), where thermal storage can earn money for capacity the
   user already owns.

The second reframes the product: from "saves money on the spot price" to
"monetises a battery you did not know you had." That said, market
participation itself is a large piece of work with contractual and telemetry
requirements; publishing the abstraction is the useful first step and stands on
its own.

## 21. What-if simulator in the card

The optimizer can already price a plan, but the user never sees the price of
their own comfort choices. Setpoints are chosen blind and their cost is never
attributed.

Proposed approach:

- Let the user drag comfort temperature, or move a DHW guaranteed slot, in the
  card, and show the resulting monthly cost delta immediately.
- Reuse the existing optimizer against the current forecast. No new modelling
  is required, which makes this unusually cheap for its impact.
- The expanded popup added in v2.7.0 is the natural home for it.

This converts "I set 21 because it sounds about right" into an informed
decision, and it makes the value of the whole integration visible in the place
users already look.

Care needed: run the what-if evaluation off the live plan so an exploratory
drag never disturbs actual operation, and rate-limit it so dragging a slider
does not trigger a solve per pixel.

## 22. Give the comfort slider a home: a "Temperatures" section with DHW minimum

**Superseded decision (user, 2026-08-23). This item used to say "remove the
comfort temperature slider". It now says keep it.** The slider was called
"weird" because it appeared on its own with no context — a lone unlabelled
temperature control in a section about scheduling. The problem was placement,
not the control. The fix is to group it with a second slider, **minimum hot
water temperature**, in a section of its own.

Read the rest of this item with that inversion in mind; the earlier framing
about retiring the simulate path is dead. The simulator is what makes both
sliders worth having, because it prices the change.

**Where it is now.** `heatpump-optimizer-card.js`, in the second `.wi-section`
("My usual schedule"), rendered around line 1020 as `input.wi-temp` bound to
`draft.comfort`, seeded by `_currentComfortTemp()` (~1102) with the listener at
~1319.

**The good news: the backend is already done for the what-if side.**
`simulate_plan` accepts `dhw_min_temperature` today — it is in
`SERVICE_SCHEMA_SIMULATE_PLAN` (`__init__.py`, ~line 88) *and* handled in the
coordinator (`coordinator.py:3940`, setting `scratch_params.dhw_min_temp`). So
adding the second slider to `_whatIfOverrides()` (~1495) needs **no backend
change at all** to make the price delta work. Verify this rather than assume it;
it is the kind of thing that is easy to half-believe.

**The gap is on the save side, and it is the one thing that will bite.**
`SERVICE_SCHEMA_APPLY_SCHEDULE` (`__init__.py:106`) has only
`day_start_hour`, `day_end_hour`, `dhw_windows`, `comfort_temp_day` and
`entry_id`. `vol.Schema` rejects unknown keys by default, so adding
`dhw_min_temperature` to the card's save call **without** adding it to that
schema fails the whole call with `extra keys not allowed` — and the user loses
their heating-hours edit too, not just the DHW minimum. Add the key in three
places: the voluptuous schema (validation, mandatory), `services.yaml`
(the UI form, ~line 468 — cosmetic but it is the documented interface), and the
handler that writes it into the config entry.

**Note the two schemas already disagree, so do not treat `services.yaml` as the
source of truth.** `services.yaml`'s `apply_schedule` block does not list
`target_temp`, but `SERVICE_SCHEMA_SIMULATE_PLAN` does accept it. The real
contract is in `__init__.py`; `services.yaml` is UI metadata that has drifted.

**A correction to what this item used to claim.** The old text said
`apply_schedule` "sends `target_temp` *and* `comfort_temp_day` from the same
value". That is not what the code does. `_whatIfOverrides()` sends both, but it
is only used for `simulate_plan` (~1530); the save path at ~1461 builds its own
payload with `comfort_temp_day` and no `target_temp`. Good thing too — sending
`target_temp` there would currently be rejected by the schema above. Do not
"fix" a bug that is not there.

**Sensible shape.** A third `.wi-section` titled something like "Temperatures",
holding comfort temperature and minimum hot water temperature, leaving "My usual
schedule" as heating hours plus hot water windows. Both sliders feed the same
debounced `simulate_plan` and the same Save. Reuse the existing `.wi-temp` /
`.wi-value` CSS and the existing debounce rather than adding a second timer —
two independent debounces racing on one service call is how you get the delta
showing the price of the *previous* drag.

**Pick the range deliberately — and the user has now decided this.**
`DEFAULT_DHW_MIN_TEMP` is 45 °C (`const.py:363`), described as the usable
minimum inside demand windows. **Decision (user, 2026-08-23): clamp the DHW
minimum slider's range against `dhw_setpoint`.**

Three things that decision implies, none of which are automatic:

- **Clamp below the setpoint with a margin, not up to it.** A minimum equal to
  the setpoint leaves no deadband: the tank would have to sit exactly at target,
  so the pump would short-cycle against its own hysteresis. Put the margin in a
  named constant next to `DEFAULT_DHW_MIN_TEMP` rather than as a literal in the
  card, since the backend needs the same number to validate against.
- **The clamp has to be dynamic.** `dhw_setpoint` is itself configurable, so the
  slider's maximum has to be recomputed when it changes, not fixed at render
  time. A slider whose ceiling was computed against last week's setpoint is
  exactly the kind of staleness that bit `_draftRuns` in v3.2.0.
- **Handle a stored value that already violates it.** An existing config can
  have `dhw_min_temp` above the new ceiling. Clamp for display *and* decide
  whether saving silently rewrites it — silently lowering a user's hot water
  minimum is a surprise worth a visible note rather than a quiet correction.

**Validate on the backend too, not only in the slider.** The card's range is a
convenience; `simulate_plan` and `apply_schedule` can both be called directly
from an automation. Because the comfort and tank limits are **soft penalties**,
an out-of-range minimum is not rejected by the solver — it asks for a tank state
that can never be reached and the plan simply sits permanently in slight
violation, which is very hard to diagnose from the outside. This is the same
soft-constraint trap as everywhere else in this codebase.

**Done.** A "Temperatures" section now holds the comfort slider and a new
minimum-hot-water slider, and "My usual schedule" keeps the heating hours and
hot water windows. Notes for whoever touches this next:

- `dhw_min_temperature` was added to `SERVICE_SCHEMA_APPLY_SCHEDULE`, to the
  handler's update loop and to `services.yaml`, as this item required. The
  simulate side needed nothing, exactly as predicted.
- The deadband margin is `DHW_MIN_TEMP_SETPOINT_MARGIN` (5 °C) in `const.py`.
  **The card does not have a copy of it.** The plan sensors publish
  `dhw_min_temperature_max`, the already-computed ceiling, and the slider clamps
  to that. This is what makes the clamp dynamic for free: the sensor republishes
  when the setpoint changes, so there is no render-time staleness to get wrong.
- The backend validates per config entry *before* writing to any of them, since
  `dhw_setpoint` is per entry. A call spanning two heat pumps now fails whole
  rather than half.
- A stored value above the ceiling is clamped for display and the card says so
  in a `wi-warn` note; saving stores the clamped value.
- Found and fixed in passing: `_planAttr` used `Number(raw)` and an `isFinite`
  guard, so an attribute published as `None` became a real `0` rather than
  falling back. That would have capped the new slider at zero, and was already
  capable of showing a 0 °C comfort target.

## 23. Zoom and scroll the slot lanes

Requested after v3.2.0: the lanes should be zoomable and scrollable sideways.

**Scope decision (user, after v3.2.0): the past is out.** The original request
included scrolling 24 hours back, but there is no data source for it — both
plan sensors declare `_unrecorded_attributes = frozenset({"forecast"})`
(`sensor.py:381` and `:900`), so plan history is deliberately kept out of the
recorder and nothing stores what the plan used to say. Rather than build a ring
buffer for it, viewing the past was dropped. If it ever comes back, the good
version is plotting *measured* power from item 6 (which is recorded) — what the
pump actually did, not what was once intended.

So this is forward-only: pan and zoom between now and the end of the horizon.

**How.** `_geom.windowStart/windowEnd` (set in `_chartSvg`, ~1967) currently
derive from `now` and `cfg.hours`. Pan and zoom mean making those two values
state the user can change rather than derived constants. Do it *through*
`_geom` and re-render — not with a CSS transform on the SVG. `_timeAtClientX`
(~2202) inverts the mapping against a measured `getBoundingClientRect()`, so a
visual-only transform would silently break drag hit-testing, which is the whole
point of the lanes.

Bound the zoom-out by data, not by the axis: `cfg.hours` (the plot window,
capped at 168) is a different quantity from the optimizer's horizon
(`optimization_horizon`, default 24 h). Zooming past the horizon shows empty
space, not more plan.

`windowStart` stays pinned at now, so the existing locked-past shading
(`_editFloor`) has nothing new to handle.

**Done.** Forward-only pan and zoom, as scoped above.

- `_applyView` narrows the default window and is a **no-op until the user
  touches a control**, so an untouched card renders exactly as before — which is
  why the 37 golden scenarios and the existing card tests did not move.
- Zoom-out is bounded by the plan's real extent, not by `cfg.hours`. Note the
  consequence: with `hours` set wider than the horizon, the default view is
  wider than the plan, so the first zoom-out snaps in to the plan's extent.
  Reset returns to the configured window.
- Panning listens on `window`, not on the svg, because a view change re-renders
  and replaces the element the gesture started on.
- A plain vertical wheel is deliberately ignored so the dashboard still scrolls
  under the pointer; pinch (wheel + ctrl) zooms, sideways wheel pans. The
  `.viewctl` buttons exist because neither gesture is available on a phone or to
  a keyboard user, and they stay visible under `@media (hover: none)`.
- `_draftRuns` reads the raw sensor forecast rather than the windowed series, so
  zooming cannot truncate the draft or make Apply pin a subset. Verified, not
  assumed. Runs entirely outside the window are skipped rather than clamped, or
  they collapse into a one-pixel sliver at the plot edge.
- **Not done:** touch pinch-to-zoom. Touch users get the buttons. If it is
  added, note that `svg` already sets `touch-action: none`.
- `_editFloor`/`_editCeiling` derive from the *visible* window, so while zoomed
  a slot cannot be dragged outside it. That is a behaviour change from this
  item, and item 24+25 rewrites `_editCeiling` anyway — reconcile the two there.

## 24 + 25. A 20-hour editable window, measured from the last apply

**These are one job.** The midnight cap on editing is not arbitrary:
`manual_plan.channel_pins` frees every step at or beyond `expires_at`, so
`_editCeiling()` (~2343) caps at the next local midnight to stop the card
showing slots as pinned while they silently do nothing. Change the expiry
without the ceiling, or the other way round, and that bug comes straight back.

**Decision (user, after v3.2.0): the editable timeframe is 20 hours from the
last manual apply.**

Concretely:

- `build_override` defaults `expires_at` to `now + 20 h` instead of
  `next_local_midnight(now)`. Applying again restarts the 20 hours.
- `_editCeiling()` becomes `min(now + 20 h, horizon end)` — that is, the expiry
  the card *would* send if the user applied right now, not the expiry of the
  override currently in force.

That second point is the subtle one. If an override was applied 15 hours ago it
expires in 5, but the user editing now is composing a *new* plan that will
expire 20 hours from this moment. Deriving the ceiling from the active
override's expiry would shrink the editable window as the day wore on and stop
the user extending their own plan.

**20 rather than 24 solves a real problem, so do not quietly round it up.** The
default optimizer horizon is 24 hours (`DEFAULT_OPTIMIZATION_HORIZON`). A
24-hour override would cover the entire horizon at every moment, leaving no
free step for the optimizer until it expired — re-applying daily would switch
the optimizer off while appearing to leave it on. At 20 hours there is always a
tail of roughly 4 hours the optimizer still owns. Keep that margin if the
horizon ever becomes the thing being changed: the invariant is *override
shorter than horizon*, not the number 20.

Still clamp the ceiling to the horizon end as well, since the horizon is
configurable and may be shorter than 20 hours. Show that end the way the locked
past is shown, rather than letting the user drag into a region no pin can land
in.

**DST is no longer a concern here.** 20 hours from an apply is 20 elapsed
hours, with no wall-clock time to land on; the old `next_local_midnight`
DST-correctness argument does not carry over and does not need reproducing.

Put the 20 in one named constant used by both sides rather than repeating a
literal in the card and the backend — the whole point is that the ceiling and
the expiry cannot drift apart.

Touch points: `build_override` (`manual_plan.py:240`) and its `expires_at`
default (~269), the `apply_manual_plan` schema default in `services.yaml`,
`_editCeiling` in the card, and the expiry wording in `_overrideHtml`.

**Done.** `MANUAL_PLAN_WINDOW_HOURS = 20` in `const.py`, obeyed by both sides.

- **A correction to this item.** It says `build_override` defaults `expires_at`
  to `next_local_midnight(now)`. It does not -- `build_override` takes
  `expires_at` as a **required** keyword with no default. The real default was a
  single site in the `apply_manual_plan` handler, which is all that changed.
- `next_local_midnight` is **deleted**, along with the now-unused `timedelta`
  import it needed. Nothing else used it.
- **The card does not hold a copy of the 20.** The plan sensors publish
  `manual_plan_window_hours` and `_editCeiling` reads it, the same pattern item
  22 used for `dhw_min_temperature_max`. A literal in the card that could drift
  from the service's default is precisely the failure this item exists to
  prevent, so it is asserted in `tests/entities.py` and in `tests/card.mjs`.
- **`_editCeiling` now takes the smallest of three limits**, not two: the expiry
  the card *would send if applied now*, the end of the plan, and the visible
  window. That third term is new since item 23 made pan and zoom narrow the
  visible window -- without it a slot could be dragged out of the region the
  pointer can reach. Item 23's note asking for this to be reconciled here is
  now settled.
- **Expiry wording had to change and this item does not mention it.** Both the
  banner and the apply result formatted `toLocaleTimeString` with hour and
  minute only. Under the midnight rule the day was implicit; a 20-hour expiry
  usually lands tomorrow, so "pinned until 08:30" became ambiguous. There is now
  one `fmtExpiry` helper that adds "tomorrow" or a weekday when the expiry is
  not today.

Two tests were passing for reasons that would not survive the change:

- `tests/manual_plan.py`'s "a slot late in the horizon is still counted" pinned
  a slot at 20-22 h against a 26 h expiry. Under a 20 h window those steps are
  freed, so the check reported 0 and would otherwise have been "fixed" by
  loosening it. The slot moved to 17-19 h, which preserves what it was actually
  testing -- that the count is measured per step over the horizon rather than
  in hourly price entries -- and a new check asserts the other side of the
  boundary, that a slot past the window pins nothing.
- `tests/card.mjs` recomputed midnight by hand and asserted the ceiling was
  below it, which says nothing once the rule changes. It now asserts against the
  window directly, and a new check covers the subtle case: a card showing an
  override applied 15 hours ago must still offer the *full* window, not the
  5 hours left on the old one.

## 26. Expanded card overflows its own boundary at some window sizes

**Symptom:** at some window sizes everything below "Today's slots" — the delta
calculator and the buttons — renders outside the expanded card's visible
boundary.

**Root cause, confirmed in the CSS.** `dialog.expanded` (~1724) sets
`overflow: visible` and has **no `max-height`** — there is no `max-height`
anywhere in the file. Its width is
`min(96vw, calc((100vh - 168px) * ${VIEW_RATIO}))`, where the `168px` is a
hardcoded guess at how much vertical space the chrome needs. That budget has not
grown with the chrome: v3.2.0 added the override banner, the delta row, a third
button and a status line to the what-if panel. When the real chrome exceeds
168px, the content runs past the dialog's painted background instead of being
clipped or scrolled, which is exactly the reported symptom. Short, wide windows
hit it first, because the width formula makes the dialog *wider* as the viewport
gets shorter.

### Would splitting the dialog into two pages fix it?

Proposed by the user, 2026-08-23. **Partly — and it is worth doing — but not
along the line that fixes the reported symptom, so it is not a substitute for
bounding the height.**

The conflict is specific: `.chartwrap.big` carries
`aspect-ratio: ${VIEW_W} / ${VIEW_H}` (~line 1742), so the chart's height is
*dictated* by the dialog width, and the width formula sets that width so the
chart consumes `100vh - 168px`. A fixed-aspect chart and variable-height chrome
are competing for one fixed viewport height, and the chrome is the part that
grew. Pagination attacks this correctly in principle: put the chart and the big
chrome on different pages and they stop competing.

**The problem is where the split can go.** The slot lanes are not a separate
panel — they are `<rect class="lane">` elements drawn *inside the chart SVG*
(~2386–2432), positioned in the chart's own coordinate system, and
`_timeAtClientX` hit-tests against the SVG's measured rectangle. So "Today's
slots" cannot be moved to a page without the chart. And the reported symptom is
precisely the things attached to it — the delta calculator and the buttons
below "Today's slots".

That leaves the honest split as **page 1: chart + lanes + delta + apply
buttons; page 2: "My usual schedule"** (which, after item 22, also gains the
Temperatures section, making it a more natural page of its own). That removes
real height from the overflowing page — perhaps a third of the chrome — and may
well be enough in practice. But page 1 remains the heavy one, and it is the one
that overflows today.

**So sequence it: fix the layout first, then paginate if the UI still wants
it.** Bounding the dialog (`max-height` plus `overflow: auto`, or better the
flex column described under "Fix direction" below so the chart takes leftover
space instead of dictating it) removes the failure mode outright, for both pages
and any future panel. Pagination on its own makes the bug rarer without making
it impossible — and a second page with no height bound will eventually spill in
the same way.

**If it is built, two traps.** The current page becomes state that must survive
a re-render, and `_maybeRender` already had a stale-state bug of exactly this
shape in v3.2.0 (finding 3, the memoised `_runs`) — decide up front whether a
plan refresh resets the page. And a hidden page must be genuinely unrendered or
laid out, not merely `display: none` with live drag handlers: `_timeAtClientX`
measures `getBoundingClientRect()`, which returns zeroes for a hidden element,
so a stale listener would silently compute garbage times rather than fail.

**Fix direction.** Adding `max-height: 96vh; overflow: auto` stops the spill,
but leaves the magic number to drift again on the next panel that grows. The
durable fix is to stop guessing: lay the dialog out as a flex column and let
the chart take the space actually left over after the header, legend and panel
have been measured, so the chart adapts to the chrome rather than the chrome
being budgeted for in advance. Keep `preserveAspectRatio="none"` in mind — the
chart can be given any box, but the font is part of the geometry, so verify the
axis labels at both extremes rather than only in the middle.

**Reproduce before fixing**, at a short wide viewport (roughly 1400x700) with
an override active, since the banner is one of the elements that pushed the
chrome past its budget.

**Confirmation from the user (2026-08-23): the mobile app is fine; this only
happens in a desktop browser.** That is not a separate case to chase, it is the
diagnosis above being right. The width is
`min(96vw, calc((100vh - 168px) * VIEW_RATIO))`, a `min()` of two branches:

- On a phone the viewport is narrow and tall, so `96vw` is the smaller term and
  wins. The height-derived branch never binds, the `168px` guess is never
  consulted, and nothing overflows.
- On a desktop browser the viewport is wide and comparatively short, so the
  `calc()` branch wins and the dialog is sized *from* the height budget. Now the
  hardcoded `168px` is load-bearing, and when the real chrome exceeds it the
  content spills.

Two consequences for whoever fixes this. Do not "fix" it by special-casing
mobile or by adding a breakpoint — both viewports are running the same broken
formula, and the phone is merely on the branch that happens to be safe. And
**test on desktop only for the reproduction, but check the phone for the
regression**: replacing the formula with a flex column changes the branch the
phone was silently relying on, so the case that was never broken is the one most
likely to break.

**Done.** The height budget is gone; the dialog is a bounded flex column.

- **Reproduced first, measured in a real browser.** At 1400x700 with an override
  active, the what-if panel rendered **449px below the dialog's painted bottom
  edge**. After the fix, -16px (contained, with padding to spare).
- The width no longer encodes a chrome guess. `dialog.expanded` is
  `width: min(96vw, calc(78vh * VIEW_RATIO), 1700px)`, `max-height: 92dvh`
  (with a `92vh` fallback), `display: flex; flex-direction: column`. A new
  `.dlg-body` wraps chart + panel and carries `overflow-y: auto`; the header and
  legend are `flex: 0 0 auto`.
- **The chart keeps its exact aspect ratio deliberately.** Verified isotropic on
  screen (scaleX == scaleY == 1.4013). Bounding the chart's *height* instead
  would have been the obvious move and is wrong: `preserveAspectRatio="none"`
  means it stretches every axis label sideways.
- **Scroll survives a re-render**, which it had to: `_syncDialog` re-runs
  `showModal()` on every `_render()`, and `_render` fires on the coordinator's
  schedule, so the panel would otherwise jump to the top by itself every few
  minutes mid-edit. `_render` captures `.dlg-body` scrollTop, `_syncDialog`
  restores it after `showModal`, `_onDialogClose` resets it.
- **The ResizeObserver bug this item sat next to is gone as a side effect.** It
  observes the host card, not the dialog or viewport, so a height-only resize
  changed `100vh` -> dialog width -> the font `_scaleDialogFont` derives, with no
  observer firing. Nothing is sized from `100vh` any more.
- **Phone checked for regression, since the fix changed the branch it relied on.**
  Still on the `96vw` branch (360px at a 375px layout viewport), aspect exact, no
  horizontal overflow. Note `vw`/`vh` resolve against the *layout* viewport, not
  `innerWidth` -- an early measurement using `innerWidth` looked like a
  regression and was not one.
- **Pagination was not done**, per this item's own sequencing argument. The
  height bound removes the failure mode outright; pagination only makes it rarer.

**Found while verifying, not fixed here (out of scope):** the two right-hand
axis titles collide in the expanded view when the solar series is on --
"SEK/kWh" at viewBox x=797 and "W/m2" at x=843 are 46 units apart while the
expanded font needs ~58. Confirmed pre-existing by reproducing it identically
(22.5px vs 23.1px) under the old width formula.

### Value axis titles collide when two axes share a side (found 2026-08-23)

**Done.** Found while verifying item 26, deliberately not fixed there, and fixed
separately here.

The price axis title sits at viewBox x=797 and the solar axis title at x=843 --
46 units apart, a gap that does not scale. `FONT_EXPANDED` is 15, so "SEK/kWh"
needs roughly 58 units and overlapped "W/m2" by ~23px on screen.

The fix measures the title with the same `length * size * CHAR_WIDTH_EM` model
the time axis already uses for its own collision checks, and flips the anchor to
the inside of its own axis line when it will not fit. **It reduces exactly to the
old expression when no flip is needed** (`ux === tx` for the default anchor), so
the uncrowded case is byte-identical and the solar title never moves.

Two notes for whoever touches the chart tests next:

- **`_hidden` is persisted in localStorage, and the `tests/card.mjs` stub shares
  one store across every `build()` in the file.** An earlier test that hides a
  series leaves it hidden for every later one. The first version of these tests
  passed while silently not rendering the solar axis at all -- i.e. not testing
  the crowded case. There is now an explicit `withAllSeries()` helper and a check
  that both right-hand axes are actually present.
- Mutation tested: reverting the flip fails the expanded overlap check while the
  inline one still passes, which is correct -- at `FONT_BASE` 10 the titles fit.

## 27. The buffer tank is in the state vector but is not a store

> ## Status, 2026-08-23 (v3.7.1). Partly built.
>
> **Done.** The tank is a real store when a mixing valve exists: draw is
> decoupled from supply, the standby loss is physical at any size, and the
> optimizer can see stored tank heat. See item 29's status block for the detail
> and for what is still unexplained.
>
> **Outstanding, and both are things this item specifically asked for:**
>
> - ~~**No size threshold.**~~ **Done in v3.10.0.** The user's decision was
>   "make it a real store when the tank is large enough, and behave
>   appropriately when it is configured so small it is not a viable store".
>   `ThermalParameters.buffer_is_store` now requires a valve *and*
>   `BUFFER_STORE_MIN_VOLUME` (100 L); below it the terminal credit and the
>   settlement cap ignore the tank while the physics stay modelled. The 35 L
>   default lands below it decisively, for the reason recorded here: ~0.8 kWh
>   over a 20 K swing is below the resolution of a single 15-minute step.
> - **`get_state_matrices` is still dead and still contradictory.** This item says
>   plainly: reconcile both models or delete the dead one, and do not fix one and
>   leave the other. That is exactly what happened -- `_simulate_step_two_zone`
>   was fixed and `_get_state_matrices_two_zone` was not, so the two now disagree
>   more than before. It has zero callers repo-wide. Deleting it is the cheaper
>   half of the choice.
>
> **Decision and verification, 2026-08-23. Read this before the item text.**
>
> **User decision:** make the tank a real store *when it is large enough to be
> one*, and behave appropriately when it is configured too small to be viable.
> The user notes **most installs run >500 L**.
>
> **That conflicts with what ships.** `DEFAULT_BUFFER_TANK_VOLUME` is **35 L** --
> worth ~0.81 kWh thermal over a 20 K swing, which is below the resolution of one
> 15-minute optimizer step. So the default is probably wrong for the actual user
> base, and `BUFFER_COOLING_RATE_MAX = 30 °C/h` is likewise a clamp sized for
> 35 L and absurd for a 500 L store. Revisit both alongside the model change.
>
> **The item's central claim is confirmed exactly**, by reading rather than
> inference: in `_simulate_step_two_zone`,
> `q_rad_from_buf + q_floor_from_buf == thermal_power` identically for *any*
> `rad_fraction`, so the supply term cancels and `dT_buf = -q_buf_loss / C_buf`.
> `electrical_power` has no path to the buffer at all. Two additions to what the
> item says: the tank is fully **decoupled** from the other three states in both
> directions (removing it from the nonlinear step would not change the house
> trajectory at all), and the coordinator's re-seed only fires when the optional
> sensor is configured -- without it the value is a frozen 40.0 forever, which is
> the default install.
>
> **Both optimizer readers are effectively inert today.** The heat-loss makeup
> term is a state-dependent constant the optimizer cannot steer, and the
> end-of-horizon credit nets to ~0 because baseline and optimized end-states
> decay identically. The credit also borrows the *slab's* settlement cap key,
> which is a number computed for a concrete floor, not a 40-60 °C water tank.
>
> **For item 28:** external-heat suppression currently affects **DHW only**.
> There is no space-heating suppression path at all, so a wood furnace feeding
> the space-heating buffer gets no space-heating response today. That is likely a
> large part of item 28's real work, and the item does not say so.


**Found while assessing item 28, 2026-08-23. This is a real modelling bug and it
is item 28's prerequisite.**

In `_simulate_step_two_zone` (`thermal_model.py`, ~line 923) the tank is charged
by `thermal_power` and drawn by `q_rad_from_buf + q_floor_from_buf`, which are
`rad_fraction * thermal_power` and `(1 - rad_fraction) * thermal_power`. Those
two sum to exactly `thermal_power`, so the supply term cancels identically and

```
dT_buf = -q_buf_loss / C_buf
```

The buffer temperature can therefore **only ever fall**, toward 20 °C, at a rate
the heat pump cannot influence.

**Measured, not inferred.** Starting at 40 °C, stepping 2 h at −5 °C outdoor:

| electrical power | buffer after 2 h |
|---|---|
| 0 kW | 32.191 °C |
| 3 kW | 32.191 °C |
| 9 kW | 32.191 °C |

Identical to three decimals, while the slab moves 21.69 → 26.35 °C. The tank is
a pass-through with a leak bolted on.

**Why it has not caused visible damage.** The coordinator re-seeds
`buffer_tank_temperature` from the real sensor every cycle
(`coordinator.py:2149`), so the decay only accumulates *within* one horizon and
is corrected on the next run. The two places that read it —
the heat-loss makeup term (`optimizer.py:3022`) and the end-of-horizon stored
energy credit (`optimizer.py:3058`) — therefore get a value that is right at
step 0 and increasingly pessimistic thereafter. It biases the settle-up slightly
and cannot be steered. That is a quiet bias, not a blow-up, which is exactly why
it has survived.

**There is a second, contradictory model of the same tank.**
`_get_state_matrices_two_zone` (~1243) sets `A[3,3] = -k_buf/C_b` and
`B[3] = cop/C_b` with **no draw term at all** — there, the tank only ever
*charges*. So the linearised model and the nonlinear model disagree about the
sign of the pump's effect on the buffer. **This one is currently harmless:
`get_state_matrices` has no callers outside `thermal_model.py`** (verified), so
it is dead code. Do not fix one and leave the other; either reconcile both or
delete the dead one, or the next person to wire up an LQR/QP path inherits a
tank that charges without ever being drawn.

**What the fix actually requires.** Making the buffer a store means the draw can
no longer be defined as a fixed fraction of the supply. The draw is the *house's
demand*, which depends on emitter temperatures and flow, and the supply is the
pump. Those have to become independent, which is a genuine model change rather
than a sign fix — and it is what would let the optimizer shift load into the
tank at all. Before doing it, decide whether the tank is big enough to be worth
modelling as storage: `CONF_BUFFER_TANK_VOLUME` defaults to a small tank and the
comment at `const.py:381` already observes that a buffer tank holds very little
water. It may be that the honest fix is to stop pretending it is a state
variable, not to make it a better one. **Run `tests/golden.py` either way — this
changes plan output, so the byte-for-byte diffs will be non-empty by design and
need reviewing rather than re-baselining blind.**

## 28. Wood furnace: a second buffer tank and a mixing valve

> ## Status, 2026-08-24 (v3.11.0): done, in the item's own ranked order.
>
> **1. The harness first.** The model, both trajectory functions and the
> optimizer take a per-step `external_heat_kw` forecast; it joins the pump's
> output at the hydronic mix and never touches the COP. The savings baseline
> receives the same free heat, so a burn is not booked as savings. Feature
> off (None or all-zero) is byte-for-byte the old model.
>
> **2. The payoff, measured before the estimator was built** (the item's own
> instruction): tests/backtest.py's furnace section, a value-of-information
> A/B — the fire burns in both arms, only one plan knows. An 8 kW evening
> fire through the winter_typical peak is worth **+4.2 SEK/day** to know
> about. Zero-burn null control asserted byte-for-byte in features.py.
>
> **3. The outlet sensor → displacement.** `f = (T_out − T_hp)/(T_wood −
> T_hp)`, a new `displacement` field on `ExternalHeatState` (not
> `confidence`, exactly as this item warned). The forecast fed to the solve
> is bounded three independent ways: a hard 2 h horizon
> (`EXTERNAL_HEAT_FORECAST_MAX_HOURS`, the DHW suppression's pattern), a
> linear fade, and the wood tank's measured sensible energy. Zero unless a
> fire is active or fading, zero on any missing/stale sensor (staleness maps
> to absence via `InputReader` and the three entities are in
> `INPUT_MAX_AGE_MINUTES` from the start), zero below a 2 K identification
> margin.
>
> **4. The tank pair, scoped to the safe direction.** A measurably spent
> tank ends the decay early; a warm one never extends it past the timer.
> Measurement may argue for less trust in a fire, never more.
>
> **Not built, by the item's own ranking:** the second heat-pump-tank
> sensor. It was rated low value and blocked on item 27; item 27 is now
> done, so re-evaluate it if stratification of the pump tank ever matters —
> but note the v3.10.0 discharge law models the pump tank as well-mixed, so
> a second probe still has nothing to change.
>
> **The learner-freeze tension flagged below still stands**: on a house that
> fires daily, the COP learner is frozen exactly when the interesting tank
> temperatures occur. Nothing in v3.11.0 changes `_learning_frozen`; if the
> flow-temperature COP term ever needs validating on this house's own data,
> that freeze is the first thing in the way.
>
> Two corrections to the item text, from reading the code while working on 29:
>
> - **It undercounts the consumers of `external_heat_active`.** The item says
>   "exactly one consumer". There are five, and the largest by reach is
>   `_learning_frozen`, which freezes **six** learners whenever a fire is active
>   *or fading* -- for the full 90-minute decay, not just while burning.
> - **That creates a conflict worth planning for.** On a house that fires
>   regularly -- exactly this topology -- the COP learner is frozen precisely when
>   the interesting tank temperatures occur. Fitting anything from this house's
>   own data is therefore partly blocked by this item's own detector.
>
> Also note `confidence` on `ExternalHeatState` must **not** be repurposed as the
> displacement factor. It is continuous in type but means "how recently", not
> "how much": `_activate` sets it to exactly 1.0 regardless of fire intensity and
> `_decay` overwrites it on every non-confirming sample. Add a separate field.
>
> And `tests/backtest.py` cannot represent a fire at all today:
> `external_heat_active` is a scalar bool on the *initial state*, not a per-step
> array, and `simulate_trajectory` has no free-heat injection input. Sizing this
> item needs a per-step `external_thermal_kw` threaded through the model, which
> is a bigger harness change than anything item 29 needed.


Asked by the user, 2026-08-23: *"I have a wood furnace heating a separate buffer
tank. Water from both tanks is mixed by an automatic valve, wood prioritised,
gradually switching to 100% heat pump tank as the wood tank cools. I have a
sensor after the mixing valve, and top and bottom sensors in both tanks. Can the
three additional sensors improve the model?"*

**Short answer: yes, and the value is very unevenly spread — most of it is in
the mixing valve outlet sensor. But item 27 is a prerequisite for part of it.**

**What exists today.** There is already an external-heat feature (original item
5, `external_heat.py`, `CONF_EXTERNAL_HEAT_ENABLED`, off by default). It infers
a fire from a temperature rise faster than `min_rise` °C/h and sets a single
boolean, `ThermalState.external_heat_active`. That boolean has **exactly one
consumer**: `optimizer.py:1905`, which suppresses *discretionary hot water* for
at most 2 hours while coasting still meets the requirement. It does nothing
whatsoever for space heating, and it decays on a fixed 90-minute timer
(`DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES`). So today the furnace is detected, and
then almost entirely ignored.

Ranked by value:

**1. Mixing valve outlet — high value, and the one to do first.** This is the
only sensor that measures what the *house* actually receives. The model has no
such observation at all: delivered heat is computed as `cop × electrical_power`
split by a fixed `radiator_power_fraction`, an open-loop guess. Combined with
the two tank temperatures the outlet temperature identifies the valve's mixing
fraction, and that turns the binary `external_heat_active` into a continuous
0–1 *displacement factor*: "the furnace is currently covering 70 % of space
heating load". That is the missing quantity, and it is what would let the
optimizer defer electric space heating during a burn — which it cannot do at
all today. Everything else here is refinement; this is the step change.

**2. Wood tank top and bottom — medium value, and they must be used as a
pair.** The top–bottom *spread* is a stratification signal and therefore a
proxy for remaining stored energy: a hot top over a cold bottom means the charge
is nearly spent even though the top sensor still reads high. That converts
reactive suppression into a short forecast — "this fire is good for about
another 90 minutes" — replacing the fixed 90-minute decay constant with a
measured one. Note the fixed constant is currently doing this job by assumption,
so this is a replacement, not an addition.

**3. Second sensor in the heat pump tank — low value today, and blocked.** It
would give the same stratification signal for the pump's own tank, but that tank
is not a store in the model at all (**item 27**), so a better estimate of its
contents cannot change any decision. Do item 27 first or skip this sensor.

**Design constraints that must not be lost:**

- **Wood firing is human behaviour, not weather.** When the user lights a fire
  is not forecastable and must never be predicted. Only the *decay of an
  already-lit fire* is forecastable. Any model that learns "he usually fires at
  18:00" and pre-emptively withholds heat is wrong even when the average is
  right.
- **The failure is asymmetric, and the existing code already knows this.** The
  comment at `optimizer.py:1913` is explicit: running out of hot water because a
  fire was assumed to keep burning is the failure mode the detector is
  deliberately biased against. Extending this to space heating raises the stakes
  — a wrong bet there is a cold house, over hours, in winter. Keep the bias:
  displacement should be believed only for as long as the measured tank can
  still back it, and should degrade to zero rather than persist on assumption.
- **Soft penalties, again.** Comfort limits are penalties in the objective, not
  hard constraints, so an over-optimistic displacement estimate will not be
  refused by the solver — it will be accepted at a small modelled cost and a
  large real one. Same trap as the manual-plan safety work in v3.2.0.
- **Sensor staleness matters more here than elsewhere.** A stalled tank sensor
  reading a hot value would look like an indefinite free fire. These belong in
  `INPUT_MAX_AGE_MINUTES` (`const.py:111`) from the start, not later.

**Scope honestly.** This is a config-flow expansion (three optional entities), a
state-vector expansion, a new estimator for the displacement fraction, and a
change to how space heating demand is computed. It is the largest item in this
backlog by some margin and it is worth its own session — probably its own
release. It is also only useful to users with this topology, so it must follow
the existing external-heat precedent and **default to off**: as `const.py:130`
puts it, a feature that cannot save them anything should not be able to cost
them anything either.

**Before building any of it, check the payoff is real.** The user fires
regularly enough for this to matter, but the size of the win depends on how much
of the season the furnace actually covers. `tests/backtest.py` against a period
with known burns would size it. If the furnace covers most of the winter load,
the optimizer's remaining electric decisions are small and so is the saving —
which is worth knowing before, not after.

## 29. The buffer tank as a controllable thermal battery (mixing valve setups)

> ## Status, 2026-08-24 (v3.10.0): the optimizer charges. Done except
> ## `smart_write`.
>
> The discharge law prescribed by the audit is implemented. The valve is
> modelled as what it physically is — a flow-temperature regulator on a
> weather-compensation curve, derived rather than configured: the flow that
> holds the house at the target is the target plus the standing loss over the
> emitter UA. The emitters see `min(tank, curve)`, never raw tank water, so
> stored heat leaves at house-demand rate (a 60 °C tank now carries the house
> ~6 h at −5 °C where it previously relaxed to the curve within two steps),
> the tank's end state depends on the plan, and the terminal credit has the
> gradient it was starving for. `delivery_demand()` and its per-step gain are
> gone — the effective P-gain is the emitter UA itself, in kW/K, dt-invariant
> by construction. The user confirmed the framing independently: the valve
> must be modelled capped at the max-comfort setting, not fully open.
>
> **Measured behaviour.** Against a tank too cold to coast for free the
> optimizer saturates the cheap night block (30 kWh at 6 kW), lifts the tank
> deliberately, coasts a 4.80 morning *and* a 7.40 evening peak with zero
> purchases, and re-buys at the late-evening dip. At flat prices the
> concentration vanishes — the null control. Against a tank that starts warm
> enough to coast anyway it declines to charge, and that is correct: there is
> nothing to displace, and a hand-built charge-harder plan scores worse on
> the optimizer's own objective. Do not re-open "it will not charge" on a
> fixture whose tank starts at 40 °C.
>
> **Sizing, measured in `tests/backtest.py` with the flat-price null
> subtracted** (two more measurement traps fell in this session and are
> recorded in that file's storage section: valve-vs-none confounds comfort
> exposure, big-vs-tiny tank confounds COP pass-through spikes; both are
> price-independent, so differencing against flat removes them): at 750 L,
> ~+5 SEK/day on winter_typical, ~+17 on winter_extreme. Smaller than the
> analytical table below, and the gap is physics, not a bug: **a fixed-curve
> valve cannot hold charge for the peak** — the tank feeds the house the
> moment it is warmer than the curve, so it mostly shifts the hours right
> after charging. The analytical table assumed dispatchable delivery, which
> only `smart_write` can provide. That is now the value case for
> `smart_write`, not just a convenience.
>
> **Also in v3.10.0:** `buffer_max_temp` is a hard constraint in the solve
> (tighten-and-re-solve on the steps whose heat the cap refused — the model
> records `last_buffer_refused` beside the trajectory; tested at effectively
> free electricity, where deleted heat costs nothing and only the hard
> constraint stands between the solver and a boiled tank). The dumb-valve
> recommendation is surfaced as the Valve Target Recommendation diagnostic
> sensor. The tank size threshold landed in item 27.
>
> **The one-sided deferred-energy settlement** (audit deferred finding 2) was
> evaluated and left alone: it shapes the *reported savings*, not the plan —
> the objective's terminal cost prices every degree below the cap, so the
> charging gradient never depended on it. Revisit only if reported savings on
> a storing house look systematically low.

> ## Status, 2026-08-23 (v3.7.1). Read this before the item text.
>
> **Shipped.** The mixing valve and its control law (v3.7.0), the buffer tank's
> standby loss (v3.6.1), the Carnot COP flow-temperature term (v3.7.0), and the
> optimizer's ability to see stored tank heat (v3.7.1).
>
> **The headline goal is not met: the optimizer still does not deliberately
> charge the tank.** Everything below is either a step towards that or a thing
> ruled out on the way.
>
> ### The three blockers this item recorded
>
> **Blocker 1 -- no valve, so surplus cannot reach the tank. FIXED (v3.7.0).**
> `mixing_valve.py` holds the control law: delivery is what the house asks for,
> and the surplus goes to the tank. Measured at 750 L over 6 h at -5 C with a
> 23 C target: at 9 kW the tank charges 45 -> 70 C (its cap) while the house is
> held at 23.2 C. Without a valve the same power leaves the tank at 44.2 C
> regardless and drives the house to 30.3 C instead. Modes shipped: `none`
> (default, unchanged), `manual`, `smart_read`.
>
> **Blocker 2 -- standby loss wrong by 30x for a large tank. FIXED (v3.6.1).**
> UA follows surface area (volume^(2/3)), so the cooling rate falls as
> volume^(-1/3). Both the prior and the learner's clamp are now derived from tank
> geometry and a plausible insulation range, so a real accumulator (~2 W/K at
> 750 L) is reachable instead of floored around 17 W/K.
>
> **Blocker 3 -- seeding. MISDIAGNOSED.** `_price_ranked_start` does budget
> exactly baseline energy, and that is *not* what stops charging. Measured on the
> same objective, a storage-aware seed, a double-capacity seed and full power
> throughout all descend to the same plan as the existing seeds: 88.49 / 88.66 /
> 89.23 / 88.75. Adding seeds changes nothing.
>
> **Two real defects were found in its place, both fixed (v3.7.1):**
>
> - The tank was credited against the *slab's* settlement cap. With a slab
>   ceiling near 28 C, charging 45 -> 70 C was credited with **0.0 kWh of the
>   21.8 kWh actually stored**. The tank now has its own cap. The slab cap exists
>   to stop passive overheating counting as charge; that reasoning does not
>   transfer to a tank that only gets hot deliberately and cannot overheat
>   anything through the valve.
> - The objective's terminal cost never saw the tank at all. `_terminal_cost`
>   listed upper, lower and slab; `simulate_trajectory` computed the buffer
>   trajectory and discarded it. So charging was pure cost with no modelled
>   benefit *whatever the cap said* -- fixing the cap alone would have achieved
>   nothing.
>
> Both are measurable: plans now end with the tank at 26-28 C instead of 18-21 C.
> Both are gated on a valve existing, so golden is unchanged.
>
> ### Still unexplained
>
> The tank never charges above its starting temperature. Ruled out: seeding,
> settlement caps, terminal cost, comfort headroom (checked down to a 0.2 K
> band), weather (winter_cold / winter_mild / shoulder), price profile
> (winter_typical / winter_extreme), and pump capacity. Charging is physically
> reachable -- sustained full power takes the tank to 60.8 C -- so the optimizer
> is choosing not to.
>
> Suggested next step, which is a different kind of investigation from the ones
> already run: instrument the objective's gradient with respect to power at the
> chosen operating point and find which term opposes the terminal credit.
>
> **A retracted claim.** Limited pump capacity was blamed at one point, on the
> basis that at -12 C the fixture's 6 kW pump gives 9.4 kW thermal against a
> 6.7 kW house load. Pump capacity is configurable and 14 kW is ordinary
> (the user's own). Re-tested at 14 kW the tank still never charges.
>
> ### Answered (audit, 2026-08-23): the discharge law is why
>
> The audit ran the gradient instrumentation suggested above and found the
> answer, in two parts.
>
> **Part one — FIXED (v3.8.0).** With no valve target configured the
> fallback target was `house_temp + 1.0` — a *receding* target. As the house
> warms toward it, it moves up in step, so delivery never falls below demand
> and the surplus never diverts to the tank. The default target is now the
> comfort ceiling (`ThermalParameters.comfort_ceiling`), which is what
> `recommend_target()` recommends and what makes a dumb valve store at all.
>
> **Part two, still open, and the real answer.** The model *discharges* the
> tank with the valve wide open at the raw tank temperature: emitter delivery
> is computed from the tank temperature itself, not from the mixed flow
> temperature the valve produces. A 40-45 °C tank against 21 °C rooms then
> dumps on the order of 26 kW, so anything the plan stores is gone within a
> step or two of the pump stopping — and, decisively, the tank's end state is
> nearly plan-independent: every candidate trajectory relaxes to the same
> discharged tank well before the horizon ends. The terminal credit therefore
> has ~zero gradient with respect to charging power, and L-BFGS-B correctly
> concludes that charging buys nothing. The optimizer is not refusing to
> charge; the model is telling it storage does not work.
>
> **Suggested fix.** Bound discharge by what the emitters can actually accept
> at the *mixed* flow temperature — `q_discharge ≤ emitter_output(T_mix)`,
> with `T_mix` set by the valve target — so stored heat leaves the tank at
> house-demand rate, survives to the terminal state, and the credit gets a
> gradient. While in there, make the valve P-gain dt-invariant: the current
> `DEFAULT_VALVE_GAIN = 0.5` closes half the remaining gap per *step*, so the
> effective control bandwidth silently changes with `time_step_minutes`;
> express it per hour instead.
>
> ### Outstanding pieces of this item
>
> - **`smart_write` mode.** Not shipped: it needs an actuation path to command
>   the valve's controller. A mode that cannot do what its name says is worse
>   than one that is absent, and adding the option later needs no migration.
> - **The dumb-valve recommendation is not surfaced.**
>   `mixing_valve.recommend_target()` computes it and explains the trade-off, and
>   nothing calls it. The item asks for the integration to *recommend* a setting;
>   right now it can and tells nobody. A diagnostic sensor is the obvious home.
> - **`buffer_max_temp` is not a hard constraint in the solve.** It clamps the
>   model and caps the settlement, but this item is explicit that it must not be
>   a soft penalty and should follow the `_SAFETY_REPAIR_ROUNDS`
>   release-and-re-solve pattern. It does not yet. Latent while nothing charges;
>   a real hole the moment that changes. Note the existing loop only ever
>   *relaxes* bounds and the pin encoding cannot express "cap this step".
> - **Empirical sizing.** Deferred to after implementation, and still blocked on
>   the charging problem. `tests/profiles.py` gained `winter_moderate` (0.51) and
>   `winter_narrow` (0.70) so that a future measurement straddles the 0.75
>   break-even instead of sitting far inside it like every other profile.
>
> **Sizing spike, 2026-08-23. Read this before the item text — it corrects two
> things below and answers the "measure before building" question.**
>
> **The feature pays, and by a lot.** Storing 1 kWh thermal cheap and delivering
> it at peak is worth `p_peak/COP_deliver − p_cheap/COP_charge`. With a
> Carnot-derived flow-temperature COP term and realistic tank insulation:
>
> | profile | cheap:dear | SEK/kWh_th | 750 L/day | 2000 L/day |
> |---|---|---|---|---|
> | winter_extreme | 0.12 | 3.37 | **+75.7** | +201.8 |
> | winter_typical | 0.22 | 1.10 | **+24.7** | +65.8 |
> | winter_moderate | 0.51 | 0.32 | +7.1 | +18.8 |
> | winter_narrow | 0.70 | 0.07 | +1.5 | +4.1 |
> | flat | 1.00 | −0.22 | **−5.0** | −13.2 |
>
> A typical winter day costs ~145 SEK in these fixtures, so 750 L is worth
> **~17 %** on a typical day. Break-even is a 0.75 price ratio. Flat prices come
> out **negative**, which is the null control passing.
>
> **Three blockers, each of which alone makes the gain exactly zero:**
>
> 1. **Decoupling the draw is not sufficient — the valve is the feature.**
>    Measured with a demand-driven draw and no valve: the optimizer used **0.00 K
>    of 30 K** of headroom and the two arms produced **byte-identical** power
>    schedules. With the tank at 40 °C and zones at 21–25 °C, emitter demand is
>    ~23 kW against ~15 kW of pump output, so the tank always drains. What sends
>    surplus to the tank is the valve *throttling delivery to what the house
>    needs*.
> 2. **The standing-loss default is wrong by 30× for a large tank.**
>    `DEFAULT_BUFFER_COOLING_RATE` = 6.0 °C/h is tuned for 35 L. At 750 L that is
>    **43.8 kWh lost from a 26.1 kWh charge (168 %)** and the sizing lands at
>    exactly **0.0 SEK/day** — the feature appears worthless. Worse,
>    `BUFFER_COOLING_RATE_MIN = 0.5` **clamps** the learner, so a well-insulated
>    accumulator (~0.2 °C/h) cannot be represented at all. The clamp must scale
>    with volume.
> 3. **The optimizer cannot seed a charging plan.** `_price_ranked_start` budgets
>    exactly `baseline_energy`, the energy a thermostat would use, while charging
>    means buying *more* than baseline. None of the three seeds can express it.
>
> **A correction to the "three valve modes" section below.** It says target high
> → valve open → the tank cannot charge. That holds only *while the house is
> below target*. Set the target at the maximum permitted temperature and the slab
> charges first; once it reaches the ceiling the valve throttles and surplus goes
> to the tank — **both stores, cheapest first**. So mode 2 deserves real logic,
> not just a recorded number.
>
> **Three ways the measurement went wrong, recorded so they are not repeated.**
> Every sizing claim here needs a **null control at flat prices**; treat a
> missing one as a bug.
> - *Confounded A/B*: planning one arm against today's model and scoring both
>   under chargeable physics measures model-mismatch, not storage — it reported
>   a **20 % gain at flat prices**.
> - *Unfair baseline*: a no-tank arm that buys full power and discards the
>   surplus lets the tank "win" by recovering waste — **6.9 % at flat**.
> - *A heuristic is not an optimizer*: a fixed "charge in the cheapest 35 %" rule
>   charges constantly at flat prices and loses **37.6 %**.
>
> **So empirical sizing is blocked on the feature existing.** The analytical
> table above is the go/no-go; the backtest comparison moves to *after*
> implementation, with the real optimizer.


Raised by the user, 2026-08-23: *"A setup with such a mixing valve means during
cheap hours the heat pump buffer tank can be charged if economically feasible —
the outgoing heat to the house is limited by the automatic mixing valve if the
house is already too warm. Can capabilities be introduced to support this?"*

**The insight is correct and it identifies the missing physics precisely.**
Item 27 records that the model hard-wires draw to equal supply
(`q_rad_from_buf + q_floor_from_buf == thermal_power` identically), so the tank
cannot charge. That identity is a fair model of a system with no valve, where
whatever the pump makes goes straight to the emitters. **A mixing valve is
exactly the component that breaks it**: the valve throttles delivery to what the
house is asking for, and the surplus has nowhere to go but the tank. So in this
topology the decoupling item 27 asks for is not an approximation — it is what
the hardware actually does.

**The scope is smaller than it looks: no new control variable is needed.** The
optimizer already decides electrical power per step. Once draw is demand-driven
rather than supply-driven, charging is an *emergent* consequence — run the pump
above the house's demand and the tank temperature rises. There is no need for a
second decision channel or a "charge tank" mode. The work is in the model and
the constraints, not in the optimizer's decision vector.

Three things are needed:

1. **Decouple the draw** (item 27). House demand from the emitter/zone side, pump
   output from the compressor side, tank absorbs the difference.
2. **A COP that depends on flow temperature** — see the blocker below.
3. **A maximum tank temperature as a real constraint** — see the trap below.

### Blocker: space-heating COP has no flow-temperature term at all

`compute_cop(outdoor_temp, humidity)` (`thermal_model.py:547`) is a function of
outdoor temperature only. There is no supply-temperature dependence anywhere in
it. Only DHW has one, in `compute_cop_dhw` (~577), as
`1.0 - 0.008 * (dhw_temp - 35)`.

**This must be fixed before the tank is made chargeable, or the feature will be
actively harmful.** With a flow-temperature-independent COP, the optimizer sees
storing heat at 70 °C as costing exactly the same per kWh as delivering it at
35 °C. Storage would appear free, and it would charge the tank to whatever cap
exists, on every cheap hour, regardless of whether it pays.

The entire economics of a thermal store is this penalty against the price
spread. Break-even price ratio — how cheap the cheap hour must be relative to
the expensive one, purely to pay back the COP loss, before standing losses:

| flow temp lift | at code's 0.8 %/K | at a realistic 2 %/K | at 2.5 %/K |
|---|---|---|---|
| 10 K | 0.92 | 0.80 | 0.75 |
| 15 K | 0.88 | 0.70 | 0.62 |
| 20 K | 0.84 | 0.60 | 0.50 |
| 25 K | 0.80 | 0.50 | 0.38 |
| 30 K | 0.76 | 0.40 | 0.25 |

A 20 K lift needs the cheap hour at or below **60 %** of the expensive hour just
to break even. Nord Pool days like that exist but are not the majority, so this
is a genuinely marginal trade that the model must get right to call correctly —
it is not a case where a rough approximation lands on the right answer anyway.

Note also that **0.8 %/K is probably too gentle to borrow**. Real air-source
units lose roughly 2–2.5 % of COP per K of condensing temperature. Reusing the
DHW coefficient would systematically over-encourage storage. Prefer a
Carnot-derived term over another fitted constant, and validate it against
measured input power, which the codebase already collects for `cop_scale`.

### Trap: maximum tank temperature is a state-dependent constraint

The tank cannot be charged past its safe temperature, and that limit depends on
the state trajectory, not just on the decision variable. **Do not express it as
a penalty in the objective.** This is the exact lesson from v3.2.0: comfort and
tank limits are soft penalties, so the solver does not refuse a violation, it
accepts it at a modelled cost that is much smaller than the real one. A soft cap
here means the optimizer will happily plan to boil the tank. The existing tool
for this is the post-solve release-and-re-solve loop used for safety
(`optimizer.py` `_SAFETY_REPAIR_ROUNDS`, ~325); follow that pattern.

### Sizing: this depends entirely on tank volume, and the default is pointless

`DEFAULT_BUFFER_TANK_VOLUME` is 35 L, giving `C_buf` = 0.041 kWh/K — about
**1 kWh** over a 25 K span, well under twenty minutes of output. For the default
config this feature is not worth having, which is consistent with the comment at
`const.py:381` that a buffer tank holds very little water. Real accumulators are
a different matter:

| volume | kWh/K | usable over 25 K | over 40 K |
|---|---|---|---|
| 35 L | 0.041 | 1.0 kWh | 1.6 kWh |
| 300 L | 0.348 | 8.7 kWh | 13.9 kWh |
| 500 L | 0.580 | 14.5 kWh | 23.2 kWh |
| 1000 L | 1.160 | 29.0 kWh | 46.4 kWh |
| 2000 L | 2.320 | 58.0 kWh | 92.8 kWh |

**But measure the gain against the slab, not against zero.** `slab_thermal_mass`
defaults to **5.0 kWh/K**, so a 3 K slab swing is **15 kWh** — equal to a 500 L
tank over a 25 K span. The slab is already used as a store by the existing
pre-heating strategy, and it stores at roughly 22–26 °C, which carries **no COP
penalty at all**. Thermodynamically, pre-heating the slab beats charging a
buffer tank, and the optimizer already does it.

So the buffer tank's value is not raw capacity. It is that it stores **without
touching indoor temperature** (no comfort cost, so it can be used on days when
the slab strategy is constrained by the comfort band) and that it charges and
discharges **fast**. Those are real advantages, but they make the marginal gain
over today's behaviour considerably smaller than the kWh table suggests. Size it
with `tests/backtest.py` before building, comparing against the current slab
strategy rather than against a do-nothing baseline.

### Gotcha: the standing-loss clamp is tuned for a small tank

`BUFFER_COOLING_RATE_MIN` is **0.5 °C/h** (`const.py:387`), a sensible floor for
a 35 L tank and far too high for a well-insulated accumulator, which loses more
like 0.2 °C/h. Over an 8-hour shift on a 1000 L tank that is 4.6 kWh of modelled
loss against a real 1.9 kWh — roughly triple, applied directly against the case
for storing. The clamp would quietly bias the optimizer away from the feature
being built. Relax it as part of supporting large tanks, and make sure the
learned cooling-rate estimator is allowed to reach the true value.

### The wood tank is a store too, but a fundamentally different one

The user is right that the wood tank stores energy and that its two sensors
reveal the state of charge (see item 28 on stratification). **But the heat pump
cannot charge it** — the furnace fills it and the priority valve only draws from
it. It is an *observable* store, not a *controllable* one.

Keep these two firmly apart in the design, because conflating them is an easy
and expensive mistake:

- **HP tank — a controllable store.** Enters the optimizer as state that the
  decision variable can move. Needs everything above.
- **Wood tank — an observable store.** Enters as a *disturbance*: a forecast of
  free heat that reduces predicted electric demand over the next few hours. It
  is never a scheduling target, and the optimizer must never plan to "use" it,
  only to expect it and stand down accordingly.

The asymmetry warning from item 28 applies with full force to the wood tank
half: over-estimating stored wood energy means standing down the heat pump
against heat that is not there, and the failure is a cold house hours later.
Believe the wood tank only as far as its measured contents and a conservative
decay, and let the estimate fall to zero rather than persist on assumption.

### Making it optional, and the valve's own target temperature

**Optionality is straightforward and there is clear precedent.** Three existing
features are already switched this way: `CONF_EXTERNAL_HEAT_ENABLED` (defaults
off), `two_zone_enabled` (swaps the whole thermal model), and the ECL110
integration (inert unless MQTT topics are configured). Follow that: an optional
entity plus a boolean, defaulting off.

The important part is **what the fallback is**. Item 27 calls the
`draw == supply` identity a bug, and for a valve-less system it is not — with no
valve, whatever the pump makes does go straight to the emitters. So this is an
added branch, not a replacement, and the current behaviour must stay the default
path. Do not "fix" item 27 by making every install storage-capable.

**The valve's target temperature: necessary, not optional — and it changes what
the valve is.** The user notes the valve is controlled by *indoor* temperature,
regulating to a target. That makes it a closed-loop controller on the house, and
it cuts both ways:

- It **confirms the charging story**. Running the pump above demand cannot
  overheat the house, because the valve throttles to hold the target. The
  surplus goes to the tank. That is exactly the decoupling item 29 relies on.
- It **disables the existing slab strategy**, which is the part that is easy to
  miss. Today's optimizer saves money largely by deliberately over-heating the
  house within the comfort band during cheap hours, storing ~15 kWh in the slab
  at no COP penalty. A valve holding indoor temperature at a fixed target will
  *actively prevent* that. The optimizer would plan a pre-heat, the valve would
  refuse it, and the plan would silently fail — while the model went on
  believing it had banked the heat.

That second point is the real design conclusion: **in a valve-controlled house,
the valve's target is the actuator for house pre-heating.** Read-only is not
enough. Without write access the optimizer can only store in the tank, and would
lose the larger, cheaper store to keep the smaller, dearer one — the exact wrong
trade given the slab/tank comparison above.

So both directions are wanted, for different reasons:

- **Reading the target** tells the model when the valve is throttling versus
  wide open. That boundary decides whether surplus heat can go to the tank at
  all, so charging cannot be planned without it.
- **Writing the target** is what keeps the slab strategy alive. Raise the target
  to pre-heat, lower it to coast.

**There is already a template for this in the codebase.** The ECL110 support is
the same shape of problem: a commanded parallel shift of a shunt controller's
curve (`CONF_ECL110_DISPLACE_SET_TOPIC`), clamped by
`DEFAULT_ECL110_DISPLACE_MIN`/`MAX` (−20/+20 °C), with the controller's lag
approximated by `DEFAULT_ECL110_PID_TIME_CONSTANT` (1.5 h) and tracked as
`ecl110_displace_command` vs `ecl110_effective_displace` — commanded versus
actually-in-effect. Reuse that structure rather than inventing a second one.

**Two cautions that the ECL110 work already implies.** The valve runs its own
closed loop, so two controllers are now acting on one house and can fight; the
commanded-vs-effective split and the time constant exist precisely to model that
lag, and a valve target written without them will oscillate. And if the valve
enforces comfort itself, the optimizer's comfort penalty is partly redundant —
be careful not to double-count, or the plan will be far more conservative than
either mechanism alone intends.

### Three valve modes, including "dumb" valves held deliberately high

Requested by the user, 2026-08-23. Support both an actuated valve and a fixed
one, with a recommended setting for the fixed case.

**Model it as three modes, not a boolean:**

1. **`none`** — no valve. Today's behaviour and the default. The
   `draw == supply` identity of item 27 is *correct* here; do not change it.
2. **`fixed`** — a "dumb" valve the integration cannot write. The user sets the
   target once in the valve's own controller and tells the integration what it
   is.
3. **`actuated`** — the integration writes the target, via the ECL110 pattern
   described above.

**The user's insight about mode 2 is the interesting one, and it is sound.** Set
the fixed target deliberately high and the valve saturates wide open. It then
stops regulating, delivery follows supply again, and the house becomes heat-pump
controlled — which restores the slab pre-heating strategy that a
regulating valve would otherwise defeat. **In that saturated regime today's
model is already right**: `draw == supply` is exactly what a wide-open valve
does. That is worth knowing before writing code, because it means mode 2 needs
far less new physics than mode 3 — mostly it needs to know *when* saturation
ends.

**The trade the recommendation has to resolve.** The two storage strategies are
in direct competition through this one setting:

- **Target high** → valve open → heat goes to the house → the slab charges
  (~15 kWh at a 3 K swing, stored at 22–26 °C, **no COP penalty**), but the tank
  cannot charge because nothing is being held back.
- **Target low** → valve throttles → surplus charges the tank (14.5 kWh at
  500 L over 25 K, but paid for with the COP penalty in the table above), while
  the slab strategy is disabled.

Given those numbers the recommendation will, for most houses, come out **high**:
prefer the slab, and let the tank take the overflow only once the comfort band is
exhausted. Do not assume it always does — the tank wins when the comfort band is
narrow, when the house is already at its ceiling, or when the user wants load
shifted without touching indoor temperature at all — but expect "high" to be the
common answer and treat a recommendation of "low" as something to explain.

**It is a real optimum, not "as high as possible".** Both ends cost something:

- Too low: the valve throttles during planned pre-heating, so the plan silently
  fails to materialise.
- Too high: the valve stops protecting against overshoot. On a mild day, or
  after a forecast miss, nothing throttles and the house runs away.

So the recommended value is roughly *the flow temperature that meets the design
heat load at the design outdoor temperature, plus enough headroom to charge the
slab across the comfort band, and no more*. That is computable from parameters
the integration already has — the zone `u` values, the comfort band and the
outdoor forecast — so **the recommendation needs no new sensors**. Surface it as
a diagnostic sensor and in the card, and recompute it as coefficients are
learned (item 31), since a recommendation derived from preset priors is only as
good as the priors.

**State the safety consequence plainly in the UI.** In mode 2 with a high
target, the valve was the safety net and the user is being advised to remove it.
Afterwards the only thing standing between a solver mistake and an overheated
house is the optimizer's own comfort handling — which is a **soft penalty**, so
it does not refuse violations, it prices them. That is the same asymmetry that
bit the manual-plan work in v3.2.0. The recommendation should therefore be
conservative by default, and the mode should be opt-in with the trade-off
spelled out rather than presented as free savings.

**Config surface:** `CONF_MIXING_VALVE_MODE` (`none` / `fixed` / `actuated`,
defaulting to `none`) and `CONF_MIXING_VALVE_TARGET` for mode 2. Mode 3 reuses
the ECL110 topic/clamp/time-constant keys rather than duplicating them. In mode
2 the model must also detect *de-saturation* — when the tank or flow temperature
drops far enough that the valve starts regulating again, delivery stops
following supply and the model has to switch branches. That transition is the
one piece of genuinely new dynamics mode 2 needs.

## 30. An optional real lower-floor temperature sensor (two-zone)

Asked by the user, 2026-08-23: *"Today the model takes indoor temperature from
the top floor and infers the bottom floor from the slab return temperature.
Would an option for a real bottom-floor sensor improve the model or the
learning?"*

**Yes, clearly, and by more than the phrasing suggests — the current inference
is not a slightly noisy estimate, it is structurally wrong in two ways.**

`coordinator.py:2113` sets

```python
self._current_state.lower_floor_temperature = self._floor_return_temp + 0.5
```

while `update_slab_from_return_temp` (`thermal_model.py:1267`) sets the slab from
the *same* sensor as `return_temp + 1.0`.

**Error 1: the lower zone's room temperature is a water temperature.** A floor
circuit returns at roughly 24–30 °C while the room it serves sits at ~21 °C. So
the model believes the lower floor is 3–9 K warmer than it is. That value is not
merely informational — it goes straight into the comfort penalty
(`optimizer.py:718–736`), judged against the same `temp_min_bounds`,
`temp_max_bounds` and `comfort_targets` as the upper floor. The lower zone
therefore reads as permanently overshooting, which biases the optimizer toward
under-heating the very zone it cannot see.

**Error 2: slab-to-room transfer carries no information at all.** Because both
values come from one sensor with fixed offsets, their difference is *always*
0.5 K, whatever the sensor reads:

| return temp | slab = r+1 | lower = r+0.5 | ΔT | q_slab_to_lower |
|---|---|---|---|---|
| 24 °C | 25.0 | 24.5 | 0.5 K | 0.400 kW |
| 28 °C | 29.0 | 28.5 | 0.5 K | 0.400 kW |
| 32 °C | 33.0 | 32.5 | 0.5 K | 0.400 kW |

`q_slab_to_lower` is pinned at a constant 0.400 kW. In a real house with the
slab at 27 °C and the room at 21 °C it is `0.8 × 6.0 = 4.8 kW` — **12× larger**.
The main heat path into the lower zone is both wrong and unresponsive.

**And the error does not wash out over the horizon.** Measured with the real
model, two-zone, 2 kW electrical, −5 °C outdoor, 24 h:

| lower-zone seed | after 24 h |
|---|---|
| 21.0 °C (true sensor) | 23.60 °C |
| 28.5 °C (inferred from a 28 °C return) | 26.62 °C |

A 7.5 K seeding error is still **3.02 K** at the end of the horizon — only 60 %
decayed. The lower zone's standalone time constant is 114 h
(`C_lower / u_lower` = 8.0 / 0.07); inter-zone and slab coupling speed that up,
but nowhere near enough to make the initial condition stop mattering. Every step
of a 24-hour plan is computed against a wrong lower-zone temperature, and the
early steps — the ones that actually get executed before the next re-solve — are
the most wrong.

**Effect on learning, which is the sharper half of the question.** Any learner
that attributes observed behaviour to `slab_heat_transfer`, `inter_zone_transfer`
or `lower_floor_heat_loss` is fitting against a fabricated target. With ΔT
clamped at 0.5 K, a fitted `slab_heat_transfer` must inflate by roughly an order
of magnitude to reproduce the real heat flow — absorbing the offset into a
coefficient that then means nothing physical and cannot transfer to any other
operating point. **Check what is actually being learned before assuming this is
happening**, but if those coefficients are fitted, this sensor is a prerequisite
for the fit being meaningful rather than merely an accuracy improvement.

**Implementation is small.** A new optional `CONF_LOWER_FLOOR_TEMP_ENTITY`
alongside `CONF_INDOOR_TEMP_ENTITY`, read in the same block, with the existing
`return_temp + 0.5` retained as the fallback when it is absent. Add it to
`INPUT_MAX_AGE_MINUTES` (60 minutes, matching the indoor sensor). Note that the
fallback path at `coordinator.py:2202` — used when there is no floor return
sensor at all — sets `lower_floor_temperature = room_temperature`, which is
*more* defensible than the return-temp path; a real sensor should take
precedence over both.

**Expect golden-test churn, and read it rather than re-baselining.** This
changes plan output for every two-zone install with a floor return sensor. The
diffs are the evidence that the bug was real; if `tests/golden.py` comes back
empty for a two-zone scenario, the sensor is not actually being consumed.

**Cheapest item in this cluster and the best evidence-per-effort.** Unlike 27,
28 and 29 it needs no new physics, no new control path and no economic model —
one optional sensor, one branch, and it makes the two-zone model honest. It is
also a precondition for trusting anything measured about the lower zone, so if
the wood-furnace cluster gets built, do this first.

**Done.** `CONF_LOWER_FLOOR_TEMP_ENTITY`, optional, two-zone only. Precedence is
real sensor > `return + 0.5` > `room_temperature`.

- **This item's test guidance was wrong, and it matters.** It says to expect
  golden churn and to treat an empty diff as proof the sensor is not consumed.
  In fact **no golden scenario reaches this code at all**: the plan fixtures seed
  `ThermalState` directly, and the coordinator captures call `_forecast_arrays`
  and `_build_data_dict` but never `_update_current_state`. The only fixture that
  moved was `config_flow.json`, from the new schema field. An empty plan diff was
  the expected result.
- **So the evidence had to be built.** `tests/features.py` gained a section that
  drives the real coordinator's `_update_current_state` against `FakeHass`
  states -- the first test in the suite to exercise the sensor-to-state path at
  all. Nine checks: precedence, both fallbacks, an unavailable sensor, a stale
  sensor, and the staleness-table registration.
- **Two of those checks converge the slab first, deliberately.** The
  `update_slab_from_return_temp` merge is 0.7 sensor / 0.3 prior, so the
  `return + 1.0` fixed point takes several cycles. A single-cycle assertion on
  "slab minus lower is pinned at 0.5 K" **passes for the wrong reason** and goes
  on passing with the fix reverted -- it did, until it was strengthened. Mutation
  tested: reverting the fix now fails three checks, one reporting
  `delta 0.500 (was 0.500)`.
- **Adjacent bug fixed here too.** The two branches were guarded on different
  things -- one on `floor_return.ok`, the other on the *entity* being unset -- so
  a sensor that was configured but stale or unavailable satisfied neither and
  both `slab_temperature` and `lower_floor_temperature` silently held their last
  values with nothing marking them unfreshened. Both are guarded on the reading
  now.
- Note for item 31: the item's claim that the inferred path pins slab-to-room at
  0.5 K is **confirmed and now asserted in the suite** — so the regressor really
  does have zero variance, and `slab_heat_transfer` really is unidentifiable
  without this sensor.

**This also repairs an existing learner that was silently dead.**
`_async_learn_house_heat_loss` compares `self._current_state.room_temperature`
— the *upper* sensor in two-zone mode — against `predicted_state.room_temperature`,
which two-zone builds as the **area-weighted average of upper and lower**
(`thermal_model.py:964`). Measured against the real model, one 30-minute step at
2 kW and -5 °C outdoor:

| lower-zone seed | predicted `avg_room` |
|---|---|
| 21.0 °C (real sensor) | 21.100 |
| 28.5 °C (inferred from a 28 °C return) | 24.842 |

That is a **+3.74 K structural residual** against
`HOUSE_LOSS_MAX_RESIDUAL = 1.0`, so on any two-zone house with a floor-return
sensor the learner rejected **every** sample and never learned at all — logged
only at DEBUG. Worth checking `house_heat_loss_samples` on a real install before
and after; if it was stuck near 0, that is this bug.

## 31. Learn the two-zone coupling coefficients

Asked by the user, 2026-08-23: *"If `slab_heat_transfer`,
`inter_zone_transfer` and `lower_floor_heat_loss` and related coefficients are
not learned, implement such learning."*

**Confirmed: they are not learned.** Checked against the code rather than
assumed.

Learned today (written back into `_thermal_params` by the coordinator):
`cop_scale`, `house_heat_loss_scale`, `heat_loss_coefficient` (from `sysid`),
`dhw_cooling_rate`, `buffer_cooling_rate`, `defrost_derate` and
`dhw_hourly_draw_pattern`.

**Not learned, ever:** `slab_heat_transfer`, `inter_zone_transfer`,
`upper_floor_heat_loss`, `lower_floor_heat_loss`, all three thermal masses,
`radiator_power_fraction` and `buffer_tank_volume`.

Where they come from instead: `presets.py` derives `slab_heat_transfer`,
`upper_floor_heat_loss` and `lower_floor_heat_loss` from building era and area
(a prior, never updated), and `inter_zone_transfer` is a bare hardcoded default
of 0.5 kW/°C that is not even in the presets. `sysid.py` estimates only a
*single-zone* (loss, capacity) pair, so it does not reach any of these.

**`house_heat_loss_scale` is not a substitute.** It is applied at
`thermal_model.py:611` inside `effective_heat_loss_coefficient`, which is called
for both zones — so it scales the *total* loss but cannot correct the split
between zones, and it does not touch the transfer coefficients at all.

### Item 30 is a hard prerequisite, not a nice-to-have

**Building this before item 30 would produce confidently wrong parameters.**
`slab_heat_transfer` multiplies `(T_slab − T_lower)`, and both of those come
from the same floor-return sensor. Measured, holding the return at 28 °C:

| cycle | slab (merged) | lower = r+0.5 | ΔT |
|---|---|---|---|
| 1 | 26.900 | 28.5 | −1.600 |
| 2 | 28.370 | 28.5 | −0.130 |
| 4 | 28.943 | 28.5 | 0.443 |
| 6 | 28.995 | 28.5 | 0.495 |
| 12 | 29.000 | 28.5 | **0.500** |

The merge in `update_slab_from_return_temp` has a fixed point at
`return + 1.0`, so **ΔT converges to exactly 0.5 K within about six cycles and
then stays there**, whatever the sensor reads. A regressor with no variance
identifies nothing. Worse, the only variance it has during the transient comes
from the model's *own* prior slab estimate (the 0.3 weight in the merge), so
fitting against it is circular — the learner would be regressing on its own
prediction. `slab_heat_transfer` is therefore not merely biased today, it is
close to **unidentifiable**. Do item 30 first.

### Be honest about which coefficients are actually reachable

With four states and one input, normal operation cannot identify everything.
`sysid.py`'s own docstring makes the point: normal operation gives poor
excitation, which is why passive learners take weeks and need conservative
guards. Ranked by how reachable they are:

- **`lower_floor_heat_loss` — reachable.** Once a real lower-floor sensor
  exists, the driving ΔT to outdoor varies over a wide range across a season.
  This is the one to do first.
- **`slab_heat_transfer` — reachable after item 30**, since slab and lower zone
  then come from independent measurements.
- **`inter_zone_transfer` — weakly identifiable, and probably not worth a
  passive learner.** It multiplies `(T_lower − T_upper)`, but there is one pump,
  one water temperature and a fixed `radiator_power_fraction`, so the two zones
  are driven together and rarely diverge much. Little excitation means little
  information. This is a candidate for a `sysid` step rather than passive
  fitting, and it may be honest to leave it at its prior and say so.
- **Thermal masses — need transients**, so they belong with `sysid`, not with a
  passive learner. Extending `sysid.py` to a two-zone step is the better path
  than a fifth passive estimator.

### Traps

**Collinearity with the existing global scale.** `house_heat_loss_scale`
multiplies both zone losses. Learning `upper_floor_heat_loss` and
`lower_floor_heat_loss` independently while keeping it gives three parameters
for two degrees of freedom — they will trade off against each other and drift
without ever hurting the fit. Decide explicitly which one owns the total: either
retire the scale for two-zone installs, or constrain the learned pair to
preserve their sum and let the scale carry the level.

**Reuse `_learning_frozen`, do not invent new gating.** It already fails closed
on external heat, stale inputs and flatlines (`coordinator.py:2207`), and the
reasoning in its docstring — a paused learner loses an hour, a corrupted learner
poisons a persisted parameter — applies with more force here, because these
coefficients are structural rather than a single scalar.

**Follow the existing learner conventions**: physical bounds with clamps (as
`buffer_cooling_rate` does), persistence across restarts, a sample count exposed
as an attribute, and the prior as the starting value so a house with little data
behaves exactly as it does today.

**Validate against `tests/golden.py` and `tests/rolling.py`.** A learner that
improves one-step prediction while degrading the plan is a real outcome; the
rolling harness is what catches it. Mutation-test the guards, per the reminder
below.

**Done, in the scope this item recommends.** `lower_floor_heat_loss` is learned;
`inter_zone_transfer` is deliberately left at its prior; the thermal masses are
left to `sysid`.

**How the collinearity was resolved.** This item says to decide which parameter
owns the total -- retire the scale for two-zone, or constrain the pair to
preserve their sum. Neither exactly: the two were given **separate jobs**.
`house_heat_loss_scale` owns the *level* and is fitted from the upper zone; a new
`lower_floor_loss_ratio` owns the *split* and is fitted from the lower zone.
Because the ratio does not touch the upper zone, the scale's fit is unaffected by
it -- two parameters against two independent measurements, so neither can absorb
the other's error. The ratio stays at 1.0 without a real lower-floor sensor, so
nothing changes for an install that does not have one.

**A prerequisite this item does not mention, and it is a real bug.**
`_async_learn_house_heat_loss` compared `observed` -- the indoor sensor, which in
two-zone mode is the *upper* floor -- against `predicted_state.room_temperature`,
which two-zone builds as the **area-weighted average of both zones**. Measured
against the real model at 2 kW and -5 C over 30 minutes:

| zone split | bias injected into the residual |
|---|---|
| 0.0 K | -0.10 K |
| 0.6 K | +0.15 K |
| 1.5 K | +0.53 K |
| 3.0 K | +1.15 K -- past the 1.0 K rejection threshold |

Systematic, so it did not average out: it accumulated into the learned scale,
and a house with floors 3 K apart had every sample discarded. Fixed by comparing
upper against predicted upper, with `delta_t` and the Newton step's capacity
following the same zone.

**The trap that the tests caught, and would not have without them.** The lower
zone's standalone time constant is `C/u` = 8.0/0.07, over a hundred hours, so its
temperature barely moves and the Newton step is enormous -- a residual of only
+0.12 K implies a ΔU larger than the whole coefficient, i.e. a **negative**
target. The first implementation rejected those, exactly as the house learner
does. But they are precisely the intervals where the house lost *less* heat than
predicted, while the cold-side targets stay positive and were kept -- a
one-sided learner that would ratchet upward on noise alone. The target is now
clamped rather than discarded, and the EWMA and step limit decide the speed.

**An ordering dependency worth knowing about.** `_async_learn_house_heat_loss`
overwrites `_last_house_sample` with the current state near its top, so the split
learner has to run *before* it or it compares the current state against itself
and silently never learns. There is a test asserting the order.

**Not carried over from the house learner:** the reset-on-nameplate-change hook.
`async_update_thermal_params` resets the learned scale when the underlying
coefficient is edited, but `upper_floor_heat_loss` and `lower_floor_heat_loss`
are absent from `_THERMAL_PARAM_FIELDS` entirely -- they can only be changed
through the options flow, which reloads the entry and reloads the stored ratio
against a possibly-changed nameplate. That gap already exists for
`house_heat_loss_scale`; this item did not widen it, and did not close it either.

**Golden churn was additive only:** the four `coord_*` fixtures gained the three
new attributes and nothing else moved. All 33 plan scenarios are unchanged,
which is the check that the ratio really is identity at its default.

## 32. "Easy mode": a visual setup diagram in the config flow

> **Status, 2026-08-23: planned, not built.**


Asked by the user, 2026-08-23: *"Create an intuitive easy mode in the config
flow, where a graphic element shows a stylized version of your configured setup.
House type, one/two-zone, DHW tank or not, buffer tank or not, external heat
buffer tank or not, mixing valve or not as well as all configured
sensors/entities and their placement should be visible in the graphic. Ideally,
it should be possible to configure entities and setups directly in the
graphic."*

**Why it is worth doing.** The options flow is now eleven pages of numeric
fields, and nothing anywhere shows what the integration believes your system
*is*. A user with a two-zone house, a wood furnace and a mixing valve has no way
to confirm the model matches reality short of reading `const.py`. A picture is
the shortest path to "no, my DHW sensor is on the wrong tank".

**The hard part is Home Assistant, not the drawing.** Config flows render a
`voluptuous` schema through HA's own frontend; there is no supported way to put
an interactive SVG inside one. A genuinely clickable diagram therefore means
either a **custom panel** (registered the way `frontend.py` already registers the
card) or a config-flow step that shows a *picture* with ordinary selector fields
beside it. Do not start by fighting this.

**Recommended staging.** Ship a **read-only** diagram first, rendered from a
single `describe_setup()` helper on the coordinator, and only pursue
click-to-assign once the read-only version has proved it earns its place. Most of
the value -- "is my system modelled correctly?" -- is in the read-only version.

**Almost all of the topology is already derivable, so this needs no new
configuration.** `two_zone_enabled` and `dhw_enabled` are inferred from the
presence of their settings (`thermal_model.from_config`), the mixing-valve mode
comes from item 29, and `_OPTIONAL_ENTITY_KEYS` (`config_flow.py`) is already the
canonical list of assignable entities. The diagram is a *view* of existing state.

**Build the renderer once.** Item 33 wants the same picture in the card. Two
copies will diverge the first time a sensor is added; emit one topology
description from the coordinator and let both consume it.

**A trap worth stating.** A diagram that silently omits an unconfigured sensor is
worse than no diagram, because it looks complete. Show the *slots* a setup could
have and mark the empty ones -- the point is to reveal what is missing.

## 33. The same diagram on the card, with live values

> **Status, 2026-08-23: planned, not built.**


Asked by the user, 2026-08-23: *"Add a similar graphic element to a new page in
the card, where you can view your setup and read live values off all sensors
directly in the graphic."*

Each sensor shows its current reading at its physical place: tank temperatures on
the tanks, flow temperature after the mixing valve, indoor temperatures in their
zones. This is the diagnostic view the integration currently lacks -- today the
numbers are spread across 46 sensor entities with no picture of how they relate.

**Item 26 already paid for most of the structural work.** The expanded dialog is
now a bounded flex column with a scrolling body, so adding a second page is far
smaller than it would have been against the old fixed-height layout.

**Two traps, both already recorded against item 26 and both still live:**

- **The current page becomes state that must survive a re-render.** `_maybeRender`
  rebuilds the shadow root on every plan refresh, and it has had exactly this
  class of bug before (the memoised `_runs` in v3.2.0). Decide explicitly whether
  a plan refresh resets the page.
- **A hidden page must be genuinely unrendered, not `display: none`.**
  `getBoundingClientRect()` returns zeroes for a hidden element, so
  `_timeAtClientX` would compute garbage times rather than fail, and the slot
  lanes would silently misbehave.

**Prefer static SVG over anything interactive to begin with.** The card already
hand-writes inline SVG with no build step and no dependencies; keep it that way.

## Reminders for whoever picks this up

- Run `bash tests/run.sh`, which runs everything in dependency order
  (`plan_view.py` writes `/tmp/plandata.json`, which `tests/card.mjs` reads).
  It takes over 10 minutes: the backtest, stress and golden scripts dominate.
- Python tests need `PYTHONPATH=$PWD/tests/hastub` and the repo `.venv`. The
  stub now lives in the repo, not `/tmp`, so it survives a reboot.
- Freeze the clock in any test whose meaning depends on the time of day.
  Overrides expire at the next local midnight, so "two hours from now" silently
  means 90 minutes when the suite runs at 22:30, and the assertion stops saying
  anything about the code. Both `tests/card.mjs` and `tests/manual_plan.py` had
  to be fixed for exactly this.
- Mutation-test new safety assertions: change the fix back and confirm the test
  fails. Several assertions written this session passed against the bug they
  were meant to catch until they were strengthened.
- Delete `custom_components/heatpump_optimizer/__pycache__` after source edits.
- Bump `VERSION`, `manifest.json` and `CARD_VERSION` together, and add a
  `RELEASE_NOTES.md` entry. The Lovelace resource cache-buster derives from the
  integration version, so a card change without a bump keeps serving the cached
  old file to browsers.
- Watch the merge race seen in the v2.7.0 session: PR #9 was merged before a
  later commit was pushed, so `main` briefly claimed a feature it did not
  contain. Confirm `main` actually contains the code before tagging, and verify
  the published tarball rather than the worktree.
- This worktree cannot check out `main` (the main checkout holds it), so
  `gh pr merge --delete-branch` fails at its local step even though the remote
  merge succeeded. Check `gh pr view` rather than trusting the exit code.
- After pushing a rebase, GitHub needs a moment to recompute mergeability and
  reports `UNKNOWN` until it does; `gh pr merge` fails misleadingly with
  "the merge commit cannot be cleanly created" in that window.
