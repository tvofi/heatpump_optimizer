# Heat Pump Cost Optimizer — Release Notes

## v3.7.0

If you have a mixing valve, the optimizer can now use your buffer tank as a
store — charging it when electricity is cheap and drawing it down when it is
expensive.

### Why a valve is what makes this possible

Until now the model assumed everything the heat pump produced went straight to
your radiators and floor loops. For a system without a mixing valve that is
exactly right, and it stays the default.

But it also means the buffer tank could never fill: whatever went in came
straight back out, so the tank only ever cooled. A mixing valve is precisely the
part that changes this. It limits how much heat reaches the house, and once the
house has what it needs the surplus has nowhere to go but the tank.

Set **Mixing valve and heat storage** in the options to match your system.
Leaving it at *No mixing valve* changes nothing at all.

### Setting a valve you adjust by hand

If your valve is a fixed one you set yourself, the recommendation is to set it to
the **top of your comfort band**, and the reasoning is worth knowing.

A high setting keeps the valve open until the house reaches its ceiling, so the
building itself charges first. That storage is free: the building holds heat at
room temperature, so there is no efficiency penalty. Only once the house is
satisfied does the valve begin to throttle, and only then does the tank take the
surplus — which is stored hot, and does cost efficiency.

Building first, tank second, is the cheap order. Setting the valve low reverses
it, filling the expensive store while the free one sits empty.

One thing you give up: at that setting the valve is no longer what stops your
house overheating. The optimizer's own comfort limits do that instead.

### Storing hot costs efficiency, and the model now knows

A heat pump is less efficient the hotter it has to push water. Charging a tank to
60 °C costs noticeably more per unit of heat than running a floor loop at 35 °C,
and that penalty is the entire economics of storage: it is what decides whether
shifting heat into a cheap hour is actually worth it.

The model now accounts for it, so it will only fill the tank when the price
difference genuinely pays for the loss. On a day with little variation, it will
leave the tank alone.

The tank is also never charged above the maximum you set, however cheap
electricity happens to be.

## v3.6.1

### Fixed: large buffer tanks were modelled as losing far more heat than they do

If you have an accumulator rather than a small buffer, the model believed it
leaked roughly ten times as fast as it really does — and the correction the
integration learns from your own tank sensor was not allowed to find the truth
either.

The standby loss was described as a cooling rate in degrees per hour, and the
same rate was applied at every tank size. But heat escapes through a tank's
*surface*, and a big tank has far less surface for the water it holds. A
750-litre accumulator loses proportionally much less than a 35-litre buffer, so
one rate cannot describe both. Applied to 750 litres, the old number modelled
more heat lost in six hours than the tank can hold.

The loss now follows the tank's size the way the physics does, and the limits
the learning is allowed to move between are derived from how well a tank of that
size could plausibly be insulated. A well-insulated accumulator now sits
comfortably inside that range instead of being pinned several times above it.

The prior itself is also more honest. The old default worked out worse than an
uninsulated bare cylinder, at any size.

**What you will see.** If you have a buffer tank configured, its standing loss
drops and its hours of autonomy rise on the battery view. If you have a *large*
tank the change is substantial. Nothing changes if you never configured one.
A rate you set yourself is still respected.

## v3.6.0

The two-zone model now learns how your heat loss actually splits between the
floors, and a long-standing bias in the existing learner is fixed.

### Learning the split, not just the level

The correction the integration learns from prediction error multiplies *both*
zone losses, so it could move the total but never the balance between the
floors. If your lower floor loses more heat than the configured split assumes,
nothing could ever discover that.

There is now a second learned value that owns the split, fitted from the lower
floor while the existing one is fitted from the upper. Two numbers, two
independent measurements, so neither can quietly absorb the other's error.

It only moves when a **real lower-floor sensor** is configured (added in v3.4.0).
Without one the lower zone is inferred from the floor return water, and that
inference comes from the same sensor as the slab estimate — so there is nothing
independent to learn from. Watch `lower_floor_loss_ratio` and
`lower_floor_loss_samples` on the learning sensor.

Deliberately not learned: the inter-zone transfer coefficient. One pump, one
water temperature and a fixed radiator/floor split mean the two floors move
together and rarely diverge, so a passive fit would mostly track noise. It stays
where you configured it.

### Fixed: the heat loss learner was comparing two different things

On a two-zone system the learner compared the indoor sensor — which is the
*upper* floor — against the model's average of both floors. The difference
between your two floors was therefore being read as heat-loss error.

It is a systematic offset, not noise, so it did not average out: measured
against the real model, floors 1.5 °C apart injected about 0.53 °C into every
sample, more than half the point at which a sample is rejected as implausible.
Houses with a larger difference between floors had their samples thrown away
entirely and learned nothing at all.

The learner now compares the upper floor against the predicted upper floor.
## v3.5.0

A pinned plan now lasts 20 hours from when you apply it, instead of expiring at
midnight.

### Your plan no longer evaporates in the evening

