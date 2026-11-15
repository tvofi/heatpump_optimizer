# D4 acceptance criteria: the card and the config flow

> UI/UX — the card and the config flow, including grouping and setup
> ergonomics. It should be intuitive, user friendly and look professional.

— the owner, `D4.md`. Each statement below quotes the words it tests.

Drafted by a fixer seat under mandate 6893738184 (scope all);
binding as the owner's words until the owner rewrites them.
A finding names the statement it fails.

Surfaces: every state `node tests/card_drift.mjs --list` prints, at the
viewports, themes, languages and input modes `D4.md` step 1 names; every
config-flow and options page; every input of every `blueprints/` file.

## "look professional"

- **P1 no collision.** Overlap of two text boxes, and text past its own box,
  measured with `getBoundingClientRect`. Pass: 0 px in every surface. Fail:
  more than 0.5 px anywhere.
- **P2 contrast.** WCAG 2.2 AA from `getComputedStyle` colours: 4.5:1 for
  body text, 3:1 for text at 24 px or 18.66 px bold and for chart marks.
  Fail: one pair below its ratio.
- **P3 one look.** A series keeps one colour across states within a theme;
  headline numbers in one row share font size and baseline (±0.5 px). Fail:
  either differs between two states or two cells.
- **P4 clean console.** Fail: any console error or uncaught exception.

## "user friendly"

- **F1 hit targets.** Every interactive element is at least 24×24 px, 44×44
  px under the coarse pointer. Fail: one smaller.
- **F2 keyboard.** Tab reaches every focusable in visual order with a
  visible focus ring. Fail: one unreachable, out of order or unmarked.
- **F3 errors say what to change.** Every validation error key has a string
  in every `translations/*.json`, naming the field and an accepted value or
  range. Fail: a missing key, or a string that names neither.
- **F4 help for every term.** Every field whose label holds a unit, an
  acronym or a physics term carries a `data_description` in every language.
  Fail: one without.

## "intuitive"

- **I1 one theme per page.** A page's fields answer the question its title
  asks; related fields sit adjacent or in one section. Fail: a field another
  page's title claims, or a related pair split by an unrelated field.
- **I2 answerable defaults.** On the shortest path from adding the
  integration to the first plan, every required field has a default or is an
  entity or area picker. Fail: a required free value with neither. The
  finding states the path's page count as a measurement.
- **I3 blueprint inputs.** Every input has a name and a description, and a
  default where one is safe. Fail: one without.
