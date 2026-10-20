# Card setup page — box symbols and the configure affordance

Design pre-study, 2026-10-20. Local seat, refs only (`probe/card-symbols-design`).
Repository `tvofi/heatpump_optimizer`, measured at `origin/main`
`76bb45628` (worktree `peaceful-clarke-53d260`). The card, its topology and
the card tests are byte-identical to `0c298f6b5`; main's only change between
the two is `thermal_model.py`'s set-point gate, which does not touch the coil
predicate (re-measured below at this head).

## What is here

| file | concept |
|---|---|
| `index.html` | the five side by side (1280 light, 375 dark) and the comparison table |
| `proto-1-badge.html` | 1 · Badge — a type disc on the box's outer corner |
| `proto-2-pictogram.html` | 2 · Pictogram set — one pictogram inside the box |
| `proto-3-legend.html` | 3 · Legend strip — numbered keys and one type legend |
| `proto-4-outline.html` | 4 · Type-tinted outline — stroke, pattern and corner tab |
| `proto-5-inline.html` | 5 · Inline detail line — icon + word under the title |

Each prototype is one static, self-contained HTML file: no build, no network,
no Home Assistant. Both themes and all three wood-coil states are in every
file; the segmented controls at the top switch them. Open `index.html` from a
static server (`python3 -m http.server`) or directly; the index draws each
concept's own SVG inline (no screenshots, no iframes), and each caption links
to the full prototype.

The seven files are also committed on the ref `probe/card-symbols-design` at
`docs/design/card-symbols/` (branch `probe/card-symbols-design`, based on
`origin/main` `76bb45628`).

The prototypes reproduce the card's own design voice: `CARD_TOKENS` and
`CARD_SCALE_TOKENS` verbatim (light and dark), the 720-unit three-column
drawing, 200-unit cards with radius 10, the 16-unit padding, 13 px titles,
12 px rows, 11 px chip text, 1.5-unit pipes at 0.55 opacity with endpoint dots
and flow chevrons, and the dusk mark's rounded-stroke vocabulary. Geometry and
the pipe curves are ported from `setupSvgHtml`; label widths are measured with
the card's own `setupTextW`, not an approximation.

## Measurement 1 — the box inventory

Command (run from the worktree root):

```python3
python3 - <<'PY'
import re
src = open("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js").read()
body = src[src.index("function setupSvgHtml"):src.index("\n// ---- The token layer")]
places = [re.findall(r'"([a-z_]+)"', m.group(1))[0]
          for m in re.finditer(r'box\(\s*\d+,[\s\S]{0,220}?\[((?:"[a-z_]+",?\s*)+)\]', body)]
keys = set(re.findall(r'"setup\.box_[a-z0-9_]+"', src))
print("box() calls:", len(places))
print("places:", ", ".join(places))
print("box_* string keys:", len(keys), "| title keys (less the two aria labels):", len(keys) - 2)
print("CSS rules naming .setup-box:", len(re.findall(r"\.setup-box[ ,{]", src)))
PY
```

Output:

```
box() calls: 8
places: outdoor, heat_pump, wood_tank, mixing_valve, buffer_tank, dhw_tank, upper_zone, lower_zone
box_* string keys: 13 | title keys (less the two aria labels): 11
CSS rules naming .setup-box: 2
```

So: **8 drawable boxes, 11 title strings, one visual style.** The two CSS
rules are `.setup-box` and `.setup-svg.editing .setup-box` (the editor cursor);
neither varies by type. Nothing but the title distinguishes one box from
another today.

| box | place | drawn when | title (varies with layout) |
|---|---|---|---|
| Outside | `outdoor` | always | Outside |
| Heat pump | `heat_pump` | always | Heat pump |
| Wood furnace tank | `wood_tank` | `topo.wood.present` (`wood_furnace_on`) | Wood furnace tank (N L) |
| Mixing valve | `mixing_valve` | `valve_mode` is a throttling mode (manual / smart_read / smart_write) | Mixing valve (mode) / 4-way mixing valve (mode) |
| Buffer tank | `buffer_tank` | always | Buffer tank (N L) / Heat pump tank (N L) |
| Hot water tank | `dhw_tank` | `topo.dhw` | Hot water tank |
| Upper floor / House | `upper_zone` | always | House / Upper floor |
| Lower floor (slab) | `lower_zone` | `topo.two_zone` | Lower floor (slab) |

