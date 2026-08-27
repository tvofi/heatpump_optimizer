# Heat Pump Optimizer dashboard card

`custom:heatpump-optimizer-card` is a self-contained Lovelace card that plots the
optimizer's planning series on a single shared time axis:

- **Electricity price** (per kWh in your currency, right axis, stepped
  filled area)
- **DHW heating** power (kW, left power axis, stepped filled band)
- **Space heating** power (kW, left power axis, stepped filled band)
- **Outdoor temperature** (°C, left temperature axis, smooth line)
- **DHW tank temperature** (°C, left temperature axis, smooth line, with the
  prediction's expected error drawn as a dashed pair around it)
- **House temperature** (°C, left temperature axis; upper/lower zones drawn as
  dashed lines when the house is configured as two-zone)
- **Solar irradiance** (W/m², inner right axis, stepped filled area)

Every series has one clickable legend chip — one per series, including the
house-temperature series when it draws its two zone lines as well, because
visibility is per series and hiding one line of a series is not something the
card can do. The chip's hover text names the extra traces that ride on it; the
crosshair tooltip is where they are told apart, with a row per line. Toggling a
chip hides/shows the series and rescales the axes to the visible data.

The chart is drawn as hand-written inline SVG — there is **no** dependency on
Chart.js, ApexCharts, npm or any CDN.

A vertical "now" marker is drawn at the current time, and hovering (or touching)
the plot shows a crosshair and a tooltip with the value of every visible series
at the nearest sample, plus **why** the plan is heating at that moment.

### The two kinds of dashed line

Two series draw a dashed pair beside their solid curve, and they mean entirely
different things.

The **house temperature**'s dashed lines are the **upper and lower floor**: two
real predicted temperatures, one per zone, drawn whenever the house is
configured as two-zone. They are not error bars. The solid line between them is
the whole-house temperature the optimizer plans against. Each has its own name
in the legend and its own tooltip row, and the lower one reads *Lower floor
(modelled)* when no sensor measures it.

The **DHW tank temperature**'s dashed lines are the **prediction's expected
error** — how far the tank curve has historically been out at that distance
ahead. The band is `dhw_temp` ∓ the average error the model has actually made
for a promise that far in advance, so it widens the further into the plan you
look. It is absent entirely until there is history to draw it from: a fresh
install, or a house with no tank temperature sensor configured, publishes no
band rather than a zero-width one, and the card draws only the solid curve.

Unlike the two floors, the band's two edges are **one** thing, so they share a
single legend chip and produce a single tooltip row — *Hot water, expected
error*, stated as one ± figure. The chip's hover text explains what the dashes
mean. Where the band has no value the dashed lines simply stop, rather than
bridging the gap, and a band with no width at all is not drawn: an envelope
lying exactly on the curve would claim a precision the record has not earned.

### The headline row

Under the card title sits a compact row of numbers: **projected savings** for
the current plan, with the percentage beside it when the integration publishes
one; the **optimization score** out of 100; and the first line of the **plan
narrative**. Set `show_stats: false` to leave it out.

Every part is optional, because every source sensor is. The score is
unavailable until enough history exists, the savings sensors go blank between
optimizer runs, and older integrations publish none of them. A row with nothing
to say draws no chrome at all rather than an empty strip.

The card finds those sensors from the plan sensor it has already resolved: it
takes that entity id's prefix and appends `_predicted_savings`,
`_savings_percentage`, `_optimization_score` and `_plan_narrative`. If you have
renamed one individually, it falls back to scanning for any `sensor` whose id
ends in the suffix it wants. The savings figure is labelled with the unit the
savings sensor itself declares — nothing here converts, so a `currency:` in the
card config does not relabel it.

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
anti-legionella cycle, and so on — or simply keeping the house at target, which
is what an ordinary slot says now that it no longer borrows the weather
pre-heat label. Without this an unexpected slot is indistinguishable from a
bug.

The stretch of the horizon whose prices have not been published yet — Nord Pool
and Tibber release tomorrow around 13:00 — is shaded and labelled *estimated
prices*. Those hours rest on the integration's learned daily price shape rather
than on market data, and a plan that looks identical either way cannot be
audited.

### Language and currency

Every string the card draws lives in one table inside the card file, in English
and Swedish — about 200 keys, with no Swedish entry missing. The active
language follows `hass.language`, so `sv-SE` selects Swedish and any language
without a dictionary renders in English; a key missing from a translation falls
back to its English text rather than to a blank. Switching the Home Assistant
language re-renders the card without a reload. Times in axis labels and slot
descriptions are formatted for that same language.

Deliberately not translated: entity ids, config keys, service and attribute
names, reason codes, and the messages the card writes to the browser console.
Those are contracts, not prose.

The default title is localized too, so a Swedish install shows
*Värmepumpsplan* where an English one shows *Heat pump plan*. Set `title:`
yourself and yours wins in every language.

Prices are labelled with the first currency the card can find:

1. `currency:` in the card config.
2. The `currency` attribute the plan sensors publish (v4.1.0 and later).
3. Home Assistant's own configured currency.
4. `SEK`, as a last resort.

That currency labels the price axis, the tooltip and the slot editor's running
total. It relabels; it does not convert.

## Enlarging the chart

A dashboard card is usually too small to read a 48-hour plan comfortably.
Clicking anywhere on the card, or the expand button in its header, opens the
same chart in a large modal overlay, drawn at a larger font.

Gridlines stand at every hour. How many of them are *labelled* is worked out
from how wide a label is against how much room an hour gets, then snapped to an
interval that divides the day — 1, 2, 3, 4, 6, 8, 12 or 24 hours — so the
labels land on the same clock times each day rather than drifting across
midnight. Zoom in, or plot fewer hours, and more of them are labelled.

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
hold Shift and scroll, or drag the chart background.

A small row of buttons overlays the top of the chart: zoom out, zoom in, and
back to the whole plan. There is no pan button — panning is a drag or a
sideways gesture only — and the reset button stays disabled until the view has
actually been changed. The row fades in when you hover the chart or focus one
of its buttons, and is permanently visible on touch devices, where there is no
hover and the buttons are the only way to zoom without a trackpad. It is drawn
at all only when the plan is long enough to be worth zooming into.

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
water above heating. Drag a block to move it, drag either edge to stretch it.
Tap or click a lane without moving — or right-click it — and a small menu
offers to add a slot at that time, or to remove the one already there. The tap
form is not a duplicate: iOS synthesises no right-click of any kind, so without
it a touch user could not add or remove a slot at all.

The past is shaded and locked, because it cannot be rescheduled. So is
everything past the point where an arrangement would stop having any effect,
which is the earliest of three limits: 20 hours from now — the window
`apply_manual_plan` pins for, read from the `manual_plan_window_hours`
attribute the plan sensors publish rather than hard-coded in the card — the end
of the published plan, and the right-hand edge of the window you are currently
looking at. When it is the zoom rather than the plan or the 20 hours that is
cutting editing short, a `»` appears at the end of the lane and a line under
the lanes says so, with a **show the whole plan** button beside it. Dragging a
slot against the edge pans the window along with it.

Underneath, a running total prices the arrangement against the plan currently in
force, in the currency resolved above. It updates as you drag, so the cost of
moving the tank reheat out of the evening peak is visible before you commit to
it.

**Apply this plan** sends the arrangement to `apply_manual_plan`, which pins it
for the next 20 hours. The optimizer keeps re-solving as prices and weather
move, but it must schedule around your slots rather than through them. **Undo**
throws the draft away, and once an override is in force a banner reports when it
expires and offers **Back to automatic**.

The 20 hours run from the moment you apply, and applying again restarts them —
so a plan made at nine in the evening lasts until five the next afternoon rather
than expiring three hours later. That is why the chart stops you dragging a slot
beyond the window: past it the pin has no effect, and showing a slot as pinned
when it does nothing would be worse than not offering the gesture.

It is deliberately 20 rather than 24. The optimizer plans 24 hours ahead, so a
full-day override would cover every step it was looking at, and re-applying each
day would leave it nothing to decide — switching it off while appearing to leave
it on. At 20 there is always a few hours' tail the optimizer still owns.

One thing the card is deliberately honest about: applying a plan does not
guarantee every slot runs exactly as drawn. You control *timing*; the safety
limits still win. If your arrangement would let the tank fall below its minimum,
miss a legionella cycle, or take the house under its comfort floor, the
integration releases just the slots it has to and says so in the banner. Silently
freezing the house to honour a drag would be the wrong trade.

### Editing without a pointer

The lanes, and the editable slots on them, are real focus stops: each is a
`role="button"` element carrying a spoken label — "Heating lane. Press Enter to
add a slot", or a slot's own start and end times. Tab to one and:

- **Enter** or **Space** opens the same add/remove menu the pointer gets.
- **Delete** or **Backspace** removes the focused slot outright.
- **Escape** dismisses the menu, however it was opened, and returns focus to
  where the menu came from.

Dragging has no keyboard form; add and remove cover the same edits in more
steps. Every edit redraws the chart, which destroys the element that had focus,
so focus is deliberately moved to the lane the edit happened in — the acted-on
slot either no longer exists or has a new index — rather than being dropped
back at the top of the document. Escape puts it back on the slot the menu was
opened from.

Locked slots are left out of the tab order and stay presentational: there is
nothing to do with them. The chart itself is `role="img"` while it is only a
picture, and `role="group"` once the lanes put focusable slots inside it, so
those slots stay in the accessibility tree instead of being flattened away.

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
behind another card.

It is laid out as a column bounded by the viewport: the title and legend keep
their place, and everything below them scrolls when it does not fit. The chart
keeps its exact aspect ratio rather than being squeezed to fill the space, since
it is drawn with `preserveAspectRatio="none"` and constraining its height would
stretch every axis label sideways.

Earlier versions sized the dialog from a fixed guess at how tall the surrounding
chrome would be. That guess stopped being true as the editor grew, and the extra
content rendered outside the dialog's own background — worse on short, wide
desktop windows, because that is where the height-derived branch of the old
formula won. Nothing depends on guessing the chrome now, so a panel added later
costs a scrollbar rather than spilled content.

## The setup page

The enlarged view's **Setup** tab draws your heating system as a schematic:
each component is a thin line-art contour — the house with its gable roof
and chimney, a heated slab as a flat plate with ground hatching under it,
tanks as domed cylinders, the heat pump as a rounded cabinet with its fan,
the mixing valve as a chamfered block with a valve symbol on its own pipe,
and outside air as an open tray under a cloud, because outside air has no
walls. When the wood tank pre-heats hot water through an immersed coil, the
coil is drawn as a visible spring on the tank's upper-right wall with its
own connector stubs, and the hot-water pipe departs from it. Pipes carry
small connection dots at their endpoints and a chevron showing flow
direction.

Each shape stretches with the sensor rows inside it, and every row is the
same assignment slot it always was: click a row — or tab to it and press
Enter or Space — to pick the entity that feeds it. Each row is a
`role="button"` target with a spoken label, and a picker opened from the
keyboard takes focus, so the whole page is usable without a pointer. An
empty slot is a sensor this setup could use and does not have; it is shown
on purpose.

The layout editor works unchanged — dragging boxes and drawing or removing
connections re-renders the schematic live, and the decorations get out of
the way while you edit: the pipe dots and flow chevrons are hidden so the
pipes themselves are easier to grab. Only a drawing that matches a supported
layout can be saved, and the page says which one it matched, or what the
closest one is missing. Colors follow your Home Assistant theme in both
light and dark mode.

## Keyboard and screen readers

Everything the card lets you click is a real button: the legend chips, the
expand button in the header, the overlay's close button and its **Plan** /
**Setup** tabs, the zoom controls, and the buttons in the schedule editor. They
take focus in reading order and carry spoken labels rather than relying on
their glyphs — the zoom controls announce themselves as "Zoom out", "Zoom in"
and "Show the whole plan". The time and temperature inputs in the schedule
editor are labelled the same way.

The overlay is a native `<dialog>` opened with `showModal()`, so the browser
itself keeps focus inside it and closes it on Escape; it is labelled with the
card's title, and its two pages are a `role="tablist"` whose current tab
carries `aria-selected`.

The plan's editable slots and the setup page's assignment rows are covered
above, under [Editing without a pointer](#editing-without-a-pointer) and
[The setup page](#the-setup-page).

The card's one animation — the zoom controls fading in — is dropped entirely
when the browser reports `prefers-reduced-motion: reduce`.

## Installation

### Automatic (recommended)

When you install the integration through HACS and add a config entry, the card is
served and registered automatically:

1. The integration exposes the JS at `/heatpump_optimizer_static/heatpump-optimizer-card.js`.
2. If your dashboards use **storage mode** (the default UI-managed dashboards),
   the Lovelace resource is registered for you on setup.
3. Reload your browser (hard refresh) so the new resource is loaded, then add a
   card and pick **Heat Pump Optimizer Card**. The picker previews it, and
   picking it opens the card's own visual editor — see [Configuring the card in
   the UI](#configuring-the-card-in-the-ui). You can also paste one of the YAML
   examples below.

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
 heatpump-optimizer-card  v4.3.0
```

That is the card's own version. It moves only when the card file changes, so it
is often lower than the integration version — v5.0.0, for instance, ships card
4.3.0 unchanged. Compare it against the card version named in the release notes
for the integration version you installed, not against the integration version
itself.

If it is older than that, or an error mentions a duplicate registration, go to
Settings → Dashboards → ⋮ → Resources and remove every entry for this card
except the one under `/heatpump_optimizer_static/`. The card itself logs an
error naming both versions when a second copy wins the registration, and the
integration writes a warning to the Home Assistant log when it finds a second
Lovelace resource pointing at another copy of this card file.

## Configuring the card in the UI

The card ships its own visual editor, so **Edit dashboard → the card's pencil**
gives you a form rather than raw YAML. It is defined in the same file as the
card — one resource, no build step, no second chunk that can fail to load on
its own — and is built on Home Assistant's `ha-form`, so the pickers, toggles
and number boxes are the ones the rest of the frontend uses, themed to match.

The form offers every documented option:

- **Title**, as free text.
- **The three plan sensors**, as entity pickers filtered to this integration's
  own sensors rather than to every sensor in the house.
- **Hours to show**, as a number box stepping whole hours from 1 to 168.
- **Show the schedule editor** and **Show the headline stats**, as toggles.
- **Currency**, as a dropdown of the likely codes that still accepts any other
  ISO code typed in.
- **Series shown by default**, as an expandable group of the seven per-series
  toggles, labelled with the same names the legend uses.

Field labels follow the frontend language, like the rest of the card.

What it writes back is deliberately the leanest config that means what you
chose. The form shows every default filled in, so a toggle reads as its
effective value; but any key whose value merely restates its default is dropped
before saving, as are emptied fields, and only series you turned *off* are
stored. Switch to the YAML view afterwards and you see what you actually
changed, not a transcript of every default. The one exception is `title`: an
empty title is a legitimate setting (it renders no header text), so an
explicitly configured empty title survives edits to other fields.

## Configuration options

Everything the editor offers can also be written by hand.

```yaml
type: custom:heatpump-optimizer-card
title: Heat pump plan                    # optional, default is localized
space_entity: sensor.heat_pump_optimizer_space_heating_plan  # optional, auto-detected
dhw_entity: sensor.heat_pump_optimizer_dhw_heating_plan      # optional, auto-detected
solar_entity: sensor.heat_pump_optimizer_solar_irradiance    # optional, auto-detected
hours: 24                                # optional, hours forward to plot, default 24
what_if: true                            # optional, schedule editor in the enlarged view
show_stats: true                         # optional, headline row under the header
currency: SEK                            # optional, overrides the resolved currency
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
| `title`        | string  | localized                      | Card header text. Left out, it is the built-in default for the frontend language (`Heat pump plan`, `Värmepumpsplan`). An explicit empty string renders no header text. |
| `space_entity` | string  | auto-detected                  | Entity id of the space-heating plan sensor (its `forecast` attribute supplies `price`, `outdoor`, `space_power`, `room`, `upper`, `lower`). |
| `dhw_entity`   | string  | auto-detected                  | Entity id of the DHW plan sensor (its `forecast` attribute supplies `dhw_power`, `dhw_temp`, the `dhw_temp_lo`/`dhw_temp_hi` expected-error band, and `price`/`outdoor` fallbacks). |
| `solar_entity` | string  | auto-detected                  | Entity id of the solar irradiance sensor (its `forecast` attribute supplies `ghi`). |
| `hours`        | number  | `24`                           | How many hours forward to plot. Must be greater than `0` and at most `168`; fractional values such as `0.5` are accepted in YAML, while the visual editor's box steps whole hours from `1`. |
| `what_if`      | boolean | `true`                         | Show the slot lanes and schedule editor in the enlarged view. Editing is local to the card; only the Simulate, Save and Apply buttons reach Home Assistant. |
| `currency`     | string  | plan sensor's, else HA's, else `SEK` | Unit shown on the price axis and cost figures. The card first uses the currency the integration publishes on the plan sensors (v4.1.0+), then Home Assistant's configured currency, then `SEK`. Only override this if your price feed disagrees with all of them. It relabels rather than converts, and it does not relabel the headline savings figure, which keeps the unit its own sensor declares. |
| `show_stats`   | boolean | `true`                         | Show the headline row (projected savings, optimization score, plan narrative) under the card header. It hides itself, entirely, when the backend publishes none of those sensors. |
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

Toggle state is remembered in the browser's `localStorage`, so it survives page
reloads. The key is the space and hot-water entity ids the config carries (the
defaults, when you have not set them) plus the card's `title` and `hours` — its
config identity, not just its data sources — so a 24-hour card on a wall panel
and a 48-hour card of the same sensors elsewhere keep their own toggles instead
of overwriting each other. Cards saved before v4.2.0 used a key of the
entity ids alone; that key is still read once as a fallback, so an upgrade does
not silently reset every toggle. Writes always go to the new key.

The `series` option only sets the *initial* visibility the first time the card
is shown.

Invalid configuration — an out-of-range `hours`, non-string entity ids or
`title`, a non-boolean `what_if`, `show_stats` or series visibility, an unknown
series key — raises a descriptive error, as Lovelace expects. Those messages are
localized like the rest of the card.

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