**Apply this plan** used to pin your arrangement until the next midnight. That
made the feature least useful exactly when people reach for it: a plan made at
nine in the evening lasted three hours, and one made at half past eleven barely
survived the click. It now runs for **20 hours from the moment you apply**, and
applying again restarts the clock — so an evening plan carries through the night
and well into the next afternoon.

The chart's editable region follows the same rule, which is the point: the
backend releases every pinned step at or after the expiry, so a slot drawn
beyond it would have been shown as pinned while quietly doing nothing. The two
now read the same number from the same place rather than each keeping a copy.

It is deliberately 20 rather than 24. The optimizer plans 24 hours ahead, so a
full-day override would cover every step it was looking at, and re-applying each
day would leave it nothing left to decide — switching it off while appearing to
leave it on. At 20 there is always a few hours' tail the optimizer still owns.

The expiry is now written with a day when it is not today. Under the midnight
rule "pinned until 08:30" could only mean one thing; with a 20-hour window it
usually means tomorrow, so it says so.

The **Apply for the rest of today** button is now simply **Apply this plan**,
which is what it does.
## v3.4.1

### Fixed: two axis labels ran into each other

In the enlarged chart, with solar irradiance switched on, the electricity price
axis is labelled **SEK/kWh** and the solar axis **W/m²** — and the two ran
through each other, overlapping by about a fifth of the price label.

The space between those two axes is a fixed width, but the text is not: the
enlarged view uses a larger font, and at that size the price label no longer
fits the gap. The label is now measured, and when it will not fit it is placed
on the other side of its own axis line, where there is empty space above the
chart. Nothing moves when there is room, and the solar label never moves at all.

## v3.4.0

Two-zone houses can now tell the optimizer what the lower floor is actually
doing, instead of having it guessed from the floor return water.

### A real lower floor sensor

Two-zone mode plans against two room temperatures, but only the upper one ever
had a sensor. The lower zone was inferred as the floor return temperature plus
half a degree — and that is a *water* temperature standing in for an air
temperature. A floor loop returns at roughly 24–30 °C while the room it serves
sits near 21, so the model believed the lower floor was several degrees warmer
than it really was. Because both zones are judged against the same comfort band,
the lower one looked like it was permanently overshooting, and the optimizer
under-heated the room it could not see.

There was a quieter problem underneath. The slab estimate came from the *same*
sensor, as the return plus one degree, so the gap between slab and room was
always exactly 0.5 K no matter what the sensor read. The main heat path into the
lower zone was therefore stuck at a constant value and could not respond to
anything.

Set **Lower floor temperature sensor** in Step 1, or under Options → Entities,
and both problems go away. It is optional and two-zone only; without it the old
estimate is still used, so nothing changes until you add one. The order of
preference is a real sensor, then the return-temperature estimate, then the
upper floor's reading.

### Fixed

- **The house heat loss learner was silently dead on these houses.** It compares
  the upper sensor against the model's area-weighted average of both zones, so
  the inflated lower zone introduced a structural error of about 3.7 °C — well
  past the 1 °C residual it refuses to learn from. On a two-zone install with a
  floor return sensor it therefore rejected every sample and never learned
  anything, with nothing but a debug log to say so. With a real sensor the
  residual is back in range. If `house_heat_loss_samples` has been stuck near
  zero on your system, this is why.
- A floor return sensor that was configured but had gone stale or unavailable
  used to leave both the slab and the lower floor holding whatever they were
  last set to, with nothing marking them as unfreshened. Both now fall back
  cleanly.
## v3.3.1

### Fixed: the enlarged card could render outside its own edge

On a desktop browser, at some window sizes, everything below the chart — the
delta calculator, the buttons, the schedule editor — was drawn past the bottom
of the dialog's own background instead of inside it. At 1400x700 with a pinned
plan active, the overflow measured 449 pixels.

The dialog's width was derived from a fixed guess that the surrounding chrome
needed 168 pixels of height. That guess was made when the enlarged view was just
a title, a legend and a chart, and it never grew as the editor did. Worse, it
fed back on itself: a shorter window made the dialog *wider*, and the text
around the chart is sized from the dialog's width, so the chrome grew in the
same direction as the overflow.

The guess is gone. The dialog is now bounded by the window, and anything that
does not fit scrolls, so a panel added later costs a scrollbar rather than
spilled content. Your position in the panel is kept when the plan refreshes
underneath you, which happens every few minutes.

The chart still keeps its exact proportions rather than being squeezed to fit —
squeezing it would stretch every axis label sideways.

Phones were never affected and are unchanged: the narrow-window path never
consulted the faulty budget.

## v3.3.0

The schedule editor gained a hot water minimum, and the plan chart can be panned
and zoomed.

### A home for the temperatures

The comfort slider used to sit on its own in the middle of a section about
scheduling, with nothing around it to say what it was. It now shares a
**Temperatures** section with a second slider, **minimum hot water** — the lowest
the tank may fall to inside a demand window. Both are priced the same way as the
rest of the editor, so the cost of asking for warmer water is visible before you
save it, and **Save as my schedule** stores them along with your heating hours.

