Design review: approve 3913198407d9bfe24b597fa3daba12b98a09ed59

Reviewed design/R11-SEAM-card at 3913198407d9bfe24b597fa3daba12b98a09ed59 (round 1) from a detached worktree. Code read at the note's base origin/main bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f. Plan read at plan/r11 819aa2e354b4e5baaf824b8568fd72bea8168a75 (PLAN.md move ledger and hot-file order, PLAN.json, the D4-s3-05 finding). Roster row read on handoff/audit-r10-roster (size L, no after edge, 9 findings).

Checked with no point raised:
- Seam. The card's script is the one file. cardStyleBlock (card.js:5062), setupSvgHtml's line() (:4618), LayoutEditor's removal (:14923, :14944) and HistorySource (:7127) each own their concern at the base. The translations are read through hass.localize and never edited. No Python changes, and no new write path.
- Shape. Sections A to E each map to a named finding. The 14 px step in B is what D4-s3-05's own proposed_fix_scope allows ("adding a step only where a size is deliberate"). The crit-fill token reads 6.5:1 for white text, which I re-derived from #b3261e.
- Sibling sites. I re-ran every section 5 grep at bc658f9 and the counts match (4, 10, 21, 41, 4, 25, 4). I also went through all 25 catch sites and all 20 callService/callWS sites. No service error is shown to the user outside the ten sites in D: set_away (:6749, :6764) catches nothing and displays nothing, the debug_collect catch shows nothing, and the what-if's first.error at :13427 is a response field, not a raised HomeAssistantError.
- Evidence plan. The five failing tests can go red at the base. The harnesses and null controls are the finders'. claimed_drift.txt stays byte-identical, and card_claimed_drift.txt is the claim file for the card's markup.
- Sibling designs. No open design/* note claims the card's script. design/R11-SEAM-cycle-solve only names card.js's run() as an alternative it rejected.
- Cost. One file plus tests, committed per rule family, fits L.

Rulings on the designer's open points:
1. D5-s4-01's card units (section 7). They stay in R11-SEAM-comments-production. The owner-approved plan (PLAN.json, PLAN.md "Both comment groups ... released per file") and the roster row (comments-production hot_files include the card, released after card and product-text) already settle this. It is not pending owner confirmation, and there is no roster edit. This group writes every new or rewritten comment to C5 and does not pay the card's existing long units.
2. D6-s4-01 reads 0 at main. By the owner's precedent of 2026-11-18, it gets a regression pin only and no production edit. The pin already exists: tests/card.mjs:387-427, the en-placeholder parity arm with its planted null controls. The fixer runs card_placeholders.mjs at both ends (0 to 0), plants {minuter} to show that the harness reads 1 and the arm goes red, and records the finding in the PR body as "not reproduced at main, pinned". No new check is added.
3. D4-s3-05's predicted after-read of 1 is accepted. The harness's scale set is the fixed set {12, 13, 15, 18}, so a deliberate new step reads as off-scale. The PR body names this. The finder's harness is not edited in this round.
4. Item svg-11px is dismissed, and the dismissal is accepted.

Notes for the fixer:
- card_rule_copies is gate-only (tools/audit/archscore/ABOUT.md C24, ci_budgets.json 72). The move names card_clone_copies at 0.0. A fall in either is banked with score.py --diff and the reason the rule moved: here, ten respellings of the error rule become one function. That is a real move and not a score-only one, but any card_clone_copies fall still needs the reviewer's diff. Carry: R11-SEAM-card (item rule-copies-bank)
- The hit path is emitted only while editing. Run tests/card_drift.mjs --list before claiming anything, and claim only the states that actually move. Carry: R11-SEAM-card (item claim-only-moved)

Seat token count: not reported by this harness.
