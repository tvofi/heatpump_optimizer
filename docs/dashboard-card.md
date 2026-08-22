# Heat Pump Optimizer dashboard card

`custom:heatpump-optimizer-card` is a self-contained Lovelace card that plots the
optimizer's planning series on a single shared time axis:

- **Electricity price** (SEK/kWh, right axis, stepped filled area)
- **DHW heating** power (kW, left power axis, stepped filled band)
- **Space heating** power (kW, left power axis, stepped filled band)
- **Outdoor temperature** (°C, left temperature axis, smooth line)
- **DHW tank temperature** (°C, left temperature axis, smooth line)
- **House temperature** (°C, left temperature axis; upper/lower zones drawn as
  dashed lines when the house is configured as two-zone)
- **Solar irradiance** (W/m², inner right axis, stepped filled area)

Every series has a clickable legend chip. Toggling a chip hides/shows the series
and rescales the axes to the visible data. The chart is drawn as hand-written
inline SVG — there is **no** dependency on Chart.js, ApexCharts, npm or any CDN.

A vertical "now" marker is drawn at the current time, and hovering (or touching)
the plot shows a crosshair and a tooltip with the value of every visible series
at the nearest sample, plus **why** the plan is heating at that moment.

### The solar irradiance axis

W/m² is a fourth unit and both plot edges were already occupied by the
temperature/power axes on the left and the price axis on the right. Irradiance
therefore gets its own axis just inside the price one, and the plot only gives
up that width when the series is actually visible — a permanently narrower chart
would be a real cost to everyone who does not use it.

Scaling irradiance into the existing power axis as kW/m² was the alternative,
but a 0.8 kW/m² line sharing a scale with a 5 kW compressor is unreadable.

### Reason codes and estimated prices

Hovering a planned slot shows why it was chosen: cheapest hours, holding the
minimum temperature, pre-heating before colder weather, using solar surplus, the
anti-legionella cycle, and so on. Without this an unexpected slot is
indistinguishable from a bug.

The stretch of the horizon whose prices have not been published yet — Nord Pool
and Tibber release tomorrow around 13:00 — is shaded and labelled *estimated
prices*. Those hours rest on the integration's learned daily price shape rather
than on market data, and a plan that looks identical either way cannot be
audited.

## Enlarging the chart

A dashboard card is usually too small to read a 48-hour plan comfortably.
Clicking anywhere on the card, or the expand button in its header, opens the
same chart in a large modal overlay. The enlarged view labels the time axis
every hour instead of every third hour, since it has the room for it.

Clicking a legend chip only toggles that series; it does not open the overlay.
Toggles work inside the overlay too, and the visibility state is shared with the
card underneath. Close it with the X, the Escape key, or by clicking outside it.

The legend and the chart text are both scaled up in the overlay. The legend is
plain HTML sized in `em` against the card's font, which does not grow with the
dialog, so without that it stayed at card size next to a much larger chart and
read as cramped. SVG text has the same problem for a different reason: it is
sized in viewBox units, so the same nominal size spread across a larger area
looks smaller even though it is still vector.

### What-if simulator

Setting `what_if: true` adds a comfort-temperature slider to the enlarged view.
Dragging it shows what that temperature would cost per month, against the plan
currently in force.

Setpoints are otherwise chosen blind: the optimizer can price a plan, but you
never see the price of your own comfort choices. This turns "I set 21 because it
sounds about right" into an informed decision.

It is off by default because each answer is a real optimization solve on the
Home Assistant host. The slider is debounced in the card and the solve is
rate-limited in the integration, so dragging cannot trigger one per pixel, and
it runs against a *copy* of your configuration — an exploratory drag never
disturbs actual operation.

The overlay is a native `<dialog>` shown with `showModal()`, so it renders in
the browser's top layer and cannot be clipped by a dashboard column or hidden
behind another card. Its width is capped so the chart's aspect ratio still fits
the viewport height, because stretching the box instead would distort the axis
labels.

## Installation

### Automatic (recommended)

When you install the integration through HACS and add a config entry, the card is
served and registered automatically:

1. The integration exposes the JS at `/heatpump_optimizer_static/heatpump-optimizer-card.js`.
2. If your dashboards use **storage mode** (the default UI-managed dashboards),
   the Lovelace resource is registered for you on setup.
3. Reload your browser (hard refresh) so the new resource is loaded, then add a
   card and pick **Heat Pump Optimizer Card**, or paste one of the YAML examples
   below.

If you don't see the card in the picker, hard-refresh the browser (the resource
is cache-busted by integration version, but the browser may still hold an old
module).

