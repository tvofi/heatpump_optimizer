<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
Replaces the card's italic prose list of narrative lines with one surface-2 panel of rows: a label on the left, kWh over cost in a nowrap tabular column on the right. tvofi asked on 2026-10-03: "The insight text in the card in iOS doesn't look neat, design it better ... Make sure it also looks good in desktop resolution." Card only (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_browser.mjs, tests/golden/card_claimed_drift.txt); no Python, so every value-bearing golden is untouched.

What the screenshot showed: four italic grey sentences with no container, the numbers buried mid-sentence, and "SEK)" orphaned on a line of its own because the money tail wrapped freely.

Design: rows come from the narrative sensor's structured `items`; the label is the card's existing `reasons.*` string (EN and SV already exist), the number column is `white-space: nowrap` + tabular-nums, idle/pump_mode are a muted status row (hours, no cost). The currency is the savings sensor's declared unit (the same chain the savings tile uses). A row the card cannot label (a reason a newer integration added) shows the published line verbatim, and when `items` is absent or does not pair one to one with `lines` every line shows verbatim (R9-UX-1's every-line rule stays). One column on a phone, two once the card is about 720 px wide, from one auto-fit grid rule (no media query, so a narrow card on a wide desktop stays one column). Orchestrator decisions 2026-10-03 applied: no dot colours, two columns at >= 720 px.

Screenshots (dark theme, deviceScaleFactor 2): /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/orch/seat-ux-8/narrative-375.png, narrative-360.png, narrative-640.png, narrative-1280.png in the same directory.

## Head

9cc8bdf73c7f1d3416efc15f399da0c200fe1356

## Mutation proof

Run with `node tests/card.mjs` (HPO_PLANDATA set) at 9cc8bdf73c7f1d3416efc15f399da0c200fe1356, mutating the predicate and restoring each time:
- `items.length === lines.length` replaced by `items.length >= 1` in narrativeRows: "narrative: misaligned items and lines fall back to the lines" red (1 failed). That check now uses the three labelled, numeric fixture items with lines [lines[1], lines[2]], so a card that paired them would print the pre-heating kWh and cost on the tank-charging sentence; round 1's version used an unlabelled item and passed with the guard removed (reviewer's finding).
- the same predicate replaced by `false`: 5 checks red (label, number column, idle status row, unlabelled-reason fallback, Swedish labels).
- `white-space: nowrap` deleted from `.nl-num`: "narrative css: the number column is nowrap and tabular" red.
- the `calc(50% - 13px)` cap deleted from the grid rule: "narrative css: the column count is capped at two" red. That check is a textual pin; the layout itself (2 columns at 1280 px, not 3) is measured by the browser lane, the right pin for a layout property.

## Null control

Before the auto-fit cap the 1280 px browser check failed with 3 columns, so the check separates the two layouts (the reviewer reproduced 3 columns with the cap removed). At the merge base the local `tests/card_browser.mjs` fails exactly one check on this machine, "P9 grid: no two text runs share ink" (2 px between chart tick labels), and fails the same way on this branch; it is a local-font artefact of Chromium 1148 under Playwright 1.56, and CI's pinned browser passed it at the round-1 head. `GOLDEN_MODE=drift` `env_drift.py` against the merge base passes with the Python claim list untouched.

## Figures

Origin/main tip merged: ac255c200 (stamped 6.7.15); merge base of this head is `ac255c200`.
- `node tests/card.mjs` : ALL CARD CHECKS PASSED at 9cc8bdf73c7f1d3416efc15f399da0c200fe1356 (round 1 had 11 new narrative checks red before the implementation; this round adds one pairing check strengthened and one cap pin, 12 new in all).
- `node tests/card_drift.mjs $(git merge-base origin/main HEAD)` : rc 0, "39 state(s) moved and claimed, 1 identical"; only score_open also moves in markup; editor_schema identical and unclaimed. claims-for is 6.7.15, equal to VERSION (the claimnotes driver re-took it in the merge).
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED. `node .claude/workflows/policy_lint.mjs --budgets` : rc 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` : MODE: SCOPED, 11 scripts. Run locally, all rc 0: doc_claims, arch_score_head, deployment_shape, harness_headers, entities (2118 checks), env_drift, plan_view, card.mjs, card_drift.mjs. features.py and golden.py are left to CI (no Python moved).
- `node tests/card_browser.mjs` : the four "R9-UX-8 narrative at 360/375/640/1280 px" checks ok; the one P9 failure above is the only red.

Options considered. (1) Regex the translated sentence into label and number: rejected, language-fragile and breaks on any template edit; items are structured already. (2) Container query on .headline for the two-column switch: rejected, dialog.expanded is sized by its contents and the card's own comment warns that container-type: inline-size removes that sizing; auto-fit grid needs no containment. (3) Media query at 720 px: rejected, it reads the viewport, so a narrow card on a wide desktop would get two cramped columns. (4) Per-row hairline dividers: rejected, they do not align across two columns; row gap is enough. (5) Series-coloured dots: dropped on the orchestrator's decision. (6) Keep prose, just drop italic: rejected, does not fix the buried numbers or the orphaned SEK). (8) Bold the cost instead of the kWh: rejected, the kWh is the quantity the label describes and the first thing the eye lands on in the column, while the cost beneath it is a consequence; bolding money would also make every row compete with the Plan cost and Projected savings tiles above, which already lead with money. A taste call, not a defect. (7) Fall back all-or-nothing when any reason is unlabelled: rejected for the per-row fallback, which keeps labelled rows tidy; all-or-nothing is used only when items and lines do not pair, since pairing is then unknown.

## Red checks

none

## Forward-carry

none. Seen and not folded in: the plan chart's zoom buttons (- + reset) overlay the chart in tvofi's screenshot and the legend caption wraps to three lines; reported to the orchestrator for a separate decision.

## Friction

none
