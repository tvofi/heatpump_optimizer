# Heat Pump Cost Optimizer — Release Notes

## v2.7.0

### Added
- **Solar irradiance can now come from Open-Meteo.** Solar gain was only as good
  as the irradiance behind it, and most weather integrations never publish a
  `solar_irradiance` field, so for many installs the term silently evaluated to
  zero and the optimizer could not anticipate a sunny afternoon. Set *Solar
  forecast source* to `Open-Meteo` and pick the location on the map in the
  configurator. No API key or account is needed.
- **A new Solar Irradiance sensor** exposes the current value, with the full
  horizon and source diagnostics in its attributes.

### How it works
- Two endpoints are used because they do different jobs. The forecast API
  supplies the planning horizon and supports `minutely_15`, matching the
  optimizer's 15-minute grid exactly. The satellite archive supplies *current*
  irradiance: it is observed rather than modelled and current to roughly ten
  minutes, so the house heat-loss learner trains against what actually happened.
  The satellite endpoint is archive-only, with no forecast route, so it cannot
  serve the horizon by itself.
- The request is for `shortwave_radiation` (global horizontal irradiance) rather
  than `direct_radiation`. The window-gain calculation applies its own
  orientation factor, and direct-beam alone omits the diffuse component, which
  on an overcast day is essentially all the light there is.
- Open-Meteo timestamps mark the **end** of the averaging interval. This was
  verified against sunrise and sunset rather than assumed; reading them as
  interval starts shifts all solar gain by one interval, which at dawn and dusk
  is the difference between darkness and full sun.
- Values are resampled by overlap-weighted averaging, so the API resolution need
  not match the step length, and a window with less than half coverage returns
  no value instead of a figure derived from almost no data.

### Precedence and safety
- A configured local irradiance sensor still wins outright: a real measurement
  at the site beats any model.
- Steps the Open-Meteo data does not cover fall back to the weather entity
  rather than to zero, since "no data" is not "no sun". Missing samples are
  dropped rather than coerced to `0.0` for the same reason.
- Existing installs are unaffected. The default source remains the weather
  entity, and the feature is entirely opt-in.

### Fixed
- **A naive datetime could crash the update loop.** `dt_util.now()` returns a
  naive datetime when no timezone is configured, and comparing it against the
  timezone-aware API timestamps raised `TypeError` inside
  `_prepare_forecast_data`, taking the whole optimization down over a timezone
  detail. Instants are now normalised to UTC at the boundary.
- **`strings.json` had drifted from `translations/en.json`**, so several
  configuration fields, including the buffer tank sensor added earlier, showed
  raw keys instead of labels.

## v2.6.1

### Fixed
- **The dashboard card showed "No plan data available yet" on a stock install.**
  The plan sensors use `has_entity_name`, so Home Assistant prefixes them with
  the device name and the real ids are
  `sensor.heat_pump_optimizer_space_heating_plan` /
  `sensor.heat_pump_optimizer_dhw_heating_plan`. The card defaulted to the
  unprefixed ids, which never exist, so a default configuration could not work.
- **The card no longer depends on entity ids being stable.** The plan sensors
  publish a `plan_kind` attribute (`space` / `dhw`) and the card discovers them
  by that marker when the configured id is absent, so renaming an entity no
  longer breaks it. A name-suffix match keeps older setups working.
- **Upgrades kept serving the cached old card.** The Lovelace resource is
  registered with a `?v=<version>` cache-buster, but the existing-resource check
  matched on the base URL only and left the stale query in place, so browsers
  reused the previously cached JavaScript after every upgrade. The resource is
  now updated in place when the version changes.
- **The empty-state message is now actionable.** Instead of naming two entities
  it was only guessing at, the card reports per circuit whether the entity was
  not found, is unavailable, has no forecast yet, or has data outside the
  selected window.

## v2.6.0

### Summary
Follow-up to the hot water rework in 2.5.0. Space heating gets the same
scrutiny, the two circuits are now planned against each other instead of one
after the other, three invented cost terms that were distorting the objective
are gone, and the model learns two more of its own parameters. There are also
two new sensors that publish the full heating plan and a dashboard card that
charts it.

