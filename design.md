# Design note: R10-PRODUCT-PAGE-REDESIGN

The product page gets the layout the owner chose on 2026-11-11: "The day,
drawn" (the scroll story of one planned day), with two pieces of the calmer
"datasheet" direction grafted on, the first-week timeline and the control-path
chooser. The dashboard card redesign was declined in the same decision: the
card stays as shipped, and this group touches no card file.

The prototypes were built outside the repository. This note is everything a
fixer needs: where a block is given as code it is the prototype's own text,
already corrected for the page test; where a section is called unchanged, it is
the text of `docs/index.html` at the base and must not be retyped.

Base read for this note: `origin/main` at cbd23f1c8bf6.

## 1. Owning seam and files

One owner: `docs/index.html`, the single-file product page that
`.github/workflows/pages.yml` stages at the site root. Nothing else owns page
content. The workflow, `tools/site/build_docs.mjs`, `docs/site/docs.css` and
the plan page staged beside the site at the plan path are callers or siblings
and do not change.

| file | change |
|---|---|
| `docs/index.html` | the redesign: all markup, CSS and script below |
| a chart generator, new, under `tools/site/` (an .mjs file) | draws the illustrative day; writes it into the page between markers; has a check mode and a self-test |
| `tests/doc_claims.py` | one pin in `check_product_page`: the page's chart equals the generator's output |
| `tests/closure.py`, `tests/closures.json` | classify the new file; the closure is re-measured on Linux, never derived by hand elsewhere (`gate-scoping.md`) |
| a browser harness, new, under `dev/audit/harnesses/` | the checks of section 10 that need a browser |

No image, font or documentation file changes. No new image is added: the chart
is inline SVG. The README is not edited: every sentence quoted below was
checked to be in its cited README section at the base, by the page test's own
normalisation.

## 2. What must not change

- The ten anchors: top, main, how, card, features, works-with, install, limits,
  ai, docs. `tools/site/build_docs.mjs` links the install anchor from every
  sub-page, and outside links use the others.
- Every outbound address and every sub-page link. The set of `href` values at
  the head equals the set at the base (section 10 has the command). Links to
  sub-pages stay relative, as at the base.
- The plan page and its path: nothing here names, links or stages it.
- The claim discipline: every element stating a fact carries its source mark
  and quotes its section whole; page copy that states no fact carries the copy
  mark; no digit sits outside either; no ellipsis.
- The feature headings and the documentation cards, which
  `tests/doc_claims.py` holds equal to the README both ways. The features,
  limits, AI and documentation sections keep their content byte for byte.
- No third-party request of any kind; fonts stay the four self-hosted files
  under `docs/site/fonts/`; images are referenced by path with their
  repository mark, never embedded.
- The theme switch keeps its stored preference and its rewrite of the picture
  sources, exactly as the base script does.
- No saving, percentage or currency figure appears in copy, and none can be
  read off the chart: it has no value axis and no number on it.
- `VERSION`, the manifest, the release notes: untouched.

## 3. Tokens

All values are the base page's; nothing is recoloured.

| role | light | dark |
|---|---|---|
| page background | #f3f8fc | #0b1a28 |
| surface | #ffffff | #11263a |
| second surface, well | #eef4f9, #e8f0f6 | #16304a |
| text | #0f2233 | #eaf2f8 |
| secondary text | #4d5d6c | #a9bccb |
| hairline | #d6e0e8 | #24405a |
| accent: links, numbers, the price line | #026aa8 | #4fb3f0 |
| heat as text | #b4501a | #f08a3c |
| heat as a mark or bar | #d2601f | #f08a3c |
| green: the house temperature | #1c7350 | #3cc488 |
| hero wash, top to bottom | #e3eef7 to #f3f8fc | #10263b to #0b1a28 |

Blue is the price and the plan's line; ember is heat that was bought. Green is
used only for the house temperature and the measured points.

Type: Outfit 600 and 700 for headings, line height 1.15, balanced wrapping;
Source Sans 3 400 and 600 for body, 17 px on 1.55, paragraphs capped at 66
characters; small labels are Source Sans 3 600 at .74rem, upper case, tracked
.12em, in the secondary colour; the system monospace for code and the chart's
hour axis. Scale: page title clamp(2.4rem, 6.4vw, 4.4rem) with -.02em
tracking; section title clamp(1.6rem, 3.2vw, 2.25rem); step title 1.5rem; card
title 1.12rem; lede clamp(1.08rem, 1.6vw, 1.25rem).

Shape and space: content width 74rem with 20 px gutters; 12 px corners on
surfaces, 16 px on the chart card; pills for chips; 1 px hairlines; 16 px grid
gaps; sections open with 88 px of space; one soft shadow under the chart card
and one under the card screenshot (0 18px 40px, spread -28px and -24px, ink at
45%). Focus: a 3 px accent outline at 2 px offset on everything focusable.

Motion: only transform and opacity move. Durations .3 to .6 s, the price line
1.1 s, bars .5 s staggered 45 ms each. Every animation and transition sits
inside a no-preference motion query; with reduced motion nothing moves.

Base rules that change, all small: add a monospace token and use it for code
and the axis; `html` gets a scroll padding of 76 px; `body` clips horizontal
overflow; the sticky header's layer rises to 30 and the skip link's to 40 (the
header keeps its safe-area top inset); the section-nav hides below 940 px;
the hidden attribute always wins (display none, important); without the script
class the tab list and the theme button are not shown; the base's hero figure
rules and three-step rules are deleted with their markup; the dark backdrop the
base gives the hero's card screenshot moves with that screenshot to the card
section.

## 4. Page order

Top bar, hero, then: how it works, the dashboard card, what it does, works
with, get started, known limitations, written with AI, documentation, footer.
The base has features before how it works; the story moves up because it is the
explanation. The section nav in the top bar follows the new order (the
prototype left the old order; that was an oversight). Every section heading,
eyebrow and anchor keeps its base text.

A `script` in the head adds the class `js` to the root element before first
paint; every script-dependent style keys on it. A thin progress line, an empty
element hidden from assistive technology, is the first child of the body.