The hot water minimum is capped a few degrees below your hot water setpoint. A
minimum equal to the setpoint would leave the tank no band to work in and the
pump would short-cycle against its own hysteresis. The cap follows the setpoint
if you change it, and a stored value above the cap is lowered with a note on
screen rather than quietly corrected.

The same limit is enforced in `apply_schedule`, which now accepts
`dhw_min_temperature`, because an automation can call the service directly. It is
checked per heat pump, before anything is written, so a call covering two heat
pumps either applies to both or fails whole. This matters more than it sounds:
the solver treats tank limits as *soft* penalties, so an impossible minimum is
not refused downstream — the plan would simply sit in permanent slight violation,
which is close to undiagnosable from the outside.

### Panning and zooming the plan

Pinch to zoom, hold Ctrl and scroll, swipe sideways to pan, or drag the chart
background. There are buttons too, for touch and for the keyboard. A plain scroll
still scrolls the dashboard — a chart that swallowed the wheel would trap the
page under the pointer.

It only goes forward. Plan forecasts are deliberately kept out of the recorder,
so there is no history to scroll back into; the window stays between now and the
end of the plan, and zooming out stops where the plan does instead of showing
empty chart. Zooming moves the axis the slot lanes are drawn against rather than
just their appearance, so dragging a slot still lands on the time under your
pointer at any zoom level.

### Fixed

- A plan attribute the integration published as "unknown" was read by the card as
  a real measurement of zero, because `Number(null)` is `0` and zero is a finite
  number. This could show a 0 °C comfort target, and would have capped the new
  hot water slider at nothing.
- Dragging the chart to pan no longer opens the enlarged view when the drag ends.
  A click that never moved still opens it.

## v3.2.0

You can now rearrange today's plan by hand, and the optimizer will work around
you.

### Rearranging slots on the card

The enlarged card draws today's plan a second time as two editable lanes, hot
water above heating. Drag a block to move it, drag an edge to stretch it, and
right-click a lane to add a slot or remove the one under the pointer. A running
total at the bottom prices your arrangement against the plan in force, in the
currency Home Assistant is configured for, and updates as you drag — so the cost
of moving the tank reheat out of the evening peak is visible before you commit
to it.

**Apply this plan** pins the arrangement until midnight. The optimizer keeps
re-solving every few minutes as prices and weather move, but it now has to
schedule around your slots rather than through them. **Back to automatic**
releases it, and the pins are persisted, so they survive a restart.

The past is shaded and locked, because it cannot be rescheduled, and so is
anything beyond tonight's midnight, because the override does not outlive the
day it was made.

Until now the card could show you the plan and simulate a different *comfort
setting*, but the plan's shape was not yours to touch. If you knew something the
optimizer did not — a guest arriving, a bath at four, a car to charge — there
was no way to say so.

### Timing is yours; safety is not

Applying a plan does not promise every slot runs exactly as drawn, and the card
says so rather than pretending otherwise. If your arrangement would let the tank
fall below its minimum, miss a legionella cycle, or take the house under its
comfort floor, the integration releases just the slots it has to, re-solves, and
names them in the banner and in the `manual_override` sensor attribute.

This matters more than it might look. Comfort and tank limits are *penalties* in
the objective, not hard constraints, so pinning heating off does not make the
solver find another way — it makes it accept a cold house. Every release is
therefore followed by a fresh solve, and if a channel still cannot be made safe
after several rounds its forced-off pins are abandoned wholesale and the channel
is planned freely. Only the breaching channel is given up; an arrangement that
was never unsafe is kept, so an impossible hot water request cannot quietly
discard your heating plan and let the pump run in the hours you excluded.

### New services

* `heatpump_optimizer.apply_manual_plan` — pin `space_slots` and/or `dhw_slots`
  until `expires_at` (default: next local midnight). A channel you omit stays
  automatic; an explicit `[]` means "off until this expires". Returns the
  applied plan and how many horizon steps it pinned.
* `heatpump_optimizer.clear_manual_plan` — drop the override and re-solve.

Both plan sensors gain a `manual_override` attribute describing the active plan,
its expiry, and any slots released for safety.

### Fixes

* An `expires_at` without a timezone — exactly what the service UI's free-text
  field produces — crashed with an opaque `TypeError` instead of being handled.
* The applied-step counts were measured in hourly price entries against a
  15-minute horizon, so they covered only a quarter of the day and reported zero
  for an evening plan that had in fact applied perfectly well.
* A corrupt or hand-edited stored plan could raise during setup rather than
  simply being discarded.
* The card's chart lookup matched the header's expand-button icon instead of the
  chart itself, which mis-measured the plot area used for hit-testing.
* An untouched slot draft no longer goes stale when a new plan is published: the
  lanes follow the refresh, while an edit in progress survives it.

## v3.1.2

Three real bugs behind the symptoms reported against v3.1.0 and v3.1.1.

### Chart labels no longer overlap in the enlarged view

