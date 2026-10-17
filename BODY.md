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

`270f5d05e2841efab0bdf294db73d008439a7808` is the measured code head. It adds
one commit to `f97973cc760b126f4fc5507f2f9e24034f757c34` — the
`closures-autofix` bot's `ci: re-record closures` on top of the reviewed
`400df157` — and that one commit is the one-line census anchor described below.
`f97973cc` carries the orchestrator's merge of the authored code head
`18bd46db79da92e046a31d4a8d5c275a0bb64119` and origin/main `81b7aa9ff` into
this PR's previous head.

Every figure that reads a base is stamped with it: merge base
`81b7aa9ff976413ec98592045930647c0e0bac73`; origin/main tip at measurement
`1138a4ef590639fedfcc7642d0145bc7c6a4e137`, measured 2026-10-17T15:27Z
(`date -u`). main's five commits past the merge base touch only
`tools/coverage/` and the RCA/delivery records, and the base ends of the card
and fixture comparisons were re-run at the merge base anyway.

This is round 3. Round 2 (head `400df157`, fix `5295fa06a`) cleared the round-1
fix-review block `harness: class-open finite_inline`: the round-1 authored head
`959a011f0` had already carried the C4 fold (the four `n`-named receipt
spellings deduped to `finiteNum`), which took the finite-number census from 7
to 3; round 2 deduped the two remaining inline spellings the census used to
miss — `nowTemp` at card.js:7071 and a refit's `scale` at card.js:8684 — to
`finiteNum`, and widened the census check in `tests/card.mjs` to the finder's
own pattern (the SAME identifier on both sides of the `&&`, whatever it is), so
the census now counts 1, the `finiteNum` owner alone.

Round 3 takes the round-2 review's step-14 instrument note with its one-line
anchor: the exclusion in that census was a prefix match (`const finiteNum`), so
a second owner named `finiteNum2` left `node tests/card.mjs` green while
`card_shapes.mjs` counted `finite_inline=2`. Commit `270f5d05e` anchors the
exclusion to `const finiteNum = `; M11 below is the two-armed control — the
anchored check fails the second owner, and the prefix form passes it.

## Mutation proof

`python3 /private/tmp/r10-ux-setup/r3/mutants-r3.py` (measured at
`270f5d05e`; each mutant is an exact production-line replacement, restored
with `git checkout --` between runs; the closure is `node tests/card.mjs`, 13
runs, recorded in `/private/tmp/r10-ux-setup/r3/mutants-r3.log`):

| mutant | production line | checks that went red |
|---|---|---|
| M0 | none (null control) | 0 — the tree passes unmutated |
| M1 | `fitSlotRow` returns one ellipsized line again | `a slot label is drawn whole, wrapped rather than cut`; `and the label is never cut either, at any real length`; `a label that fits is left exactly alone`; `the six cases really are six different slopes` |
| M2 | an unset slot becomes an ordinary row again | 11 checks, including `an unset input folds into its box's one muted line, not a row`; `every slot is reachable from the diagram: a row, or inside a folded block`; `every configured slot is matched with its own hit rect`; `the census reached every navigateTo and openHaLink call site` |
| M3 | `.setup-box` left invisible (`fill: none`) | `the card is painted from the product's surface, border and radius` |
| M4 | `onePrecision` returns Home Assistant's string unchanged | `two temperatures on one drawing are spelled to one precision` |
| M5 | the axis counts characters instead of measuring its label (C1 reverted) | `the chart's label-width rule is spelled in exactly one place` |
| M6 | the no-plan empty state spelled a second time (C4 reverted) | `the no-plan empty state is built in exactly one place` |
| M7 | the finite-number test spelled a second time, name `n` (C4 reverted) | `the finite-number test is spelled in exactly one place` |
| M8 | an OPEN folded block's height counted as the folded one | `a block that is open sizes its box for the rows it now draws` |
| M9 | `nowTemp` re-spelled inline under a non-`n` name (round-2 fix reverted) | `the finite-number test is spelled in exactly one place` |
| M10 | `refit.scale` re-spelled inline under a non-`n` name (round-2 fix reverted) | `the finite-number test is spelled in exactly one place` |
| M11a | a second owner `const finiteNum2 = …` added, census exclusion anchored (this head) | `the finite-number test is spelled in exactly one place` |
| M11b | the same second owner, census exclusion reverted to the prefix form | none — `ALL CARD CHECKS PASSED` (the round-2 gap returns) |