Section heads and section bodies outside the hero and the scroll story carry
the reveal class (opacity 0 and 14 px down, to rest, once, when 8% inside the
viewport). The features grid also staggers its cards by column.

## 5. Hero

Text column left, a decorative strip of the same illustrative day right (price
line wiping in from the left, bars rising after it), stat tiles under both, and
a link down to the story. The card screenshot that the base shows here moves to
the card section. Below 900 px the strip sits under the text at full width.

The strip reuses the generator's price and bars layers in a 720 by 236 view box
(the top of the chart), is hidden from assistive technology, shows heating bars
only, and carries no label: it echoes the README banner, which has none.

```html
<div class="hero" id="top">
  <div class="wrap">
   <div class="hero-top">
    <div class="hero-txt">
    <span class="eyebrow">Home Assistant integration · installs from the Marketplace or HACS</span>
    <h1 data-src="README.md#heat-pump-cost-optimizer-for-home-assistant">As warm as you asked, <em>bought in better hours</em>.</h1>
    <p class="lede" data-src="README.md#heat-pump-cost-optimizer-for-home-assistant">Model-predictive heating control for Home Assistant. It plans your heat pump and your hot water 24 hours ahead against hourly electricity prices, the weather forecast, and a thermal model of your own house that it keeps correcting from your own sensors.</p>
    <div class="cta">
      <a class="btn primary" href="#install">Install from the Marketplace</a>
      <a class="btn ghost" href="#docs">Read the documentation</a>
    </div>
    </div>
    <div class="hero-art" aria-hidden="true"><div class="w"><svg viewBox="0 0 720 236"><!-- chart:price --><!-- /chart:price --></svg></div><svg viewBox="0 0 720 236"><!-- chart:bars --><!-- /chart:bars --></svg></div>
   </div>
    <div class="tiles" aria-label="At a glance">
      <div class="tile" data-src="README.md#what-it-does" data-q="A 24-hour model-predictive plan is re-solved on every interval"><span class="v">24<small>h</small></span><span class="l">plan, re-solved every interval</span></div>
      <div class="tile" data-src="README.md#your-first-week" data-q="30 minutes by default"><span class="v">30<small>min</small></span><span class="l">between solves, by default</span></div>
      <div class="tile" data-src="README.md#what-it-does" data-q="pins exact run slots for up to 20 hours"><span class="v">20<small>h</small></span><span class="l">of run slots you can pin yourself</span></div>
      <div class="tile" data-src="README.md#what-it-does" data-q="entity names are translated (English, Swedish and German)"><span class="v">EN<small>·</small>SV<small>·</small>DE</span><span class="l">entity names follow your language</span></div>
    </div>
    <a class="next" href="#how" data-copy><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>Scroll through one day</a>
  </div>
</div>
```

The empty comment pairs are the generator's markers (section 8).

## 6. How it works: the scroll story

Two columns from 900 px up: five steps on the left, the chart card pinned on
the right at 84 px from the top. Each step is about three quarters of a
viewport tall, so one step is in play at a time. Entering step n shows layers 1
to n and marks step n as current (ember left rule, filled number):

| step | title | layer it adds | legend chips it lights |
|---|---|---|---|
| 1 | Read | the stepped price line wipes in left to right; the dotted forecast line fades in | Price, Forecast |
| 2 | Plan | space-heating bars rise in the cheap hours; the dashed comfort floor appears | Space heating, Comfort floor |
| 3 | Plan the hot water with it | two shaded demand time frames; one outlined hot-water bar before each | Hot water, Demand time frame |
| 4 | Act | the green house-temperature line | House temperature |
| 5 | Learn | measured points beside the line | Measured afterwards |

Scrolling back up removes layers again; above the first step the chart is the
bare grid. A chip not yet lit is dashed and dimmed, never removed, so the
legend does not jump. The chart carries the word "Illustrative" as a pill in
its legend and one line of small print under it.

Below 900 px the chart card pins under the top bar at 60 px, full bleed, with
its heading and small print hidden and its chips shrunk; steps are 64% of the
viewport tall and scroll beneath it.

The base's how-it-works picture and its three step cards are removed from the
page (the picture remains in the README and on the how-it-works sub-page). All
their sentences are kept, in the five steps.

