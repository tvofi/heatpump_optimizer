Fix review: blocked 82daaab4421a380e3e73c570e58dffe19dc0d588 harness: the card claims a tests/card.mjs pin and a finite census it does not have

bus-nonce: d3ff91435d44935db71c9e37cf60e410

Round 1 for this PR. Measured at `82daaab4421a380e3e73c570e58dffe19dc0d588`
(merge base `e3f3b312fff572904f24d78a44a2c4492b1a8ddb`) from a detached worktree at
the head; the contract in `dev/governance/roles/` is current (empty three-dot against
`origin/main`). The head matches the SHA the body names.

## RESULT lines (mine, not the fixer's)

Finder harnesses run unmodified, sha1 as the body states (`66b390554c0aa54c8960eacb532b04ff827ca8cf`
`wizard_widgets.py`; `677b75421ca84ac0f404dc90fa0b6a0b72edea0e` `card_shapes.mjs`), at both ends:

    RESULT menu_fallbacks=23 -> 23
    RESULT menu_disagree=1 -> 0
    RESULT golden_equal=1 -> 1
    RESULT total=31 -> 24; char_width_inline=2 -> 0; finite_inline=7 -> 3
    RESULT no_plan_state=2 -> 1; dead=2 (top:textWidth top:openHaLink) -> 0
    RESULT v2_card_lines total=34 -> 27 (isfinite 7->3, char_width 3->1, no_plan 4->3)

Null control: both censuses run twice on the same file report identical counts.

Mutation proof re-run independently with my own replacements
(`evidence/mutants-review.py`, `.log`, `.json`; closure `node tests/card.mjs`):

    M0 rc=0 fails=0 (null control)
    M1 fails=4  M2 fails=11  M8 fails=1  M3 fails=1  M4 fails=1  M5 fails=1  M6 fails=1  M7 fails=1

Each of the eight named checks from the body's table went red under its mutant, and
the file was restored from git between runs. `node tests/card.mjs` passes unmutated.