### Changed
- **Hot water and space heating are now co-optimized.** They share one
  compressor, so the old sequential decomposition — plan hot water first, then
  give space heating whatever capacity is left — let hot water fill the cheapest
  hours to the ceiling and push space heating into dearer ones. Measured on the
  winter scenarios that displaced 2.6 kWh (typical) to 4.7 kWh (extreme prices)
  of space heating out of the cheap block. The hot water LP now carries a
  congestion premium: taking capacity in a contended step is charged the extra
  cost of buying the displaced space heating at the cheapest price within a
  6 hour window instead. Because the displacement is piecewise-linear in hot
  water power this stays an exact linear program. A second pass then re-plans
  hot water against the space heating profile that resulted, and adopts it only
  if it scores strictly better on the same objective. Contended steps drop from
  22 to 4 and winter cost falls about 0.6%.

- **Three heuristic cost terms have been removed from the space heating
  objective.** `solar_anticipation_cost` and `pre_heat_incentive` were invented
  currency layered on top of physics the simulation already models: the
  trajectory itself shows that heating before sunshine is wasted and that
  coasting into a windy night is expensive, because solar gain and the weather
  heat loss factors are applied to the real dynamics. Restating that as an extra
  cost double-counted it, and `pre_heat_incentive` was worse than redundant — it
  was a *negative* cost, effectively paying the plan to burn electricity.
  `pre_heat_incentive` also existed only on the no-hot-water code path, so
  simply enabling hot water silently changed the space heating objective.
  Removing them cuts cost 1.1% (mild windy winter) and 4.3-5.6% (shoulder
  season) with no change in comfort. The anticipatory weighting still shapes the
  solver's initial guess, where being wrong costs nothing; it no longer
  discounts real minimum-temperature breaches.

- **The comfort floor is now enforced with an exact penalty.** A purely
  quadratic undershoot penalty has vanishing gradient at the boundary, so the
  solver would park a few hundredths of a degree below the configured minimum
  where the electricity saved outweighed the penalty. A small linear term
  restores a non-zero slope at the bound. Residual violations across the
  validation scenarios go to zero.

- **The solver starts from several candidate schedules instead of one.** The
  space heating objective is not convex, and from a single starting guess the
  two-zone model settled on schedules that random perturbation could beat by
  around 3%. Candidates are scored on the objective first, which is cheap, and
  only the two most promising are actually optimized, so this costs roughly one
  extra solve. Two-zone winter cost falls 2.2%.

- **Buffer tank standby loss is stated as a cooling rate.** Like the hot water
  tank in 2.5.0 it is now expressed in °C/h at a reference temperature
  difference and the UA value is derived from it, which is what makes it
  observable and therefore learnable. The default reproduces the previous fixed
  coefficient.

### Added
- **Self-learning buffer tank cooling rate.** If you point the new *Buffer tank
  temperature sensor* option at a sensor, the integration estimates the tank's
  standby loss from quiet decay, using the same lower-envelope estimator as the
  hot water tank: every contaminating effect can only make a tank look leakier
  than it is, so the estimate drops quickly towards a quieter reading and only
  creeps upward.

- **Self-learning house heat transfer.** The configured heat loss coefficient is
  a nameplate estimate; what the optimizer needs is how fast *your* house loses
  heat. Each update replays the interval that just elapsed through the same
  model the optimizer uses, with the power that was actually applied, and
  attributes the difference between predicted and measured indoor temperature to
  the heat loss coefficient. Everything the model already accounts for — slab
  transfer, solar gain, internal gains, wind, rain — is therefore excluded, and
  a Newton step on the remaining residual gives the correction directly. Unlike
  the tanks the bias here is two-sided, so this uses a symmetric slow average
  rather than a lower envelope, plus a per-interval rate limit and a residual
  cutoff so an open window or a wood stove cannot run away with the model. It
  is learned as a dimensionless scale, which also handles the two-zone case
  where a single indoor sensor cannot identify the two floors separately.

- **Two plan sensors: `Space Heating Plan` and `DHW Heating Plan`.** Each
  publishes the contiguous heating slots the optimizer intends to run, with
  start, end, duration, energy, average price and cost, plus a step-by-step
  `forecast` covering the whole horizon. The existing schedule attributes are
  truncated to 24 steps, which at the default 15 minute resolution is only the
  first six hours; these sensors carry the full 24 hours. The bulky series are
  declared unrecorded so they do not bloat the recorder database.

