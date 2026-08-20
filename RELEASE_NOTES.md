# Heat Pump Cost Optimizer — Release Notes

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
