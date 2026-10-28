Fix review: blocked 2cfb8b9660f5940d27a8ed38c5c54e77e9a821e3 regression: tests / browser is red at this head and green at the merge base (P9 grid: 29 cells throw on screenshot, and pop-ups leave the viewport by 4.5-6.7 px), reproduced locally at both ends, and the body does not name it

bus-nonce: b79560b6b2641b8059faefc1fa834ee9

## Round

First review of this head (2cfb8b9660f5940d27a8ed38c5c54e77e9a821e3), measured from a detached worktree. Merge base 5261ba84139d9459465ccd842b61b04c2b1329d8 is origin/main now. Role files: `git diff <mb>...origin/main -- dev/governance/roles/` is empty.

## Block

- `tests / browser` (check run 121335806091) concluded **failure** on this head. On main at the merge base 5261ba84, `tests / browser` concluded **success** (run 40245337471, job 121325686963).
- Reproduced in this seat with `HPO_BROWSER_SCOPE=full node tests/card_browser.mjs` after `tests/plan_view.py`: **head rc=1, base rc=0** (ev/browser_wt2.txt, ev/browser_base.txt). Same two failures as CI, so this is deterministic, not a flake:
  - `FAIL P9 grid: every cell mounted and every driver step found its target`: `threw 29: page.screenshot: Clipped area is either empty or outside the resulting image`.
  - `FAIL P9 grid: no pop-up leaves the viewport or its chart`: `10: div.slot-menu 6.7px outside | div.tooltip 4.5px outside | div.slot-menu 5.3px outside`.
  - Base: `ALL BROWSER CHECKS PASSED` (19736 text runs, 660 inked pairs). Head: 20350 text runs, 850 inked pairs.
- The likeliest cause is the dialog's 14 px floor (H1), which enlarges the slot menu and tooltip. I did not bisect it.
- The body's Red checks section does not mention `tests / browser`. Its scoped gate ran 24 scripts and skipped the browser lane, which costs about 4 minutes locally and was the cheaper detector before the handoff (defect-root-cause.md). The fixer owes the fix, and either a red-check answer naming this lane or a root-cause line.

## Findings

- Regression: the P9 browser grid fails at the head and passes at the base (see Block). Severity: blocking. Carry: R10-CARD-VOICE
- `.adv-row:hover` still paints `var(--secondary-background-color, #f5f5f5)` under the card's `--hpo-text` ink, so in the unthemed dark arm the hovered advisor what-if row is the same 1.20:1 pair H3a fixed for `.health-row` and `.adv-inbox-row`. H3 named only those two classes, so this is outside the carry. Severity: minor. Carry: dismissed: outside H3's named classes; a hover state on the advisor page, for the D4 brief if the owner wants the pair rule applied to every surface
- H3a's themed arm is not the no-op the brief predicted: 14.44:1 → 11.08:1 with a theme defining `--secondary-background-color` (#111111). The body states this, and both values clear AA. Severity: info. Carry: dismissed: disclosed in the body, and V5's pair rule wins over theme passthrough

## Evidence

Each carry checked at the head:
- **C1 (H1):** `DIALOG_FONT_PX_MIN = 14`; caption roles are `max(12px, …)`. Measured with the study's harness (6aea0d10 harness.html and states.js, run by the fixer's driver `dev/audit/harnesses/r10_card_harmony.mjs`, which I ran myself at both ends; ev/harmony_summary.txt):
  - dialog base 12/12/12.9 → 14/14/14 px;
  - HTML text nodes under 12 px → 0 on every page and width;
  - wi-hint 10.20/10.20/10.96 → 12.00;
  - group title 10.80/10.80/11.61 → 12.60.
  - Card-face null arm: 5 of 32 nodes move at every width and theme, all caption roles (hl-caveat 11.48→12, legend-note 10.64→12, three viewctl buttons 11.90→12).
- **C2 (H2):**
  - Layout bar against the chip: 9.84/9.84/10.58 → 16/14/14 px, against a chip of 16/14/14 px, so equal at all three widths.
  - Disc rendered at 14/17.1/29.4 px, measured. The brief's 17.5/29.8 is a prediction, and the body reports the measured values.
  - Glyph stroke 1.5px. The null arm holds: box stroke 1px and pipe stroke 1.5px at both ends.
  - The disc is `aria-hidden`, and each box `<g>` carries a `<title>`.
- **C3 (H3):**
  - Unthemed dark row: 1.20:1 → 11.08:1.
  - Themed arm: 14.44 → 11.08:1 (see Findings).
  - Health heading weight 700 → 600.
  - The savings empty state is `<div class="empty">`.
- **C4 (H4):** the `.replay` overflow-x and 560 px svg min-width sit inside `@media (max-width: 600px)`. Labels at 375 go from 5.89–6.42 to 10.27–11.20 px; 768 (12.65–13.81) and 1280 (21.67–23.64) are unchanged. My base figures are at 5261ba84, and they match the body's da12aa37d figures.
- **C5:**
  - All five `--hpo-text-sm` fallbacks read 13px.
  - The setup chip comments now say the chip is NOT a legend chip's size.
  - `DIALOG_FONT_PX_MAX = 18`, and its comment derives 17.85.
- **C6:** `savings_page`, `savings_empty`, `health_page`, `setup_not_published` and `advisor_empty` are added to tests/card_drift.mjs.

Group brief:
- type disc per box, with a spring on the wood tank while a coil is configured, dimmed when not modelled;
- the accent coil pipe, dashed when not modelled, with no `data-edge`;
- three coil states in words on the hot-water box;
- Configure on every box, naming its page, plus a destination line above the drawing;
- `dhw_wood_coil_configured` published by `describe_setup`;
- dashboard-card.md no longer describes contours or a spring on the tank wall;
- all three hydronic SVGs have 0 `setup-contour` and 0 `setup-coil`.

Tests and records:
- `node tests/card.mjs` at the head: ALL CARD CHECKS PASSED.
- Mutation proof (my own mutants, ev/mutants.txt): M1, M2, M3, M6, M10, M12, M13, M14, M15, M15b, M16, M16b, M17, M19, M19b, M20, M21 and M22 each turn card.mjs red on the named check. Backend M8 (`"dhw_wood_coil_configured": False`) gives `1 of 4415 FEATURE CHECKS FAILED` (the body says 4402, since main added checks). The tree was restored and verified clean.
- `node tests/card_drift.mjs 5261ba84…`: `44 state(s) moved and claimed, 1 identical`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `claims-for` 7.0.4 = VERSION. VERSION, the manifest version and RELEASE_NOTES are untouched in the three-dot diff.
- The delivery row dev/programme/delivery/2841.md is in the three-dot diff.
- `git merge-tree --write-tree origin/main <head>` exits 0 (clean).
- I did not re-run `env_drift.py --all`; the five coord claims are add-only and were read from the diff.

CI at this head:
- `tests / browser`: failure (Block).
- `governance / delivery-status`: failure. Its log reads "This check is NOT a required context and a red here blocks no merge"; the OVERDUE rows are other merged PRs' main backlog, not this diff's.
- Still in progress when read: `tests / coverage`, `tests / closures`, `tests / fast (3.14)`, `codeql / Analyze (python)`.
- Every other completed check is green or skipped.

This seat posted no PR comment. The dispatch payload forbids comments, and that overrides the brief's "post the verdict as a comment"; the orchestrator relays the verdict.