Drift and claims: `card_drift.mjs origin/main` -> `39 state(s) moved and claimed, 1
identical` (editor_schema). I re-derived the body's "33 inside the `<style>` block"
claim under its stated rule (common prefix/suffix of the two dumped `html` strings
against the block's own offsets): 33 states differ entirely inside `<style>`(61..49863);
the other six (setup_single_buffer, setup_two_tank, setup_coil, layout_editing_dragged,
layout_editing_tidy, picker_open_filtered) differ outside. That is the body's split.
`env_drift.py --all origin/main` -> 56 scenarios, `NO UNCLAIMED DRIFT`, `NO STALE
FIXTURE`. Both claim files' `claims-for:` is `7.0.0` (= VERSION). VERSION, manifest and
the RELEASE_NOTES heading are untouched. `tests/structure.py` -> `STRUCTURE RATCHET PASSED`,
no row moved. `merge-tree --write-tree origin/main <head>` exits 0, no claim-driver
refusal. CI's head check-runs: no failure anywhere in the range; the eight earlier heads
have no red gate run and the merge commit's only non-successes are cancellations.

Browser lane (my own runs, FULL grid, both ends): head and base each 74 `ok` and the
same single `FAIL P9 grid: no two text runs share ink -- 20: text "2" x text "3" 2 px of
shared ink`. Same pair, same 2 px, both ends: main's own, not this PR's. Head measures
324 cells and 102 colour rules (base 315 and 97); `every card rule that sets a colour is
rendered in some cell`, `no text is clipped where its ancestor cannot scroll to it`, AA
contrast, 24 px targets all pass. The Setup page renders at 375/768/1280 in both themes.
The two committed page figures are byte-identical to a head regeneration; 12 of 14
figures are byte-identical head vs base, the two Setup ones differ and are committed.
`make_card_figures.mjs` at both ends: `chart-anatomy.svg` and `chart-dashed-lines.svg`
byte-identical. Design tokens are shared, not gamed: the card uses `--hpo-surface-2`,
`--hpo-divider`, `--hpo-ink`/`--hpo-ink-2`, `--hpo-accent`, the same tokens the tiles and
chips read; the P9 colour-rule delta is the new colour rules being measured, not a literal
added to pass a check.

Forward-carry: the destination the body names (`wave-r10-groups.json`, group
R10-ARCHSCORE-COVERAGE's `brief`) does carry the precondition and its control ("measure
them on a base where the folds have landed, or the recorded dead-definition row counts a
helper the folds have since used"). Both `archscore.card_dead_definitions` and
`archscore.card_clone_copies` are absent from `tests/ci_budgets.json` at base and head, so
the carry, not a re-record here, is correct.

## Blocking findings

1. **harness -- a pin the card says it has and does not.**
   `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:626-629` and
   `:2434-2437` (both added by this PR) say `tests/card.mjs` pins the four
   `setup.page_*` names against `translations/en.json` "so the card cannot drift from
   the flow it points at (the class #2222 is about)". No test in the tree reads the
   card's `STRINGS` table, the `setup.page_*` keys, or `translations/en.json` from
   `tests/card.mjs`/`tests/card_rig.mjs`. The values are right at this head (they equal
   `_OPTION_PAGES` and `en.json`'s `options.step.advanced.menu_options` for
   entities/entities_pump/building/hot_water_tank), so no wrong copy ships; the defect
   is the false guarantee, in the PR that closes part of #2222's I5 class. It is the
   "claim stronger than the check" shape: a later seat will read the comment and trust a
   control that does not exist. Remedy: add the pin (compare the four `STRINGS` values
   with the four `translations/en.json` menu labels, keyed by config_flow's page ids) or
   remove the claim from both comments.

2. **harness -- the finite-number census overclaims.**
   `tests/card.mjs`, added under ARCH2-s5 C4: `check("the finite-number test is spelled
   in exactly one place", ...)` counts only the literal `typeof n === "number" &&
   Number.isFinite(n)` spelling. Two inline spellings of the same rule remain at
   `card.js:7071` (`nowTemp`) and `card.js:8684` (`refit.scale`), and the finder's own
   census says `finite_inline=3` at this head (the body reports 3, 7 -> 3 by design).
   The check's name and its comment ("neither is re-spelled inline anywhere else in the
   card") are stronger than what it measures, so a reader trusts a rule the check does
   not apply. Remedy: widen the census to the finder's pattern (any identifier) and
   either fold the two sites or narrow the name/comment to the spelling it does count.

3. **harness -- a comment this PR made false.**
   `tests/card.mjs:11565-11567`: "Driven directly, because no button calls it until a
   later group converts one." This PR gives `openHaLink` its first caller
   (`card.js:12304`, the Configure chip), and the press census presses it. Cheap, but it
   is the same stale-comment class the PR is closing.

## Body figure to correct

- M2's row says "10 checks"; the fixer's own `mutants.log` prints `fails=11` and lists
  eleven, and my run prints eleven. Correct the body to 11.

## Non-blocking, checked and holding

- The Setup-tab render seams I enumerated -- `setupSvgHtml`, the `.setup-*`/`.layout-*`
  stylesheet, `SetupPage`'s render/wireControls, `tankBarHtml`, `LayoutEditor.barHtml`,
  `pickerHtml`/`setpointHtml` -- are all in the diff or (the picker) already token-styled
  and outside the owner's acceptance list. No undispositioned UI seam of this class.
- Every acceptance item is answered: no silhouettes (`.setup-contour`/`.setup-coil`/
  `NODE_SHAPES` gone, no dangling refs), labels wrap (2 lines, all published labels
  fit), unset rows fold into one muted line + Configure chip with `openHaLink` and
  accessible names, pipes stop on the card border and are painted under opaque cards,
  one precision per unit with an unnamed-unit null control, layout-bar/tank buttons share
  the chip rule.
- The mutation table's per-mutant check names match my run exactly except M2's count.
- `ci_predict.py --base origin/main` -> `no closures or fast red predicted`.

## What I could not re-derive

Nothing material. The 33/6 drift split I derived with the body's own rule rather than a
finder harness; the escaped-string offsets are in `evidence/card_drift.review.log`.
The two `--all`/`card_drift` runs are the committed instruments.

Evidence: `evidence/` (`HEAD.txt`, `mutants-review.*`, `card_drift.review.log`,
`env_drift.review.log`, `browser-{head,base}.log`, `browser-figures{,-base}.log`,
`figures-compare.txt`, `rederivation.txt`, the regenerated PNG/SVG sets).

Code-owned paths (`tests/card.mjs`, the config_flow fixture): tvofi's approving review is
owed after this verdict, not this reviewer's.
