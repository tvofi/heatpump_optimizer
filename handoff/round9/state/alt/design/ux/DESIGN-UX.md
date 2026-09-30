# Design of record: lane UX (R9-UX-1..7)

The dusk identity and the lane-UI system of `../DESIGN.md` apply here unchanged: the tokens, the palette of record, the
concept-A panels and the four stat tiles. Mockups are in `out/`: light and dark at 964 px, and the phone at 390 px for
the inbox, health and savings pages. `ux_mockups.py` draws them and `render_ux.mjs` renders them.

- Plan values come from the repository fixture (`../plandata.json`).
- Advisor money, learned parameters, receipt lines and the measured replay series are **examples**, and each mockup
  says so.
- `CONTRAST.json`: all 34 new colour pairs pass (text 4.5:1, graphics 3:1) in both themes.
- `PRE-STUDY-UX.md` holds the facts, decisions U1 to U5, and the placement.

## Shared rules

- **No new colour.** Components use the lane-UI tokens: text, secondary text, surface-2 rows, accent, ok, and heat as
  graphic only. There are three status pairs:
  - ok: `#1c7350` on `#e8f1ed` light, `#1fad6b` on `#1c3027` dark;
  - warn: `#8a5a00` on `#fbf1de` light, `#e3b25a` on `#352c1a` dark;
  - critical: `#b3261e` on `#fbe9e7` light, `#f28b82` on `#3b2322` dark.

  Each is measured in `CONTRAST.json`. A status always carries a word as well as a colour ("Fresh", "Stale").
- **Tabs** are Plan, Setup, Savings, Advisor and Health. Health is new in UX-3. Tab targets are 44 px tall, and a
  row's action button is 32 px tall, above the 24 px floor.
- **Rows** are surface-2 blocks with 12 px radius. Content is a title, a detail and a value (tabular figures, right
  aligned), and at most one action. On a phone the action wraps under the text.
- **Copy** writes the owner's side of the screen. An estimate reads "≈", and an explanation that is inferred rather than
  coded reads "likely because".
- **Documentation (U5).** Each group regenerates the screenshots of the page it changes with the browser test's
  page-screenshot mode (introduced by R9-UI-3), writes them to `docs/img/card/`, and updates that page's section in
  `docs/dashboard-card.md` in the same PR. Screenshots are never captured by hand.

## UX-1: why now, why not (Plan tab)

Mockup: `out/UX-1-why-{light,dark}.png`, the fixture at 16:00.

**Headline.** "Today's plan" lists every narrative line, not only the first: kWh and cost per reason, sorted by spend,
then the idle hours. The lines are the English and Swedish templates already published on the narrative sensor.

**Tooltip on an idle step** (space channel in the example): "16:00–16:15 · Space heating off. Likely because:
- 2.85 SEK/kWh is among the dearest 17 % of the next 24 h (cheapest 0.62);
- the house is coasting on heat stored 00:00–05:00;
- the next run is at 23:00 at 0.78 SEK/kWh."

The footer gives the house and outdoor temperatures. On a hot-water step the tooltip compares the tank temperature
with the published hot-water minimum. With solar ahead, it names the solar surplus.

**Rules:**
- Nothing is claimed that the published fields cannot show: no room floor, no fuse cap.
- Exact sub-codes arrive with UX-5 and replace "likely because" with "because" for the steps they cover.
- The tooltip stays inside the chart and flips left of the crosshair past mid-width.
- **Must keep working:** hover on active steps, the reason strings of today, the lane editor, and pan and zoom.

## UX-2: advisor inbox (Advisor tab)

Mockups: `out/UX-2-inbox-*.png`.

**Section "Worth doing"**, ranked by monthly value:
- hot-water setpoint: "Apply" arrives with UX-5; until then, "Open schedule";
- sensor gap: "Assign sensor" opens today's picker;
- valve target: "Apply" through `assign_entity` with a manual setpoint;
- price of a degree, when enabled: "Try in what-if" opens the simulator with ±1 °C.

