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

The chart and the chrome around it scale differently, because they are
different kinds of thing.

The chart is drawn in a fixed 900x380 coordinate system and stretched to fill
whatever space it is given, so its text grows with it for free — the same label
renders around 6px in a dashboard column and around 20px in a dialog. Its size
is *not* a free preference, though: the margins, tick spacing and legend rows
are authored in those same units against a font of about 10, so raising the
font without moving everything else makes labels collide.

The header, legend, tooltip and schedule editor are plain HTML and cannot scale
by themselves. They are sized in `em`, and the card sets the single font size
they derive from once the dialog has been laid out, from its measured width and
clamped at both ends. Container query units would say this in CSS alone, but
`container-type: inline-size` also applies inline-axis containment, which is a
large side effect for a font size.

### Panning and zooming the plan window

Pinch to zoom, or hold Ctrl and scroll. Swipe sideways with two fingers to pan,
or drag the chart background. The small row of buttons above the chart does the
same, and exists because neither gesture is available on a phone or to someone
tabbing through the card.

A plain vertical scroll is deliberately left alone. The card sits in a dashboard
people scroll, and a chart that swallowed the wheel would trap the page the
moment the pointer crossed it.

It is **forward-only**. There is no history to scroll back into: both plan
sensors keep their `forecast` attribute out of the recorder, so nothing stores
what the plan used to say. The window therefore stays between now and the end of
the plan, and zooming out stops at the plan's real extent rather than at the
configured plot width — past the optimizer's horizon there is empty chart, not
more plan. The reset button returns to the window the card was configured for.

Zooming changes the axis the lanes are drawn against, not just their appearance,
so dragging a slot keeps hitting the time under the pointer at any zoom level.
Your draft arrangement is read from the published plan rather than from what is
on screen, so zooming in cannot quietly drop the slots you cannot see.

### Rearranging today's slots

The enlarged view draws today's plan a second time as two editable lanes, hot
water above heating. Drag a block to move it, drag either edge to stretch it,
and right-click the lane to add a slot there or remove the one under the
pointer. The past is shaded and locked, because it cannot be rescheduled, and so
is anything beyond tonight's midnight, because an override never outlives the
day it was made.

Underneath, a running total prices the arrangement against the plan currently in
force, in your Home Assistant currency (or `currency:` if you set it). It
updates as you drag, so the cost of moving the tank reheat out of the evening
peak is visible before you commit to it.

**Apply this plan** sends the arrangement to `apply_manual_plan`, which pins it
until midnight: the optimizer keeps re-solving as prices and weather move, but
it must schedule around your slots rather than through them. **Undo** throws the
draft away, and once an override is in force a banner reports when it expires
and offers **Back to automatic**.

One thing the card is deliberately honest about: applying a plan does not
guarantee every slot runs exactly as drawn. You control *timing*; the safety
limits still win. If your arrangement would let the tank fall below its minimum,
miss a legionella cycle, or take the house under its comfort floor, the
integration releases just the slots it has to and says so in the banner. Silently
freezing the house to honour a drag would be the wrong trade.

### Schedule editor and what-if simulator

The enlarged view also carries an editor for the heating day, the hot water
windows and two temperatures. It is shown by default and hidden with
`what_if: false`, which hides the slot lanes too.

The temperatures live in a section of their own: the **comfort temperature** the
house is held at during the heating day, and the **minimum hot water**
temperature the tank may fall to inside a demand window. They are grouped because
a lone temperature slider inside a section about scheduling reads as a stray
control with no context. The hot water minimum is capped a few degrees below your
setpoint so the tank keeps a band to work in — the cap moves on its own when you
change the setpoint, and a saved value above it is lowered with a visible note
rather than silently.

Editing only builds a draft inside the card. Two buttons act on it: **Simulate
these slots** prices the draft against the plan currently in force, and **Save
as my schedule** writes it into the configuration through `apply_schedule`,
after a confirming second press.

Setpoints are otherwise chosen blind: the optimizer can price a plan, but you
never see the price of your own comfort choices. This turns "I set 21 because it
sounds about right" into an informed decision.

Each answer is a real optimization solve on the Home Assistant host. Both
temperature sliders are debounced in the card — sharing one timer, so two drags
cannot race and report the price of the previous one — and the solve is
rate-limited in the integration, so dragging cannot trigger one per pixel. It
runs against a *copy* of your configuration, so an exploratory drag never
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

### If an upgrade seems to change nothing

Only one copy of the card can be active: a custom element name can be claimed
once per page, and the first copy to load keeps it. A second copy — usually a
manual install left under `/local/` from an earlier version — therefore wins
permanently, and every upgrade after it loads and is ignored. New features
appear to be missing even though the files on disk are current.

To check, open the browser console and reload the dashboard. The card prints
its version on load:

```
 heatpump-optimizer-card  v3.1.2
```

If that version is older than the one you installed, or an error mentions a
duplicate registration, go to Settings → Dashboards → ⋮ → Resources and remove
every entry for this card except the one under `/heatpump_optimizer_static/`.
Home Assistant also logs a warning when it spots such a duplicate.

## Configuration options

```yaml
type: custom:heatpump-optimizer-card
title: Heat pump plan                    # optional, default "Heat pump plan"
space_entity: sensor.heat_pump_optimizer_space_heating_plan  # optional, auto-detected
dhw_entity: sensor.heat_pump_optimizer_dhw_heating_plan      # optional, auto-detected
solar_entity: sensor.heat_pump_optimizer_solar_irradiance    # optional, auto-detected
hours: 24                                # optional, hours forward to plot, default 24 (1–168)
what_if: true                            # optional, schedule editor in the enlarged view
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
| `what_if`      | boolean | `true`                         | Show the slot lanes and schedule editor in the enlarged view. Editing is local to the card; only the Simulate, Save and Apply buttons reach Home Assistant. |
| `currency`     | string  | Home Assistant's currency      | Unit shown next to the slot editor's cost delta. Only override this if your price sensor is not in the currency Home Assistant is configured for. |
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