### Manual resource registration (fallback)

If your dashboards are in **YAML mode**, or automatic registration failed for any
reason, add the resource yourself.

**UI (storage mode):** Settings → Dashboards → ⋮ → Resources → Add resource

- URL: `/heatpump_optimizer_static/heatpump-optimizer-card.js`
- Resource type: **JavaScript Module**

**YAML mode:** add to your `configuration.yaml` / dashboard YAML:

```yaml
lovelace:
  mode: yaml
  resources:
    - url: /heatpump_optimizer_static/heatpump-optimizer-card.js
      type: module
```

Restart or reload the dashboard afterwards.

## Configuration options

```yaml
type: custom:heatpump-optimizer-card
title: Heat pump plan                    # optional, default "Heat pump plan"
space_entity: sensor.heat_pump_optimizer_space_heating_plan  # optional, auto-detected
dhw_entity: sensor.heat_pump_optimizer_dhw_heating_plan      # optional, auto-detected
solar_entity: sensor.heat_pump_optimizer_solar_irradiance    # optional, auto-detected
hours: 24                                # optional, hours forward to plot, default 24 (1–168)
what_if: false                           # optional, comfort slider in the enlarged view
series:                                  # optional, initial per-series visibility
  price: true
  dhw_slots: true
  space_slots: true
  outdoor: true
  dhw_temp: true
  house_temp: true
  solar: true
```

| Option         | Type    | Default                        | Description |
|----------------|---------|--------------------------------|-------------|
| `type`         | string  | —                              | Must be `custom:heatpump-optimizer-card`. |
| `title`        | string  | `Heat pump plan`               | Card header text. |
| `space_entity` | string  | auto-detected                  | Entity id of the space-heating plan sensor (its `forecast` attribute supplies `price`, `outdoor`, `space_power`, `room`, `upper`, `lower`). |
| `dhw_entity`   | string  | auto-detected                  | Entity id of the DHW plan sensor (its `forecast` attribute supplies `dhw_power`, `dhw_temp`, and `price`/`outdoor` fallbacks). |
| `solar_entity` | string  | auto-detected                  | Entity id of the solar irradiance sensor (its `forecast` attribute supplies `ghi`). |
| `hours`        | number  | `24`                           | How many hours forward to plot. Must be `1`–`168`. |
| `what_if`      | boolean | `false`                        | Show the comfort-temperature what-if slider in the enlarged view. Each drag triggers a real optimization solve, so this is opt-in. |
| `series`       | map     | all `true`                     | Initial visibility per series key. Keys: `price`, `dhw_slots`, `space_slots`, `outdoor`, `dhw_temp`, `house_temp`, `solar`. |

### Entity discovery

The plan sensors use `has_entity_name`, so Home Assistant prefixes them with the
device name. A stock install produces
`sensor.heat_pump_optimizer_space_heating_plan` and
`sensor.heat_pump_optimizer_dhw_heating_plan`.

You normally do not need to configure either option. The card resolves entities
in this order:

1. The id you configured, if that entity exists.
2. Any `sensor` whose `plan_kind` attribute is `space`, `dhw` or `solar`. This
   is a stable marker published by the integration, so renaming an entity does
   not break the card.
3. Any `sensor` whose id ends in `space_heating_plan` / `dhw_heating_plan` /
   `solar_irradiance`, for integration versions older than 2.6.1.

If nothing is found the card names the id it looked for, so check
**Developer Tools → States** and set the option explicitly.

Toggle state is remembered in the browser's `localStorage`, keyed by the two
entity ids, so it survives page reloads. The `series` option only sets the
*initial* visibility the first time the card is shown.

Invalid configuration (bad `hours`, non-string entity ids, unknown series keys,
non-boolean visibility values) raises a descriptive error, as Lovelace expects.

## Example configs

### Minimal

```yaml
type: custom:heatpump-optimizer-card
```

### Custom entities and a shorter horizon

```yaml
type: custom:heatpump-optimizer-card
title: Heating plan (next 12 h)
space_entity: sensor.villa_space_heating_plan
dhw_entity: sensor.villa_dhw_heating_plan
hours: 12
```

### Price and power focus (temperatures hidden by default)

```yaml
type: custom:heatpump-optimizer-card
title: When will it heat?
hours: 24
series:
  price: true
  dhw_slots: true
  space_slots: true
  outdoor: false
  dhw_temp: false
  house_temp: false
```

## Behaviour when data is missing

If a sensor is missing, `unavailable`, or its `forecast` is empty, the card shows
a friendly message instead of throwing. Series whose sensor has no data are
rendered as disabled (greyed-out) legend chips.
