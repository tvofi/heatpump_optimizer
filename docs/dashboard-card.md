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

Every series has a clickable legend chip. Toggling a chip hides/shows the series
and rescales the axes to the visible data. The chart is drawn as hand-written
inline SVG — there is **no** dependency on Chart.js, ApexCharts, npm or any CDN.

A vertical "now" marker is drawn at the current time, and hovering (or touching)
the plot shows a crosshair and a tooltip with the value of every visible series
at the nearest sample.

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
hours: 24                                # optional, hours forward to plot, default 24 (1–168)
series:                                  # optional, initial per-series visibility
  price: true
  dhw_slots: true
  space_slots: true
  outdoor: true
  dhw_temp: true
  house_temp: true
```

| Option         | Type    | Default                        | Description |
|----------------|---------|--------------------------------|-------------|
| `type`         | string  | —                              | Must be `custom:heatpump-optimizer-card`. |
| `title`        | string  | `Heat pump plan`               | Card header text. |
| `space_entity` | string  | auto-detected                  | Entity id of the space-heating plan sensor (its `forecast` attribute supplies `price`, `outdoor`, `space_power`, `room`, `upper`, `lower`). |
| `dhw_entity`   | string  | auto-detected                  | Entity id of the DHW plan sensor (its `forecast` attribute supplies `dhw_power`, `dhw_temp`, and `price`/`outdoor` fallbacks). |
| `hours`        | number  | `24`                           | How many hours forward to plot. Must be `1`–`168`. |
| `series`       | map     | all `true`                     | Initial visibility per series key. Keys: `price`, `dhw_slots`, `space_slots`, `outdoor`, `dhw_temp`, `house_temp`. |

### Entity discovery

The plan sensors use `has_entity_name`, so Home Assistant prefixes them with the
device name. A stock install produces
`sensor.heat_pump_optimizer_space_heating_plan` and
`sensor.heat_pump_optimizer_dhw_heating_plan`.

You normally do not need to configure either option. The card resolves entities
in this order:

1. The id you configured, if that entity exists.
2. Any `sensor` whose `plan_kind` attribute is `space` or `dhw`. This is a
   stable marker published by the integration, so renaming an entity does not
   break the card.
3. Any `sensor` whose id ends in `space_heating_plan` / `dhw_heating_plan`,
   for integration versions older than 2.6.1.

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