Four are always drawn, four conditional; the measured fixture draws all
eight. The three names that switch are why 11 title strings cover 8 boxes.
`floor_loop` is a slot place folded into the lower-floor box, not a box of its
own; `slab_shunt` has no box on any modelled layout.

What a reader cannot tell apart today: the three stores (heat-pump/buffer
tank, wood tank, hot water tank) are the same rectangle with the same title
weight; the heat pump and the valve are the same rectangle; the two floors are
the same rectangle. Title text is the only carrier.

## Measurement 2 — what the tree means by a wood coil

It is an **immersed hot-water coil in the wood furnace tank**: mains water on
its way to the hot-water tank is preheated by the wood tank's stored heat. It
is not a heating coil and not a coil on the heat pump.

The predicate is `ThermalParameters.dhw_coil_active`
(`custom_components/heatpump_optimizer/thermal_model.py:311`):

```
dhw_wood_coil_enabled  AND  dhw_enabled  AND  two_tank_modelled
```

and `two_tank_modelled` (`thermal_model.py:376`) is
`topology_layout == "two_tank_4way"`. The layout is derived
(`thermal_model.py:343`) as two_tank_4way only when a **throttling mixing
valve**, **two zones** and a **wood-tank probe entity** are all configured; a
stored layout override is accepted only if `topology_layout_valid`
(`const.py:405`) says the same three conditions hold.

Command (the seat's `python3`, from the worktree root):

```python3
PYTHONPATH=tests/hastub python3 - <<'PY'
import sys; sys.path.insert(0, ".")
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters
from custom_components.heatpump_optimizer.const import *
base = {CONF_DHW_ENABLED: True, CONF_WOOD_FURNACE_ENABLED: True,
        CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
        CONF_MIXING_VALVE_MODE: "manual", CONF_TWO_ZONE_MODE: "on",
        CONF_DHW_WOOD_COIL_ENABLED: True}
def show(tag, c):
    p = ThermalParameters.from_config(c)
    print(f"{tag:24} layout={p.topology_layout:20} two_tank={p.two_tank_modelled} coil={p.dhw_coil_active}")
show("all five", base)
for drop in ["probe", "zone", "valve", "coil", "dhw"]:
    c = dict(base)
    if drop == "probe": c.pop(CONF_WOOD_TANK_TOP_ENTITY)
    if drop == "zone":  c[CONF_TWO_ZONE_MODE] = "off"
    if drop == "valve": c[CONF_MIXING_VALVE_MODE] = "none"
    if drop == "coil":  c[CONF_DHW_WOOD_COIL_ENABLED] = False
    if drop == "dhw":   c[CONF_DHW_ENABLED] = False
    show("without " + drop, c)
PY
```

Output:

```
all five                 layout=two_tank_4way        two_tank=True  coil=True
without probe            layout=single_tank_valve    two_tank=False coil=False
without zone             layout=single_tank_valve    two_tank=False coil=False
without valve            layout=no_valve             two_tank=False coil=False
without coil             layout=two_tank_4way        two_tank=True  coil=False
without dhw              layout=two_tank_4way        two_tank=True  coil=False
```

So the configuration that produces a drawn wood coil is: **wood furnace on +
a wood-tank probe + a throttling valve + two zones + hot water + the
“DHW wood coil” option**. The option's shipped default is `False`
(`const.py:365`, `DEFAULT_DHW_WOOD_COIL_ENABLED`).

### What the schematic draws for it today

Rendered with the card's own renderer (`tests/setup_qa_render.mjs`, the
`coil` topology in `tests/card_rig.mjs:519`):

```
node tests/setup_qa_render.mjs /tmp/plandata-<hash>.json
```

The coil page draws exactly two things beyond the two-tank layout:

1. the edge `wood_tank>dhw_tank`, in `class="setup-pipe"` — the same class,
   stroke width, colour and opacity as every heating pipe;
