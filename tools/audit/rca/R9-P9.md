# R9 RCA — class P9 (card UI: clipping ancestor, missing colour token, unfloored hit target)

Seat: round-9 RCA, slug `p9`. Starts beside F6.1; the barrier lands in F6.3.
Baseline `1936d5ca` (v6.7.1), main `db878b29`. Prototype branch
`handoff/r9-rca-p9` @ `4f3b9d4f928f7616f601e8bc6f294bc693ddb7e5` (cut from `db878b29`, edits only
`tests/card_browser.mjs`). Probes and raw runs: `probe/` and `runs/` beside this file.
Machine: 4 vCPU cloud container shared with other seats, Chromium 1194 at `/opt/pw-browsers`,
playwright 1.56.1 at `/opt/node22/lib/node_modules`. Every wall-clock figure is stated with the
`load1` it was measured at.

## Root cause

### Cause, reproduced

**The card's CI witness is keyed to instances; the property is only measured by the audit.**
`tests/card_browser.mjs` runs on every PR, but each of its P9 checks pins the selector and state
that one past finding named. The D4 brief (`tools/audit/briefs/D4.md` §1: "WCAG AA contrast of
every text/background pair … every state … at viewports 375×812, 768×1024 and 1280×800, light
and dark, sv and en") is the rule over the whole rendered card, and that rule runs once per
round, in a finder seat. So every round re-finds instances at selectors and states the lane never
names. Three places in the lane show the shape:

- The contrast check asserts `const REQUIRED = ["wi-apply", "wi-save", "setup-slot.empty", "chip-off"]`
  (`d49659fe`, 2026-09-05). Its own carry-forward block, landed two days later (`c609b917`, #569,
  whose title is "four contrast and geometry defects the CI witness could not see"), says "The
  failing set is a RULE, not a list … Re-derive it." The list stayed. Its HA theme also defines no
  `--error/--success/--warning-color`, so the lane cannot see the tokens D4-s1-01 is about.
- The axis-unit ink check matches `unitPat = /^(°C|kW|kr\/kWh|öre\/kWh|W\/m²)$/` (`dae7baf5`). The
  card's default currency renders `SEK/kWh`, and the pattern does not match it.
- The card claims two labels never meet, and measures nothing to back the claim: "the "now" marker's
  label, which lives at a different x … whenever both happen to be visible together"
  (heatpump-optimizer-card.js, the `plan.estimated_prices` label). The grid measures 17–153 px of
  shared glyph ink between those two labels (below).

**The second half of the cause: which states get reached.** `tests/card_drift.mjs` STATES (40)
never reaches the status outcomes. The sweep had to add `x_*` states "the status-text outcomes
STATES never reaches". The barrier's reach rule (below) found 26 colour-setting CSS rules that the
12-state canonical grid never renders, and still 10 after adding 13 card_drift-shaped states.
Driving those 10 found new instances.

Reproduced here at `1936d5ca` with the sweep's enumerator (`D4/s1/sweep.mjs`, identical to
`D14/sweep/P9/enumerate.mjs`), the canonical 144 cells: `contrast_instances=90`,
`popup_out_cells=6`, `option_indistinct_pairs=8`, `now_marker_collisions=24`,
`overlap_instances=160`, `pointerOnly_instances=204`, wall 83.9 s at load1 5.78
(`runs/base.out`). The same numbers at `db878b29` (`runs/main.out`), so #1643 moved nothing.

