The Setup tab is redrawn in the product's own design identity, and the owner's
acceptance list is answered item by item. Folds ARCH2-s5 C1 and C4, and the
hot_water_pumps label drift. Part of #2254, part of #2238, part of #2222 (the roster's `fixes` is empty for this group, so the orchestrator closes them after verifying each).

What the owner's screenshot named, and what closes it:

- **Sketchy hand-drawn boxes and wobbly double borders.** The v4.3.0
  `NODE_SHAPES` vocabulary (cloud, gabled house, domed cylinder, fan shroud,
  bowtie) is deleted: a box is now ONE flat card painted by CSS on the very
  rect that was already the geometry carrier the drag editor reads — the
  product's surface, border and radius. Two outlines per box became one, and
  the card is opaque, so a pipe routed behind it is covered by it.
- **Truncated labels.** `fitSlotRow` wraps instead of ellipsizing: the value
  keeps the first line's right end, the label takes what is left of it and the
  whole width of the next, and a box is as tall as the lines it actually
  draws.
- **"not configured" rows in the reading's weight.** A box's unset inputs fold
  into ONE muted line — "N optional inputs not set" — with a Configure chip
  beside it. The line is itself the disclosure that opens that box's rows in
  place, so per-slot assignment is not lost by the fold, and the chip is a
  deep link out to the options page that owns those inputs.
- **Pipes crossing boxes and labels.** A pipe endpoint now stops ON a card's
  border (the per-place insets went with the shapes), the cards are opaque,
  and the valve's bowtie — whose apex merged with the edge of "Valve outlet
  temperature" — is gone.
- **Inconsistent decimals.** One precision per unit: Home Assistant formats
  each entity at the precision that entity sets for itself, so the diagram
  carried 19.30 °C beside 20.8 °C. A unit the table does not name keeps Home
  Assistant's own spelling.
- **Unstyled topology chips.** The layout bar's buttons and the tank toggles
  now share the legend chips' rule — one rule, two surfaces — so they cannot
  drift into unstyled boxes beside them.
