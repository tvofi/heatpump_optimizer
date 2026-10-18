Fix review: blocked e9e6b99b30de85eebba6a1a77507a0179f36f5ad harness: class-open residual not exact: RV4's written form, appended to document.body and submitted by a button click, passes both arms rc=0 fails=0 inside a DRIVEN press (RD4, after advisor:settings' navigateTo), so the Residual paragraph, the body's "Residual, exactly" and the four carries, which confine the gap to handlers the dynamic arm does not drive, still over-claim; and R10-DEEPLINK-HANDLERS' control "each of RV1-RV7 must go red once its handler is driven" is already false for RV4

bus-nonce: b87aaea45b247c1eb1cadfaea183ecaa

Round: 9, a delta review after the orchestrator's split ruling. It judges b678c7d16 plus the main merges since ee409c81d. Measured head: e9e6b99b30de85eebba6a1a77507a0179f36f5ad; refs/pull/2345/head was re-read just before posting.

## RESULT lines (mine, at e9e6b99b30de85eebba6a1a77507a0179f36f5ad)
RESULT mutant=NULL_no_plant rc=0 fails=0
node tests/card.mjs: ALL CARD CHECKS PASSED, 1257 ok, 0 FAIL
RESULT mutant=RV1_history_bracket_back_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV2_history_optional_back_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV3_history_destructure_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV4_form_ns_action_member_button_click_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV5_action_member_to_variable_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV6_object_assign_quoted_action_key_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV7_create_element_ns_form_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV1c_history_dot_back_control rc=1 fails=1
RESULT mutant=RV5c_action_member_to_literal_control rc=1 fails=1
RESULT mutant=Y1_runtime_name_on_unresolved_selector_residual rc=0 fails=0
These come from the PR's own driver (evidence9/r9*.log). RV1-RV7, RV1c and RV5c are byte-identical to my review_plants.py: I compared each plant's edit list programmatically and all nine read VERBATIM.

My round-9 plants (evidence9/review_plants9.py, my own instrument, using the PR driver's after_nav and run()) put the same spellings in a press the census DOES drive (evidence9/rd*.log):
RESULT mutant=RD1_history_bracket_back_driven rc=1 fails=1            (RV1's spelling, driven: red on "every link the census records ... haLink builds")
RESULT mutant=RD5_action_member_to_variable_on_rendered_form_driven rc=1 fails=1   (createElementNS form with .action = u, appended to the shadow root, driven: red, the control)
RESULT mutant=RD4_form_ns_action_member_button_click_driven rc=0 fails=0   (RV4 verbatim, driven: GREEN)
RD4 and RD5 differ only in where the form goes and how it is submitted. RD5 appends it to root and is red. RD4 appends it to document.body and submits it with a button's click(), which no row names; it is green. The dynamic arm reads href/action/formaction off the shadow root after each press, and the stub's click() submits nothing, so a form outside the shadow root that a button submits is invisible to both arms even where a press reaches it.

## (a) Over-claims
- Card.mjs Residual paragraph: the old "refuses ... wherever they are written" is gone, and the gap is now stated as the spellings its rows name. But it confines the gap to "a handler it does not drive" plus the a.zz stub selector, and RD4 is a third shape inside a driven press. The residual is narrower than measured, so it is still not exact.
- The body ("Residual, exactly: navigation written in a handler the dynamic arm does not drive ...") and all four carries (R10-UX-SETUP, R10-ADVISOR, R10-SCORES, R10-UX-HEALTH: "navigation written in a handler the census's dynamic arm does not drive ... is not covered") have the same defect. They tell a later stage that a click-driven row is covered when RD4 shows it is not.
- R10-DEEPLINK-HANDLERS's brief (f2d13bb4a) says "each of RV1-RV7 must go red once its handler is driven". RD4 shows RV4 stays green when driven. The split group's control is unsatisfiable as written, and driving handlers alone does not close that shape.
- Z-plant comment ("in that unreached handler"): accurate. Grepping card.mjs and the driver for "wherever" finds no census claim left.
Fix (narrow, comments and text only plus one plant): in the Residual paragraph, the body and the four carries, add a form placed outside the shadow root (document.body) and submitted by a button's click(), which passes even where a press reaches it. Add RD4 to the driver as a green-by-design witness beside RD5, the red control. The orchestrator then amends R10-DEEPLINK-HANDLERS's brief: RV4/RD4 needs the dynamic arm to read document-level markup, or a click-submits-form instrument, as well as driving handlers.

## (b) RV plants: committed verbatim and re-run (above). Green and red as claimed.
## (c) Disclosed: the body now discloses the runsFrom rename (open to run, d3513acc8). The X-plant docstring is corrected: X1/X2 alone red, X3-X13 alone green, X7K1b red on "no press throws". That matches my round-8 runs (X3, X7, X8 alone green; X7K1b FAIL "no press throws", evidence/sweep4.log).
## (d) Closing keyword: none. The body says "Part of #2317". closingIssuesReferences is [], and a keyword regex over the body finds no match.
## (e) Merges: pure. git merge-tree --write-tree of each merge's parents equals its tree for eb277f48f, 34f85f45f and e9e6b99b3. git merge-tree --write-tree origin/main e9e6b99b30de85eebba6a1a77507a0179f36f5ad exits 0. The b678c7d16 diff to tests/card.mjs changes comment lines only, and git diff ee409c81d b678c7d16 touches tests/card.mjs, the driver, the roster and two delivery rows only.

## Checks
At e9e6b99b30de85eebba6a1a77507a0179f36f5ad all 42 check names' latest runs are success or skipped (evidence9/checkruns_head.tsv). The failure and cancelled runs in ee409c81d..e9e6b99b30de85eebba6a1a77507a0179f36f5ad are on main's own record commits 2808c5419 and 56182647d, not this branch's (evidence9/red_delta.tsv). The red-history answers judged in round 8 are unchanged in the body. Not re-run: the gate, mutation table, structure and archscore (CI's, green).