- **A dashboard card.** `custom:heatpump-optimizer-card` plots electricity
  price, planned hot water slots, planned space heating slots, outdoor
  temperature, predicted tank temperature and predicted house temperature on one
  shared time axis, with per-series legend toggles that persist across reloads.
  It is hand-written inline SVG with no external chart dependency, and the
  integration registers it automatically. See `docs/dashboard-card.md`.

## v2.5.0

### Summary
Hot water is now planned as what it actually is — a battery. Previously the
tank was only heated shortly before the water was needed, which meant a
17:00–22:00 demand window was largely paid for at 17:00–22:00 prices. The
planner can now buy hot water at *any* hour of the horizon and store it, and it
learns how quickly your particular tank loses that stored heat instead of
assuming it. In the validation scenarios hot water costs 10–15% less, uses less
energy, and the tank runs slightly warmer at its lowest point.

### Changed
- **Hot water is scheduled by a minimum-cost plan over the full horizon.** The
  old planner walked forward, found the first moment the tank would fall short,
  and bought the missing energy from the cheapest *preceding* hours — subject to
  a hard cap of at most 18 hours of lead time, and to a headroom rule that let a
  single already-scheduled slot block every cheaper slot before it. In practice
  that pinned heating to the demand windows themselves. The tank is a linear
  store, so the whole schedule is now solved as one linear program: heat
  delivered `k` steps early still contributes `(1 - UA·Δt/C)^k / C` degrees when
  it is needed, and minimising `Σ price·energy/COP` under the availability
  floors and the tank ceiling gives the genuinely cheapest feasible plan. That
  decay factor *is* the standby loss, so pre-heating is priced correctly by
  construction and the artificial lead-time cap has been removed entirely.
  Heating now lands in the cheap night block and holds, rather than running
  through the evening peak.

  The previous cheapest-first planner is still there, seeded with that solution,
  as a repair pass: it re-simulates with the true non-linear tank (temperature
  dependent COP, cold-water floor) and tops up any residual shortfall. If the
  solve is unavailable for any reason it takes over completely, so the
  integration cannot lose hot water to a solver failure.

### Added
- **The tank's standby loss is learned instead of assumed.** How far ahead
  pre-heating pays off depends entirely on how well the tank holds heat, so it
  is now measured. The parameter has been restated in terms you can actually
  check — **°C lost per hour at 45 °C tank temperature in a 20 °C room**,
  defaulting to 0.3 °C/h — and is converted to a heat loss coefficient using
  your tank volume. The previous fixed coefficient implied 0.36–0.65 °C/h
  depending on tank size, i.e. a leakier tank than most, which made the
  optimizer needlessly reluctant to store heat.

  Whenever the tank temperature is sampled across an interval in which the heat
  pump did not run, the decay itself gives the answer:
  `UA/C = -ln((T_end - T_ambient)/(T_start - T_ambient)) / Δt`. Water drawn
  during the interval can only make the tank look leakier than it is, never
  tighter, so readings are folded in as a lower envelope — the estimate moves
  quickly towards a quieter observation and only creeps upward. One unnoticed
  shower therefore cannot convince the model that the tank is badly insulated,
  while a genuinely deteriorating tank is still learned within days. Samples
  shorter than 15 minutes or longer than 6 hours, and tanks within 5 °C of room
  temperature, are ignored; the result is clamped to 0.05–3.0 °C/h and survives
  restarts.

- **Tank cooling rate is configurable.** It appears in the DHW step of both the
  setup and options flows, and as `dhw_cooling_rate` on the
  `set_thermal_parameters` service. Setting it explicitly resets the learned
  estimate to your value.

- **New attributes on the DHW sensors.** `dhw_cooling_rate`,
  `dhw_cooling_rate_learned`, `dhw_cooling_samples`, `dhw_hold_hours` and
  `dhw_preheat_hours` show what the model believes about your tank and how far
  ahead it is willing to plan.

### Upgrading
No action required. Existing installations pick up the 0.3 °C/h default and
start refining it from the next quiet period onwards; the value only affects
*when* hot water is heated, never whether it is available.

## v2.4.1

### Summary
A QA pass against a real Home Assistant instance found two ways an ordinary
weather forecast could quietly ruin a day's heating plan, plus a handful of
smaller defects. If your house has been running warmer and more expensively
than the savings figures suggested, this release is likely the reason why.