The enlarged chart labelled the time axis every hour. Over a 48-hour horizon
that puts labels about 15 units apart in a chart whose labels are 40 units
wide, so they simply ran into each other. Label spacing is now worked out from
the room available and the width of the labels themselves, which also fixes
12-hour locales, where `12:00 AM` is over half again as wide as `13:00`.

### The comfort slider showed an unrelated thermostat's setpoint

The what-if panel picked the first `climate.*` entity it found and used its
target temperature. In a home with more than one thermostat that is an
arbitrary choice, and a valve sitting on frost protection made the slider open
at 5 °C. It now reads the comfort temperature from the optimizer's own plan,
as the heating-hour and hot-water fields already did.

### An old copy of the card could silently keep running

If a second copy of the card was installed — usually a leftover manual install
under `/local/` — it claimed the custom element first, and every later version
loaded and did nothing at all. There was no error and no clue: upgrades simply
appeared to have no effect, and the schedule editor added in v3.0.0 stayed
invisible. Now:

- a duplicate registration logs a clear console error naming both versions and
  where to remove the extra resource;
- Home Assistant warns in the log when it finds another resource pointing at a
  different copy of the card;
- the card is served without long-lived cache headers, so a browser cannot hold
  an old copy after an upgrade. This matters most in YAML dashboard mode, where
  the integration cannot refresh the resource's cache-busting query itself.

If you are affected, check Settings → Dashboards → Resources and keep only the
entry under `/heatpump_optimizer_static/`.

## v3.1.1

Fixes for three things v3.1.0 got wrong or left hidden.

### The schedule editor is now visible without extra configuration

The editor added in v3.1.0 was gated behind `what_if: true` in the card's YAML,
off by default and documented as a comfort-temperature slider. Several people
looked for it and concluded it did not exist.

It is now shown by default. The reasoning that made it opt-in does not hold:
holding a draft costs nothing, because the draft lives in the card. Only
**Simulate these slots** runs a solve, and only **Save as my schedule** changes
any configuration. `what_if: false` still hides the panel.

### Chart labels no longer overlap

v3.1.0 tried to make chart text render at a constant pixel size by converting a
pixel target through the chart's measured width. That was the wrong model. The
chart's whole geometry — the 92-unit left margin, the 34-unit bottom margin, the
tick spacing, the legend rows — is authored in the same coordinate units as the
font, against a font of about 10. Converting for pixel size pushed it to about
20 units in a typical dashboard column, so labels ran into each other.

The font is part of that geometry and is fixed again. Nothing is lost: the chart
is stretched from a fixed coordinate system, so its text already grew roughly
3.5× when the card was enlarged. That was never the part that failed to scale.

### The enlarged view's chrome scales without side effects

The header, legend, tooltip and editor are plain HTML and do need help scaling.
v3.1.0 did that with container query units, which required
`container-type: inline-size` on the dialog — and that also applies inline-axis
containment, a large and easily-missed side effect for a font size.

The dialog's font size is now set directly from its measured width, clamped so a
phone-width dialog stays legible and a very wide one does not turn the legend
into a headline. Everything in the chrome is in `em`, so one value sizes all of
it. The dialog's width comes from the viewport rather than its contents, so this
cannot feed back into a resize loop.

### Not fixed: creating a helper from an entity picker

Creating an `input_datetime` helper from the away page's picker can still fail
with `required key not provided @ data['name']`. This is in Home Assistant's own
helper dialog rather than in this integration — the create request is sent with
no name, and `input_datetime` requires one. Until it is fixed upstream, create
the helper from **Settings → Devices & services → Helpers** and then select it
in the away page.

## v3.1.0

Edit your schedule from the card, and two fixes in the configuration pages.

### Change the schedule from the card, not just simulate it

The what-if panel could already move the heating day and the hot water windows
and tell you what the change would cost — but there was no way to keep the
answer. You had to read the number, close the card, and retype the same
schedule in the options pages.

The panel now has a **Save as my schedule** button next to **Simulate these
slots**, backed by a new `heatpump_optimizer.apply_schedule` service. Saving
writes the schedule into your configuration and reloads the integration, so the
next plan is made against it.

Because saving replaces what the house actually runs on, it asks first: the
button turns into *Confirm: overwrite my schedule* and only saves on a second
press. Editing anything in between disarms it, so you cannot confirm one
schedule and save another, and an armed confirmation lapses after a few seconds
rather than sitting waiting for a stray click. Windows are validated before they
are stored, so a malformed schedule is refused at the button instead of failing
on every later reload.

The README now says how to reach the panel: it lives in the enlarged card and
needs `what_if: true`, which was documented only as a comfort-temperature
slider and was easy to miss.

### Chart text no longer changes size when you enlarge the card

The chart is drawn in a fixed coordinate system and stretched to fit its
container, so text sized in those coordinates renders at whatever pixel size the
stretch happens to produce — around 5 px in a narrow card and around 30 px in a
full-width dialog. Enlarging the card did not scale the text so much as distort
it, and the surrounding labels, legend and tooltip did not follow at all,
because they are ordinary HTML sized against the card's own font.

