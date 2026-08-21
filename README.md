# Heat Pump Cost Optimizer for Home Assistant

A custom Home Assistant integration that uses **Model Predictive Control (MPC)** to optimize heat pump operation and minimize electricity costs, while maintaining indoor comfort and domestic hot water availability. Integrates with **Tibber** for dynamic electricity prices and Home Assistant weather entities for temperature, wind, rain, and solar forecasts.

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
- **Self-learning thermal parameters** — tank cooling rates and house heat loss are estimated from your own house
- **Rich sensor entities** — 29 sensors including full heating plans, DHW, predictive insights, per-zone temperatures
- **Dashboard card** — plots price, planned heating slots and predicted temperatures on one graph with per-series toggles
- **Climate entity** — virtual thermostat with full HA climate integration
- **Service calls** — manual optimization, mode changes, runtime parameter tuning

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
- **Wind effect**: Convective heat loss increases by `wind_sensitivity × wind_speed` (default 15% per m/s)
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
is configured; without one the configured default is used unchanged.

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

**Wind effect** (convective heat transfer):
```
U_effective = U_base × (1 + wind_sensitivity × wind_speed)
```
- Default: 15% increase per m/s wind speed
- Example: 5 m/s wind → 75% higher heat loss coefficient
- Uses FORECASTED wind speed at each future time step

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

### Floor Return Temperature Feedback

When a floor heating return temperature sensor is configured, the optimizer uses it to correct the slab temperature model:
```
T_slab_estimated = 0.7 × (T_return + 1°C) + 0.3 × T_slab_model
```

### Backward Compatibility

When two-zone parameters are not configured, the model falls back to single-zone operation. DHW optimization is only active when a DHW temperature sensor or DHW tank volume is configured.

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
| Floor return temp sensor | Floor heating return temp | No |
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
| Wind sensitivity | 0.15 | 15% heat loss increase per m/s wind |
| Rain multiplier | 1.15 | 15% heat loss increase when raining |

## Entities Created

### Sensors (29 total)
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
| Solar Heat Gain | Current solar gain (kW) |
| Buffer Tank Temperature | Modeled buffer tank temp |
| **Space Heating Plan** | Planned space heating slots + full-horizon forecast |
| **DHW Heating Plan** | Planned hot water slots + full-horizon forecast |
| **DHW Temperature** | Current hot water temperature |
| **DHW Heating Schedule** | Planned DHW heating periods |
| **DHW Heating Cost** | Estimated DHW heating cost |
| **Predictive Insight** | Anticipatory control status |

### Dashboard Card

`custom:heatpump-optimizer-card` charts electricity price, planned hot water
slots, planned space heating slots, outdoor temperature, predicted tank
temperature and predicted house temperature on one shared time axis. Each series
has a legend chip that toggles it on and off, and the choice is remembered. The
integration serves and registers the card automatically. See
[docs/dashboard-card.md](docs/dashboard-card.md).

```yaml
type: custom:heatpump-optimizer-card
```

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
├── const.py             # Constants (incl. DHW + weather sensitivity)
├── config_flow.py       # UI config (6 steps: user, temp, thermal, zones, dhw, weather)
├── coordinator.py       # Data fetching, full 24h forecasts, DHW state
├── thermal_model.py     # Two-zone model + DHW tank + enhanced wind/rain loss
├── dhw_schedule.py      # Hot water demand time frame parsing and evaluation
├── optimizer.py         # Predictive MPC with solar/wind/rain anticipation + DHW
├── sensor.py            # 27 sensors (incl. DHW + predictive insights)
├── climate.py           # Virtual climate entity with DHW status
├── switch.py            # Enable/disable switch
├── services.yaml        # Service definitions (incl. DHW + weather params)
├── strings.json         # UI strings
├── translations/
│   ├── en.json          # English translations
│   └── sv.json          # Swedish translations
└── manifest.json        # Integration manifest
```

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
| Sensors and connection | Tibber token, weather entity, and every optional sensor |
| Comfort | Target, minimum and maximum temperature, day/night hours |
| Hot water | Tank size, temperatures, demand time frames, anti-legionella |
| Building | Heat loss, thermal mass, windows, two-zone settings |
| Tuning | Price weight, comfort weight, horizon, forecast handling |
| Heat curve | Heat curve points and offsets |

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
| 5 (default) | 19.1 °C | 45% |
| 10 | 19.5 °C | 42% |
| 20 | 19.9 °C | 38% |
| 40 | 20.1 °C | 36% |

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

MIT

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