### Fixed
- **Wind speed is no longer guessed from its magnitude.** The forecast wind was
  assumed to be km/h whenever it exceeded 30, and m/s otherwise. Home Assistant
  hands the forecast over in whichever unit you have configured, so an ordinary
  20 km/h breeze fell under that threshold and was used as 20 m/s, a severe
  storm. For anyone whose units are km/h that inflated the predicted heat loss
  2.17x, the scheduled energy by 128% and the predicted cost by 211%. The
  correction applied above the threshold was the km/h factor, so it was wrong
  for mph as well. The unit is now read from the weather entity, and m/s, km/h,
  mph and knots all produce the same plan.

- **A single missing value in the forecast no longer disables the optimizer.**
  Weather integrations are allowed to report a field as empty. An empty wind
  speed raised an error that was caught and discarded, so the integration went
  on looking perfectly healthy while silently never producing a plan again. An
  empty temperature was worse: it spread through the prediction until most of
  the 24-hour trajectory was invalid, the solver gave up, and the savings
  sensors either disappeared at startup or froze at their last value while
  logging an error every cycle. Unusable values now fall back to a sane default.

- **Missing electricity prices are reported instead of invented.** When prices
  could not be fetched, a flat 0.5 SEK/kWh curve was substituted and the
  optimizer still published a savings figure that no price data supported. It
  now says so in the log and skips the run, leaving the cost sensors unknown.

- **The hot water slab thermal mass could not be set.** The `slab_thermal_mass`
  field of the `set_thermal_parameters` service was documented and accepted but
  silently did nothing.

- **The target temperature on the thermostat card is yours again.** It used to
  show the optimizer's own setpoint for the current 15-minute step, so the card
  drifted away from whatever you had just dialled in, and your change was lost
  on the next reload. The card now shows and remembers your target; the
  optimizer's current setpoint is available as the "Optimal Setpoint" sensor and
  as an `optimizer_setpoint` attribute.

- **The current price sensor records history again.** It declared itself a
  monetary sensor while reporting a continuous measurement, a combination Home
  Assistant rejects, so it warned on every startup and stored no statistics.

- **Turning the optimizer off no longer reports an unknown preset**, and the
  three platforms no longer disagree about the device's model and version. The
  device now reports the real version from the manifest.

## v2.4.0

### Summary
Two things: the options flow is now a proper menu where every setting,
including the sensor entities, can be changed after setup and every field is
explained in plain language. And the optimizer got substantially cheaper to
run, because the term that pulls the house toward the target temperature was
drowning out the electricity price.

### Changed
- **The comfort pull is now measured against the range you allow.** The
  pull-to-target penalty was a fixed quadratic, which at a typical winter
  setting was roughly 2.4x the entire electricity bill for the day. The
  optimizer therefore behaved like an ordinary thermostat and the minimum
  temperature you configured had almost no effect. It is now scaled by the gap
  between your target and your minimum, so widening that range genuinely buys
  cheaper operation and narrowing it holds the setpoint tighter. Winter savings
  went from ~35% to ~45% in a single-zone house and from ~15% to ~36% in a
  two-zone house.

  If you prefer the previous, warmer behaviour, raise "How strictly to hold the
  temperature". Around 5 lets the house use the full range you allow, 10 keeps
  it noticeably closer to target, and 20 or more behaves much like a thermostat.

- **Reconfiguration is now a menu.** Instead of one long form, the options flow
  opens on a menu with separate pages for sensors, comfort, hot water, the
  building, tuning and the heat curve. Editing one page leaves the others
  untouched.

### Added
- **Sensor entities can be changed after setup.** Indoor and outdoor
  temperature, solar radiance, wind, precipitation, power and energy meters and
  the Tibber token can all be re-pointed from the options flow. Previously they
  were fixed at initial setup. Clearing a field now genuinely clears it.
- **Every setting is explained.** All options pages and all setup steps have
  friendly labels and a per-field description, in English and Swedish, instead
  of raw parameter names.
- **A terminal cost on the planning horizon.** Nothing beyond the horizon was
  scored, so the optimizer reliably dumped the last couple of hours of every
  plan: it coasted the house down because the resulting cold never appeared in
  the objective. End-of-horizon shortfall is now priced using the same
  reference the savings settle-up uses, so the plan and the reported savings
  agree.