```html
<section class="band" id="how" aria-labelledby="how-h">
  <div class="sec-head"><span class="eyebrow">How it works</span><h2 id="how-h">One solve every interval: read, plan, act, learn</h2></div>
  <div class="scrolly">
    <div class="viz" id="viz"><div class="vizcard">
      <div class="vizhead"><span class="eyebrow" data-copy>One day, as a plan</span></div>
      <div class="chart" role="img" aria-label="An illustrative day: a stepped price line with a morning and an evening peak; heating slots sit in the cheap night and midday hours, one hot-water run sits before each of two demand windows, and the house temperature stays above the comfort floor all day">
        <svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:grid --><!-- /chart:grid --></svg>
        <div class="lay l-win"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:windows --><!-- /chart:windows --></svg></div>
        <div class="lay l-price"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:price --><!-- /chart:price --></svg></div>
        <div class="lay l-out"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:outdoor --><!-- /chart:outdoor --></svg></div>
        <div class="lay l-bars"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:bars --><!-- /chart:bars --></svg></div>
        <div class="lay l-floor"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:floor --><!-- /chart:floor --></svg></div>
        <div class="lay l-house"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:comfort --><!-- /chart:comfort --></svg></div>
        <div class="lay l-meas"><svg viewBox="0 0 720 380" aria-hidden="true"><!-- chart:measured --><!-- /chart:measured --></svg></div>
      </div>
      <div class="axis" aria-hidden="true" data-copy><span>00</span><span>06</span><span>12</span><span>18</span><span>24 h</span></div>
      <ul class="legend" aria-label="Legend">
        <li class="chip k1"><i class="k-price"></i>Price</li>
        <li class="chip k1"><i class="k-out"></i>Forecast</li>
        <li class="chip k2"><i class="k-heat"></i>Space heating</li>
        <li class="chip k2"><i class="k-floor"></i>Comfort floor</li>
        <li class="chip k3"><i class="k-dhw"></i>Hot water</li>
        <li class="chip k3"><i class="k-win"></i>Demand time frame</li>
        <li class="chip k4"><i class="k-house"></i>House temperature</li>
        <li class="chip k5"><i class="k-meas"></i>Measured afterwards</li>
        <li class="illus">Illustrative</li>
      </ul>
      <p class="fine" data-copy>An illustrative day drawn by a toy planner on this page. It is not a recording of the integration, and no number is read off it.</p>
    </div></div>
    <ol class="steps-a" id="steps" style="list-style:none;margin:0;padding:0">
      <li class="st" data-step="1"><div class="in" data-src="README.md#how-it-works">
        <h3 data-copy><span class="n" aria-hidden="true">1</span>Read</h3>
        <ul><li>Published hourly prices</li><li>Temperature, wind, rain, forecast irradiance</li><li>Indoor/outdoor temps, tank temps, power</li></ul>
      </div></li>
      <li class="st" data-step="2"><div class="in">
        <h3 data-copy><span class="n" aria-hidden="true">2</span>Plan</h3>
        <p class="q" data-src="README.md#how-it-works">Solve: minimize cost + comfort penalty subject to comfort floor, tank limits, legionella clock, fuse and peak caps</p>
        <p data-src="README.md#what-it-does">A 24-hour model-predictive plan is re-solved on every interval against the full forecast trajectory, not against the weather right now.</p>
      </div></li>
      <li class="st" data-step="3"><div class="in" data-src="README.md#what-it-does">
        <h3 data-copy><span class="n" aria-hidden="true">3</span>Plan the hot water with it</h3>
        <p class="q">Space heating and hot water share one compressor, so they are planned against each other rather than one after the other.</p>
        <p>Hot water is guaranteed inside demand time frames rather than kept permanently hot, which is where most of the saving comes from.</p>
      </div></li>
      <li class="st" data-step="4"><div class="in">
        <h3 data-copy><span class="n" aria-hidden="true">4</span>Act</h3>
        <p class="q" data-src="README.md#how-it-works">Publish plan sensors, switch the heat pump, ECL110 displace / frequency advice</p>
        <p data-src="README.md#known-limitations">The plan is re-solved once per optimization interval — 30 minutes by default — and holds until the next solve.</p>
      </div></li>
      <li class="st" data-step="5"><div class="in">
        <h3 data-copy><span class="n" aria-hidden="true">5</span>Learn</h3>
        <p class="q" data-src="README.md#how-it-works">Afterwards: compare prediction against reality, nudge the learned parameters</p>
        <p data-src="README.md#what-it-does">Every learner is snapshotted weekly (the last eight are kept), and a drift watchdog can roll them back to the last healthy snapshot.</p>
        <p data-copy>The full theory: <a href="how-it-works.html">how it works</a></p>
      </div></li>
    </ol>
  </div>
</section>
```

## 7. The other sections

**The dashboard card.** The base's lead block (heading, paragraph, the YAML
line, the documentation link), then the card screenshot moved from the hero
with its caption, then the base's gallery. In the gallery markup no panel
carries the hidden attribute any more: the script hides the unselected ones, so
a browser without script shows all four.

```html
  <figure class="shot rv">
    <div class="stage"><img src="img/card/card-plan-chart.png" data-repo="docs/img/card/card-plan-chart.png" width="1864" height="1700" loading="lazy" alt="The dashboard card's plan chart: 24 hours of spot price, forecast temperature and solar, over the heating and hot-water slots the optimizer chose"></div>
    <figcaption data-src="README.md#heat-pump-cost-optimizer-for-home-assistant">The next 24 hours as the optimizer sees them — price, forecast, solar, and the slots it picked for heating and for hot water.</figcaption>
  </figure>
```

**What it does.** Unchanged content; the grid gains the reveal.

**Works with.** The three requirement panels are unchanged. The control-path
table is replaced by the chooser grafted from the datasheet direction: one
question, four radio pills, and under them what you provide and what the
optimizer writes for the chosen path. It is the table's own text, cell for
cell; the sentence that stood under the table is the fourth answer. It needs no
script: the panes are switched by the checked radio in CSS. A browser without
the needed selector shows all four answers stacked, each under its own name
(add the path name as a small heading inside each pane, shown only in that
fallback and in print, so stacked answers are told apart). Arrow keys move
between the radios as the platform provides; the focus ring is drawn on the
pill.

```html
  <div class="cp rv" data-src="README.md#supported-heat-pumps-and-controls">
    <fieldset><legend data-copy>How is your heat pump controlled?</legend>
      <div class="opts">
        <label><input type="radio" name="cp" id="cp1" checked>On/off switch</label>
        <label><input type="radio" name="cp" id="cp2">ECL110 heat curve</label>
        <label><input type="radio" name="cp" id="cp3">Compressor frequency</label>
        <label data-copy><input type="radio" name="cp" id="cp0">None of these</label>
      </div>
    </fieldset>
    <div aria-live="polite">
      <div class="pp p1"><div><span class="eyebrow">You provide</span><p>a switch that turns the heat pump on and off</p></div><div><span class="eyebrow">The optimizer writes</span><p>may turn it off during expensive hours</p></div></div>
      <div class="pp p2"><div><span class="eyebrow">You provide</span><p>a Danfoss ECL110-compatible weather-compensated controller, reachable over MQTT</p></div><div><span class="eyebrow">The optimizer writes</span><p>a heat-pump on/off decision and an integer parallel shift (displace) onto the controller's own heat curve</p></div></div>
      <div class="pp p3"><div><span class="eyebrow">You provide</span><p>the compressor frequency exposed as a number entity (typically from Modbus or ESPHome)</p></div><div><span class="eyebrow">The optimizer writes</span><p>the recommended frequency via number.set_value — but only once you switch the mode to Control</p></div></div>
      <div class="pp p0"><div class="one"><span class="eyebrow" data-copy>With none of them</span><p>Each path is optional, the three are independent of each other, and with none of them configured “the plan is published on sensors for your own automations to act on”</p></div></div>
    </div>
  </div>
```