M9 and M10 are the class the round-1 check missed: M7 re-spells the rule under
the owner's own `n`, which the old `typeof n === …` census already caught, but
M9 and M10 re-spell it under `nowTemp` and `refit.scale`, which only the widened
`typeof (\w+(?:\.\w+)?) === "number" && Number\.isFinite\(\1\)` census sees. That
the two kill the check is the proof the class is now closed, not the dedupe
alone.

M11a and M11b are the step-14 control for the check itself, not a production
fold: the same card is green under M11b and red under M11a, so the anchor is
what catches a second owner and the round-2 prefix form is what let it through.

M8 is the bug the P9 grid found at a narrow width before the fix: the height
pass counted the folded block only while it was folded, so a box that had just
been opened drew its last caption past its own card.

## Null control

- **The unmutated tree passes**: M0 above, `node tests/card.mjs` ->
  `ALL CARD CHECKS PASSED` at `270f5d05e`.
- **The census harness is stable**: the two card censuses run twice on the
  same file report identical counts (the harness documents this as its own
  null control, `dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs`).
- **The finder's harness reproduces the finding at the baseline**, not only at
  the head: `wizard_widgets.py` prints `menu_disagree=1` at the merge base
  `81b7aa9ff` and `menu_disagree=0` at this head, with `menu_fallbacks=23` at
  both ends — the comparison executes either way, and the `--bump
  heat_pump_cop_nominal` perturbation moves `disagree` 0 -> 2 at both ends, so
  the census is live, not vacuous.
- **The finite census reads the class, not the instance**: the widened check
  applies the finder's own pattern, so a re-spelling under ANY identifier
  (M9/M10) is what it catches, not a search for the two names the block named;
  and its exclusion is anchored (M11a/M11b), so a second owner under a
  different name is caught rather than skipped.

## Figures

- `node tests/card.mjs` (at `270f5d05e`) -> `ALL CARD CHECKS PASSED` (the
  closure for the card).
- `node tests/card_drift.mjs 81b7aa9ff976413ec98592045930647c0e0bac73` ->
  `39 state(s) moved and claimed, 1 identical`; the claims are in
  `tests/golden/card_claimed_drift.txt`, whose `claims-for:` is the live
  VERSION.
