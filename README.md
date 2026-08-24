# Heat Pump Cost Optimizer for Home Assistant

A custom Home Assistant integration that uses **Model Predictive Control (MPC)** to optimize heat pump operation and minimize electricity costs, while maintaining indoor comfort and domestic hot water availability. Integrates with **Tibber** for dynamic electricity prices and Home Assistant weather entities for temperature, wind, rain, and solar forecasts.

## Acknowledgement

This project began as a fork of
[**strutsfarm/heatpump_optimizer**](https://github.com/strutsfarm/heatpump_optimizer)
at version 2.2.0, and everything it does rests on that foundation: the MPC
formulation, the two-zone thermal model with its slab and buffer tank, the
Tibber and weather integration, the config flow, and the ECL110 heat-curve
control path are all originally strutsfarm's work. The companion
[**strutsfarm/ecl110**](https://github.com/strutsfarm/ecl110) project provides
the MQTT interface this integration drives.

Versions 2.3.0 onward were developed in this fork. Both projects are MIT
licensed. Thank you to strutsfarm for the original code and for releasing it
under a licence that made this possible. The formal attribution is recorded in
[NOTICE](NOTICE); `LICENSE` is kept as the verbatim MIT text so that automated
licence detection recognises it.

## Disclaimer

**Read this before installing.** This software controls real heating equipment
and makes claims about money. Both deserve care.

**No warranty.** This project is provided "as is" and "as available" under the
MIT licence, with no warranty or condition of any kind, express or implied,
including but not limited to warranties of merchantability, fitness for a
particular purpose, title, accuracy, and non-infringement. There is no
guarantee that it works at all, that it works as described, that it will
continue to work, or that any defect will ever be corrected. See
[LICENSE](LICENSE) for the full text.

**Any use of this software is entirely at your own risk.** You accept that risk
in full, and in its entirety, the moment you install or run it.

**No responsibility, no liability.** The authors and contributors accept **no
responsibility whatsoever** for anything arising out of, or in any way
connected with, this software — its use, its misuse, its inability to be used,
its effects, its behaviour, its functions or its failure to function.

This exclusion is intended to be as broad as the law allows. It covers every
kind of loss or damage, whether direct, indirect, incidental, special,
exemplary, punitive or consequential, and regardless of the legal theory
advanced — contract, tort, negligence, strict liability, statute or otherwise —
and applies even if the possibility of such damage was known or foreseeable. It
includes, without limitation: damage to your heat pump, boiler, tanks, pipes,
controller, sensors, wiring or any other equipment; damage to your building or
its contents, including from freezing, overheating, condensation, water or
fire; loss of heating or hot water, and any discomfort, disruption or
displacement resulting from it; injury or illness, including any arising from
water temperature or hygiene; excessive electricity consumption, unexpected
bills, missed savings, tariff penalties or peak charges; wear, shortened
service life, or voided warranties on your equipment; corrupted or lost
configuration, history or data; time and cost spent installing, diagnosing,
repairing or removing it; and any decision you make in reliance on anything
this software calculates, predicts, reports or displays.

**It is your decision and your risk.** Any use of this software, and anything
you do with it or because of it, is entirely and exclusively at your own risk.
You alone are responsible for deciding whether to install it, for how you
configure it, for what you allow it to control, for supervising what it does,
and for making sure independent protections remain in place. Nobody is obliged
to provide support, fixes, updates or maintenance of any kind. If any part of
this exclusion is held unenforceable, the remainder continues to apply and
liability is limited to the smallest amount permitted by law.

**It is not a safety device.** Do not rely on it for frost protection, for
keeping pipes from freezing, for legionella control, or for anything else where
failure has consequences. It can stop working for many ordinary reasons — a
lost network connection, an expired API token, a Home Assistant upgrade, a
crashed process, a dead sensor — and when it does, your heat pump is left
wherever it was last told to be. Keep your heat pump's own thermostats,
limits and safety controls active and correctly configured. They, not this
integration, are what protect your home.

**Anti-legionella is a convenience, not a compliance feature.** The cycle
scheduled here is a best effort based on a modelled tank temperature at one
sensor. It is not a substitute for following your local regulations and your
tank manufacturer's guidance on hot water hygiene, and it cannot detect
stratification, dead legs or a mis-sited sensor. If in doubt, keep an
independent legionella cycle configured on the tank itself.

**Savings figures are estimates.** Every cost, saving and percentage this
integration reports is the output of a model, computed against forecast prices
and forecast weather. Real savings depend on your building, your tariff, your
heat pump, your habits and the weather actually occurring. Nothing here is a
guarantee or a financial projection, and the baseline it compares against is a
simulated always-on thermostat rather than a measurement of what you would
otherwise have spent. Treat the numbers as a guide to relative decisions, not
as an accounting record.

**The model learns, and can be wrong.** Several parameters are estimated from
your own house over time. A faulty or mis-configured sensor can push those
estimates somewhere unhelpful, and the optimizer will then plan confidently
against a wrong model. The input watchdog and the guard thresholds exist to
limit that, but they cannot eliminate it. Check the diagnostic sensors
occasionally, especially in the first weeks.

**Your equipment, your responsibility.** Driving a heat pump or an external
controller over MQTT may affect its warranty, may interact badly with its own
internal logic, and may be subject to local regulation. Confirm that what you
are doing is permitted and sensible for your specific hardware before enabling
control features. Cycling a compressor more than its manufacturer intends can
shorten its life.

**No affiliation.** This project is not affiliated with, endorsed by, or
supported by Home Assistant, Nabu Casa, Tibber, Nord Pool, Danfoss, Open-Meteo,
or any heat pump manufacturer. Product and company names are used only to
describe what the integration interoperates with. Use of third-party APIs is
subject to those providers' own terms, and their availability, accuracy and
pricing are outside this project's control.

## Features

- **True Predictive MPC** — uses FULL 24-hour weather forecast trajectories for anticipatory control
- **Solar Anticipation** — reduces pre-heating when sunny weather is forecasted (the sun will heat for free)
- **Wind/Rain Anticipation** — increases pre-heating before forecasted bad weather (higher heat loss coming)
- **Two-zone thermal model** — separately models upper floor (radiators) and lower floor (slab floor heating)
- **Joint DHW and space heating optimization** — the two circuits share one compressor and are planned against each other, not one after the other
- **Enhanced heat loss model** — wind speed increases convective loss, rain increases envelope U-value
- **Solar heat gain calculation** — accounts for passive solar gains through windows
- **Buffer tank dynamics** — models the heat pump buffer tank coupling both heating circuits
- **Tibber integration** — uses real-time and day-ahead electricity prices
- **COP modeling** — adjusts for outdoor temperature–dependent heat pump efficiency
- **Real sensor feedback** — uses floor heating return temperature for slab state estimation
- **Multiple operation modes** — Auto, Comfort, Economy, Boost, Off
- **Self-learning thermal parameters** — tank cooling rates, house heat loss, COP and the defrost derate are estimated from your own house
- **Capacity tariff awareness** — models the monthly *effekttariff* many Swedish grid companies bill, so cheap-hour stacking cannot cost more than it saves
- **PV self-consumption** — prices each hour at what consuming actually costs you, which is the export compensation while your array is in surplus
- **Learned price prior** — models the unpublished part of the horizon from your own typical daily price shape instead of repeating the last price
- **External heat source detection** — spots a wood furnace charging the tanks and stops paying to heat water that is already hot
- **Away and holiday mode** — deep setback with recovery heat bought in the cheapest hours before you get home
- **Input staleness watchdog** — a sensor that stops updating is treated as missing, and learning pauses rather than training on a flatline
- **Closed-loop accuracy reporting** — predicted versus realised temperature, power and cost, so model drift is visible
- **Building type presets** — three answerable questions about your house instead of two unanswerable ones about kWh/°C
- **Plan reason codes** — every planned slot says *why* it was chosen
- **Energy dashboard integration** — accumulating energy and cost totals, split hot water versus space heating
- **The house as a virtual battery** — state of charge, capacity and rates published so other automations can use it
- **Rich sensor entities** — 47 sensors including full heating plans, DHW, predictive insights, per-zone temperatures
- **Dashboard card** — plots price, planned heating slots, irradiance and predicted temperatures on one graph, with per-series toggles, reason codes and a what-if simulator
- **Climate entity** — virtual thermostat with full HA climate integration
- **Buttons and binary sensors** — force a run, arm a measurement experiment, and see input health, external heat and away state at a glance
- **Service calls** — manual optimization, mode changes, runtime parameter tuning, and what-if simulation

## How the Predictive Optimization Works

### True Anticipatory Control (Not Just Reactive!)

The key differentiator of this optimizer is that it uses **forecasted weather data** to make decisions about **current** actions. This is what makes it true Model Predictive Control:

#### Solar Anticipation Strategy
```
Current time: 22:00 (night, cheap electricity)
Forecast: Tomorrow 10:00-16:00 → 400-600 W/m² solar radiation

Traditional optimizer: Pre-heat slab during cheap night electricity ✓
THIS optimizer: REDUCE slab pre-heating because solar will heat it for free! 💰

Result: Less overnight heating → sun heats the slab tomorrow → SAVINGS
```

This falls out of the physics rather than from a bonus term. Solar gain is
applied to the simulated trajectory at every future step, so a plan that
pre-heats the slab before a sunny morning simply predicts an overheated house
and gets charged for the electricity it wasted. The optimizer avoids it because
it is genuinely more expensive, not because it is told to.

Earlier versions also added an explicit "heating before sun is bad" cost on top.
That double-counted physics the simulation already had, and removing it made
shoulder-season plans 4-6% cheaper with identical comfort. The solar forecast
still shapes the solver's initial guess, where a wrong hunch costs nothing.

#### Wind/Rain Anticipation Strategy
```
Current time: 14:00 (afternoon, moderate price)
Forecast: Tonight 20:00-06:00 → 8-12 m/s wind + rain

Traditional optimizer: React to wind when it arrives (too late!)
THIS optimizer: INCREASE pre-heating NOW while electricity is cheaper! 🏠

Result: Thermal mass pre-charged → house stays warm through bad weather → COMFORT
```

Again this is emergent. The forecast heat loss factors are applied to the real
dynamics at each step:
- **Wind effect**: Infiltration/convective heat loss increases by `wind_sensitivity × wind_speed` (default 3% per m/s)
- **Rain effect**: Wet building envelope U-value increases by `rain_multiplier` (default 15%)

so coasting into a windy night predicts a cold house and a comfort penalty. The
cheapest way to avoid that penalty is to pre-charge the thermal mass while
electricity is cheap, which is exactly what the plan does.

#### Joint hot water and space heating planning

The two circuits share one compressor, so they are planned against each other
rather than one after the other. Hot water is scheduled first as a minimum-cost
linear program, but that program is charged a **congestion premium**: taking
compressor capacity in a step where space heating also wants it costs the extra
price of buying the displaced space heating elsewhere, using the cheapest slot
within a 6 hour window. A second pass then re-plans hot water against the
resulting space heating profile and keeps it only if it scores strictly better.

Without this, hot water filled the cheapest hours to the ceiling and pushed
2.6-4.7 kWh of space heating out into dearer ones.

### DHW (Domestic Hot Water) Optimization

The optimizer coordinates DHW heating with space heating:

```
Heat Pump Capacity: 5 kW total
├── Space Heating: 0-5 kW (variable)
└── DHW Heating:   0-5 kW (variable)
    Total:         ≤ 5 kW (capacity constraint)
```

#### Demand time frames

Hot water is only *required* during the time frames you configure — for example
`06:00-08:30, 17:00-22:00`. This is the single biggest lever on DHW cost:

- **Inside a time frame** the tank is guaranteed to stay at or above the DHW
  minimum temperature (default 45 °C), so hot water is always available.
- **When a time frame opens** the tank is pre-heated to a "ready" temperature
  sized from the draw actually expected in that frame, capped at the DHW
  setpoint. A household that uses little water is never heated to 55 °C just
  because the setpoint says so.
- **Outside the time frames** there is no availability requirement at all. The
  tank is allowed to drift down, so no electricity is spent keeping water hot
  that nobody is going to use.

Time frames accept 24-hour times separated by commas, and may wrap past
midnight (`22:00-02:00`). Leave the field empty and the optimizer derives the
frames from the *learned* hourly usage profile instead. Switch the schedule off
entirely to require hot water around the clock (the pre-2.3 behaviour).

#### Minimum-cost production

DHW is a deferrable, essentially on/off load: the tank is a battery, and heat
put in at any hour is still there later, minus standby loss. It is therefore
scheduled separately from the gradient-based space-heating solve:

1. **A linear program plans the tank over the whole horizon.** The tank is a
   linear store, so its temperature at any step is an affine function of the
   heat put in earlier — a kWh delivered `k` steps ago still contributes
   `(1 - UA·Δt/C)^k / C` degrees today. Minimising `Σ price·energy/COP` under
   the availability floors and the tank's maximum temperature gives the
   genuinely cheapest feasible plan. The decay factor *is* the standby loss, so
   buying heat early is automatically priced above buying it late, and no
   artificial "don't pre-heat more than N hours ahead" cap is needed — none is
   applied. Heating can land at 02:00 for a 17:00 demand frame whenever that is
   cheaper, subject only to how much the tank can hold.
2. **A cheapest-first pass repairs the remainder.** The linear model ignores the
   COP's dependence on tank temperature and the cold-water floor, so a greedy
   top-up fixes any residual shortfall — and takes over entirely if the solve
   is unavailable.
3. **Space heating is then optimized around that fixed DHW schedule,** with the
   pump's remaining capacity during a DHW block bounding space heating power.

Because nothing in the objective rewards a hot tank for its own sake, price is
the only thing deciding *when* the pump runs for hot water. The result is
discrete heating blocks the pump can actually deliver, concentrated in the
cheapest hours, and no heating during price peaks that could have been done
earlier and stored.

#### Self-learning tank cooling

How far ahead pre-heating pays off depends entirely on how well the tank holds
heat, so that is measured rather than assumed. The parameter is stated as a
**cooling rate in °C per hour at 45 °C tank temperature in a 20 °C room**,
defaulting to 0.3 °C/h, and converted to a UA value using the tank's volume.

Every time the tank temperature is sampled across an interval in which the heat
pump did not run, the standby time constant follows from the decay itself:

```
UA/C = -ln((T_end - T_ambient) / (T_start - T_ambient)) / Δt
```

Hot water drawn during the interval can only make the tank *look* leakier than
it is, never tighter, so observations are folded in as a **lower envelope**: the
estimate moves quickly towards a quieter reading and only creeps upward. One
shower therefore cannot convince the model that the tank is badly insulated,
while a genuinely deteriorating tank is still learned within a few days. The
result is clamped to 0.05–3.0 °C/h and persisted across restarts.

A tank that holds heat well earns a longer pre-heating horizon and more of its
heating in cheap hours; a leaky one is heated closer to when the water is
needed. The learned value, its sample count and the resulting hold time are
exposed as attributes on the **DHW Temperature** sensor.

#### Anti-legionella

Since the tank is now allowed to cool between time frames, a periodic
disinfection cycle is enabled by default: every 7 days the tank is heated to
60 °C, scheduled at the cheapest hour before the deadline. The timer resets
whenever the tank is observed at the disinfection temperature for any reason
(planned cycle, manual boost, or immersion heater), so an already-hot tank never
triggers a redundant cycle.

Other behaviour:

- The optimizer models a time-of-day hot water draw pattern, masked by the
  configured time frames (learned from observed tank temperature drops).
- DHW tank thermal dynamics include standby losses and consumption draws.
- The tank is never planned above `min(70 °C, max(setpoint, legionella temp))`.

### Self-Learning Model Parameters

Three parameters are estimated from your own house instead of being taken on
faith from configuration. All three are clamped to plausible ranges, persisted
across restarts, and exposed as sensor attributes.

| Parameter | Learned from | Estimator |
|---|---|---|
| Hot water tank cooling rate | Tank temperature decay with no heating | Lower envelope |
| Buffer tank cooling rate | Buffer temperature decay with the pump off | Lower envelope |
| House heat loss coefficient | Predicted vs. measured indoor temperature | Symmetric average |

**Why the estimators differ.** For a tank, every source of error points the same
way: an unnoticed draw can only make it look leakier than it is. So the estimate
tracks the *lower envelope* of what is observed, dropping quickly towards a
quieter reading and creeping upward only slowly. One shower cannot convince the
model that the tank is badly insulated.

The house is not like that. Unmodelled gains (an oven, a full room of people)
bias the estimate down, while an open window or a draughty day biases it up, so
a lower envelope would be systematically wrong. It uses a slow symmetric average
instead, with a per-interval rate limit and a residual cutoff so a single
anomaly cannot move the model far.

**How the house estimate works.** Rather than waiting for a coasting period —
a heated house in winter rarely has one — each update replays the interval that
just elapsed through the same model the optimizer uses, with the electrical
power that was actually applied. Slab transfer, solar gain, internal gains, wind
and rain are therefore already accounted for, and the leftover difference
between predicted and measured indoor temperature is attributed to heat loss.
Predicted room change is linear in the heat loss coefficient with slope
`-(T_room - T_out)·Δt / C_room`, so a Newton step on the residual gives the
correction directly.

It is learned as a dimensionless scale on whatever you configured, which keeps
your entered value meaningful and also handles the two-zone case, where a single
indoor sensor cannot identify the upper and lower floor coefficients separately.

The buffer tank rate is only learned when a **Buffer tank temperature sensor**
is configured; without one a prior derived from the tank's size is used.

That prior, and the range the learning is allowed to move within, both follow
the tank's **surface area** rather than its volume. Heat escapes through a
tank's skin, and a large tank has far less skin for the water it holds — a
750-litre accumulator loses proportionally much less than a 35-litre buffer, so
a single "degrees per hour" figure cannot describe both. If you have an
accumulator this matters a great deal: applied unscaled, a small tank's figure
models more heat lost in six hours than the tank can physically hold, which
makes storing heat in it look pointless when it is not.

### Two-Zone Thermal Model

The house is modeled as two thermal zones served by a single air-to-water heat pump with a buffer tank:

```
                    ┌─────────────────────────┐
                    │    Heat Pump (COP)       │
                    └────────┬────────────────┘
                             │ Q_hp
                    ┌────────▼────────────────┐
                    │   Buffer Tank (35L)      │
                    └──┬──────────────────┬───┘
           Q_rad (40%) │                  │ Q_floor (60%)
                       │                  │
        ┌──────────────▼───┐   ┌─────────▼────────────┐
        │  Zone 1: Upper   │   │  Zone 2: Lower Floor  │
        │  Floor (Radiator)│   │  (Slab Floor Heating)  │
        │  Low thermal mass│   │  High thermal mass     │
        │  Fast response   │   │  Slow response         │
        └──────┬───────────┘   └──────┬────────────────┘
               │  Q_inter (open       │
               │◄─layout heat─────────┤
               │   transfer)          │
               │                      │
          ┌────▼──────────────────────▼───┐
          │   Outdoor environment          │
          │   Wind → ↑ convective loss     │
          │   Rain → ↑ envelope U-value    │
          └───────────────────────────────┘
```

### Enhanced Heat Loss Model

The heat loss model accounts for forecasted weather at EACH time step:

**Wind effect** (infiltration and convective heat transfer):
```
U_effective = U_base × (1 + wind_sensitivity × wind_speed)
```
- Default: 3% increase per m/s wind speed
- Example: 5 m/s wind → 15% higher heat loss coefficient
- Uses FORECASTED wind speed at each future time step
- Only the infiltration/convective share of the loss responds to wind, so the
  whole-house sensitivity is small. Raise it toward 0.05-0.08 for a draughty
  or very exposed house; measured infiltration studies put a 10 m/s wind at
  roughly +20-40% for typical tightness.

| House | Suggested wind sensitivity |
|---|---|
| Modern, tight, sheltered | 0.01-0.02 |
| Typical (default) | 0.03 |
| Older or exposed site | 0.04-0.06 |
| Draughty, coastal/open field | 0.06-0.08 |

**Rain effect** (wet building envelope):
```
U_effective = U_wind_adjusted × rain_multiplier (when raining)
```
- Default: 15% increase during rain (rain_multiplier = 1.15)
- Scales with precipitation intensity (light rain → partial multiplier)
- Uses FORECASTED precipitation at each future time step

### Solar Heat Gain

Solar radiation through windows reduces heating need:
```
Q_solar = solar_radiation × window_area × orientation_factor × SHGC / 1000
```

Solar gains are split between zones:
- Upper floor: 40% (default) — light reaches upper level
- Lower floor: 60% (default) — sun hits lower floor through large windows

#### Where the irradiance comes from

Solar gain is only as good as the irradiance behind it, and most weather
integrations never publish a `solar_irradiance` field, so the term silently
evaluated to zero for many installs. There are now three sources, tried in this
order:

1. **A local irradiance sensor**, if configured. A real measurement at the
   actual site always beats a model, so this wins outright.
2. **Open-Meteo**, if *Solar forecast source* is set to `Open-Meteo`. Pick the
   location on the map in the configurator. No API key or account is needed.
3. **The weather entity's forecast**, which is the previous behaviour and stays
   the default.

Open-Meteo is used through two endpoints because they do different jobs:

| Endpoint | Role | Why |
|---|---|---|
| `api.open-meteo.com/v1/forecast` | The planning horizon | Supports `minutely_15`, which matches the optimizer's 15-minute grid exactly |
| `satellite-api.open-meteo.com/v1/archive` | Current irradiance | Observed rather than modelled, current to ~10 minutes, so the heat-loss learner trains against what actually happened |

The satellite endpoint is archive-only and has no forecast route, which is why
it cannot serve the horizon on its own.

Two details worth knowing if you compare the numbers against the API by hand:

- The optimizer requests **`shortwave_radiation`** (global horizontal
  irradiance), not `direct_radiation`. The window-gain formula above applies its
  own orientation factor, and direct-beam alone omits the diffuse component,
  which on an overcast day is essentially all the light there is.
- **Open-Meteo timestamps mark the end of the averaging interval**, so the
  sample stamped `04:00` covers `03:00-04:00`. Reading them as interval starts
  shifts every value by one interval, which around dawn and dusk is the
  difference between darkness and full sun.

Values are resampled by overlap-weighted averaging, so the API's resolution does
not have to match the optimizer's step length. A step that Open-Meteo does not
cover falls back to the weather entity rather than to zero, because "no data" is
not the same as "no sun".

### Floor Return Temperature Feedback

When a floor heating return temperature sensor is configured, the optimizer uses it to correct the slab temperature model:
```
T_slab_estimated = 0.7 × (T_return + 1°C) + 0.3 × T_slab_model
```

### Learning how the heat loss splits between the floors

Once a real lower-floor sensor exists, the model can stop taking the *split*
between the two zones on trust as well.

The catch is that `house_heat_loss_scale`, the correction learned from
prediction error, multiplies **both** zone losses. It can move the total but
never the split, so learning both zone losses independently alongside it would
be three parameters chasing two degrees of freedom — they trade off against each
other and drift without ever making the fit worse.

So the two are given separate jobs. The scale owns the **level** and is fitted
from the upper floor. A new ratio owns the **split** and is fitted from the
lower floor, which the scale's own fit does not touch. Two parameters, two
independent measurements.

It only moves when a real lower-floor sensor is configured. Without one the
lower zone is inferred from the floor return water — an estimate derived from
the same sensor as the slab — so there is nothing independent to fit against.
Watch `lower_floor_loss_ratio` and `lower_floor_loss_samples` on the learning
sensor; the ratio stays at 1.0, the configured split, until it has evidence.

Deliberately **not** learned: the inter-zone transfer coefficient. One pump, one
water temperature and a fixed radiator/floor split mean the two zones are driven
together and rarely diverge, so there is very little to learn from and a passive
fit would mostly track noise. It stays at its configured value.

### Using the buffer tank as a store (mixing valve required)

Without a mixing valve, everything the heat pump makes goes straight to your
radiators and floor loops. The buffer tank is then just a hydraulic separator
that happens to lose a little heat — whatever enters it leaves immediately, so it
can never be charged. That is the default and it is a correct model.

A mixing valve changes this. It limits how much heat reaches the house, so once
the house has what it needs the surplus has nowhere to go but the tank. Set
**Mixing valve and heat storage** in the options:

| Setting | Meaning |
|---|---|
| No mixing valve | Default. Nothing changes. |
| Set by hand | A fixed valve you adjust yourself; tell the integration what you set it to. |
| Read from a sensor | The integration reads the valve's target but cannot change it. |

**What to set a hand-adjusted valve to.** The top of your comfort band, in
almost every case. A high setting keeps the valve open until the house reaches
its ceiling, so the building charges first — and building storage is free,
because the heat sits at room temperature. Only then does the valve throttle and
the tank take the surplus, which is stored hot and does cost efficiency.
Building first, tank second, is the cheap order; a low setting reverses it and
fills the expensive store while the free one sits empty.

The cost of that choice is that the valve is no longer what prevents your house
overheating — the optimizer's comfort limits are.

**Storing hot is not free.** A heat pump loses efficiency the hotter it must
push water, and that penalty is the whole economics of a thermal store: it
decides whether moving heat into a cheap hour actually pays. The model accounts
for it, so the tank is only charged when the price difference covers the loss.
On a flat-price day it will leave the tank alone. The tank is also never charged
past the maximum you configure, however cheap electricity gets.

### Knowing the lower floor, rather than guessing it

Two-zone mode plans against two room temperatures, but only the upper one has
ever had a sensor. The lower zone was inferred from the floor return water as
`T_return + 0.5 °C` — and that is a *water* temperature standing in for an air
temperature. A floor loop returns at roughly 24–30 °C while the room it serves
sits near 21, so the model believed the lower floor was several degrees warmer
than it was. That value is judged against the same comfort band as the upper
floor, so the zone read as permanently overshooting and the optimizer
under-heated the one room it could not see.

There was a second, quieter problem. The slab was derived from the *same* sensor
as `T_return + 1 °C`, so the difference between slab and room was always exactly
0.5 K no matter what the sensor read — which pinned the main heat path into the
lower zone at a constant value, unable to respond to anything.

**Configure `Lower floor temperature sensor`** (Step 1, or Options → Entities)
and both problems go away: the zone is measured, and slab-to-room becomes a real
difference again. It is optional and two-zone only. Without it the old estimate
is still used, so nothing changes for existing installations until you add one.

The order of preference is: a real sensor, then the floor return estimate, then
the upper floor's temperature.

### Backward Compatibility

When two-zone parameters are not configured, the model falls back to single-zone operation. DHW optimization is only active when a DHW temperature sensor or DHW tank volume is configured.

### Knowing when a sensor has gone bad

Every sensor read is guarded against `unavailable` and `unknown`. Those are the
easy failures: they are visible, and everything downstream already handles them.

The dangerous failure is a sensor that stops updating while continuing to report
its last value. A dead battery in a tank probe, or a dropped Zigbee room sensor,
leaves a perfectly valid-looking constant in the state machine indefinitely. Two
things then go wrong, and the second is worse:

1. The optimizer plans against a fiction.
2. The learners observe a flatline, attribute it to thermal behaviour, and
   corrupt a parameter that is then persisted — so the damage survives a
   restart.

So each input has a maximum age, and an over-age value is treated as **missing**
rather than as data. The learners freeze rather than training on it. A room
temperature may reasonably be minutes old and an outdoor forecast hours, so the
limits differ per input. The **Input Problem** binary sensor names which inputs
are stale, how old they are, and why the learners paused.

This is on by default, because it protects everything else and costs nothing.

### Measuring rather than assuming

Three optional entities change how much the integration can actually know:

| Entity | What it unlocks |
|---|---|
| Heat pump power meter | Real COP, predicted-versus-actual cost, reliable wood-furnace detection |
| Whole-house power meter | A capacity tariff model that sees the peak the grid actually bills |
| Cumulative energy meter | Cost accounting against a real meter rather than integrated power |

Watts, kilowatts and megawatts are all accepted and normalised. An unrecognised
unit is refused rather than guessed: a wrongly scaled power value is worse than
no power value, because everything downstream trusts it.

Note that **Recommended Power** is what the optimizer is *commanding* and
**Measured Power** is what the pump is *drawing*. They are deliberately named to
keep that distinction visible.

### Capacity (effekt) tariffs

Many Swedish grid companies bill a monthly capacity charge based on your highest
hours — commonly the mean of the three highest. Without modelling that, the
optimizer will happily stack hot water and space heating into the same cheap
hour, and one new monthly peak can easily cost more than the energy that
stacking saved.

Two details matter:

- **Only exceeding the peak already billed this month costs anything.** If the
  month has a 9 kW peak recorded, an 8 kW hour is free — the bill is already
  set. Treating this as "keep power low" would give away savings for nothing.
- **The penalty is soft.** A hard cap would fight the comfort band and could
  make a cold morning infeasible. What is wanted is a price signal the optimizer
  trades off like any other.

Take the price per kW and the number of peaks averaged from your grid invoice;
they vary a lot between grid companies.

### Prices past the published horizon

Nord Pool and Tibber publish tomorrow's prices around 13:00. Before then, a
large part of a 24-hour-plus horizon has no data at all.

That gap used to be filled by repeating the last known price. A flat tail has no
trough, so the optimizer could not see a cheap period ahead worth waiting for,
and systematically under-deferred load in the morning — precisely when deferral
is most valuable.

Instead, a normalised daily price *shape* is learned from the prices you have
actually seen, split weekday/weekend, and scaled to the recent price level. It
never displaces published data, it is heavily damped until several days have
been observed, and the plan records which steps rest on it. The dashboard card
shades that stretch of the chart, because a plan that looks identical whether or
not it rests on real prices cannot be audited.

### Wood furnaces and other external heat

If something other than the heat pump is charging your tanks — typically a wood
furnace on the same buffer — paying for electric hot water at the same time is
the most expensive mistake available.

Detection uses sensors you already have: a tank warming while the compressor is
off, or warming faster than the compressor could possibly manage. If you have a
flue thermostat or a stove switch, point the integration at it and that is
trusted instead.

The detector is deliberately reluctant, because the two errors do not cost the
same. Wrongly believing a fire is lit means skipping a cheap-hours charge and
either paying peak prices later or running out of hot water; missing one costs a
single unnecessary charge. So it wants several consecutive confirmations, and it
keeps assuming the fire for a while after the rise stops, since a fire dies down
gradually and re-planning a full charge the moment it drops would be wrong.

While it is active, discretionary electric hot water is suppressed — but only
while coasting still meets your requirement — and the learners freeze. If the
fire gets the tank all the way to the anti-legionella temperature, the existing
cycle timer resets on its own and no electric cycle is scheduled at all.

**With three more sensors, the fire stops being all-or-nothing.** If your
furnace heats its own buffer tank and an automatic valve mixes the two tanks,
point the integration at the temperature after that valve and at the wood
tank's top and bottom probes (all optional, on the learning page). The outlet
is the one sensor that measures what the house actually receives: together
with the tank temperatures it says how much of the heating the fire covers
right now — the furnace is doing 70 %, so electric space heating stands down
by 70 % — and the plan is given that free heat for a strictly bounded window:
never more than two hours ahead, fading over it, and never more energy than
the wood tank measurably holds. The tank pair also ends the
keep-assuming-the-fire window early once a hot top sits over a cold bottom,
because that charge is nearly spent whatever the timer says. Measurement is
only ever allowed to argue for *less* trust in the fire, never more: a wrong
promise of free heat is a cold house in winter.

Off by default: most users have no such source, and a feature that cannot save
them anything should not be able to cost them anything.

### Away and holiday mode

A week away is the largest single saving a heating system can offer: a deep
setback plus hot water suppressed entirely.

What makes this more than a manual setpoint is the **return time**. Knowing when
the house must be comfortable again lets the recovery heat be bought in the
cheapest hours beforehand, instead of panic-heating on arrival at whatever the
spot price happens to be. That is the same deadline-driven machinery the hot
water planner already uses, applied to the building.

Away state can come from a person, a device tracker, a calendar entry or a plain
toggle. The polarity differs by domain — a person is `not_home` when away, a
holiday toggle is `on` — and that is handled for you. Recovery starts
deliberately early, because a wrong return time is a comfort failure you will
notice.

### Why a slot was chosen

Each planned slot now carries a reason code: cheapest hours, holding the minimum
temperature, pre-heating before colder weather, using solar surplus, the
anti-legionella cycle, and so on. It appears in the plan sensor attributes and
in the card's tooltip.

This is a small change with a disproportionate effect: without it, an unexpected
slot is indistinguishable from a bug, which makes the optimizer hard to trust
and bug reports much weaker than they could be.

### Grid costs beyond the price per kWh

Two things cost money that the spot price does not describe.

**A capacity tariff** is billed as the price per kW times the mean of the
month's highest few hourly peaks. The cost of a plan is therefore the marginal
price times the sum of its top-k excesses above what the month has already
committed to — charging only the single largest, which is the obvious
simplification, under-states exactly the plan a capacity tariff exists to
discourage. Below the running threshold, an hour changes nothing and costs
nothing; and until the month has recorded some peaks there is no reference at
all, so the charge stays switched off rather than treating every kW as new.

**A compressor start** costs oil dilution, wear, and the loss while the system
re-establishes steady state. It is modelled as a smooth term on the
step-to-step power difference, which keeps the problem continuous — a true
minimum-runtime constraint would make it a MILP, which is not affordable inside
a Home Assistant update. It defaults to zero because the measurement came
first: realistic plans make two to four starts a day, so most installs have
nothing to fix, and the planned start count is published so the decision can be
made from evidence.

### Self-learning, and how to see it

Beyond the tank cooling rates and house heat loss learned in earlier versions:

- **COP** becomes observable with a power meter, instead of being derived from a
  nominal figure and a temperature curve.
- **A defrost derate** is learned per outdoor-temperature and humidity bucket
  from predicted-versus-actual performance. Air-source units lose real capacity
  in the 0 to +5 °C humid band, which is exactly the Swedish shoulder season and
  exactly where the plan is most aggressive about coasting. The derate is
  learned rather than taken from a datasheet, because units vary far more than
  the effect being modelled. With no evidence it is exactly 1.0.
- **Comfort weight** can be learned from your own overrides (opt-in). Every time
  you override the temperature you are saying the plan went too far in one
  direction, which is the only evidence anyone ever produces about a number that
  has no intuitive units. It moves slowly, needs consistent evidence, and has
  its own sensor and a reset button — an invisible self-adjusting objective
  would be alarming.
- **Active system identification** (opt-in) runs a small deliberate heating step
  on a mild, cheap night and fits the response, getting the time constant and
  loss coefficient in days rather than the weeks passive learning needs. The
  step is kept small enough not to be noticed, and comfort is a hard constraint:
  it aborts if the room drifts too far. It will not repeat on a house that has
  already converged.

The **Prediction Accuracy** sensor publishes how far off the model currently is,
including the *signed* bias — a mean absolute error cannot tell random noise from
a model that is consistently half a degree optimistic, and it is the second that
means the model is drifting.

Measured end to end in `tests/rolling.py`: given a house that loses 35% more
heat than its configuration says, the correction recovers 99% of that error
within two simulated days, settles rather than oscillating, and leaves an
already-correct model alone.

## Configuration

### Step 1: API & Entity Selection
| Parameter | Description | Required |
|---|---|---|
| Tibber API token | Get from https://developer.tibber.com | Yes |
| Weather entity | HA weather entity for forecasts | Yes |
| Indoor temp sensor | Room temperature sensor | No |
| Outdoor temp sensor | Outdoor temperature sensor | No |
| Heat pump climate entity | To control the heat pump | No |
| Heat pump switch | On/off switch for heat pump | No |
| Solar radiation sensor | W/m² irradiance sensor | No |
| Solar forecast source | `Weather entity` or `Open-Meteo`; see below | No |
| Solar location | Map coordinate used when the source is Open-Meteo | No |
| Floor return temp sensor | Floor heating return temp | No |
| Lower floor temp sensor | Real thermometer on the lower floor (two-zone); without it the zone is inferred from the return water and reads several degrees too warm | No |
| DHW temp sensor | Hot water tank temperature | No |
| Buffer tank temp sensor | Buffer tank temperature; enables cooling-rate learning | No |

### Step 2: Temperature Settings
| Parameter | Default | Range |
|---|---|---|
| Target temperature | 21.0°C | 15-28°C |
| Min temperature | 19.0°C | 14-25°C |
| Max temperature | 23.0°C | 18-28°C |
| Comfort temp (day) | 21.0°C | 16-26°C |
| Comfort temp (night) | 19.5°C | 15-24°C |
| Day starts | 07:00 | 0-12 |
| Day ends | 22:00 | 18-23 |

### Step 3: Thermal Model
| Parameter | Default | Unit |
|---|---|---|
| House thermal mass | 10.0 | kWh/°C |
| Heat loss coefficient | 0.15 | kW/°C |
| Slab thermal mass | 5.0 | kWh/°C |
| Slab heat transfer | 0.8 | kW/°C |
| HP nominal COP | 3.5 | - |
| HP max power | 5.0 | kW |
| HP min power | 1.0 | kW |

### Step 4: Two-Zone & Solar (Optional)
| Parameter | Default | Unit |
|---|---|---|
| Upper floor thermal mass | 3.0 | kWh/°C |
| Lower floor thermal mass | 8.0 | kWh/°C |
| Upper floor heat loss | 0.08 | kW/°C |
| Lower floor heat loss | 0.07 | kW/°C |
| Inter-zone transfer | 0.5 | kW/°C |
| Radiator power fraction | 0.4 | 0-1 |
| Buffer tank volume | 35 | L (10–1500) |
| Window area | 10 | m² |
| Solar orientation factor | 0.7 | 0-1 |
| SHGC | 0.7 | 0-1 |

### Step 5: DHW Configuration (Optional)
| Parameter | Default | Unit |
|---|---|---|
| DHW tank volume | 200 | L (50–1500) |
| DHW setpoint | 55 | °C |
| DHW minimum temperature | 45 | °C |
| Daily consumption | 150 | L/day |
| Tank cooling rate | 0.3 | °C/h at 45 °C tank, 20 °C room (0.05–3.0) |
| Only guarantee hot water during set time frames | on | — |
| Hot water time frames | `06:00-08:30, 17:00-22:00` | HH:MM-HH:MM, comma separated |
| Tank minimum outside the time frames | 20 | °C |
| Anti-legionella cycle | on | — |
| Anti-legionella temperature | 60 | °C |
| Anti-legionella interval | 7 | days |

The time frames are the periods when hot water must be available. Outside them
the tank may cool freely, which is where most of the savings come from. Leave
the field empty to let the optimizer learn the frames from observed usage, or
turn the toggle off to require hot water around the clock.

### Step 6: Weather Sensitivity
| Parameter | Default | Description |
|---|---|---|
| Wind sensitivity | 0.03 | 3% heat loss increase per m/s wind |
| Rain multiplier | 1.15 | 15% heat loss increase when raining |

## Entities Created

### Sensors (47 total)
| Sensor | Description |
|---|---|
| Optimization Mode | Current mode (auto/comfort/economy/boost/off) |
| Optimization Status | Solver status (optimal/suboptimal/failed) |
| Predicted Savings | Cost savings vs. baseline (SEK) |
| Savings Percentage | Savings as percentage |
| Predicted Cost | Optimized 24h cost (SEK) |
| Baseline Cost | Non-optimized 24h cost (SEK) |
| Current Electricity Price | Current Tibber price (SEK/kWh) |
| Optimal Setpoint | Current recommended setpoint (°C) |
| Recommended Power | Current recommended power (kW) |
| Estimated COP | COP at current outdoor temp |
| Indoor Temperature | Current indoor temp (optimizer) |
| Outdoor Temperature | Current outdoor temp (optimizer) |
| Slab Temperature | Estimated slab temperature (°C) |
| Next Optimization | Timestamp of next optimization run |
| Last Optimization | Timestamp of last optimization run |
| Heat Pump Action | Current action (off/eco/normal/pre_heat/boost) |
| Optimization Schedule | Full 24h schedule (in attributes) |
| Upper Floor Temperature | Upper floor (radiator zone) temp |
| Lower Floor Temperature | Lower floor (slab zone) temp |
| Floor Heating Return Temp | Floor return sensor reading |
| Solar Radiation | Current solar radiation (W/m²) |
| Solar Irradiance (Open-Meteo) | Open-Meteo irradiance, with the horizon in attributes |
| Solar Heat Gain | Current solar gain (kW) |
| Buffer Tank Temperature | Modeled buffer tank temp |
| **Space Heating Plan** | Planned space heating slots + full-horizon forecast |
| **DHW Heating Plan** | Planned hot water slots + full-horizon forecast |
| **DHW Temperature** | Current hot water temperature |
| **DHW Heating Schedule** | Planned DHW heating periods |
| **DHW Heating Cost** | Estimated DHW heating cost |
| **Predictive Insight** | Anticipatory control status |
| **Measured Power** | Actual electrical draw, when a power entity is configured |
| **Observed COP** | Efficiency derived from measurement rather than the nameplate curve |
| **Space Heating Energy** | Accumulating kWh, for the Energy dashboard |
| **Hot Water Energy** | Accumulating kWh, for the Energy dashboard |
| **Total Energy** | Accumulating kWh, for the Energy dashboard |
| **Space Heating Cost** | Accumulating cost |
| **Hot Water Cost** | Accumulating cost |
| **Total Heating Cost** | Accumulating cost |
| **Prediction Accuracy** | Mean error of the predicted indoor temperature, with the bias in attributes |
| **Monthly Peak Power** | Peak the capacity tariff is currently billed on, and the free headroom |
| **Solar Surplus Forecast** | Forecast PV surplus available to the heat pump |
| **Thermal Battery Charge** | State of charge of the house and tanks, against the comfort band |
| **Thermal Battery Energy** | Stored energy available above the comfort floor |
| **Comfort Weight** | The comfort weight in force, learned or configured |
| **Valve Target Recommendation** | What to set a dumb mixing valve to, with the reasoning in its attributes |

### Binary Sensors (3 total)
| Binary sensor | Description |
|---|---|
| **Input Problem** | On when an input is stale or missing, with the evidence and the freeze reason in attributes |
| **External Heat Source** | On while something other than the heat pump is heating the tanks |
| **Away Mode** | On while the house is empty, with the return time and recovery state |

### Buttons (3 total)
| Button | Description |
|---|---|
| **Optimize Now** | Force an optimization run. Unavailable while one is in flight |
| **Run System Identification** | Arm the commissioning step test for the next mild, cheap night |
| **Reset Learned Comfort Weight** | Undo the revealed-preference tuning |

### Dashboard Card

`custom:heatpump-optimizer-card` charts electricity price, planned hot water
slots, planned space heating slots, outdoor temperature, solar irradiance,
predicted tank temperature and predicted house temperature on one shared time
axis. Each series has a legend chip that toggles it on and off, and the choice
is remembered. Hovering a slot shows *why* it was planned, and the stretch of
the horizon whose prices are estimated rather than published is shaded. The
integration serves and registers the card automatically. See
[docs/dashboard-card.md](docs/dashboard-card.md).

```yaml
type: custom:heatpump-optimizer-card
# Optional: set to false to hide the schedule editor in the enlarged view.
what_if: true
```

**Click the card to enlarge it.** The enlarged view draws today's plan again as
two editable lanes. Drag a block to move it, drag an edge to resize it, and
right-click a lane to add or remove one. A running total prices your arrangement
against the plan in force, and **Apply this plan** pins it for the next 20
hours — the
optimizer keeps re-solving, but has to schedule around your slots.

**Pan and zoom the plan window.** Pinch to zoom (or hold Ctrl and scroll), swipe
sideways with two fingers to pan, or drag the chart background. The buttons above
the chart do the same for touch and keyboard. It is forward-only — there is no
stored history to scroll back into, because plan forecasts are deliberately kept
out of the recorder — so the window stays between now and the end of the plan,
and zooming out stops at the plan's real extent rather than showing empty chart.
A plain scroll is left alone so the dashboard still scrolls under the pointer.

Timing is yours; safety is not. If an arrangement would let the tank fall below
its minimum, skip a legionella cycle or take the house under its comfort floor,
the integration releases only the slots it must and tells you which. The past,
and anything past midnight, is locked.

Below that is a panel where you can drag the comfort temperature, move the
heating day, and add or remove hot water windows:

* **Simulate these slots** prices the change against the current forecast and
  reports the difference. Nothing is applied, and nothing is saved.
* **Save as my schedule** writes the edited schedule into your configuration and
  reloads the integration, so the next plan is made against it. It asks for a
  second press first, because it replaces what the house actually runs on.
* **Reset** discards the draft and returns to the schedule now in force.

Both are shown by default: holding a draft costs nothing, and only the buttons
reach Home Assistant. Set `what_if: false` to hide them.

### Climate Entity
- Virtual thermostat with HVAC modes and presets
- Attributes include zone temperatures, DHW status, and predictive optimization insights

### Switch Entity
- Enable/disable the optimizer

## Services

### `heatpump_optimizer.run_optimization`
Manually trigger a predictive optimization run.

### `heatpump_optimizer.set_mode`
Set operation mode: auto, comfort, economy, boost, off.

### `heatpump_optimizer.simulate_plan`
Prices a hypothetical comfort choice against the current forecast without
disturbing operation, and returns the cost difference against the live plan.
This is what the card's what-if simulator calls. The solve is rate-limited, so
rapid repeat calls return the previous answer rather than queueing work.

### `heatpump_optimizer.apply_schedule`
Writes a schedule into your configuration and reloads the integration, so the
next plan is made against it. This is what the card's **Save as my schedule**
button calls. Every field is optional; only what you pass is changed.

```yaml
service: heatpump_optimizer.apply_schedule
data:
  day_start_hour: 6          # comfort period starts
  day_end_hour: 22           # comfort period ends
  dhw_windows: "06:00-08:30, 17:00-22:00"
  comfort_temp_day: 21.0
  dhw_min_temperature: 45.0  # lowest usable tank temperature in a window
```

The windows are validated and canonicalised before they are stored, so a
malformed schedule is rejected here rather than failing on every later reload.

`dhw_min_temperature` must stay a few degrees below your hot water setpoint. A
minimum equal to the setpoint leaves the tank no band to work in, so the pump
would short-cycle against its own hysteresis; a value that close is rejected
rather than quietly accepted. The limit is checked per heat pump, because the
setpoint is configured per heat pump.

### `heatpump_optimizer.apply_manual_plan`
Pins today's heating and hot water slots, so the optimizer plans around them
instead of choosing them. This is what the card's **Apply this plan** button
calls.

```yaml
service: heatpump_optimizer.apply_manual_plan
data:
  dhw_slots:
    - start: "2026-01-15T13:00:00+01:00"
      end: "2026-01-15T14:30:00+01:00"
  expires_at: "2026-01-16T00:00:00+01:00"   # optional, defaults to 20 hours from now
```

A channel you leave out stays fully automatic. Passing an explicit empty list is
different, and means "do not run this at all until the override expires" — so
`dhw_slots: []` switches hot water off for the whole pinned window.

The pins constrain *timing only*. Tank minimums, legionella and the house
comfort floor still override them: if your slots cannot be made safe, the
integration releases the ones it has to, re-solves, and reports them in the
`manual_override` attribute of the plan sensors. The plan is persisted, so it
survives a restart, and it is dropped once it expires.

### `heatpump_optimizer.clear_manual_plan`
Removes the override and re-solves, returning to fully automatic planning. This
is the card's **Back to automatic** button.

### `heatpump_optimizer.set_thermal_parameters`
Runtime parameter tuning:
```yaml
service: heatpump_optimizer.set_thermal_parameters
data:
  house_thermal_mass: 12.0
  wind_sensitivity_factor: 0.20
  rain_heat_loss_multiplier: 1.20
  dhw_setpoint: 55
  dhw_min_temperature: 45
  dhw_cooling_rate: 0.3
  window_area: 15.0
  solar_heat_gain_coefficient: 0.65
```

## Troubleshooting

### Temperature swings between zones
- Adjust `inter_zone_heat_transfer` (higher for open layouts)

### Solar over-heating in summer
- Reduce `window_area` or `solar_heat_gain_coefficient`
- Consider seasonal shading effects

### Floor heating slow response
- This is expected — slab has high thermal mass
- The optimizer accounts for this by pre-heating during cheap periods

### DHW too cold / too often heated
- Check the **hot water time frames** first — hot water is only guaranteed
  inside them, and outside them the tank is *meant* to cool down
- Water cold when you need it? Widen the time frame, or start it earlier
- Water cold at the very start of a frame? Raise `dhw_min_temperature`
- Still heating during expensive hours? The tank probably cannot store enough
  to bridge the peak — raise `dhw_setpoint` so more cheap energy fits in the
  tank, or shorten the time frame
- Decrease `dhw_daily_consumption` if the tank stays warmer than you need
- The `DHW Temperature` sensor exposes `dhw_in_demand_window`,
  `dhw_next_window_in_hours` and `dhw_required_temperature` so you can see
  exactly what the optimizer is being asked to deliver right now
- It also exposes `dhw_cooling_rate` (°C/h at 45/20 °C),
  `dhw_cooling_rate_learned`, `dhw_cooling_samples` and `dhw_hold_hours`. If the
  learned rate looks far too high, the tank sensor is probably seeing draws that
  the model reads as standby loss; set the rate explicitly with
  `set_thermal_parameters` (`dhw_cooling_rate`) to reset the estimate.

### Predictive optimization not working
- Check that your weather entity provides hourly forecasts
- Check the "Predictive Insight" sensor for forecast analysis
- Solar anticipation requires solar irradiance in weather data
- Wind/rain anticipation requires wind_speed and precipitation in forecasts

## Architecture

```
custom_components/heatpump_optimizer/
├── __init__.py          # Entry point, service registration
├── const.py             # Constants and configuration keys
├── config_flow.py       # UI config: setup steps plus 11 editable option pages
├── coordinator.py       # Data fetching, full 24h forecasts, learners, state
├── thermal_model.py     # Two-zone model + DHW tank + enhanced wind/rain loss
├── optimizer.py         # Predictive MPC, DHW co-planning, reason codes
├── dhw_schedule.py      # Hot water demand time frame parsing and evaluation
├── open_meteo.py        # Solar irradiance forecast and satellite observations
│
│   # Feature modules, each independently testable
├── inputs.py            # Guarded sensor reads: freshness and unit handling
├── external_heat.py     # Wood-furnace detection with hysteresis and decay
├── price_model.py       # Learned diurnal price shape for the unknown horizon
├── tariff.py            # Monthly capacity (effekt) tariff and peak tracking
├── pv.py                # PV production model and marginal-cost pricing
├── away.py              # Away state, return time and recovery scheduling
├── accuracy.py          # Predicted-versus-realised recording and drift metrics
├── defrost.py           # Learned COP derate by outdoor temperature and humidity
├── presets.py           # Building archetypes → thermal parameters
├── sysid.py             # Active step-response identification
├── comfort_learning.py  # Revealed-preference comfort weight tuning
├── battery.py           # The thermal stores, published as a battery
│
├── sensor.py            # 47 sensors
├── binary_sensor.py     # Input health, external heat, away mode
├── button.py            # Optimize now, run identification, reset comfort weight
├── climate.py           # Virtual climate entity with DHW status
├── switch.py            # Enable/disable switch
├── frontend.py          # Serves and registers the Lovelace card
├── www/                 # The dashboard card
├── services.yaml        # Service definitions
├── strings.json         # UI strings
├── translations/
│   ├── en.json          # English translations
│   └── sv.json          # Swedish translations
└── manifest.json        # Integration manifest
```

Everything in the feature-module block is deliberately free of Home Assistant
imports, so each can be driven directly by `tests/features.py`. That matters
because their failure mode is a *plausible* plan: a detector that never fires or
a watchdog that lets a flatline through produces output that looks entirely
normal, and only a mechanism-level test will catch it.

### How a plan is made

```
prices ─┐
weather ┼─► coordinator._forecast_arrays()  ──► _Horizon  ──► optimizer.optimize()
solar  ─┘        │                                                    │
                 ├─ learned price shape fills the unpublished tail    ├─ with hot water:
                 ├─ PV surplus replaces the import price              │    plan the tank by LP,
                 └─ Open-Meteo overrides irradiance by timestamp      │    then solve space
                                                                      │    around it, then
                                                                      │    re-plan the tank
                                                                      │    against contention
                                                                      └─ without: solve directly
                                                                             │
   entities ◄── coordinator._build_data_dict() ◄── OptimizationResult ◄──────┘
                     │
                     └─ composed from per-domain views (thermal, dhw, learning,
                        measurement, grid, ECL110, external heat, health)
```

Both optimizer paths share one set of cost terms — the comfort penalty, the
terminal cost, the cycling and capacity charges — so enabling hot water cannot
change the space-heating objective. That is not hypothetical tidiness: it used
to, and the two objectives had silently drifted apart.

## Roadmap

Known bugs and planned work are tracked in
[docs/backlog.md](docs/backlog.md), which records each item together with the
investigation behind it — the code that causes it, what was measured, and what
a fix has to be careful of. Items 1-21 are released; 22-31 are open.

## Requirements

- Home Assistant 2024.1.0 or newer
- Tibber account with API access
- Weather integration with hourly forecasts (recommended: Met.no or similar)
- Python packages: `numpy`, `scipy`

## Changing settings after setup

Open the integration and choose **Configure**. Instead of one long form you get
a menu, and each page can be edited independently:

| Page | What it covers |
|---|---|
| Sensors and entities | Tibber token, weather entity, and every optional sensor including the power meters |
| Comfort and temperatures | Target, minimum and maximum temperature, day/night hours |
| Hot water | Tank size, temperatures, demand time frames, anti-legionella |
| House and heating system | Heat loss, thermal mass, windows, two-zone settings |
| Building type and emitters | Structure, era, foundation, area and emitters, which derive the page above |
| Savings vs comfort | Price weight, comfort weight, recalculation interval |
| Grid costs and cycling | Capacity tariff, compressor start cost, price prior |
| Solar panels | Array size, efficiency, export compensation |
| Away and holiday mode | Presence source, return time, setback temperatures |
| Self-learning and diagnostics | Staleness watchdog, external heat detection, comfort learning, identification |
| Heat curve control (ECL110) | Heat curve points and offsets |

Every sensor you picked during setup can be re-pointed here, including the
solar radiance sensor. Clearing a field genuinely clears it. Every field has a
plain-language description, so you should not need this table to understand
what a setting does.

### How hard the optimizer chases low prices

The single most useful setting is **How strictly to hold the temperature**
(`comfort_weight`), on the Tuning page. It is weighed against the range you
allow, so it interacts directly with your minimum temperature: a wide range
gives the optimizer room to shift heating into cheap hours, and a narrow one
keeps it near the setpoint.

Measured on a cold January day in SE3 with a target of 21 °C and a minimum
of 17 °C:

| Comfort weight | Average room temp | Savings |
|---|---|---|
| 5 (default) | 19.4 °C | 53% |
| 10 | 19.8 °C | 51% |
| 20 | 20.2 °C | 49% |
| 40 | 20.4 °C | 47% |

If the house feels cooler than you want, raise this value or raise your minimum
temperature. Both work, and both trade savings for warmth.

## Installation

### HACS (Recommended)
1. Add this repository to HACS as a custom repository
2. Install "Heat Pump Cost Optimizer"
3. Restart Home Assistant
4. Configure via Settings → Integrations → Add → Heat Pump Cost Optimizer

### Manual
1. Copy `custom_components/heatpump_optimizer` to your HA `custom_components` folder
2. Restart Home Assistant
3. Configure via the UI

## License

MIT. See [LICENSE](LICENSE).

This project is a fork of
[strutsfarm/heatpump_optimizer](https://github.com/strutsfarm/heatpump_optimizer),
which is also MIT licensed; the upstream copyright is retained alongside this
project's own. See the [Acknowledgement](#acknowledgement) and
[Disclaimer](#disclaimer) at the top of this file.

## ECL110 MQTT Control (Heat Pump ON/OFF + Displace)

This integration can now drive an ECL110-compatible controller using two explicit outputs from MPC:

- `heat_pump_on` (boolean): whether supply should be enabled
- `displace_value` (°C): parallel shift command for ECL110 heat curve (published as integer to ECL110)

### MQTT command publishing

The coordinator now publishes the **preferred direct-write command** as a plain number to:

- `ecl110_displace_set_topic` (default: `ecl110/flow_temp_control/displace/set`)

Example payload:

```text
4
```

For backward compatibility, it can also publish a **legacy JSON payload** to:

- `ecl110_command_topic` (default: `ecl110/command`)

```json
{
  "source": "heatpump_optimizer",
  "reason": "scheduled_update",
  "timestamp": "2026-01-01T12:00:00+00:00",
  "command": {
    "type": "ecl110_control",
    "heat_pump_on": true,
    "displace": 4
  },
  "context": {
    "price": 1.23,
    "mode": "pre_heat",
    "pre_heat_urgency": 0.6
  }
}
```

### New configuration options

- `ecl110_displace_set_topic`
- `ecl110_command_topic` (legacy JSON path)
- `ecl110_state_topic`
- `ecl110_mqtt_qos`
- `ecl110_mqtt_retain`
- `ecl110_displace_min` / `ecl110_displace_max`
- `ecl110_pid_time_constant_hours`

### PI/PID dynamics handling

ECL110 PI/PID response is approximated as a first-order lag, so internal displace commands are smoothed before dispatch, then rounded to integer values for MQTT output, and an `effective_displace` state is tracked for observability.