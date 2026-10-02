Fix review: blocked 6277884fecfae0b3c23b48615125ad0490892771 mutation: series confinement to its panel is unpinned; bars and areas on the plot floor, the actioned band and the shared-step hatch outside the power panel all pass both card lanes

Round 1. Reviewer: opus, cloud seat. Measured code head 6277884f; merge delta to PR head 1429b69e checked for the card lane only.

What holds (re-run here, not carried):
- RESULT card.mjs @6277884f: ALL CARD CHECKS PASSED (card_head.txt)
- RESULT card_browser.mjs @6277884f: ALL BROWSER CHECKS PASSED (browser_head.txt)
- RESULT card_drift.mjs 661d56f4 @6277884f: 39 state(s) moved and claimed, 1 identical (drift_head.txt)
- RESULT failing-first 65a40f4e card.mjs: deuteranope ok; protanope FAIL; tritanope FAIL; 2 checks failed
- RESULT @1429b69e (main 90335cbd merged): card.mjs ALL PASSED; card_drift vs 90335cbd 39 moved and claimed, 1 identical
- Viénot protan plane (L = 2.02344 M - 2.52581 S) and Machado 2009 tritan severity 1.0 matrix checked against the published values.
- Palette in SERIES_DEFS matches DESIGN.md section 4 table, light and dark, all eight series.
- D2 rule kept: geom x fields (plotL, plotW, plotR, window) unchanged; lanes under bottom panel. D5 untouched. U5: docs/img/card regenerated, docs/dashboard-card.md chart text describes three panels, no stale four-axis text.
- No VERSION, manifest or notes-heading change; claimed_drift.txt untouched.

The block. Targeted mutants on the code head (mutants.py, one at a time, restored after):

| mutant | change | card.mjs | card_browser.mjs |
|---|---|---|---|
| MA | baseOf returns plotB (areas and bars stand on the chart floor, so the price fill floods the power and temperature panels) | survived | survived |
| MB | actioned band at plotB instead of the power panel's base | survived | survived |
| MC | shared-step hatch spans plotT..plotB instead of the power panel | survived | survived |
| MD | dark outdoor = dark house | killed (4) | not run |
| MF | now-temp label at the top panel | killed (1) | not run |
| MH | hidden panels keep their height | survived | killed (1) |
| ME | estimated wash in the first panel only | survived | survived |
| MG | vertical grid one full-height rule | survived | survived |

MA, MB and MC are the substance of concept A (D2): each series drawn in its own panel. Every one of them is a visible regression that both lanes pass, and the body's mutation table (M1..M5) does not reach them. Requested: one check that every series path, band, actioned-band rect and shared-step hatch lies within its own panel's [top, bottom] (for example from the .panel rects' data-panel and SERIES_DEFS' panel), shown red on MA, MB and MC and green at the head. ME and MG are cosmetic; pinning them in the same check is optional.

Not blocking, for the fixer's judgement: the slot lanes still paint the old series colours (#e0544e, #4a90e2, laneSpecs) beside bars in the palette of record (#d2403f, #2a78d6) and do not follow colorDark; the body discloses this as out of the brief's list.

CI on 1429b69e at review time: browser, mutation, typing, policy-docs, pr-contract, budget-raise-gate, delivery-status, nightly-status green; fast, closures and coverage still running. Not cited for the verdict.