Both halves now aim at a pixel size instead of a coordinate size. The chart
measures its own width and converts the target back through it, clamped so a
pathologically narrow or wide chart still produces readable text. The HTML
chrome uses container-query units so it tracks the dialog's width, with the
previous fixed sizes kept as a fallback for browsers without them.

### Fixes

* **The capacity tariff window could not be submitted.** Choosing *1 hour* on
  the grid page failed with `expected str`. The dropdown's options are strings
  but its default was the number `60`, and leaving the already-selected option
  untouched submits that default — so the one option most people want was the
  one that could not be saved.
* **Creating a helper from an entity picker failed.** Adding a return-time
  helper from the away page failed with
  `required key not provided @ data['name']`. The pickers declared their domains
  using Home Assistant's legacy top-level `domain` key; the frontend reads only
  the newer `filter` key when it works out which helper type to create, so it
  had no type to create and submitted the new helper without a name. All entity
  pickers now use `filter`, which also restores domain filtering in the picker
  itself.

Both failures were invisible to the test suite because its Home Assistant stub
accepted any value a selector was given. The stub now enforces the same rule the
real one does, and the suite renders every options page and submits it back
untouched — the cheapest thing a user can do, and the case that broke.

## v3.0.0

The three releases developed since v2.6.1 — v2.7.0, v2.8.0 and v2.9.0 —
collected into one major release. Everything below is included.

The theme across all three is the same. The optimizer used to reason about a
*model* of the house and a *plan* for the heat pump, with almost no way to find
out whether either was true, and no way for a user to see why it had decided
anything. Most of what follows closes those two gaps.

Upgrading is safe: every new capability is off or neutral by default, and an
existing config entry migrates without a behaviour change.

---

## Added

### Knowing when an input has gone bad

- **An input staleness watchdog.** Every sensor read was guarded against
  `unavailable` and `unknown` — the visible failures, which every call site
  already handled. The dangerous failure is a sensor that stops updating while
  still reporting its last value. A dead battery in a tank probe or a dropped
  Zigbee room sensor leaves a perfectly valid-looking constant in the state
  machine indefinitely.

  The optimizer then plans against a fiction, but the worse consequence is that
  the learners observe a flatline, attribute it to thermal behaviour, and
  persist a corrupted parameter that survives a restart. Over-age values are
  now treated as *missing*, learning freezes rather than training on them, and
  a new **Input Problem** binary sensor names which inputs are stale and why
  the learners paused. Limits are per input: a room temperature may reasonably
  be minutes old, an outdoor forecast hours.

- **An optional measured power entity**, plus whole-house power and a
  cumulative energy meter. `CONF_HEAT_PUMP_MAX_POWER` is a nameplate limit and
  "Recommended Power" is what the optimizer is *commanding*; neither is a
  measurement. With a real meter, COP becomes observable rather than assumed —
  and since every plan is priced through COP, an error there was an error in
  every cost reported. New **Measured Power** and **Observed COP** sensors.
  Watts, kilowatts and megawatts are all accepted and normalised; an
  unrecognised unit is refused rather than guessed, because a wrongly scaled
  power value is worse than none.

- **Closed-loop accuracy reporting.** Predicted versus realised temperature,
  power and cost are recorded per interval and published on a **Prediction
  Accuracy** sensor. The *signed* bias is published alongside the magnitude,
  because a mean absolute error cannot distinguish random noise from a model
  that is consistently half a degree optimistic — and it is the second that
  indicates drift.

### Costs the optimizer could not previously see

- **Capacity (effekt) tariff awareness.** Swedish and increasingly Nordic DSOs
  bill a monthly capacity charge, typically the mean of the three highest
  hourly peaks. Nothing modelled this, so the optimizer would happily stack hot
  water and space heating into the same cheap hour — and one new monthly peak
  can easily cost more than the energy that stacking saved.

  The penalty is soft rather than a hard cap, so it trades off against comfort
  like everything else, and it charges only for exceeding the peak *already
  billed this month*: if the month has a 9 kW peak, an 8 kW hour is free, and
  modelling it as "keep power low" would give away savings for nothing. A
  **Monthly Peak Power** sensor shows the billed peak and the free headroom.

- **PV self-consumption.** For a house with solar, heating hot water or the
  buffer from surplus beats exporting it. While the array is in surplus, an
  extra kWh does not cost the import price — it costs the export compensation
  foregone. Substituting that marginal price is all that is needed: the
  hot-water LP, the space-heating objective and the savings settle-up all keep
  working unchanged.

- **Compressor cycling cost.** An optional per-start cost, expressed as a
  smooth term on the step-to-step power difference. That keeps the problem
  continuous; a true minimum-runtime constraint would make it a MILP, which is
  not affordable inside a Home Assistant update cycle. It defaults to **zero**,
  because the measurement came first: realistic plans make two to four starts a
  day, so most installs have nothing to fix and should not pay savings for
  smoothness they do not need. The planned start count is published so the
  decision can be made from evidence.