The fourth label is page copy, not a quotation, and is marked so; the
prototype lacked that mark and the page test would have refused it.

**Get started.** The two-column block and the four setup screenshots are
unchanged, except that the small "Immediately" panel leaves the right column:
its sentence is the first stop of the timeline that now closes the section, and
the same sentence twice in one section reads as a mistake. The first-week
timeline, grafted from the datasheet direction: four stops on one ruled line,
the first two with filled ember squares, the last two outlined; a column of
four from 860 px up, a vertical line with the squares on it below. Stop titles
are one level below the "Your first week" heading.

```html
  <h3 style="margin-top:44px" data-copy>Your first week</h3>
  <ol class="week rv" data-src="README.md#your-first-week">
    <li><h4>Immediately.</h4><p>The first plan is solved within one optimization interval (30 minutes by default). Add the dashboard card and you can see what it intends to do.</p></li>
    <li><h4>Day one.</h4><p>If you want the commissioning step test, first switch on Allow a one-off measurement experiment under Advanced settings → Self-learning and diagnostics</p></li>
    <li><h4>The first days.</h4><p>The heat-loss scale, tank cooling rates and the COP curve start correcting themselves as soon as there is data to correct them with.</p></li>
    <li><h4>The first weeks.</h4><p>Hot-water draw quantiles and the heavy-day demand sensor need weeks of observation before they mean anything, and stay unavailable until they do.</p></li>
  </ol>
```

**Known limitations, Written with AI, Documentation, footer.** Unchanged.

## 8. The chart and its generator

The chart is committed in the page as plain SVG, eight layers each in its own
`svg` element stacked in one box of ratio 720 to 380, so it draws without
script. It is not hand-edited: a generator under `tools/site/` owns it.

The generator's interface, in words: with a write flag it replaces the text
between each marker pair in the page (an HTML comment naming the layer, and its
closing twin) with that layer's markup; with a check flag it exits non-zero,
naming the layer, when any pair's content differs from what it would write;
with a self-test flag it asserts the invariants below. The hero's two pairs
take the same strings as the story's price and bars layers.

The model is a toy and says so in its own header. Its whole text:

```js
/* The illustrative day and the toy planner behind every chart on this page.
   Not the integration's solver: a 24-step dynamic programme over a house that
   gains three units of stored heat in a heating hour and loses one in an idle
   hour, with one hot-water run owed before each of two demand windows and one
   compressor shared between the two. Prices are unitless. */
const HPO = (() => {
  const PRESETS = {
    peaks: [3.0, 2.6, 2.3, 2.1, 2.0, 2.5, 4.2, 6.6, 8.6, 8.0, 6.9, 5.9, 5.4, 5.1, 5.6, 6.7, 8.8, 9.6, 9.1, 7.6, 6.2, 5.0, 4.4, 3.8],
  };
  const CAP = 9, START = 3, GAIN = 3;
  const WINDOWS = [[6, 9], [18, 21]];          // hot-water demand windows, [from, to)
  const DHW_SPANS = [[2, 6], [14, 18]];        // hours a run may sit in, inclusive

  function baseline(p) {
    const space = Array(24).fill(false), dhw = Array(24).fill(false), temp = [START];
    let t = START;
    for (let h = 0; h < 24; h++) {
      if (h === 6 || h === 18) { dhw[h] = true; t -= 1; }
      else if (t <= 1) { space[h] = true; t += GAIN; }
      else t -= 1;
      temp.push(t);
    }
    return finish(p, space, dhw, temp);
  }

  function finish(p, space, dhw, temp) {
    let cost = 0, n = 0, cheap = 0;
    const mean = p.reduce((a, b) => a + b, 0) / 24;
    for (let h = 0; h < 24; h++) if (space[h] || dhw[h]) { cost += p[h]; n++; if (p[h] < mean - 1e-9) cheap++; }
    return { space, dhw, temp, cost, hours: n, cheap, mean };
  }

  function dp(p, dhwHours, endMin) {
    const INF = 1e9;
    let cur = Array(CAP + 1).fill(INF); cur[START] = 0;
    const back = [];
    for (let h = 0; h < 24; h++) {
      const nxt = Array(CAP + 1).fill(INF), from = Array(CAP + 1).fill(null);
      for (let t = 0; t <= CAP; t++) {
        if (cur[t] >= INF) continue;
        if (dhwHours.includes(h)) {
          if (t - 1 >= 0 && cur[t] + p[h] < nxt[t - 1]) { nxt[t - 1] = cur[t] + p[h]; from[t - 1] = [t, false]; }
          continue;
        }
        if (t - 1 >= 0 && cur[t] < nxt[t - 1] - 1e-9) { nxt[t - 1] = cur[t]; from[t - 1] = [t, false]; }
        if (t + GAIN <= CAP && cur[t] + p[h] < nxt[t + GAIN] - 1e-9) { nxt[t + GAIN] = cur[t] + p[h]; from[t + GAIN] = [t, true]; }
      }
      back.push(from); cur = nxt;
    }
    let best = -1;
    for (let t = endMin; t <= CAP; t++) if (cur[t] < INF && (best < 0 || cur[t] < cur[best] - 1e-9)) best = t;
    if (best < 0) return null;
    const space = Array(24).fill(false), temp = Array(25).fill(0);
    let t = best; temp[24] = t;
    for (let h = 23; h >= 0; h--) { const [pt, on] = back[h][t]; space[h] = on; t = pt; temp[h] = t; }
    return { cost: cur[best], space, temp };
  }

  function solve(p) {
    const base = baseline(p);
    const endMin = base.temp[24];
    let best = null;
    for (let a = DHW_SPANS[0][0]; a <= DHW_SPANS[0][1]; a++)
      for (let b = DHW_SPANS[1][0]; b <= DHW_SPANS[1][1]; b++) {
        const r = dp(p, [a, b], endMin);
        if (r && (!best || r.cost < best.r.cost - 1e-9)) best = { r, a, b };
      }
    const dhw = Array(24).fill(false); dhw[best.a] = dhw[best.b] = true;
    return { plan: finish(p, best.r.space, dhw, best.r.temp), base };
  }

  /* Geometry: a 720 x 380 drawing, no text in it. */
  const G = { W: 720, H: 380, L: 10, cw: 700 / 24, pTop: 22, pBase: 214, tFloor: 356, tStep: 9 };
  const x = h => +(G.L + h * G.cw).toFixed(2);
  const py = v => +(G.pBase - 62 - v * 13).toFixed(2);
  const ty = t => +(G.tFloor - 6 - t * G.tStep).toFixed(2);

  function grid() {
    let s = "";
    for (let h = 0; h <= 24; h++) s += `<line class="g${h % 6 ? "" : " g6"}" x1="${x(h)}" x2="${x(h)}" y1="${G.pTop}" y2="${G.pBase}"/>`;
    s += `<line class="g g6" x1="${x(0)}" x2="${x(24)}" y1="${G.pBase}" y2="${G.pBase}"/>`;
    return s;
  }
  function windows() {
    return WINDOWS.map(([a, b]) => `<rect class="c-win" x="${x(a)}" y="${G.pTop}" width="${+(x(b) - x(a)).toFixed(2)}" height="${G.pBase - G.pTop}"/>`).join("");
  }
  function price(p) {
    let d = `M${x(0)} ${py(p[0])}`;
    for (let h = 0; h < 24; h++) d += ` V${py(p[h])} H${x(h + 1)}`;
    return `<path class="c-price-fill" d="${d} V${G.pBase} H${x(0)} Z"/><path class="c-price" d="${d}"/>`;
  }
  function bars(s, cls) {
    let out = "", i = 0;
    for (let h = 0; h < 24; h++) {
      if (!s.space[h] && !s.dhw[h]) continue;
      const hh = s.space[h] ? 50 : 32;
      out += `<rect class="bar ${s.space[h] ? "c-heat" : "c-dhw"}${cls ? " " + cls : ""}" style="--i:${i++}" x="${+(x(h) + 4).toFixed(2)}" y="${G.pBase - 4 - hh}" width="${+(G.cw - 8).toFixed(2)}" height="${hh}" rx="4"/>`;
    }
    return out;
  }
  function comfort(s) {
    const pts = s.temp.map((t, h) => `${x(h)} ${ty(t)}`).join(" L");
    return `<path class="c-house" d="M${pts}"/>`;
  }
  function floor() {
    return `<line class="c-floor" x1="${x(0)}" x2="${x(24)}" y1="${G.tFloor}" y2="${G.tFloor}"/>`;
  }
  function outdoor() {
    let d = "";
    for (let h = 0; h <= 24; h++) { const v = 250 + 9 * Math.cos((h - 15) / 24 * 2 * Math.PI) * -1 + 9; d += (h ? " L" : "M") + x(h) + " " + v.toFixed(1); }
    return `<path class="c-out" d="${d}"/>`;
  }
  /* What the house then did: the prediction, a little off, as the learners see it. */
  function measured(s) {
    let out = "";
    const off = [0, 2, 3, 1, -2, -3, -1, 2, 3, 2, 0, -2, -3, -2, 1, 2, 3, 1, -1, -2, -3, -1, 1, 2, 1];
    for (let h = 1; h <= 24; h++) out += `<circle class="c-meas" style="--i:${h}" cx="${x(h)}" cy="${(ty(s.temp[h]) + off[h]).toFixed(1)}" r="3.2"/>`;
    return out;
  }
  function layers(p, s) {
    return { grid: grid(), windows: windows(), price: price(p), bars: bars(s), comfort: comfort(s), floor: floor(), outdoor: outdoor(), measured: measured(s) };
  }
  return { PRESETS, WINDOWS, G, solve, layers };
})();
if (typeof module !== "undefined") module.exports = HPO;
```

The page draws the first preset. Its solution, for the reviewer: space heating
in hours 3, 4, 5, 12, 13 and 23; hot water in hours 2 and 14; stored heat by
hour 3, 2, 1, 0, 3, 6, 9, 8, 7, 6, 5, 4, 3, 6, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 3.

Invariants the self-test asserts: stored heat is never below zero (the line
never crosses the floor); exactly one hot-water run sits in each allowed span
and ends before its demand window opens; the plan's cost is not above the
unoptimized schedule's on the drawn day; a flat price gives equal cost for
both; two runs give byte-identical output.

## 9. New CSS and script

The story, the hero strip, the progress line, the card lead and the features
reveal:

```css
.progress { display: none }
@supports (animation-timeline: scroll()) { @media (prefers-reduced-motion: no-preference) {
  .progress { display: block; position: fixed; inset: 0 0 auto 0; height: 3px; background: var(--heat-mark); transform-origin: 0 50%; z-index: 35; animation: grow linear both; animation-timeline: scroll(root) }
  @keyframes grow { from { transform: scaleX(0) } to { transform: scaleX(1) } }
} }

.hero { position: relative; background: linear-gradient(180deg, var(--hero-a), var(--hero-b)); border-bottom: 1px solid var(--line); overflow: hidden }
.hero .wrap { position: relative; padding-block: 84px 60px; display: grid; gap: 26px }
.hero h1 { font-size: clamp(2.4rem, 6.4vw, 4.4rem); font-weight: 700; letter-spacing: -.02em; max-width: 15ch }
.hero h1 em { font-style: normal; color: var(--heat) }
.hero .lede { font-size: clamp(1.08rem, 1.6vw, 1.25rem); max-width: 58ch }
.hero-top { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 32px; align-items: end }
.hero-txt { display: grid; gap: 26px }
.hero-art { position: relative; aspect-ratio: 720 / 236; align-self: end; margin-bottom: 4px; -webkit-mask-image: linear-gradient(90deg, transparent, #000 30%); mask-image: linear-gradient(90deg, transparent, #000 30%) }
.hero-art .w, .hero-art svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block }
.hero-art .w { overflow: hidden }
.hero-art .c-price { fill: none; stroke: var(--accent); stroke-width: 3; stroke-linejoin: round }
.hero-art .c-price-fill { fill: var(--accent); opacity: .07 }
.hero-art .c-heat { fill: var(--heat-mark) } .hero-art .c-dhw { display: none }
.hero-art .bar { transform-box: fill-box; transform-origin: 50% 100% }
@media (max-width: 900px) { .hero-top { grid-template-columns: 1fr; gap: 18px } .hero-art { -webkit-mask-image: none; mask-image: none; opacity: .9 } }
.hero .tiles { margin-top: 10px }
.next { display: inline-flex; align-items: center; gap: 10px; color: var(--ink-2); font-weight: 600; text-decoration: none; margin-top: 6px; width: fit-content }
.next svg { width: 18px; height: 18px }

.scrolly { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 56px; align-items: start }
.viz { position: sticky; top: 84px; order: 2 }
.vizcard { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 20px 22px 18px; display: grid; gap: 12px; box-shadow: 0 18px 40px -28px rgb(15 34 51 / .45) }
.vizhead { display: flex; justify-content: space-between; align-items: center; gap: 12px }
.fine { font-size: .84rem; color: var(--ink-2) }
.st { display: grid; align-content: center; padding-block: 18px }
@media (prefers-reduced-motion: no-preference) {
  .js .st { min-height: 74vh; padding-block: 0 }
  .js .st:first-child { min-height: 52vh; align-content: start; padding-top: 6vh }
  .js .st:last-child { min-height: 60vh }
}
.st .in { display: grid; gap: 12px; padding: 4px 0 4px 22px; border-left: 3px solid var(--line) }
.st h3 { font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 12px }
.st .n { display: inline-grid; place-items: center; width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--accent); color: var(--accent); font: 700 .95rem var(--f-display); flex: none }
.st p, .st li { color: var(--ink-2) }
.st ul { margin: 0; padding-left: 1.1em; display: grid; gap: 4px }
.st .q { color: var(--ink) }
.st.on .in { border-left-color: var(--heat-mark) }
.st.on .n { background: var(--accent); color: var(--accent-ink) }
@media (max-width: 900px) {
  .scrolly { grid-template-columns: 1fr; gap: 0 }
  .viz { order: 0; top: 60px; z-index: 5; margin-inline: -20px; padding: 10px 12px; background: var(--bg); border-bottom: 1px solid var(--line) }
  .vizcard { padding: 12px 12px 10px; gap: 8px; box-shadow: none; border-radius: 12px }
  .viz .fine, .viz .vizhead { display: none }
  .viz .chip { font-size: .74rem; padding: 2px 8px; gap: 5px }
  .viz .illus { font-size: .62rem; padding: 4px 8px }
  .viz .legend { gap: 4px }
  .viz .axis { font-size: .7rem; margin-top: 0 }
  @media (prefers-reduced-motion: no-preference) { .js .st, .js .st:first-child, .js .st:last-child { min-height: 64vh; padding-top: 5vh; align-content: start } }
  html:not(.js) .viz { position: static }
}

/* the layers: all drawn without the script; with it, each waits for its step */
.l-price { overflow: hidden !important }
.js .viz:not(.s1) .l-price, .js .viz:not(.s1) .l-out,
.js .viz:not(.s3) .l-win, .js .viz:not(.s4) .l-house, .js .viz:not(.s2) .l-floor, .js .viz:not(.s5) .l-meas { opacity: 0 }
.js .viz:not(.s1) .l-price { transform: translateX(-100%) }
.js .viz:not(.s1) .l-price > svg { transform: translateX(100%) }
.js .viz:not(.s2) .c-heat, .js .viz:not(.s3) .c-dhw { transform: scaleY(0); opacity: 0 }
.js .viz:not(.s1) .k1 i, .js .viz:not(.s2) .k2 i, .js .viz:not(.s3) .k3 i, .js .viz:not(.s4) .k4 i, .js .viz:not(.s5) .k5 i { opacity: .25 }
.js .viz:not(.s1) .k1, .js .viz:not(.s2) .k2, .js .viz:not(.s3) .k3, .js .viz:not(.s4) .k4, .js .viz:not(.s5) .k5 { border-style: dashed; background: transparent; color: var(--ink-2) }
@media (prefers-reduced-motion: no-preference) {
  .lay { transition: opacity .6s ease }
  .chip i { transition: opacity .3s ease }
  .l-price, .l-price > svg { transition: transform 1.1s cubic-bezier(.4, 0, .2, 1), opacity .2s }
  .chart .bar { transition: transform .5s cubic-bezier(.2, .8, .2, 1), opacity .3s; transition-delay: calc(var(--i) * 45ms) }
  .st .in, .st .n { transition: border-color .3s, background-color .3s, color .3s }
  .hero-art .w { animation: wipe-a 1.5s cubic-bezier(.4, 0, .2, 1) .2s both }
  .hero-art .w > svg { animation: wipe-b 1.5s cubic-bezier(.4, 0, .2, 1) .2s both }
  .hero-art .bar { animation: bar-up .5s cubic-bezier(.2, .8, .2, 1) both; animation-delay: calc(1.3s + var(--i) * 70ms) }
  @keyframes wipe-a { from { transform: translateX(-100%) } to { transform: none } }
  @keyframes wipe-b { from { transform: translateX(100%) } to { transform: none } }
  @keyframes bar-up { from { transform: scaleY(0) } to { transform: none } }
}

.cardlead { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 32px; align-items: start; margin-bottom: 26px }
@media (max-width: 860px) { .cardlead { grid-template-columns: 1fr } }
.shot { display: grid; gap: 10px; margin-bottom: 30px }
.shot .stage { box-shadow: 0 18px 40px -24px rgb(15 34 51 / .45) }
.features { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); gap: 16px }
@media (prefers-reduced-motion: no-preference) {
  .js .features .feat { opacity: 0; transform: translateY(14px); transition: opacity .5s ease, transform .5s ease }
  .js .features.in .feat { opacity: 1; transform: none }
  .features .feat:nth-child(3n+2) { transition-delay: 80ms } .features .feat:nth-child(3n) { transition-delay: 160ms }
}
```