### Fixed
- **Two-zone houses were applying the comfort weight twice.** The penalty
  summed both zones, so a two-zone house behaved as if the setting were double
  what was configured. It hugged the setpoint and gave up most of the available
  savings, and used 22% of its energy in the most expensive quarter of the day
  against 3% now. The penalty is averaged across zones, so the setting means
  the same thing in both modes.
- **Savings could be reported as strongly negative in summer.** The settle-up
  charged the optimizer for ending *less* overheated than the baseline: in July
  both end up well above target from solar gain, and stored heat above what is
  actually useful was still being valued. Stored heat is now capped at what the
  comfort target and hot water requirement genuinely call for, and only real
  shortfalls are charged.
- **Two-zone end-of-horizon state was partly fabricated.** The end state was
  built from the room and slab only, so in two-zone mode the floor and buffer
  tank temperatures silently fell back to their defaults and were compared
  against the baseline's real values. The schedule is now replayed through the
  model to get a consistent end state.
- **"Suboptimal" was reported for perfectly good plans.** On a flat price curve
  the cost surface is genuinely degenerate, so the solver's line search aborts
  even though the result is fine. That is no longer surfaced as suboptimal
  unless the solver actually failed to improve on its starting point.

## v2.3.1

### Summary
Fixes the savings sensors, which routinely reported implausible numbers (often
above 90%). The reported figure is the gap between an optimized plan and a
"what a normal thermostat would have done" baseline, and the baseline was
burning far more energy than any real thermostat would.

### Fixed
- **The baseline no longer burns minimum power around the clock.** Baseline
  power was clipped to a *minimum* of the heat pump's minimum modulation power,
  so the reference schedule consumed at least `min_power x 24 h` every day even
  in weather that needs no heating at all. On a mild day that was a flat
  ~24 kWh against an optimized 0.16 kWh, which by itself produced the >90%
  readings. It also drove the baseline house to 25.3 °C, which no thermostat
  would do. Minimum modulation power is the lowest the pump can run *while
  running*; a pump that cannot go lower cycles instead, so 0 is now allowed.
- **The same floor applied to the optimizer itself.** With DHW disabled, space
  heating power was bounded below by the minimum modulation power, so the pump
  was forced on every single step. In warm weather this heated the house to
  25.3 °C and cost 40 SEK/day where the correct answer was to stay off.
- **The baseline is now a real thermostat.** It used a heuristic proportional
  term that over-delivered heat. It is now a cascade controller derived from
  the thermal model's own steady state, so the comparison is like-for-like. It
  holds the setpoint within 0.02–0.5 °C and its energy balance closes exactly.
- **End-of-horizon borrowed heat is no longer counted as savings.** Nothing
  past the optimization window is penalised, so the plan coasts the building
  and tank down as the window closes. That heat has to be bought back in the
  next window. The difference in stored thermal energy is now settled up at the
  25th-percentile price and charged against the reported savings. It is
  published separately as a `deferred_energy_cost` attribute on the savings
  percentage sensor, so `predicted_cost` remains the actual expected spend.
- **Savings percentage is clamped and guarded.** Baselines at or near zero no
  longer turn rounding noise into huge percentages.
- **Two-zone simulation lost the slab temperature every step.** The two-zone
  step function computed the new slab temperature and then dropped it when
  building the next state, so the slab was pinned at its default value forever
  and the lower floor could never be charged. Outdoor temperature and the
  anti-legionella timer were dropped the same way, which broke legionella
  tracking in two-zone mode.

### Effect on reported numbers
A control scenario with a completely flat electricity price, where there is
nothing to arbitrage and correct savings are therefore near zero, previously
reported 27%. It now reports 3.1%. Realistic scenarios with a 10x daily price
spread report 43–50% instead of up to 93%.

## v2.3.0

### Summary
This release reworks domestic hot water (DHW) optimization. Hot water is now
required only during time frames you configure, and it is produced with a
cheapest-first schedule instead of a target temperature the optimizer tried to
track regardless of price.

### Fixed
- **DHW no longer heats to high setpoints during price peaks.** The objective
  previously contained a "comfort" term that penalised any deviation from a
  ramped DHW target temperature. Its weight was orders of magnitude larger than
  the electricity cost term, so the solver effectively ignored price and heated
  the tank to setpoint whenever it drifted — including in the most expensive
  hours and while space heating was idle. DHW is now penalised only for
  *violating an availability requirement*, never rewarded for being hot, which
  leaves electricity cost as the only thing deciding when the pump runs.
