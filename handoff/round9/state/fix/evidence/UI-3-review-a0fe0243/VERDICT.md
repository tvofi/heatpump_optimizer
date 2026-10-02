Fix review: blocked a0fe02438bf2f0d466d75a4ee6a5ff0db8e1faa4 theme-contrast: tiles, idle pill and the restyled savings/score row pair theme text with a literal light surface; under a dark HA theme without modes.dark (HA forces darkMode false) they paint 1.24:1 and 2.63:1, and the savings/score row regresses from 13.03:1 and 6.13:1 at base

Round 1. R9-UI-3, branch handoff/r9-ui-card-2i3zh7, code head a0fe0243 (transport 56239b83 changes BODY.md only). Merge base f67f598a; main dc6c97e4.

## Finding (blocking)

`--hpo-surface-2` is a bare literal (`#f7f9fb` light, `#242a30` dark) chosen from `hass.themes.darkMode`, but the text painted on it (`--hpo-text`, `--hpo-text-2`) resolves through `--primary-text-color` and `--secondary-text-color`, so a theme overrides the text and never the surface. HA's frontend (src/state/themes-mixin.ts, dev) sets `darkMode = false` for any selected theme without `modes.dark`:

    if (!selectedTheme.modes || !("dark" in selectedTheme.modes)) { darkMode = false; }

Most community dark themes are written that way, so on those installs the card takes the light surface while the theme supplies light text.

Harness: `theme_probe.mjs` in this directory. It is the reviewer's own probe, not the finder's (this is a feature, so there is no finder) and not the fixer's. It paints the shipped `cardStyleBlock(false)` in a shadow root under HA's own dark values set as theme variables (`--primary-text-color #e1e1e1`, `--secondary-text-color #9b9b9b`, `--card-background-color #1c1c1c`), then reads computed colours and the effective background.

RESULT head a0fe0243, dark theme, darkMode false:

| element | contrast |
|---|---|
| tile-n | 1.24:1 |
| tile-k | 2.63:1 |
| tile-u | 2.63:1 |
| status-pill (idle) | 2.63:1 |
| hl-value | 1.24:1 |
| hl-label | 2.63:1 |

RESULT base f67f598a, same theme: hl-value 13.03:1 and hl-label 6.13:1. The savings and score row was readable before this PR.

Null control: HA default light values, darkMode false, at the head give tile-k 4.56:1 and tile-n 15.26:1. Those equal DESIGN.md section 3's contrast table exactly, so the probe measures the cascade the design measured. Full output: `theme_probe.txt`.

The design's contrast table and the P9 grid both assume HA's default theme variables, so neither reaches this configuration. That is why the head's own checks are green.

## What would clear it (fixer's choice)

Keep each text and surface pair on one source. One way is to derive the surface from the theme, which keeps one `var()` level, for example a theme-derived token or a `color-mix()` of the card background and the text colour. The other is to paint the tiles, the idle pill and the restyled `hl-stat` with literal text tokens, as the ok, warn and crit pill tones already do. Either way, add a case to tests/card.mjs or the P9 grid in which theme variables are dark and darkMode is false, failing first at a0fe0243.

## Checked and found sound

- The stale rule mirrors coordinator `_plan_is_stale`: 3 x the interval, floor 90 min, the same `_last_optimization` (successful solves only).
- `next_optimization` is set to now + interval each cycle, so its state minus `last_changed` is the interval.
- `total_energy_kwh` and `total_cost` are per plan (space from raw_space, DHW from raw_dhw), so the tile's sum does not double-count.
- "no plan" is the plan sensors' empty-plan state, and `active_now` is step 0 > 0.05 kW.
- The indoor sensor joined `headlineSignature`, as the brief requires.
- "Planned heating" is the honest label for `total_energy_kwh` (electricity). The deviation from DESIGN.md's "planned heat" is accepted.
- `git merge-tree --write-tree origin/main a0fe0243` exits 0. Main has not touched the card, its tests or the card claim file since the merge base.
- No resume files are in the code-head ancestry. VERSION, the manifest and the notes heading are untouched.
- `git diff merge-base...origin/main -- tools/audit/briefs/` is empty, so this contract is current.

Not re-run here: the full gate and the mutation table (cite the head's CI per fix-review.md step 11). The fixer's card.mjs, drift, browser grid and JS mutant results are being re-taken, and round 2 will report them.

## Re-run at a0fe0243 (independent, finished after posting)

I re-ran these myself, and all of them agree with the fixer's claims. These checks were green in round 1 and are not what the block is about.

- `node tests/card.mjs`: rc 0, ALL CARD CHECKS PASSED.
- `node tests/card_drift.mjs origin/main`: 39 states moved and claimed, 1 identical.
- `HPO_BROWSER_SCOPE=full node tests/card_browser.mjs`: rc 0. The P9 grid ran 306 cells.
- `structure.py` and `entities.py`: rc 0.
- The fixer's js_mutants.py: 18 of 18 mutants killed.
- Failing first: the head's card.mjs run at f67f598a has 20 UI-3 checks failing and 5 passing. The 5 that pass are absence and shape checks, as the body states.

Environment: python 3.11 with the pinned numerical stack, and playwright 1.56.1 from tests/pwlane's lockfile.