**Section "More advice, once turned on"**: wood-stove timing, fuse size and compressor frequency, each with "Open
settings". A disabled or opt-in advisor is never read, only offered.

**States:**
- empty: "Nothing to do: the plan is already as cheap as your settings allow";
- waiting: the advisor's own waiting reason;
- error: "This advice is unavailable right now", with the reason from its attributes.

**Rules:**
- The advisor sensors are added to the card's render signature through a separate list.
- **Must keep working:** today's sensor ranking and its assign flow.

## UX-3: health view (Health tab)

Mockup: `out/UX-3-health-*.png`.

- **Inputs**: one row per required input, with age and limit, and "the plan uses … instead" when it falls back. The
  content comes from Input Problem's published problems.
- **Plan**: solved-ago, next solve, steps, solve time.
- **Still learning**: each waiting sensor with its waiting reason in words.
- **First-plan checklist**:
  - price, weather, indoor and heat-pump write are the required steps;
  - a power meter is recommended;
  - "N insight sensors are off by default", with "Show".
- **"Something looks wrong?"**: download diagnostics.
- The header pill summarises: "1 input stale" (warn), or "All inputs fresh" (ok).

## UX-4: events and blueprint (no card change)

Mockup: `out/UX-4-notify-*.png`.

**Events** (documented in `docs/automations.md`):
- monthly receipt: month, total, saving;
- comfort at risk: predicted minimum, when, the floor, and why;
- input stale: input, age, limit;
- plan stale: age;
- manual plan released: channel, steps, reason.

Each fires once per occurrence, and the notifier remembers what it has sent across restarts.

**Blueprint "Heat pump optimizer notifications"**: a notify target, one toggle per event, and quiet hours that comfort
alerts pass through.

**Copy of the two samples:**
- "Heating and hot water cost 612 kr, 148 kr (19 %) less than a plain thermostat would have."
- "The plan expects 18.6 °C at 06:00, below your 19.0 °C minimum: the fuse limit caps heating 02:00–05:00."

## UX-5: advisor actions and exact idle reasons

No new page. The UX-2 "Apply" on the hot-water setpoint becomes live through a persistent schedule field, and the UX-1
tooltip gains exact sub-codes:
- dearer than the hours used;
- above the floor, coasting;
- capped by the fuse;
- waiting for solar;
- the other channel has the capacity.

The sub-codes are published per step and in the narrative templates, in English and Swedish. The Plan and Advisor
screenshots are regenerated.

## UX-6: money and memory (Savings tab)

Mockups: `out/UX-6-receipt-replay-*.png`.

**Receipt**, per closed month:
- the total;
- the saving against a plain thermostat;
- lines: spot, grid energy fee, capacity charge (new), and compressor wear ("not priced" until a wear price is set),
  with total and basis;
- the note "Covers …; the savings figure compares spot cost only".

**Where the money went**: one-hue horizontal bars per reason, with direct labels and values in text colour. The bars sum
to the spot line.

**Yesterday: the plan against reality**:
- two panels sharing the x-axis: indoor °C (the house colour of record) and cumulative cost (the price colour of
  record);
- the promise dashed, the measurement solid, and a legend that names both;
- one sentence of summary in words;
- the promise is the plan snapshot taken at 00:00.

**Must keep working:** today's monthly savings table and its estimate badge.

## UX-7: model status and diagnostics (Health tab)

Mockup: `out/UX-7-model-*.png`.

**"What the model has learned"**: heat loss, solar gain, lower floor, tank cooling and heat-pump efficiency. Each row
has a value, days of evidence against what the learner needs, and one plain-language sentence. An internal-gains
24-hour bar strip goes in the accent colour.

**Diagnostics bundle** adds the last diagnosis, input states, the plan summary and the learning view, with the token,
the name, `person.*` and `calendar.*` ids redacted and the location coarsened.