- **DHW plans are now physically realizable.** The gradient solver used to smear
  DHW across many steps at 0.1–0.5 kW, below the level at which the heat pump is
  considered to be running. DHW is now scheduled as discrete on/off blocks.
- **The 45 °C floor no longer applies around the clock.** It applies inside the
  demand time frames; outside them the tank may cool to the idle minimum.
- **The options dialog no longer fails with a 500 error.** Reconfiguring an
  already-configured device returned *"Config flow could not be loaded: 500
  Internal Server Error"*. The options flow assigned to `self.config_entry`,
  which goes through a property setter Home Assistant deprecated in 2024.11 and
  removed in 2025.12. The flow now keeps its own reference to the entry.
- **Config entries from older releases now migrate.** The config flow declared
  schema version 6 without an `async_migrate_entry` handler, so Home Assistant
  refused to load entries written by earlier releases. Entries are now migrated
  forward; a newer entry is refused with a clear log message instead of failing
  obscurely.
- **Removed an invalid SciPy solver option** (`disp`) that produced an
  `OptimizeWarning` on every optimization run with recent SciPy versions.

### Added
- **Hot water demand time frames.** Configure when hot water must be available,
  e.g. `06:00-08:30, 17:00-22:00`. Frames may wrap past midnight and are
  editable from both the setup dialog and the options dialog.
  - Inside a frame the tank is guaranteed at or above the DHW minimum
    temperature.
  - At the start of a frame the tank is pre-heated only as far as that frame's
    expected draw requires, capped at the DHW setpoint — small consumers are no
    longer heated to full setpoint for no reason.
  - Outside the frames there is no availability requirement.
  - Leave the field empty to derive the frames from the learned usage profile,
    or switch the schedule off to require hot water around the clock.
- **Anti-legionella cycle**, enabled by default: the tank is heated to 60 °C
  every 7 days, scheduled at the cheapest hour before the deadline. The timer
  resets whenever the tank is observed at the disinfection temperature for any
  reason, so manual boosts and immersion heaters count. Temperature and interval
  are configurable, and the cycle can be turned off.
- **Idle minimum temperature** (default 20 °C) — the floor that applies outside
  the demand time frames.
- New DHW sensor attributes: `dhw_windows`, `dhw_in_demand_window`,
  `dhw_next_window_in_hours`, `dhw_required_temperature`,
  `dhw_idle_min_temperature`, `dhw_legionella_due_in_hours` and
  `dhw_planned_heating_hours`.

### Changed
- **Two-stage solve.** DHW is scheduled by a cheapest-first planner, then space
  heating is optimized around the fixed DHW blocks with the pump's remaining
  capacity as a hard per-step bound. This replaces the joint solve and its soft
  capacity penalty, so the capacity limit can no longer be violated.
- Slot ranking uses an *effective* price that includes the standby heat lost
  while water waits in the tank, so pre-heating many hours ahead is only chosen
  when it is genuinely cheaper.
- The tank is never planned above `min(70 °C, max(setpoint, legionella temp))`.
- The learned hourly draw pattern is masked by the configured time frames while
  preserving the total daily volume.
- Typical solve time with DHW enabled dropped from roughly 6 s to under 1 s, and
  the solver no longer hits its iteration limit.

### Changed limits
- Buffer tank volume now accepts up to **1500 L** (was 500 L), and is editable
  from the options dialog instead of setup only.
- DHW tank volume and daily hot water consumption now accept up to **1500 L**
  and **1500 L/day** (both were 500).

### Configuration options
| Option | Default |
|---|---|
| `dhw_schedule_enabled` | `true` |
| `dhw_windows` | `06:00-08:30, 17:00-22:00` |
| `dhw_idle_min_temperature` | `20` °C |
| `dhw_legionella_enabled` | `true` |
| `dhw_legionella_temperature` | `60` °C |
| `dhw_legionella_interval_days` | `7` |

### Upgrade notes
Existing installations pick up the default time frames on upgrade. If your
household draws hot water at other times, set `dhw_windows` in the integration
options. To keep the previous always-hot behaviour, turn off *Only guarantee hot
water during set time frames*.

## v2.2.0
**Release date:** 2026-04-27