- **The unknown price horizon is modelled instead of repeated.** Prices past
  the published horizon were filled with a flat repeat of the last known value.
  Nord Pool and Tibber publish tomorrow around 13:00, so before then a large
  part of the horizon was a constant — and a flat tail has no trough, so the
  optimizer could not see a cheap period worth waiting for and systematically
  under-deferred load in the morning.

  A normalised diurnal shape is now learned from the prices actually seen,
  split weekday/weekend, and scaled to the recent price level. It never
  displaces real data, it is heavily damped until several days have been
  observed, and the plan marks which steps rest on it — the dashboard card
  shades that stretch.

### Understanding the house

- **Building type presets.** The thermal page asked for `house_thermal_mass` in
  kWh/°C, which no homeowner knows, and the shipped defaults quietly encoded
  one specific house. Every other building started from a wrong prior, and the
  learners then spent weeks walking away from it. Three answerable questions —
  what the house is built from, roughly when, and what the heat comes out of —
  now derive the physics, scaled by heated floor area. Presets set *starting
  values only*, which is stated in the UI, and the numeric path remains for
  anyone with a real energy declaration.

- **Active system identification.** Every learner was passive: each waited for
  the house to happen to do something informative, which is why parameters took
  weeks and why the guard thresholds had to be so conservative. Opt-in, the
  optimizer will now run a deliberate step change on a mild, cheap night and
  fit the response. Comfort is a hard constraint on the experiment rather than
  a cost term: it aborts if the room drifts past the allowed excursion, and it
  will not repeat on a house that has already converged.

- **A learned defrost and cold-humid derate.** Air-source units lose real
  capacity between roughly 0 and +5 °C in humid air, which is precisely the
  Swedish shoulder season and precisely where the plan is most aggressive about
  coasting. Plans made there quietly under-delivered. The derate is *learned*
  per temperature and humidity bucket from the closed-loop accuracy signal, not
  taken from a datasheet, because between-unit spread is larger than the effect
  being modelled. With no evidence it is exactly 1.0.

- **Revealed-preference comfort tuning.** `comfort_weight` is the most
  consequential number in the configuration and the least knowable; it has no
  intuitive units. But users reveal the answer constantly — every manual
  override says the plan went too far in one direction. Opt-in, the value is
  now nudged from that evidence, slowly, only on consistent signals, and with a
  quiet-period signal so it can come *down* as well as up. The learned value
  has its own sensor and a reset button, because an invisible self-adjusting
  objective would be alarming.

### Reacting to the world

- **External heat source detection.** A wood furnace tied into the same buffer
  heats the tanks for free, and burning electricity to heat water that is
  already being heated is the single most expensive mistake available.
  Detection is inferred from sensors that already exist: a tank warming while
  the compressor is off, or warming faster than the compressor could manage. An
  explicit stove or flue entity overrides the inference.

  The detector is deliberately reluctant, because the costs are asymmetric:
  wrongly believing a fire is lit means skipping a cheap-hours charge and
  either paying peak prices later or running out of hot water, while missing
  one costs a single unnecessary charge. So it needs consecutive
  confirmations, and a decay window keeps it from flapping as a fire dies down.
  While active, discretionary electric hot water is suppressed — but only while
  coasting still meets the requirement — and the learners freeze with the
  reason recorded.

- **Away and holiday mode.** A week away is the largest single saving a heating
  system can offer. What makes this more than an `input_number` is the *return
  time*: knowing when the house must be comfortable again lets the recovery
  heat be bought in the cheapest hours beforehand instead of panic-heating on
  arrival. Away state can come from a person, device tracker, calendar or plain
  toggle — the polarity differs by domain and is handled for you. Recovery
  starts deliberately early, because a wrong return time is a comfort failure
  the user will notice.

### Seeing what it is doing

- **Plan reason codes.** The plan sensors published which slots were chosen but
  never why. A slot could be cheapest-price, deadline-driven, legionella,
  terminal-value or a comfort floor, and nothing distinguished them — so an
  unexpected slot was indistinguishable from a bug. Every step now carries a
  reason code, carried through to the sensor attributes and shown in the card's
  tooltip.

- **Energy dashboard and long-term cost statistics.** Every monetary sensor was
  `MEASUREMENT`, so none of it reached Home Assistant's Energy dashboard and
  there was no long-term cost history. The integration's central claim — that
  it saves money — was invisible in the one place users look for exactly that.
  There are now `TOTAL_INCREASING` energy and cost accumulators, split hot water
  versus space heating. The split is apportioned from the planned power split
  and says so in its attributes, because one meter cannot separate two circuits
  and pretending otherwise would be worse.

- **The house published as a virtual battery.** State of charge, usable
  capacity, charge and discharge rates and round-trip efficiency, so other Home
  Assistant energy automations can reason about the heat pump alongside a real
  battery. State of charge is measured against the comfort band, since energy
  below the minimum acceptable temperature is not actually available.
  Round-trip efficiency is reported in thermal terms; an electrical figure
  would exceed 100% because charging happens at COP > 1.