- `PYTHONPATH=tests/hastub python3
  /private/tmp/r10-ux-setup/export/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`
  (sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`; the harness derives its
  repo root from `__file__`, so it was copied byte-identical into each measured
  tree at that relative path and run from that tree's root; the copy is
  untracked and is removed before the scoped gate, which therefore sees only
  the committed diff) -> `menu_disagree` 1 at merge base `81b7aa9ff`, 0 here;
  `menu_fallbacks` 23 at both; `golden_equal=1` at both; `--bump
  heat_pump_cop_nominal` moves `disagree` 0 -> 2 at both ends.
- `node
  /private/tmp/r10-ux-setup/export/dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs
  <card>` (sha1 `677b75421ca84ac0f404dc90fa0b6a0b72edea0e`) -> at merge base
  `81b7aa9ff` `total=31`, `char_width_inline=2`, `finite_inline=7`,
  `no_plan_state=2`, `dead=2` (`top:textWidth top:openHaLink`); at this head
  `total=22`, `char_width_inline=0`, `finite_inline=1`, `no_plan_state=1`,
  `dead=0`.
- `node
  dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs <card>` -> at
  merge base `81b7aa9ff` `total=34` (`isfinite_lines=7`, `char_width_lines=3`,
  `no_plan_lines=4`); here `total=25` (`1`, `1`, `3`) — the finder's own
  second arm for the same folds.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`, no row moved.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all
  81b7aa9ff976413ec98592045930647c0e0bac73` -> `NO UNCLAIMED DRIFT: 56
  scenario(s) checked against 81b7aa9ff` and `NO STALE FIXTURE: 56 committed
  fixture(s) still match what this tree computes`.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=81b7aa9ff976413ec98592045930647c0e0bac73
  ./tests/run.sh` -> `MODE: SCOPED -- 16 script(s) run, 17 scoped out` (the
  same selection the round-2 review measured).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`
  -> `no closures or fast red predicted against 81b7aa9ff976 (a data-file read
  is not seen)`.

## Red checks

`closures` — red at `400df157`, green at `f97973cc`. The red was
`UNDER-SCOPED`: the new card check reads
`custom_components/heatpump_optimizer/translations/en.json`, and the recorded
closure did not list it. The answer is the autofix chain, not a hand re-record
(`ci-autofix.md`): `closures-autofix` classified the run and pushed the bot
commit `f97973cc` (`ci: re-record closures`), which adds
`translations/en.json` to that closure and re-records two `seconds`; the
`closures` check-run at `f97973cc` is `success`. The cheaper detector for a
missing closure entry is the `closures` check's own recorded run, which
enumerates the reads a closure must list; `tests/closure.py select` reads the
existing closures and cannot see a read one lacks, so there is no cheaper
detector — the gate that caught it is the one that reaches the fact.

`pr-contract` — red at `f97973cc` (run 39042398374), solely because `## Red
checks` did not name `closures`; the paragraph above discharges it.

`P9 grid: no two text runs share ink` — `20: text "2" x text "3" 2 px of
shared ink`. This is main's own, on this machine: the same check fails with
the SAME pair and the same 2 px at the merge base `81b7aa9ff` (log
`/private/tmp/r10-ux-setup/browser-base.log`, whose last line is `1 BROWSER
CHECK(S) FAILED`), and the round-2 review re-derived it there. The cheaper
detector is the gate that ran: the pair only exists once Chromium has rastered
the glyphs, and no earlier and cheaper instrument can see ink. CI is
authoritative for it; this lane's own header says the raster is not bit-stable
across Chromium builds.

`env_drift.py --all` — this script turned the branch's first two local gate
runs red, both times because of the same one-line label and each time for a
different reason: first `1 COMMITTED FIXTURE(S) ARE STALE` (the committed
capture still held the old label), then `1 UNCLAIMED DRIFT(S) vs the merge
base` (the capture no longer matches main's, which is what the change is FOR).
The trigger's question is whether a cheaper detector could have caught either
earlier, and in both cases the cheapest detector that reaches the fact is the
one that caught it, inside the run that caught it. The re-record-then-claim
sequence is now clean (`NO UNCLAIMED DRIFT` / `NO STALE FIXTURE` above).

## Unpinned sites

The `page ? L(page) : placeLabel(b.place)` fallback that `d408fa76a` adds (a
place the backend adds ahead of the card names itself, not "undefined") is a
written triage, not a pin. Its truthy branch is pinned by the round-2 check
`the Configure chip names the options page the flow itself names`, which reads
`SETUP_CONFIGURE_PAGE`, `STRINGS.en` and `translations/en.json` and refuses the
day any map entry stops naming the step the flow itself names. Its falsy branch
delegates to `placeLabel`, whose contract (`PLACE_LABELS[id] ? L(PLACE_LABELS[id]) : id`)
never returns "undefined", and the branch itself is unreachable from any
topology the diagram can draw today: every box place `setupSvgHtml` produces is
in `SETUP_CONFIGURE_PAGE` (wood_valve re-homes onto mixing_valve/wood_tank, and
slab_shunt has no box on any modelled layout). A behavioral pin would have to
inject a synthetic box the card would otherwise never draw, pinning a state
instead of the guard; the guard is one conditional, so a written triage is the
honest disposition. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py
--base origin/main` -> `no closures or fast red predicted`.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, group R10-ARCHSCORE-COVERAGE's
`brief`: the card's dead-definition row and clone census must be recorded at a
base that already carries these C1/C4 folds, and on this branch both rows were
absent from `tests/ci_budgets.json`, so the re-record lands with that group.
The carry names no literal, only the precondition and its control. The round-2
review's step-14 instrument note (`finiteNum2`) is closed in this head by the
anchor and M11a/M11b, so it needs no carry.

## Friction

`card_browser: unenforced: the twelve committed page figures under
docs/img/card regenerate differently on this machine at the merge base as
well, and no check compares a committed figure to what the card draws -- only
the two this change moves are committed here. The control is the regeneration
at the merge base: it rewrites all twelve, so the drift is the raster and not
this branch`.
