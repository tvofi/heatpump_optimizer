# Class sweep P9, round 11 (D14 steps 3-4)

Mechanism (bugclasses.json): Card UI with a clipping ancestor, a missing colour token or a hit target below the floor. The class has recurred in rounds 1-9, 37 instances in total. Its detector is the P9 grid in `tests/card_browser.mjs`.
Baseline: `handoff/audit-r11-register` at 28b864af6d. The worktree is sparse because the host disk was full (236 MB free).

## Enumerator
`node dev/audit/rounds/round11/D14/p9_enumerate.mjs custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
This is a static pass over every CSS rule in the card. It flags seven kinds of seam:
- `clip`: an overflow hidden/clip rule
- `colour`: a raw colour literal outside `var()`
- `role-colour`: a templated role colour
- `target`: a `cursor:pointer` rule or pipe stroke with no 24 px min floor
- `target-coarse`: a floor under 44 px with no `pointer: coarse` override
- `type`: a font size off the scale
- `row-align`: a repeat-column grid without `align-items`

Output: 70 seams, recorded in `D14/p9_seams.json`. By kind: type 29, target 18, colour 10, row-align 5, role-colour 4, clip 3, target-coarse 1.

- **Positive control:** the enumerator lists the site of every finding: D4-s1-01 (`.setup-pipe`, target), D4-s1-03 (`.hl-fold-head`, target-coarse), D4-s3-02 (`.hl-stats` and `.tiles`, row-align), D4-s3-03 (`.tooltip`, type), D4-s3-04 (the errorColor sites, role-colour) and D4-s3-05 (type).
- **Null control:** `D14/p9_clean_fixture.js` gives 0.
- **Perturbation:** `--perturb` adds one line to `.hl-fold-head` (overflow, a raw colour and a 10 px font) and one second role colour. The count goes from 70 to 74.

## Dispositions
- **Instances (judged sites, beyond_finding false):** the six sites of the findings, listed in sweep-P9.json.
- **Guarded (target, 17 rules other than the pipes):** the P9 grid in card_browser.mjs checks the 24 px floor, or WCAG 2.5.8's spacing exception, on every rendered node in 31 states. These rules carry their size through padding or SVG hit twins, so the CSS shows no min-height.
- **Guarded (colour, 10 rules):** the P9 grid checks AA contrast over what is underneath each node in light, dark and cross-scheme cells. The literals are var() fallbacks, shadows or SVG data series.
- **Guarded (clip, 3 rules):** `.sb-bar`, `dialog.expanded` and `.rb-track` are covered by the grid's "no unreachable clipped ink" assertion. The bar tracks clip only their own fill.
- **Guarded (role-colour warnColor/successColor, L6174 and L6263):** each role has one `*_READABLE` constant per scheme. The split is in the error role only (D4-s3-04).
- **Not applicable (row-align `.hl-narrative`, `.health-inputs`, `.receipt-grid`):** their cells are single text runs, so the default stretch alignment leaves no baseline offset. The value-and-label stacks that misalign in D4-s3-02 occur only in the headline tiles. This was not checked in a browser here because disk space blocked the box.

Instances beyond the findings: **0**.

## Barrier
`barriered: false`. The P9 grid exists but missed four of the six findings: the 44 px coarse-pointer floor, type-scale membership, a single colour per role, and row alignment. The proposed barrier adds these to the grid's per-node asserts, with this static enumerator as a cheap pre-check in `tests/`. The gate cost is about 1 s for the static pass, plus the grid's existing browser time.