The chart, the legend and the section reveal:

```css
.week h4 { font: 600 1.12rem/1.15 var(--f-display); margin: 0 }
/* the illustrative chart: the mark's two colours, plus the card's green for the house */
.chart { position: relative; aspect-ratio: 720 / 380 }
.chart > svg, .chart .lay, .chart .lay > svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block; overflow: visible }
.chart .g { stroke: var(--c-grid, var(--line)); stroke-width: 1; opacity: .55 }
.chart .g6 { opacity: 1 }
.chart .c-price { fill: none; stroke: var(--c-price, var(--accent)); stroke-width: 3; stroke-linejoin: round; stroke-linecap: round }
.chart .c-price-fill { fill: var(--c-price, var(--accent)); opacity: .08 }
.chart .c-heat { fill: var(--c-heat, var(--heat-mark)) }
.chart .c-dhw { fill: color-mix(in srgb, var(--c-heat, var(--heat-mark)) 28%, transparent); stroke: var(--c-heat, var(--heat-mark)); stroke-width: 2 }
.chart .c-win { fill: var(--c-price, var(--accent)); opacity: .09 }
.chart .c-house { fill: none; stroke: var(--c-ok, var(--ok)); stroke-width: 3; stroke-linejoin: round; stroke-linecap: round }
.chart .c-floor { stroke: var(--c-ink2, var(--ink-2)); stroke-width: 2; stroke-dasharray: 6 6 }
.chart .c-out { fill: none; stroke: var(--c-price, var(--accent)); stroke-width: 2; stroke-dasharray: 3 6; stroke-linecap: round; opacity: .75 }
.chart .c-meas { fill: var(--c-surface, var(--surface)); stroke: var(--c-ok, var(--ok)); stroke-width: 2 }
.chart .bar { transform-box: fill-box; transform-origin: 50% 100% }
.axis { display: flex; justify-content: space-between; font: .78rem var(--f-mono); color: var(--ink-2); padding-inline: 1.2%; margin-top: 6px }
.legend { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; list-style: none; margin: 0; padding: 0 }
.chip { display: inline-flex; align-items: center; gap: 8px; padding: 5px 12px; border: 1px solid var(--line); border-radius: 999px; font-size: .88rem; background: var(--surface); color: var(--ink) }
.chip i { width: 14px; height: 10px; border-radius: 3px; flex: none; display: block }
.chip .k-price { height: 3px; background: var(--accent) }
.chip .k-heat { background: var(--heat-mark) }
.chip .k-dhw { background: color-mix(in srgb, var(--heat-mark) 28%, transparent); border: 2px solid var(--heat-mark) }
.chip .k-house { height: 3px; background: var(--ok) }
.chip .k-floor { height: 0; border-top: 2px dashed var(--ink-2); border-radius: 0 }
.chip .k-win { background: color-mix(in srgb, var(--accent) 18%, transparent) }
.chip .k-out { height: 0; border-top: 2px dotted var(--accent); border-radius: 0 }
.chip .k-meas { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--ok); background: var(--surface) }
.illus { display: inline-flex; align-items: center; gap: 6px; font: 600 .74rem/1 var(--f-body); letter-spacing: .08em; text-transform: uppercase; color: var(--heat); border: 1px solid currentColor; border-radius: 999px; padding: 5px 10px; white-space: nowrap }

/* section reveals: only once the script has said it is running, never under reduced motion */
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth }
  .js .rv { opacity: 0; transform: translateY(14px); transition: opacity .5s ease, transform .5s ease }
  .js .rv.in { opacity: 1; transform: none }
}
```

The chooser and the timeline:

```css
/* works with: pick your control path */
.cp { margin-top: 22px; border: 1px solid var(--line); border-radius: var(--r); background: var(--surface); padding: 18px 20px 20px; display: grid; gap: 14px }
.cp fieldset { border: 0; margin: 0; padding: 0; min-width: 0 }
.cp legend { padding: 0; margin-bottom: 10px; font: 600 1.05rem var(--f-display) }
.cp .opts { display: flex; flex-wrap: wrap; gap: 8px }
.cp .opts label { position: relative; display: inline-flex; align-items: center; min-height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 999px; font-weight: 600; font-size: .95rem; color: var(--ink-2); cursor: pointer }
.cp .opts input { position: absolute; inset: 0; opacity: 0; margin: 0; width: 100%; height: 100%; cursor: pointer }
.cp .opts label:has(input:checked) { background: var(--accent); border-color: var(--accent); color: var(--accent-ink) }
.cp .opts label:has(input:focus-visible) { outline: 3px solid var(--accent); outline-offset: 2px }
.cp .pp { display: none; grid-template-columns: 1fr 1fr; gap: 0; border-top: 1px solid var(--line) }
.cp .pp > div { padding: 14px 18px 2px 0; display: grid; gap: 4px; align-content: start }
.cp .pp > div + div { padding-left: 18px; border-left: 1px solid var(--line) }
.cp .pp .one { grid-column: 1 / -1 }
.cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }
@supports not selector(:has(*)) { .cp .pp { display: grid; margin-top: 8px } }
@media (max-width: 640px) { .cp .pp { grid-template-columns: 1fr } .cp .pp > div + div { padding-left: 0; border-left: 0; border-top: 1px solid var(--line) } }

/* first week */
.week { list-style: none; margin: 34px 0 0; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0 }
.week li { position: relative; padding: 26px 18px 0 0; border-top: 2px solid var(--line); display: grid; gap: 6px; align-content: start }
.week li::before { content: ""; position: absolute; top: -8px; left: 0; width: 14px; height: 14px; border-radius: 4px; background: var(--heat-mark) }
.week li:nth-child(n+3)::before { background: var(--bg); border: 2px solid var(--heat-mark) }
.week p { font-size: .95rem; color: var(--ink-2) }
@media (max-width: 860px) { .week { grid-template-columns: 1fr; margin-left: 7px } .week li { border-top: 0; border-left: 2px solid var(--line); padding: 0 0 22px 22px } .week li::before { top: 2px; left: -8px } }
```