Which side moved (`git log -S`): the status colours (`8adb3191`, `f0019a0f`, 2026-08-22/23), the
picker `sp-select` (`21497751`, 08-24) and the slot menu (`364d9b41`, 08-22) all predate the
browser lane's contrast and geometry witnesses (09-05..09-08). They are latent, and seven rounds of
per-instance pins did not reach them. The now-temp label (`3df1be62`, #1495, 2026-09-23) is new: a
feature PR introduced it and passed the browser lane, because the lane has no general text-overlap rule.

### Class search (beyond the sweep)

The prototype grid (below) at `1936d5ca`, 31 states × 7 cells (`runs/base-full.json`):

| # | seam | measurement | disposition |
|---|---|---|---|
| 1 | `button.sp-save.confirm` "Confirm: clear this sensor" (setup picker, clear armed) | 4.29:1 < 4.5 (white on HA `--error-color` #db4437), 4 cells | **new instance**, same cause as D4-s1-01's `wi-save.confirm`; the sweep never reached the state |
| 2 | `plan.estimated_prices` label on the estimated band | 3.94:1 < 4.5, en and sv, 6 cells | **new instance** (every price estimated, i.e. a price source down) |
| 3 | `text.now-label` × `plan.estimated_prices` label | 17–153 px of shared glyph ink, 375/768/1280, en and sv, 7 cells; `probe/estimated_price_hover.png` shows "now" printed over "estimated p…" | **new instance**, D4-s1-05's mechanism at a second seam; contradicts the code comment quoted above |
| 4 | `rect.slot-hit` 17.4×24.5 px, shared-steps state, 375 px | overlapped 2.3 px and 7.3 px by its neighbours' grown targets; fails the 2.5.8 spacing exception; not "boxed in" | **candidate instance**. The card grows each target against its neighbours' ink, not their grown targets |
| 5 | P9-sw1, axis number/unit pairs ("60"/"°C", "6"/"kW", "400"/"W/m²", "3"/"SEK/kWh") | **0 px shared ink** in all 13 box-intersecting pairs probed (375/1280, inline and dialog; `probe/ink_pairs.mjs`); 0 of 421 box-intersecting pairs flagged across 217 cells on the fixed card; `probe/axis_1280.png` shows "°C" stacked clear above "60" | **not a P9 instance under an ink rule**: the sweep's box metric counts line-box overlap. Positive control for the same probe: now-label × now-temp shares 150 px (1280) and 51 px (375) |
| 6 | `button.vc-in` / `vc-out` 4.24:1 at 1280 in `away_status` | appeared only with transitions running; 0 under `reducedMotion: "reduce"` | **artefact** (fade measured half-way): a flake source for any grid, so the barrier runs with reduced motion |

### Process state: **(c)**, the process was followed and did not produce the intended result

The process: the real-browser lane (#121, "geometry the DOM stub cannot see") plus the fix protocol
(failing test first; `fixer.md` step 8's class enumeration since `6bc932db`, 2026-09-22). It was
followed. `tests/card_browser.mjs` has 18 commits, nearly each a round's D4 fix adding its witness
(#135, #333, #258/#262, #558 C1/C4, #935/#936, #1320, r7-card, #1553), and every witness passes
today (`runs/lane-mainx.out`: "ALL BROWSER CHECKS PASSED"). The result was not the intended one:
the ledger (`tools/audit/bugclasses.json` P9) records 19 instances in rounds 1, 2, 4, 5, 6, 7;
round 9 adds 5; the grid finds 3–4 more at baseline.

- Not (a): the lane and the protocol existed. The ledger has named the detector since `ef4a1bf1`
  (2026-09-24): "The browser geometry sweep over every rendered node: hit-target floor, contrast,
  clip against its ancestor".
- Not (b): the pins were written and are green.
- Not (d): no precondition changed. The unit of work was always the instance.

The countermeasure is therefore not a firmer instruction. It moves the audit's property rule into
the per-PR lane, with a control that fails when the rule stops reaching a styled state.

## Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, per audit round.

- **Standing cost, measured.** The existing lane took 18.5 s; with the grid it took 152.6 s
  (both at load1 ≈ 1, `runs/lane-*.out`), so **+134 s per run**. Under load1 5–20 the grid alone
  took 103–184 s. It runs inside the existing `browser` job, which is never scoped, runs in parallel
  on every PR and push, and has a 20-min timeout. The window `cdf82daa..1936d5ca` (2.6 days) merged
  **88 PRs**, which comes to about 88 × 134 s ≈ 3.3 runner-hours per round. It adds zero seat time.
  It adds up to 134 s of PR latency only when `browser` is the slowest job; I did not measure the
  other jobs' durations (no `gh`).
- **P(recurrence), measured.** ≥1 P9 instance in 7 of 9 rounds (ledger rounds 1, 2, 4, 5, 6, 7
  plus 9); 24 instances in 9 rounds, **2.7 per round**. The grid adds 3–4 at baseline. All 5
  round-9 instances shipped in v6.7.1.
- **Defect cost, estimated, not measured.** Each instance is a user-visible escape, plus the
  round's per-finding pipeline (finder, three verifiers, judge, sweep, fix PR, review, and RCA for
  the class). Git cannot time squash-merged PRs, so I measured no per-instance wall-clock. Even at
  an assumed 1 seat-hour per instance, the right side is ≥ 2.7 seat-hours per round, against
  0 seat-hours and ≤ 134 s of latency per PR on the left.
- **Verdict: build it.** A cheaper form was considered and not chosen: run the grid only when the
  card surface changes. Only 5 of the 88 PRs touched `www/`, `card_browser.mjs` or `card_rig.mjs`,
  so this would cut the runner cost about 18×. It adds a skip path to a job that is deliberately
  unscoped, so it is tvofi's call, not a default.

## The barrier (prototype on `handoff/r9-rca-p9`)

**Form:** a property-keyed grid inside `tests/card_browser.mjs` (`p9Grid`, +572 lines, test only).
It adds no new tracked file (`card_browser.mjs` is already INERT and `NOT_A_TEST`), and it imports
the existing `tests/card_rig.mjs` helpers.

- **Grid.** 31 states × 7 cells: 375/768/1280 × en/sv light, plus 375 dark in English. Contrast
  varies with theme and geometry varies with width and language, so the 12-cell product is not
  needed. HA default theme tokens include `--error/--warning/--success/--info-color`. Clock frozen;
  `reducedMotion: "reduce"`.
- **Rules over every rendered node:**
  - WCAG AA contrast, composited over what is actually underneath (HTML backgrounds and preceding
    SVG shapes);
  - **zero shared glyph ink** between two text runs. Box-intersecting pairs are rasterised one run
    at a time, forced black on white, and their pixels intersected. This is what separates D4-s1-05
    from P9-sw1;
  - pop-ups (`.tooltip`, `.slot-menu`) stay inside the viewport and their chart;
  - listbox options are distinct as shown;
  - no clipped ink that its ancestor cannot scroll to;
  - 24 px targets, or the 2.5.8 spacing exception, with the lane's existing "boxed in" case allowed.
- **Controls that stop it going green by skipping:**
  1. every cell mounted, every driver step found its target, and the cell count equals
     states × cells;
  2. **reach**: every card CSS rule that sets `color`, `background` or `fill` matches a visible
     element in some cell. A new status class with no state that renders it fails the lane. This
     closes the state half of the cause.

**Evidence** (in-memory fix emulation `probe/fixed.mjs`: the sweep's four perturbations, plus
confirm-button fill #b3261e and the estimated label moved two lines lower in the text token):

| run | result |
|---|---|
| `1936d5ca`, full grid (`runs/base-full.json`) | FAIL: contrast 73, ink 21, pop-up 3, options 5, target 3; reach ok; drivers ok |
| in situ, branch lane on `db878b29` (`runs/lane-situ-main.out`) | 5 P9 checks FAIL; every pre-existing check passes |
| in situ, branch lane on fix-emulated `db878b29` (`runs/lane-situ-fixed.out`) | every P9 rule **ok** except targets (candidate #4, no fix emulated; one attempt, half-gap growth, made 53 targets worse) |
| fixed card, one fix reverted at a time (`runs/reintro.out`) | status tokens → contrast 53; confirm fill → contrast 14; menu clamp → pop-up 3; picker wrap → options 5; now-temp → ink 14; estimated label → contrast 6 + ink 7. Each reverted fix fires only its own rule |
| **null, reach**: the 7 status states dropped from the catalogue | reach FAILS, 9 unreached (`.wi-save.confirm`, `.sp-save.confirm`, `.wi-result.cheaper/.dearer`, `.wi-warn`, …). This is the round-9 D4-s1-01 escape path, now refused |
| **null, healthy nodes**: fixed card | 421 box-intersecting text pairs inked, 0 flagged; 11 763 text runs, 0 contrast failures; 0 unparsed colours |

Ratchet: `tests/structure.py` on the branch prints "STRUCTURE RATCHET PASSED". No budget moves, no
raise needed.

## Plan fold

- **Landing PR: F6.3, as planned.** It is tvofi-gated because `tests/card_browser.mjs` is
  code-owned (`/tests/card_browser.mjs @tvofi`). No policy file is touched.
- **Files:** `tests/card_browser.mjs` only. It imports `tests/card_rig.mjs`, which is not
  code-owned and needs no edit.
- **Lines:** production 0; test +572 in the prototype. The F6.3 fixer may pay some of it back by
  deleting per-instance witnesses the grid subsumes. The obvious one is the `REQUIRED` four-selector
  contrast loop. Whether to delete each is the fixer's call, with the grid shown failing on each
  deleted witness's own perturbation first.
- **Plan change: F6.3 cannot go green until these are fixed or dispositioned.** The grid is a zero
  rule and takes no allow-list (`fixer.md` step 14). Proposed: add to **F6.1** (same file, same lane):
  - new instances #1 (`.sp-save.confirm` contrast), #2 (estimated-prices label contrast) and
    #3 (now-label × estimated-prices ink);
  - candidate #4 (squeezed `slot-hit`), which needs a fix design, so it may belong in F6.2 or a
    split.

  F6.1 already carries 4 findings plus sw1. If these push it past the brief's 5-finding / 400-line
  stop, split it into F6.1b with `after: F6.1`, and make F6.3 `after: F6.2, F6.1b`.
- **Carry to F6.1's brief (finding-propagation):** P9-sw1 does not reproduce under an ink
  measurement: 0 shared px, with the positive control on the same probe. F6.1 should not move axis
  unit labels on its account. The barrier's ink rule is its pin, and it stays green with the labels
  where they are. The class count under the barrier's rule is 4 judged + 3 new + 1 candidate. The
  orchestrator decides the issue's N.
- **F6.2 exposure:** the grid is not a keyboard lane. The 204 pointer-only hits remain F6.2's to
  re-check with keyboard cells on.
- `after` edges are otherwise unchanged.

## Needs tvofi

1. F6.3's review (code-owned lane), as the plan already says.
2. Whether ~134 s more per `browser` run (about 3.3 runner-hours per round at 88 PRs) is accepted
   unscoped, or the grid is scoped to card-surface diffs with `main` forced full.
3. Whether the new instances enlarge F6.1 or become F6.1b.
