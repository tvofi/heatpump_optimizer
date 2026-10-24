# Design pre-study — setup-page box symbols and the configure affordance (5 prototypes)

Role: **design pre-study seat**. Repository `tvofi/heatpump_optimizer`. LOCAL seat, refs only, no cloud.

## The ask (owner, tvofi, 2026-10-20)

> The card setup page has since the re-design no way of indicating clearly when a wood coil is used. Suggestion: add
> a small symbol for this, and identify the existing box types with symbols as well. Also, the configure buttons do
> not yet lead to the right config pages. Do a design pre-study preparing 5 prototypes in the integration's design
> voice for me to choose from.

So: two things designed together, and **five genuinely different prototypes**, not five colour variations.

## What exists (read it, do not guess)

- The card: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` — a plant schematic built from named
  boxes (`box_heat_pump`, `box_hp_tank`, `box_wood_tank`, `box_mixing_valve`, `box_lower_floor`, `box_upper_floor`,
  `box_outside`, `box_house` and the `boxes`/`boxesOut` collections around them). Take its own design voice from that
  file: its CSS tokens for colour, type and spacing, its light and dark treatment, its radii and stroke styles. The
  prototypes must look like they belong in this card, not like a generic dashboard.
- The setup path: `custom_components/heatpump_optimizer/quick_setup.py` and the config/options flow in
  `custom_components/heatpump_optimizer/config_flow.py` (the wood fields are `wood_furnace`, `wood_buffer_tank`;
  the other axes are `dhw_tank`, `buffer_tank`, `two_zone`).
- The rendering rig the tests use: `tests/card_rig.mjs` (`buildCard`, `planStates`), `tests/card.mjs`,
  `tests/card_drift.mjs` (`STATES`), and the docs page `docs/dashboard-card.md`.
- The deep-link work already in flight: PR #2452 (roster group R10-DEEPLINK-HANDLERS) is about the card's deep-link
  handlers; read its diff and say in your report where your design meets it — do not design a second deep-link
  mechanism. If the configure buttons' wrong destinations are #2452's defect, say that plainly and design only the
  affordance, not the routing.

## What to establish first (measured, not assumed)

1. **The box inventory**: every box the schematic can draw, the config condition that makes each one appear, and
   which of them a user currently cannot tell apart from another. Derive the count, do not carry one.
2. **The wood-coil case**: what the tree actually means by a wood coil — read the model and the flow, and state which
   config combination produces it, and what the schematic draws for it today (and why it reads as ambiguous).
3. **The configure affordance today**: every configure button/control in the card, its current destination, the
   correct destination (which config entry page or options step), and whether the wrongness is a routing bug
   (#2452's), a labelling issue, or missing affordance. Name each with the element and its handler.

## The five prototypes

Five distinct concepts for the same surface — the setup page's plant schematic and its box identification — each
rendered as a **self-contained, static HTML file** (no build, no network, no Home Assistant) that reproduces the
card's tokens faithfully in both light and dark, and holds up at 375, 768 and 1280 px. Each prototype must show:

- the symbols/identifiers in place on the boxes, including the wood-coil indicator, with the box-type system extended
  consistently to the other boxes;
- the configure affordance as you would ship it, with the destination each control is meant to reach written in the
  prototype's own caption.

Concepts to cover (you may adjust, but deliver five that differ in *mechanism*, and say what each costs and risks):

1. **Badge** — a small glyph attached to the box that carries the type (coil, tank, valve, furnace), in the card's own
   stroke language.
2. **Pictogram set** — every box type gets a small pictogram inside the box outline; wood coil is one of the set.
3. **Legend strip** — a compact legend/type row beneath or beside the schematic, with the boxes keyed to it.
4. **Type-tinted outline** — the box's own outline weight/pattern/colour-coded corner encodes the type, with a key.
5. **Inline detail line** — the box gains a one-line type label inside it (icon + word), the lightest-touch option.

Each prototype file is `proto-<n>-<concept>.html` and there is one **`index.html`** that shows all five side by side
with a short comparison (mechanism, cost, risk, how it reads at 375 px, what it does for the wood-coil ambiguity, and
how the configure affordance behaves). The owner chooses from the index.

Accessibility is part of the design, not a note: contrast AA for every text/background pair, hit targets at least 24 px
(44 px on a coarse pointer), the symbol never the only carrier of meaning (a label or an accessible name beside it).

## Deliver

- `/Users/timmalmstrom/hpo-seats/r10s3/card-symbols/` — the six HTML files plus `NOTES.md` (the three measurements
  above, each with the command that produced it).
- Push the whole directory: commit it in a worktree branched from `origin/main` and
  `git push origin HEAD:probe/card-symbols-design`. Refs only — no pull request, no GitHub write.
- Report: the ref SHA, the box inventory count and its derivation, what the tree means by a wood coil and why it is
  ambiguous today, the configure-button table (control → today → correct, and whose defect each is), and the five
  concepts in one line each.

The owner picks one; the orchestrator folds the choice into the roster. Do not build a site or a design system — five
prototypes of one surface, in this card's voice.