- **Buttons**: force an optimization run, arm the identification experiment,
  and reset the learned comfort weight. Buttons rather than switches, because
  these are momentary actions with no lasting state; a toggle would have to
  bounce itself back and until it did the UI would imply a state that does not
  exist. The run button goes unavailable while a solve is in flight, so a
  control that appears to do nothing for several seconds does not invite
  repeated presses.

### Solar forecasting

- **Solar irradiance can come from Open-Meteo.** Solar gain was only as good as
  the irradiance behind it, and most weather integrations never publish a
  `solar_irradiance` field, so for many installs the term silently evaluated to
  zero and the optimizer could not anticipate a sunny afternoon. Set *Solar
  forecast source* to Open-Meteo and pick the location on the map. No API key
  or account is needed.

  Two endpoints are used because they do different jobs: the forecast API
  supplies the planning horizon at 15-minute resolution, matching the
  optimizer's grid exactly, while the satellite archive supplies *observed*
  current irradiance so the house heat-loss learner trains against what
  actually happened. Open-Meteo timestamps mark the **end** of the averaging
  interval — verified against sunrise and sunset rather than assumed, since
  reading them as starts shifts all solar gain by one interval, which at dawn
  and dusk is the difference between darkness and full sun.

- **A Solar Irradiance sensor** exposes the current value, with the full
  horizon and source diagnostics in its attributes.

### Dashboard card

- **Clicking the card opens a large version of the chart.** A card in a
  dashboard column is too small to read a 48-hour plan comfortably. Clicking
  anywhere, or the expand button, opens the same chart in a modal that labels
  the time axis every hour instead of every third. It is a native `<dialog>`
  shown with `showModal()`, so it renders in the browser's top layer and cannot
  be clipped by a dashboard column or hidden behind another card.

- **A solar irradiance series**, discovered by the same `plan_kind` marker the
  plan sensors use rather than by a hardcoded entity id — that exact mistake
  caused the v2.6.1 bug where the card never found its sensors. W/m² is a
  fourth unit and both plot edges were already occupied, so it gets an inner
  right-hand axis that only appears when the series is on.

- **Reason codes in the tooltip**, and the estimated-price stretch of the
  horizon shaded and labelled.

- **A what-if simulator** in the expanded view, off by default. Drag the
  comfort temperature, edit the heating hours, and add, remove or retime the
  hot water demand windows — then see what each would cost per month. It
  reports the comfort consequence next to the money, because a plan is always
  cheaper if it is allowed to be colder or to let the tank run down, and a
  simulator showing only the saving would invite exactly that mistake. It runs
  against a *copy* of the configuration, so an exploratory drag never disturbs
  operation, and it is debounced in the card and rate-limited in the
  integration.

---

## Fixed

Most of these were found by tests written to check a mechanism rather than an
outcome. Every one produced output that looked entirely plausible.

- **The capacity tariff raised the peak it was supposed to lower.** The charge
  was the marginal price times the single largest excess. That is wrong twice:
  it under-states a bill that averages the month's top few peaks, so a plan
  with several high hours — exactly what the tariff exists to discourage — was
  charged as if it had one; and `max` has zero gradient everywhere except at
  that one window, so a gradient-based solver saw the term at 1 step in 96 and
  it was effectively inert. It is now the marginal price times the sum of the
  top-k excesses, which is algebraically identical to the bill and gives every
  one of those windows a gradient.

- **On a fresh install the capacity tariff dwarfed the entire energy cost.**
  With no peaks yet recorded the threshold was zero, so every kilowatt counted
  as a brand-new monthly peak — a normal 6 kW day was charged around nine times
  its own energy cost, which would have contorted the plan to avoid a peak the
  house sets on any ordinary day regardless. The threshold now measures against
  what has actually been observed, and the charge stays off until there is
  something real to compare against.

- **The hot water planners could push the tank past its rating.** The
  minimum-run rounding, which raises a sub-minimum slot to a power the hardware
  can really deliver, overshot a 20 litre tank by 28 °C; and with negative
  prices the cost term rewards consumption, so the linearised planner pushed
  through its own temperature ceiling. A capacity clamp now runs after the
  economics, because the tank's rating is physics rather than a preference.

- **System identification fitted the wrong quantity.** The step-response fit
  regressed the room's energy balance against *electrical* draw rather than
  thermal output. Both identified parameters came out scaled by the COP while
  their ratio — the time constant — stayed correct, which is exactly the kind
  of error that looks entirely plausible.

- **The COP learner erased its own learning.** `cop_scale` multiplies the
  nameplate curve, but the modelled COP it was compared against already had the
  current scale folded in, so the update used a *relative* correction as an
  *absolute* target. That makes 1.0 the only fixed point: a sample that
  perfectly confirmed the model still dragged the learned value back towards
  "trust the nameplate".

- **Space-only power was compared against a whole-pump meter.** The current
  action carries space heating in `power` and hot water in `dhw_power`, but an
  electricity meter sees only their sum. Three places compared the space figure
  alone against the measured total, so an ordinary planned hot-water charge
  looked like the pump drawing power nobody asked for — registering as an
  external heat source (freezing every learner and suppressing hot water for
  the decay window), as a collapsed COP, and as a defrost derate, all at once.