2. one muted caption on the hot-water tank: `refilled through a wood tank
   coil` (`setup-slot extra`, 12 px secondary ink).

The wood tank itself carries nothing. There is no coil glyph: the re-design
removed it, and the code says so at
`heatpump_optimizer-card.js:2380-2381` — “`.setup-contour`, `.setup-accent`
silhouettes and `.setup-coil` are gone with the vocabulary that drew them”.
The comment above the pipe says the same: “The coil helix that used to mark
the wood tank's wall is gone … the coil is carried by its own pipe and by the
caption on the tank being preheated.”

### Why it reads ambiguously

1. **The coil's only drawing is an ordinary pipe.** Same class, stroke, colour
   and opacity as every hydronic pipe. Nothing says this one carries potable
   water rather than heating water.
2. **The caption is on the wrong box.** It sits on the hot-water tank; the
   wood tank — the thing with the coil in it — has no mark at all.
3. **It is one caption away from invisible.** The two lines are muted 12 px
   rows among many; on a phone they scale to ~9 px.
4. **Configured-but-inactive is silent.** Set the coil option with no probe, no
   valve or one zone and `dhw_coil_active` is false: no pipe, no caption, and
   nothing says the option the owner just switched on does nothing. The
   measured table above is exactly that case.
5. **“Coil” appears nowhere on the wood tank**, so a reader looking for “a wood
   coil” has no anchor.
6. **The documentation promises a coil the page no longer draws.**
   `docs/dashboard-card.md:709` — “the coil is drawn as a visible spring on the
   tank's upper-right wall with its own connector stubs”; the checked-in figure
   `docs/img/model/hydronic-coil.svg` still carries a `class="setup-coil"`
   element (`grep -c setup-coil docs/img/model/hydronic-coil.svg` → 2) and the
   line-art silhouettes (`grep -c setup-contour` → 3), while the card's
   stylesheet has neither. The same paragraph still describes every box as “a
   thin line-art contour — the house with its gable roof and chimney …”, which
   the card redesign replaced with cards. That is a documentation/figure drift
   worth its own fix and is **not** changed here.

### The design's answer, held across all five prototypes

- The hot-water box always states the coil in words, in all three states:
  *active* “refilled through a wood tank coil / preheats the mains water”;
  *configured, not modelled* “coil configured, not modelled / needs 2 zones,
  valve, probe”; *none* “no hot-water coil / wood heat only”.
- The coil pipe is the one **accent** pipe in every concept, and dashed when
  configured-but-not-modelled — so the path stops reading as heating water.