### Summary
This minor release introduces a new, preferred ECL110 MQTT direct-write control path while keeping full backward compatibility with existing legacy JSON command workflows.

### Highlights
- **New ECL110 direct-write MQTT interface (preferred):**
  - Commands are now published as plain numeric payloads to a dedicated `/set` topic for cleaner, lower-overhead control.
  - Default direct-write topic: `ecl110/flow_temp_control/displace/set`.
- **Backward compatibility preserved:**
  - Legacy JSON command publishing remains supported on `ecl110/command`.
  - Existing ECL110 installations using the previous JSON interface continue to work without mandatory migration.
- **Broader state payload compatibility:**
  - State handling now supports both legacy JSON/dictionary payloads and scalar numeric payloads from hierarchical topic structures.
- **Improved configuration UX:**
  - Added a new configurable option: `ecl110_displace_set_topic`.
  - Existing `ecl110_command_topic` labeling has been clarified as the **legacy JSON path**.
  - Updated UI strings/translations for clearer topic purpose in both setup and options flows.

### Configuration options
The following MQTT topic settings are now available for ECL110 control:
- `ecl110_displace_set_topic` *(new, preferred direct-write path)*
  - Default: `ecl110/flow_temp_control/displace/set`
- `ecl110_command_topic` *(legacy JSON path, optional for compatibility)*
  - Default: `ecl110/command`
- `ecl110_state_topic` *(state feedback topic)*
  - Default: `ecl110/flow_temp_control/displace`

### User impact
- Recommended for users integrating with ECL110 hierarchical MQTT topics and direct numeric control.
- Existing users can safely upgrade without immediate topic migration.
- Integrators can run both paths in parallel during transition if needed.

### Notes
- This is a backward-compatible minor release.
- No required database/config migration for existing installations.

## v2.1.0
**Release date:** 2026-04-23

### Summary
This release improves Domestic Hot Water (DHW) optimization to prioritize cost savings while maintaining safe hot water availability.

### Highlights
- **Configured DHW minimum temperature is now actively enforced as the true floor** in optimization logic.
- **Predictive DHW pre-heating** now uses forecasted usage windows and estimated lead-time so the tank can coast near minimum between peaks.
- **Price-aware DHW control** reduces heating in expensive periods when no near-term hot water usage is predicted.
- **Learning usage patterns over time** from observed DHW temperature drops, persisted across restarts.
- **Post-install editability improvements** in the options flow for comfort/day-night schedule and DHW parameters.
- **Branding update**: added integration icon (`icon.png`) for HACS/repository branding.

## v2.0.1
**Release date:** 2026-04-21

### Summary
This patch release fixes a critical control logic issue that could prevent Domestic Hot Water (DHW) reheating when space heating demand was low or zero.

### Fixed bug
- **Critical ON/OFF control fix:**
  - The heat pump ON decision now correctly considers **both**:
    - space heating demand, and
    - DHW demand.
  - Previously, ON/OFF logic only evaluated space heating demand, which could keep the heat pump OFF even when DHW needed heating.

### Improvements and changes
- Updated ON/OFF schedule generation to use combined demand logic (`space OR dhw`) so the heat pump can activate for DHW-only demand periods.
- Added enhanced debug logging for optimizer decision-making, including:
  - per-step space heating power,
  - per-step DHW power,
  - threshold comparisons,
  - explicit decision reason tags (for example: `space_only`, `dhw_only`, `space_and_dhw`).
- Added clearer first-step decision summary logging to simplify troubleshooting during live operation.

### User impact and benefits
- Prevents missed DHW reheating cycles when there is no immediate space heating demand.
- Improves comfort and reliability by ensuring DHW demand can independently trigger heat pump operation.
- Makes behavior easier to diagnose with richer decision logs.
- Reduces risk of confusion where optimization output indicated DHW demand but physical heat pump stayed OFF.

### Upgrade instructions (HACS)
1. Open **HACS → Integrations**.
2. Find **Heat Pump Cost Optimizer**.
3. Click **Update** and install **v2.0.1**.
4. Restart Home Assistant (recommended after integration updates).
5. Verify operation:
   - Confirm integration version shows **2.0.1**.
   - Check logs at debug level if needed to validate combined ON/OFF decisions for space heating and DHW.

### Notes
- This is a backward-compatible patch release focused on control correctness and observability.
- No configuration migration is required.