- **Phone width and both themes.** The canvas already scrolled sideways under
  600 px (#40 item 1), which is what keeps a 12-unit row a tappable row; the
  drawing no longer relies on that alone, because nothing is cut to fit. The
  muted text inside a card takes its ink from the same darkMode switch as the
  card's own surface, so a dark theme that reports `darkMode: false` no longer
  paints dark grey on the light literal (measured at 2.63:1 before that rule).

**One fixture moved, and it is not a value.** The `hot_water_pumps` label is
captured verbatim in `tests/golden/config_flow.json` (float-free, compared
exactly), so the re-record is one line:
`PYTHONPATH=tests/hastub python3 tests/golden.py --record --only config_flow`
-> `1 file changed, 1 insertion(+), 1 deletion(-)`, the label alone. Nothing
about the card is in that fixture and no solver float is involved, so the
re-record is honest on this machine (the gate's own staleness report says so).

**Method.** The Setup page is one seam: `setupSvgHtml` and its stylesheet, the
`SetupPage` controls that drive it, and the strings and constants they read.
The three folds land in the same seam or beside it: C1 and C4 are the card's
own text-width and empty-state owners, and the label is one table entry in
`config_flow.py`.

## Head

`959a011f0` (measured at this commit; every figure below is from this tree).

## Mutation proof

`python3 /private/tmp/r10-ux-setup/mutants.py` (each mutant is an exact
production-line replacement, restored with `git checkout --` between runs; the
closure is `node tests/card.mjs`, 9 runs, recorded in
`/private/tmp/r10-ux-setup/mutants.log`):

| mutant | production line | checks that went red |
|---|---|---|
| M0 | none (null control) | 0 -- the tree passes unmutated |
| M1 | `fitSlotRow` returns one ellipsized line again | `a slot label is drawn whole, wrapped rather than cut`; `and the label is never cut either, at any real length`; `a label that fits is left exactly alone`; `the six cases really are six different slopes` |
| M2 | an unset slot becomes an ordinary row again | 10 checks, including `an unset input folds into its box's one muted line, not a row`; `every slot is reachable from the diagram: a row, or inside a folded block`; `every configured slot is matched with its own hit rect`; `the census reached every navigateTo and openHaLink call site` |
| M3 | `.setup-box` left invisible (`fill: none`) | `the card is painted from the product's surface, border and radius` |
| M4 | `onePrecision` returns Home Assistant's string unchanged | `two temperatures on one drawing are spelled to one precision` |
| M5 | the axis counts characters instead of measuring its label (C1 reverted) | `the chart's label-width rule is spelled in exactly one place` |
| M6 | the no-plan empty state spelled a second time (C4 reverted) | `the no-plan empty state is built in exactly one place` |
| M7 | the finite-number test spelled a second time (C4 reverted) | `the finite-number test is spelled in exactly one place` |
| M8 | an OPEN folded block's height counted as the folded one | `a block that is open sizes its box for the rows it now draws` |

M8 is the bug the P9 grid found at a narrow width before the fix: the height
pass counted the folded block only while it was folded, so a box that had just
been opened drew its last caption past its own card.

## Null control

- **The unmutated tree passes**: M0 above, `node tests/card.mjs` ->
  `ALL CARD CHECKS PASSED`.
- **The census harness is stable**: the two card censuses run twice on the
  same file report identical counts (the harness documents this as its own
  null control, `dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs`).
- **The finder's harness reproduces the finding at the baseline**, not only at
  the head: `wizard_widgets.py` prints
  `advanced.hot_water_pumps: code 'Circulation pumps' vs en.json 'Hot water
  circulation'` at the merge base and `menu_disagree=0` at this head, with
  `menu_fallbacks=23` at both ends -- the comparison executes either way.
- **The drift claims are controlled**: of the 39 states `card_drift.mjs`
  reports moved, the differing region of 33 lies entirely inside the
  `<style>` block (shared prefix and suffix of the two dumped `html` strings
  against the block's own offsets); the other six render the Setup page or its
  layout editor. `editor_schema` stays byte-identical.
- **The docs figures are controlled**: `node
  docs/img/card/make_card_figures.mjs` run on this tree and on the merge base
  produces byte-identical `chart-anatomy.svg` and `chart-dashed-lines.svg`, so
  this change moves no committed SVG figure -- and the same comparison on the
  page screenshots leaves twelve of the fourteen identical, naming the other
  two as this change's own.

## Figures

- `node tests/card.mjs` -> `ALL CARD CHECKS PASSED` (the closure for the card).
- `node tests/card_drift.mjs origin/main` -> `39 state(s) moved and claimed, 1
  identical`; the claims are in `tests/golden/card_claimed_drift.txt`, whose
  `claims-for:` is the live VERSION.
- `node tests/card_browser.mjs` -> 1 failing check, named under Red checks.
- `PYTHONPATH=tests/hastub python3
  /private/tmp/r10-ux-setup/export/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`
  (sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`) -> `menu_disagree` 1 at the
  merge base, 0 here; `menu_fallbacks` 23 at both.
- `node
  /private/tmp/r10-ux-setup/export/dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs
  <card>` (sha1 `677b75421ca84ac0f404dc90fa0b6a0b72edea0e`) -> at the merge base
  `total=31`, `char_width_inline=2`, `finite_inline=7`, `no_plan_state=2`,
  `dead=2` (`top:textWidth top:openHaLink`); here `total=24`,
  `char_width_inline=0`, `finite_inline=3`, `no_plan_state=1`, `dead=0`.
- `node
  dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs <card>` -> at the
  merge base `total=34` (`isfinite_lines=7`, `char_width_lines=3`,
  `no_plan_lines=4`); here `total=27` (`3`, `1`, `3`) -- the finder's own
  second arm for the same folds.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`, no row moved.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main` ->
  `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO
  STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- `HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs` -> the 14 page
  figures for `docs/dashboard-card.md`; two of them (`setup-light.png`,
  `setup-dark.png`) differ from a regeneration at the merge base and are
  committed here, and the other twelve come out byte-identical to that
  regeneration.
- `GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh` -> `MODE: SCOPED -- 16
  script(s) run, 17 scoped out`, every script green, `>> TESTS PASSED`.

## Red checks

`P9 grid: no two text runs share ink` -- `20: text "2" x text "3" 2 px of
shared ink`. This is main's own, on this machine: the same check fails with
the SAME pair and the same 2 px at the merge base, measured by running
`node tests/card_browser.mjs` in a detached worktree at `origin/main`
(`/private/tmp/r10-ux-setup/browser-base.log`, `1 BROWSER CHECK(S) FAILED`).
The cheaper detector is the gate that ran: the pair only exists once Chromium
has rastered the glyphs, and no earlier and cheaper instrument can see ink.
CI is authoritative for it; this lane's own header says the raster is not
bit-stable across Chromium builds.

`env_drift.py --all` -- this script turned the branch's first two local gate
runs red, both times because of the same one-line label and each time for a
different reason: first `1 COMMITTED FIXTURE(S) ARE STALE` (the committed
capture still held the old label), then `1 UNCLAIMED DRIFT(S) vs origin/main`
(the capture no longer matches main's, which is what the change is FOR). The
trigger's question is whether a cheaper detector could have caught either
earlier, and in both cases the cheapest detector that reaches the fact is the
one that caught it, inside the run that caught it: the staleness comparison
runs first in the script and costs seconds, where the half after it re-solves
56 scenarios; and "this branch moved a fixture main does not move" is a
statement about a comparison, so only the comparison can reach it. Nothing
cheaper exists to build -- which is why the answer is the two edits this
branch did (the re-record, then the claim), not a new check.

## Unpinned sites

`n/a: step 6d's ci_predict lists no unpinned mutation site this diff adds` -- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -> `no closures or fast red predicted`.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, group R10-ARCHSCORE-COVERAGE's
`brief`: the card's dead-definition row and clone census must be recorded at a
base that already carries these C1/C4 folds, and on this branch both rows were
absent from `tests/ci_budgets.json`, so the re-record lands with that group.
The carry names no literal, only the precondition and its control.

## Friction

`card_browser: unenforced: the twelve committed page figures under
docs/img/card regenerate differently on this machine at the merge base as
well, and no check compares a committed figure to what the card draws -- only
the two this change moves are committed here. The control is the regeneration
at the merge base: it rewrites all twelve, so the drift is the raster and not
this branch`.