- Each concept carries the coil on the wood tank itself in its own mechanism
  (a spring disc, a spring inside the tank pictogram, key 6, a spring on the
  tank's border, the word `COIL`).

## Measurement 3 — the configure affordance

The page's controls, their handlers and where they go. The page cannot be
driven through a real Home Assistant here; the card is driven in the repository
rig (`tests/card_rig.mjs`) with the plan payload and a registry stub, and the
navigation the card performs is recorded.

The control that leaves the card is
`.setup-chip-hit[data-configure]`; its handler
(`heatpump_optimizer-card.js:12305-12309`) calls
`openHaLink(this.host, "options", null)` for **every** box — it ignores its own
`data-configure` place. `openHaLink` (`:8876`) resolves the entry id from the
entity registry and `haLink` (`:8861`) builds
`/config/integrations/integration/heatpump_optimizer#config_entry=<id>`.

Driver (the whole file; run from the worktree root with `node`):

```js
import fs from "fs";
import { CARD_PATH, DEFAULT_SPACE, makeCardContext, loadCard, planStates, qaTopologies }
  from "./tests/card_rig.mjs";
const plan = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const { ctx } = makeCardContext();
const Card = loadCard(ctx, fs.readFileSync(CARD_PATH, "utf8"));
const { coil } = qaTopologies();
const ENTRY = "abc123entry";
const states = () => { const s = planStates(plan);
  s[DEFAULT_SPACE].attributes.setup_topology = JSON.parse(JSON.stringify(coil)); return s; };
const callWS = async (msg) =>
  msg.type === "config/entity_registry/get" && msg.entity_id in states()
    ? { entity_id: msg.entity_id, config_entry_id: ENTRY } : (() => { throw new Error("no"); })();
const c = new Card();
c.setConfig({ type: "custom:heatpump-optimizer-card" });
c.hass = { states: states(), callService: async () => {}, callWS };
c._onCardClick({}); c.dialog.page = "setup"; c._render();
const pushed = []; ctx.history = { pushState: (_a, _b, p) => pushed.push(p) };
const seen = []; const walk = (n) => { if (n._listeners && (n._listeners.click || []).length) seen.push(n);
  (n.children || []).forEach(walk); }; walk(c.shadowRoot);
const out = [];
for (const el of seen) {
  const place = (el.dataset || {}).configure;
  if (place === undefined) continue;
  pushed.length = 0;
  for (const f of el._listeners.click) await f({ currentTarget: el, stopPropagation() {}, preventDefault() {} });
  await new Promise((r) => setTimeout(r, 0));
  out.push({ place, aria: el.getAttribute("aria-label"), dest: pushed.slice() });
}
console.log(JSON.stringify(out, null, 1));
```

Measured output (the `coil` fixture, which has unset slots on five boxes):

```
[
 { "place": "heat_pump",   "aria": "Configure: Heat pump telemetry",              "dest": ["/config/integrations/integration/heatpump_optimizer#config_entry=abc123entry"] },
 { "place": "wood_tank",   "aria": "Configure: Heating system and heat storage",  "dest": ["/config/integrations/integration/heatpump_optimizer#config_entry=abc123entry"] },
 { "place": "mixing_valve","aria": "Configure: Heating system and heat storage",  "dest": ["/config/integrations/integration/heatpump_optimizer#config_entry=abc123entry"] },
 { "place": "dhw_tank",    "aria": "Configure: Hot water tank and inlet",         "dest": ["/config/integrations/integration/heatpump_optimizer#config_entry=abc123entry"] },
 { "place": "lower_zone",  "aria": "Configure: Sensors and entities",             "dest": ["/config/integrations/integration/heatpump_optimizer#config_entry=abc123entry"] }
]
```

Four different page names, one destination. The mapping itself is right and is
pinned against `translations/en.json` by `tests/card.mjs:3109` (“the Configure
chip names the options page the flow itself names”); the wrongness is that the
page identity exists only in the aria-label and never reaches the navigation.

### Control table

Paths are relative to Home Assistant: **Settings › Devices & services ›
Heatpump Optimizer › Configure › Advanced settings ›** — every page in
`SETUP_CONFIGURE_PAGE` (`card.js:2438`) is an `_ADVANCED` entry in
`_OPTION_PAGES` (`config_flow.py:1537`).

| control (element, handler) | place(s) | today | correct destination | whose defect |
|---|---|---|---|---|
| Configure chip `.setup-chip-hit[data-configure]` → `openHaLink("options")`, `card.js:12305` | outdoor, upper_zone, lower_zone | `/config/integrations/integration/heatpump_optimizer#config_entry=<id>` (entry highlighted) | … › Advanced settings › **Sensors and entities** | card: label/destination gap. R10-DEEPLINK moved it from the integration list to the entry; R10-UX-SETUP gave each box a page name. **Not #2452** (see below). |
| same | heat_pump | same | … › Advanced settings › **Heat pump telemetry** | same |
| same | buffer_tank, mixing_valve, wood_tank | same | … › Advanced settings › **Heating system and heat storage** | same |
| same | dhw_tank | same | … › Advanced settings › **Hot water tank and inlet** | same |
| Slot row `.setup-hit[data-key]` → `openPicker` → `assign_entity` | every assigned/unset slot | in-card picker; no page opens | in-card picker — correct | none |
| Fold line `.setup-fold-hit[data-fold]` → toggle | boxes with unset slots | opens the box's unset rows in place | in place — correct | none |
| Tank toggles `[data-tank]` → `persistTanks` → `apply_topology`, `card.js:12271` | DHW tank, Wood tank | writes the config in place | in place — correct, but the button does not say it writes | labelling only |
| Layout editor toggle / Save → `apply_topology`, `card.js:13393` | the drawing | in place | in place — correct | none |
| Advisor / Health “settings · diagnostics” (`act === "settings"`) | — | `navigateTo(SETTINGS_PATH)` | the integration entry — correct for that row's promise | none |

Two facts the table cannot show:

- the chip is drawn **only for a box with at least one unset slot** (the fold's
  Configure line is emitted inside the `if (b.unsetRows.length)` block), so a
  fully configured box — the buffer tank, the upper floor — has no route to its
  page at all;
- Home Assistant's frontend has **no URL route into an options-flow step**; the
  card's own comment (`card.js:2429-2433`) records this and the frontend
  version it was checked against. A card can open the integration page with the
  entry highlighted and no more. That is why the prototypes fix the *promise*
  (the button names its page; a page caption states the path) rather than
  inventing a second deep-link mechanism.

### PR #2452 is not this defect

`gh pr diff 2452 --name-only`:

```
dev/programme/delivery/2452.md
dev/programme/rosters/wave-r10-groups.json
tests/card.mjs
tools/audit/seat/r10_deeplink_mutants.py
```

R10-DEEPLINK-HANDLERS changes **no card file**; its own body says “The card is
unchanged”. It hardens the link census so a navigation written in an undriven
handler or appended outside the shadow root is refused. It neither causes nor
fixes the configure destination. Where this design meets it: the prototypes add
no navigation and no deep-link mechanism, keep `openHaLink("options")` as the
only route, and if a later PR changes the chip's handler the census will drive
it (every `addEventListener` site must be driven) — the aria/label change must
keep passing the translations pin at `tests/card.mjs:3109`.

## The five concepts, one line each

1. **Badge** — a 16-unit type disc on each box's outer corner; the wood tank's
   disc is a spring, and the coil pipe is the one accent pipe.
2. **Pictogram set** — a 14-unit pictogram above the title inside each box; the
   wood tank's is the cylinder-with-spring the re-design removed, restored.
3. **Legend strip** — no glyphs on the boxes, only numbered keys decoded by one
   six-entry type legend above the drawing (key 6 is the coil).
4. **Type-tinted outline** — the box outline itself carries the type (weight +
   pattern + corner tab), and the coil is a spring drawn on the wood tank's own
   border with its pipe the only dashed accent pipe.
5. **Inline detail line** — one icon-and-word line under the title
   (`STORE · WOOD · COIL`) and a `coil` label on the pipe: the lightest-touch
   option and the only one that needs no symbol literacy.

## What was verified on the rendered files

Checked in Chromium from the served directory (the preview pane), on the
rendered HTML, not asserted:

| check | 375 px | 768 px | 1280 px |
|---|---|---|---|
| document horizontal overflow | none (375 = 375) | none | none |
| the drawing's scroll | 560 px in a 321 px canvas (as the card ships) | fits (702) | fits (1146) |
| box titles past their box | none | none | none |
| drawn hit targets | 44 px (coarse) | 24 px (fine) | 24 px (fine) |
| visible coil state | exactly one of three | one | one |

Contrast, computed on the rendered colours (light / dark): title and rows
15.3 / 11.1; secondary text 4.6 / 5.2; chip label 5.8 / 7.3; type glyphs
5.5 / 6.2 (graphics). All text pairs clear AA 4.5:1; `--hpo-heat` is used only
as a graphic at 3.7:1, never as text. Every glyph is `aria-hidden`; every box
is a `role="group"` named with its type and coil state; every control is a
button with a focus ring.

## Decisions for the owner

1. Which concept (the index compares them).
2. The hot-water box always stating the coil state in words — a propose-yes;
   it makes "configured but not modelled" visible, at two rows on one box.
3. The configure control becoming a visible two-line button naming its page,
   versus today's one-line chip — it adds ~13 units to each chipped box and is
   the reason the prototypes' drawings are taller than the shipped one.
4. The docs/figure drift in `docs/dashboard-card.md` and `docs/img/model/`
   (they still show the coil spring and the line-art silhouettes) is a real
   finding outside this seat's scope; it needs its own fix.