- **The defrost derate's humidity dimension was never applied.** The learner
  recorded observations against the real humidity, but every lookup fell back
  to a default that landed in the dry bucket. Everything observed in humid
  frosting conditions — the conditions the feature exists for — was written
  down and then never used.

- **A heated basement's thermal mass was inflated by 25%.** The foundation
  adjustment was applied twice to the lower floor's slow store, in the branch
  used by the most common Swedish two-zone layout.

- **A naive datetime could crash the update loop.** `dt_util.now()` returns a
  timezone-aware value, and comparing it against a naive one raises.

- **The chart tooltip is now anchored to its own chart** rather than to the
  card, so it positions correctly in the expanded view.

- **`strings.json` had drifted from the translations**, so several settings
  showed raw keys instead of labels. All three files are now generated from one
  source and their keys are asserted equal by a test.

- **The what-if debounce timer survived card removal**, firing a multi-second
  solve into a detached DOM after the user had navigated away.

---

## Refactored

The backlog's precondition for this work was a characterization harness, on the
grounds that the existing tests assert on outcomes and would not catch a change
that quietly shifts a plan by one interval or drops a constraint in a rare
branch. That harness was built first, and every change below was made with its
diffs empty.

| | before | after |
|---|---|---|
| `_optimize_with_dhw` / `_optimize_space_only` | 514 / 345 lines | 362 / 175 |
| duplication between them | 162 lines in 17 runs | 37 lines |
| `coordinator.__init__` | 254 lines | 41 |
| `_build_data_dict` | 235 lines | composed from domain views |
| `ThermalParameters.from_config` | 196 lines | a table |
| `config_flow.py` | 1,932 lines | 1,417 |

The optimizer duplication had already caused a real bug — enabling hot water
silently changed the space-heating objective — so the shared cost terms are now
shared in fact. Two eighteen-parameter signatures became one `_Horizon`
context, so adding a per-solve input is one edit instead of four. The config
mapping is a table with a test that probes every declared field for a config
key that actually reaches it, since a forgotten row silently ignores a user's
setting forever.

---

## Tests

- **`tests/golden.py`** records the complete output of 37 scenarios — every
  schedule, trajectory, setpoint, cost, reason code and option-flow field — and
  diffs byte for byte. Its sensitivity is demonstrated rather than assumed:
  shifting a fixture by one interval makes it fail and say so.
- **`tests/stress.py`** sweeps 48 combinations of season, building archetype,
  zoning and feature flags, plus 17 edge conditions, checking physical,
  economic and comfort invariants. It found three of the bugs above. Its
  comfort check compares against what running flat out would achieve, because
  an undersized pump in a leaky house cannot hold the floor and calling that a
  planning bug would be blaming the optimizer for physics.
- **`tests/rolling.py`** drives the real re-planning cycle for several
  simulated days against a plant deliberately mismatched from the model — the
  only test that exercises the self-learning heat-loss correction against a
  house that genuinely differs from its model. Given a 35% error it recovers
  99% of it within two simulated days, converges rather than oscillating, and
  leaves an already-correct model alone. Opt-in via `SLOW=1`.
- **`tests/features.py`** and **`tests/entities.py`** drive the feature modules
  and every entity directly, catching failures that produce no error anywhere:
  a platform registered in one list but not the other, an options menu row with
  no handler, a translation file drifting from `strings.json`, an accumulator
  declared `MEASUREMENT` and therefore invisible to the Energy dashboard.
- The Home Assistant stub is version-controlled in `tests/hastub/` instead of
  living in `/tmp` and vanishing on reboot, and the card's DOM stub now
  *parses* `innerHTML` — storing it as a string was silently skipping every
  path where the card wires up its own controls.
- The README's comfort-weight table and entity counts are asserted, so the
  documentation cannot drift from the code unnoticed. Both had.

---

## Notes

**Attribution.** This project is a fork of
[strutsfarm/heatpump_optimizer](https://github.com/strutsfarm/heatpump_optimizer)
at v2.2.0. The MPC formulation, two-zone thermal model, Tibber and weather
integration, config flow and ECL110 control path are originally strutsfarm's
work, and the upstream copyright is now recorded in `LICENSE`. The README
carries a full acknowledgement and a disclaimer: no warranty, no
responsibility or liability of any kind for any effect, behaviour, function,
failure or damage arising from use of the software, plus specific notes on
safety, legionella, savings claims, equipment responsibility and third-party
services.

**Two things deliberately left alone.** Adjacent comfort weights can invert on
cost by around a percent, because the objective is non-convex and two nearby
settings can land in different basins; neither a third multi-start solve nor a
polishing pass closed the gap, and both cost 25–30% more time. The user-facing
contract — the README's published table of what comfort weight buys — holds
exactly and is tested. Separately, the coordinator's private attribute names
were left as they are: grouping forty of them into dataclasses is a large
mechanical diff across 3,700 lines for no functional gain, and the readability
was obtained by splitting the constructor instead.

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