The story's script. It reads one shared constant, the reduced-motion media
query, declared once at the top of the page script:

```js
(() => {
  const viz = document.getElementById("viz"), steps = [...document.querySelectorAll("#steps .st")];
  const set = n => {
    for (let i = 1; i <= 5; i++) viz.classList.toggle("s" + i, i <= n);
    steps.forEach(s => s.classList.toggle("on", +s.dataset.step === n));
  };
  if (reduced.matches || !("IntersectionObserver" in window)) { set(5); steps.forEach(s => s.classList.remove("on")); return; }
  const vis = new Set();
  const io = new IntersectionObserver(es => {
    es.forEach(e => e.isIntersecting ? vis.add(+e.target.dataset.step) : vis.delete(+e.target.dataset.step));
    if (vis.size) set(Math.max(...vis));
    else if (steps[0].getBoundingClientRect().top > innerHeight * .5) set(0);
  }, { rootMargin: matchMedia("(max-width: 900px)").matches ? "-56% 0px -22% 0px" : "-42% 0px -42% 0px" });
  steps.forEach(s => io.observe(s));
})();
```

The rest of the page script is the base's, with three additions: after wiring
the tabs it selects the tab marked selected, which hides the other panels; the
tab keys gain Home and End; and one observer adds the class `in` to each
reveal element the first time it intersects (root margin 0 0 -8% 0), or to all
of them at once where the observer is missing. Observers only; no scroll
listener.

## 10. Fallbacks, floors and acceptance

| condition | what the visitor gets |
|---|---|
| no script | every section visible; the finished chart beside an ordinary list of five steps, not pinned on a phone; all four gallery panels; the chooser still works; no tab list, no theme button |
| reduced motion | no animation or transition anywhere; the finished chart, pinned, beside a compact list with no step marked current; no progress line; reveals already at rest |
| no scroll-driven animation | no progress line; nothing else changes |
| no relational selector | all four control-path answers shown, named |
| no intersection observer | the finished chart; all reveals at rest |

Accessibility floors: body text at least 4.5 to 1 against its background in
both themes (the two ember words of the page title are large text and meet 3
to 1, unchanged from the base); the chart is one image to assistive technology,
with the sentence given in its label, and its inner drawings are hidden; the
story is an ordered list whose content does not depend on the chart; step
numbers are decorative and hidden; every control is reachable and operable by
keyboard with a visible ring; targets are at least 40 px; no horizontal scroll
at 360, 390, 768 and 1440 px; the page reads in order with styles off.

Acceptance, each runnable by the reviewer at the head:

1. `tests/doc_claims.py` is green, and its product-page section reports more
   claims than at the base.
2. The generator's check mode exits zero; after changing one price in the
   preset it exits non-zero and names a layer (the perturbation), and reverting
   restores zero (the null control). The new pin in `check_product_page` goes
   red on the same change: that line is the mutation target.
3. The generator's self-test passes.
4. Links: `grep -o 'href="[^"#][^"]*"' docs/index.html | sort -u` gives the
   same lines at the base and at the head.
5. Anchors: each of the ten ids of section 2 appears exactly once.
6. Nothing embedded: no `data:` address in the page, and its size stays under
   70 kB (the base is 45 kB; the design adds about 15).
7. Sentences: every text node under a source mark at the base is still on the
   page at the head, except the alternative text of the removed how-it-works
   picture. The harness prints the difference; it must be that one line.
8. In a browser, by the harness, at 360, 390, 768 and 1440 px in both themes:
   scroll width equals window width; no console message; no request other than
   the page, its four fonts and its images.
9. The story: scrolling step n to mid-viewport gives the chart card exactly the
   classes for layers 1 to n, for n from 1 to 5, and back up again.
10. With script disabled, and separately with reduced motion requested, the
    table above holds: all layers have opacity 1, no element has a running
    animation, and all four gallery panels are displayed in the first case.
11. The chooser: checking each radio displays exactly its own pane.

What the prototypes did not establish, and the fixer's browser run should:
only one browser engine was run; no screen reader was run; touch was emulated.

## 11. Alternatives, and why they lost

- **Draw the chart at load, in script.** The page would then show nothing of
  the story without script, and the page test, which reads the file, could not
  see what a visitor sees. Committed SVG costs about 6 kB and is checked.
- **Ship the chart as an image under the docs images.** One file per theme and
  no layers: the story would need five images per theme, or would lose its
  build-up. Inline SVG takes the page's own colour tokens in both themes.
- **Keep the control-path table and add the chooser above it.** The same
  twelve cells twice. The fallback and print already show every answer.
- **A separate stylesheet and script file under the site folder.** The page is
  one file by its design of record, and `tests/doc_claims.py` reads claims,
  styles and requests from that one file; splitting it changes what the test
  must open for no gain at this size.

## 12. Sibling sites

`git grep -n 'index.html' -- tools/site tests .github` lists every reader of
the page. None needs a change: the sub-page builder links the page and its
install anchor only; `tests/entities.py` stages the page by name without
reading its content; the README's own hero picture and how-it-works picture are
pinned in the README, not on the page.

## Notes for the fixer

- The page parser in `tests/doc_claims.py` treats an element as closed only by
  its end tag unless the tag is in its void list. Write the chart's `line`
  elements self-closed, as the generator does, or text after them is attributed
  to the wrong owner.
- The hour axis under the chart is digits outside any claim unless it carries
  the copy mark; the markup above has it.
- `tests/closure.py` lists the sized PNGs the page test opens. The how-it-works
  PNG leaves this page but stays on a published sub-page; confirm before
  touching that list.
- The prototype named its illustrative chart box with the same class the base
  gives the hero screenshot's stage. The screenshot's stage loses that class
  when it moves; its dark backdrop rule is re-keyed to its new place.
- A new tracked file is classified deliberately or `tests/entities.py` fails.
- `tests/structure.py` measures the tree; measure it before and after, and pay
  any growth by keeping the pin to one call.
