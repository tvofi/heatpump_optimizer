<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
Replaces the card's italic prose list of narrative lines with one surface-2 panel of rows: a label on the left, kWh over cost in a nowrap tabular column on the right. tvofi asked on 2026-10-03: "The insight text in the card in iOS doesn't look neat, design it better ... Make sure it also looks good in desktop resolution." Card only (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_browser.mjs, tests/golden/card_claimed_drift.txt); no Python, so every value-bearing golden is untouched.

What the screenshot showed: four italic grey sentences with no container, the numbers buried mid-sentence, and "SEK)" orphaned on a line of its own because the money tail wrapped freely.

Design: rows come from the narrative sensor's structured `items`; the label is the card's existing `reasons.*` string (EN and SV already exist), the number column is `white-space: nowrap` + tabular-nums, idle/pump_mode are a muted status row (hours, no cost). The currency is the savings sensor's declared unit (the same chain the savings tile uses). A row the card cannot label (a reason a newer integration added) shows the published line verbatim, and when `items` is absent or does not pair one to one with `lines` every line shows verbatim (R9-UX-1's every-line rule stays). One column on a phone, two once the card is about 720 px wide, from one auto-fit grid rule (no media query, so a narrow card on a wide desktop stays one column). Orchestrator decisions 2026-10-03 applied: no dot colours, two columns at >= 720 px.

Screenshots (dark theme, deviceScaleFactor 2): /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/orch/seat-ux-8/narrative-375.png, narrative-360.png, narrative-640.png, narrative-1280.png in the same directory.

## Head

b86c98f04b590b6397a1756ea0e40c96267fe20c

## Mutation proof

Run from the branch with `node tests/card.mjs` (HPO_PLANDATA set), mutating the predicate:
- `Array.isArray(items) && items.length === lines.length` replaced by `false` in narrativeRows: 5 checks red ("the label is the card's reason string", "kWh and cost sit in a number column of their own", "an idle item is a muted status row", "an unlabelled reason falls back", "labels follow the card language").
- `white-space: nowrap` deleted from `.nl-num`: "narrative css: the number column is nowrap and tabular" red.
Both restored (card sha1 prefix a46001f125fe). The layout lane `tests/card_browser.mjs` ("R9-UX-8 narrative at 360/375/640/1280 px") measures the property itself in Chromium: no kWh or cost run wraps, numbers flush right per column, no overflow, one column below 720 and two at 1280.

## Null control

Before the auto-fit cap the same 1280 px check failed with 3 columns (cols:3 against the expected 2), so the check does separate the two layouts. At the merge base (b09e0b912) `tests/card_browser.mjs` fails exactly one check on this machine, "P9 grid: no two text runs share ink" (2 px between chart tick labels "2" and "3"), and the same check fails on this branch: a local-font artefact of running Chromium 1148 under Playwright 1.56, not this change; CI's pinned browser decides. `GOLDEN_MODE=drift` `env_drift.py` against the merge base passes with the claim file's Python list untouched.

## Figures

- `node tests/card.mjs` : ALL CARD CHECKS PASSED (the 11 new "narrative" checks failed before the implementation, 11 red at the failing-test-first run).
- `node tests/card_drift.mjs $(git merge-base origin/main HEAD)` : rc 0; 39 of the 40 states move (the stylesheet text, same shape as #1388's claim); only score_open also moves in markup (the one state whose fixture carries a narrative); editor_schema is identical and unclaimed. claims-for stays 6.7.14.
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED. `node .claude/workflows/policy_lint.mjs --budgets` : rc 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` : MODE: SCOPED, 11 scripts; run locally: doc_claims, arch_score_head, deployment_shape, harness_headers, entities (2118 checks), env_drift, plan_view, card.mjs, card_drift.mjs all rc 0; features.py and golden.py left to CI (no Python moved).

Options considered. (1) Regex the translated sentence into label and number: rejected, language-fragile and breaks on any template edit; items are structured already. (2) Container query on .headline for the two-column switch: rejected, dialog.expanded is sized by its contents and the card's own comment warns that container-type: inline-size removes that sizing; auto-fit grid needs no containment. (3) Media query at 720 px: rejected, it reads the viewport, so a narrow card on a wide desktop would get two cramped columns. (4) Per-row hairline dividers: rejected, they do not align across two columns; row gap is enough. (5) Series-coloured dots: dropped on the orchestrator's decision. (6) Keep prose, just drop italic: rejected, does not fix the buried numbers or the orphaned SEK). (7) Fall back all-or-nothing when any reason is unlabelled: rejected for the per-row fallback, which keeps labelled rows tidy; all-or-nothing is used only when items and lines do not pair, since pairing is then unknown.

## Red checks

none

## Forward-carry

none. Seen and not folded in: the plan chart's zoom buttons (- + reset) overlay the chart in tvofi's screenshot and the legend caption wraps to three lines; reported to the orchestrator for a separate decision.

## Friction

none
